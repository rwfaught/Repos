"""Structured route proposal source and admission pipeline.

This module is deterministic and non-executing. It does not infer route intent
from raw natural language, select providers/models/runtimes/substrates, access
connectors, schedule reminders, perform lookups, or mutate files.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from orchestrator.request_routing import validate_route_envelope


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

SUBSTRATE_EXECUTOR_TERMS = (
    "codex",
    "hermes",
    "openclaw",
    "ollama",
    "qwen",
    "openai",
    "anthropic",
    "provider",
    "model",
    "runtime",
    "platform",
    "worker_substrate",
    "executor",
)

SUBSTRATE_SENSITIVE_FIELDS = (
    "execution_policy",
    "recommended_next_action",
    "reasoning_summary_for_operator",
    "intake_source",
)

STRUCTURED_CAPABILITY_ASSESSMENT_FIELDS = (
    "input_completeness",
    "objective_clarity",
    "consequence_level",
    "external_capability_dependency",
    "reviewability",
    "reversibility",
    "requires_human_decision",
    "blocked_conditions",
    "missing_information",
)

_CAPABILITY_ASSESSMENT_ALLOWED_VALUES = {
    "input_completeness": {"complete", "incomplete"},
    "objective_clarity": {"clear", "needs_clarification"},
    "consequence_level": {"low", "moderate", "elevated", "high"},
    "reviewability": {"reviewable", "not_reviewable"},
    "reversibility": {"reversible", "limited", "irreversible"},
}

ROUTE_ENVELOPE_FIELDS = (
    "request_id",
    "request_type",
    "confidence",
    "user_intent_summary",
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
    "caveats",
)


@dataclass(frozen=True)
class RequestIntakeRecord:
    request_id: str
    observed_request_summary: str
    request_type: str
    confidence: float
    required_capabilities: tuple[str, ...]
    missing_inputs: tuple[str, ...]
    risk_level: str
    execution_policy: str
    recommended_next_action: str
    requires_operator_confirmation: bool
    requires_external_connector: bool
    allowed_to_answer_directly: bool
    allowed_to_mutate_files: bool
    allowed_to_schedule: bool
    allowed_to_use_local_documents: bool
    allowed_to_use_web: bool
    reasoning_summary_for_operator: str
    caveats: tuple[str, ...] = ()
    intake_source: str = "structured_operator_intake"
    structured_capability_assessment: dict[str, Any] | None = None


@dataclass(frozen=True)
class CandidateRouteProposal:
    request_id: str
    proposal_source: str
    route_envelope: dict[str, Any]
    proposal_state: str
    non_proofs: tuple[str, ...]
    structured_capability_assessment: dict[str, Any] | None = None


@dataclass(frozen=True)
class AdmissionDecision:
    request_id: str
    route_admission: str
    accepted: bool
    request_type: str
    missing_requirements: tuple[str, ...]
    blocked_conditions: tuple[str, ...]
    capability_assessment: dict[str, Any]
    recommended_next_action: str
    next_boundary_kind: str
    emitted_boundary_type: str
    non_proofs: tuple[str, ...]
    activity_statement: str
    candidate_proposal_state: str
    validated_envelope_state: str
    accepted_route_state: str
    execution_authority: bool
    activity_flags: dict[str, bool]
    structured_capability_assessment: dict[str, Any] | None = None


def _capability_assessment_decision(
    *,
    assessment_state: str,
    accepted: bool,
    missing_information: tuple[str, ...] = (),
    blocked_conditions: tuple[str, ...] = (),
    review_reasons: tuple[str, ...] = (),
    next_bounded_action: str,
    next_boundary_kind: str,
    normalized_assessment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a provider-neutral, non-executing assessment decision."""
    return {
        "assessment_state": assessment_state,
        "accepted": accepted,
        "normalized_assessment": deepcopy(normalized_assessment)
        if normalized_assessment is not None
        else None,
        "missing_information": list(missing_information),
        "blocked_conditions": list(blocked_conditions),
        "review_reasons": list(review_reasons),
        "next_bounded_action": next_bounded_action,
        "next_boundary_kind": next_boundary_kind,
        "execution_authority": False,
        "authorization_created": False,
        "dispatch_performed": False,
        "canonical_execution_state_created": False,
        "non_proofs": [
            "structured_capability_assessment_is_not_execution_authority",
            "structured_capability_assessment_does_not_select_execution_substrate",
            "structured_capability_assessment_does_not_create_persistence",
        ],
    }


