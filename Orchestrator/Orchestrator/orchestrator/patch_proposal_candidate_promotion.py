from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.packet_result_patch_proposal_candidate import (
    load_packet_result_patch_proposal_candidate,
)
from orchestrator.paths import DATA_DIR, record_path, validate_record_id


PATCH_PROPOSAL_CANDIDATE_PROMOTIONS_DIR = DATA_DIR / "patch_proposal_candidate_promotions"

SUPPORTED_PROMOTION_DECISIONS = {
    "promote_to_patch_proposal_candidate_ready",
    "reject_candidate",
    "defer_candidate",
}

_NO_ACTIVITY_FLAGS = {
    "promotion_record_created": False,
    "patch_proposal_created": False,
    "patch_apply_authorized": False,
    "patch_applied": False,
    "execution_performed": False,
    "artifact_created": False,
    "artifact_mutated": False,
    "provider_executed": False,
    "runtime_executed": False,
    "model_executed": False,
    "platform_invoked": False,
    "autonomous_ai_coding_claimed": False,
    "production_readiness_claimed": False,
    "semantic_correctness_claimed": False,
}

_NON_PROOFS = [
    "promotion_record_is_not_patch_apply_authorization",
    "promotion_record_does_not_apply_patch",
    "accepted_packet_decision_alone_does_not_promote_candidate",
    "candidate_creation_is_not_patch_authorization",
    "no_semantic_correctness_proof",
    "no_live_provider_model_proof",
    "no_runtime_platform_proof",
    "no_autonomous_ai_coding_proof",
    "no_model_backed_generation_proof",
    "no_production_readiness_proof",
]


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _blocked(
    *,
    reason_code: str,
    missing_requirements: list[str] | None = None,
    blocked_conditions: list[str] | None = None,
    detail: str = "",
    candidate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "patch_proposal_candidate_promotion_surface": True,
        "promotion_record_created": False,
        "promotion_status": "blocked",
        "operator_decision": "",
        "reason_code": reason_code,
        "missing_requirements": sorted(set(missing_requirements or [])),
        "blocked_conditions": sorted(set(blocked_conditions or [])),
        "detail": detail,
        "candidate_summary": candidate or {},
        "promotion_record_id": "",
        "promotion_record_path": "",
        "patch_proposal_created": False,
        "no_apply_authorization": True,
        "promotion_is_not_patch_apply_authorization": True,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "non_proofs": list(_NON_PROOFS),
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        **_NO_ACTIVITY_FLAGS,
    }


def _promotion_path(record_id: str) -> Path:
    return record_path(
        PATCH_PROPOSAL_CANDIDATE_PROMOTIONS_DIR,
        record_id,
        label="promotion record id",
    )


