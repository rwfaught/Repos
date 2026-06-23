"""Deterministic supervised provider-call tracer packet contract.

This module defines a future operator packet and a pure captured-result
classifier. It never calls a provider, model, route, worker, runtime surface,
network endpoint, platform, connector, scheduler, service, UI, or production
behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


PHASE = "PHASE_187"
ARTIFACT_KIND = "supervised_provider_call_tracer_packet_contract"
FIXTURE_ID = "safe_direct_answer"
ORIGINAL_PACKET_PHASE = "PHASE_183"
TARGET_RECONCILIATION_PHASE = "PHASE_187"
INVENTORY_EVIDENCE_PHASE = "PHASE_186_RETRY4"
SOURCE_TRACER_PHASE = "PHASE_169"
ADAPTER_PHASE = "PHASE_176"
OPERATOR_SMOKE_PHASE = "PHASE_179"
PROVIDER_CATALOG_KEY = "local_model_candidate"
MODEL_NAME = "qwen3.6:35b-a3b"
RETIRED_PACKET_TARGET = "qwen3.6:27b"
ENDPOINT_SHAPE = "POST local_ollama_http/api/generate"
ENDPOINT_URL = "http://127.0.0.1:11434/api/generate"
PROMPT_CONTRACT = "Return exactly: ORCH_PROVIDER_SMOKE_OK"
EXPECTED_MARKER = "ORCH_PROVIDER_SMOKE_OK"
FUTURE_BOUNDARY = "future_supervised_provider_call_tracer_operator_proof"
FUTURE_PROOF = "captured_http_status_json_response_marker_and_no_route_execution"
CURRENT_READINESS = "target_reconciliation_complete_future_marker_smoke_required"
INVENTORY_EVIDENCE_KEY = "phase_186_retry4_qwen36_35b_a3b_inventory_visibility_only"


SUPERVISED_PROVIDER_CALL_TRACER_NON_PROOFS = (
    "supervised_provider_call_tracer_is_packet_contract_only",
    "endpoint_string_is_not_endpoint_execution",
    "model_name_is_not_model_execution",
    "phase_186_retry4_inventory_visibility_is_not_marker_smoke_proof",
    "qwen36_35b_a3b_has_no_supervised_marker_smoke_proof_yet",
    "qwen36_27b_marker_smoke_evidence_is_not_transferred_to_qwen36_35b_a3b",
    "future_smoke_pass_would_not_prove_semantic_correctness",
    "future_smoke_pass_would_not_prove_real_workload_loadability",
    "future_smoke_pass_would_not_prove_real_workload_vram_sufficiency",
    "future_smoke_pass_would_not_prove_route_execution",
    "future_smoke_pass_would_not_prove_production_readiness",
)

NO_SUPERVISED_PROVIDER_CALL_TRACER_ACTIVITY_FLAGS = {
    "provider_selected": False,
    "provider_executed": False,
    "model_selected": False,
    "model_executed": False,
    "runtime_executed": False,
    "platform_executed": False,
    "route_executed": False,
    "generation_performed": False,
    "api_generate_called": False,
    "api_chat_called": False,
    "api_show_called": False,
    "api_tags_called": False,
    "worker_dispatched": False,
    "codex_dispatched": False,
    "ollama_executed": False,
    "wsl_executed": False,
    "openclaw_executed": False,
    "hermes_executed": False,
    "discord_executed": False,
    "rag_lookup_performed": False,
    "web_lookup_performed": False,
    "scheduler_executed": False,
    "connector_executed": False,
    "service_executed": False,
    "api_endpoint_executed": False,
    "ui_executed": False,
    "product_executed": False,
    "cleanup_performed": False,
    "deletion_performed": False,
    "archive_performed": False,
    "production_executed": False,
}


@dataclass(frozen=True)
class SupervisedProviderCallTracerPacket:
    phase: str
    artifact_kind: str
    fixture_id: str
    original_packet_phase: str
    target_reconciliation_phase: str
    inventory_evidence_phase: str
    source_tracer_phase: str
    adapter_phase: str
    operator_smoke_phase: str
    provider_catalog_key: str
    model_name: str
    endpoint_shape: str
    endpoint_url: str
    prompt_contract: str
    expected_marker: str
    request_parameters: dict[str, Any]
    required_future_boundary: str
    required_future_proof: str
    current_readiness: str
    provider_evidence_keys: tuple[str, ...]
    accepted_facts: tuple[str, ...]
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    caveats: tuple[str, ...]
    non_proofs: tuple[str, ...]
    activity_flags: dict[str, bool]
    provider_selection_allowed: bool
    provider_execution_allowed: bool
    route_execution_allowed: bool
    generation_allowed: bool
    production_readiness: bool


@dataclass(frozen=True)
class SupervisedProviderCallTracerReview:
    status: str
    classification: str
    accepted: bool
    accepted_facts: tuple[str, ...]
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    caveats: tuple[str, ...]
    non_proofs: tuple[str, ...]
    route_execution_allowed: bool
    production_readiness: bool

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in (
            "accepted_facts",
            "blocked_conditions",
            "missing_requirements",
            "caveats",
            "non_proofs",
        ):
            payload[key] = list(payload[key])
        return payload


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def build_supervised_provider_call_tracer_packet() -> SupervisedProviderCallTracerPacket:
    """Build the deterministic future operator packet without execution."""

    provider_evidence_keys = (INVENTORY_EVIDENCE_KEY,)
    accepted_facts = (
        f"phase={PHASE}",
        f"artifact_kind={ARTIFACT_KIND}",
        f"fixture_id={FIXTURE_ID}",
        f"original_packet_phase={ORIGINAL_PACKET_PHASE}",
        f"target_reconciliation_phase={TARGET_RECONCILIATION_PHASE}",
        f"inventory_evidence_phase={INVENTORY_EVIDENCE_PHASE}",
        f"source_tracer_phase={SOURCE_TRACER_PHASE}",
        f"adapter_phase={ADAPTER_PHASE}",
        f"operator_smoke_phase={OPERATOR_SMOKE_PHASE}",
        f"provider_catalog_key={PROVIDER_CATALOG_KEY}",
        f"model_name={MODEL_NAME}",
        f"retired_packet_target={RETIRED_PACKET_TARGET}",
        f"endpoint_shape={ENDPOINT_SHAPE}",
        "endpoint_url_registered_as_string_only",
        f"prompt_contract={PROMPT_CONTRACT}",
        f"expected_marker={EXPECTED_MARKER}",
        f"required_future_boundary={FUTURE_BOUNDARY}",
        f"required_future_proof={FUTURE_PROOF}",
        f"current_readiness={CURRENT_READINESS}",
        "phase_186_retry4_api_version_http_200_ollama_0_30_10",
        "phase_186_retry4_api_tags_http_200",
        "phase_186_retry4_qwen36_27b_absent_from_inventory",
        "phase_186_retry4_qwen36_35b_a3b_present_in_inventory",
    )
    caveats = (
        "packet_contract_only",
        "endpoint_string_is_not_endpoint_execution",
        "model_name_is_not_model_execution",
        "phase_186_retry4_inventory_visibility_is_not_marker_smoke_proof",
        "qwen36_35b_a3b_requires_future_supervised_marker_smoke_proof",
        "qwen36_27b_marker_smoke_evidence_not_transferred_to_qwen36_35b_a3b",
        "future_operator_must_capture_status_json_marker_and_no_route_execution",
    )
    missing_requirements = (
        "future_operator_run_not_performed_by_phase_187",
        "captured_http_status_missing_until_future_operator_boundary",
        "captured_json_response_missing_until_future_operator_boundary",
        "captured_marker_missing_until_future_operator_boundary",
        "qwen36_35b_a3b_supervised_marker_smoke_proof_missing_until_future_boundary",
    )
    return SupervisedProviderCallTracerPacket(
        phase=PHASE,
        artifact_kind=ARTIFACT_KIND,
        fixture_id=FIXTURE_ID,
        original_packet_phase=ORIGINAL_PACKET_PHASE,
        target_reconciliation_phase=TARGET_RECONCILIATION_PHASE,
        inventory_evidence_phase=INVENTORY_EVIDENCE_PHASE,
        source_tracer_phase=SOURCE_TRACER_PHASE,
        adapter_phase=ADAPTER_PHASE,
        operator_smoke_phase=OPERATOR_SMOKE_PHASE,
        provider_catalog_key=PROVIDER_CATALOG_KEY,
        model_name=MODEL_NAME,
        endpoint_shape=ENDPOINT_SHAPE,
        endpoint_url=ENDPOINT_URL,
        prompt_contract=PROMPT_CONTRACT,
        expected_marker=EXPECTED_MARKER,
        request_parameters={
            "stream": False,
            "num_predict": 96,
            "temperature": 0,
        },
        required_future_boundary=FUTURE_BOUNDARY,
        required_future_proof=FUTURE_PROOF,
        current_readiness=CURRENT_READINESS,
        provider_evidence_keys=provider_evidence_keys,
        accepted_facts=accepted_facts,
        blocked_conditions=("future_operator_boundary_required_before_execution",),
        missing_requirements=missing_requirements,
        caveats=caveats,
        non_proofs=SUPERVISED_PROVIDER_CALL_TRACER_NON_PROOFS,
        activity_flags=dict(NO_SUPERVISED_PROVIDER_CALL_TRACER_ACTIVITY_FLAGS),
        provider_selection_allowed=False,
        provider_execution_allowed=False,
        route_execution_allowed=False,
        generation_allowed=False,
        production_readiness=False,
    )


def supervised_provider_call_tracer_packet_to_dict(
    packet: SupervisedProviderCallTracerPacket,
) -> dict[str, Any]:
    """Return a JSON-safe packet payload."""

    payload = asdict(packet)
    for key in (
        "provider_evidence_keys",
        "accepted_facts",
        "blocked_conditions",
        "missing_requirements",
        "caveats",
        "non_proofs",
    ):
        payload[key] = list(payload[key])
    payload["activity_flags"] = dict(packet.activity_flags)
    payload["request_parameters"] = dict(packet.request_parameters)
    return payload


def render_supervised_provider_call_tracer_packet_text(
    packet: SupervisedProviderCallTracerPacket,
) -> str:
    """Render the packet in a coordinator-review-shaped text form."""

    lines = [
        "Assessment",
        "Supervised provider-call tracer packet is ready for a future operator boundary only.",
        "",
        "Accepted Facts",
        *[f"- {fact}" for fact in packet.accepted_facts],
        f"- endpoint_url={packet.endpoint_url}",
        f"- provider_evidence_keys={', '.join(packet.provider_evidence_keys)}",
        f"- stream={str(packet.request_parameters['stream']).lower()}",
        f"- num_predict={packet.request_parameters['num_predict']}",
        "",
        "Decision",
        "Do not execute. Register packet contract only.",
        "",
        "NBM",
        packet.required_future_boundary,
        "",
        "Deliverable/Command",
        (
            "Future operator may run the supervised local provider marker smoke "
            "only under a separate accepted boundary."
        ),
        "",
        "RESPONSE_METADATA",
        f"phase={packet.phase}",
        f"artifact_kind={packet.artifact_kind}",
        f"fixture_id={packet.fixture_id}",
        f"model_name={packet.model_name}",
        f"provider_selection_allowed={str(packet.provider_selection_allowed).lower()}",
        f"provider_execution_allowed={str(packet.provider_execution_allowed).lower()}",
        f"route_execution_allowed={str(packet.route_execution_allowed).lower()}",
        f"generation_allowed={str(packet.generation_allowed).lower()}",
        f"production_readiness={str(packet.production_readiness).lower()}",
    ]
    return "\n".join(lines)


def _review(
    *,
    status: str,
    classification: str,
    accepted: bool,
    accepted_facts: tuple[str, ...] = (),
    blocked_conditions: tuple[str, ...] = (),
    missing_requirements: tuple[str, ...] = (),
    caveats: tuple[str, ...] = (),
) -> SupervisedProviderCallTracerReview:
    return SupervisedProviderCallTracerReview(
        status=status,
        classification=classification,
        accepted=accepted,
        accepted_facts=_dedupe(accepted_facts),
        blocked_conditions=_dedupe(blocked_conditions),
        missing_requirements=_dedupe(missing_requirements),
        caveats=_dedupe(
            caveats
            + (
                "captured_result_review_only",
                "pass_classification_does_not_authorize_route_execution",
                "pass_classification_does_not_authorize_production_readiness",
            )
        ),
        non_proofs=SUPERVISED_PROVIDER_CALL_TRACER_NON_PROOFS,
        route_execution_allowed=False,
        production_readiness=False,
    )


def classify_supervised_provider_call_tracer_result(
    captured_result: dict[str, Any],
) -> SupervisedProviderCallTracerReview:
    """Classify caller-supplied captured result data without making calls."""

    required_fields = (
        "http_status",
        "json_parse_success",
        "returned_model",
        "response_text",
        "done",
    )
    missing = tuple(field for field in required_fields if field not in captured_result)
    if missing:
        return _review(
            status="FAIL",
            classification="missing_required_fields",
            accepted=False,
            blocked_conditions=("captured_result_missing_required_fields",),
            missing_requirements=tuple(f"missing_{field}" for field in missing),
        )

    if captured_result["http_status"] != 200:
        return _review(
            status="FAIL",
            classification="non_200_http_status",
            accepted=False,
            blocked_conditions=("http_status_not_200",),
            accepted_facts=(f"http_status={captured_result['http_status']}",),
        )

    if captured_result["json_parse_success"] is not True:
        return _review(
            status="FAIL",
            classification="json_parse_failure",
            accepted=False,
            blocked_conditions=("json_parse_success_not_true",),
        )

    if captured_result["returned_model"] != MODEL_NAME:
        return _review(
            status="FAIL",
            classification="wrong_model",
            accepted=False,
            blocked_conditions=("returned_model_mismatch",),
            accepted_facts=(f"returned_model={captured_result['returned_model']}",),
        )

    if EXPECTED_MARKER not in str(captured_result["response_text"]):
        return _review(
            status="FAIL",
            classification="missing_marker",
            accepted=False,
            blocked_conditions=("expected_marker_missing_from_response_text",),
        )

    if captured_result["done"] is not True:
        return _review(
            status="FAIL",
            classification="incomplete_done_false",
            accepted=False,
            blocked_conditions=("done_not_true",),
        )

    accepted_facts = (
        "http_status=200",
        "json_parse_success=True",
        f"returned_model={MODEL_NAME}",
        f"response_text_contains={EXPECTED_MARKER}",
        "done=True",
    )
    if "done_reason" in captured_result:
        accepted_facts = accepted_facts + (f"done_reason={captured_result['done_reason']}",)
    return _review(
        status="PASS",
        classification="captured_marker_smoke_pass_not_route_execution",
        accepted=True,
        accepted_facts=accepted_facts,
        caveats=(
            "future_smoke_pass_would_not_prove_semantic_correctness",
            "future_smoke_pass_would_not_prove_real_workload_loadability",
            "future_smoke_pass_would_not_prove_production_readiness",
        ),
    )
