"""Deterministic local-first provider catalog and escalation matrix.

This module is a policy catalog only. It does not import or execute provider
runtime modules, models, workers, RAG, web, schedulers, connectors, platforms,
or production behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


NO_PROVIDER_CATALOG_ACTIVITY_FLAGS = {
    "provider_executed": False,
    "model_executed": False,
    "runtime_executed": False,
    "platform_executed": False,
    "worker_dispatched": False,
    "codex_dispatched": False,
    "rag_lookup_performed": False,
    "web_lookup_performed": False,
    "scheduler_executed": False,
    "connector_executed": False,
    "route_executed": False,
    "production_executed": False,
}

PROVIDER_CATALOG_NON_PROOFS = (
    "provider_catalog_is_not_provider_execution",
    "provider_catalog_is_not_model_execution",
    "provider_catalog_is_not_runtime_execution",
    "provider_catalog_is_not_platform_execution",
    "provider_catalog_is_not_worker_dispatch",
    "provider_catalog_is_not_codex_dispatch",
    "provider_catalog_is_not_rag_lookup",
    "provider_catalog_is_not_web_lookup",
    "provider_catalog_is_not_scheduler_execution",
    "provider_catalog_is_not_connector_execution",
    "provider_catalog_is_not_route_execution",
    "provider_catalog_is_not_production_readiness",
)

REQUIRED_PROVIDER_KEYS = (
    "local_model_candidate",
    "frontier_provider_candidate",
    "worker_codex_boundary",
    "rag_local_document_boundary",
    "scheduler_reminder_boundary",
    "web_research_boundary",
    "provider_blocked_or_unavailable",
)


@dataclass(frozen=True)
class ModelProviderCatalogEntry:
    provider_key: str
    provider_tier: str
    maturity_status: str
    allowed_boundary: str
    execution_allowed: bool
    selection_allowed: bool
    fallback: str
    escalation_posture: str
    required_authority: str
    non_proofs: tuple[str, ...]
    activity_flags: dict[str, bool]
    provider_posture: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _entry(
    *,
    provider_key: str,
    provider_tier: str,
    maturity_status: str,
    allowed_boundary: str,
    fallback: str,
    escalation_posture: str,
    required_authority: str,
    provider_posture: str,
    extra_non_proofs: tuple[str, ...] = (),
) -> ModelProviderCatalogEntry:
    return ModelProviderCatalogEntry(
        provider_key=provider_key,
        provider_tier=provider_tier,
        maturity_status=maturity_status,
        allowed_boundary=allowed_boundary,
        execution_allowed=False,
        selection_allowed=False,
        fallback=fallback,
        escalation_posture=escalation_posture,
        required_authority=required_authority,
        non_proofs=PROVIDER_CATALOG_NON_PROOFS + extra_non_proofs,
        activity_flags=dict(NO_PROVIDER_CATALOG_ACTIVITY_FLAGS),
        provider_posture=provider_posture,
    )


_CATALOG_ENTRIES = (
    _entry(
        provider_key="local_model_candidate",
        provider_tier="local_first_candidate",
        maturity_status="policy_candidate_only",
        allowed_boundary="direct_answer_or_report_only_boundary",
        fallback="ask_clarification_or_escalate_to_frontier_review_if_authorized",
        escalation_posture="frontier_provider_review_only_if_explicitly_authorized",
        required_authority="explicit_future_provider_model_boundary_before_execution",
        provider_posture="local_first_when_authorized_no_provider_executed",
        extra_non_proofs=("local_first_preference_is_not_local_model_execution",),
    ),
    _entry(
        provider_key="frontier_provider_candidate",
        provider_tier="frontier_candidate",
        maturity_status="escalation_candidate_only",
        allowed_boundary="frontier_provider_escalation_boundary",
        fallback="ask_operator_for_explicit_provider_or_platform_boundary",
        escalation_posture="escalate_only_if_separate_boundary_authorizes",
        required_authority="explicit_frontier_provider_escalation_boundary",
        provider_posture="provider_model_runtime_platform_not_selected",
        extra_non_proofs=("frontier_candidate_is_not_frontier_provider_execution",),
    ),
    _entry(
        provider_key="worker_codex_boundary",
        provider_tier="worker_boundary",
        maturity_status="bounded_worker_boundary_required",
        allowed_boundary="bounded_worker_codex_boundary",
        fallback="prepare_human_mediated_worker_packet",
        escalation_posture="worker_boundary_required_before_any_dispatch",
        required_authority="explicit_bounded_worker_codex_boundary",
        provider_posture="provider_model_not_selected_for_direct_execution",
        extra_non_proofs=("worker_boundary_catalog_entry_is_not_worker_dispatch",),
    ),
    _entry(
        provider_key="rag_local_document_boundary",
        provider_tier="retrieval_boundary",
        maturity_status="boundary_required_not_implemented_execution",
        allowed_boundary="rag_local_document_lookup_boundary",
        fallback="ask_operator_for_document_source_authority",
        escalation_posture="defer_to_rag_local_document_boundary",
        required_authority="explicit_rag_local_document_lookup_boundary",
        provider_posture="no_provider_selected",
        extra_non_proofs=("rag_boundary_catalog_entry_is_not_document_lookup",),
    ),
    _entry(
        provider_key="scheduler_reminder_boundary",
        provider_tier="scheduler_boundary",
        maturity_status="boundary_required_not_implemented_execution",
        allowed_boundary="scheduler_reminder_boundary",
        fallback="ask_operator_for_time_target_and_persistence_confirmation",
        escalation_posture="defer_to_scheduler_reminder_boundary",
        required_authority="explicit_scheduler_reminder_boundary",
        provider_posture="no_provider_selected",
        extra_non_proofs=("scheduler_boundary_catalog_entry_is_not_scheduling",),
    ),
    _entry(
        provider_key="web_research_boundary",
        provider_tier="web_research_boundary",
        maturity_status="boundary_required_not_implemented_execution",
        allowed_boundary="web_research_boundary",
        fallback="ask_operator_for_web_research_authority",
        escalation_posture="defer_to_web_research_boundary",
        required_authority="explicit_web_research_boundary",
        provider_posture="no_provider_selected",
        extra_non_proofs=("web_boundary_catalog_entry_is_not_web_lookup",),
    ),
    _entry(
        provider_key="provider_blocked_or_unavailable",
        provider_tier="blocked",
        maturity_status="blocked_or_unavailable",
        allowed_boundary="operator_clarification_or_explicit_future_boundary",
        fallback="reject_or_reframe_without_provider_model_runtime_execution",
        escalation_posture="blocked_until_explicit_boundary_and_fresh_proof",
        required_authority="explicit_future_provider_model_runtime_platform_boundary",
        provider_posture="no_provider_selected",
        extra_non_proofs=("blocked_provider_catalog_entry_is_not_availability_proof",),
    ),
)

MODEL_PROVIDER_CATALOG = {entry.provider_key: entry for entry in _CATALOG_ENTRIES}

ROUTE_TO_PROVIDER_KEY = {
    "local_first_answer": "local_model_candidate",
    "separate_provider_or_platform_boundary_required": "frontier_provider_candidate",
    "worker_codex_boundary": "worker_codex_boundary",
    "rag_local_document_boundary": "rag_local_document_boundary",
    "scheduler_reminder_boundary": "scheduler_reminder_boundary",
    "web_research_boundary": "web_research_boundary",
    "block": "provider_blocked_or_unavailable",
    "ask_clarification": "provider_blocked_or_unavailable",
}


def get_model_provider_catalog() -> dict[str, ModelProviderCatalogEntry]:
    """Return a deterministic catalog keyed by provider policy key."""

    return dict(MODEL_PROVIDER_CATALOG)


def get_model_provider_catalog_entry(provider_key: str) -> ModelProviderCatalogEntry:
    """Return one catalog entry, falling back to the blocked posture."""

    return MODEL_PROVIDER_CATALOG.get(provider_key, MODEL_PROVIDER_CATALOG["provider_blocked_or_unavailable"])


def provider_posture_for_route(recommended_route: str) -> str:
    """Return the non-executing provider posture string for a route."""

    provider_key = ROUTE_TO_PROVIDER_KEY.get(recommended_route, "provider_blocked_or_unavailable")
    return get_model_provider_catalog_entry(provider_key).provider_posture