def _strict_text_list(value: Any, field_name: str) -> tuple[tuple[str, ...], str | None]:
    if not isinstance(value, list):
        return (), f"capability_assessment_{field_name}_must_be_list"
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return (), f"capability_assessment_{field_name}_must_contain_non_empty_strings"
    return tuple(item.strip() for item in value), None


def assess_structured_capability_assessment(value: Any) -> dict[str, Any] | None:
    """Assess explicit capability facts without inferring raw objective intent.

    ``None`` preserves the existing intake/admission behavior. Any supplied
    assessment is strict: unknown fields and malformed values are rejected
    rather than coerced into a route decision.
    """
    if value is None:
        return None
    if not isinstance(value, dict):
        return _capability_assessment_decision(
            assessment_state="blocked",
            accepted=False,
            blocked_conditions=("structured_capability_assessment_must_be_object",),
            next_bounded_action="provide_a_structured_capability_assessment",
            next_boundary_kind="reject_or_reframe",
        )

    unknown_fields = sorted(set(value) - set(STRUCTURED_CAPABILITY_ASSESSMENT_FIELDS))
    missing_fields = [
        field for field in STRUCTURED_CAPABILITY_ASSESSMENT_FIELDS if field not in value
    ]
    validation_errors: list[str] = []
    if unknown_fields:
        validation_errors.append("structured_capability_assessment_unknown_fields")
    if missing_fields:
        validation_errors.append("structured_capability_assessment_missing_required_fields")

    normalized: dict[str, Any] = {}
    for field, allowed_values in _CAPABILITY_ASSESSMENT_ALLOWED_VALUES.items():
        raw = value.get(field)
        if not isinstance(raw, str) or raw not in allowed_values:
            validation_errors.append(f"capability_assessment_{field}_invalid")
        else:
            normalized[field] = raw

    for field in ("external_capability_dependency", "requires_human_decision"):
        raw = value.get(field)
        if not isinstance(raw, bool):
            validation_errors.append(f"capability_assessment_{field}_must_be_boolean")
        else:
            normalized[field] = raw

    for field in ("blocked_conditions", "missing_information"):
        values, error = _strict_text_list(value.get(field), field)
        if error:
            validation_errors.append(error)
        else:
            normalized[field] = list(values)

    if not validation_errors:
        if normalized["input_completeness"] == "complete" and normalized["missing_information"]:
            validation_errors.append(
                "capability_assessment_complete_input_cannot_have_missing_information"
            )
        if normalized["input_completeness"] == "incomplete" and not normalized["missing_information"]:
            validation_errors.append(
                "capability_assessment_incomplete_input_requires_missing_information"
            )

    if validation_errors:
        return _capability_assessment_decision(
            assessment_state="blocked",
            accepted=False,
            missing_information=tuple(missing_fields),
            blocked_conditions=tuple(sorted(set(validation_errors))),
            next_bounded_action="repair_the_structured_capability_assessment",
            next_boundary_kind="reject_or_reframe",
        )

    if (
        normalized["input_completeness"] == "incomplete"
        or normalized["objective_clarity"] == "needs_clarification"
        or normalized["missing_information"]
    ):
        return _capability_assessment_decision(
            assessment_state="clarification_required",
            accepted=False,
            missing_information=tuple(normalized["missing_information"]),
            next_bounded_action="ask_operator_for_missing_capability_information",
            next_boundary_kind="ask_clarification",
            normalized_assessment=normalized,
        )

    if normalized["blocked_conditions"]:
        return _capability_assessment_decision(
            assessment_state="blocked",
            accepted=False,
            blocked_conditions=tuple(normalized["blocked_conditions"]),
            next_bounded_action="resolve_blocked_capability_conditions",
            next_boundary_kind="reject_or_reframe",
            normalized_assessment=normalized,
        )

    review_reasons = []
    if normalized["consequence_level"] in {"elevated", "high"}:
        review_reasons.append("elevated_consequence")
    if normalized["external_capability_dependency"]:
        review_reasons.append("external_capability_dependency")
    if normalized["reviewability"] == "not_reviewable":
        review_reasons.append("reviewability_not_established")
    if normalized["reversibility"] == "irreversible":
        review_reasons.append("irreversible_effect")
    if normalized["requires_human_decision"]:
        review_reasons.append("human_decision_required")
    if review_reasons:
        return _capability_assessment_decision(
            assessment_state="operator_review_required",
            accepted=True,
            review_reasons=tuple(review_reasons),
            next_bounded_action="obtain_operator_capability_review_before_next_boundary",
            next_boundary_kind="ready_for_coordinator_boundary_decision",
            normalized_assessment=normalized,
        )

    return _capability_assessment_decision(
        assessment_state="eligible_for_bounded_next_boundary",
        accepted=True,
        next_bounded_action="prepare_bounded_next_boundary_from_structured_intake",
        next_boundary_kind="ready_for_coordinator_boundary_decision",
        normalized_assessment=normalized,
    )


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _tuple_of_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(text for text in (_normalize_text(item) for item in value) if text)


