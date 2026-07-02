from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from orchestrator.authorized_draft_patch_apply import (
    AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_ARTIFACT_TYPE,
    load_authorized_draft_patch_apply_attempt,
)
from orchestrator.draft_patch_proposal_apply_authorization_record import (
    load_draft_patch_proposal_apply_authorization_record,
)
from orchestrator.paths import resolve_declared_project_path, validate_record_id


AUTHORIZED_BOUNDED_APPLY_RESULT_VERIFICATION_ARTIFACT_TYPE = (
    "authorized_bounded_apply_result_verification"
)
AUTHORIZED_BOUNDED_APPLY_RESULT_VERIFICATION_SOURCE = (
    "phase_307_authorized_bounded_apply_result_verification"
)
MECHANICALLY_VERIFIED = "mechanically_verified"
VERIFICATION_FAILED = "verification_failed"
VERIFICATION_BLOCKED = "verification_blocked"

_ALLOWED_APPLY_STATUSES = {"applied", "failed", "blocked"}
_NON_PROOFS = [
    "mechanical_verification_is_not_semantic_correctness",
    "mechanical_verification_is_not_patch_task_finalization",
    "mechanical_verification_is_not_production_readiness",
    "no_autonomous_ai_coding_proof",
    "no_provider_model_runtime_platform_proof",
]
_AUTHORIZED_STATUS = "authorized_for_later_bounded_apply"
_AUTHORIZE_APPLY = "authorize_apply"
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
    "semantic_correctness_proven": "semantic_correctness_claim_is_non_proof",
    "production_ready": "production_readiness_claim_rejected",
    "production_readiness": "production_readiness_claim_rejected",
    "production_readiness_claimed": "production_readiness_claim_rejected",
    "production_readiness_proven": "production_readiness_claim_rejected",
    "autonomous_ai_coding": "autonomous_ai_coding_claim_rejected",
    "autonomous_ai_coding_claimed": "autonomous_ai_coding_claim_rejected",
    "patch_task_finalized": "finalization_smuggling_rejected",
    "finalized": "finalization_smuggling_rejected",
    "completed": "finalization_smuggling_rejected",
    "verification_satisfied": "verification_smuggling_rejected",
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


def _path_identity(path: str) -> str:
    return path.replace("\\", "/")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
                "detail",
                "timestamp",
                "created_at",
                "expected_before",
                "replacement_after",
                "description",
                "authorization_decision",
                "operator_decision",
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
        if (
            "not proven" in normalized
            or "non-proof" in normalized
            or "no proof" in normalized
            or "does not prove" in normalized
        ):
            return ""
        for needle, reason in _SMUGGLED_TEXT_REASONS.items():
            if needle in normalized:
                return reason
    return ""


def _block(
    *,
    reason_code: str,
    apply_attempt_id: str = "",
    authorization_id: str = "",
    draft_proposal_id: str = "",
    evidence_chain: dict[str, Any] | None = None,
    files_expected: list[str] | None = None,
    files_observed: list[str] | None = None,
    unexpected_files: list[str] | None = None,
    status: str = VERIFICATION_BLOCKED,
    detail: str = "",
) -> dict[str, Any]:
    return _artifact(
        verification_status=status,
        reason_code=reason_code,
        apply_attempt_id=apply_attempt_id,
        authorization_id=authorization_id,
        draft_proposal_id=draft_proposal_id,
        evidence_chain=evidence_chain or {},
        files_expected=files_expected or [],
        files_observed=files_observed or [],
        unexpected_files=unexpected_files or [],
        patch_verified_mechanically=False,
        detail=detail,
    )


