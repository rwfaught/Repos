from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.packet_result_patch_proposal_eligibility import (
    evaluate_packet_result_patch_proposal_eligibility,
)
from orchestrator.paths import DATA_DIR, record_path, validate_record_id


PACKET_PATCH_PROPOSAL_CANDIDATES_DIR = DATA_DIR / "packet_patch_proposal_candidates"

_NO_ACTIVITY_FLAGS = {
    "patch_proposal_created": False,
    "patch_apply_authorized": False,
    "patch_applied": False,
    "execution_performed": False,
    "artifact_created": True,
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
    "candidate_artifact_is_not_patch_authorization",
    "candidate_artifact_is_not_patch_apply_request",
    "packet_acceptance_is_not_patch_authorization",
    "eligibility_is_not_patch_authorization",
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
    eligibility: dict[str, Any] | None = None,
    detail: str = "",
) -> dict[str, Any]:
    return {
        "packet_result_patch_proposal_candidate_surface": True,
        "candidate_artifact_created": False,
        "candidate_status": "blocked",
        "reason_code": reason_code,
        "missing_requirements": sorted(set(missing_requirements or [])),
        "blocked_conditions": sorted(set(blocked_conditions or [])),
        "detail": detail,
        "eligibility_summary": eligibility or {},
        "candidate_id": "",
        "candidate_path": "",
        "no_apply_authorization": True,
        "candidate_is_not_patch_authorization": True,
        "candidate_is_not_patch_apply_request": True,
        "patch_proposal_created": False,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "non_proofs": list(_NON_PROOFS),
        "no_activity_flags": {**_NO_ACTIVITY_FLAGS, "artifact_created": False},
        **{**_NO_ACTIVITY_FLAGS, "artifact_created": False},
    }


def _candidate_path(candidate_id: str) -> Path:
    return record_path(
        PACKET_PATCH_PROPOSAL_CANDIDATES_DIR,
        candidate_id,
        label="candidate id",
    )


def _patch_candidate_evidence(packet_result: dict[str, Any]) -> dict[str, Any]:
    evidence = packet_result.get("structured_patch_candidate_evidence")
    if not isinstance(evidence, dict):
        evidence = packet_result.get("patch_candidate_evidence")
    return evidence if isinstance(evidence, dict) else {}


