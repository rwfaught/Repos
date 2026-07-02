from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from orchestrator import artifact_store
from orchestrator.draft_patch_proposal_apply_authorization_record import (
    AUTHORIZE_APPLY,
    load_draft_patch_proposal_apply_authorization_record,
    read_draft_patch_proposal_apply_authorization_status,
)
from orchestrator.patch_apply_engine import apply_authorized_patch
from orchestrator.paths import resolve_declared_project_path, validate_record_id
from orchestrator.task_schema import FILESYSTEM_MUTATION_EXECUTION_POLICY


AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_ARTIFACT_TYPE = (
    "authorized_draft_patch_apply_attempt"
)
AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_SOURCE = (
    "phase_303_authorized_draft_patch_proposal_bounded_apply_execution"
)

_AUTHORIZED_STATUS = "authorized_for_later_bounded_apply"
_SUPPORTED_OPERATION_KEYS = {
    "operation_id",
    "file_path",
    "path",
    "expected_before",
    "replacement_after",
    "description",
}
_NON_PROOFS = [
    "bounded_apply_attempt_is_not_apply_result_verification",
    "bounded_apply_attempt_does_not_finalize_patch_task",
    "bounded_apply_attempt_does_not_prove_semantic_correctness",
    "bounded_apply_attempt_does_not_prove_production_readiness",
    "no_semantic_correctness_proof",
    "no_live_provider_model_proof",
    "no_runtime_platform_proof",
    "no_autonomous_ai_coding_proof",
    "no_model_backed_generation_proof",
    "no_production_readiness_proof",
]
_SMUGGLED_FIELD_REASONS = {
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
    "production_ready": "production_readiness_claim_rejected",
    "production_readiness": "production_readiness_claim_rejected",
    "production_readiness_claimed": "production_readiness_claim_rejected",
    "autonomous_ai_coding": "autonomous_ai_coding_claim_rejected",
    "autonomous_ai_coding_claimed": "autonomous_ai_coding_claim_rejected",
    "patch_task_finalized": "finalization_smuggling_rejected",
    "finalized": "finalization_smuggling_rejected",
    "verification_satisfied": "apply_result_verification_smuggling_rejected",
    "semantic_correctness_proven": "semantic_correctness_claim_is_non_proof",
    "production_readiness_proven": "production_readiness_claim_rejected",
}
_SMUGGLED_TEXT_REASONS = {
    "provider": "provider_model_runtime_platform_claim_rejected",
    "model": "provider_model_runtime_platform_claim_rejected",
    "runtime": "provider_model_runtime_platform_claim_rejected",
    "platform": "provider_model_runtime_platform_claim_rejected",
    "ollama": "provider_model_runtime_platform_claim_rejected",
    "semantic correctness": "semantic_correctness_claim_is_non_proof",
    "semantically correct": "semantic_correctness_claim_is_non_proof",
    "production ready": "production_readiness_claim_rejected",
    "production-readiness": "production_readiness_claim_rejected",
    "production readiness": "production_readiness_claim_rejected",
    "autonomous ai coding": "autonomous_ai_coding_claim_rejected",
    "autonomous coding": "autonomous_ai_coding_claim_rejected",
    "finalized": "finalization_smuggling_rejected",
    "finalization": "finalization_smuggling_rejected",
}


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_sequence(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _attempt_path(attempt_id: str):
    return artifact_store.artifact_path(validate_record_id(attempt_id, label="attempt id"))


def _blocked(
    *,
    reason_code: str,
    authorization_id: str = "",
    draft_proposal_id: str = "",
    evidence_chain: dict[str, Any] | None = None,
    files_attempted: list[str] | None = None,
    detail: str = "",
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "artifact_type": AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_ARTIFACT_TYPE,
        "source": AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_SOURCE,
        "apply_attempt_created": False,
        "apply_attempt_id": "",
        "source_authorization_id": authorization_id,
        "authorization_id": authorization_id,
        "draft_proposal_id": draft_proposal_id,
        "linked_evidence_chain": evidence_chain or {},
        "bounded_target_information": {},
        "files_attempted": files_attempted or [],
        "apply_status": "blocked",
        "reason_code": reason_code,
        "detail": detail,
        "patch_not_verified": True,
        "not_finalized": True,
        "semantic_correctness_not_proven": True,
        "production_readiness_not_proven": True,
        "no_finalization_in_this_phase": True,
        "patch_task_finalized": False,
        "verification_satisfied": False,
        "apply_result_verified": False,
        "provider_executed": False,
        "model_executed": False,
        "runtime_executed": False,
        "platform_invoked": False,
        "autonomous_ai_coding_claimed": False,
        "semantic_correctness_claimed": False,
        "production_readiness_claimed": False,
        "timestamp": now,
        "caveats": ["blocked_before_bounded_apply_engine_execution"],
        "non_proofs": list(_NON_PROOFS),
    }


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
                "decision_reason",
                "operator_authorization_note",
                "operator_authorization_reason",
                "explicit_semantic_correctness_not_proven_statement",
                "explicit_production_readiness_not_proven_statement",
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
        for needle, reason in _SMUGGLED_TEXT_REASONS.items():
            if needle in normalized:
                return reason
    return ""


def _evidence_chain(authorization: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase_299_authorization_id": _normalize_text(authorization.get("authorization_id")),
        "phase_296_authorization_eligibility": _as_mapping(
            authorization.get("phase_296_authorization_eligibility_reference")
            or authorization.get("eligibility_record")
        ),
        "phase_294_draft_proposal_id": _normalize_text(draft.get("draft_proposal_id")),
        "phase_290_promotion_record_id": _normalize_text(
            draft.get("source_promotion_record_id")
        ),
        "phase_289_candidate_id": _normalize_text(draft.get("source_candidate_id")),
        "phase_288_packet_eligibility": _as_mapping(
            draft.get("phase_288_eligibility_reference")
        ),
        "source_packet_id": _normalize_text(draft.get("source_packet_id")),
        "source_run_id": _normalize_text(draft.get("source_run_id")),
        "source_task_id": _normalize_text(draft.get("source_task_id")),
        "source_execution_artifact_id": _normalize_text(
            draft.get("source_execution_artifact_id")
        ),
        "source_verifier_result_path": _normalize_text(
            draft.get("source_verifier_result_path")
        ),
        "operator_decision_record_id": _normalize_text(
            draft.get("operator_decision_record_id")
        ),
        "current_success_review_reference": _as_mapping(
            draft.get("current_success_review_reference")
        ),
    }


def _operations_from_payload(payload: dict[str, Any]) -> tuple[list[dict[str, str]], str]:
    raw_operations = payload.get("operations") or payload.get("apply_operations")
    if raw_operations is None:
        raw_operations = payload.get("proposed_changes")
    if not isinstance(raw_operations, list) or not raw_operations:
        return [], "structured_patch_payload_missing"

    operations: list[dict[str, str]] = []
    for index, raw_operation in enumerate(raw_operations):
        if not isinstance(raw_operation, dict):
            return [], "ambiguous_patch_payload_rejected"
        if any(key not in _SUPPORTED_OPERATION_KEYS for key in raw_operation):
            return [], "ambiguous_patch_payload_rejected"
        file_path = _normalize_text(raw_operation.get("file_path") or raw_operation.get("path"))
        operation_id = _normalize_text(raw_operation.get("operation_id")) or f"operation_{index}"
        expected_before = raw_operation.get("expected_before")
        replacement_after = raw_operation.get("replacement_after")
        if (
            not file_path
            or not isinstance(expected_before, str)
            or expected_before == ""
            or not isinstance(replacement_after, str)
        ):
            return [], "ambiguous_patch_payload_rejected"
        try:
            validate_record_id(operation_id, label="operation id")
            resolve_declared_project_path(file_path)
        except ValueError as error:
            text = str(error)
            if "relative" in text:
                return [], "absolute_patch_path_rejected"
            if "parent traversal" in text or "outside" in text:
                return [], "path_traversal_rejected"
            return [], "unbounded_target_path_rejected"
        if "\\" in file_path:
            return [], "unsafe_patch_path_rejected"
        operations.append(
            {
                "operation_id": operation_id,
                "file_path": file_path,
                "expected_before": expected_before,
                "replacement_after": replacement_after,
                "description": _normalize_text(raw_operation.get("description")),
            }
        )
    return operations, ""


def _validate_chain(
    authorization: dict[str, Any],
    readback: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    authorization_id = _normalize_text(authorization.get("authorization_id"))
    draft = _as_mapping(authorization.get("phase_294_draft_proposal_reference"))
    draft_id = _normalize_text(draft.get("draft_proposal_id"))
    if not draft:
        return draft, "draft_proposal_missing"
    if authorization.get("authorization_decision") != AUTHORIZE_APPLY:
        return draft, "apply_authorization_not_authorize_apply"
    if authorization.get("authorization_status") != _AUTHORIZED_STATUS:
        return draft, "apply_authorization_not_active"
    if not readback.get("authorization_active"):
        return draft, "latest_apply_authorization_not_active"
    if _normalize_text(readback.get("authorization_id")) != authorization_id:
        return draft, "stale_apply_authorization_rejected"
    if _normalize_text(authorization.get("draft_proposal_id")) != draft_id:
        return draft, "authorization_draft_link_mismatch"
    if draft.get("draft_proposal_status") != "draft_only" or not draft.get("draft_only"):
        return draft, "draft_only_status_required"
    if not draft.get("not_applied") or draft.get("patch_applied"):
        return draft, "draft_already_applied_rejected"
    if not draft.get("source_candidate_id"):
        return draft, "candidate_link_missing"
    if not draft.get("source_packet_id"):
        return draft, "accepted_packet_result_link_missing"
    candidate = _as_mapping(draft.get("phase_289_candidate_reference"))
    promotion = _as_mapping(draft.get("phase_290_promotion_reference"))
    packet_eligibility = _as_mapping(draft.get("phase_288_eligibility_reference"))
    current_success = _as_mapping(draft.get("current_success_review_reference"))
    if not candidate:
        return draft, "candidate_link_missing"
    if not promotion:
        return draft, "promotion_link_missing"
    if not packet_eligibility:
        return draft, "accepted_packet_result_link_missing"
    if not current_success:
        return draft, "current_success_reference_missing"
    if _normalize_text(candidate.get("candidate_id")) != _normalize_text(
        draft.get("source_candidate_id")
    ):
        return draft, "candidate_id_mismatch"
    if _normalize_text(promotion.get("candidate_id")) != _normalize_text(
        draft.get("source_candidate_id")
    ):
        return draft, "promotion_candidate_id_mismatch"
    for field_name in (
        "source_packet_id",
        "source_run_id",
        "source_task_id",
        "source_execution_artifact_id",
        "source_execution_artifact_path",
        "source_verifier_result_path",
        "operator_decision_record_id",
    ):
        draft_value = _normalize_text(draft.get(field_name))
        if _normalize_text(candidate.get(field_name)) != draft_value:
            return draft, f"candidate_{field_name}_mismatch"
        promotion_value = _normalize_text(promotion.get(field_name))
        if promotion_value and promotion_value != draft_value:
            return draft, f"promotion_{field_name}_mismatch"
    if _normalize_text(packet_eligibility.get("task_id")) != _normalize_text(
        draft.get("source_task_id")
    ):
        return draft, "packet_task_id_mismatch"
    if _normalize_text(packet_eligibility.get("packet_id")) != _normalize_text(
        draft.get("source_packet_id")
    ):
        return draft, "packet_id_mismatch"
    if _normalize_text(current_success.get("task_id")) != _normalize_text(
        draft.get("source_task_id")
    ):
        return draft, "current_success_task_id_mismatch"
    if _normalize_text(current_success.get("run_id")) != _normalize_text(
        draft.get("source_run_id")
    ):
        return draft, "current_success_run_id_mismatch"
    if _as_mapping(draft.get("phase_284_generated_residue_guard")).get(
        "generated_residue_detected"
    ):
        return draft, "phase_284_generated_residue_guard_reported"
    eligibility = _as_mapping(
        authorization.get("phase_296_authorization_eligibility_reference")
        or authorization.get("eligibility_record")
    )
    if eligibility.get("authorization_eligibility_status") != "authorization_eligible":
        return draft, "authorization_eligibility_not_clean"
    if _normalize_text(eligibility.get("draft_proposal_id")) != draft_id:
        return draft, "authorization_eligibility_draft_mismatch"
    claim_reason = _claim_reason(authorization) or _claim_reason(draft)
    if claim_reason:
        return draft, claim_reason
    return draft, ""


def _duplicate_apply_attempt_reason(
    *,
    authorization_id: str,
    draft_proposal_id: str,
    existing_apply_attempts: list[dict[str, Any]] | None,
) -> str:
    for attempt in existing_apply_attempts or []:
        if not isinstance(attempt, dict):
            continue
        same_authorization = _normalize_text(
            attempt.get("source_authorization_id") or attempt.get("authorization_id")
        ) == authorization_id
        same_draft = _normalize_text(attempt.get("draft_proposal_id")) == draft_proposal_id
        if same_authorization or same_draft:
            return "existing_apply_attempt_rejected"
    return ""


def _write_bridge_artifacts(
    *,
    bridge_proposal_id: str,
    bridge_authorization_id: str,
    authorization: dict[str, Any],
    draft: dict[str, Any],
    files: list[str],
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    proposal = {
        "artifact_type": "patch_proposal",
        "proposal_id": bridge_proposal_id,
        "task_id": _normalize_text(draft.get("source_task_id")),
        "run_id": _normalize_text(draft.get("source_run_id")) or None,
        "execution_policy": FILESYSTEM_MUTATION_EXECUTION_POLICY,
        "files_in_scope": files,
        "proposed_changes": [{"path": path, "description": "Phase 303 bounded apply."} for path in files],
        "proposed_diff": _normalize_text(draft.get("unified_diff") or draft.get("proposed_diff")),
        "unified_diff": _normalize_text(draft.get("unified_diff") or draft.get("proposed_diff")),
        "rationale": _normalize_text(draft.get("rationale") or "Phase 303 bounded apply attempt."),
        "requires_operator_apply": True,
        "applied": False,
        "source": AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_SOURCE,
        "created_at": now,
        "proposal_status": "awaiting_operator_apply",
        "execution_performed": False,
        "provider_executed": False,
        "model_executed": False,
        "runtime_executed": False,
        "completion_proof": False,
        "causal_change_satisfied": False,
    }
    authorization_payload = {
        "artifact_type": "patch_apply_authorization",
        "authorization_id": bridge_authorization_id,
        "proposal_id": bridge_proposal_id,
        "task_id": proposal["task_id"],
        "run_id": proposal["run_id"],
        "execution_policy": FILESYSTEM_MUTATION_EXECUTION_POLICY,
        "files_authorized": files,
        "operator_decision": "authorize_apply",
        "operator_label": "phase_303_authorized_draft_apply",
        "decision_reason": (
            "Bridge artifact derived from explicit Phase 299/301 authorization "
            f"{authorization['authorization_id']}."
        ),
        "created_at": now,
        "requires_separate_apply_boundary": True,
        "applied": False,
        "source": AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_SOURCE,
        "authorization_status": "authorized_for_future_apply_boundary",
        "execution_performed": False,
        "provider_executed": False,
        "model_executed": False,
        "runtime_executed": False,
        "completion_proof": False,
        "verification_satisfied": False,
        "causal_change_satisfied": False,
    }
    artifact_store.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    artifact_store.artifact_path(bridge_proposal_id).write_text(
        json.dumps(proposal, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    artifact_store.artifact_path(bridge_authorization_id).write_text(
        json.dumps(authorization_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def execute_authorized_draft_patch_apply(
    authorization_id: str,
    *,
    authorization_record: dict[str, Any] | None = None,
    authorization_records: list[dict[str, Any]] | None = None,
    existing_apply_attempts: list[dict[str, Any]] | None = None,
    apply_engine: Callable[..., dict[str, Any]] = apply_authorized_patch,
) -> dict[str, Any]:
    safe_authorization_id = validate_record_id(authorization_id, label="authorization id")
    try:
        authorization = (
            authorization_record
            if authorization_record is not None
            else load_draft_patch_proposal_apply_authorization_record(safe_authorization_id)
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return _blocked(
            reason_code="apply_authorization_record_missing",
            authorization_id=safe_authorization_id,
            detail=str(error),
        )

    if _normalize_text(authorization.get("authorization_id")) != safe_authorization_id:
        return _blocked(
            reason_code="authorization_id_mismatch",
            authorization_id=safe_authorization_id,
            draft_proposal_id=_normalize_text(authorization.get("draft_proposal_id")),
        )

    draft_id = _normalize_text(authorization.get("draft_proposal_id"))
    readback = read_draft_patch_proposal_apply_authorization_status(
        draft_id,
        authorization_records=authorization_records or [authorization],
    )
    draft, chain_reason = _validate_chain(authorization, readback)
    evidence_chain = _evidence_chain(authorization, draft) if draft else {}
    if chain_reason:
        return _blocked(
            reason_code=chain_reason,
            authorization_id=safe_authorization_id,
            draft_proposal_id=draft_id,
            evidence_chain=evidence_chain,
        )
    duplicate_reason = _duplicate_apply_attempt_reason(
        authorization_id=safe_authorization_id,
        draft_proposal_id=draft_id,
        existing_apply_attempts=existing_apply_attempts,
    )
    if duplicate_reason:
        return _blocked(
            reason_code=duplicate_reason,
            authorization_id=safe_authorization_id,
            draft_proposal_id=draft_id,
            evidence_chain=evidence_chain,
        )

    patch_payload = _as_mapping(draft.get("proposed_patch_evidence_payload"))
    if not patch_payload:
        return _blocked(
            reason_code="structured_patch_payload_missing",
            authorization_id=safe_authorization_id,
            draft_proposal_id=draft_id,
            evidence_chain=evidence_chain,
        )
    operations, operation_reason = _operations_from_payload(patch_payload)
    files = list(dict.fromkeys(operation["file_path"] for operation in operations))
    if operation_reason:
        return _blocked(
            reason_code=operation_reason,
            authorization_id=safe_authorization_id,
            draft_proposal_id=draft_id,
            evidence_chain=evidence_chain,
            files_attempted=files,
        )

    attempt_id = f"authorized_draft_patch_apply_attempt_{uuid4().hex[:8]}"
    bridge_proposal_id = f"phase303_bridge_proposal_{uuid4().hex[:8]}"
    bridge_authorization_id = f"phase303_bridge_authorization_{uuid4().hex[:8]}"
    _write_bridge_artifacts(
        bridge_proposal_id=bridge_proposal_id,
        bridge_authorization_id=bridge_authorization_id,
        authorization=authorization,
        draft=draft,
        files=files,
    )

    now = datetime.now(timezone.utc).isoformat()
    try:
        engine_result = apply_engine(bridge_authorization_id, operations=operations)
    except Exception as error:
        attempt = _blocked(
            reason_code="bounded_patch_apply_engine_failed",
            authorization_id=safe_authorization_id,
            draft_proposal_id=draft_id,
            evidence_chain=evidence_chain,
            files_attempted=files,
            detail=str(error),
        )
        attempt.update(
            {
                "apply_attempt_created": True,
                "apply_attempt_id": attempt_id,
                "apply_status": "failed",
                "bounded_target_information": {
                    "bridge_proposal_id": bridge_proposal_id,
                    "bridge_authorization_id": bridge_authorization_id,
                    "files_authorized": files,
                },
                "timestamp": now,
            }
        )
    else:
        attempt = {
            "artifact_type": AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_ARTIFACT_TYPE,
            "source": AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_SOURCE,
            "apply_attempt_created": True,
            "apply_attempt_id": attempt_id,
            "source_authorization_id": safe_authorization_id,
            "authorization_id": safe_authorization_id,
            "draft_proposal_id": draft_id,
            "linked_evidence_chain": evidence_chain,
            "bounded_target_information": {
                "bridge_proposal_id": bridge_proposal_id,
                "bridge_authorization_id": bridge_authorization_id,
                "files_authorized": files,
                "phase_99_apply_id": engine_result.get("apply_id"),
            },
            "files_attempted": files,
            "apply_status": "applied" if engine_result.get("applied") else "failed",
            "reason_code": (
                "bounded_patch_apply_attempt_applied"
                if engine_result.get("applied")
                else "bounded_patch_apply_engine_failed"
            ),
            "phase_99_apply_result_reference": engine_result,
            "patch_not_verified": True,
            "not_finalized": True,
            "semantic_correctness_not_proven": True,
            "production_readiness_not_proven": True,
            "no_finalization_in_this_phase": True,
            "patch_task_finalized": False,
            "verification_satisfied": False,
            "apply_result_verified": False,
            "provider_executed": False,
            "model_executed": False,
            "runtime_executed": False,
            "platform_invoked": False,
            "autonomous_ai_coding_claimed": False,
            "semantic_correctness_claimed": False,
            "production_readiness_claimed": False,
            "timestamp": now,
            "caveats": [
                "apply_attempt_requires_later_phase_100_style_verification",
                "apply_attempt_requires_later_phase_101_style_finalization",
            ],
            "non_proofs": list(_NON_PROOFS),
        }

    _attempt_path(attempt_id).write_text(
        json.dumps(attempt, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return attempt


def load_authorized_draft_patch_apply_attempt(attempt_id: str) -> dict[str, Any]:
    safe_attempt_id = validate_record_id(attempt_id, label="attempt id")
    payload = json.loads(_attempt_path(safe_attempt_id).read_text(encoding="utf-8"))
    if payload.get("artifact_type") != AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_ARTIFACT_TYPE:
        raise ValueError("Stored artifact is not an authorized draft patch apply attempt.")
    if payload.get("apply_attempt_id") != safe_attempt_id:
        raise ValueError("Stored apply attempt id does not match.")
    return payload


def read_authorized_draft_patch_apply_attempt_status(
    apply_attempt_id: str | None = None,
    *,
    apply_attempt_record: dict[str, Any] | None = None,
    apply_attempt_records: list[dict[str, Any]] | None = None,
    draft_proposal_id: str | None = None,
    authorization_id: str | None = None,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    if apply_attempt_record is not None:
        records = [apply_attempt_record]
    elif apply_attempt_records is not None:
        records = [record for record in apply_attempt_records if isinstance(record, dict)]
    elif apply_attempt_id:
        try:
            records = [load_authorized_draft_patch_apply_attempt(apply_attempt_id)]
        except (OSError, ValueError, json.JSONDecodeError) as error:
            return _readback_blocked(
                reason_code="apply_attempt_record_missing",
                detail=str(error),
                apply_attempt_id=_normalize_text(apply_attempt_id),
                draft_proposal_id=_normalize_text(draft_proposal_id),
                authorization_id=_normalize_text(authorization_id),
            )
    else:
        return _readback_blocked(reason_code="apply_attempt_record_required")

    requested_draft_id = _normalize_text(draft_proposal_id)
    requested_authorization_id = _normalize_text(authorization_id)
    filtered = []
    for record in records:
        if record.get("artifact_type") != AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_ARTIFACT_TYPE:
            continue
        if requested_draft_id and _normalize_text(record.get("draft_proposal_id")) != requested_draft_id:
            continue
        if requested_authorization_id and _normalize_text(
            record.get("source_authorization_id") or record.get("authorization_id")
        ) != requested_authorization_id:
            continue
        filtered.append(record)

    if not filtered:
        return _readback_blocked(
            reason_code="apply_attempt_record_missing",
            apply_attempt_id=_normalize_text(apply_attempt_id),
            draft_proposal_id=requested_draft_id,
            authorization_id=requested_authorization_id,
        )

    latest = sorted(
        filtered,
        key=lambda record: _normalize_text(record.get("timestamp") or record.get("created_at")),
    )[-1]
    return {
        "authorized_bounded_apply_attempt_readback_surface": True,
        "apply_attempt_id": _normalize_text(latest.get("apply_attempt_id")),
        "draft_proposal_id": _normalize_text(latest.get("draft_proposal_id")),
        "authorization_id": _normalize_text(
            latest.get("source_authorization_id") or latest.get("authorization_id")
        ),
        "bounded_apply_status": _normalize_text(latest.get("apply_status")) or "blocked",
        "apply_status": _normalize_text(latest.get("apply_status")) or "blocked",
        "files_attempted": list(latest.get("files_attempted", [])),
        "reason_code": _normalize_text(latest.get("reason_code")),
        "linked_evidence_chain": _as_mapping(latest.get("linked_evidence_chain")),
        "bounded_target_information": _as_mapping(latest.get("bounded_target_information")),
        "patch_not_verified": latest.get("patch_not_verified") is True,
        "not_finalized": latest.get("not_finalized") is True,
        "semantic_correctness_not_proven": latest.get("semantic_correctness_not_proven") is True,
        "production_readiness_not_proven": latest.get("production_readiness_not_proven") is True,
        "no_finalization_in_this_phase": latest.get("no_finalization_in_this_phase") is True,
        "patch_task_finalized": False,
        "verification_satisfied": False,
        "apply_result_verified": False,
        "provider_executed": False,
        "model_executed": False,
        "runtime_executed": False,
        "platform_invoked": False,
        "caveats": list(latest.get("caveats", [])),
        "non_proofs": list(latest.get("non_proofs", _NON_PROOFS)),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase_303_apply_attempt_reference": latest,
    }


def _readback_blocked(
    *,
    reason_code: str,
    detail: str = "",
    apply_attempt_id: str = "",
    draft_proposal_id: str = "",
    authorization_id: str = "",
) -> dict[str, Any]:
    return {
        "authorized_bounded_apply_attempt_readback_surface": True,
        "apply_attempt_id": apply_attempt_id,
        "draft_proposal_id": draft_proposal_id,
        "authorization_id": authorization_id,
        "bounded_apply_status": "blocked",
        "apply_status": "blocked",
        "files_attempted": [],
        "reason_code": reason_code,
        "detail": detail,
        "linked_evidence_chain": {},
        "bounded_target_information": {},
        "patch_not_verified": True,
        "not_finalized": True,
        "semantic_correctness_not_proven": True,
        "production_readiness_not_proven": True,
        "no_finalization_in_this_phase": True,
        "patch_task_finalized": False,
        "verification_satisfied": False,
        "apply_result_verified": False,
        "provider_executed": False,
        "model_executed": False,
        "runtime_executed": False,
        "platform_invoked": False,
        "caveats": ["readback_only_no_apply_execution"],
        "non_proofs": list(_NON_PROOFS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
