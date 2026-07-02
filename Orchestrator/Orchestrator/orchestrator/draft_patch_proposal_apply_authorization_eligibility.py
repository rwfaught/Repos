from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any

from orchestrator.paths import resolve_declared_project_path, validate_record_id
from orchestrator.promoted_candidate_draft_patch_proposal import (
    load_draft_patch_proposal,
)


AUTHORIZATION_ELIGIBLE = "authorization_eligible"
AUTHORIZATION_INELIGIBLE = "authorization_ineligible"
AUTHORIZATION_BLOCKED = "authorization_blocked"

_PROMOTED_STATUS = "candidate_ready_for_later_patch_proposal_boundary"
_PROMOTE_DECISION = "promote_to_patch_proposal_candidate_ready"
_ACCEPTED_PACKET_DECISIONS = {
    "accept_packet_result",
    "accepted",
    "operator_accepted",
}
_STRUCTURED_PATCH_FIELDS = ("proposed_changes", "unified_diff", "rationale")

_NO_ACTIVITY_FLAGS = {
    "authorization_eligibility_evaluated": True,
    "apply_authorization_created": False,
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
    "authorization_eligibility_is_not_apply_authorization",
    "authorization_eligibility_does_not_apply_patch",
    "draft_creation_is_not_apply_authorization",
    "candidate_promotion_is_not_apply_authorization",
    "candidate_creation_is_not_apply_authorization",
    "packet_acceptance_is_not_apply_authorization",
    "no_semantic_correctness_proof",
    "no_live_provider_model_proof",
    "no_runtime_platform_proof",
    "no_autonomous_ai_coding_proof",
    "no_model_backed_generation_proof",
    "no_production_readiness_proof",
]

