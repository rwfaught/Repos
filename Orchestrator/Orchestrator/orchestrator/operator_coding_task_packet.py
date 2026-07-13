from __future__ import annotations

from typing import Any

from orchestrator import engine
import orchestrator.run_manager as run_manager
from orchestrator.execution_authorization import persist_execution_authorization
from orchestrator.current_success_result_review import review_current_success_task_result
from orchestrator.current_success_acceptance import record_current_success_result_acceptance
from orchestrator.operator_packet_result_decision import record_packet_result_operator_decision
from orchestrator.paths import record_path, resolve_declared_project_path, validate_record_id
from orchestrator.task_schema import FILESYSTEM_MUTATION_EXECUTION_POLICY, Task
import orchestrator.paths as project_paths
from orchestrator.trusted_worker_security import (
    WorkerSecurityError,
    prepare_trusted_worker_workspace,
    validate_trust_posture,
)


_REQUIRED_FIELDS = (
    "packet_id",
    "run_id",
    "task_id",
    "title",
    "files_in_scope",
    "success_criteria",
    "expected_output",
)

_PROVIDER_RUNTIME_REQUEST_FIELDS = (
    "model",
    "model_name",
    "runtime",
    "runtime_name",
    "platform",
    "platform_name",
    "ollama_model",
    "openclaw_runtime",
    "hermes_runtime",
    "allow_live_provider",
)

_NON_PROOFS = [
    "no_semantic_correctness_proof",
    "no_live_provider_model_proof",
    "no_runtime_platform_proof",
    "no_autonomous_ai_coding_proof",
    "no_production_readiness_proof",
    "local_file_is_deterministic_local_behavior_not_model_backed_generation",
    "deterministic_verification_is_a_bounded_tripwire",
]

