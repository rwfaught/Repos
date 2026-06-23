"""Deterministic route-mediated provider smoke runner contract.

This module prepares dry artifact shapes and reviews caller-supplied captured
results for a future route-mediated provider smoke proof. It never executes a
route, provider, model, runtime surface, HTTP endpoint, worker, platform,
connector, scheduler, service, UI, or production behavior.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from orchestrator.route_path_proof_packet import (
    DISALLOWED_MODEL,
    FALLBACK_CANDIDATE,
    FUTURE_ROUTE_MARKER,
    PRIOR_DIRECT_MARKER,
    REQUIRED_FUTURE_PROOF_FIELDS,
    ROUTE_PATH_PROOF_NON_PROOFS,
    ROUTE_PROOF_TARGET_MODEL,
    build_route_path_proof_packet,
    review_route_path_proof_capture,
)


PHASE = "PHASE_206"
ARTIFACT_KIND = "route_mediated_provider_smoke_runner_contract"
EXECUTION_ADAPTER_PHASE = "PHASE_208"
EXECUTION_ADAPTER_ARTIFACT_KIND = "route_mediated_provider_smoke_execution_adapter_contract"
LIVE_TRANSPORT_ADAPTER_PHASE = "PHASE_212"
LIVE_TRANSPORT_ADAPTER_ARTIFACT_KIND = "route_mediated_provider_smoke_live_transport_adapter_contract"
PROMPT = f"Return exactly: {FUTURE_ROUTE_MARKER}"
DEFAULT_MODE = "dry_artifact_shape_only"
EXECUTION_MODE = "route_mediated_provider_smoke_execution"
LIVE_OLLAMA_EXECUTION_MODE = "live_ollama_route_mediated_provider_smoke_execution"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
OLLAMA_GENERATE_PATH = "/api/generate"
LIVE_OLLAMA_OPTIONS = {
    "num_ctx": 4096,
    "num_predict": 64,
    "temperature": 0,
}


ROUTE_MEDIATED_PROVIDER_SMOKE_NON_PROOFS = (
    "route_mediated_provider_smoke_runner_is_not_route_execution",
    "route_mediated_provider_smoke_runner_is_not_provider_execution",
    "route_mediated_provider_smoke_runner_is_not_model_execution",
    "route_mediated_provider_smoke_runner_is_not_runtime_execution",
    "route_mediated_provider_smoke_runner_is_not_http_or_ollama_call",
    "route_mediated_provider_smoke_runner_is_not_worker_dispatch",
    "route_mediated_provider_smoke_runner_is_not_production_readiness",
    "source_test_acceptance_is_not_runtime_proof",
) + ROUTE_PATH_PROOF_NON_PROOFS

NO_RUNNER_ACTIVITY_FLAGS = {
    "dry_artifact_prepared": False,
    "caller_supplied_capture_reviewed": False,
    "future_runtime_execution_requested": False,
    "provider_call_allowed": False,
    "request_intake_executed": False,
    "route_recommended": False,
    "route_readiness_executed": False,
    "route_executed": False,
    "provider_executed": False,
    "model_executed": False,
    "generation_performed": False,
    "api_generate_called": False,
    "api_chat_called": False,
    "api_tags_called": False,
    "api_version_called": False,
    "runtime_executed": False,
    "worker_dispatched": False,
    "ollama_executed": False,
    "wsl_executed": False,
    "openclaw_executed": False,
    "hermes_executed": False,
    "discord_executed": False,
    "artifact_persisted": False,
    "outcome_displayed": False,
    "production_executed": False,
}


@dataclass(frozen=True)
class RouteMediatedProviderSmokeArtifact:
    phase: str
    artifact_kind: str
    mode: str
    route_marker: str
    prompt: str
    target_model: str
    disallowed_model: str
    fallback_candidate: str
    ollama_url: str
    request_body_redacted_or_safe: Any
    request_intake_harness_evidence: Any
    route_recommendation_readiness_evidence: Any
    explicit_route_execution_boundary_evidence: Any
    provider_call_through_route_path_evidence: Any
    captured_http_status_json_model_marker_evidence: Any
    persisted_artifact_path_evidence: Any
    displayed_reviewable_outcome_evidence: Any
    route_path_packet_review: dict[str, Any]
    phase_206_runner_review: Any
    phase_208_adapter_review: Any
    non_proofs: tuple[str, ...]
    activity_flags: dict[str, bool]
    route_execution_allowed: bool
    provider_execution_allowed: bool
    generation_allowed: bool
    production_readiness: bool


@dataclass(frozen=True)
class RouteMediatedProviderSmokeResult:
    accepted: bool
    classification: str
    artifact: RouteMediatedProviderSmokeArtifact
    payload: dict[str, Any]
    written_path: str | None = None


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _flags(**updates: bool) -> dict[str, bool]:
    flags = dict(NO_RUNNER_ACTIVITY_FLAGS)
    for key, value in updates.items():
        flags[key] = bool(value)
    return flags


def build_route_mediated_provider_smoke_dry_artifact() -> RouteMediatedProviderSmokeResult:
    """Build a deterministic dry artifact shape without execution."""

    packet = build_route_path_proof_packet()
    packet_payload = {
        "status": "PENDING",
        "classification": "route_mediated_runtime_proof_not_run",
        "packet_phase": packet.phase,
        "required_future_proof_fields": list(packet.required_future_proof_fields),
        "route_execution_allowed": False,
        "provider_execution_allowed": False,
        "generation_allowed": False,
        "production_readiness": False,
    }
    pending = "pending_future_runtime_operator_boundary"
    artifact = RouteMediatedProviderSmokeArtifact(
        phase=PHASE,
        artifact_kind=ARTIFACT_KIND,
        mode=DEFAULT_MODE,
        route_marker=FUTURE_ROUTE_MARKER,
        prompt=PROMPT,
        target_model=ROUTE_PROOF_TARGET_MODEL,
        disallowed_model=DISALLOWED_MODEL,
        fallback_candidate=FALLBACK_CANDIDATE,
        ollama_url="not_applicable_dry_runner",
        request_body_redacted_or_safe="not_applicable_dry_runner",
        request_intake_harness_evidence=pending,
        route_recommendation_readiness_evidence=pending,
        explicit_route_execution_boundary_evidence=pending,
        provider_call_through_route_path_evidence=pending,
        captured_http_status_json_model_marker_evidence=pending,
        persisted_artifact_path_evidence=pending,
        displayed_reviewable_outcome_evidence=pending,
        route_path_packet_review=packet_payload,
        phase_206_runner_review="not_applicable_phase_206_base_artifact",
        phase_208_adapter_review="not_applicable_phase_206_base_artifact",
        non_proofs=ROUTE_MEDIATED_PROVIDER_SMOKE_NON_PROOFS,
        activity_flags=_flags(dry_artifact_prepared=True),
        route_execution_allowed=False,
        provider_execution_allowed=False,
        generation_allowed=False,
        production_readiness=False,
    )
    payload = route_mediated_provider_smoke_artifact_to_dict(artifact)
    return RouteMediatedProviderSmokeResult(
        accepted=False,
        classification="dry_artifact_shape_only_not_runtime_proof",
        artifact=artifact,
        payload=payload,
    )


def execute_route_mediated_provider_smoke_with_injected_provider(
    *,
    provider_callable: Any | None,
    allow_route_execution: bool = False,
    allow_provider_call: bool = False,
    execution_mode: str = "",
    target_model: str = ROUTE_PROOF_TARGET_MODEL,
    route_marker: str = FUTURE_ROUTE_MARKER,
    production_readiness: bool = False,
    output_path: str | Path | None = None,
) -> RouteMediatedProviderSmokeResult:
    """Run the guarded fake/injected execution adapter without live transport.

    The callable is dependency-injected by a later operator/test harness. This
    function never imports or constructs a provider transport on its own.
    """

    rejection = _execution_adapter_rejection(
        allow_route_execution=allow_route_execution,
        allow_provider_call=allow_provider_call,
        execution_mode=execution_mode,
        target_model=target_model,
        route_marker=route_marker,
        production_readiness=production_readiness,
        provider_callable=provider_callable,
    )
    if rejection:
        return rejection

    provider_result = provider_callable(model=target_model, prompt=PROMPT)
    captured_result = _captured_result_from_provider_result(provider_result)
    runner_result = review_route_mediated_provider_smoke_capture(captured_result)
    classification = (
        "fake_route_mediated_provider_smoke_shape_valid_not_runtime_proof"
        if runner_result.accepted
        else runner_result.classification
    )
    artifact = _phase_208_artifact_from_phase_206_artifact(
        runner_result.artifact,
        classification=classification,
        accepted=runner_result.accepted,
        activity_flags=_flags(
            caller_supplied_capture_reviewed=True,
            future_runtime_execution_requested=True,
            provider_call_allowed=True,
            request_intake_executed=True,
            route_recommended=True,
            route_readiness_executed=True,
            route_executed=True,
            provider_executed=True,
            model_executed=True,
            generation_performed=True,
            api_generate_called=True,
            outcome_displayed=True,
        ),
    )
    payload = route_mediated_provider_smoke_artifact_to_dict(artifact)
    result = RouteMediatedProviderSmokeResult(
        accepted=runner_result.accepted,
        classification=classification,
        artifact=artifact,
        payload=payload,
    )
    if output_path is not None:
        return _write_result_payload(result, output_path, "phase_208_route_mediated_provider_smoke_execution_adapter_artifact.json")
    return result


def execute_route_mediated_provider_smoke_with_live_ollama_transport(
    *,
    transport_callable: Any | None = None,
    execute_live_ollama_route_smoke: bool = False,
    allow_route_execution: bool = False,
    allow_provider_call: bool = False,
    allow_ollama_http: bool = False,
    execution_mode: str = "",
    target_model: str = ROUTE_PROOF_TARGET_MODEL,
    route_marker: str = FUTURE_ROUTE_MARKER,
    prompt: str = PROMPT,
    production_readiness: bool = False,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    output_path: str | Path | None = None,
) -> RouteMediatedProviderSmokeResult:
    """Run the Phase 212 guarded live Ollama transport adapter.

    Tests inject ``transport_callable``. A later operator boundary may omit it,
    in which case the guarded stdlib Ollama transport is used only after every
    explicit live-execution flag has passed.
    """

    request_body = _live_ollama_request_body(target_model=target_model, prompt=prompt)
    rejection = _live_transport_adapter_rejection(
        execute_live_ollama_route_smoke=execute_live_ollama_route_smoke,
        allow_route_execution=allow_route_execution,
        allow_provider_call=allow_provider_call,
        allow_ollama_http=allow_ollama_http,
        execution_mode=execution_mode,
        target_model=target_model,
        route_marker=route_marker,
        prompt=prompt,
        production_readiness=production_readiness,
        output_path=output_path,
    )
    if rejection:
        return rejection

    transport = transport_callable or _stdlib_ollama_generate_transport
    provider_result = transport(ollama_url=ollama_url, request_body=request_body)
    captured_result = _captured_result_from_live_transport_result(
        provider_result,
        ollama_url=ollama_url,
        request_body=request_body,
        injected_transport=transport_callable is not None,
    )
    runner_result = review_route_mediated_provider_smoke_capture(captured_result)
    live_evidence = _live_runtime_evidence_present(captured_result)
    classification = (
        "test_injected_live_transport_shape_valid_not_runtime_proof"
        if transport_callable is not None and runner_result.accepted
        else "route_mediated_provider_smoke_runtime_marker_pass"
        if transport_callable is None and runner_result.accepted and live_evidence
        else runner_result.classification
    )
    accepted = runner_result.accepted and (
        transport_callable is not None or classification == "route_mediated_provider_smoke_runtime_marker_pass"
    )
    artifact = _phase_212_artifact_from_phase_206_artifact(
        runner_result.artifact,
        classification=classification,
        accepted=accepted,
        ollama_url=ollama_url,
        request_body=request_body,
        phase_206_runner_review=runner_result.artifact.route_path_packet_review,
        phase_208_adapter_review={
            "phase": EXECUTION_ADAPTER_PHASE,
            "not_invoked_by_phase_212": True,
            "fake_injected_provider_path_distinct_from_live_transport_path": True,
        },
        activity_flags=_flags(
            caller_supplied_capture_reviewed=True,
            future_runtime_execution_requested=True,
            provider_call_allowed=True,
            request_intake_executed=True,
            route_recommended=True,
            route_readiness_executed=True,
            route_executed=True,
            provider_executed=True,
            model_executed=True,
            generation_performed=True,
            api_generate_called=True,
            ollama_executed=True,
            outcome_displayed=True,
        ),
    )
    payload = route_mediated_provider_smoke_artifact_to_dict(artifact)
    result = RouteMediatedProviderSmokeResult(
        accepted=accepted,
        classification=classification,
        artifact=artifact,
        payload=payload,
    )
    return _write_result_payload(result, output_path, "phase_212_route_mediated_provider_smoke_live_transport_adapter_artifact.json")


def _execution_adapter_rejection(
    *,
    allow_route_execution: bool,
    allow_provider_call: bool,
    execution_mode: str,
    target_model: str,
    route_marker: str,
    production_readiness: bool,
    provider_callable: Any | None,
) -> RouteMediatedProviderSmokeResult | None:
    if not allow_route_execution:
        return _phase_208_rejected_result("missing_allow_route_execution")
    if not allow_provider_call:
        return _phase_208_rejected_result("missing_allow_provider_call")
    if execution_mode != EXECUTION_MODE:
        return _phase_208_rejected_result("missing_explicit_route_smoke_execution_mode")
    if target_model == DISALLOWED_MODEL:
        return _phase_208_rejected_result("disallowed_35b_target_rejected")
    if target_model == FALLBACK_CANDIDATE:
        return _phase_208_rejected_result("fallback_candidate_not_active_target")
    if target_model != ROUTE_PROOF_TARGET_MODEL:
        return _phase_208_rejected_result("wrong_target_model")
    if route_marker != FUTURE_ROUTE_MARKER:
        return _phase_208_rejected_result("wrong_route_marker")
    if production_readiness is True:
        return _phase_208_rejected_result("production_readiness_claim_rejected")
    if provider_callable is None:
        return _phase_208_rejected_result("provider_callable_required")
    return None


def _live_transport_adapter_rejection(
    *,
    execute_live_ollama_route_smoke: bool,
    allow_route_execution: bool,
    allow_provider_call: bool,
    allow_ollama_http: bool,
    execution_mode: str,
    target_model: str,
    route_marker: str,
    prompt: str,
    production_readiness: bool,
    output_path: str | Path | None,
) -> RouteMediatedProviderSmokeResult | None:
    if not execute_live_ollama_route_smoke:
        return _phase_212_rejected_result("missing_execute_live_ollama_route_smoke")
    if not allow_route_execution:
        return _phase_212_rejected_result("missing_allow_route_execution")
    if not allow_provider_call:
        return _phase_212_rejected_result("missing_allow_provider_call")
    if not allow_ollama_http:
        return _phase_212_rejected_result("missing_allow_ollama_http")
    if execution_mode != LIVE_OLLAMA_EXECUTION_MODE:
        return _phase_212_rejected_result("missing_explicit_live_ollama_execution_mode")
    if target_model == DISALLOWED_MODEL:
        return _phase_212_rejected_result("disallowed_35b_target_rejected")
    if target_model == FALLBACK_CANDIDATE:
        return _phase_212_rejected_result("fallback_candidate_not_active_target")
    if target_model != ROUTE_PROOF_TARGET_MODEL:
        return _phase_212_rejected_result("wrong_target_model")
    if route_marker != FUTURE_ROUTE_MARKER:
        return _phase_212_rejected_result("wrong_route_marker")
    if prompt != PROMPT:
        return _phase_212_rejected_result("wrong_prompt")
    if production_readiness is True:
        return _phase_212_rejected_result("production_readiness_claim_rejected")
    if output_path is None:
        return _phase_212_rejected_result("output_path_required")
    return None


def _phase_208_rejected_result(classification: str) -> RouteMediatedProviderSmokeResult:
    base = build_route_mediated_provider_smoke_dry_artifact().artifact
    artifact = _phase_208_artifact_from_phase_206_artifact(
        base,
        classification=classification,
        accepted=False,
        activity_flags=_flags(future_runtime_execution_requested=True),
    )
    return RouteMediatedProviderSmokeResult(
        accepted=False,
        classification=classification,
        artifact=artifact,
        payload=route_mediated_provider_smoke_artifact_to_dict(artifact),
    )


def _phase_212_rejected_result(classification: str) -> RouteMediatedProviderSmokeResult:
    base = build_route_mediated_provider_smoke_dry_artifact().artifact
    artifact = _phase_212_artifact_from_phase_206_artifact(
        base,
        classification=classification,
        accepted=False,
        ollama_url=DEFAULT_OLLAMA_URL,
        request_body=_live_ollama_request_body(),
        phase_206_runner_review=base.route_path_packet_review,
        phase_208_adapter_review="not_invoked_guard_rejection",
        activity_flags=_flags(future_runtime_execution_requested=True),
    )
    return RouteMediatedProviderSmokeResult(
        accepted=False,
        classification=classification,
        artifact=artifact,
        payload=route_mediated_provider_smoke_artifact_to_dict(artifact),
    )


def _captured_result_from_provider_result(provider_result: dict[str, Any]) -> dict[str, Any]:
    response_text = str(provider_result.get("response_text", provider_result.get("response", "")))
    returned_model = str(provider_result.get("returned_model", provider_result.get("model", "")))
    marker = str(provider_result.get("marker", response_text))
    return {
        "request_intake_harness_evidence": {"source": "phase_208_injected_adapter", "mode": "fake_injected"},
        "route_recommendation_readiness_evidence": {"target_model": ROUTE_PROOF_TARGET_MODEL},
        "explicit_route_execution_boundary_evidence": {"execution_mode": EXECUTION_MODE},
        "provider_call_through_route_path_evidence": {"transport": "injected_provider_callable"},
        "captured_http_status_json_model_marker_evidence": {
            "http_status": provider_result.get("http_status"),
            "json_parse_success": provider_result.get("json_parse_success"),
            "returned_model": returned_model,
            "response_text": response_text,
            "done": provider_result.get("done"),
            "done_reason": provider_result.get("done_reason"),
            "marker_present": FUTURE_ROUTE_MARKER in response_text or marker == FUTURE_ROUTE_MARKER,
        },
        "persisted_artifact_path_evidence": {"pending_or_caller_supplied": True},
        "displayed_reviewable_outcome_evidence": {"reviewable_payload_built": True},
        "marker": marker,
        "returned_model": returned_model,
        "production_readiness": False,
    }


def _captured_result_from_live_transport_result(
    provider_result: dict[str, Any],
    *,
    ollama_url: str,
    request_body: dict[str, Any],
    injected_transport: bool,
) -> dict[str, Any]:
    response_text = str(provider_result.get("response_text", provider_result.get("response", "")))
    returned_model = str(provider_result.get("returned_model", provider_result.get("model", "")))
    marker = str(provider_result.get("marker", response_text))
    return {
        "request_intake_harness_evidence": {
            "source": "phase_212_live_transport_adapter",
            "mode": "test_injected_transport" if injected_transport else "live_ollama_transport",
        },
        "route_recommendation_readiness_evidence": {"target_model": ROUTE_PROOF_TARGET_MODEL},
        "explicit_route_execution_boundary_evidence": {"execution_mode": LIVE_OLLAMA_EXECUTION_MODE},
        "provider_call_through_route_path_evidence": {
            "transport": "injected_live_transport_callable" if injected_transport else "stdlib_urllib_ollama_generate",
            "ollama_url": ollama_url,
            "endpoint_shape": f"POST local_ollama_http{OLLAMA_GENERATE_PATH}",
        },
        "captured_http_status_json_model_marker_evidence": {
            "http_status": provider_result.get("http_status"),
            "json_parse_success": provider_result.get("json_parse_success"),
            "returned_model": returned_model,
            "response_text": response_text,
            "done": provider_result.get("done"),
            "done_reason": provider_result.get("done_reason"),
            "marker_present": FUTURE_ROUTE_MARKER in response_text or marker == FUTURE_ROUTE_MARKER,
            "request_body_redacted_or_safe": request_body,
        },
        "persisted_artifact_path_evidence": {"pending_until_write": True},
        "displayed_reviewable_outcome_evidence": {"reviewable_payload_built": True},
        "marker": marker,
        "returned_model": returned_model,
        "production_readiness": False,
    }


def _phase_208_artifact_from_phase_206_artifact(
    artifact: RouteMediatedProviderSmokeArtifact,
    *,
    classification: str,
    accepted: bool,
    activity_flags: dict[str, bool],
) -> RouteMediatedProviderSmokeArtifact:
    return RouteMediatedProviderSmokeArtifact(
        **{
            **asdict(artifact),
            "phase": EXECUTION_ADAPTER_PHASE,
            "artifact_kind": EXECUTION_ADAPTER_ARTIFACT_KIND,
            "mode": "fake_injected_execution_review_only" if accepted else "guarded_execution_adapter_rejected",
            "route_path_packet_review": {
                **artifact.route_path_packet_review,
                "phase_206_runner_review": artifact.route_path_packet_review,
                "adapter_classification": classification,
                "adapter_accepted": accepted,
                "source_test_acceptance_is_not_runtime_proof": True,
            },
            "activity_flags": activity_flags,
            "production_readiness": False,
        }
    )


def _phase_212_artifact_from_phase_206_artifact(
    artifact: RouteMediatedProviderSmokeArtifact,
    *,
    classification: str,
    accepted: bool,
    ollama_url: str,
    request_body: dict[str, Any],
    phase_206_runner_review: Any,
    phase_208_adapter_review: Any,
    activity_flags: dict[str, bool],
) -> RouteMediatedProviderSmokeArtifact:
    return RouteMediatedProviderSmokeArtifact(
        **{
            **asdict(artifact),
            "phase": LIVE_TRANSPORT_ADAPTER_PHASE,
            "artifact_kind": LIVE_TRANSPORT_ADAPTER_ARTIFACT_KIND,
            "mode": "live_ollama_transport_review_only" if accepted else "guarded_live_transport_adapter_rejected",
            "ollama_url": ollama_url,
            "request_body_redacted_or_safe": request_body,
            "route_path_packet_review": {
                **artifact.route_path_packet_review,
                "phase_212_live_transport_classification": classification,
                "phase_212_live_transport_accepted": accepted,
                "source_test_acceptance_is_not_runtime_proof": True,
                "runtime_pass_classification_reserved_for_non_injected_live_http": (
                    "route_mediated_provider_smoke_runtime_marker_pass"
                ),
            },
            "phase_206_runner_review": phase_206_runner_review,
            "phase_208_adapter_review": phase_208_adapter_review,
            "activity_flags": activity_flags,
            "production_readiness": False,
        }
    )


def _live_ollama_request_body(
    *,
    target_model: str = ROUTE_PROOF_TARGET_MODEL,
    prompt: str = PROMPT,
) -> dict[str, Any]:
    return {
        "model": target_model,
        "prompt": prompt,
        "stream": False,
        "options": dict(LIVE_OLLAMA_OPTIONS),
    }


def _live_runtime_evidence_present(captured_result: dict[str, Any]) -> bool:
    evidence = captured_result.get("captured_http_status_json_model_marker_evidence", {})
    return (
        evidence.get("http_status") == 200
        and evidence.get("json_parse_success") is True
        and evidence.get("returned_model") == ROUTE_PROOF_TARGET_MODEL
        and evidence.get("marker_present") is True
        and (evidence.get("done") is True or "done" not in evidence)
    )


def _stdlib_ollama_generate_transport(*, ollama_url: str, request_body: dict[str, Any]) -> dict[str, Any]:
    target_url = ollama_url.rstrip("/") + OLLAMA_GENERATE_PATH
    encoded = json.dumps(request_body).encode("utf-8")
    request = urllib.request.Request(
        target_url,
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        body = response.read().decode("utf-8")
        parsed = json.loads(body)
        return {
            "http_status": response.status,
            "json_parse_success": True,
            "returned_model": parsed.get("model", ""),
            "response_text": parsed.get("response", ""),
            "marker": parsed.get("response", ""),
            "done": parsed.get("done"),
            "done_reason": parsed.get("done_reason"),
        }


def review_route_mediated_provider_smoke_capture(
    captured_result: dict[str, Any],
) -> RouteMediatedProviderSmokeResult:
    """Review caller-supplied captured route-smoke data without executing it."""

    if captured_result.get("production_readiness") is True:
        packet_review = review_route_path_proof_capture(captured_result)
        artifact = _artifact_from_capture(
            captured_result,
            route_path_packet_review={
                **packet_review.to_dict(),
                "status": "FAIL",
                "classification": "production_readiness_claim_rejected",
            },
            accepted=False,
            classification="production_readiness_claim_rejected",
        )
        return RouteMediatedProviderSmokeResult(
            accepted=False,
            classification="production_readiness_claim_rejected",
            artifact=artifact,
            payload=route_mediated_provider_smoke_artifact_to_dict(artifact),
        )

    packet_review = review_route_path_proof_capture(captured_result)
    accepted = packet_review.accepted
    classification = (
        "route_mediated_provider_smoke_shape_valid_review_only"
        if accepted
        else packet_review.classification
    )
    artifact = _artifact_from_capture(
        captured_result,
        route_path_packet_review=packet_review.to_dict(),
        accepted=accepted,
        classification=classification,
    )
    return RouteMediatedProviderSmokeResult(
        accepted=accepted,
        classification=classification,
        artifact=artifact,
        payload=route_mediated_provider_smoke_artifact_to_dict(artifact),
    )


def _artifact_from_capture(
    captured_result: dict[str, Any],
    *,
    route_path_packet_review: dict[str, Any],
    accepted: bool,
    classification: str,
) -> RouteMediatedProviderSmokeArtifact:
    missing_value = "missing_from_caller_supplied_capture"
    evidence = {
        field: captured_result.get(field, missing_value)
        for field in REQUIRED_FUTURE_PROOF_FIELDS
    }
    artifact = RouteMediatedProviderSmokeArtifact(
        phase=PHASE,
        artifact_kind=ARTIFACT_KIND,
        mode="caller_supplied_capture_review_only",
        route_marker=str(captured_result.get("marker", "")),
        prompt=PROMPT,
        target_model=ROUTE_PROOF_TARGET_MODEL,
        disallowed_model=DISALLOWED_MODEL,
        fallback_candidate=FALLBACK_CANDIDATE,
        ollama_url=str(captured_result.get("ollama_url", "not_applicable_capture_review_only")),
        request_body_redacted_or_safe=captured_result.get(
            "request_body_redacted_or_safe",
            "not_applicable_capture_review_only",
        ),
        request_intake_harness_evidence=evidence["request_intake_harness_evidence"],
        route_recommendation_readiness_evidence=evidence["route_recommendation_readiness_evidence"],
        explicit_route_execution_boundary_evidence=evidence["explicit_route_execution_boundary_evidence"],
        provider_call_through_route_path_evidence=evidence["provider_call_through_route_path_evidence"],
        captured_http_status_json_model_marker_evidence=evidence["captured_http_status_json_model_marker_evidence"],
        persisted_artifact_path_evidence=evidence["persisted_artifact_path_evidence"],
        displayed_reviewable_outcome_evidence=evidence["displayed_reviewable_outcome_evidence"],
        route_path_packet_review={
            **route_path_packet_review,
            "runner_classification": classification,
            "runner_accepted": accepted,
        },
        phase_206_runner_review="capture_review_only",
        phase_208_adapter_review="not_applicable_capture_review_only",
        non_proofs=_dedupe(ROUTE_MEDIATED_PROVIDER_SMOKE_NON_PROOFS + tuple(route_path_packet_review.get("non_proofs", ()))),
        activity_flags=_flags(caller_supplied_capture_reviewed=True),
        route_execution_allowed=False,
        provider_execution_allowed=False,
        generation_allowed=False,
        production_readiness=False,
    )
    return artifact


def reject_future_runtime_execution_request(*, allow_provider_call: bool = False) -> RouteMediatedProviderSmokeResult:
    """Reject future runtime execution flags during Phase 206."""

    artifact = build_route_mediated_provider_smoke_dry_artifact().artifact
    rejected = RouteMediatedProviderSmokeArtifact(
        **{
            **asdict(artifact),
            "mode": "future_runtime_execution_rejected_by_phase_206",
            "route_path_packet_review": {
                "status": "FAIL",
                "classification": "future_runtime_execution_not_authorized_by_phase_206",
                "allow_provider_call_requested": allow_provider_call,
            },
            "activity_flags": _flags(future_runtime_execution_requested=True),
        }
    )
    return RouteMediatedProviderSmokeResult(
        accepted=False,
        classification="future_runtime_execution_not_authorized_by_phase_206",
        artifact=rejected,
        payload=route_mediated_provider_smoke_artifact_to_dict(rejected),
    )


def route_mediated_provider_smoke_artifact_to_dict(
    artifact: RouteMediatedProviderSmokeArtifact,
) -> dict[str, Any]:
    """Return a JSON-safe route-mediated smoke artifact payload."""

    payload = asdict(artifact)
    payload["non_proofs"] = list(artifact.non_proofs)
    payload["activity_flags"] = dict(artifact.activity_flags)
    payload["route_path_packet_review"] = dict(artifact.route_path_packet_review)
    return payload


def write_route_mediated_provider_smoke_artifact(
    output_path: str | Path,
    *,
    captured_result: dict[str, Any] | None = None,
) -> RouteMediatedProviderSmokeResult:
    """Write a dry/review artifact to a caller-supplied path or directory."""

    result = (
        review_route_mediated_provider_smoke_capture(captured_result)
        if captured_result is not None
        else build_route_mediated_provider_smoke_dry_artifact()
    )
    return _write_result_payload(result, output_path, "phase_206_route_mediated_provider_smoke_artifact.json")


def _write_result_payload(
    result: RouteMediatedProviderSmokeResult,
    output_path: str | Path,
    default_filename: str,
) -> RouteMediatedProviderSmokeResult:
    target = Path(output_path)
    if target.exists() and target.is_dir():
        target = target / default_filename
    elif not target.suffix:
        target.mkdir(parents=True, exist_ok=True)
        target = target / default_filename
    else:
        target.parent.mkdir(parents=True, exist_ok=True)

    payload = dict(result.payload)
    payload["activity_flags"] = dict(payload["activity_flags"])
    payload["activity_flags"]["artifact_persisted"] = True
    payload["persisted_artifact_path_evidence"] = {"path": str(target)}
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return RouteMediatedProviderSmokeResult(
        accepted=result.accepted,
        classification=result.classification,
        artifact=result.artifact,
        payload=payload,
        written_path=str(target),
    )
