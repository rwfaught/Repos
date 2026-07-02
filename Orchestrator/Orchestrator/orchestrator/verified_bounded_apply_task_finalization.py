from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from orchestrator import artifact_store
from orchestrator.authorized_bounded_apply_result_verification import (
    AUTHORIZED_BOUNDED_APPLY_RESULT_VERIFICATION_ARTIFACT_TYPE,
    MECHANICALLY_VERIFIED,
    load_authorized_bounded_apply_result_verification,
)
from orchestrator.paths import resolve_declared_project_path, validate_record_id


VERIFIED_BOUNDED_APPLY_TASK_FINALIZATION_ARTIFACT_TYPE = (
    "verified_bounded_apply_task_finalization"
)
VERIFIED_BOUNDED_APPLY_TASK_FINALIZATION_SOURCE = (
    "phase_311_verified_bounded_apply_task_finalization_record"
)
FINALIZATION_COMPLETED = "finalization_record_persisted"
FINALIZATION_BLOCKED = "finalization_blocked"
FINALIZATION_FAILED = "finalization_failed"

_NON_PROOFS = [
    "finalization_is_not_semantic_correctness",
    "finalization_is_not_production_readiness",
    "finalization_is_not_autonomous_ai_coding",
    "finalization_is_not_provider_model_runtime_execution",
    "finalization_does_not_declare_backbone_v0",
]
_REQUIRED_CHAIN_FIELDS = (
    "phase_294_draft_proposal_id",
    "phase_289_candidate_id",
    "source_packet_id",
    "source_task_id",
    "source_execution_artifact_id",
    "source_verifier_result_path",
    "operator_decision_record_id",
)
_SMUGGLED_FIELD_REASONS = {
    "semantic_correctness": "semantic_correctness_claim_is_non_proof",
    "semantic_correctness_claimed": "semantic_correctness_claim_is_non_proof",
    "semantic_correctness_proven": "semantic_correctness_claim_is_non_proof",
    "production_ready": "production_readiness_claim_rejected",
    "production_readiness": "production_readiness_claim_rejected",
    "production_readiness_claimed": "production_readiness_claim_rejected",
    "production_readiness_proven": "production_readiness_claim_rejected",
    "autonomous_ai_coding": "autonomous_ai_coding_claim_rejected",
    "autonomous_ai_coding_claimed": "autonomous_ai_coding_claim_rejected",
    "provider": "provider_model_runtime_platform_claim_rejected",
    "provider_name": "provider_model_runtime_platform_claim_rejected",
    "model": "provider_model_runtime_platform_claim_rejected",
    "model_name": "provider_model_runtime_platform_claim_rejected",
    "runtime": "provider_model_runtime_platform_claim_rejected",
    "runtime_name": "provider_model_runtime_platform_claim_rejected",
    "platform": "provider_model_runtime_platform_claim_rejected",
    "platform_name": "provider_model_runtime_platform_claim_rejected",
    "backbone_v0_declared": "backbone_v0_declaration_rejected",
}
_SMUGGLED_TEXT_REASONS = {
    "semantically correct": "semantic_correctness_claim_is_non_proof",
    "semantic correctness": "semantic_correctness_claim_is_non_proof",
    "production ready": "production_readiness_claim_rejected",
    "production readiness": "production_readiness_claim_rejected",
    "autonomous ai coding": "autonomous_ai_coding_claim_rejected",
    "autonomous coding": "autonomous_ai_coding_claim_rejected",
    "provider": "provider_model_runtime_platform_claim_rejected",
    "model": "provider_model_runtime_platform_claim_rejected",
    "runtime": "provider_model_runtime_platform_claim_rejected",
    "platform": "provider_model_runtime_platform_claim_rejected",
    "backbone v0": "backbone_v0_declaration_rejected",
}


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _path_identity(path: str) -> str:
    return path.replace("\\", "/")


def verified_bounded_apply_task_finalization_path(finalization_id: str):
    return artifact_store.artifact_path(
        validate_record_id(finalization_id, label="finalization id")
    )


