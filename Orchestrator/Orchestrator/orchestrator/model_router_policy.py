"""Deterministic local-first model/router policy contract.

This module recommends boundary posture only. It does not execute providers,
models, workers, runtime surfaces, RAG/local lookup, web lookup, scheduler
behavior, connectors, or production work.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.capability_registry import assess_required_capabilities
from orchestrator.model_provider_catalog import ROUTE_TO_PROVIDER_KEY, get_model_provider_catalog_entry


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
    "rag_lookup_performed": False,
    "web_lookup_performed": False,
    "scheduler_executed": False,
    "connector_executed": False,
    "worker_dispatched": False,
    "codex_dispatched": False,
    "export_performed": False,
    "package_performed": False,
    "cleanup_performed": False,
    "deletion_performed": False,
    "archive_performed": False,
}

ROUTER_POLICY_NON_PROOFS = (
    "router_policy_is_not_provider_execution",
    "router_policy_is_not_model_execution",
    "router_policy_is_not_live_router",
    "router_policy_is_not_worker_dispatch",
    "router_policy_is_not_codex_dispatch",
    "router_policy_is_not_route_execution",
    "router_policy_is_not_rag_lookup",
    "router_policy_is_not_web_lookup",
    "router_policy_is_not_scheduler_execution",
    "router_policy_is_not_connector_execution",
    "router_policy_is_not_platform_execution",
    "router_policy_is_not_file_mutation",
    "router_policy_is_not_production_readiness",
)

PROVIDER_OR_PLATFORM_CAPABILITIES = {
    "provider_model",
    "platform_runtime",
}

PRODUCTION_CAPABILITIES = {
    "production_execution",
}

LOCAL_DOCUMENT_CAPABILITIES = {
    "local_document_lookup",
}

REMINDER_CAPABILITIES = {
    "scheduling_contract",
}

WEB_CAPABILITIES = {
    "web_research",
}

CODING_CAPABILITIES = {
    "coding_task",
    "source_inspection",
    "patch_proposal",
    "bounded_file_write",
    "filesystem_mutation_authority",
}


@dataclass(frozen=True)
class ModelRouterPolicyRequest:
    request_id: str
    request_type: str
    confidence: float | None
    required_capabilities: tuple[str, ...]
    missing_inputs: tuple[str, ...] = ()
    risk_level: str = "low"
    allowed_to_answer_directly: bool = False
    allowed_to_mutate_files: bool = False
    allowed_to_schedule: bool = False
    allowed_to_use_local_documents: bool = False
    allowed_to_use_web: bool = False
    requires_operator_confirmation: bool = False
    requires_external_connector: bool = False


@dataclass(frozen=True)
class ModelRouterPolicyRecommendation:
    request_id: str
    recommended_route: str
    provider_posture: str
    provider_catalog_key: str
    provider_tier: str
    provider_maturity_status: str
    provider_allowed_boundary: str
    provider_required_authority: str
    provider_execution_allowed: bool
    provider_selection_allowed: bool
    provider_catalog_escalation_posture: str
    provider_catalog_fallback: str
    provider_catalog_non_proofs: tuple[str, ...]
    provider_catalog_activity_flags: dict[str, bool]
    confidence: float | None
    reason: str
    fallback: str
    escalation_posture: str
    required_boundary: str
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    non_proofs: tuple[str, ...]
    activity_flags: dict[str, bool]


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _tuple_of_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(text for text in (_normalize_text(item) for item in value) if text)


def _coerce_request(value: ModelRouterPolicyRequest | dict[str, Any]) -> ModelRouterPolicyRequest | None:
    if isinstance(value, ModelRouterPolicyRequest):
        return value
    if not isinstance(value, dict):
        return None

    confidence = value.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        normalized_confidence = None
    else:
        normalized_confidence = float(confidence)

    return ModelRouterPolicyRequest(
        request_id=_normalize_text(value.get("request_id")),
        request_type=_normalize_text(value.get("request_type")),
        confidence=normalized_confidence,
        required_capabilities=_tuple_of_text(value.get("required_capabilities")),
        missing_inputs=_tuple_of_text(value.get("missing_inputs", ())),
        risk_level=_normalize_text(value.get("risk_level", "low")).lower() or "low",
        allowed_to_answer_directly=value.get("allowed_to_answer_directly") is True,
        allowed_to_mutate_files=value.get("allowed_to_mutate_files") is True,
        allowed_to_schedule=value.get("allowed_to_schedule") is True,
        allowed_to_use_local_documents=value.get("allowed_to_use_local_documents") is True,
        allowed_to_use_web=value.get("allowed_to_use_web") is True,
        requires_operator_confirmation=value.get("requires_operator_confirmation") is True,
        requires_external_connector=value.get("requires_external_connector") is True,
    )


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _recommendation(
    request: ModelRouterPolicyRequest,
    *,
    recommended_route: str,
    provider_posture: str,
    reason: str,
    fallback: str,
    escalation_posture: str,
    required_boundary: str,
    blocked_conditions: tuple[str, ...] = (),
    missing_requirements: tuple[str, ...] = (),
    capability_non_proofs: tuple[str, ...] = (),
) -> ModelRouterPolicyRecommendation:
    provider_catalog_key = ROUTE_TO_PROVIDER_KEY.get(recommended_route, "provider_blocked_or_unavailable")
    provider_catalog_entry = get_model_provider_catalog_entry(provider_catalog_key)
    return ModelRouterPolicyRecommendation(
        request_id=request.request_id,
        recommended_route=recommended_route,
        provider_posture=provider_catalog_entry.provider_posture,
        provider_catalog_key=provider_catalog_entry.provider_key,
        provider_tier=provider_catalog_entry.provider_tier,
        provider_maturity_status=provider_catalog_entry.maturity_status,
        provider_allowed_boundary=provider_catalog_entry.allowed_boundary,
        provider_required_authority=provider_catalog_entry.required_authority,
        provider_execution_allowed=provider_catalog_entry.execution_allowed,
        provider_selection_allowed=provider_catalog_entry.selection_allowed,
        provider_catalog_escalation_posture=provider_catalog_entry.escalation_posture,
        provider_catalog_fallback=provider_catalog_entry.fallback,
        provider_catalog_non_proofs=provider_catalog_entry.non_proofs,
        provider_catalog_activity_flags=dict(provider_catalog_entry.activity_flags),
        confidence=request.confidence,
        reason=reason,
        fallback=fallback,
        escalation_posture=escalation_posture,
        required_boundary=required_boundary,
        blocked_conditions=_dedupe(blocked_conditions),
        missing_requirements=_dedupe(missing_requirements),
        non_proofs=_dedupe(ROUTER_POLICY_NON_PROOFS + provider_catalog_entry.non_proofs + capability_non_proofs),
        activity_flags=dict(NO_ACTIVITY_FLAGS),
    )


def recommend_model_route(
    route_request: ModelRouterPolicyRequest | dict[str, Any],
) -> ModelRouterPolicyRecommendation:
    """Recommend local-first/provider escalation posture without execution."""

    request = _coerce_request(route_request)
    if request is None:
        empty_request = ModelRouterPolicyRequest("", "needs_clarification", None, ())
        return _recommendation(
            empty_request,
            recommended_route="ask_clarification",
            provider_posture="",
            reason="Structured model router policy request is required.",
            fallback="ask_operator_for_structured_router_policy_fields",
            escalation_posture="clarification_required",
            required_boundary="operator_clarification_boundary",
            missing_requirements=("structured_router_policy_request",),
        )

    missing_requirements: list[str] = []
    blocked_conditions: list[str] = []

    if not request.request_id:
        missing_requirements.append("request_id")
    if not request.request_type:
        missing_requirements.append("request_type")
    if request.confidence is None:
        missing_requirements.append("confidence")
    elif not 0.0 <= request.confidence <= 1.0:
        blocked_conditions.append("confidence_out_of_range")
    if not request.required_capabilities:
        missing_requirements.append("required_capabilities")

    capability_assessment = assess_required_capabilities(list(request.required_capabilities))
    capability_non_proofs = tuple(capability_assessment.get("non_proofs", ()))
    capabilities = set(request.required_capabilities)

    if capability_assessment.get("unknown_capabilities"):
        blocked_conditions.append("unknown_capability_authority")

    if missing_requirements or blocked_conditions:
        return _recommendation(
            request,
            recommended_route="ask_clarification",
            provider_posture="",
            reason="Missing or invalid router policy authority prevents recommendation.",
            fallback="ask_operator_for_request_type_confidence_and_capability_authority",
            escalation_posture="clarification_required",
            required_boundary="operator_clarification_boundary",
            blocked_conditions=tuple(blocked_conditions),
            missing_requirements=tuple(missing_requirements),
            capability_non_proofs=capability_non_proofs,
        )

    if capabilities & PRODUCTION_CAPABILITIES:
        return _recommendation(
            request,
            recommended_route="block",
            provider_posture="",
            reason="Production execution capability requires a separate future production boundary.",
            fallback="reject_or_reframe_without_production_execution",
            escalation_posture="blocked_requires_explicit_production_boundary",
            required_boundary="explicit_production_execution_boundary",
            blocked_conditions=("production_execution_blocked",),
            capability_non_proofs=capability_non_proofs,
        )

    if capabilities & PROVIDER_OR_PLATFORM_CAPABILITIES:
        return _recommendation(
            request,
            recommended_route="separate_provider_or_platform_boundary_required",
            provider_posture="",
            reason="Provider/model/platform/runtime capabilities require separate authority.",
            fallback="ask_operator_for_explicit_provider_or_platform_boundary",
            escalation_posture="escalate_only_if_separate_boundary_authorizes",
            required_boundary="provider_model_or_platform_runtime_boundary",
            blocked_conditions=("provider_model_or_platform_runtime_boundary_required",),
            capability_non_proofs=capability_non_proofs,
        )

    if request.request_type == "local_document_lookup" or capabilities & LOCAL_DOCUMENT_CAPABILITIES:
        return _recommendation(
            request,
            recommended_route="rag_local_document_boundary",
            provider_posture="",
            reason="Local document lookup requires a RAG/local-document lookup boundary.",
            fallback="ask_operator_for_document_source_authority",
            escalation_posture="defer_to_rag_local_document_boundary",
            required_boundary="rag_local_document_lookup_boundary",
            blocked_conditions=("rag_lookup_not_executed",),
            capability_non_proofs=capability_non_proofs,
        )

    if request.request_type == "reminder_request" or capabilities & REMINDER_CAPABILITIES:
        return _recommendation(
            request,
            recommended_route="scheduler_reminder_boundary",
            provider_posture="",
            reason="Reminder requests require scheduler/reminder confirmation and boundary.",
            fallback="ask_operator_for_time_target_and_persistence_confirmation",
            escalation_posture="defer_to_scheduler_reminder_boundary",
            required_boundary="scheduler_reminder_boundary",
            blocked_conditions=("scheduler_not_executed",),
            capability_non_proofs=capability_non_proofs,
        )

    if request.request_type == "research_request" or capabilities & WEB_CAPABILITIES or request.allowed_to_use_web:
        return _recommendation(
            request,
            recommended_route="web_research_boundary",
            provider_posture="",
            reason="Research/web requests require an explicit web/research boundary.",
            fallback="ask_operator_for_web_research_authority",
            escalation_posture="defer_to_web_research_boundary",
            required_boundary="web_research_boundary",
            blocked_conditions=("web_lookup_not_executed",),
            capability_non_proofs=capability_non_proofs,
        )

    if request.request_type in {"coding_task", "file_operation"} or capabilities & CODING_CAPABILITIES:
        return _recommendation(
            request,
            recommended_route="worker_codex_boundary",
            provider_posture="",
            reason="Coding and file mutation routes require a bounded worker/Codex boundary.",
            fallback="prepare_human_mediated_worker_packet",
            escalation_posture="worker_boundary_required_before_any_dispatch",
            required_boundary="bounded_worker_codex_boundary",
            blocked_conditions=("worker_dispatch_not_executed",),
            capability_non_proofs=capability_non_proofs,
        )

    if (
        request.request_type in {"general_answer", "planning_request", "creative_generation"}
        and request.allowed_to_answer_directly
        and not request.missing_inputs
        and request.risk_level not in {"high", "critical"}
    ):
        return _recommendation(
            request,
            recommended_route="local_first_answer",
            provider_posture="",
            reason="Low-risk answer route may stay local-first when direct answer is allowed.",
            fallback="ask_clarification_or_escalate_to_frontier_review_if_authorized",
            escalation_posture="frontier_provider_review_only_if_explicitly_authorized",
            required_boundary="direct_answer_or_report_only_boundary",
            capability_non_proofs=capability_non_proofs,
        )

    return _recommendation(
        request,
        recommended_route="ask_clarification",
        provider_posture="",
        reason="Router policy cannot safely recommend a downstream posture from current fields.",
        fallback="ask_operator_for_missing_inputs_or_boundary_authority",
        escalation_posture="clarification_required",
        required_boundary="operator_clarification_boundary",
        missing_requirements=("route_authority_or_permission_alignment",),
        capability_non_proofs=capability_non_proofs,
    )