def _contains_substrate_reference(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_contains_substrate_reference(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_substrate_reference(item) for item in value)

    text = _normalize_text(value).lower()
    if not text:
        return False
    substrate_phrase = any(
        phrase in text
        for phrase in (
            "execute with",
            "run with",
            "handled by",
            "provider:",
            "model:",
            "runtime:",
            "platform:",
            "worker substrate",
        )
    )
    return substrate_phrase and any(term in text for term in SUBSTRATE_EXECUTOR_TERMS)


def _coerce_intake_record(value: RequestIntakeRecord | dict[str, Any]) -> RequestIntakeRecord | None:
    if isinstance(value, RequestIntakeRecord):
        return value
    if not isinstance(value, dict):
        return None

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
        return None

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


def _non_proofs(extra: tuple[str, ...] = ()) -> tuple[str, ...]:
    return (
        "candidate_route_proposal_is_not_authorization",
        "validated_route_envelope_is_not_execution",
        "accepted_route_is_not_execution_authority",
        "admission_pipeline_does_not_infer_raw_prompt_intent",
        "admission_pipeline_does_not_select_provider_model_runtime_platform_or_worker_substrate",
        "admission_pipeline_does_not_mutate_files",
    ) + extra


def _needs_clarification_decision(request_id: str, reason: str) -> AdmissionDecision:
    return AdmissionDecision(
        request_id=request_id,
        route_admission="needs_clarification",
        accepted=False,
        request_type="needs_clarification",
        missing_requirements=(reason,),
        blocked_conditions=(),
        capability_assessment={
            "requested_capabilities": [],
            "known_capabilities": [],
            "unknown_capabilities": [],
            "maturity_statuses": {},
            "blocked_or_external_capabilities": [],
            "production_ready_capabilities": [],
            "non_proofs": [],
            "admission_notes": ["structured_route_fields_required", "raw_prompt_not_inferred"],
            "authorized_execution": False,
        },
        recommended_next_action="ask_operator_for_structured_route_fields",
        next_boundary_kind="ask_clarification",
        emitted_boundary_type="ask_clarification",
        non_proofs=_non_proofs(("raw_or_unclassified_request_was_not_inferred",)),
        activity_statement=(
            "Route proposal admission only; no mutation, execution, provider, model, runtime, "
            "platform, connector, scheduler, lookup, export, package, cleanup, deletion, or archive occurred."
        ),
        candidate_proposal_state="not_proposed",
        validated_envelope_state="not_validated",
        accepted_route_state="not_accepted",
        execution_authority=False,
        activity_flags=dict(NO_ACTIVITY_FLAGS),
    )


def build_candidate_route_envelope(
    intake_record: RequestIntakeRecord | dict[str, Any],
) -> CandidateRouteProposal:
    """Build a validator-compatible candidate envelope from structured intake."""

    intake = _coerce_intake_record(intake_record)
    if intake is None:
        raise ValueError("structured_route_fields_required")

    assessment = assess_structured_capability_assessment(
        intake.structured_capability_assessment
    )
    intake_values = asdict(intake)
    for field in SUBSTRATE_SENSITIVE_FIELDS:
        if _contains_substrate_reference(intake_values.get(field)):
            envelope = {
                "request_id": intake.request_id,
                "request_type": intake.request_type or "needs_clarification",
                "confidence": intake.confidence,
                "user_intent_summary": intake.observed_request_summary,
                "required_capabilities": list(intake.required_capabilities),
                "missing_inputs": list(intake.missing_inputs),
                "risk_level": intake.risk_level,
                "execution_policy": intake.execution_policy,
                "recommended_next_action": intake.recommended_next_action,
                "requires_operator_confirmation": intake.requires_operator_confirmation,
                "requires_external_connector": intake.requires_external_connector,
                "allowed_to_answer_directly": intake.allowed_to_answer_directly,
                "allowed_to_mutate_files": intake.allowed_to_mutate_files,
                "allowed_to_schedule": intake.allowed_to_schedule,
                "allowed_to_use_local_documents": intake.allowed_to_use_local_documents,
                "allowed_to_use_web": intake.allowed_to_use_web,
                "reasoning_summary_for_operator": intake.reasoning_summary_for_operator,
                "caveats": list(intake.caveats) + ["route_proposal_substrate_smuggling_blocked"],
            }
            return CandidateRouteProposal(
                request_id=intake.request_id,
                proposal_source=intake.intake_source,
                route_envelope=envelope,
                proposal_state="candidate_route_proposed_with_substrate_smuggling_caveat",
                non_proofs=_non_proofs(("substrate_specific_smuggling_detected",)),
                structured_capability_assessment=assessment,
            )

    envelope = {
        "request_id": intake.request_id,
        "request_type": intake.request_type,
        "confidence": intake.confidence,
        "user_intent_summary": intake.observed_request_summary,
        "required_capabilities": list(intake.required_capabilities),
        "missing_inputs": list(intake.missing_inputs),
        "risk_level": intake.risk_level,
        "execution_policy": intake.execution_policy,
        "recommended_next_action": intake.recommended_next_action,
        "requires_operator_confirmation": intake.requires_operator_confirmation,
        "requires_external_connector": intake.requires_external_connector,
        "allowed_to_answer_directly": intake.allowed_to_answer_directly,
        "allowed_to_mutate_files": intake.allowed_to_mutate_files,
        "allowed_to_schedule": intake.allowed_to_schedule,
        "allowed_to_use_local_documents": intake.allowed_to_use_local_documents,
        "allowed_to_use_web": intake.allowed_to_use_web,
        "reasoning_summary_for_operator": intake.reasoning_summary_for_operator,
        "caveats": list(intake.caveats),
    }
    return CandidateRouteProposal(
        request_id=intake.request_id,
        proposal_source=intake.intake_source,
        route_envelope=envelope,
        proposal_state=(
            "candidate_route_proposed_with_structured_capability_assessment"
            if assessment is not None
            else "candidate_route_proposed"
        ),
        non_proofs=_non_proofs(),
        structured_capability_assessment=assessment,
    )


def _next_boundary_kind(validation_result: dict[str, Any]) -> str:
    request_type = validation_result["request_type"]
    blocked_conditions = validation_result["blocked_conditions"]
    assessment = validation_result["capability_assessment"]

    if validation_result["accepted"]:
        return "ready_for_coordinator_boundary_decision"
    if validation_result["route_admission"] == "needs_clarification":
        return "ask_clarification"
    if request_type == "unsupported_or_requires_connector":
        return "external_boundary_required"
    if "blocked_or_external_required_capabilities" in blocked_conditions:
        return "separate_boundary_required"
    if assessment.get("blocked_or_external_capabilities"):
        return "separate_boundary_required"
    return "reject_or_reframe"


def admit_route_proposal(
    intake_or_proposal: RequestIntakeRecord | CandidateRouteProposal | dict[str, Any],
) -> AdmissionDecision:
    """Validate a structured proposal and return a non-executing admission decision."""

    if isinstance(intake_or_proposal, CandidateRouteProposal):
        proposal = intake_or_proposal
    else:
        try:
            proposal = build_candidate_route_envelope(intake_or_proposal)
        except ValueError:
            request_id = ""
            if isinstance(intake_or_proposal, dict):
                request_id = _normalize_text(intake_or_proposal.get("request_id"))
            return _needs_clarification_decision(request_id, "structured_route_fields_required")

    validation_result = validate_route_envelope(deepcopy(proposal.route_envelope))
    next_boundary_kind = _next_boundary_kind(validation_result)
    blocked_conditions = tuple(validation_result["blocked_conditions"])
    if "route_proposal_substrate_smuggling_blocked" in proposal.route_envelope.get("caveats", ()):
        blocked_conditions = tuple(dict.fromkeys(blocked_conditions + ("route_proposal_substrate_smuggling_blocked",)))
        next_boundary_kind = "reject_or_reframe"

    assessment = proposal.structured_capability_assessment
    assessment_state = _normalize_text(assessment.get("assessment_state")) if assessment else ""
    assessment_accepted = assessment.get("accepted") is True if assessment else True
    if assessment:
        blocked_conditions = tuple(
            dict.fromkeys(blocked_conditions + tuple(assessment["blocked_conditions"]))
        )
        missing_requirements = tuple(
            dict.fromkeys(
                tuple(validation_result["missing_requirements"])
                + tuple(assessment["missing_information"])
            )
        )
        if assessment_state == "clarification_required":
            next_boundary_kind = "ask_clarification"
        elif assessment_state == "blocked":
            next_boundary_kind = "reject_or_reframe"
        elif assessment_state in {
            "operator_review_required",
            "eligible_for_bounded_next_boundary",
        }:
            next_boundary_kind = assessment["next_boundary_kind"]
    else:
        missing_requirements = tuple(validation_result["missing_requirements"])

    request_id = _normalize_text(proposal.route_envelope.get("request_id")) or proposal.request_id
    accepted = validation_result["accepted"] and "route_proposal_substrate_smuggling_blocked" not in blocked_conditions
    accepted = accepted and assessment_accepted
    route_admission = validation_result["route_admission"] if accepted else (
        "needs_clarification"
        if assessment_state == "clarification_required"
        or (validation_result["route_admission"] == "needs_clarification" and not blocked_conditions)
        else "rejected"
    )
    recommended_next_action = _normalize_text(proposal.route_envelope.get("recommended_next_action"))
    if assessment:
        recommended_next_action = assessment["next_bounded_action"]

    return AdmissionDecision(
        request_id=request_id,
        route_admission=route_admission,
        accepted=accepted,
        request_type=validation_result["request_type"],
        missing_requirements=missing_requirements,
        blocked_conditions=blocked_conditions,
        capability_assessment=deepcopy(validation_result["capability_assessment"]),
        recommended_next_action=recommended_next_action,
        next_boundary_kind=next_boundary_kind,
        emitted_boundary_type=next_boundary_kind,
        non_proofs=tuple(
            dict.fromkeys(
                proposal.non_proofs
                + tuple(validation_result["capability_assessment"].get("non_proofs", ()))
                + tuple(assessment["non_proofs"] if assessment else ())
            )
        ),
        activity_statement=(
            "Route proposal admission only; no mutation, execution, provider, model, runtime, "
            "platform, connector, scheduler, lookup, export, package, cleanup, deletion, or archive occurred."
        ),
        candidate_proposal_state=proposal.proposal_state,
        validated_envelope_state="validated_envelope_metadata_only",
        accepted_route_state="accepted_route_without_execution_authority" if accepted else "not_accepted",
        execution_authority=False,
        activity_flags={field: validation_result[field] for field in NO_ACTIVITY_FLAGS},
        structured_capability_assessment=deepcopy(assessment),
    )