def _claim_reason(payload: Any) -> str:
    if isinstance(payload, dict):
        for field, reason in _SMUGGLED_FIELD_REASONS.items():
            value = payload.get(field)
            present = value if isinstance(value, bool) else bool(_normalize_text(value))
            if present:
                return reason
        for key, value in payload.items():
            if key in {
                "artifact_type",
                "source",
                "non_proofs",
                "caveats",
                "reason_code",
                "timestamp",
                "created_at",
                "finalization_note",
                "operator_or_system_finalization_note",
                "explicit_semantic_correctness_not_proven_statement",
                "explicit_production_readiness_not_proven_statement",
                "explicit_model_provider_runtime_execution_not_proven_statement",
                "explicit_backbone_v0_not_declared_statement",
            }:
                continue
            reason = _claim_reason(value)
            if reason:
                return reason
    elif isinstance(payload, list):
        for value in payload:
            reason = _claim_reason(value)
            if reason:
                return reason
    elif isinstance(payload, str):
        normalized = payload.casefold()
        if (
            "not proven" in normalized
            or "non-proof" in normalized
            or "no proof" in normalized
            or "does not prove" in normalized
            or "not declared" in normalized
        ):
            return ""
        for needle, reason in _SMUGGLED_TEXT_REASONS.items():
            if needle in normalized:
                return reason
    return ""