def _artifact(
    *,
    verification_status: str,
    reason_code: str,
    apply_attempt_id: str,
    authorization_id: str,
    draft_proposal_id: str,
    evidence_chain: dict[str, Any],
    files_expected: list[str],
    files_observed: list[str],
    unexpected_files: list[str],
    patch_verified_mechanically: bool,
    detail: str = "",
) -> dict[str, Any]:
    return {
        "artifact_type": AUTHORIZED_BOUNDED_APPLY_RESULT_VERIFICATION_ARTIFACT_TYPE,
        "source": AUTHORIZED_BOUNDED_APPLY_RESULT_VERIFICATION_SOURCE,
        "verification_id": f"authorized_bounded_apply_result_verification_{uuid4().hex[:8]}",
        "apply_attempt_id": apply_attempt_id,
        "authorization_id": authorization_id,
        "draft_proposal_id": draft_proposal_id,
        "verification_status": verification_status,
        "reason_code": reason_code,
        "detail": detail,
        "linked_evidence_chain": evidence_chain,
        "files_expected": files_expected,
        "files_observed": files_observed,
        "unexpected_files": unexpected_files,
        "patch_verified_mechanically": patch_verified_mechanically,
        "semantic_correctness_not_proven": True,
        "production_readiness_not_proven": True,
        "not_finalized": True,
        "no_finalization_in_this_phase": True,
        "patch_task_finalized": False,
        "semantic_correctness_claimed": False,
        "production_readiness_claimed": False,
        "autonomous_ai_coding_claimed": False,
        "provider_executed": False,
        "model_executed": False,
        "runtime_executed": False,
        "platform_invoked": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "caveats": [
            "mechanical_apply_result_verification_only",
            "phase_101_style_finalization_not_invoked",
        ],
        "non_proofs": list(_NON_PROOFS),
    }


def _expected_operations(authorization: dict[str, Any]) -> tuple[list[dict[str, str]], str]:
    draft = _as_mapping(authorization.get("phase_294_draft_proposal_reference"))
    payload = _as_mapping(draft.get("proposed_patch_evidence_payload"))
    operations = payload.get("operations") or payload.get("apply_operations")
    if operations is None:
        operations = payload.get("proposed_changes")
    if not isinstance(operations, list) or not operations:
        return [], "structured_patch_payload_missing"

    normalized: list[dict[str, str]] = []
    for raw in operations:
        if not isinstance(raw, dict):
            return [], "ambiguous_patch_payload_rejected"
        path = _normalize_text(raw.get("file_path") or raw.get("path"))
        expected_before = raw.get("expected_before")
        replacement_after = raw.get("replacement_after")
        if (
            not path
            or not isinstance(expected_before, str)
            or expected_before == ""
            or not isinstance(replacement_after, str)
        ):
            return [], "ambiguous_patch_payload_rejected"
        try:
            resolve_declared_project_path(path)
        except (TypeError, ValueError):
            return [], "unbounded_target_path_rejected"
        if "\\" in path:
            return [], "unbounded_target_path_rejected"
        normalized.append(
            {
                "file_path": path,
                "expected_before": expected_before,
                "replacement_after": replacement_after,
            }
        )
    return normalized, ""


def _chain_reason(
    *,
    attempt: dict[str, Any],
    authorization: dict[str, Any],
) -> str:
    chain = _as_mapping(attempt.get("linked_evidence_chain"))
    authorization_id = _normalize_text(
        attempt.get("source_authorization_id") or attempt.get("authorization_id")
    )
    draft = _as_mapping(authorization.get("phase_294_draft_proposal_reference"))
    candidate = _as_mapping(draft.get("phase_289_candidate_reference"))
    promotion = _as_mapping(draft.get("phase_290_promotion_reference"))
    packet = _as_mapping(draft.get("phase_288_eligibility_reference"))

    if _normalize_text(authorization.get("authorization_decision")) != _AUTHORIZE_APPLY:
        return "apply_authorization_not_authorize_apply"
    if _normalize_text(authorization.get("authorization_status")) != _AUTHORIZED_STATUS:
        return "latest_apply_authorization_not_active"
    if _normalize_text(authorization.get("authorization_id")) != authorization_id:
        return "authorization_link_missing"
    if _normalize_text(authorization.get("draft_proposal_id")) != _normalize_text(
        attempt.get("draft_proposal_id")
    ):
        return "authorization_draft_link_mismatch"
    if not draft:
        return "draft_proposal_link_missing"
    if _normalize_text(draft.get("draft_proposal_id")) != _normalize_text(
        attempt.get("draft_proposal_id")
    ):
        return "draft_proposal_id_mismatch"
    if not candidate or not promotion or not packet:
        return "evidence_chain_incomplete"
    expected_links = {
        "phase_294_draft_proposal_id": draft.get("draft_proposal_id"),
        "phase_289_candidate_id": draft.get("source_candidate_id"),
        "source_packet_id": draft.get("source_packet_id"),
        "source_run_id": draft.get("source_run_id"),
        "source_task_id": draft.get("source_task_id"),
        "source_execution_artifact_id": draft.get("source_execution_artifact_id"),
        "source_verifier_result_path": draft.get("source_verifier_result_path"),
        "operator_decision_record_id": draft.get("operator_decision_record_id"),
    }
    for key, expected in expected_links.items():
        if _normalize_text(chain.get(key)) != _normalize_text(expected):
            return f"{key}_mismatch"
    if _normalize_text(candidate.get("candidate_id")) != _normalize_text(
        draft.get("source_candidate_id")
    ):
        return "candidate_id_mismatch"
    if _normalize_text(promotion.get("candidate_id")) != _normalize_text(
        draft.get("source_candidate_id")
    ):
        return "promotion_candidate_id_mismatch"
    if _normalize_text(packet.get("packet_id")) != _normalize_text(
        draft.get("source_packet_id")
    ):
        return "packet_id_mismatch"
    if _normalize_text(packet.get("task_id")) != _normalize_text(
        draft.get("source_task_id")
    ):
        return "packet_task_id_mismatch"
    if _as_mapping(draft.get("phase_284_generated_residue_guard")).get(
        "generated_residue_detected"
    ):
        return "phase_284_generated_residue_guard_reported"
    return ""


