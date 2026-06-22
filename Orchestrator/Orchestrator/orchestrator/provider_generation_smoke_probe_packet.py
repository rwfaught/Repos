"""Deterministic future local provider generation smoke probe packet.

This packet describes a future manual operator proof boundary. It does not
call providers, execute models, generate text, select routes, dispatch workers,
perform network activity, or prove production readiness.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


NO_SMOKE_PACKET_ACTIVITY_FLAGS = {
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

SMOKE_PACKET_NON_PROOFS = (
    "packet_contract_is_not_provider_execution",
    "packet_contract_is_not_model_execution",
    "packet_contract_is_not_generation",
    "packet_contract_is_not_api_generate",
    "packet_contract_is_not_api_chat",
    "future_smoke_pass_would_not_prove_semantic_correctness",
    "future_smoke_pass_would_not_prove_vram_sufficiency_for_real_workloads",
    "future_smoke_pass_would_not_prove_route_execution",
    "future_smoke_pass_would_not_prove_worker_dispatch",
    "future_smoke_pass_would_not_prove_rag",
    "future_smoke_pass_would_not_prove_scheduler",
    "future_smoke_pass_would_not_prove_connector",
    "future_smoke_pass_would_not_prove_service_api_ui_productization",
    "future_smoke_pass_would_not_prove_production_readiness",
)


@dataclass(frozen=True)
class ProviderGenerationSmokeProbePacket:
    packet_key: str
    future_boundary: str
    provider_catalog_key: str
    model_name: str
    endpoint_surface: str
    endpoint_path: str
    method: str
    request_shape: dict[str, Any]
    prompt_contract: str
    response_acceptance_criteria: tuple[str, ...]
    operator_evidence_to_capture: tuple[str, ...]
    allowed_future_operation: str
    coordinator_acceptance_required: bool
    provider_selection_allowed: bool
    provider_execution_allowed: bool
    generation_allowed_now: bool
    route_execution_allowed: bool
    production_readiness: bool
    non_proofs: tuple[str, ...]
    activity_flags: dict[str, bool]


def get_local_provider_generation_smoke_probe_packet() -> ProviderGenerationSmokeProbePacket:
    """Return the deterministic future smoke probe packet contract."""

    return ProviderGenerationSmokeProbePacket(
        packet_key="local_provider_generation_smoke_probe_packet",
        future_boundary="PHASE_157_LOCAL_PROVIDER_GENERATION_SMOKE_PROBE_27B_OPERATOR_PROOF",
        provider_catalog_key="local_model_candidate",
        model_name="qwen3.6:27b",
        endpoint_surface="local_ollama_http",
        endpoint_path="/api/generate",
        method="POST",
        request_shape={
            "model": "qwen3.6:27b",
            "prompt": "Return exactly: ORCH_PROVIDER_SMOKE_OK",
            "stream": False,
            "output_size": "small",
            "tool_calls": "none",
            "external_lookup": "none",
            "route_execution": "none",
        },
        prompt_contract="Return exactly: ORCH_PROVIDER_SMOKE_OK",
        response_acceptance_criteria=(
            "operator_captures_command_boundary_markers",
            "operator_captures_http_status_code",
            "operator_captures_content_type",
            "operator_captures_response_bytes_count",
            "operator_captures_finish_or_done_marker_if_available",
            "response_text_includes_ORCH_PROVIDER_SMOKE_OK_or_bounded_equivalent",
            "exit_code_captured_separately",
            "elapsed_time_captured_if_possible",
        ),
        operator_evidence_to_capture=(
            "command_boundary_markers",
            "http_status_code",
            "content_type",
            "response_bytes_count",
            "finish_or_done_marker_if_available",
            "response_text_marker_ORCH_PROVIDER_SMOKE_OK",
            "exit_code",
            "elapsed_time_if_present",
        ),
        allowed_future_operation="manual_operator_generation_smoke_probe_only_after_explicit_boundary_acceptance",
        coordinator_acceptance_required=True,
        provider_selection_allowed=False,
        provider_execution_allowed=False,
        generation_allowed_now=False,
        route_execution_allowed=False,
        production_readiness=False,
        non_proofs=SMOKE_PACKET_NON_PROOFS,
        activity_flags=dict(NO_SMOKE_PACKET_ACTIVITY_FLAGS),
    )


def provider_generation_smoke_probe_packet_to_dict(packet: ProviderGenerationSmokeProbePacket) -> dict[str, Any]:
    """Return a serializable smoke probe packet dictionary."""

    payload = asdict(packet)
    payload["request_shape"] = dict(packet.request_shape)
    payload["response_acceptance_criteria"] = list(packet.response_acceptance_criteria)
    payload["operator_evidence_to_capture"] = list(packet.operator_evidence_to_capture)
    payload["non_proofs"] = list(packet.non_proofs)
    payload["activity_flags"] = dict(packet.activity_flags)
    return payload


def summarize_provider_generation_smoke_probe_packet(packet: ProviderGenerationSmokeProbePacket) -> str:
    """Render a compact summary without execution authority."""

    return (
        f"{packet.packet_key}: future_boundary={packet.future_boundary}; "
        f"provider_catalog_key={packet.provider_catalog_key}; model_name={packet.model_name}; "
        f"endpoint_shape={packet.method} {packet.endpoint_surface}{packet.endpoint_path}; "
        "packet_contract_only=true; generation_allowed_now=false"
    )
