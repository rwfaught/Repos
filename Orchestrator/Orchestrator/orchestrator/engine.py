import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.adequacy import assess_output_adequacy
from orchestrator.artifact_store import create_artifact
from orchestrator.alpha_runtime import SCHEMA_VERSION, atomic_write_json
from orchestrator.dispatcher import dispatch_task
from orchestrator.paths import (
    VERIFIER_RESULTS_DIR,
    record_path,
    resolve_declared_project_path,
    validate_record_id,
)
from orchestrator.reviewer_output import (
    build_recommendation_record,
    parse_reviewer_recommendation,
    persist_recommendation_record,
    validate_reviewer_recommendation,
)
from orchestrator.run_manager import (
    create_reviewer_task,
    get_next_task,
    is_recommendation_emitter_reviewer_task,
    save_task,
)
from orchestrator.task_schema import (
    FILESYSTEM_MUTATION_EXECUTION_POLICY,
    Task,
    normalize_execution_policy,
)
from orchestrator.state import load_state
from verifiers.base import VerificationCheckResult, VerificationResult
from verifiers.registry import run_check


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _snapshot_causal_targets(task: Task) -> list[dict]:
    snapshots = []
    seen_targets = set()

    for declared_path in task.files_in_scope:
        target = str(declared_path).strip()
        if not target or target in seen_targets:
            continue
        seen_targets.add(target)

        resolved_path = resolve_declared_project_path(target)
        existed_before = resolved_path.is_file()
        snapshots.append(
            {
                "declared_path": target,
                "resolved_path": str(resolved_path),
                "existed_before": existed_before,
                "sha256_before": _sha256_file(resolved_path) if existed_before else None,
            }
        )

    return snapshots


def _complete_causal_target_snapshots(snapshots: list[dict]) -> list[dict]:
    completed = []
    for snapshot in snapshots:
        resolved_path = Path(snapshot["resolved_path"])
        existed_after = resolved_path.is_file()
        completed.append(
            {
                **snapshot,
                "existed_after": existed_after,
                "sha256_after": _sha256_file(resolved_path) if existed_after else None,
            }
        )
    return completed


def _apply_causal_change_verification(
    task: Task,
    verification_result: VerificationResult,
    causal_targets: list[dict],
) -> None:
    verification_result.causal_change_required = task.requires_causal_change
    if not task.requires_causal_change:
        return

    changed_targets = []
    for target in causal_targets:
        created = not target["existed_before"] and target["existed_after"]
        modified = (
            target["existed_before"]
            and target["existed_after"]
            and target["sha256_before"] != target["sha256_after"]
        )
        if created or modified:
            changed_targets.append(target["declared_path"])

    causal_change_passed = bool(changed_targets)
    message = (
        "Causal filesystem change verified."
        if causal_change_passed
        else "Required causal filesystem change was not observed."
    )
    verification_result.checks.append(
        VerificationCheckResult(
            name="causal_file_change",
            passed=causal_change_passed,
            message=message,
            evidence={
                "targets": causal_targets,
                "changed_targets": changed_targets,
            },
        )
    )
    verification_result.messages.append(message)
    verification_result.overall_passed = (
        verification_result.overall_passed and causal_change_passed
    )
    verification_result.causal_change_passed = causal_change_passed
    verification_result.causal_change_targets = causal_targets
    verification_result.changed_targets = changed_targets