def _load_candidate(promotion_input: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    candidate = _as_mapping(promotion_input.get("candidate"))
    if candidate:
        return candidate, None

    candidate_id = _normalize_text(promotion_input.get("candidate_id"))
    if not candidate_id:
        return None, _blocked(
            reason_code="candidate_id_required",
            missing_requirements=["candidate_id"],
            blocked_conditions=["candidate_id_required"],
        )
    try:
        safe_candidate_id = validate_record_id(candidate_id, label="candidate id")
        return load_packet_result_patch_proposal_candidate(safe_candidate_id), None
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return None, _blocked(
            reason_code="candidate_unreadable",
            missing_requirements=["candidate"],
            blocked_conditions=["candidate_unreadable"],
            detail=str(error),
        )


def create_patch_proposal_candidate_promotion_record(
    promotion_input: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(promotion_input, dict):
        return _blocked(
            reason_code="json_object_input_required",
            missing_requirements=["promotion_input"],
            blocked_conditions=["json_object_input_required"],
        )

    decision = _normalize_text(
        promotion_input.get("operator_decision")
        or promotion_input.get("decision")
    )
    note = _normalize_text(
        promotion_input.get("operator_note")
        or promotion_input.get("promotion_note")
        or promotion_input.get("reason")
    )

    if decision not in SUPPORTED_PROMOTION_DECISIONS:
        return _blocked(
            reason_code="unsupported_promotion_decision",
            missing_requirements=["operator_decision"],
            blocked_conditions=["unsupported_promotion_decision"],
        )
    if not note:
        return _blocked(
            reason_code="promotion_note_required",
            missing_requirements=["operator_note"],
            blocked_conditions=["promotion_note_required"],
        )

    candidate, load_block = _load_candidate(promotion_input)
    if load_block is not None:
        return load_block
    assert candidate is not None

    blocked: list[str] = []
    missing: list[str] = []
    if candidate.get("candidate_status") != "candidate_only":
        blocked.append("candidate_only_status_required")
        missing.append("candidate_status_candidate_only")
    eligibility = _as_mapping(candidate.get("eligibility_record"))
    if eligibility.get("status") != "eligible":
        blocked.append("eligible_candidate_required")
        missing.append("eligible_candidate")
    if not candidate.get("no_apply_authorization") or candidate.get("patch_apply_authorized"):
        blocked.append("apply_authorization_smuggling_rejected")
        missing.append("no_apply_authorization")
    if candidate.get("patch_applied"):
        blocked.append("applied_candidate_rejected")
        missing.append("unapplied_candidate")
    if not _normalize_text(candidate.get("source_task_id")):
        blocked.append("candidate_source_task_id_required")
        missing.append("source_task_id")
    if not _normalize_text(candidate.get("source_execution_artifact_id")):
        blocked.append("candidate_execution_artifact_required")
        missing.append("source_execution_artifact_id")
    if not _normalize_text(candidate.get("source_verifier_result_path")):
        blocked.append("candidate_verifier_result_required")
        missing.append("source_verifier_result_path")

    if blocked:
        return _blocked(
            reason_code=sorted(set(blocked))[0],
            missing_requirements=missing,
            blocked_conditions=blocked,
            candidate=candidate,
        )

    record_id = f"candidate_promotion_{uuid4().hex[:8]}"
    decided_at = datetime.now(timezone.utc).isoformat()
    promotion_status = {
        "promote_to_patch_proposal_candidate_ready": "candidate_ready_for_later_patch_proposal_boundary",
        "reject_candidate": "candidate_rejected",
        "defer_candidate": "candidate_deferred",
    }[decision]
    record = {
        "patch_proposal_candidate_promotion_surface": True,
        "artifact_type": "patch_proposal_candidate_promotion_record",
        "promotion_record_id": record_id,
        "promotion_status": promotion_status,
        "operator_decision": decision,
        "operator_note": note,
        "candidate_id": _normalize_text(candidate.get("candidate_id")),
        "candidate_status": _normalize_text(candidate.get("candidate_status")),
        "source_packet_id": _normalize_text(candidate.get("source_packet_id")),
        "source_run_id": _normalize_text(candidate.get("source_run_id")),
        "source_task_id": _normalize_text(candidate.get("source_task_id")),
        "source_execution_artifact_id": _normalize_text(candidate.get("source_execution_artifact_id")),
        "source_execution_artifact_path": _normalize_text(candidate.get("source_execution_artifact_path")),
        "source_verifier_result_path": _normalize_text(candidate.get("source_verifier_result_path")),
        "operator_decision_record_id": _normalize_text(candidate.get("operator_decision_record_id")),
        "eligibility_record": eligibility,
        "candidate_reference": candidate,
        "decided_at": decided_at,
        "patch_proposal_created": False,
        "no_apply_authorization": True,
        "promotion_is_not_patch_apply_authorization": True,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "non_proofs": list(_NON_PROOFS),
        "no_activity_flags": {**_NO_ACTIVITY_FLAGS, "promotion_record_created": True, "artifact_created": True},
        **{**_NO_ACTIVITY_FLAGS, "promotion_record_created": True, "artifact_created": True},
    }

    PATCH_PROPOSAL_CANDIDATE_PROMOTIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = _promotion_path(record_id)
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "patch_proposal_candidate_promotion_surface": True,
        "promotion_record_created": True,
        "promotion_record_id": record_id,
        "promotion_record_path": str(path),
        "promotion_status": promotion_status,
        "operator_decision": decision,
        "candidate_id": record["candidate_id"],
        "source_task_id": record["source_task_id"],
        "patch_proposal_created": False,
        "no_apply_authorization": True,
        "promotion_is_not_patch_apply_authorization": True,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "non_proofs": list(_NON_PROOFS),
        "no_activity_flags": {**_NO_ACTIVITY_FLAGS, "promotion_record_created": True, "artifact_created": True},
        **{**_NO_ACTIVITY_FLAGS, "promotion_record_created": True, "artifact_created": True},
    }


def load_patch_proposal_candidate_promotion_record(record_id: str) -> dict[str, Any]:
    safe_record_id = validate_record_id(record_id, label="promotion record id")
    payload = json.loads(_promotion_path(safe_record_id).read_text(encoding="utf-8"))
    if payload.get("artifact_type") != "patch_proposal_candidate_promotion_record":
        raise ValueError("Stored artifact is not a candidate promotion record.")
    if payload.get("promotion_record_id") != safe_record_id:
        raise ValueError("Stored promotion record id does not match.")
    return payload
