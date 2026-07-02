from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from uuid import uuid4

from orchestrator.draft_patch_proposal_apply_authorization_eligibility import (
    AUTHORIZATION_ELIGIBLE,
    evaluate_draft_patch_proposal_apply_authorization_eligibility,
)
from orchestrator.paths import DATA_DIR, record_path, resolve_declared_project_path, validate_record_id
from orchestrator.promoted_candidate_draft_patch_proposal import load_draft_patch_proposal


DRAFT_PATCH_PROPOSAL_APPLY_AUTHORIZATIONS_DIR = (
    DATA_DIR / "draft_patch_proposal_apply_authorizations"
)

AUTHORIZE_APPLY = "authorize_apply"
REJECT_APPLY_AUTHORIZATION = "reject_apply_authorization"
DEFER_APPLY_AUTHORIZATION = "defer_apply_authorization"
SUPPORTED_AUTHORIZATION_DECISIONS = {
    AUTHORIZE_APPLY,
    REJECT_APPLY_AUTHORIZATION,
    DEFER_APPLY_AUTHORIZATION,
}

_STRUCTURED_PATCH_FIELDS = ("proposed_changes", "unified_diff", "rationale")
_AUTHORIZED_STATUS = "authorized_for_later_bounded_apply"
_REJECTED_STATUS = "apply_authorization_rejected"
_DEFERRED_STATUS = "apply_authorization_deferred"
_PROMOTED_STATUS = "candidate_ready_for_later_patch_proposal_boundary"
_PROMOTE_DECISION = "promote_to_patch_proposal_candidate_ready"
_ACCEPTED_PACKET_DECISIONS = {
    "accept_packet_result",
    "accepted",
    "operator_accepted",
}

_NO_ACTIVITY_FLAGS = {
    "operator_apply_authorization_record_created": False,
    "apply_authorization_created": False,
    "patch_apply_authorized": False,
    "patch_applied": False,
    "apply_result_created": False,
    "patch_task_finalized": False,
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
    "apply_authorization_record_is_not_patch_apply_execution",
    "apply_authorization_record_does_not_create_apply_result",
    "apply_authorization_record_does_not_finalize_task",
    "authorization_does_not_prove_patch_will_apply_cleanly",
    "authorization_does_not_prove_semantic_correctness",
    "authorization_does_not_prove_production_readiness",
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
    "patch_apply_authorized": "existing_apply_authorization_rejected",
    "apply_authorized": "existing_apply_authorization_rejected",
    "authorized_for_apply": "existing_apply_authorization_rejected",
    "patch_applied": "existing_apply_rejected",
    "apply_result_created": "apply_result_smuggling_rejected",
    "patch_task_finalized": "finalization_smuggling_rejected",
}

