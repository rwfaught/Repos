"""Deterministic route-selection readiness contract.

This module consumes router recommendation envelope data and reports what
proof remains missing before provider/model route selection or execution could
be authorized. It does not execute providers, models, workers, routes,
runtime surfaces, network calls, lookups, schedulers, connectors, or
production behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from orchestrator.model_router_policy import ModelRouterPolicyRecommendation, recommend_model_route


GENERATION_SMOKE_EVIDENCE_KEY = "phase_159_retry1_qwen36_27b_generate_marker_smoke"


NO_READINESS_ACTIVITY_FLAGS = {
    "provider_selected": False,
    "provider_executed": False,
    "model_selected": False,
    "model_executed": False,
    "generation_performed": False,
    "api_generate_called": False,
    "api_chat_called": False,
    "runtime_executed": False,
    "platform_executed": False,
    "route_executed": False,
    "worker_dispatched": False,
    "codex_dispatched": False,
    "rag_lookup_performed": False,
    "web_lookup_performed": False,
    "scheduler_executed": False,
    "connector_executed": False,
    "production_executed": False,
}

READINESS_NON_PROOFS = (
    "readiness_contract_is_not_provider_execution",
    "readiness_contract_is_not_model_execution",
    "readiness_contract_is_not_generation",
    "readiness_contract_is_not_api_generate",
    "readiness_contract_is_not_api_chat",
    "readiness_contract_is_not_route_execution",
    "readiness_contract_is_not_worker_dispatch",
    "readiness_contract_is_not_production_readiness",
)


@dataclass(frozen=True)
class RouteSelectionReadinessResult:
    request_id: str
    provider_catalog_key: str
    recommended_route: str
    provider_evidence_status: str
    provider_evidence_keys: tuple[str, ...]
    provider_evidence_source_phases: tuple[str, ...]
    route_selection_readiness: str
    readiness_status: str
    blocked_conditions: tuple[str, ...]
    next_required_boundary: str
    next_required_proof: str
    provider_selection_allowed: bool
    provider_execution_allowed: bool
    route_execution_allowed: bool
    generation_allowed: bool
    production_readiness: bool
    non_proofs: tuple[str, ...]
    activity_flags: dict[str, bool]


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _coerce_recommendation(value: Any) -> ModelRouterPolicyRecommendation:
    if isinstance(value, ModelRouterPolicyRecommendation):
        return value
    if isinstance(value, dict) and "recommended_route" in value and "provider_catalog_key" in value:
        return _recommendation_from_dict(value)
    return recommend_model_route(value)


def _recommendation_from_dict(value: dict[str, Any]) -> ModelRouterPolicyRecommendation:
    return ModelRouterPolicyRecommendation(
        request_id=str(value.get("request_id", "")),
        recommended_route=str(value.get("recommended_route", "")),
        provider_posture=str(value.get("provider_posture", "")),
        provider_catalog_key=str(value.get("provider_catalog_key", "")),
        provider_tier=str(value.get("provider_tier", "")),
        provider_maturity_status=str(value.get("provider_maturity_status", "")),
        provider_allowed_boundary=str(value.get("provider_allowed_boundary", "")),
        provider_required_authority=str(value.get("provider_required_authority", "")),
        provider_execution_allowed=value.get("provider_execution_allowed") is True,
        provider_selection_allowed=value.get("provider_selection_allowed") is True,
        provider_catalog_escalation_posture=str(value.get("provider_catalog_escalation_posture", "")),
        provider_catalog_fallback=str(value.get("provider_catalog_fallback", "")),
        provider_catalog_non_proofs=tuple(value.get("provider_catalog_non_proofs", ())),
        provider_catalog_activity_flags=dict(value.get("provider_catalog_activity_flags", {})),
        provider_evidence_status=str(value.get("provider_evidence_status", "")),
        provider_evidence_keys=tuple(value.get("provider_evidence_keys", ())),
        provider_evidence_source_phases=tuple(value.get("provider_evidence_source_phases", ())),
        provider_evidence_summary=str(value.get("provider_evidence_summary", "")),
        model_metadata_evidence_name=str(value.get("model_metadata_evidence_name", "")),
        model_metadata_format=str(value.get("model_metadata_format", "")),
        model_metadata_family=str(value.get("model_metadata_family", "")),
        model_metadata_parameter_size=str(value.get("model_metadata_parameter_size", "")),
        model_metadata_quantization_level=str(value.get("model_metadata_quantization_level", "")),
        provider_evidence_non_proofs=tuple(value.get("provider_evidence_non_proofs", ())),
        provider_evidence_activity_flags=dict(value.get("provider_evidence_activity_flags", {})),
        confidence=value.get("confidence") if isinstance(value.get("confidence"), (int, float)) else None,
        reason=str(value.get("reason", "")),
        fallback=str(value.get("fallback", "")),
        escalation_posture=str(value.get("escalation_posture", "")),
        required_boundary=str(value.get("required_boundary", "")),
        blocked_conditions=tuple(value.get("blocked_conditions", ())),
        missing_requirements=tuple(value.get("missing_requirements", ())),
        non_proofs=tuple(value.get("non_proofs", ())),
        activity_flags=dict(value.get("activity_flags", {})),
    )


def evaluate_route_selection_readiness(request_or_recommendation: Any) -> RouteSelectionReadinessResult:
    """Evaluate route-selection readiness without selecting or executing anything."""

    recommendation = _coerce_recommendation(request_or_recommendation)
    generation_smoke_satisfied = GENERATION_SMOKE_EVIDENCE_KEY in recommendation.provider_evidence_keys
    if generation_smoke_satisfied:
        route_selection_readiness = "blocked_pending_qwen36_27b_metadata_proof"
        blocked_conditions = _dedupe(
            tuple(recommendation.blocked_conditions)
            + tuple(recommendation.missing_requirements)
            + ("qwen36_27b_api_show_metadata_proof_missing",)
        )
        next_required_boundary = "future_qwen36_27b_api_show_metadata_proof_boundary"
        next_required_proof = "bounded_qwen36_27b_api_show_metadata_operator_proof"
    else:
        route_selection_readiness = "blocked_pending_generation_probe_boundary"
        blocked_conditions = _dedupe(
            tuple(recommendation.blocked_conditions)
            + tuple(recommendation.missing_requirements)
            + ("generation_smoke_probe_boundary_not_authorized",)
        )
        next_required_boundary = "future_local_provider_generation_smoke_probe_boundary"
        next_required_proof = "bounded_generation_smoke_probe_operator_proof"

    return RouteSelectionReadinessResult(
        request_id=recommendation.request_id,
        provider_catalog_key=recommendation.provider_catalog_key,
        recommended_route=recommendation.recommended_route,
        provider_evidence_status=recommendation.provider_evidence_status,
        provider_evidence_keys=tuple(recommendation.provider_evidence_keys),
        provider_evidence_source_phases=tuple(recommendation.provider_evidence_source_phases),
        route_selection_readiness=route_selection_readiness,
        readiness_status="not_ready_for_execution",
        blocked_conditions=blocked_conditions,
        next_required_boundary=next_required_boundary,
        next_required_proof=next_required_proof,
        provider_selection_allowed=False,
        provider_execution_allowed=False,
        route_execution_allowed=False,
        generation_allowed=False,
        production_readiness=False,
        non_proofs=_dedupe(READINESS_NON_PROOFS + tuple(recommendation.provider_evidence_non_proofs)),
        activity_flags=dict(NO_READINESS_ACTIVITY_FLAGS),
    )


def route_selection_readiness_to_dict(result: RouteSelectionReadinessResult) -> dict[str, Any]:
    """Return a serializable readiness dictionary."""

    payload = asdict(result)
    payload["provider_evidence_keys"] = list(result.provider_evidence_keys)
    payload["provider_evidence_source_phases"] = list(result.provider_evidence_source_phases)
    payload["blocked_conditions"] = list(result.blocked_conditions)
    payload["non_proofs"] = list(result.non_proofs)
    payload["activity_flags"] = dict(result.activity_flags)
    return payload


def summarize_route_selection_readiness(result: RouteSelectionReadinessResult) -> str:
    """Render a compact readiness summary without execution claims."""

    return (
        f"{result.readiness_status}: {result.route_selection_readiness}; "
        f"next_required_boundary={result.next_required_boundary}; "
        f"next_required_proof={result.next_required_proof}"
    )
