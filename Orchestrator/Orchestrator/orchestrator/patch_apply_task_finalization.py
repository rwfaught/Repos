from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from orchestrator import artifact_store, run_manager
from orchestrator.patch_apply_result_review import (
    ELIGIBLE_FOR_COMPLETION,
    review_patch_apply_result,
)
from orchestrator.paths import resolve_declared_project_path, validate_record_id
from orchestrator.task_schema import FILESYSTEM_MUTATION_EXECUTION_POLICY


PATCH_APPLY_TASK_FINALIZATION_ARTIFACT_TYPE = "patch_apply_task_finalization"
PATCH_APPLY_TASK_FINALIZATION_SOURCE = "verified_patch_apply_task_finalization"
_FINALIZABLE_TASK_STATUSES = frozenset({"queued", "in_progress"})


def patch_apply_task_finalization_path(finalization_id: str):
    return artifact_store.artifact_path(
        validate_record_id(finalization_id, label="finalization id")
    )


def _required_review_id(review_result: dict[str, Any], field: str) -> str:
    return validate_record_id(
        review_result.get(field),
        label=field.replace("_", " "),
    )


def _bounded_review_files(review_result: dict[str, Any]) -> list[str]:
    raw_files = review_result.get("files_changed")
    if not isinstance(raw_files, list) or not raw_files:
        raise ValueError("Eligible review requires non-empty files_changed evidence.")

    files: list[str] = []
    seen: set[str] = set()
    for raw_path in raw_files:
        path = str(raw_path or "").strip()
        resolve_declared_project_path(path)
        identity = path.replace("\\", "/")
        if identity not in seen:
            files.append(path)
            seen.add(identity)
    return files


def _validate_review_result(
    task_id: str,
    review_result: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(review_result, dict):
        raise ValueError("A Phase 100 review result is required.")
    if review_result.get("decision") != ELIGIBLE_FOR_COMPLETION:
        raise ValueError("Review result is not eligible_for_completion.")
    if review_result.get("eligible_for_completion") is not True:
        raise ValueError("Review result lacks affirmative completion eligibility.")

    reviewed_task_id = _required_review_id(review_result, "task_id")
    if reviewed_task_id != task_id:
        raise ValueError("Review result task_id does not match the requested task.")

    apply_id = _required_review_id(review_result, "apply_id")
    proposal_id = _required_review_id(review_result, "proposal_id")
    authorization_id = _required_review_id(review_result, "authorization_id")
    files_changed = _bounded_review_files(review_result)

    if review_result.get("causal_change_observed") is not True:
        raise ValueError("Review result lacks causal change evidence.")
    if review_result.get("requires_verification") is not True:
        raise ValueError("Review result lacks requires_verification evidence.")

    canonical_review = review_patch_apply_result(
        apply_id,
        expected_task_id=task_id,
    )
    if canonical_review.get("decision") != ELIGIBLE_FOR_COMPLETION:
        raise ValueError("Referenced apply result lacks Phase 100 eligibility.")
    for field, expected in (
        ("task_id", reviewed_task_id),
        ("apply_id", apply_id),
        ("proposal_id", proposal_id),
        ("authorization_id", authorization_id),
    ):
        if canonical_review.get(field) != expected:
            raise ValueError(
                f"Review result {field} does not match canonical Phase 100 evidence."
            )

    canonical_files = _bounded_review_files(canonical_review)
    if {
        path.replace("\\", "/") for path in canonical_files
    } != {path.replace("\\", "/") for path in files_changed}:
        raise ValueError(
            "Review result files_changed does not match canonical Phase 100 evidence."
        )

    return {
        "task_id": reviewed_task_id,
        "apply_id": apply_id,
        "proposal_id": proposal_id,
        "authorization_id": authorization_id,
        "files_changed": canonical_files,
        "causal_change_observed": True,
        "requires_verification": True,
    }


def finalize_verified_patch_apply_task(
    task_id: str,
    *,
    review_result: dict[str, Any] | None,
) -> dict[str, Any]:
    safe_task_id = validate_record_id(task_id, label="task id")
    evidence = _validate_review_result(safe_task_id, review_result)
    task = run_manager.load_task(safe_task_id)

    if task.status == "completed":
        raise ValueError("Task is already completed.")
    if task.status not in _FINALIZABLE_TASK_STATUSES:
        raise ValueError(
            f"Task status {task.status!r} is incompatible with patch finalization."
        )
    if task.execution_policy != FILESYSTEM_MUTATION_EXECUTION_POLICY:
        raise ValueError("Patch finalization requires a filesystem_mutation task.")
    if task.requires_causal_change is not True:
        raise ValueError("Patch finalization requires task causal-change policy.")

    task_scope = {
        str(path or "").strip().replace("\\", "/") for path in task.files_in_scope
    }
    for path in evidence["files_changed"]:
        if path.replace("\\", "/") not in task_scope:
            raise ValueError(
                f"Reviewed file {path!r} is outside task files_in_scope."
            )

    previous_status = task.status
    finalization_id = f"patch_apply_task_finalization_{uuid4().hex[:8]}"
    finalization = {
        "artifact_type": PATCH_APPLY_TASK_FINALIZATION_ARTIFACT_TYPE,
        "finalization_id": finalization_id,
        "task_id": safe_task_id,
        "apply_id": evidence["apply_id"],
        "proposal_id": evidence["proposal_id"],
        "authorization_id": evidence["authorization_id"],
        "decision": "task_completed",
        "previous_task_status": previous_status,
        "new_task_status": "completed",
        "completed": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence_summary": {
            "phase_100_decision": ELIGIBLE_FOR_COMPLETION,
            "files_changed": evidence["files_changed"],
            "causal_change_observed": True,
            "requires_verification": True,
            "semantic_correctness_independently_proven": False,
            "semantic_correctness_caveat": (
                "Finalization relies on supplied Phase 100 eligibility evidence; "
                "semantic correctness is not independently proven."
            ),
        },
        "source": PATCH_APPLY_TASK_FINALIZATION_SOURCE,
        "patch_applied_by_finalization": False,
        "provider_executed": False,
        "model_executed": False,
        "runtime_executed": False,
    }

    task.status = "completed"
    run_manager.save_task(task)
    try:
        path = patch_apply_task_finalization_path(finalization_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(finalization, indent=2), encoding="utf-8")
    except Exception:
        task.status = previous_status
        run_manager.save_task(task)
        raise
    return finalization


def load_patch_apply_task_finalization(finalization_id: str) -> dict[str, Any]:
    safe_id = validate_record_id(finalization_id, label="finalization id")
    path = patch_apply_task_finalization_path(safe_id)
    finalization = json.loads(path.read_text(encoding="utf-8"))
    if (
        finalization.get("artifact_type")
        != PATCH_APPLY_TASK_FINALIZATION_ARTIFACT_TYPE
    ):
        raise ValueError("Stored artifact is not a patch apply task finalization.")
    if finalization.get("finalization_id") != safe_id:
        raise ValueError(
            "Stored finalization id does not match the requested finalization id."
        )
    return finalization
