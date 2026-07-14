"""End-to-end non-executing intake-to-admission pipeline contract.

This module composes the Phase 113 fixture contract with the Phase 111 route
proposal/admission contract. It does not infer raw prompt intent or execute
routes.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from orchestrator.prompt_to_envelope import (
    PromptInferenceDecision,
    PromptInferenceFixture,
    classify_prompt_fixture,
    fixture_to_request_intake,
)
from orchestrator.route_proposal import (
    AdmissionDecision,
    CandidateRouteProposal,
    RequestIntakeRecord,
    admit_route_proposal,
    build_candidate_route_envelope,
)


NO_ACTIVITY_FLAGS = {
    "mutation_performed": False,
    "execution_performed": False,
    "provider_executed": False,
    "model_executed": False,
    "runtime_executed": False,
    "wsl_executed": False,
    "installer_executed": False,
    "discord_executed": False,
    "bridge_executed": False,
    "adapter_executed": False,
    "platform_executed": False,
    "export_performed": False,
    "package_performed": False,
    "cleanup_performed": False,
    "deletion_performed": False,
    "archive_performed": False,
}

PIPELINE_NON_PROOFS = (
    "pipeline_is_not_live_prompt_inference",
    "pipeline_is_not_natural_language_intent_inference",
    "pipeline_is_not_regex_classifier",
    "pipeline_is_not_model_provider_inference",
    "pipeline_is_not_live_router",
    "pipeline_is_not_route_execution",
    "pipeline_does_not_select_provider_model_runtime_platform_or_worker_substrate",
    "pipeline_does_not_perform_rag_or_local_lookup",
    "pipeline_does_not_perform_web_lookup",
    "pipeline_does_not_execute_scheduler_or_reminder",
    "pipeline_does_not_execute_connector",
    "pipeline_does_not_mutate_files",
    "pipeline_does_not_export_or_package_artifacts",
    "pipeline_does_not_cleanup_delete_or_archive",
    "pipeline_does_not_execute_production_work",
    "pipeline_is_not_production_readiness",
)

EMPTY_CAPABILITY_ASSESSMENT = {
    "requested_capabilities": [],
    "known_capabilities": [],
    "unknown_capabilities": [],
    "maturity_statuses": {},
    "blocked_or_external_capabilities": [],
    "production_ready_capabilities": [],
    "non_proofs": [],
    "admission_notes": ["pipeline_stopped_before_route_validation"],
    "authorized_execution": False,
}


@dataclass(frozen=True)
class IntakeAdmissionPipelineResult:
    pipeline_stage: str
    accepted: bool
    request_id: str
    request_type: str
    fixture_decision: PromptInferenceDecision | None
    intake_record: RequestIntakeRecord | None
    candidate_route: CandidateRouteProposal | None
    admission_decision: AdmissionDecision | None
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    capability_assessment: dict[str, Any]
    recommended_next_action: str
    non_proofs: tuple[str, ...]
    no_activity_flags: dict[str, bool]
    execution_authority: bool = False
    structured_capability_assessment: dict[str, Any] | None = None


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _tuple_of_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(text for text in (_normalize_text(item) for item in value) if text)


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _coerce_intake(value: RequestIntakeRecord | dict[str, Any]) -> RequestIntakeRecord:
    if isinstance(value, RequestIntakeRecord):
        return value
    if not isinstance(value, dict):
        raise ValueError("structured_intake_record_required")

    required = {
        "request_id",
        "observed_request_summary",
        "request_type",
        "confidence",
        "required_capabilities",
        "missing_inputs",
        "risk_level",
        "execution_policy",
        "recommended_next_action",
        "requires_operator_confirmation",
        "requires_external_connector",
        "allowed_to_answer_directly",
        "allowed_to_mutate_files",
        "allowed_to_schedule",
        "allowed_to_use_local_documents",
        "allowed_to_use_web",
        "reasoning_summary_for_operator",
    }
    if not required.issubset(value):
        raise ValueError("structured_intake_fields_required")

    return RequestIntakeRecord(
        request_id=_normalize_text(value.get("request_id")),
        observed_request_summary=_normalize_text(value.get("observed_request_summary")),
        request_type=_normalize_text(value.get("request_type")),
        confidence=value.get("confidence"),
        required_capabilities=_tuple_of_text(value.get("required_capabilities")),
        missing_inputs=_tuple_of_text(value.get("missing_inputs")),
        risk_level=_normalize_text(value.get("risk_level")),
        execution_policy=_normalize_text(value.get("execution_policy")),
        recommended_next_action=_normalize_text(value.get("recommended_next_action")),
        requires_operator_confirmation=value.get("requires_operator_confirmation") is True,
        requires_external_connector=value.get("requires_external_connector") is True,
        allowed_to_answer_directly=value.get("allowed_to_answer_directly") is True,
        allowed_to_mutate_files=value.get("allowed_to_mutate_files") is True,
        allowed_to_schedule=value.get("allowed_to_schedule") is True,
        allowed_to_use_local_documents=value.get("allowed_to_use_local_documents") is True,
        allowed_to_use_web=value.get("allowed_to_use_web") is True,
        reasoning_summary_for_operator=_normalize_text(value.get("reasoning_summary_for_operator")),
        caveats=_tuple_of_text(value.get("caveats", ())),
        intake_source=_normalize_text(value.get("intake_source", "structured_operator_intake")),
        structured_capability_assessment=value.get("structured_capability_assessment"),
    )


def _stopped_result(
    fixture_decision: PromptInferenceDecision,
) -> IntakeAdmissionPipelineResult:
    stage = (
        "fixture_needs_clarification"
        if fixture_decision.route_admission == "needs_clarification"
        else "fixture_classification_blocked"
    )
    return IntakeAdmissionPipelineResult(
        pipeline_stage=stage,
        accepted=False,
        request_id=fixture_decision.fixture_id,
        request_type=fixture_decision.request_type,
        fixture_decision=fixture_decision,
        intake_record=None,
        candidate_route=None,
        admission_decision=None,
        blocked_conditions=fixture_decision.blocked_conditions,
        missing_requirements=fixture_decision.missing_inputs,
        capability_assessment=deepcopy(EMPTY_CAPABILITY_ASSESSMENT),
        recommended_next_action=fixture_decision.recommended_next_action,
        non_proofs=_dedupe(PIPELINE_NON_PROOFS + fixture_decision.non_proofs),
        no_activity_flags=dict(NO_ACTIVITY_FLAGS),
        execution_authority=False,
        structured_capability_assessment=None,
    )


def _result_from_admission(
    intake_record: RequestIntakeRecord,
    candidate_route: CandidateRouteProposal,
    admission_decision: AdmissionDecision,
    fixture_decision: PromptInferenceDecision | None = None,
) -> IntakeAdmissionPipelineResult:
    non_proofs = PIPELINE_NON_PROOFS + admission_decision.non_proofs
    if fixture_decision is not None:
        non_proofs += fixture_decision.non_proofs

    return IntakeAdmissionPipelineResult(
        pipeline_stage="route_admission_decided",
        accepted=admission_decision.accepted,
        request_id=admission_decision.request_id,
        request_type=admission_decision.request_type,
        fixture_decision=fixture_decision,
        intake_record=intake_record,
        candidate_route=candidate_route,
        admission_decision=admission_decision,
        blocked_conditions=admission_decision.blocked_conditions,
        missing_requirements=admission_decision.missing_requirements,
        capability_assessment=deepcopy(admission_decision.capability_assessment),
        recommended_next_action=admission_decision.recommended_next_action,
        non_proofs=_dedupe(non_proofs),
        no_activity_flags=dict(admission_decision.activity_flags),
        execution_authority=False,
        structured_capability_assessment=deepcopy(
            admission_decision.structured_capability_assessment
        ),
    )


def run_fixture_admission_pipeline(
    fixture: PromptInferenceFixture | dict[str, Any],
) -> IntakeAdmissionPipelineResult:
    """Run fixture classification through non-executing route admission."""

    fixture_decision = classify_prompt_fixture(fixture)
    if not fixture_decision.accepted:
        return _stopped_result(fixture_decision)

    intake_record = fixture_to_request_intake(fixture_decision)
    candidate_route = build_candidate_route_envelope(intake_record)
    admission_decision = admit_route_proposal(candidate_route)
    return _result_from_admission(
        intake_record,
        candidate_route,
        admission_decision,
        fixture_decision,
    )


def run_structured_intake_admission_pipeline(
    intake: RequestIntakeRecord | dict[str, Any],
) -> IntakeAdmissionPipelineResult:
    """Run structured intake through non-executing route admission."""

    intake_record = _coerce_intake(intake)
    candidate_route = build_candidate_route_envelope(intake_record)
    admission_decision = admit_route_proposal(candidate_route)
    return _result_from_admission(intake_record, candidate_route, admission_decision)
