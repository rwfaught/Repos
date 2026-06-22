"""Coordinator-facing review report contract for fixture packet pipelines.

Review reports are deterministic artifacts only. They are not coordinator
ratification, worker dispatch, execution, substrate selection, or production
readiness.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from orchestrator.fixture_packet_pipeline import FixtureBoundaryPacketPipelineResult
from orchestrator.model_router_policy import recommend_model_route


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
    "rag_lookup_performed": False,
    "web_lookup_performed": False,
    "scheduler_executed": False,
    "connector_executed": False,
    "worker_dispatched": False,
    "codex_dispatched": False,
}

REPORT_NON_PROOFS = (
    "review_report_is_not_execution",
    "review_report_is_not_coordinator_ratification_by_itself",
    "review_report_is_not_worker_execution",
    "review_report_is_not_dispatch",
    "review_report_is_not_concrete_substrate_selection",
    "review_report_is_not_provider_model_selection",
    "review_report_is_not_route_execution",
    "review_report_is_not_production_readiness",
)


@dataclass(frozen=True)
class CoordinatorReviewReport:
    report_id: str
    source_request_id: str
    report_kind: str
    accepted: bool
    request_type: str
    pipeline_stage: str
    route_admission: str
    packet_kind: str
    boundary_name: str
    recommended_next_action: str
    next_boundary: str
    decision_summary: str
    accepted_facts: tuple[str, ...]
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    capability_assessment_summary: dict[str, Any]
    router_policy_recommendation: dict[str, Any]
    packet_text: str
    evidence_status: str
    non_proofs: tuple[str, ...]
    caveats: tuple[str, ...]
    no_activity_flags: dict[str, bool]


@dataclass(frozen=True)
class CoordinatorReviewReportResult:
    accepted: bool
    report: CoordinatorReviewReport
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    recommended_next_action: str
    non_proofs: tuple[str, ...]
    no_activity_flags: dict[str, bool]
    caveats: tuple[str, ...]


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _capability_summary(result: FixtureBoundaryPacketPipelineResult) -> dict[str, Any]:
    assessment = deepcopy(result.capability_assessment)
    return {
        "requested_capabilities": list(assessment.get("requested_capabilities", [])),
        "known_capabilities": list(assessment.get("known_capabilities", [])),
        "unknown_capabilities": list(assessment.get("unknown_capabilities", [])),
        "blocked_or_external_capabilities": list(assessment.get("blocked_or_external_capabilities", [])),
        "production_ready_capabilities": list(assessment.get("production_ready_capabilities", [])),
        "authorized_execution": assessment.get("authorized_execution") is True,
        "maturity_statuses": deepcopy(assessment.get("maturity_statuses", {})),
    }


def _router_policy_request(result: FixtureBoundaryPacketPipelineResult) -> dict[str, Any]:
    admission = result.intake_admission_result
    intake = admission.intake_record
    if intake is not None:
        return {
            "request_id": intake.request_id,
            "request_type": intake.request_type,
            "confidence": intake.confidence,
            "required_capabilities": list(intake.required_capabilities),
            "missing_inputs": list(intake.missing_inputs),
            "risk_level": intake.risk_level,
            "allowed_to_answer_directly": intake.allowed_to_answer_directly,
            "allowed_to_mutate_files": intake.allowed_to_mutate_files,
            "allowed_to_schedule": intake.allowed_to_schedule,
            "allowed_to_use_local_documents": intake.allowed_to_use_local_documents,
            "allowed_to_use_web": intake.allowed_to_use_web,
            "requires_operator_confirmation": intake.requires_operator_confirmation,
            "requires_external_connector": intake.requires_external_connector,
        }

    fixture_decision = admission.fixture_decision
    if fixture_decision is not None:
        required_capabilities = list(fixture_decision.required_capabilities)
        blocked = set(fixture_decision.blocked_conditions)
        if not required_capabilities and "provider_model_runtime_platform_requires_separate_boundary" in blocked:
            required_capabilities = ["provider_model", "platform_runtime"]
        if not required_capabilities and "production_execution_blocked" in blocked:
            required_capabilities = ["production_execution"]
        return {
            "request_id": fixture_decision.fixture_id,
            "request_type": fixture_decision.request_type,
            "confidence": fixture_decision.confidence,
            "required_capabilities": required_capabilities,
            "missing_inputs": list(fixture_decision.missing_inputs),
            "risk_level": fixture_decision.risk_level,
            "allowed_to_answer_directly": fixture_decision.allowed_to_answer_directly,
            "allowed_to_mutate_files": fixture_decision.allowed_to_mutate_files,
            "allowed_to_schedule": fixture_decision.allowed_to_schedule,
            "allowed_to_use_local_documents": fixture_decision.allowed_to_use_local_documents,
            "allowed_to_use_web": fixture_decision.allowed_to_use_web,
            "requires_operator_confirmation": fixture_decision.requires_operator_confirmation,
            "requires_external_connector": fixture_decision.requires_external_connector,
        }

    return {
        "request_id": result.request_id,
        "request_type": result.request_type,
        "confidence": None,
        "required_capabilities": list(result.capability_assessment.get("requested_capabilities", ())),
        "missing_inputs": list(result.missing_requirements),
        "risk_level": "unknown",
        "allowed_to_answer_directly": False,
        "allowed_to_mutate_files": False,
        "allowed_to_schedule": False,
        "allowed_to_use_local_documents": False,
        "allowed_to_use_web": False,
        "requires_operator_confirmation": False,
        "requires_external_connector": False,
    }


def _router_policy_summary(result: FixtureBoundaryPacketPipelineResult) -> dict[str, Any]:
    recommendation = recommend_model_route(_router_policy_request(result))
    return {
        "request_id": recommendation.request_id,
        "recommended_route": recommendation.recommended_route,
        "provider_posture": recommendation.provider_posture,
        "provider_catalog_key": recommendation.provider_catalog_key,
        "provider_tier": recommendation.provider_tier,
        "provider_maturity_status": recommendation.provider_maturity_status,
        "provider_allowed_boundary": recommendation.provider_allowed_boundary,
        "provider_required_authority": recommendation.provider_required_authority,
        "provider_execution_allowed": recommendation.provider_execution_allowed,
        "provider_selection_allowed": recommendation.provider_selection_allowed,
        "provider_catalog_escalation_posture": recommendation.provider_catalog_escalation_posture,
        "provider_catalog_fallback": recommendation.provider_catalog_fallback,
        "provider_catalog_non_proofs": list(recommendation.provider_catalog_non_proofs),
        "provider_catalog_activity_flags": dict(recommendation.provider_catalog_activity_flags),
        "confidence": recommendation.confidence,
        "reason": recommendation.reason,
        "fallback": recommendation.fallback,
        "escalation_posture": recommendation.escalation_posture,
        "required_boundary": recommendation.required_boundary,
        "blocked_conditions": list(recommendation.blocked_conditions),
        "missing_requirements": list(recommendation.missing_requirements),
        "non_proofs": list(recommendation.non_proofs),
        "activity_flags": dict(recommendation.activity_flags),
    }


def _route_admission(result: FixtureBoundaryPacketPipelineResult) -> str:
    admission = result.intake_admission_result.admission_decision
    if admission is None:
        return "not_admitted"
    return admission.route_admission


def _accepted_facts(result: FixtureBoundaryPacketPipelineResult) -> tuple[str, ...]:
    facts = (
        f"fixture_or_intake_source={result.fixture_or_intake_source}",
        f"request_type={result.request_type}",
        f"pipeline_stage={result.pipeline_stage}",
        f"route_admission={_route_admission(result)}",
        f"packet_draft_present={result.packet_draft is not None}",
        "dispatch_execution_authority=false",
    )
    if result.packet_draft is not None:
        facts += (
            f"packet_kind={result.packet_draft.packet_kind}",
            f"boundary_name={result.packet_draft.boundary_name}",
        )
    return facts


def _decision_summary(result: FixtureBoundaryPacketPipelineResult) -> str:
    if result.accepted:
        return "Pipeline produced a coordinator-reviewable packet draft; no dispatch or execution is authorized."
    if result.blocked_conditions:
        return "Pipeline is blocked or rejected; coordinator should clarify, reframe, or route a separate boundary."
    return "Pipeline is not accepted; coordinator review is required before any next action."


def _next_boundary(result: FixtureBoundaryPacketPipelineResult) -> str:
    if result.packet_draft is not None:
        return result.packet_draft.next_review_boundary
    if result.blocked_conditions:
        return "clarification_or_reframe_required_before_boundary_packet"
    return "coordinator_review_required"


def build_coordinator_review_report(
    pipeline_result: FixtureBoundaryPacketPipelineResult,
) -> CoordinatorReviewReportResult:
    """Build a deterministic coordinator-facing review report."""

    if not isinstance(pipeline_result, FixtureBoundaryPacketPipelineResult):
        raise TypeError("pipeline_result must be FixtureBoundaryPacketPipelineResult")

    packet_kind = pipeline_result.packet_draft.packet_kind if pipeline_result.packet_draft else "no_packet_draft"
    boundary_name = pipeline_result.packet_draft.boundary_name if pipeline_result.packet_draft else ""
    router_policy = _router_policy_summary(pipeline_result)
    non_proofs = _dedupe(
        REPORT_NON_PROOFS
        + pipeline_result.non_proofs
        + tuple(router_policy["non_proofs"])
        + tuple(router_policy["provider_catalog_non_proofs"])
    )
    caveats = _dedupe(pipeline_result.caveats + ("review_report_draft_only_not_ratification",))
    flags = dict(NO_ACTIVITY_FLAGS)
    for key in flags:
        flags[key] = bool(pipeline_result.no_activity_flags.get(key, False))
    for key, value in router_policy["activity_flags"].items():
        flags[key] = flags.get(key, False) or bool(value)
    for key, value in router_policy["provider_catalog_activity_flags"].items():
        flags[key] = flags.get(key, False) or bool(value)

    report = CoordinatorReviewReport(
        report_id=f"review_{pipeline_result.request_id}",
        source_request_id=pipeline_result.request_id,
        report_kind="coordinator_review_report",
        accepted=pipeline_result.accepted,
        request_type=pipeline_result.request_type,
        pipeline_stage=pipeline_result.pipeline_stage,
        route_admission=_route_admission(pipeline_result),
        packet_kind=packet_kind,
        boundary_name=boundary_name,
        recommended_next_action=pipeline_result.recommended_next_action,
        next_boundary=_next_boundary(pipeline_result),
        decision_summary=_decision_summary(pipeline_result),
        accepted_facts=_accepted_facts(pipeline_result),
        blocked_conditions=pipeline_result.blocked_conditions,
        missing_requirements=pipeline_result.missing_requirements,
        capability_assessment_summary=_capability_summary(pipeline_result),
        router_policy_recommendation=router_policy,
        packet_text=pipeline_result.packet_text,
        evidence_status="deterministic_source_test_report_only_no_runtime_execution",
        non_proofs=non_proofs,
        caveats=caveats,
        no_activity_flags=flags,
    )

    return CoordinatorReviewReportResult(
        accepted=pipeline_result.accepted,
        report=report,
        blocked_conditions=report.blocked_conditions,
        missing_requirements=report.missing_requirements,
        recommended_next_action=report.recommended_next_action,
        non_proofs=report.non_proofs,
        no_activity_flags=dict(report.no_activity_flags),
        caveats=report.caveats,
    )


def render_coordinator_review_text(report: CoordinatorReviewReport) -> str:
    """Render a compact coordinator review artifact draft."""

    lines = [
        "Assessment",
        f"- Review artifact draft only; not coordinator ratification by itself.",
        f"- Accepted: {report.accepted}",
        f"- Request type: {report.request_type}",
        f"- Pipeline stage: {report.pipeline_stage}",
        f"- Route admission: {report.route_admission}",
        f"- Packet kind: {report.packet_kind}",
        "",
        "Accepted Facts",
        *[f"- {item}" for item in report.accepted_facts],
        "",
        "Decision",
        f"- {report.decision_summary}",
        f"- Blocked conditions: {', '.join(report.blocked_conditions) if report.blocked_conditions else 'none'}",
        f"- Missing requirements: {', '.join(report.missing_requirements) if report.missing_requirements else 'none'}",
        "",
        "Router Policy",
        f"- recommended_route={report.router_policy_recommendation['recommended_route']}",
        f"- provider_posture={report.router_policy_recommendation['provider_posture']}",
        f"- provider_catalog_key={report.router_policy_recommendation['provider_catalog_key']}",
        f"- provider_tier={report.router_policy_recommendation['provider_tier']}",
        f"- provider_maturity_status={report.router_policy_recommendation['provider_maturity_status']}",
        f"- provider_allowed_boundary={report.router_policy_recommendation['provider_allowed_boundary']}",
        f"- provider_required_authority={report.router_policy_recommendation['provider_required_authority']}",
        f"- provider_execution_allowed={report.router_policy_recommendation['provider_execution_allowed']}",
        f"- provider_selection_allowed={report.router_policy_recommendation['provider_selection_allowed']}",
        f"- required_boundary={report.router_policy_recommendation['required_boundary']}",
        f"- escalation_posture={report.router_policy_recommendation['escalation_posture']}",
        f"- fallback={report.router_policy_recommendation['fallback']}",
        "- blocked_conditions="
        f"{', '.join(report.router_policy_recommendation['blocked_conditions']) if report.router_policy_recommendation['blocked_conditions'] else 'none'}",
        "- missing_requirements="
        f"{', '.join(report.router_policy_recommendation['missing_requirements']) if report.router_policy_recommendation['missing_requirements'] else 'none'}",
        f"- confidence={report.router_policy_recommendation['confidence']}",
        "",
        "NBM",
        f"- {report.next_boundary}",
        f"- Recommended next action: {report.recommended_next_action}",
        "",
        "Deliverable/Command",
        "- Coordinator review report artifact only.",
        "- Packet text is preserved below when present; it is not dispatch.",
        report.packet_text if report.packet_text else "- No packet draft text produced.",
        "",
        "RESPONSE_METADATA",
        f"- report_id={report.report_id}",
        f"- source_request_id={report.source_request_id}",
        f"- boundary_name={report.boundary_name or 'none'}",
        f"- evidence_status={report.evidence_status}",
        "- coordinator_ratification=false",
        "- worker_execution=false",
        "- dispatch=false",
        "- production_readiness=false",
        "",
        "Non-Proofs",
        *[f"- {item}" for item in report.non_proofs],
        "",
        "Caveats",
        *[f"- {item}" for item in report.caveats],
    ]
    return "\n".join(lines)