def _verify_task_outputs(task: Task) -> VerificationResult:
    if task.verification_checks:
        checks = []
        messages = []
        overall_passed = True

        for declared_check in task.verification_checks:
            check_name = declared_check["check"]
            target = declared_check["target"]
            resolved_path = resolve_declared_project_path(target)
            result = run_check(check_name, str(resolved_path), check_options=declared_check)
            checks.extend(result.checks)
            messages.extend(result.messages)
            overall_passed = overall_passed and result.overall_passed

        return VerificationResult(
            overall_passed=overall_passed,
            checks=checks,
            messages=messages,
        )

    if not task.files_in_scope:
        return VerificationResult(
            overall_passed=True,
            checks=[],
            messages=["Verification skipped: no files_in_scope provided."],
        )

    checks = []
    messages = []
    overall_passed = True

    for file_path in task.files_in_scope:
        resolved_path = resolve_declared_project_path(file_path)
        result = run_check("file_exists", str(resolved_path))
        checks.extend(result.checks)
        messages.extend(result.messages)
        overall_passed = overall_passed and result.overall_passed

    return VerificationResult(
        overall_passed=overall_passed,
        checks=checks,
        messages=messages,
    )


def _store_verification_result(task: Task, verification_result: VerificationResult) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    VERIFIER_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    task_id = validate_record_id(task.id, label="task id")
    result_path = record_path(
        VERIFIER_RESULTS_DIR,
        f"{task_id}_{timestamp}",
        label="verifier result id",
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "task_id": task.id,
        "run_id": task.run_id,
        "execution_artifact_id": task.execution_artifact_id,
        "authorization_id": (task.execution_authorization_provenance or {}).get("authorization_id"),
        "execution_policy": task.execution_policy,
        "requires_causal_change": task.requires_causal_change,
        "verification_result": verification_result.to_dict(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write_json(result_path, payload)
    return result_path


def _validate_execution_policy_preconditions(task: Task) -> str | None:
    policy = normalize_execution_policy(task)
    if policy != FILESYSTEM_MUTATION_EXECUTION_POLICY:
        return None
    if not task.files_in_scope:
        return "Filesystem-mutation tasks require at least one bounded file target."

    for declared_path in task.files_in_scope:
        resolve_declared_project_path(declared_path)
    return None


def _fail_execution_policy_precondition(task: Task, reason: str) -> None:
    task.status = "verification_failed"
    verification_result = VerificationResult(
        overall_passed=False,
        checks=[
            VerificationCheckResult(
                name="execution_policy_precondition",
                passed=False,
                message=reason,
                evidence={
                    "execution_policy": task.execution_policy,
                    "files_in_scope": list(task.files_in_scope),
                    "requires_causal_change": task.requires_causal_change,
                },
            )
        ],
        messages=[reason],
        causal_change_required=task.requires_causal_change,
        causal_change_passed=False if task.requires_causal_change else None,
        causal_change_targets=[] if task.requires_causal_change else None,
        changed_targets=[] if task.requires_causal_change else None,
    )
    verification_path = _store_verification_result(task, verification_result)
    save_task(task)

    print(f"Task processed: {task.id}")
    print(f"Title: {task.title}")
    print(f"Execution policy: {task.execution_policy}")
    print("Provider dispatch: skipped")
    print("Verification passed: False")
    print(f"Verification result: {verification_path}")
    print(f"Status: {task.status}")


def _execute_task(task: Task, provider_name: str = "mock", provider=None, context: dict | None = None) -> None:
    precondition_failure = _validate_execution_policy_preconditions(task)
    task.status = "in_progress"
    save_task(task)
    if precondition_failure is not None:
        _fail_execution_policy_precondition(task, precondition_failure)
        return

    causal_targets_before = (
        _snapshot_causal_targets(task) if task.requires_causal_change else []
    )
    dispatch_context = dict(context or {})
    dispatch_context["allowed_paths"] = [
        str(resolve_declared_project_path(path)) for path in task.files_in_scope
    ]
    if provider is None and context is None:
        # Preserve the legacy dispatcher call shape for non-canonical callers.
        result = dispatch_task(task, provider_name=provider_name)
    else:
        result = dispatch_task(
            task,
            provider_name=provider_name,
            provider=provider,
            context=dispatch_context,
        )
    causal_targets = _complete_causal_target_snapshots(causal_targets_before)
    artifact = create_artifact(task, result)
    task.execution_artifact_id = artifact["artifact_id"]

    verification_result = _verify_task_outputs(task)
    verification_result.execution_artifact_id = task.execution_artifact_id
    _apply_causal_change_verification(task, verification_result, causal_targets)
    verification_path = _store_verification_result(task, verification_result)
    adequacy_result = {"is_adequate": None, "reason": "Adequacy check not run."}
    recommendation_validation = {"is_valid": None, "reason": "Recommendation validation not run."}
    recommendation_record_path = None
    reviewer_task_id = None

    provider_execution_status = str(result.get("status", "")).strip()

    if provider_execution_status != "success":
        task.status = "execution_failed"
    elif not verification_result.overall_passed:
        task.status = "verification_failed"
    elif is_recommendation_emitter_reviewer_task(task):
        parsed_recommendation, parse_reason = parse_reviewer_recommendation(result.get("output"))
        if parsed_recommendation is None:
            recommendation_validation = {"is_valid": False, "reason": parse_reason}
            task.status = "verification_failed"
        else:
            is_valid, validation_reason = validate_reviewer_recommendation(parsed_recommendation)
            recommendation_validation = {"is_valid": is_valid, "reason": validation_reason}
            if is_valid:
                record = build_recommendation_record(
                    task=task,
                    recommendation=parsed_recommendation,
                    provider_name=str(result.get("provider")),
                )
                recommendation_record_path = persist_recommendation_record(task=task, record=record)
                task.status = "completed"
            else:
                task.status = "verification_failed"
    else:
        adequacy_result = assess_output_adequacy(task, result)
        ollama_status = adequacy_result.get("provider_status")
        if ollama_status in {"blocked", "needs_review"}:
            task.status = "needs_review"
            adequacy_result["is_adequate"] = False
            adequacy_result["reason"] = f"Ollama provider declared task status {ollama_status}."
            if task.role != "reviewer":
                reviewer_task = create_reviewer_task(
                    original_task=task,
                    source_artifact_id=artifact["artifact_id"],
                    review_reason=adequacy_result["reason"],
                    expected_output="concise review",
                )
                reviewer_task_id = reviewer_task.id
        elif adequacy_result["is_adequate"]:
            task.status = "completed"
        else:
            task.status = "needs_review"
            if task.role != "reviewer":
                reviewer_task = create_reviewer_task(
                    original_task=task,
                    source_artifact_id=artifact["artifact_id"],
                    review_reason=adequacy_result["reason"],
                    expected_output="concise review",
                )
                reviewer_task_id = reviewer_task.id

    save_task(task)

    print(f"Task processed: {task.id}")
    print(f"Title: {task.title}")
    print(f"Execution policy: {task.execution_policy}")
    print(f"Artifact: {artifact['artifact_id']}")
    print(f"Provider: {result.get('provider')}")
    print(f"Execution status: {result.get('status')}")
    if result.get("error"):
        print(f"Execution error: {result.get('error')}")
    print(f"Verification passed: {verification_result.overall_passed}")
    print(f"Verification result: {verification_path}")
    print(f"Adequacy passed: {adequacy_result['is_adequate']}")
    print(f"Adequacy reason: {adequacy_result['reason']}")
    print(f"Recommendation valid: {recommendation_validation['is_valid']}")
    print(f"Recommendation reason: {recommendation_validation['reason']}")
    if recommendation_record_path:
        print(f"Recommendation record: {recommendation_record_path}")
    if reviewer_task_id:
        print(f"Reviewer task created: {reviewer_task_id}")
    print(f"Status: {task.status}")


def process_task_by_id(task: Task, provider_name: str = "mock", provider=None, context: dict | None = None) -> None:
    _execute_task(task=task, provider_name=provider_name, provider=provider, context=context)


def process_next_task(provider_name: str = "mock") -> None:
    state = load_state()
    run_id = state.get("active_run_id")

    if not run_id:
        print("No active run")
        return

    task = get_next_task(run_id)
    if task is None:
        print("No runnable tasks")
        return

    _execute_task(task=task, provider_name=provider_name)
