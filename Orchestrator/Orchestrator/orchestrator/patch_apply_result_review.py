from __future__ import annotations

from typing import Any

from orchestrator.patch_apply_engine import (
    PATCH_APPLY_RESULT_ARTIFACT_TYPE,
    load_patch_apply_result,
)
from orchestrator.paths import resolve_declared_project_path, validate_record_id


ELIGIBLE_FOR_COMPLETION = "eligible_for_completion"
NEEDS_REVIEW = "needs_review"
REJECTED = "rejected"
INSUFFICIENT_EVIDENCE = "insufficient_evidence"


def _review(
    *,
    decision: str,
    apply_id: str,
    expected_task_id: str,
    result: dict[str, Any] | None,
    reasons: list[str],
) -> dict[str, Any]:
    result = result or {}
    files_changed = result.get("files_changed")
    operations_applied = result.get("operations_applied")
    return {
        "decision": decision,
        "eligible_for_completion": decision == ELIGIBLE_FOR_COMPLETION,
        "apply_id": result.get("apply_id") or apply_id,
        "proposal_id": result.get("proposal_id"),
        "authorization_id": result.get("authorization_id"),
        "task_id": result.get("task_id"),
        "expected_task_id": expected_task_id,
        "files_changed": list(files_changed) if isinstance(files_changed, list) else [],
        "operations_applied": (
            list(operations_applied) if isinstance(operations_applied, list) else []
        ),
        "requires_verification": result.get("requires_verification"),
        "causal_change_observed": result.get("causal_change_observed"),
        "reasons": reasons,
        "task_completed": False,
        "task_state_mutated": False,
        "patch_applied_by_review": False,
    }


def _non_empty_id(value: Any, *, label: str) -> str:
    return validate_record_id(value, label=label)


def _valid_sha256(value: Any) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(
        character in "0123456789abcdefABCDEF" for character in text
    )


def review_patch_apply_result(
    apply_id: str,
    *,
    expected_task_id: str,
) -> dict[str, Any]:
    safe_apply_id = validate_record_id(apply_id, label="apply id")
    expected_task = validate_record_id(expected_task_id, label="expected task id")

    try:
        result = load_patch_apply_result(safe_apply_id)
    except FileNotFoundError:
        return _review(
            decision=INSUFFICIENT_EVIDENCE,
            apply_id=safe_apply_id,
            expected_task_id=expected_task,
            result=None,
            reasons=["Patch apply result evidence does not exist."],
        )
    except (TypeError, ValueError):
        return _review(
            decision=REJECTED,
            apply_id=safe_apply_id,
            expected_task_id=expected_task,
            result=None,
            reasons=["Stored patch apply result is structurally invalid."],
        )

    reasons: list[str] = []
    if result.get("artifact_type") != PATCH_APPLY_RESULT_ARTIFACT_TYPE:
        reasons.append("Artifact type is not patch_apply_result.")

    for field, label in (
        ("apply_id", "apply id"),
        ("proposal_id", "proposal id"),
        ("authorization_id", "authorization id"),
        ("task_id", "task id"),
    ):
        try:
            _non_empty_id(result.get(field), label=label)
        except (TypeError, ValueError):
            reasons.append(f"{field} is missing or invalid.")

    if result.get("task_id") != expected_task:
        reasons.append("Apply result task_id does not match the expected task.")

    files_changed = result.get("files_changed")
    bounded_files: list[str] = []
    if not isinstance(files_changed, list) or not files_changed:
        reasons.append("files_changed must be a non-empty list.")
    else:
        for raw_path in files_changed:
            path = str(raw_path or "").strip()
            try:
                resolve_declared_project_path(path)
            except (TypeError, ValueError) as exc:
                reasons.append(f"files_changed path {path!r} is invalid: {exc}")
            else:
                bounded_files.append(path)

    before_sha256 = result.get("before_sha256")
    after_sha256 = result.get("after_sha256")
    if not isinstance(before_sha256, dict) or not isinstance(after_sha256, dict):
        reasons.append("before_sha256 and after_sha256 must be objects.")
    else:
        for path in bounded_files:
            before_hash = before_sha256.get(path)
            after_hash = after_sha256.get(path)
            if not _valid_sha256(before_hash) or not _valid_sha256(after_hash):
                reasons.append(f"Changed file {path!r} requires valid before/after SHA-256.")
            elif before_hash == after_hash:
                reasons.append(f"Changed file {path!r} has identical before/after SHA-256.")

    operations = result.get("operations_applied")
    if not isinstance(operations, list) or not operations:
        reasons.append("operations_applied must be a non-empty list.")
    elif any(not isinstance(operation, dict) for operation in operations):
        reasons.append("Each operations_applied entry must be an object.")

    if result.get("causal_change_observed") is not True:
        reasons.append("causal_change_observed must be true.")
    if result.get("requires_verification") is not True:
        reasons.append("requires_verification must be true.")

    decision = REJECTED if reasons else ELIGIBLE_FOR_COMPLETION
    return _review(
        decision=decision,
        apply_id=safe_apply_id,
        expected_task_id=expected_task,
        result=result,
        reasons=reasons,
    )
