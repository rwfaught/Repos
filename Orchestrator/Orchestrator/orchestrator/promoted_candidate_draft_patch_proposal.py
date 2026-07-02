from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.packet_result_patch_proposal_candidate import (
    load_packet_result_patch_proposal_candidate,
)
from orchestrator.patch_proposal_candidate_promotion import (
    load_patch_proposal_candidate_promotion_record,
)
from orchestrator.paths import DATA_DIR, record_path, validate_record_id


DRAFT_PATCH_PROPOSALS_DIR = DATA_DIR / "draft_patch_proposals"

_PROMOTED_STATUS = "candidate_ready_for_later_patch_proposal_boundary"
_PROMOTE_DECISION = "promote_to_patch_proposal_candidate_ready"
_STRUCTURED_PATCH_FIELDS = ("proposed_changes", "unified_diff", "rationale")

_NO_ACTIVITY_FLAGS = {
    "draft_patch_proposal_created": False,
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
    "draft_patch_proposal_is_not_apply_authorization",
    "draft_patch_proposal_does_not_apply_patch",
    "candidate_promotion_is_not_patch_apply_authorization",
    "candidate_creation_is_not_patch_authorization",
    "packet_acceptance_is_not_patch_authorization",
    "authorization_eligibility_not_evaluated",
    "no_semantic_correctness_proof",
    "no_live_provider_model_proof",
    "no_runtime_platform_proof",
    "no_autonomous_ai_coding_proof",
    "no_model_backed_generation_proof",
    "no_production_readiness_proof",
]

_SMUGGLED_CLAIM_FIELDS = {
    "provider": "provider_model_runtime_platform_claim_rejected",
    "provider_name": "provider_model_runtime_platform_claim_rejected",
    "model": "provider_model_runtime_platform_claim_rejected",
    "model_name": "provider_model_runtime_platform_claim_rejected",
    "runtime": "provider_model_runtime_platform_claim_rejected",
    "runtime_name": "provider_model_runtime_platform_claim_rejected",
    "platform": "provider_model_runtime_platform_claim_rejected",
    "platform_name": "provider_model_runtime_platform_claim_rejected",
    "semantic_correctness": "semantic_correctness_claim_is_non_proof",
    "semantic_correctness_claimed": "semantic_correctness_claim_is_non_proof",
    "autonomous_ai_coding": "autonomous_ai_coding_claim_rejected",
    "autonomous_ai_coding_claimed": "autonomous_ai_coding_claim_rejected",
    "production_ready": "production_readiness_claim_rejected",
    "production_readiness": "production_readiness_claim_rejected",
    "production_readiness_claimed": "production_readiness_claim_rejected",
    "patch_apply_authorized": "patch_apply_authorization_claim_rejected",
    "apply_authorized": "patch_apply_authorization_claim_rejected",
    "authorized_for_apply": "patch_apply_authorization_claim_rejected",
    "patch_applied": "patch_apply_claim_rejected",
}


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
    promotion: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "promoted_candidate_draft_patch_proposal_surface": True,
        "draft_patch_proposal_created": False,
        "draft_proposal_status": "blocked",
        "reason_code": reason_code,
        "missing_requirements": sorted(set(missing_requirements or [])),
        "blocked_conditions": sorted(set(blocked_conditions or [])),
        "detail": detail,
        "candidate_summary": candidate or {},
        "promotion_summary": promotion or {},
        "draft_proposal_id": "",
        "draft_proposal_path": "",
        "source_candidate_id": _normalize_text((candidate or {}).get("candidate_id")),
        "source_promotion_record_id": _normalize_text(
            (promotion or {}).get("promotion_record_id")
        ),
        "draft_only": False,
        "not_authorized_for_apply": True,
        "not_applied": True,
        "no_apply_authorization": True,
        "draft_proposal_is_not_patch_apply_authorization": True,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "non_proofs": list(_NON_PROOFS),
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        **_NO_ACTIVITY_FLAGS,
    }