def _matching_finalization_exists(
    *,
    attempt: dict[str, Any],
    finalization_records: list[dict[str, Any]] | None,
) -> bool:
    attempt_id = _normalize_text(attempt.get("apply_attempt_id"))
    authorization_id = _normalize_text(
        attempt.get("source_authorization_id") or attempt.get("authorization_id")
    )
    draft_id = _normalize_text(attempt.get("draft_proposal_id"))
    phase_99_apply_id = _normalize_text(
        _as_mapping(attempt.get("bounded_target_information")).get("phase_99_apply_id")
    )
    for record in finalization_records or []:
        if not isinstance(record, dict):
            continue
        if _normalize_text(record.get("apply_attempt_id")) == attempt_id:
            return True
        if _normalize_text(record.get("authorization_id")) == authorization_id:
            return True
        if _normalize_text(record.get("draft_proposal_id")) == draft_id:
            return True
        if phase_99_apply_id and _normalize_text(record.get("apply_id")) == phase_99_apply_id:
            return True
    return False


def _observed_files(attempt: dict[str, Any]) -> list[str]:
    phase_99 = _as_mapping(attempt.get("phase_99_apply_result_reference"))
    files = phase_99.get("files_changed")
    if isinstance(files, list):
        return [_normalize_text(path) for path in files]
    return [_normalize_text(path) for path in _as_sequence(attempt.get("files_attempted"))]