def _blocked(
    *,
    reason_code: str,
    verification_id: str = "",
    apply_attempt_id: str = "",
    authorization_id: str = "",
    draft_proposal_id: str = "",
    finalization_note: str = "",
) -> dict[str, Any]:
    return {
        "artifact_type": VERIFIED_BOUNDED_APPLY_TASK_FINALIZATION_ARTIFACT_TYPE,
        "source": VERIFIED_BOUNDED_APPLY_TASK_FINALIZATION_SOURCE,
        "finalization_created": False,
        "finalization_id": "",
        "finalization_status": FINALIZATION_BLOCKED,
        "reason_code": reason_code,
        "verification_id": verification_id,
        "apply_attempt_id": apply_attempt_id,
        "authorization_id": authorization_id,
        "draft_proposal_id": draft_proposal_id,
        "candidate_id": "",
        "packet_task_artifact_verifier_current_success_references": {},
        "files_mechanically_verified": [],
        "operator_or_system_finalization_note": finalization_note,
        "semantic_correctness_not_proven": True,
        "production_readiness_not_proven": True,
        "model_provider_runtime_not_proven": True,
        "autonomous_ai_coding_not_proven": True,
        "backbone_v0_not_declared": True,
        "explicit_semantic_correctness_not_proven_statement": (
            "Semantic correctness is not proven by this finalization record."
        ),
        "explicit_production_readiness_not_proven_statement": (
            "Production readiness is not proven by this finalization record."
        ),
        "explicit_model_provider_runtime_execution_not_proven_statement": (
            "Model/provider/runtime execution is not proven by this finalization record."
        ),
        "explicit_backbone_v0_not_declared_statement": (
            "Backbone V0 is not declared by this finalization record."
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "caveats": ["finalization_blocked_no_task_state_mutation"],
        "non_proofs": list(_NON_PROOFS),
    }


def _prior_finalization_reason(
    *,
    verification: dict[str, Any],
    existing_finalizations: list[dict[str, Any]] | None,
) -> str:
    verification_id = _normalize_text(verification.get("verification_id"))
    attempt_id = _normalize_text(verification.get("apply_attempt_id"))
    task_id = _normalize_text(
        _as_mapping(verification.get("linked_evidence_chain")).get("source_task_id")
    )
    for finalization in existing_finalizations or []:
        if not isinstance(finalization, dict):
            continue
        if _normalize_text(finalization.get("verification_id")) == verification_id:
            return "prior_finalization_exists"
        if _normalize_text(finalization.get("apply_attempt_id")) == attempt_id:
            return "prior_finalization_exists"
        references = _as_mapping(
            finalization.get("packet_task_artifact_verifier_current_success_references")
        )
        if task_id and _normalize_text(references.get("task_id")) == task_id:
            return "prior_finalization_exists"
    return ""


def _validate_verification(verification: dict[str, Any]) -> str:
    if (
        verification.get("artifact_type")
        != AUTHORIZED_BOUNDED_APPLY_RESULT_VERIFICATION_ARTIFACT_TYPE
    ):
        return "verification_record_missing"
    for field in (
        "verification_id",
        "apply_attempt_id",
        "authorization_id",
        "draft_proposal_id",
    ):
        if not _normalize_text(verification.get(field)):
            return f"{field}_missing"
    if verification.get("verification_status") != MECHANICALLY_VERIFIED:
        return "verification_not_mechanically_verified"
    if verification.get("patch_verified_mechanically") is not True:
        return "verification_not_mechanically_verified"
    if verification.get("not_finalized") is not True:
        return "verification_already_finalized_or_not_marked_open"
    if verification.get("unexpected_files"):
        return "unexpected_files_block_finalization"
    expected_files = verification.get("files_expected")
    observed_files = verification.get("files_observed")
    if not isinstance(expected_files, list) or not expected_files:
        return "expected_files_missing"
    if not isinstance(observed_files, list) or not observed_files:
        return "mechanically_verified_files_missing"
    for path in observed_files:
        try:
            resolve_declared_project_path(_normalize_text(path))
        except (TypeError, ValueError):
            return "unbounded_path_blocks_finalization"
    chain = _as_mapping(verification.get("linked_evidence_chain"))
    for field in _REQUIRED_CHAIN_FIELDS:
        if not _normalize_text(chain.get(field)):
            return f"{field}_missing"
    if _normalize_text(chain.get("phase_294_draft_proposal_id")) != _normalize_text(
        verification.get("draft_proposal_id")
    ):
        return "draft_proposal_id_mismatch"
    if _as_mapping(chain.get("phase_284_generated_residue_guard")).get(
        "generated_residue_detected"
    ):
        return "phase_284_generated_residue_guard_reported"
    claim_reason = _claim_reason(verification)
    if claim_reason:
        return claim_reason
    return ""


def finalize_verified_bounded_apply_task(
    verification_id: str | None = None,
    *,
    verification_record: dict[str, Any] | None = None,
    finalization_note: str,
    existing_finalizations: list[dict[str, Any]] | None = None,
    requested_finalization_status: str = FINALIZATION_COMPLETED,
    persist: bool = True,
) -> dict[str, Any]:
    note = _normalize_text(finalization_note)
    if not note:
        return _blocked(reason_code="finalization_note_required")
    if _normalize_text(requested_finalization_status) != FINALIZATION_COMPLETED:
        return _blocked(
            reason_code="unsupported_finalization_status",
            finalization_note=note,
        )
    note_reason = _claim_reason(note)
    if note_reason:
        return _blocked(reason_code=note_reason, finalization_note=note)

    if verification_record is None:
        if not verification_id:
            return _blocked(reason_code="verification_record_missing", finalization_note=note)
        safe_verification_id = validate_record_id(
            verification_id,
            label="verification id",
        )
        try:
            verification = load_authorized_bounded_apply_result_verification(
                safe_verification_id
            )
        except (OSError, ValueError, json.JSONDecodeError) as error:
            blocked = _blocked(
                reason_code="verification_record_missing",
                verification_id=safe_verification_id,
                finalization_note=note,
            )
            blocked["detail"] = str(error)
            return blocked
    else:
        verification = verification_record

    verification_id_value = _normalize_text(verification.get("verification_id"))
    if verification_id and verification_id_value and validate_record_id(
        verification_id,
        label="verification id",
    ) != verification_id_value:
        return _blocked(
            reason_code="verification_id_mismatch",
            verification_id=verification_id_value,
            finalization_note=note,
        )

    base = {
        "verification_id": verification_id_value,
        "apply_attempt_id": _normalize_text(verification.get("apply_attempt_id")),
        "authorization_id": _normalize_text(verification.get("authorization_id")),
        "draft_proposal_id": _normalize_text(verification.get("draft_proposal_id")),
        "finalization_note": note,
    }
    reason = _validate_verification(verification)
    if reason:
        return _blocked(reason_code=reason, **base)
    prior_reason = _prior_finalization_reason(
        verification=verification,
        existing_finalizations=existing_finalizations,
    )
    if prior_reason:
        return _blocked(reason_code=prior_reason, **base)

    chain = _as_mapping(verification.get("linked_evidence_chain"))
    files = list(verification.get("files_observed") or verification.get("files_expected"))
    finalization_id = f"verified_bounded_apply_task_finalization_{uuid4().hex[:8]}"
    finalization = {
        "artifact_type": VERIFIED_BOUNDED_APPLY_TASK_FINALIZATION_ARTIFACT_TYPE,
        "source": VERIFIED_BOUNDED_APPLY_TASK_FINALIZATION_SOURCE,
        "finalization_created": True,
        "finalization_id": finalization_id,
        "finalization_status": FINALIZATION_COMPLETED,
        "reason_code": "mechanically_verified_bounded_apply_task_finalized",
        "verification_id": verification_id_value,
        "apply_attempt_id": base["apply_attempt_id"],
        "authorization_id": base["authorization_id"],
        "draft_proposal_id": base["draft_proposal_id"],
        "candidate_id": _normalize_text(chain.get("phase_289_candidate_id")),
        "packet_task_artifact_verifier_current_success_references": {
            "packet_id": _normalize_text(chain.get("source_packet_id")),
            "task_id": _normalize_text(chain.get("source_task_id")),
            "execution_artifact_id": _normalize_text(
                chain.get("source_execution_artifact_id")
            ),
            "verifier_result_path": _normalize_text(
                chain.get("source_verifier_result_path")
            ),
            "operator_decision_record_id": _normalize_text(
                chain.get("operator_decision_record_id")
            ),
            "current_success_review_reference": _as_mapping(
                chain.get("current_success_review_reference")
            ),
        },
        "files_mechanically_verified": files,
        "operator_or_system_finalization_note": note,
        "semantic_correctness_not_proven": True,
        "production_readiness_not_proven": True,
        "model_provider_runtime_not_proven": True,
        "autonomous_ai_coding_not_proven": True,
        "backbone_v0_not_declared": True,
        "explicit_semantic_correctness_not_proven_statement": (
            "Semantic correctness is not proven by this finalization record."
        ),
        "explicit_production_readiness_not_proven_statement": (
            "Production readiness is not proven by this finalization record."
        ),
        "explicit_model_provider_runtime_execution_not_proven_statement": (
            "Model/provider/runtime execution is not proven by this finalization record."
        ),
        "explicit_backbone_v0_not_declared_statement": (
            "Backbone V0 is not declared by this finalization record."
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "caveats": [
            "mechanical_finalization_record_only",
            "phase_101_style_task_state_finalization_not_invoked",
        ],
        "non_proofs": list(_NON_PROOFS),
    }
    if persist:
        path = verified_bounded_apply_task_finalization_path(finalization_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(finalization, indent=2, sort_keys=True), encoding="utf-8")
    return finalization


def load_verified_bounded_apply_task_finalization(finalization_id: str) -> dict[str, Any]:
    safe_id = validate_record_id(finalization_id, label="finalization id")
    payload = json.loads(
        verified_bounded_apply_task_finalization_path(safe_id).read_text(encoding="utf-8")
    )
    if payload.get("artifact_type") != VERIFIED_BOUNDED_APPLY_TASK_FINALIZATION_ARTIFACT_TYPE:
        raise ValueError("Stored artifact is not a verified bounded apply task finalization.")
    if payload.get("finalization_id") != safe_id:
        raise ValueError("Stored finalization id does not match.")
    return payload