_NO_ACTIVITY_FLAGS = {
    "model_executed": False,
    "runtime_executed": False,
    "platform_invoked": False,
    "live_provider_invoked": False,
    "ollama_invoked": False,
    "openclaw_invoked": False,
    "hermes_invoked": False,
    "discord_invoked": False,
    "installer_invoked": False,
    "autonomous_ai_coding_claimed": False,
    "production_readiness_claimed": False,
    "semantic_correctness_claimed": False,
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _blocked(
    *,
    packet: dict[str, Any] | None,
    blocked_conditions: list[str],
    missing_requirements: list[str] | None = None,
    detail: str = "",
) -> dict[str, Any]:
    packet = packet if isinstance(packet, dict) else {}
    return {
        "operator_coding_task_packet_surface": True,
        "packet_id": _normalize_text(packet.get("packet_id")),
        "run_id": _normalize_text(packet.get("run_id")),
        "task_id": _normalize_text(packet.get("task_id")),
        "accepted": False,
        "blocked": True,
        "blocked_conditions": sorted(set(blocked_conditions)),
        "missing_requirements": sorted(set(missing_requirements or [])),
        "detail": detail,
        "execution_provider": "",
        "final_task_status": "",
        "execution_artifact_id": "",
        "current_success_review": {},
        "operator_response_surface": "blocked_operator_coding_task_packet_options",
        "operator_next_action": "repair_packet_before_execution_boundary",
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        "non_proofs": list(_NON_PROOFS),
    }


def _require_nonempty_sequence(
    packet: dict[str, Any],
    field_name: str,
) -> tuple[list[str], str | None]:
    raw = packet.get(field_name)
    if not isinstance(raw, list):
        return [], field_name
    values = [_normalize_text(item) for item in raw]
    values = [item for item in values if item]
    if not values:
        return [], field_name
    return values, None


def _validate_packet(packet: Any) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(packet, dict):
        return None, _blocked(
            packet=None,
            blocked_conditions=["packet_must_be_json_object"],
            detail="Operator coding task packet must be a JSON object.",
        )

    missing = [
        field_name
        for field_name in _REQUIRED_FIELDS
        if not _normalize_text(packet.get(field_name))
    ]

    packet_id = _normalize_text(packet.get("packet_id"))
    run_id = _normalize_text(packet.get("run_id"))
    task_id = _normalize_text(packet.get("task_id"))
    title = _normalize_text(packet.get("title"))
    expected_output = (
        str(packet.get("expected_output"))
        if packet.get("expected_output") is not None
        else ""
    )

    files_in_scope, files_missing = _require_nonempty_sequence(packet, "files_in_scope")
    success_criteria, criteria_missing = _require_nonempty_sequence(
        packet,
        "success_criteria",
    )
    if files_missing:
        missing.append(files_missing)
    if criteria_missing:
        missing.append(criteria_missing)

    blocked_conditions: list[str] = []
    details: list[str] = []

    if missing:
        blocked_conditions.append("missing_required_packet_fields")

    provider_name = _normalize_text(packet.get("provider_name")) or "local_file"
    if provider_name not in {"local_file", "subprocess_worker"}:
        blocked_conditions.append("unsupported_provider_name")
        details.append("Canonical execution allows only an explicit subprocess_worker; local_file remains legacy-only.")
    trust_posture = _normalize_text(packet.get("worker_trust_posture"))
    if provider_name == "subprocess_worker":
        posture_error = validate_trust_posture(trust_posture)
        if posture_error:
            blocked_conditions.append(posture_error)
            details.append("Canonical subprocess execution requires explicit trusted_local_unsandboxed posture.")

    requested_runtime_fields = [
        field_name
        for field_name in _PROVIDER_RUNTIME_REQUEST_FIELDS
        if field_name in packet and _normalize_text(packet.get(field_name))
    ]
    if requested_runtime_fields:
        blocked_conditions.append("provider_model_runtime_platform_request_rejected")
        missing.extend(requested_runtime_fields)

    execution_policy = (
        _normalize_text(packet.get("execution_policy"))
        or FILESYSTEM_MUTATION_EXECUTION_POLICY
    )
    if execution_policy != FILESYSTEM_MUTATION_EXECUTION_POLICY:
        blocked_conditions.append("unsupported_execution_policy")
        details.append("Phase 274 requires filesystem_mutation execution_policy.")

    for label, value in (
        ("packet id", packet_id),
        ("run id", run_id),
        ("task id", task_id),
    ):
        if not value:
            continue
        try:
            validate_record_id(value, label=label)
        except ValueError as error:
            blocked_conditions.append(f"{label.replace(' ', '_')}_invalid")
            details.append(str(error))

    if task_id and "task_id_invalid" not in blocked_conditions:
        task_path = record_path(run_manager.TASKS_DIR, task_id, label="task id")
        if task_path.exists():
            blocked_conditions.append("task_id_already_exists")
            details.append("Task id already has a persisted task record.")

    for declared_path in files_in_scope:
        if "\\" in declared_path:
            blocked_conditions.append("declared_file_path_invalid")
            details.append("Declared project path must use forward slashes.")
            continue
        try:
            resolve_declared_project_path(declared_path)
        except ValueError as error:
            blocked_conditions.append("declared_file_path_invalid")
            details.append(str(error))

    if blocked_conditions:
        return None, _blocked(
            packet=packet,
            blocked_conditions=blocked_conditions,
            missing_requirements=missing,
            detail=" ".join(details),
        )

    validated = {
        "packet_id": packet_id,
        "run_id": run_id,
        "task_id": task_id,
        "title": title,
        "files_in_scope": files_in_scope,
        "success_criteria": success_criteria,
        "expected_output": expected_output,
        "provider_name": provider_name,
        "execution_policy": execution_policy,
        "worker_trust_posture": trust_posture,
    }
    return validated, None


def _operator_next_action_from_review(review: dict[str, Any]) -> str:
    option_ids = [
        _normalize_text(option.get("option_id"))
        for option in review.get("response_options", [])
        if isinstance(option, dict)
    ]
    preferred = [
        "inspect_task_state",
        "inspect_execution_artifact",
        "inspect_verifier_result",
        "record_operator_acceptance_later",
    ]
    available = [option_id for option_id in preferred if option_id in option_ids]
    return "; ".join(available) or _normalize_text(review.get("next_action"))


def run_operator_coding_task_packet(packet: dict[str, Any], *, provider: Any = None) -> dict[str, Any]:
    validated, blocked = _validate_packet(packet)
    if blocked is not None:
        return blocked
    assert validated is not None

    if provider is None:
        return _blocked(
            packet=packet,
            blocked_conditions=["explicit_worker_provider_required"],
            detail="Implicit local_file execution is retired from the canonical packet path.",
        )
    active_provider_name = _normalize_text(getattr(provider, "provider_name", ""))
    if active_provider_name != validated["provider_name"]:
        return _blocked(
            packet=packet,
            blocked_conditions=["provider_identity_mismatch"],
            detail="The explicit worker provider must match packet provider_name.",
        )

    worker_execution_policy = getattr(provider, "worker_execution_policy", None)
    authorization = persist_execution_authorization(
        packet,
        validated["task_id"],
        validated["files_in_scope"],
        worker_execution_policy=worker_execution_policy,
    )
    if not authorization["execution_authorized"]:
        return {
            **_blocked(packet=packet, blocked_conditions=["execution_authorization_denied"], detail=authorization["denial_reason"]),
            "authorization": authorization,
            "operator_next_action": "provide_explicit_execution_authorization",
        }

    try:
        worker_security = prepare_trusted_worker_workspace(
            project_paths.DATA_DIR,
            task_id=validated["task_id"],
            run_id=validated["run_id"],
            trust_posture=validated["worker_trust_posture"],
            declared_paths=validated["files_in_scope"],
        )
    except WorkerSecurityError as error:
        return {
            **_blocked(packet=packet, blocked_conditions=[error.code], detail=str(error)),
            "authorization": authorization,
        }

    run_manager.ensure_run(validated["run_id"], validated["title"], worker_security=worker_security)

    task = Task(
        id=validated["task_id"],
        run_id=validated["run_id"],
        title=validated["title"],
        role="coder",
        status="queued",
        dependencies=[],
        success_criteria=validated["success_criteria"],
        files_in_scope=validated["files_in_scope"],
        retry_count=0,
        expected_output=validated["expected_output"],
        execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
        requires_causal_change=True,
        execution_authorization_provenance={
            "authorization_id": authorization["authorization_id"],
            "decision": authorization["decision"],
            "task_id": authorization["task_id"],
            "authorized_scope": list(authorization["authorized_scope"]),
            "operator_provenance": authorization["operator_provenance"],
            "worker_trust_posture": authorization["worker_trust_posture"],
            "worker_execution_policy": authorization["worker_execution_policy"],
        },
        worker_security=worker_security,
        worker_execution_policy=authorization["worker_execution_policy"],
    )

    run_manager.save_task(task)
    engine.process_task_by_id(
        run_manager.load_task(task.id),
        provider_name=active_provider_name,
        provider=provider,
        context={
            "execution_authorization": authorization,
            "worker_security": worker_security,
            "worker_execution_policy": authorization["worker_execution_policy"],
        },
    )
    completed = run_manager.load_task(task.id)
    review = review_current_success_task_result({"task_id": task.id})
    acceptance = {}
    disposition = {}
    if isinstance(packet.get("human_review"), dict):
        human_review = packet["human_review"]
        if human_review.get("accepted") is True:
            acceptance = record_current_success_result_acceptance({"task_id": task.id, **human_review})
        else:
            disposition = record_packet_result_operator_decision(
                {
                    "task_id": task.id,
                    "packet_id": validated["packet_id"],
                    "operator_decision": human_review.get("operator_decision") or "rejected",
                    "operator_note": human_review.get("operator_note") or human_review.get("reason"),
                }
            )

    execution_succeeded = completed.status == "completed"

    return {
        "operator_coding_task_packet_surface": True,
        "packet_id": validated["packet_id"],
        "run_id": completed.run_id,
        "task_id": completed.id,
        "accepted": execution_succeeded,
        "blocked": not execution_succeeded,
        "blocked_conditions": [] if execution_succeeded else [f"task_{completed.status}"],
        "missing_requirements": [],
        "execution_provider": getattr(provider, "provider_name", ""),
        "authorization": authorization,
        "worker_execution_policy": authorization["worker_execution_policy"],
        "final_task_status": completed.status,
        "execution_artifact_id": completed.execution_artifact_id or "",
        "current_success_review": review,
        "human_review_acceptance": acceptance,
        "human_review_disposition": disposition,
        "execution_succeeded": execution_succeeded,
        "operator_response_surface": review.get("operator_response_surface"),
        "operator_next_action": _operator_next_action_from_review(review),
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        "non_proofs": list(_NON_PROOFS),
    }
