"""Deterministic route-mediated provider smoke runner contract.

This module prepares dry artifact shapes and reviews caller-supplied captured
results for a future route-mediated provider smoke proof. It never executes a
route, provider, model, runtime surface, HTTP endpoint, worker, platform,
connector, scheduler, service, UI, or production behavior.
"""

from __future__ import annotations

import json
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
PROMPT = f"Return exactly: {FUTURE_ROUTE_MARKER}"
DEFAULT_MODE = "dry_artifact_shape_only"


ROUTE_MEDIATED_PROVIDER_SMOKE_NON_PROOFS = (
    "route_mediated_provider_smoke_runner_is_not_route_execution",
    "route_mediated_provider_smoke_runner_is_not_provider_execution",
    "route_mediated_provider_smoke_runner_is_not_model_execution",
    "route_mediated_provider_smoke_runner_is_not_runtime_execution",
    "route_mediated_provider_smoke_runner_is_not_http_or_ollama_call",
    "route_mediated_provider_smoke_runner_is_not_worker_dispatch",
    "route_mediated_provider_smoke_runner_is_not_production_readiness",
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
    request_intake_harness_evidence: Any
    route_recommendation_readiness_evidence: Any
    explicit_route_execution_boundary_evidence: Any
    provider_call_through_route_path_evidence: Any
    captured_http_status_json_model_marker_evidence: Any
    persisted_artifact_path_evidence: Any
    displayed_reviewable_outcome_evidence: Any
    route_path_packet_review: dict[str, Any]
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
        request_intake_harness_evidence=pending,
        route_recommendation_readiness_evidence=pending,
        explicit_route_execution_boundary_evidence=pending,
        provider_call_through_route_path_evidence=pending,
        captured_http_status_json_model_marker_evidence=pending,
        persisted_artifact_path_evidence=pending,
        displayed_reviewable_outcome_evidence=pending,
        route_path_packet_review=packet_payload,
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
    target = Path(output_path)
    if target.exists() and target.is_dir():
        target = target / "phase_206_route_mediated_provider_smoke_artifact.json"
    elif not target.suffix:
        target.mkdir(parents=True, exist_ok=True)
        target = target / "phase_206_route_mediated_provider_smoke_artifact.json"
    else:
        target.parent.mkdir(parents=True, exist_ok=True)

    payload = dict(result.payload)
    payload["activity_flags"] = dict(payload["activity_flags"])
    payload["activity_flags"]["artifact_persisted"] = True
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return RouteMediatedProviderSmokeResult(
        accepted=result.accepted,
        classification=result.classification,
        artifact=result.artifact,
        payload=payload,
        written_path=str(target),
    )