_CAVEATS = [
    "authorization_eligibility_only",
    "operator_apply_authorization_required_later",
    "no_patch_apply_performed",
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
    "authorize apply": "existing_apply_authorization_rejected",
    "authorized for apply": "existing_apply_authorization_rejected",
    "apply authorization": "existing_apply_authorization_rejected",
    "apply patch": "existing_apply_rejected",
    "patch applied": "existing_apply_rejected",
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_sequence(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _result(
    *,
    status: str,
    reason_code: str,
    draft: dict[str, Any] | None = None,
    missing_evidence: list[str] | None = None,
    linked_evidence: list[dict[str, Any]] | None = None,
    caveats: list[str] | None = None,
    blocked_conditions: list[str] | None = None,
    detail: str = "",
) -> dict[str, Any]:
    draft = draft or {}
    return {
        "draft_patch_proposal_apply_authorization_eligibility_surface": True,
        "draft_proposal_id": _normalize_text(draft.get("draft_proposal_id")),
        "authorization_eligibility_status": status,
        "reason_code": reason_code,
        "eligible": status == AUTHORIZATION_ELIGIBLE,
        "ineligible": status == AUTHORIZATION_INELIGIBLE,
        "blocked": status == AUTHORIZATION_BLOCKED,
        "missing_evidence": sorted(set(missing_evidence or [])),
        "linked_evidence": linked_evidence or [],
        "caveats": list(dict.fromkeys([*(caveats or []), *_CAVEATS])),
        "non_proofs": list(_NON_PROOFS),
        "explicit_no_authorization_statement": (
            "No apply authorization has been granted by this eligibility readback."
        ),
        "explicit_no_apply_statement": (
            "No patch apply has been invoked or performed by this eligibility readback."
        ),
        "no_apply_authorization": True,
        "apply_authorization_created": False,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "blocked_conditions": sorted(set(blocked_conditions or [])),
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        **_NO_ACTIVITY_FLAGS,
    }


def _load_draft(readback_input: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    draft = _as_mapping(
        readback_input.get("draft_proposal")
        or readback_input.get("draft_patch_proposal")
        or readback_input.get("draft")
    )
    if draft:
        return draft, ""
    draft_id = _normalize_text(
        readback_input.get("draft_proposal_id") or readback_input.get("draft_id")
    )
    if not draft_id:
        return None, "draft_proposal_required"
    try:
        safe_draft_id = validate_record_id(draft_id, label="draft proposal id")
        return load_draft_patch_proposal(safe_draft_id), ""
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return None, str(error)


def _validate_embedded_ids(draft: dict[str, Any]) -> tuple[list[str], list[str]]:
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
            missing.append(
                f"proposed_patch_evidence_payload.proposed_changes.{index}.path"
            )
            blocked.append("ambiguous_patch_payload_rejected")
            continue
        if PurePosixPath(path).is_absolute() or PureWindowsPath(path).is_absolute():
            missing.append(
                f"proposed_patch_evidence_payload.proposed_changes.{index}.path"
            )
            blocked.append("absolute_patch_path_rejected")
            continue
        if "\\" in path:
            missing.append(
                f"proposed_patch_evidence_payload.proposed_changes.{index}.path"
            )
            blocked.append("unsafe_patch_path_rejected")
            continue
        try:
            resolve_declared_project_path(path)
        except ValueError as error:
            missing.append(
                f"proposed_patch_evidence_payload.proposed_changes.{index}.path"
            )
            text = str(error)
            if "absolute" in text:
                blocked.append("absolute_patch_path_rejected")
            elif "parent traversal" in text or "outside" in text:
                blocked.append("path_traversal_rejected")
            else:
                blocked.append("unsafe_patch_path_rejected")
    return missing, blocked


def _latest_promotion_record(readback_input: dict[str, Any]) -> dict[str, Any]:
    records = [
        record
        for record in _as_sequence(readback_input.get("promotion_records"))
        if isinstance(record, dict)
    ]
    if not records:
        return {}
    return sorted(
        records,
        key=lambda record: _normalize_text(
            record.get("created_at")
            or record.get("decided_at")
            or record.get("timestamp")
        ),
    )[-1]


def _accepted_decision_ok(draft: dict[str, Any], candidate: dict[str, Any]) -> bool:
    decision = _normalize_text(
        candidate.get("operator_decision")
        or draft.get("operator_decision")
        or _as_mapping(candidate.get("eligibility_record")).get("operator_decision")
        or _as_mapping(candidate.get("eligibility_record")).get("accepted_packet_decision")
    )
    if not decision:
        return True
    return decision in _ACCEPTED_PACKET_DECISIONS


def evaluate_draft_patch_proposal_apply_authorization_eligibility(
    readback_input: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(readback_input, dict):
        return _result(
            status=AUTHORIZATION_BLOCKED,
            reason_code="json_object_input_required",
            missing_evidence=["readback_input"],
            blocked_conditions=["json_object_input_required"],
        )

    draft, load_error = _load_draft(readback_input)
    if draft is None:
        return _result(
            status=AUTHORIZATION_BLOCKED,
            reason_code="draft_proposal_missing",
            missing_evidence=["draft_proposal"],
            blocked_conditions=["draft_proposal_missing"],
            detail=load_error,
        )

    candidate = _as_mapping(draft.get("phase_289_candidate_reference"))
    promotion = _as_mapping(draft.get("phase_290_promotion_reference"))
    eligibility = _as_mapping(draft.get("phase_288_eligibility_reference"))
    current_success = _as_mapping(draft.get("current_success_review_reference"))
    patch_payload = _as_mapping(draft.get("proposed_patch_evidence_payload"))

    missing: list[str] = []
    blocked: list[str] = []
    linked = list(draft.get("linked_evidence", []))
    caveats = list(draft.get("caveats", []))

    id_missing, id_blocked = _validate_embedded_ids(draft)
    missing.extend(id_missing)
    blocked.extend(id_blocked)

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
    if draft.get("apply_authorization_created") or draft.get("authorized_for_apply"):
        missing.append("no_existing_apply_authorization")
        blocked.append("existing_apply_authorization_rejected")

    if not candidate:
        missing.append("phase_289_candidate_reference")
        blocked.append("promoted_candidate_link_missing")
    if not promotion:
        missing.append("phase_290_promotion_reference")
        blocked.append("promoted_candidate_link_missing")
    if not eligibility:
        missing.append("phase_288_eligibility_reference")
        blocked.append("accepted_packet_result_link_missing")
    if not current_success:
        missing.append("current_success_review_reference")
        blocked.append("current_success_reference_missing")

    if candidate and candidate.get("candidate_status") != "candidate_only":
        missing.append("candidate_status_candidate_only")
        blocked.append("candidate_only_status_required")
    if promotion and (
        promotion.get("promotion_status") != _PROMOTED_STATUS
        or promotion.get("operator_decision") != _PROMOTE_DECISION
    ):
        missing.append("promoted_candidate_decision")
        blocked.append("latest_negative_candidate_promotion_decision")
    latest_promotion = _latest_promotion_record(readback_input)
    if latest_promotion and (
        latest_promotion.get("promotion_status") != _PROMOTED_STATUS
        or latest_promotion.get("operator_decision") != _PROMOTE_DECISION
    ):
        missing.append("latest_promoted_candidate_decision")
        blocked.append("latest_negative_candidate_promotion_decision")

    if eligibility and eligibility.get("status") != "eligible":
        missing.append("eligible_phase_288_record")
        blocked.append("accepted_packet_result_link_missing")
    if candidate and not _accepted_decision_ok(draft, candidate):
        missing.append("accepted_packet_decision")
        blocked.append("accepted_packet_decision_mismatch")
    if current_success and (
        current_success.get("classification") != "completed_current_state_success"
        or not current_success.get("ready_for_operator_review")
    ):
        missing.append("current_success_completed_success_reference")
        blocked.append("current_success_reference_not_ready")

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

    patch_missing, patch_blocked = _patch_payload_blocks(patch_payload)
    missing.extend(patch_missing)
    blocked.extend(patch_blocked)
    claim_blocks = _claim_blocks(draft, candidate, promotion, eligibility, patch_payload)
    missing.extend(claim_blocks)
    blocked.extend(claim_blocks)

    if draft.get("source_candidate_id"):
        linked.append(
            {
                "evidence_type": "phase_289_candidate_artifact",
                "evidence_id": _normalize_text(draft.get("source_candidate_id")),
            }
        )
    if draft.get("source_promotion_record_id"):
        linked.append(
            {
                "evidence_type": "phase_290_promotion_record",
                "evidence_id": _normalize_text(draft.get("source_promotion_record_id")),
            }
        )
    if draft.get("source_execution_artifact_id"):
        linked.append(
            {
                "evidence_type": "execution_artifact",
                "evidence_id": _normalize_text(draft.get("source_execution_artifact_id")),
                "path": _normalize_text(draft.get("source_execution_artifact_path")),
            }
        )
    if draft.get("source_verifier_result_path"):
        linked.append(
            {
                "evidence_type": "verifier_result",
                "evidence_id": "",
                "path": _normalize_text(draft.get("source_verifier_result_path")),
            }
        )

    if blocked:
        return _result(
            status=AUTHORIZATION_BLOCKED,
            reason_code=sorted(set(blocked))[0],
            draft=draft,
            missing_evidence=missing,
            linked_evidence=linked,
            caveats=caveats,
            blocked_conditions=blocked,
        )

    return _result(
        status=AUTHORIZATION_ELIGIBLE,
        reason_code="draft_patch_proposal_has_authorization_eligibility_evidence",
        draft=draft,
        missing_evidence=[],
        linked_evidence=linked,
        caveats=caveats,
    )


def draft_patch_proposal_apply_authorization_eligibility_summary(
    draft_proposal_id: str,
) -> dict[str, Any]:
    return evaluate_draft_patch_proposal_apply_authorization_eligibility(
        {"draft_proposal_id": draft_proposal_id}
    )
