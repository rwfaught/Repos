"""Provider/runtime probe boundary packet draft contract.

This module drafts future-boundary paperwork only. It does not import or
execute provider runtimes, probes, models, workers, RAG, web, schedulers,
connectors, platforms, or production behavior.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from orchestrator.model_provider_catalog import get_model_provider_catalog_entry
from orchestrator.model_router_policy import ModelRouterPolicyRecommendation


NO_PROBE_ACTIVITY_FLAGS = {
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

PROBE_PACKET_NON_PROOFS = (
    "probe_packet_is_not_provider_execution",
    "probe_packet_is_not_model_execution",
    "probe_packet_is_not_provider_availability_proof",
    "probe_packet_is_not_model_availability_proof",
    "probe_packet_is_not_runtime_execution",
    "probe_packet_is_not_platform_execution",
    "probe_packet_is_not_worker_dispatch",
    "probe_packet_is_not_codex_dispatch",
    "probe_packet_is_not_route_execution",
    "probe_packet_is_not_rag_lookup",
    "probe_packet_is_not_web_lookup",
    "probe_packet_is_not_scheduler_execution",
    "probe_packet_is_not_connector_execution",
    "probe_packet_is_not_production_readiness",
)

EXPLICIT_EXCLUSIONS = (
    "No provider/model execution.",
    "No provider or model availability probe.",
    "No provider runtime import.",
    "No concrete model selection for execution.",
    "No runtime/platform execution.",
    "No worker/Codex dispatch.",
    "No RAG/local-document lookup.",
    "No web lookup.",
    "No scheduler/reminder execution.",
    "No connector execution.",
    "No route execution.",
    "No production execution or production readiness claim.",
)

PROBE_BOUNDARY_BY_PROVIDER_KEY = {
    "local_model_candidate": "future_local_provider_model_probe_boundary",
    "frontier_provider_candidate": "future_frontier_provider_escalation_probe_boundary",
    "worker_codex_boundary": "future_bounded_worker_codex_probe_boundary",
    "rag_local_document_boundary": "future_rag_local_document_probe_boundary",
    "scheduler_reminder_boundary": "future_scheduler_reminder_probe_boundary",
    "web_research_boundary": "future_web_research_probe_boundary",
}

ALLOWED_OPERATIONS_BY_PROVIDER_KEY = {
    "local_model_candidate": (
        "draft_future_local_provider_model_probe_scope",
        "declare_expected_provider_and_model_availability_evidence",
        "preserve_coordinator_acceptance_gate",
    ),
    "frontier_provider_candidate": (
        "draft_future_frontier_provider_escalation_probe_scope",
        "declare_expected_frontier_provider_authority_evidence",
        "preserve_coordinator_acceptance_gate",
    ),
    "worker_codex_boundary": (
        "draft_future_worker_codex_boundary_probe_scope",
        "declare_expected_worker_boundary_evidence",
        "preserve_no_dispatch_gate",
    ),
    "rag_local_document_boundary": (
        "draft_future_rag_local_document_probe_scope",
        "declare_expected_retrieval_boundary_evidence",
        "preserve_no_lookup_gate",
    ),
    "scheduler_reminder_boundary": (
        "draft_future_scheduler_reminder_probe_scope",
        "declare_expected_scheduler_boundary_evidence",
        "preserve_no_scheduler_execution_gate",
    ),
    "web_research_boundary": (
        "draft_future_web_research_probe_scope",
        "declare_expected_web_research_boundary_evidence",
        "preserve_no_web_lookup_gate",
    ),
}


@dataclass(frozen=True)
class ProviderProbeBoundaryPacketRequest:
    request_id: str
    source_router_recommendation: ModelRouterPolicyRecommendation | dict[str, Any] | None
    requested_probe_kind: str
    requested_surface: str
    operator_authorized_probe_boundary: bool
    allowed_probe_scope: tuple[str, ...]
    expected_evidence: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    caveats: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderProbeBoundaryPacketDraft:
    packet_id: str
    source_request_id: str
    packet_kind: str
    provider_catalog_key: str
    provider_tier: str
    provider_allowed_boundary: str
    requested_probe_kind: str
    requested_surface: str
    purpose: str
    allowed_operations: tuple[str, ...]
    explicit_exclusions: tuple[str, ...]
    validation_expectations: tuple[str, ...]
    expected_evidence: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    non_proofs: tuple[str, ...]
    activity_flags: dict[str, bool]
    caveats: tuple[str, ...]
    coordinator_acceptance_required: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderProbeBoundaryPacketResult:
    accepted: bool
    packet_draft: ProviderProbeBoundaryPacketDraft | None
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    recommended_next_action: str
    non_proofs: tuple[str, ...]
    activity_flags: dict[str, bool]
    caveats: tuple[str, ...]


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _tuple_of_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(text for text in (str(item).strip() for item in value) if text)


def _coerce_request(value: ProviderProbeBoundaryPacketRequest | dict[str, Any]) -> ProviderProbeBoundaryPacketRequest:
    if isinstance(value, ProviderProbeBoundaryPacketRequest):
        return value
    if not isinstance(value, dict):
        raise TypeError("request must be ProviderProbeBoundaryPacketRequest or dict")
    return ProviderProbeBoundaryPacketRequest(
        request_id=str(value.get("request_id", "")).strip(),
        source_router_recommendation=value.get("source_router_recommendation"),
        requested_probe_kind=str(value.get("requested_probe_kind", "")).strip(),
        requested_surface=str(value.get("requested_surface", "")).strip(),
        operator_authorized_probe_boundary=value.get("operator_authorized_probe_boundary") is True,
        allowed_probe_scope=_tuple_of_text(value.get("allowed_probe_scope")),
        expected_evidence=_tuple_of_text(value.get("expected_evidence")),
        stop_conditions=_tuple_of_text(value.get("stop_conditions")),
        caveats=_tuple_of_text(value.get("caveats")),
    )


def _router_recommendation_dict(
    source: ModelRouterPolicyRecommendation | dict[str, Any] | None,
) -> dict[str, Any] | None:
    if isinstance(source, ModelRouterPolicyRecommendation):
        return asdict(source)
    if isinstance(source, dict):
        return deepcopy(source)
    return None


def _blocked_result(
    *,
    blocked_conditions: tuple[str, ...],
    missing_requirements: tuple[str, ...] = (),
    recommended_next_action: str,
    non_proofs: tuple[str, ...] = (),
    caveats: tuple[str, ...] = (),
) -> ProviderProbeBoundaryPacketResult:
    return ProviderProbeBoundaryPacketResult(
        accepted=False,
        packet_draft=None,
        blocked_conditions=_dedupe(blocked_conditions),
        missing_requirements=_dedupe(missing_requirements),
        recommended_next_action=recommended_next_action,
        non_proofs=_dedupe(PROBE_PACKET_NON_PROOFS + non_proofs),
        activity_flags=dict(NO_PROBE_ACTIVITY_FLAGS),
        caveats=_dedupe(caveats),
    )


def _purpose(provider_catalog_key: str, requested_probe_kind: str, requested_surface: str) -> str:
    return (
        "Draft future-boundary paperwork for "
        f"{provider_catalog_key} probe posture over {requested_surface or 'unspecified surface'} "
        f"as {requested_probe_kind or 'unspecified probe kind'}; no probe is executed."
    )


def build_provider_probe_boundary_packet(
    request: ProviderProbeBoundaryPacketRequest | dict[str, Any],
) -> ProviderProbeBoundaryPacketResult:
    """Draft a future provider/runtime probe boundary packet without probing."""

    packet_request = _coerce_request(request)
    recommendation = _router_recommendation_dict(packet_request.source_router_recommendation)
    if recommendation is None:
        return _blocked_result(
            blocked_conditions=("missing_structured_router_recommendation",),
            missing_requirements=("source_router_recommendation",),
            recommended_next_action="provide_structured_router_recommendation_before_probe_packet",
            caveats=packet_request.caveats,
        )

    missing_requirements: list[str] = []
    if not packet_request.request_id:
        missing_requirements.append("request_id")
    if not packet_request.requested_probe_kind:
        missing_requirements.append("requested_probe_kind")
    if not packet_request.requested_surface:
        missing_requirements.append("requested_surface")
    if not packet_request.allowed_probe_scope:
        missing_requirements.append("allowed_probe_scope")
    if not packet_request.expected_evidence:
        missing_requirements.append("expected_evidence")
    if not packet_request.operator_authorized_probe_boundary:
        missing_requirements.append("operator_authorized_probe_boundary")
    if missing_requirements:
        return _blocked_result(
            blocked_conditions=("probe_packet_missing_required_authority_or_scope",),
            missing_requirements=tuple(missing_requirements),
            recommended_next_action="collect_probe_boundary_authority_scope_and_evidence_before_packet",
            non_proofs=tuple(recommendation.get("non_proofs", ())),
            caveats=packet_request.caveats,
        )

    recommended_route = str(recommendation.get("recommended_route", "")).strip()
    provider_catalog_key = str(recommendation.get("provider_catalog_key", "")).strip()
    if recommended_route in {"block", "ask_clarification"}:
        return _blocked_result(
            blocked_conditions=("router_recommendation_not_probe_eligible",),
            missing_requirements=("non_blocked_non_clarification_router_recommendation",),
            recommended_next_action="resolve_block_or_clarification_before_probe_packet",
            non_proofs=tuple(recommendation.get("non_proofs", ())),
            caveats=packet_request.caveats,
        )
    if provider_catalog_key == "provider_blocked_or_unavailable":
        return _blocked_result(
            blocked_conditions=("provider_blocked_or_unavailable_not_probe_eligible",),
            recommended_next_action="obtain_unblocked_provider_catalog_posture_before_probe_packet",
            non_proofs=tuple(recommendation.get("non_proofs", ())),
            caveats=packet_request.caveats,
        )
    if provider_catalog_key not in PROBE_BOUNDARY_BY_PROVIDER_KEY:
        return _blocked_result(
            blocked_conditions=("unsupported_provider_catalog_key_for_probe_packet",),
            missing_requirements=("supported_provider_catalog_key",),
            recommended_next_action="route_supported_catalog_posture_before_probe_packet",
            non_proofs=tuple(recommendation.get("non_proofs", ())),
            caveats=packet_request.caveats,
        )

    catalog_entry = get_model_provider_catalog_entry(provider_catalog_key)
    provider_boundary = PROBE_BOUNDARY_BY_PROVIDER_KEY[provider_catalog_key]
    catalog_non_proofs = tuple(recommendation.get("provider_catalog_non_proofs", ())) or catalog_entry.non_proofs
    catalog_activity_flags = dict(recommendation.get("provider_catalog_activity_flags", {})) or dict(
        catalog_entry.activity_flags
    )
    if any(bool(value) for value in catalog_activity_flags.values()):
        return _blocked_result(
            blocked_conditions=("source_router_recommendation_claims_probe_or_execution_activity",),
            recommended_next_action="repair_router_recommendation_activity_flags_before_probe_packet",
            non_proofs=tuple(recommendation.get("non_proofs", ())) + catalog_non_proofs,
            caveats=packet_request.caveats,
        )

    packet = ProviderProbeBoundaryPacketDraft(
        packet_id=f"probe_packet_{packet_request.request_id}",
        source_request_id=packet_request.request_id,
        packet_kind="provider_runtime_probe_boundary_packet_draft",
        provider_catalog_key=provider_catalog_key,
        provider_tier=str(recommendation.get("provider_tier", catalog_entry.provider_tier)),
        provider_allowed_boundary=provider_boundary,
        requested_probe_kind=packet_request.requested_probe_kind,
        requested_surface=packet_request.requested_surface,
        purpose=_purpose(provider_catalog_key, packet_request.requested_probe_kind, packet_request.requested_surface),
        allowed_operations=ALLOWED_OPERATIONS_BY_PROVIDER_KEY[provider_catalog_key],
        explicit_exclusions=EXPLICIT_EXCLUSIONS,
        validation_expectations=(
            "future_boundary_must_define_read_only_probe_commands_before_execution",
            "future_boundary_must_capture_provider_or_runtime_output_as_evidence",
            "future_boundary_must_stop_on_any_unapproved_execution_or_import_request",
            "coordinator_must_review_probe_evidence_before_acceptance",
        ),
        expected_evidence=packet_request.expected_evidence,
        stop_conditions=_dedupe(
            packet_request.stop_conditions
            + (
                "missing_future_probe_boundary",
                "provider_runtime_import_requested_without_boundary",
                "provider_or_model_execution_requested_without_boundary",
                "unexpected_true_activity_flag",
            )
        ),
        non_proofs=_dedupe(PROBE_PACKET_NON_PROOFS + tuple(recommendation.get("non_proofs", ())) + catalog_non_proofs),
        activity_flags=dict(NO_PROBE_ACTIVITY_FLAGS),
        caveats=_dedupe(
            packet_request.caveats
            + (
                "packet_is_future_boundary_paperwork_only",
                "coordinator_acceptance_required_before_any_probe",
            )
        ),
        coordinator_acceptance_required=True,
    )

    return ProviderProbeBoundaryPacketResult(
        accepted=True,
        packet_draft=packet,
        blocked_conditions=(),
        missing_requirements=(),
        recommended_next_action="coordinator_review_probe_packet_before_any_runtime_boundary",
        non_proofs=packet.non_proofs,
        activity_flags=dict(packet.activity_flags),
        caveats=packet.caveats,
    )


def render_provider_probe_boundary_packet_text(packet: ProviderProbeBoundaryPacketDraft) -> str:
    """Render compact reviewable future-boundary probe packet text."""

    lines = [
        "Boundary",
        f"- packet_id={packet.packet_id}",
        f"- packet_kind={packet.packet_kind}",
        f"- source_request_id={packet.source_request_id}",
        f"- coordinator_acceptance_required={packet.coordinator_acceptance_required}",
        "",
        "Purpose",
        f"- {packet.purpose}",
        "",
        "Provider Catalog Facts",
        f"- provider_catalog_key={packet.provider_catalog_key}",
        f"- provider_tier={packet.provider_tier}",
        f"- provider_allowed_boundary={packet.provider_allowed_boundary}",
        f"- requested_probe_kind={packet.requested_probe_kind}",
        f"- requested_surface={packet.requested_surface}",
        "",
        "Allowed Operations",
        *[f"- {item}" for item in packet.allowed_operations],
        "",
        "Explicit Exclusions",
        *[f"- {item}" for item in packet.explicit_exclusions],
        "",
        "Expected Evidence",
        *[f"- {item}" for item in packet.expected_evidence],
        "",
        "Stop Conditions",
        *[f"- {item}" for item in packet.stop_conditions],
        "",
        "Non-Proofs",
        *[f"- {item}" for item in packet.non_proofs],
        "",
        "Caveats",
        *[f"- {item}" for item in packet.caveats],
        "",
        "RESPONSE_METADATA",
        "- provider_executed=false",
        "- model_executed=false",
        "- runtime_executed=false",
        "- platform_executed=false",
        "- worker_dispatched=false",
        "- codex_dispatched=false",
        "- rag_lookup_performed=false",
        "- web_lookup_performed=false",
        "- scheduler_executed=false",
        "- connector_executed=false",
        "- route_executed=false",
        "- production_readiness=false",
    ]
    return "\n".join(lines)