def _draft_path(draft_id: str) -> Path:
    return record_path(
        DRAFT_PATCH_PROPOSALS_DIR,
        draft_id,
        label="draft proposal id",
    )


def _load_candidate(draft_input: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    candidate = _as_mapping(draft_input.get("candidate"))
    if candidate:
        return candidate, None

    candidate_id = _normalize_text(draft_input.get("candidate_id"))
    if not candidate_id:
        return None, _blocked(
            reason_code="candidate_required",
            missing_requirements=["candidate_id"],
            blocked_conditions=["candidate_required"],
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


def _load_promotion(draft_input: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    promotion = _as_mapping(draft_input.get("promotion_record"))
    if promotion:
        return promotion, None

    promotion_id = _normalize_text(
        draft_input.get("promotion_record_id") or draft_input.get("promotion_id")
    )
    if not promotion_id:
        return None, _blocked(
            reason_code="promotion_record_required",
            missing_requirements=["promotion_record_id"],
            blocked_conditions=["promotion_record_required"],
        )
    try:
        safe_promotion_id = validate_record_id(
            promotion_id,
            label="promotion record id",
        )
        return load_patch_proposal_candidate_promotion_record(safe_promotion_id), None
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return None, _blocked(
            reason_code="promotion_record_unreadable",
            missing_requirements=["promotion_record"],
            blocked_conditions=["promotion_record_unreadable"],
            detail=str(error),
        )


def _claim_blocks(*payloads: dict[str, Any]) -> list[str]:
    blocks: list[str] = []
    for payload in payloads:
        for field_name, reason_code in _SMUGGLED_CLAIM_FIELDS.items():
            value = payload.get(field_name)
            present = value if isinstance(value, bool) else bool(_normalize_text(value))
            if present:
                blocks.append(reason_code)
    return sorted(set(blocks))


def _missing_patch_fields(payload: dict[str, Any]) -> list[str]:
    return [
        f"proposed_patch_evidence_payload.{field_name}"
        for field_name in _STRUCTURED_PATCH_FIELDS
        if not payload.get(field_name)
    ]


def create_promoted_candidate_draft_patch_proposal(
    draft_input: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(draft_input, dict):
        return _blocked(
            reason_code="json_object_input_required",
            missing_requirements=["draft_input"],
            blocked_conditions=["json_object_input_required"],
        )

    draft_note = _normalize_text(
        draft_input.get("draft_note")
        or draft_input.get("draft_reason")
        or draft_input.get("reason")
    )
    if not draft_note:
        return _blocked(
            reason_code="draft_note_required",
            missing_requirements=["draft_note"],
            blocked_conditions=["draft_note_required"],
        )

    requested_draft_id = _normalize_text(
        draft_input.get("draft_proposal_id") or draft_input.get("draft_id")
    )
    if requested_draft_id:
        try:
            draft_id = validate_record_id(
                requested_draft_id,
                label="draft proposal id",
            )
        except ValueError as error:
            return _blocked(
                reason_code="draft_proposal_id_invalid",
                missing_requirements=["draft_proposal_id"],
                blocked_conditions=["draft_proposal_id_invalid"],
                detail=str(error),
            )
    else:
        draft_id = f"draft_patch_proposal_{uuid4().hex[:8]}"

    candidate, candidate_block = _load_candidate(draft_input)
    if candidate_block is not None:
        return candidate_block
    assert candidate is not None

    promotion, promotion_block = _load_promotion(draft_input)
    if promotion_block is not None:
        return _blocked(
            reason_code=promotion_block["reason_code"],
            missing_requirements=promotion_block["missing_requirements"],
            blocked_conditions=promotion_block["blocked_conditions"],
            detail=promotion_block.get("detail", ""),
            candidate=candidate,
        )
    assert promotion is not None

    missing: list[str] = []
    blocked: list[str] = []

    if candidate.get("candidate_status") != "candidate_only":
        missing.append("candidate_status_candidate_only")
        blocked.append("candidate_only_status_required")
    eligibility = _as_mapping(candidate.get("eligibility_record"))
    if eligibility.get("status") != "eligible":
        missing.append("eligible_candidate")
        blocked.append("eligible_candidate_required")
    if not candidate.get("no_apply_authorization") or candidate.get("patch_apply_authorized"):
        missing.append("no_apply_authorization")
        blocked.append("apply_authorization_smuggling_rejected")
    if candidate.get("patch_applied"):
        missing.append("unapplied_candidate")
        blocked.append("applied_candidate_rejected")

    if promotion.get("promotion_status") != _PROMOTED_STATUS:
        missing.append("promotion_status_promoted")
        blocked.append("promoted_candidate_required")
    if promotion.get("operator_decision") != _PROMOTE_DECISION:
        missing.append("operator_decision_promote")
        blocked.append("promotion_decision_not_promote")
    if not _normalize_text(promotion.get("operator_note")):
        missing.append("promotion_note")
        blocked.append("promotion_note_required")
    if not promotion.get("no_apply_authorization") or promotion.get("patch_apply_authorized"):
        missing.append("promotion_no_apply_authorization")
        blocked.append("promotion_apply_authorization_smuggling_rejected")
    if promotion.get("patch_applied"):
        missing.append("unapplied_promotion")
        blocked.append("promotion_applied_rejected")

    mismatch_fields = []
    for field_name in (
        "candidate_id",
        "source_packet_id",
        "source_run_id",
        "source_task_id",
        "source_execution_artifact_id",
        "source_execution_artifact_path",
        "source_verifier_result_path",
        "operator_decision_record_id",
    ):
        candidate_value = _normalize_text(candidate.get(field_name))
        promotion_value = _normalize_text(promotion.get(field_name))
        if candidate_value and promotion_value and candidate_value != promotion_value:
            mismatch_fields.append(field_name)
    if mismatch_fields:
        missing.extend([f"matching_{field_name}" for field_name in mismatch_fields])
        blocked.append("promotion_candidate_evidence_mismatch")

    patch_payload = _as_mapping(candidate.get("proposed_patch_evidence_payload"))
    missing_patch = _missing_patch_fields(patch_payload)
    if missing_patch:
        missing.extend(missing_patch)
        blocked.append("structured_patch_payload_missing")

    claim_blocks = _claim_blocks(draft_input, candidate, promotion, patch_payload)
    if claim_blocks:
        missing.extend(claim_blocks)
        blocked.extend(claim_blocks)

    if blocked:
        return _blocked(
            reason_code=sorted(set(blocked))[0],
            missing_requirements=missing,
            blocked_conditions=blocked,
            candidate=candidate,
            promotion=promotion,
        )

    now = datetime.now(timezone.utc).isoformat()
    linked_evidence = list(candidate.get("linked_evidence", []))
    linked_evidence.extend(
        [
            {
                "evidence_type": "phase_289_candidate_artifact",
                "evidence_id": _normalize_text(candidate.get("candidate_id")),
                "path": _normalize_text(draft_input.get("candidate_path")),
            },
            {
                "evidence_type": "phase_290_promotion_record",
                "evidence_id": _normalize_text(promotion.get("promotion_record_id")),
                "path": _normalize_text(draft_input.get("promotion_record_path")),
            },
        ]
    )

    draft = {
        "promoted_candidate_draft_patch_proposal_surface": True,
        "artifact_type": "draft_patch_proposal",
        "draft_proposal_id": draft_id,
        "draft_proposal_status": "draft_only",
        "source_candidate_id": _normalize_text(candidate.get("candidate_id")),
        "source_promotion_record_id": _normalize_text(
            promotion.get("promotion_record_id")
        ),
        "source_packet_id": _normalize_text(candidate.get("source_packet_id")),
        "source_run_id": _normalize_text(candidate.get("source_run_id")),
        "source_task_id": _normalize_text(candidate.get("source_task_id")),
        "source_execution_artifact_id": _normalize_text(
            candidate.get("source_execution_artifact_id")
        ),
        "source_execution_artifact_path": _normalize_text(
            candidate.get("source_execution_artifact_path")
        ),
        "source_verifier_result_path": _normalize_text(
            candidate.get("source_verifier_result_path")
        ),
        "current_success_review_reference": _as_mapping(
            candidate.get("current_success_review_reference")
        ),
        "operator_decision_record_id": _normalize_text(
            candidate.get("operator_decision_record_id")
        ),
        "operator_decision_record_path": _normalize_text(
            candidate.get("operator_decision_record_path")
        ),
        "phase_288_eligibility_reference": eligibility,
        "phase_289_candidate_reference": candidate,
        "phase_290_promotion_reference": promotion,
        "candidate_promotion_note": _normalize_text(promotion.get("operator_note")),
        "draft_creation_note": draft_note,
        "proposed_patch_evidence_payload": patch_payload,
        "proposed_changes": patch_payload["proposed_changes"],
        "unified_diff": patch_payload["unified_diff"],
        "proposed_diff": patch_payload["unified_diff"],
        "rationale": patch_payload["rationale"],
        "missing_or_ambiguous_patch_fields": [],
        "reason_code": "draft_patch_proposal_created",
        "linked_evidence": linked_evidence,
        "caveats": list(candidate.get("caveats", [])),
        "non_proofs": list(_NON_PROOFS),
        "created_at": now,
        "timestamp": now,
        "draft_only": True,
        "not_authorized_for_apply": True,
        "not_applied": True,
        "no_apply_authorization": True,
        "draft_proposal_is_not_patch_apply_authorization": True,
        "patch_proposal_created": False,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "authorization_eligibility_evaluated": False,
        "authorization_eligibility_status": "not_evaluated",
        "no_activity_flags": {
            **_NO_ACTIVITY_FLAGS,
            "draft_patch_proposal_created": True,
            "artifact_created": True,
        },
        **{
            **_NO_ACTIVITY_FLAGS,
            "draft_patch_proposal_created": True,
            "artifact_created": True,
        },
    }

    DRAFT_PATCH_PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    path = _draft_path(draft_id)
    path.write_text(json.dumps(draft, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "promoted_candidate_draft_patch_proposal_surface": True,
        "draft_patch_proposal_created": True,
        "draft_proposal_status": "draft_only",
        "reason_code": "draft_patch_proposal_created",
        "draft_proposal_id": draft_id,
        "draft_proposal_path": str(path),
        "source_candidate_id": draft["source_candidate_id"],
        "source_promotion_record_id": draft["source_promotion_record_id"],
        "source_task_id": draft["source_task_id"],
        "draft_only": True,
        "not_authorized_for_apply": True,
        "not_applied": True,
        "no_apply_authorization": True,
        "draft_proposal_is_not_patch_apply_authorization": True,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "non_proofs": list(_NON_PROOFS),
        "no_activity_flags": {
            **_NO_ACTIVITY_FLAGS,
            "draft_patch_proposal_created": True,
            "artifact_created": True,
        },
        **{
            **_NO_ACTIVITY_FLAGS,
            "draft_patch_proposal_created": True,
            "artifact_created": True,
        },
    }


def load_draft_patch_proposal(draft_proposal_id: str) -> dict[str, Any]:
    safe_draft_id = validate_record_id(
        draft_proposal_id,
        label="draft proposal id",
    )
    payload = json.loads(_draft_path(safe_draft_id).read_text(encoding="utf-8"))
    if payload.get("artifact_type") != "draft_patch_proposal":
        raise ValueError("Stored artifact is not a draft patch proposal.")
    if payload.get("draft_proposal_id") != safe_draft_id:
        raise ValueError("Stored draft proposal id does not match.")
    return payload