def verify_authorized_bounded_apply_result(
    apply_attempt_id: str | None = None,
    *,
    apply_attempt_record: dict[str, Any] | None = None,
    authorization_record: dict[str, Any] | None = None,
    finalization_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if apply_attempt_record is None:
        if not apply_attempt_id:
            return _block(reason_code="apply_attempt_record_missing")
        safe_attempt_id = validate_record_id(apply_attempt_id, label="apply attempt id")
        try:
            attempt = load_authorized_draft_patch_apply_attempt(safe_attempt_id)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            return _block(
                reason_code="apply_attempt_record_missing",
                apply_attempt_id=safe_attempt_id,
                detail=str(error),
            )
    else:
        attempt = apply_attempt_record

    attempt_id = _normalize_text(attempt.get("apply_attempt_id"))
    if apply_attempt_id and attempt_id and validate_record_id(
        apply_attempt_id,
        label="apply attempt id",
    ) != attempt_id:
        return _block(
            reason_code="apply_attempt_id_mismatch",
            apply_attempt_id=attempt_id,
        )
    authorization_id = _normalize_text(
        attempt.get("source_authorization_id") or attempt.get("authorization_id")
    )
    draft_id = _normalize_text(attempt.get("draft_proposal_id"))
    evidence_chain = _as_mapping(attempt.get("linked_evidence_chain"))
    if attempt.get("artifact_type") != AUTHORIZED_DRAFT_PATCH_APPLY_ATTEMPT_ARTIFACT_TYPE:
        return _block(reason_code="apply_attempt_record_missing", apply_attempt_id=attempt_id)
    if not attempt_id:
        return _block(reason_code="apply_attempt_record_missing")
    if not authorization_id:
        return _block(
            reason_code="authorization_link_missing",
            apply_attempt_id=attempt_id,
            draft_proposal_id=draft_id,
            evidence_chain=evidence_chain,
        )

    if authorization_record is None:
        try:
            authorization = load_draft_patch_proposal_apply_authorization_record(
                authorization_id
            )
        except (OSError, ValueError, json.JSONDecodeError) as error:
            return _block(
                reason_code="authorization_link_missing",
                apply_attempt_id=attempt_id,
                authorization_id=authorization_id,
                draft_proposal_id=draft_id,
                evidence_chain=evidence_chain,
                detail=str(error),
            )
    else:
        authorization = authorization_record

    smuggled_reason = _claim_reason(attempt) or _claim_reason(authorization)
    if smuggled_reason:
        return _block(
            reason_code=smuggled_reason,
            apply_attempt_id=attempt_id,
            authorization_id=authorization_id,
            draft_proposal_id=draft_id,
            evidence_chain=evidence_chain,
        )

    operations, operation_reason = _expected_operations(authorization)
    expected_files = list(dict.fromkeys(operation["file_path"] for operation in operations))
    observed_files = _observed_files(attempt)
    unexpected_files = [
        path for path in observed_files if _path_identity(path) not in {_path_identity(p) for p in expected_files}
    ]
    common = {
        "apply_attempt_id": attempt_id,
        "authorization_id": authorization_id,
        "draft_proposal_id": draft_id,
        "evidence_chain": evidence_chain,
        "files_expected": expected_files,
        "files_observed": observed_files,
        "unexpected_files": unexpected_files,
    }

    if operation_reason:
        return _block(reason_code=operation_reason, **common)
    if _matching_finalization_exists(
        attempt=attempt,
        finalization_records=finalization_records,
    ):
        return _block(reason_code="existing_finalization_record_blocks_verification", **common)
    chain_reason = _chain_reason(attempt=attempt, authorization=authorization)
    if chain_reason:
        return _block(reason_code=chain_reason, **common)

    apply_status = _normalize_text(attempt.get("apply_status"))
    if apply_status not in _ALLOWED_APPLY_STATUSES:
        return _block(reason_code="apply_attempt_status_invalid", **common)
    if apply_status in {"failed", "blocked"}:
        return _artifact(
            verification_status=MECHANICALLY_VERIFIED,
            reason_code=f"{apply_status}_state_preserved:{_normalize_text(attempt.get('reason_code'))}",
            patch_verified_mechanically=True,
            **common,
        )
    for path in expected_files + observed_files:
        try:
            resolve_declared_project_path(path)
        except (TypeError, ValueError):
            return _block(reason_code="unbounded_file_path_blocks_verification", **common)
    if unexpected_files:
        return _block(reason_code="unexpected_changed_file_blocks_verification", **common)

    if not observed_files:
        return _block(reason_code="missing_observed_changed_file_fails_verification", status=VERIFICATION_FAILED, **common)
    missing = [
        path for path in expected_files if _path_identity(path) not in {_path_identity(p) for p in observed_files}
    ]
    if missing:
        return _block(
            reason_code="missing_expected_changed_file_fails_verification",
            status=VERIFICATION_FAILED,
            **common,
        )

    phase_99 = _as_mapping(attempt.get("phase_99_apply_result_reference"))
    if phase_99.get("applied") is not True:
        return _block(reason_code="applied_attempt_lacks_phase_99_applied_evidence", **common)
    if phase_99.get("verification_satisfied") is not False or phase_99.get("task_completed") is not False:
        return _block(reason_code="finalization_smuggling_rejected", **common)

    after_sha256 = _as_mapping(phase_99.get("after_sha256"))
    before_sha256 = _as_mapping(phase_99.get("before_sha256"))
    for file_path in expected_files:
        if file_path not in after_sha256 or file_path not in before_sha256:
            return _block(
                reason_code="missing_phase_99_hash_evidence_fails_verification",
                status=VERIFICATION_FAILED,
                **common,
            )
        if after_sha256[file_path] == before_sha256[file_path]:
            return _block(
                reason_code="changed_content_mismatch_fails_verification",
                status=VERIFICATION_FAILED,
                **common,
            )
        current_text = resolve_declared_project_path(file_path).read_text(encoding="utf-8")
        if _sha256_text(current_text) != after_sha256[file_path]:
            return _block(
                reason_code="changed_content_mismatch_fails_verification",
                status=VERIFICATION_FAILED,
                **common,
            )
    for operation in operations:
        current_text = resolve_declared_project_path(operation["file_path"]).read_text(
            encoding="utf-8"
        )
        if operation["replacement_after"] not in current_text:
            return _block(
                reason_code="changed_content_mismatch_fails_verification",
                status=VERIFICATION_FAILED,
                **common,
            )

    return _artifact(
        verification_status=MECHANICALLY_VERIFIED,
        reason_code="applied_attempt_mechanically_verified",
        patch_verified_mechanically=True,
        **common,
    )