_SMUGGLED_TEXT_CLAIMS = {
    "provider": "provider_model_runtime_platform_claim_rejected",
    "model": "provider_model_runtime_platform_claim_rejected",
    "runtime": "provider_model_runtime_platform_claim_rejected",
    "platform": "provider_model_runtime_platform_claim_rejected",
    "ollama": "provider_model_runtime_platform_claim_rejected",
    "semantic correctness": "semantic_correctness_claim_is_non_proof",
    "semantically correct": "semantic_correctness_claim_is_non_proof",
    "autonomous coding": "autonomous_ai_coding_claim_rejected",
    "autonomous ai coding": "autonomous_ai_coding_claim_rejected",
    "production ready": "production_readiness_claim_rejected",
    "production-readiness": "production_readiness_claim_rejected",
    "production readiness": "production_readiness_claim_rejected",
    "apply patch": "apply_execution_smuggling_rejected",
    "patch applied": "existing_apply_rejected",
    "apply result": "apply_result_smuggling_rejected",
    "finalize": "finalization_smuggling_rejected",
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_sequence(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _authorization_path(authorization_id: str) -> Path:
    return record_path(
        DRAFT_PATCH_PROPOSAL_APPLY_AUTHORIZATIONS_DIR,
        authorization_id,
        label="authorization id",
    )


def _blocked(
    *,
    reason_code: str,
    draft: dict[str, Any] | None = None,
    eligibility: dict[str, Any] | None = None,
    missing_requirements: list[str] | None = None,
    blocked_conditions: list[str] | None = None,
    detail: str = "",
) -> dict[str, Any]:
    draft = draft or {}
    return {
        "draft_patch_proposal_apply_authorization_record_surface": True,
        "operator_apply_authorization_record_created": False,
        "authorization_status": "blocked",
        "authorization_decision": "",
        "reason_code": reason_code,
        "missing_requirements": sorted(set(missing_requirements or [])),
        "blocked_conditions": sorted(set(blocked_conditions or [])),
        "detail": detail,
        "draft_proposal_id": _normalize_text(draft.get("draft_proposal_id")),
        "authorization_id": "",
        "authorization_record_path": "",
        "eligibility_record": eligibility or {},
        "apply_authorization_created": False,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "apply_result_created": False,
        "patch_task_finalized": False,
        "explicit_authorization_only_statement": (
            "Authorization record only; patch not applied."
        ),
        "explicit_semantic_correctness_not_proven_statement": (
            "Semantic correctness is not proven by this authorization record."
        ),
        "explicit_production_readiness_not_proven_statement": (
            "Production readiness is not proven by this authorization record."
        ),
        "non_proofs": list(_NON_PROOFS),
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        **_NO_ACTIVITY_FLAGS,
    }


def _load_draft(input_payload: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    draft = _as_mapping(
        input_payload.get("draft_proposal")
        or input_payload.get("draft_patch_proposal")
        or input_payload.get("draft")
    )
    if draft:
        return draft, ""
    draft_id = _normalize_text(input_payload.get("draft_proposal_id") or input_payload.get("draft_id"))
    if not draft_id:
        return None, "draft_proposal_required"
    try:
        safe_draft_id = validate_record_id(draft_id, label="draft proposal id")
        return load_draft_patch_proposal(safe_draft_id), ""
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return None, str(error)


def _validate_ids(draft: dict[str, Any]) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    blocked: list[str] = []
    for field_name in (
        "draft_proposal_id",
        "source_candidate_id",
        "source_promotion_record_id",
        "source_packet_id",
        "source_run_id",
        "source_task_id",
        "source_execution_artifact_id",
        "operator_decision_record_id",
    ):
        value = _normalize_text(draft.get(field_name))
        if not value:
            missing.append(field_name)
            blocked.append("linked_evidence_id_missing")
            continue
        try:
            validate_record_id(value, label=field_name)
        except ValueError:
            missing.append(field_name)
            blocked.append("path_traversal_or_absolute_id_rejected")
    return missing, blocked


def _claim_blocks(*payloads: dict[str, Any]) -> list[str]:
    blocks: list[str] = []
    for payload in payloads:
        for field_name, reason_code in _SMUGGLED_CLAIM_FIELDS.items():
            value = payload.get(field_name)
            present = value if isinstance(value, bool) else bool(_normalize_text(value))
            if present:
                blocks.append(reason_code)
        for value in payload.values():
            if isinstance(value, str):
                normalized = value.casefold()
                for needle, reason_code in _SMUGGLED_TEXT_CLAIMS.items():
                    if needle in normalized:
                        blocks.append(reason_code)
    return sorted(set(blocks))


def _patch_payload_blocks(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    missing = [
        f"proposed_patch_evidence_payload.{field_name}"
        for field_name in _STRUCTURED_PATCH_FIELDS
        if not payload.get(field_name)
    ]
    blocked: list[str] = []
    if missing:
        blocked.append("structured_patch_payload_missing")
    changes = payload.get("proposed_changes")
    if not isinstance(changes, list) or not changes:
        missing.append("proposed_patch_evidence_payload.proposed_changes")
        blocked.append("structured_patch_payload_missing")
        return missing, blocked
    for index, change in enumerate(changes):
        if not isinstance(change, dict):
            missing.append(f"proposed_patch_evidence_payload.proposed_changes.{index}")
            blocked.append("ambiguous_patch_payload_rejected")
            continue
        path = _normalize_text(change.get("path"))
        if not path:
            missing.append(f"proposed_patch_evidence_payload.proposed_changes.{index}.path")
            blocked.append("ambiguous_patch_payload_rejected")
            continue
        if PurePosixPath(path).is_absolute() or PureWindowsPath(path).is_absolute():
            missing.append(f"proposed_patch_evidence_payload.proposed_changes.{index}.path")
            blocked.append("absolute_patch_path_rejected")
            continue
        if "\\" in path:
            missing.append(f"proposed_patch_evidence_payload.proposed_changes.{index}.path")
            blocked.append("unsafe_patch_path_rejected")
            continue
        try:
            resolve_declared_project_path(path)
        except ValueError as error:
            missing.append(f"proposed_patch_evidence_payload.proposed_changes.{index}.path")
            text = str(error)
            if "absolute" in text:
                blocked.append("absolute_patch_path_rejected")
            elif "parent traversal" in text or "outside" in text:
                blocked.append("path_traversal_rejected")
            else:
                blocked.append("unsafe_patch_path_rejected")
    return missing, blocked


def _duplicate_blocks(
    *,
    draft_id: str,
    authorization_records: list[Any],
) -> tuple[list[str], list[str]]:
    for record in authorization_records:
        if not isinstance(record, dict):
            continue
        if _normalize_text(record.get("draft_proposal_id")) == draft_id:
            return ["existing_apply_authorization_record"], [
                "duplicate_apply_authorization_record_rejected"
            ]
    return [], []


def _draft_evidence_blocks(draft: dict[str, Any]) -> tuple[list[str], list[str]]:
    candidate = _as_mapping(draft.get("phase_289_candidate_reference"))
    promotion = _as_mapping(draft.get("phase_290_promotion_reference"))
    packet_eligibility = _as_mapping(draft.get("phase_288_eligibility_reference"))
    current_success = _as_mapping(draft.get("current_success_review_reference"))

    missing: list[str] = []
    blocked: list[str] = []

    if candidate and candidate.get("candidate_status") != "candidate_only":
        missing.append("candidate_status_candidate_only")
        blocked.append("candidate_only_status_required")
    if promotion and (
        promotion.get("promotion_status") != _PROMOTED_STATUS
        or promotion.get("operator_decision") != _PROMOTE_DECISION
    ):
        missing.append("promoted_candidate_decision")
        blocked.append("latest_negative_candidate_promotion_decision")
    if current_success and (
        current_success.get("classification") != "completed_current_state_success"
        or not current_success.get("ready_for_operator_review")
    ):
        missing.append("current_success_completed_success_reference")
        blocked.append("current_success_reference_not_ready")

    accepted_decision = _normalize_text(
        candidate.get("operator_decision")
        or packet_eligibility.get("operator_decision")
        or packet_eligibility.get("accepted_packet_decision")
    )
    if accepted_decision and accepted_decision not in _ACCEPTED_PACKET_DECISIONS:
        missing.append("accepted_packet_decision")
        blocked.append("accepted_packet_decision_mismatch")

    for field_name in (
        "source_candidate_id",
        "source_packet_id",
        "source_run_id",
        "source_task_id",
        "source_execution_artifact_id",
        "source_execution_artifact_path",
        "source_verifier_result_path",
        "operator_decision_record_id",
    ):
        draft_value = _normalize_text(draft.get(field_name))
        candidate_value = _normalize_text(
            candidate.get(
                "candidate_id" if field_name == "source_candidate_id" else field_name
            )
        )
        if candidate and draft_value and candidate_value and draft_value != candidate_value:
            missing.append(f"matching_candidate_{field_name}")
            blocked.append("candidate_evidence_mismatch")

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
        draft_field = "source_candidate_id" if field_name == "candidate_id" else field_name
        draft_value = _normalize_text(draft.get(draft_field))
        promotion_value = _normalize_text(promotion.get(field_name))
        if promotion and draft_value and promotion_value and draft_value != promotion_value:
            missing.append(f"matching_promotion_{field_name}")
            blocked.append("candidate_evidence_mismatch")

    for field_name in ("task_id", "run_id"):
        draft_value = _normalize_text(draft.get(f"source_{field_name}"))
        current_value = _normalize_text(current_success.get(field_name))
        if current_success and draft_value and current_value and draft_value != current_value:
            missing.append(f"matching_current_success_{field_name}")
            blocked.append("current_success_reference_mismatch")

    return missing, blocked


def _eligibility_matches_draft(
    draft: dict[str, Any],
    eligibility: dict[str, Any],
) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    blocked: list[str] = []
    if eligibility.get("authorization_eligibility_status") != AUTHORIZATION_ELIGIBLE:
        missing.append("authorization_eligible_readback")
        blocked.append("authorization_eligibility_not_clean")
    if _normalize_text(eligibility.get("draft_proposal_id")) != _normalize_text(
        draft.get("draft_proposal_id")
    ):
        missing.append("matching_eligibility_draft_proposal_id")
        blocked.append("authorization_eligibility_draft_mismatch")
    return missing, blocked


def create_draft_patch_proposal_apply_authorization_record(
    authorization_input: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(authorization_input, dict):
        return _blocked(
            reason_code="json_object_input_required",
            missing_requirements=["authorization_input"],
            blocked_conditions=["json_object_input_required"],
        )

    draft, load_error = _load_draft(authorization_input)
    if draft is None:
        return _blocked(
            reason_code="draft_proposal_missing",
            missing_requirements=["draft_proposal"],
            blocked_conditions=["draft_proposal_missing"],
            detail=load_error,
        )

    decision = _normalize_text(
        authorization_input.get("authorization_decision")
        or authorization_input.get("operator_decision")
        or authorization_input.get("decision")
    )
    note = _normalize_text(
        authorization_input.get("operator_authorization_note")
        or authorization_input.get("authorization_note")
        or authorization_input.get("decision_reason")
        or authorization_input.get("reason")
    )
    if decision not in SUPPORTED_AUTHORIZATION_DECISIONS:
        return _blocked(
            reason_code="unsupported_authorization_decision",
            draft=draft,
            missing_requirements=["authorization_decision"],
            blocked_conditions=["unsupported_authorization_decision"],
        )
    if not note:
        return _blocked(
            reason_code="operator_authorization_note_required",
            draft=draft,
            missing_requirements=["operator_authorization_note"],
            blocked_conditions=["operator_authorization_note_required"],
        )

    eligibility = _as_mapping(
        authorization_input.get("authorization_eligibility")
        or authorization_input.get("eligibility_record")
        or authorization_input.get("eligibility")
    )
    if not eligibility:
        return _blocked(
            reason_code="authorization_eligibility_required",
            draft=draft,
            missing_requirements=["authorization_eligibility"],
            blocked_conditions=["authorization_eligibility_required"],
        )

    candidate = _as_mapping(draft.get("phase_289_candidate_reference"))
    promotion = _as_mapping(draft.get("phase_290_promotion_reference"))
    packet_eligibility = _as_mapping(draft.get("phase_288_eligibility_reference"))
    current_success = _as_mapping(draft.get("current_success_review_reference"))
    patch_payload = _as_mapping(draft.get("proposed_patch_evidence_payload"))

    missing: list[str] = []
    blocked: list[str] = []

    id_missing, id_blocked = _validate_ids(draft)
    missing.extend(id_missing)
    blocked.extend(id_blocked)
    eligibility_missing, eligibility_blocked = _eligibility_matches_draft(draft, eligibility)
    missing.extend(eligibility_missing)
    blocked.extend(eligibility_blocked)

    if draft.get("artifact_type") != "draft_patch_proposal":
        missing.append("artifact_type_draft_patch_proposal")
        blocked.append("draft_proposal_artifact_required")
    if draft.get("draft_proposal_status") != "draft_only" or not draft.get("draft_only"):
        missing.append("draft_only_status")
        blocked.append("draft_only_status_required")
    if not draft.get("not_authorized_for_apply") or draft.get("patch_apply_authorized"):
        missing.append("not_authorized_for_apply")
        blocked.append("existing_apply_authorization_rejected")
    if not draft.get("not_applied") or draft.get("patch_applied"):
        missing.append("not_applied")
        blocked.append("existing_apply_rejected")
    if not candidate:
        missing.append("phase_289_candidate_reference")
        blocked.append("promoted_candidate_link_missing")
    if not promotion:
        missing.append("phase_290_promotion_reference")
        blocked.append("promoted_candidate_link_missing")
    if not packet_eligibility or packet_eligibility.get("status") != "eligible":
        missing.append("phase_288_eligibility_reference")
        blocked.append("accepted_packet_result_link_missing")
    if not current_success:
        missing.append("current_success_review_reference")
        blocked.append("current_success_reference_missing")
    evidence_missing, evidence_blocked = _draft_evidence_blocks(draft)
    missing.extend(evidence_missing)
    blocked.extend(evidence_blocked)

    patch_missing, patch_blocked = _patch_payload_blocks(patch_payload)
    missing.extend(patch_missing)
    blocked.extend(patch_blocked)
    duplicate_missing, duplicate_blocked = _duplicate_blocks(
        draft_id=_normalize_text(draft.get("draft_proposal_id")),
        authorization_records=_as_sequence(authorization_input.get("authorization_records")),
    )
    missing.extend(duplicate_missing)
    blocked.extend(duplicate_blocked)

    claim_blocks = _claim_blocks(
        authorization_input,
        draft,
        eligibility,
        candidate,
        promotion,
        packet_eligibility,
        patch_payload,
    )
    missing.extend(claim_blocks)
    blocked.extend(claim_blocks)

    if blocked:
        return _blocked(
            reason_code=sorted(set(blocked))[0],
            draft=draft,
            eligibility=eligibility,
            missing_requirements=missing,
            blocked_conditions=blocked,
        )

    authorization_id = _normalize_text(
        authorization_input.get("authorization_id")
        or f"draft_apply_authorization_{uuid4().hex[:8]}"
    )
    try:
        authorization_id = validate_record_id(authorization_id, label="authorization id")
    except ValueError as error:
        return _blocked(
            reason_code="authorization_id_invalid",
            draft=draft,
            eligibility=eligibility,
            missing_requirements=["authorization_id"],
            blocked_conditions=["authorization_id_invalid"],
            detail=str(error),
        )

    now = datetime.now(timezone.utc).isoformat()
    is_authorized = decision == AUTHORIZE_APPLY
    status = {
        AUTHORIZE_APPLY: _AUTHORIZED_STATUS,
        REJECT_APPLY_AUTHORIZATION: _REJECTED_STATUS,
        DEFER_APPLY_AUTHORIZATION: _DEFERRED_STATUS,
    }[decision]
    linked_evidence = list(eligibility.get("linked_evidence", []))
    record = {
        "draft_patch_proposal_apply_authorization_record_surface": True,
        "artifact_type": "draft_patch_proposal_apply_authorization_record",
        "authorization_id": authorization_id,
        "authorization_decision": decision,
        "operator_decision": decision,
        "authorization_status": status,
        "draft_proposal_id": _normalize_text(draft.get("draft_proposal_id")),
        "eligibility_record": eligibility,
        "source_packet_id": _normalize_text(draft.get("source_packet_id")),
        "source_run_id": _normalize_text(draft.get("source_run_id")),
        "source_task_id": _normalize_text(draft.get("source_task_id")),
        "source_execution_artifact_id": _normalize_text(draft.get("source_execution_artifact_id")),
        "source_execution_artifact_path": _normalize_text(draft.get("source_execution_artifact_path")),
        "source_verifier_result_id": _normalize_text(draft.get("source_verifier_result_id")),
        "source_verifier_result_path": _normalize_text(draft.get("source_verifier_result_path")),
        "current_success_review_reference": current_success,
        "operator_packet_acceptance_decision_reference": {
            "operator_decision_record_id": _normalize_text(draft.get("operator_decision_record_id")),
            "operator_decision_record_path": _normalize_text(draft.get("operator_decision_record_path")),
            "operator_decision": _normalize_text(candidate.get("operator_decision")),
        },
        "phase_288_eligibility_reference": packet_eligibility,
        "phase_289_candidate_reference": candidate,
        "phase_290_promotion_reference": promotion,
        "phase_294_draft_proposal_reference": draft,
        "phase_296_authorization_eligibility_reference": eligibility,
        "operator_authorization_note": note,
        "operator_authorization_reason": note,
        "linked_evidence": linked_evidence,
        "caveats": list(dict.fromkeys([*draft.get("caveats", []), *eligibility.get("caveats", [])])),
        "non_proofs": list(_NON_PROOFS),
        "created_at": now,
        "timestamp": now,
        "explicit_authorization_only_statement": (
            "Authorization record only; patch not applied."
        ),
        "explicit_semantic_correctness_not_proven_statement": (
            "Semantic correctness is not proven by this authorization record."
        ),
        "explicit_production_readiness_not_proven_statement": (
            "Production readiness is not proven by this authorization record."
        ),
        "apply_authorization_created": is_authorized,
        "patch_apply_authorized": is_authorized,
        "patch_applied": False,
        "apply_result_created": False,
        "patch_task_finalized": False,
        "requires_later_bounded_apply_boundary": is_authorized,
        "no_activity_flags": {
            **_NO_ACTIVITY_FLAGS,
            "operator_apply_authorization_record_created": True,
            "apply_authorization_created": is_authorized,
            "patch_apply_authorized": is_authorized,
            "artifact_created": True,
        },
        **{
            **_NO_ACTIVITY_FLAGS,
            "operator_apply_authorization_record_created": True,
            "apply_authorization_created": is_authorized,
            "patch_apply_authorized": is_authorized,
            "artifact_created": True,
        },
    }

    DRAFT_PATCH_PROPOSAL_APPLY_AUTHORIZATIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = _authorization_path(authorization_id)
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "draft_patch_proposal_apply_authorization_record_surface": True,
        "operator_apply_authorization_record_created": True,
        "authorization_id": authorization_id,
        "authorization_record_path": str(path),
        "authorization_decision": decision,
        "authorization_status": status,
        "draft_proposal_id": record["draft_proposal_id"],
        "reason_code": status,
        "apply_authorization_created": is_authorized,
        "patch_apply_authorized": is_authorized,
        "patch_applied": False,
        "apply_result_created": False,
        "patch_task_finalized": False,
        "explicit_authorization_only_statement": record["explicit_authorization_only_statement"],
        "explicit_semantic_correctness_not_proven_statement": record[
            "explicit_semantic_correctness_not_proven_statement"
        ],
        "explicit_production_readiness_not_proven_statement": record[
            "explicit_production_readiness_not_proven_statement"
        ],
        "non_proofs": list(_NON_PROOFS),
        "no_activity_flags": record["no_activity_flags"],
        **record["no_activity_flags"],
    }


def load_draft_patch_proposal_apply_authorization_record(
    authorization_id: str,
) -> dict[str, Any]:
    safe_id = validate_record_id(authorization_id, label="authorization id")
    payload = json.loads(_authorization_path(safe_id).read_text(encoding="utf-8"))
    if payload.get("artifact_type") != "draft_patch_proposal_apply_authorization_record":
        raise ValueError("Stored artifact is not a draft proposal apply authorization record.")
    if payload.get("authorization_id") != safe_id:
        raise ValueError("Stored authorization id does not match.")
    return payload
