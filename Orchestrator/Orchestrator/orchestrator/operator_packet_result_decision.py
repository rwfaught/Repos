from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.current_success_result_review import review_current_success_task_result
from orchestrator.paths import DATA_DIR, validate_record_id
from orchestrator.alpha_runtime import SCHEMA_VERSION, atomic_write_json, load_json_record


PACKET_OPERATOR_DECISION_RECORDS_DIR = DATA_DIR / "packet_operator_decision_records"

SUPPORTED_DECISIONS = {"accepted", "rejected"}

_SMUGGLED_PROVIDER_RUNTIME_FIELDS = {
    "model",
    "model_name",
    "runtime",
    "runtime_name",
    "platform",
    "platform_name",
    "provider",
    "provider_name",
    "ollama_model",
    "openclaw_runtime",
    "hermes_runtime",
    "allow_live_provider",
}

_NO_ACTIVITY_FLAGS = {
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
    "autonomous_ai_coding_claimed": False,
    "production_readiness_claimed": False,
    "semantic_correctness_claimed": False,
}

_NON_PROOFS = [
    "no_semantic_correctness_proof",
    "no_live_provider_model_proof",
    "no_runtime_platform_proof",
    "no_autonomous_ai_coding_proof",
    "no_model_backed_generation_proof",
    "no_production_readiness_proof",
    "no_service_api_ui_dashboard_auth_deployment_proof",
    "no_general_answer_resumption",
]


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _blocked(
    *,
    task_id: str = "",
    decision: str = "",
    reason: str,
    blocked_conditions: list[str],
    missing_requirements: list[str] | None = None,
    review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "packet_result_operator_decision_surface": True,
        "operator_decision_record_created": False,
        "operator_decision": decision,
        "accepted": False,
        "rejected": False,
        "task_id": task_id,
        "operator_decision_record_id": "",
        "operator_decision_record_path": "",
        "reason": reason,
        "blocked_conditions": sorted(set(blocked_conditions)),
        "missing_requirements": sorted(set(missing_requirements or [])),
        "review_summary": review or {},
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        "non_proofs": list(_NON_PROOFS),
        **_NO_ACTIVITY_FLAGS,
    }


def _validate_optional_record_id(value: Any, *, label: str) -> tuple[str, str | None]:
    normalized = _normalize_string(value)
    if not normalized:
        return "", None
    try:
        return validate_record_id(normalized, label=label), None
    except ValueError as error:
        return "", str(error)


def _artifact_id(review: dict[str, Any]) -> str:
    artifact = review.get("artifact_summary") if isinstance(review.get("artifact_summary"), dict) else {}
    return _normalize_string(artifact.get("artifact_id"))


def _verifier_result_path(review: dict[str, Any]) -> str:
    verification = review.get("verification_summary") if isinstance(review.get("verification_summary"), dict) else {}
    return _normalize_string(verification.get("verifier_result_path"))


def _review_classification(review: dict[str, Any]) -> str:
    return _normalize_string(review.get("final_outcome_classification"))


def _input_smuggling_fields(decision_input: dict[str, Any]) -> list[str]:
    return sorted(
        field_name
        for field_name in _SMUGGLED_PROVIDER_RUNTIME_FIELDS
        if field_name in decision_input and _normalize_string(decision_input.get(field_name))
    )


def _latest_record_payloads(task_id: str) -> list[dict[str, Any]]:
    if not PACKET_OPERATOR_DECISION_RECORDS_DIR.exists():
        return []

    records: list[dict[str, Any]] = []
    for path in sorted(PACKET_OPERATOR_DECISION_RECORDS_DIR.glob("packet_decision_*.json")):
        try:
            payload = load_json_record(path, record_type="operator decision")
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        if _normalize_string(payload.get("task_id")) != task_id:
            continue
        records.append({"path": path, "payload": payload})
    return records


def latest_packet_result_operator_decision_summary(task_id: str) -> dict[str, Any]:
    normalized_task_id = _normalize_string(task_id)
    if not normalized_task_id:
        return {
            "operator_decision_record_present": False,
            "operator_decision": "",
            "accepted": False,
            "rejected": False,
            "operator_decision_record_id": "",
            "operator_decision_record_path": "",
        }

    records = _latest_record_payloads(normalized_task_id)
    if not records:
        return {
            "operator_decision_record_present": False,
            "operator_decision": "",
            "accepted": False,
            "rejected": False,
            "operator_decision_record_id": "",
            "operator_decision_record_path": "",
        }

    records.sort(key=lambda record: _normalize_string(record["payload"].get("decided_at")), reverse=True)
    latest = records[0]
    payload = latest["payload"]
    decision = _normalize_string(payload.get("operator_decision"))
    return {
        "operator_decision_record_present": True,
        "operator_decision": decision,
        "accepted": decision == "accepted",
        "rejected": decision == "rejected",
        "operator_decision_record_id": _normalize_string(payload.get("operator_decision_record_id")),
        "operator_decision_record_path": str(latest["path"]),
        "decided_at": _normalize_string(payload.get("decided_at")),
        "operator_note_present": bool(_normalize_string(payload.get("operator_note"))),
        "packet_id": _normalize_string(payload.get("packet_id")),
        "run_id": _normalize_string(payload.get("run_id")),
        "execution_artifact_id": _normalize_string(payload.get("execution_artifact_id")),
        "verifier_result_path": _normalize_string(payload.get("verifier_result_path")),
        "current_success_review_classification": _normalize_string(
            payload.get("current_success_review_classification")
        ),
        "rejection_is_not_automatic_product_failure": bool(
            payload.get("rejection_is_not_automatic_product_failure")
        ),
    }