def create_packet_result_patch_proposal_candidate(
    candidate_input: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(candidate_input, dict):
        return _blocked(
            reason_code="json_object_input_required",
            missing_requirements=["candidate_input"],
            blocked_conditions=["json_object_input_required"],
        )

    candidate_note = _normalize_text(
        candidate_input.get("candidate_note")
        or candidate_input.get("candidate_reason")
        or candidate_input.get("reason")
    )
    if not candidate_note:
        return _blocked(
            reason_code="candidate_note_required",
            missing_requirements=["candidate_note"],
            blocked_conditions=["candidate_note_required"],
        )

    requested_candidate_id = _normalize_text(candidate_input.get("candidate_id"))
    if requested_candidate_id:
        try:
            candidate_id = validate_record_id(
                requested_candidate_id,
                label="candidate id",
            )
        except ValueError as error:
            return _blocked(
                reason_code="candidate_id_invalid",
                missing_requirements=["candidate_id"],
                blocked_conditions=["candidate_id_invalid"],
                detail=str(error),
            )
    else:
        candidate_id = f"packet_patch_candidate_{uuid4().hex[:8]}"

    eligibility_input = _as_mapping(candidate_input.get("eligibility_input"))
    if not eligibility_input:
        eligibility_input = {
            key: value
            for key, value in candidate_input.items()
            if key not in {"candidate_id", "candidate_note", "candidate_reason", "reason"}
        }
    eligibility = _as_mapping(candidate_input.get("eligibility"))
    if not eligibility:
        eligibility = evaluate_packet_result_patch_proposal_eligibility(eligibility_input)

    if eligibility.get("status") != "eligible":
        return _blocked(
            reason_code="eligible_packet_result_required",
            missing_requirements=list(eligibility.get("missing_evidence", [])),
            blocked_conditions=[
                "eligible_packet_result_required",
                _normalize_text(eligibility.get("reason_code")) or "eligibility_not_met",
            ],
            eligibility=eligibility,
        )

    packet_result = _as_mapping(eligibility_input.get("packet_result"))
    current_success = _as_mapping(eligibility_input.get("current_success_review"))
    decision = _as_mapping(eligibility_input.get("operator_decision_summary"))
    artifact_summary = _as_mapping(current_success.get("artifact_summary"))
    verification_summary = _as_mapping(current_success.get("verification_summary"))
    patch_evidence = _patch_candidate_evidence(packet_result)

    now = datetime.now(timezone.utc).isoformat()
    candidate = {
        "packet_result_patch_proposal_candidate_surface": True,
        "artifact_type": "packet_result_patch_proposal_candidate",
        "candidate_id": candidate_id,
        "candidate_status": "candidate_only",
        "source_packet_id": _normalize_text(eligibility.get("packet_id")),
        "source_run_id": _normalize_text(eligibility.get("run_id")),
        "source_task_id": _normalize_text(eligibility.get("task_id")),
        "source_execution_artifact_id": _normalize_text(
            artifact_summary.get("artifact_id")
            or decision.get("execution_artifact_id")
            or packet_result.get("execution_artifact_id")
        ),
        "source_execution_artifact_path": _normalize_text(
            artifact_summary.get("artifact_path")
            or packet_result.get("execution_artifact_path")
        ),
        "source_verifier_result_path": _normalize_text(
            verification_summary.get("verifier_result_path")
            or decision.get("verifier_result_path")
            or packet_result.get("verifier_result_path")
        ),
        "current_success_review_reference": {
            "task_id": _normalize_text(current_success.get("task_id")),
            "run_id": _normalize_text(current_success.get("run_id")),
            "classification": _normalize_text(current_success.get("final_outcome_classification")),
            "ready_for_operator_review": bool(current_success.get("ready_for_operator_review")),
        },
        "operator_decision_record_id": _normalize_text(
            decision.get("operator_decision_record_id")
        ),
        "operator_decision_record_path": _normalize_text(
            decision.get("operator_decision_record_path")
        ),
        "operator_decision": _normalize_text(decision.get("operator_decision")),
        "operator_note_present": bool(decision.get("operator_note_present")),
        "eligibility_record": eligibility,
        "candidate_note": candidate_note,
        "proposed_patch_evidence_payload": patch_evidence,
        "missing_or_ambiguous_patch_fields": list(eligibility.get("missing_evidence", [])),
        "linked_evidence": list(eligibility.get("linked_evidence", [])),
        "caveats": list(eligibility.get("caveats", [])),
        "non_proofs": list(_NON_PROOFS),
        "created_at": now,
        "no_apply_authorization": True,
        "candidate_is_not_patch_authorization": True,
        "candidate_is_not_patch_apply_request": True,
        "patch_proposal_created": False,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        **_NO_ACTIVITY_FLAGS,
    }

    PACKET_PATCH_PROPOSAL_CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
    path = _candidate_path(candidate_id)
    path.write_text(json.dumps(candidate, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "packet_result_patch_proposal_candidate_surface": True,
        "candidate_artifact_created": True,
        "candidate_status": "candidate_only",
        "candidate_id": candidate_id,
        "candidate_path": str(path),
        "source_task_id": candidate["source_task_id"],
        "source_packet_id": candidate["source_packet_id"],
        "source_run_id": candidate["source_run_id"],
        "eligibility_summary": eligibility,
        "no_apply_authorization": True,
        "candidate_is_not_patch_authorization": True,
        "candidate_is_not_patch_apply_request": True,
        "patch_proposal_created": False,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "non_proofs": list(_NON_PROOFS),
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        **_NO_ACTIVITY_FLAGS,
    }


def load_packet_result_patch_proposal_candidate(candidate_id: str) -> dict[str, Any]:
    path = _candidate_path(validate_record_id(candidate_id, label="candidate id"))
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("artifact_type") != "packet_result_patch_proposal_candidate":
        raise ValueError("Stored artifact is not a packet patch proposal candidate.")
    if payload.get("candidate_id") != candidate_id:
        raise ValueError("Stored candidate id does not match the requested candidate id.")
    return payload
