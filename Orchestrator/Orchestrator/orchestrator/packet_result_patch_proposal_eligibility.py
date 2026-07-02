from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.current_success_result_review import review_current_success_task_result
from orchestrator.operator_packet_result_decision import (
    latest_packet_result_operator_decision_summary,
)
from orchestrator.paths import validate_record_id


ELIGIBILITY_SURFACE = "packet_result_patch_proposal_eligibility"

_READY_CURRENT_SUCCESS_CLASSIFICATIONS = {"completed_current_state_success"}

_STRUCTURED_PATCH_CANDIDATE_FIELDS = (
    "proposed_changes",
    "unified_diff",
    "rationale",
)

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
}

_NO_ACTIVITY_FLAGS = {
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
    "packet_acceptance_is_not_patch_authorization",
    "eligibility_is_not_patch_authorization",
    "eligibility_does_not_create_patch_proposal",
    "eligibility_does_not_apply_patch",
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


def _path_exists(value: Any) -> bool:
    text = _normalize_text(value)
    return bool(text) and Path(text).exists()


def _validate_optional_id(value: Any, *, label: str) -> tuple[str, str | None]:
    text = _normalize_text(value)
    if not text:
        return "", None
    try:
        return validate_record_id(text, label=label), None
    except ValueError as error:
        return "", str(error)


def _claim_blocks(payloads: list[dict[str, Any]]) -> list[str]:
    blocks: list[str] = []
    for payload in payloads:
        for field_name, reason_code in _SMUGGLED_CLAIM_FIELDS.items():
            value = payload.get(field_name)
            if isinstance(value, bool):
                present = value
            else:
                present = bool(_normalize_text(value))
            if present:
                blocks.append(reason_code)
    return sorted(set(blocks))


def _structured_patch_evidence(packet_result: dict[str, Any]) -> tuple[list[str], list[dict[str, str]]]:
    evidence = _as_mapping(
        packet_result.get("structured_patch_candidate_evidence")
        or packet_result.get("patch_candidate_evidence")
    )
    missing = [
        field_name
        for field_name in _STRUCTURED_PATCH_CANDIDATE_FIELDS
        if not evidence.get(field_name)
    ]
    linked = []
    if evidence:
        linked.append(
            {
                "evidence_type": "structured_patch_candidate_evidence",
                "evidence_id": _normalize_text(
                    evidence.get("evidence_id") or evidence.get("candidate_evidence_id")
                ),
                "source": "packet_result",
            }
        )
    return missing, linked


def _result(
    *,
    status: str,
    reason_code: str,
    task_id: str,
    packet_id: str = "",
    run_id: str = "",
    missing_evidence: list[str] | None = None,
    linked_evidence: list[dict[str, str]] | None = None,
    caveats: list[str] | None = None,
    blocked_conditions: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "packet_result_patch_proposal_eligibility_surface": True,
        "surface": ELIGIBILITY_SURFACE,
        "status": status,
        "eligible": status == "eligible",
        "ineligible": status == "ineligible",
        "blocked": status == "blocked",
        "reason_code": reason_code,
        "task_id": task_id,
        "packet_id": packet_id,
        "run_id": run_id,
        "missing_evidence": sorted(set(missing_evidence or [])),
        "linked_evidence": linked_evidence or [],
        "caveats": caveats or [],
        "non_proofs": list(_NON_PROOFS),
        "no_apply_authorization": True,
        "packet_acceptance_is_not_patch_authorization": True,
        "eligibility_is_not_patch_authorization": True,
        "patch_proposal_created": False,
        "patch_apply_authorized": False,
        "patch_applied": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "blocked_conditions": sorted(set(blocked_conditions or [])),
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        **_NO_ACTIVITY_FLAGS,
    }


def evaluate_packet_result_patch_proposal_eligibility(
    eligibility_input: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(eligibility_input, dict):
        return _result(
            status="blocked",
            reason_code="json_object_input_required",
            task_id="",
            missing_evidence=["eligibility_input"],
            blocked_conditions=["json_object_input_required"],
        )

    task_id, task_id_error = _validate_optional_id(
        eligibility_input.get("task_id"),
        label="task id",
    )
    if task_id_error or not task_id:
        return _result(
            status="blocked",
            reason_code="task_id_invalid_or_missing",
            task_id="",
            missing_evidence=["task_id"],
            caveats=[task_id_error] if task_id_error else [],
            blocked_conditions=["task_id_invalid_or_missing"],
        )

    current_success = _as_mapping(eligibility_input.get("current_success_review"))
    if not current_success:
        current_success = review_current_success_task_result({"task_id": task_id})

    decision = _as_mapping(eligibility_input.get("operator_decision_summary"))
    if not decision:
        decision = latest_packet_result_operator_decision_summary(task_id)

    packet_result = _as_mapping(eligibility_input.get("packet_result"))
    artifact_summary = _as_mapping(current_success.get("artifact_summary"))
    verification_summary = _as_mapping(current_success.get("verification_summary"))

    packet_id, packet_id_error = _validate_optional_id(
        eligibility_input.get("packet_id")
        or decision.get("packet_id")
        or packet_result.get("packet_id"),
        label="packet id",
    )
    run_id, run_id_error = _validate_optional_id(
        eligibility_input.get("run_id")
        or decision.get("run_id")
        or current_success.get("run_id")
        or packet_result.get("run_id"),
        label="run id",
    )

    missing: list[str] = []
    blocked: list[str] = []
    caveats: list[str] = []
    linked_evidence: list[dict[str, str]] = []

    if packet_id_error:
        missing.append("packet_id")
        blocked.append("packet_id_invalid")
        caveats.append(packet_id_error)
    if run_id_error:
        missing.append("run_id")
        blocked.append("run_id_invalid")
        caveats.append(run_id_error)

    if not packet_result:
        missing.append("completed_packet_result")
        blocked.append("completed_packet_result_missing")
    elif _normalize_text(packet_result.get("status")) not in {"completed", "accepted_completed"}:
        blocked.append("packet_result_not_completed")

    artifact_id = (
        _normalize_text(artifact_summary.get("artifact_id"))
        or _normalize_text(decision.get("execution_artifact_id"))
        or _normalize_text(packet_result.get("execution_artifact_id"))
    )
    artifact_path = (
        _normalize_text(artifact_summary.get("artifact_path"))
        or _normalize_text(packet_result.get("execution_artifact_path"))
    )
    if not artifact_id:
        missing.append("execution_artifact_id")
        blocked.append("execution_artifact_id_missing")
    if not _path_exists(artifact_path):
        missing.append("execution_artifact_path")
        blocked.append("execution_artifact_missing")

    verifier_path = (
        _normalize_text(verification_summary.get("verifier_result_path"))
        or _normalize_text(decision.get("verifier_result_path"))
        or _normalize_text(packet_result.get("verifier_result_path"))
    )
    if not _path_exists(verifier_path):
        missing.append("verifier_result_path")
        blocked.append("verifier_result_missing")

    review_classification = _normalize_text(
        current_success.get("final_outcome_classification")
        or decision.get("current_success_review_classification")
    )
    if review_classification not in _READY_CURRENT_SUCCESS_CLASSIFICATIONS:
        missing.append("current_success_ready_classification")
        blocked.append("current_success_not_ready")

    if not decision.get("operator_decision_record_present"):
        missing.append("operator_decision_record")
        blocked.append("operator_decision_missing")
    elif not decision.get("accepted"):
        missing.append("accepted_operator_decision")
        return _result(
            status="ineligible",
            reason_code="operator_decision_not_accepted",
            task_id=task_id,
            packet_id=packet_id,
            run_id=run_id,
            missing_evidence=missing,
            linked_evidence=linked_evidence,
            caveats=caveats,
            blocked_conditions=blocked,
        )

    if not decision.get("operator_note_present") and not _normalize_text(
        decision.get("operator_note") or eligibility_input.get("operator_note")
    ):
        missing.append("operator_note")
        blocked.append("operator_note_missing")

    mismatches: list[str] = []
    if _normalize_text(decision.get("task_id")) and _normalize_text(decision.get("task_id")) != task_id:
        mismatches.append("task_id")
    if _normalize_text(decision.get("execution_artifact_id")) and artifact_id:
        if _normalize_text(decision.get("execution_artifact_id")) != artifact_id:
            mismatches.append("execution_artifact_id")
    if _normalize_text(decision.get("verifier_result_path")) and verifier_path:
        if _normalize_text(decision.get("verifier_result_path")) != verifier_path:
            mismatches.append("verifier_result_path")
    if _normalize_text(decision.get("current_success_review_classification")) and review_classification:
        if _normalize_text(decision.get("current_success_review_classification")) != review_classification:
            mismatches.append("current_success_review_classification")
    if mismatches:
        missing.extend([f"matching_{field_name}" for field_name in mismatches])
        blocked.append("decision_evidence_link_mismatch")

    claim_blocks = _claim_blocks([eligibility_input, packet_result, decision, current_success])
    if claim_blocks:
        missing.extend(claim_blocks)
        blocked.extend(claim_blocks)

    patch_missing, patch_linked = _structured_patch_evidence(packet_result)
    if patch_missing:
        missing.extend([f"structured_patch_candidate_evidence.{field}" for field in patch_missing])
    linked_evidence.extend(patch_linked)

    if artifact_id:
        linked_evidence.append({"evidence_type": "execution_artifact", "evidence_id": artifact_id, "path": artifact_path})
    if verifier_path:
        linked_evidence.append({"evidence_type": "verifier_result", "evidence_id": "", "path": verifier_path})
    if decision.get("operator_decision_record_id"):
        linked_evidence.append(
            {
                "evidence_type": "operator_decision_record",
                "evidence_id": _normalize_text(decision.get("operator_decision_record_id")),
                "path": _normalize_text(decision.get("operator_decision_record_path")),
            }
        )

    if blocked:
        return _result(
            status="blocked",
            reason_code=sorted(set(blocked))[0],
            task_id=task_id,
            packet_id=packet_id,
            run_id=run_id,
            missing_evidence=missing,
            linked_evidence=linked_evidence,
            caveats=caveats,
            blocked_conditions=blocked,
        )

    if patch_missing:
        return _result(
            status="ineligible",
            reason_code="structured_patch_candidate_evidence_missing",
            task_id=task_id,
            packet_id=packet_id,
            run_id=run_id,
            missing_evidence=missing,
            linked_evidence=linked_evidence,
            caveats=caveats,
        )

    return _result(
        status="eligible",
        reason_code="accepted_packet_result_has_patch_candidate_evidence",
        task_id=task_id,
        packet_id=packet_id,
        run_id=run_id,
        missing_evidence=[],
        linked_evidence=linked_evidence,
        caveats=caveats,
    )


def packet_result_patch_proposal_eligibility_summary(task_id: str) -> dict[str, Any]:
    return evaluate_packet_result_patch_proposal_eligibility({"task_id": task_id})