def record_packet_result_operator_decision(decision_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(decision_input, dict):
        return _blocked(
            reason="Operator decision input must be a JSON object.",
            blocked_conditions=["json_object_input_required"],
            missing_requirements=["decision_input"],
        )

    decision = _normalize_string(decision_input.get("operator_decision") or decision_input.get("decision")).lower()
    task_id = _normalize_string(decision_input.get("task_id"))
    operator_note = _normalize_string(
        decision_input.get("operator_note")
        or decision_input.get("operator_reason")
        or decision_input.get("reason")
    )

    input_blocks: list[str] = []
    missing: list[str] = []
    if decision not in SUPPORTED_DECISIONS:
        input_blocks.append("unsupported_operator_decision")
        missing.append("operator_decision")
    if not task_id:
        input_blocks.append("task_id_required")
        missing.append("task_id")
    else:
        try:
            task_id = validate_record_id(task_id, label="task id")
        except ValueError as error:
            return _blocked(
                task_id="",
                decision=decision,
                reason="Task id is invalid.",
                blocked_conditions=["task_id_invalid"],
                missing_requirements=["task_id"],
                review={"detail": str(error)},
            )
    if not operator_note:
        input_blocks.append("operator_note_required")
        missing.append("operator_note")

    smuggled = _input_smuggling_fields(decision_input)
    if smuggled:
        input_blocks.append("provider_model_runtime_platform_smuggling_rejected")
        missing.extend(smuggled)

    packet_id, packet_id_error = _validate_optional_record_id(decision_input.get("packet_id"), label="packet id")
    if packet_id_error:
        input_blocks.append("packet_id_invalid")
        missing.append("packet_id")

    if input_blocks:
        return _blocked(
            task_id=task_id,
            decision=decision,
            reason="Operator decision input is incomplete or unsupported.",
            blocked_conditions=input_blocks,
            missing_requirements=missing,
        )

    review = review_current_success_task_result({"task_id": task_id})
    review_blocks: list[str] = []
    if not review.get("current_success_result_review_surface"):
        review_blocks.append("current_success_review_surface_missing")
    if not review.get("ready_for_operator_review"):
        review_blocks.append("current_success_result_not_ready_for_operator_review")
    if _review_classification(review) != "completed_current_state_success":
        review_blocks.append("completed_current_state_success_required")

    artifact_id = _artifact_id(review)
    verifier_path = _verifier_result_path(review)
    if not _normalize_string(review.get("run_id")):
        review_blocks.append("run_id_required")
    if not artifact_id:
        review_blocks.append("execution_artifact_id_required")
    if not verifier_path:
        review_blocks.append("verifier_result_path_required")

    if review_blocks:
        return _blocked(
            task_id=task_id,
            decision=decision,
            reason="Current-success result is not eligible for packet operator decision recording.",
            blocked_conditions=review_blocks,
            missing_requirements=[],
            review=review,
        )

    record_id = f"packet_decision_{uuid4().hex[:8]}"
    decided_at = datetime.now(timezone.utc).isoformat()
    record = {
        "schema_version": SCHEMA_VERSION,
        "operator_decision_record_id": record_id,
        "packet_id": packet_id,
        "task_id": task_id,
        "run_id": _normalize_string(review.get("run_id")),
        "execution_artifact_id": artifact_id,
        "verifier_result_path": verifier_path,
        "current_success_review_classification": _review_classification(review),
        "operator_decision": decision,
        "accepted": decision == "accepted",
        "rejected": decision == "rejected",
        "operator_note": operator_note,
        "decided_at": decided_at,
        "caveats": [
            "Operator acceptance records a bounded decision under stated caveats; it does not prove semantic correctness.",
            "Operator acceptance does not prove autonomous AI coding, model-backed generation, live provider/model execution, runtime/platform behavior, or production readiness.",
            "Operator rejection preserves the operator decision and reason; it does not automatically mutate the task into product failure.",
        ],
        "rejection_is_not_automatic_product_failure": decision == "rejected",
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        "non_proofs": list(_NON_PROOFS),
    }

    record_path = PACKET_OPERATOR_DECISION_RECORDS_DIR / f"{record_id}.json"
    atomic_write_json(record_path, record)

    return {
        "packet_result_operator_decision_surface": True,
        "operator_decision_record_created": True,
        "operator_decision": decision,
        "accepted": decision == "accepted",
        "rejected": decision == "rejected",
        "task_id": task_id,
        "packet_id": packet_id,
        "run_id": record["run_id"],
        "execution_artifact_id": artifact_id,
        "verifier_result_path": verifier_path,
        "current_success_review_classification": record["current_success_review_classification"],
        "operator_decision_record_id": record_id,
        "operator_decision_record_path": str(record_path),
        "rejection_is_not_automatic_product_failure": decision == "rejected",
        "review_summary": {
            "final_outcome_classification": review.get("final_outcome_classification"),
            "ready_for_operator_review": review.get("ready_for_operator_review"),
            "execution_artifact_id": artifact_id,
            "verifier_result_path": verifier_path,
        },
        "next_action": "packet_result_operator_decision_record_persisted",
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        "non_proofs": list(_NON_PROOFS),
        **_NO_ACTIVITY_FLAGS,
    }
