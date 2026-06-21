from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from orchestrator.current_success_result_review import review_current_success_task_result
from orchestrator.paths import DATA_DIR


ACCEPTANCE_RECORDS_DIR = DATA_DIR / "acceptance_records"

_NO_EXECUTION_FLAGS = {
    "task_created": False,
    "task_mutated": False,
    "task_executed": False,
    "execution_performed": False,
    "artifact_created": False,
    "artifact_mutated": False,
    "verifier_invoked": False,
    "reviewer_invoked": False,
    "provider_executed": False,
    "runtime_executed": False,
    "model_executed": False,
    "planner_invoked": False,
    "platform_invoked": False,
    "openclaw_invoked": False,
    "discord_invoked": False,
    "bridge_invoked": False,
    "adapter_invoked": False,
    "followup_task_created": False,
    "repair_task_created": False,
}


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "accepted", "acknowledged"}
    return False


def _blocked(task_id: str, reason: str, blocked_conditions: list[str], review: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "current_success_acceptance_record_surface": True,
        "acceptance_record_created": False,
        "accepted": False,
        "task_id": task_id,
        "acceptance_record_id": "",
        "acceptance_record_path": "",
        "reason": reason,
        "blocked_conditions": sorted(set(blocked_conditions)),
        "review_summary": review or {},
        **_NO_EXECUTION_FLAGS,
    }


def _latest_verifier_result_path(review: dict[str, Any]) -> str:
    verification = review.get("verification_summary") if isinstance(review.get("verification_summary"), dict) else {}
    return _normalize_string(verification.get("verifier_result_path"))


def _artifact_id(review: dict[str, Any]) -> str:
    artifact = review.get("artifact_summary") if isinstance(review.get("artifact_summary"), dict) else {}
    return _normalize_string(artifact.get("artifact_id"))


def _task_summary_value(review: dict[str, Any], key: str) -> Any:
    task_summary = review.get("task_summary") if isinstance(review.get("task_summary"), dict) else {}
    return task_summary.get(key)


def record_current_success_result_acceptance(acceptance_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(acceptance_input, dict):
        return _blocked(
            task_id="",
            reason="Acceptance input must be a JSON object.",
            blocked_conditions=["json_object_input_required"],
        )

    task_id = _normalize_string(acceptance_input.get("task_id"))
    if not task_id:
        return _blocked(
            task_id="",
            reason="Task id is required.",
            blocked_conditions=["task_id_required"],
        )

    accepted = _normalize_bool(acceptance_input.get("accepted"))
    operator_note = _normalize_string(
        acceptance_input.get("operator_note")
        or acceptance_input.get("acceptance_note")
        or acceptance_input.get("reason")
    )
    verification_ack = _normalize_bool(acceptance_input.get("verification_caveat_acknowledged"))
    provider_ack = _normalize_bool(acceptance_input.get("provider_caveat_acknowledged"))

    input_blocks: list[str] = []
    if not accepted:
        input_blocks.append("explicit_acceptance_required")
    if not operator_note:
        input_blocks.append("operator_note_required")
    if not verification_ack:
        input_blocks.append("verification_caveat_acknowledgement_required")
    if not provider_ack:
        input_blocks.append("provider_caveat_acknowledgement_required")

    if input_blocks:
        return _blocked(
            task_id=task_id,
            reason="Acceptance input is incomplete or non-accepting.",
            blocked_conditions=input_blocks,
        )

    review = review_current_success_task_result({"task_id": task_id})

    review_blocks: list[str] = []
    if not review.get("current_success_result_review_surface"):
        review_blocks.append("current_success_review_surface_missing")
    if not review.get("ready_for_operator_review"):
        review_blocks.append("current_success_result_not_ready_for_operator_review")
    if review.get("final_outcome_classification") != "completed_current_state_success":
        review_blocks.append("completed_current_state_success_required")

    verification = review.get("verification_summary") if isinstance(review.get("verification_summary"), dict) else {}
    if verification.get("overall_passed") is not True:
        review_blocks.append("deterministic_verification_pass_required")

    artifact_id = _artifact_id(review)
    verifier_result_path = _latest_verifier_result_path(review)
    if not artifact_id:
        review_blocks.append("execution_artifact_id_required")
    if not verifier_result_path:
        review_blocks.append("verifier_result_path_required")

    if review_blocks:
        return _blocked(
            task_id=task_id,
            reason="Current-success result is not eligible for operator acceptance recording.",
            blocked_conditions=review_blocks,
            review=review,
        )

    record_id = f"acceptance_{uuid4().hex[:8]}"
    accepted_at = datetime.now(timezone.utc).isoformat()
    record = {
        "acceptance_record_id": record_id,
        "task_id": task_id,
        "run_id": _normalize_string(review.get("run_id")),
        "execution_artifact_id": artifact_id,
        "verifier_result_path": verifier_result_path,
        "accepted": True,
        "accepted_at": accepted_at,
        "operator_note": operator_note,
        "result_classification_accepted": "completed_current_state_success",
        "verification_caveat_acknowledged": True,
        "provider_caveat_acknowledged": True,
        "verification_caveat": "Deterministic verification is a bounded tripwire only; it does not prove semantic correctness, production readiness, or task adequacy in the strong sense.",
        "provider_caveat": "If the provider was local_file, this acceptance does not prove autonomous AI coding, model-backed generation, or runtime/model execution.",
        "task_files_in_scope": list(_task_summary_value(review, "files_in_scope") or []),
        "no_execution_flags": dict(_NO_EXECUTION_FLAGS),
    }

    ACCEPTANCE_RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    record_path = ACCEPTANCE_RECORDS_DIR / f"{record_id}.json"
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    return {
        "current_success_acceptance_record_surface": True,
        "acceptance_record_created": True,
        "accepted": True,
        "task_id": task_id,
        "run_id": record["run_id"],
        "acceptance_record_id": record_id,
        "acceptance_record_path": str(record_path),
        "result_classification_accepted": "completed_current_state_success",
        "verification_caveat_acknowledged": True,
        "provider_caveat_acknowledged": True,
        "review_summary": {
            "final_outcome_classification": review.get("final_outcome_classification"),
            "ready_for_operator_review": review.get("ready_for_operator_review"),
            "verification_overall_passed": verification.get("overall_passed"),
            "execution_artifact_id": artifact_id,
            "verifier_result_path": verifier_result_path,
        },
        "next_action": "operator_acceptance_record_persisted_for_completed_current_success_result",
        **_NO_EXECUTION_FLAGS,
    }
