"""Deterministic route-path proof packet contract.

This module defines the smallest future proof boundary needed to move from
direct captured provider marker smoke to route-mediated provider marker smoke.
It never executes a route, provider, model, worker, runtime surface, network
endpoint, platform, connector, scheduler, service, UI, or production behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


PHASE = "PHASE_202"
ARTIFACT_KIND = "route_path_proof_packet_contract"
PRIOR_DIRECT_MARKER_PROOF_PHASE = "PHASE_194"
PRIOR_DIRECT_MARKER = "ORCH_PROVIDER_SMOKE_OK"
ROUTE_PROOF_TARGET_MODEL = "qwen3:30b-a3b-instruct-2507-q4_K_M"
DISALLOWED_MODEL = "qwen3.6:35b-a3b"
FALLBACK_CANDIDATE = "qwen3.6:27b"
FUTURE_ROUTE_MARKER = "ORCH_ROUTE_PROVIDER_SMOKE_OK"
FUTURE_BOUNDARY = "future_route_mediated_provider_marker_smoke_operator_proof"
FUTURE_PROOF = "request_to_route_to_provider_to_artifact_to_reviewable_outcome"


REQUIRED_FUTURE_PROOF_FIELDS = (
    "request_intake_harness_evidence",
    "route_recommendation_readiness_evidence",
    "explicit_route_execution_boundary_evidence",
    "provider_call_through_route_path_evidence",
    "captured_http_status_json_model_marker_evidence",
    "persisted_artifact_path_evidence",
    "displayed_reviewable_outcome_evidence",
)

ROUTE_PATH_PROOF_NON_PROOFS = (
    "packet_contract_is_not_route_execution",
    "route_recommendation_is_not_execution",
    "provider_target_string_is_not_model_execution",
    "prior_direct_provider_smoke_is_not_route_mediated_proof",
    "no_api_chat_proof",
    "no_semantic_correctness_proof",
    "no_real_workload_sufficiency_proof",
    "no_long_context_proof",
    "no_sustained_load_proof",
    "no_production_readiness_proof",
    "no_hermes_openclaw_behavior_proof",
)

NO_ROUTE_PATH_PROOF_ACTIVITY_FLAGS = {
    "request_intake_executed": False,
    "route_recommended": False,
    "route_readiness_executed": False,
    "route_executed": False,
    "provider_selected": False,
    "provider_executed": False,
    "model_selected": False,
    "model_executed": False,
    "generation_performed": False,
    "api_generate_called": False,
    "api_chat_called": False,
    "api_tags_called": False,
    "api_version_called": False,
    "runtime_executed": False,
    "platform_executed": False,
    "worker_dispatched": False,
    "codex_dispatched": False,
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
class RoutePathProofPacket:
    phase: str
    artifact_kind: str
    prior_direct_marker_proof_phase: str
    route_proof_target_model: str
    disallowed_model: str
    fallback_candidate: str
    prior_direct_marker: str
    future_route_marker: str
    future_boundary: str
    future_required_proof: str
    required_future_proof_fields: tuple[str, ...]
    accepted_facts: tuple[str, ...]
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    caveats: tuple[str, ...]
    non_proofs: tuple[str, ...]
    activity_flags: dict[str, bool]
    route_execution_allowed: bool
    provider_execution_allowed: bool
    generation_allowed: bool
    production_readiness: bool


@dataclass(frozen=True)
class RoutePathProofReview:
    status: str
    classification: str
    accepted: bool
    accepted_facts: tuple[str, ...]
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    caveats: tuple[str, ...]
    non_proofs: tuple[str, ...]
    route_execution_allowed: bool
    provider_execution_allowed: bool
    generation_allowed: bool
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


def build_route_path_proof_packet() -> RoutePathProofPacket:
    """Build the deterministic future route-path proof packet without execution."""

    accepted_facts = (
        f"phase={PHASE}",
        f"artifact_kind={ARTIFACT_KIND}",
        f"prior_direct_marker_proof_phase={PRIOR_DIRECT_MARKER_PROOF_PHASE}",
        f"route_proof_target_model={ROUTE_PROOF_TARGET_MODEL}",
        f"disallowed_model={DISALLOWED_MODEL}",
        f"fallback_candidate={FALLBACK_CANDIDATE}",
        f"prior_direct_marker={PRIOR_DIRECT_MARKER}",
        f"future_route_marker={FUTURE_ROUTE_MARKER}",
        f"future_boundary={FUTURE_BOUNDARY}",
        f"future_required_proof={FUTURE_PROOF}",
        "phase_190_30b_viability_only",
        "phase_194_direct_product_marker_smoke_only",
        "phase_194_classification=captured_marker_smoke_pass_not_route_execution",
        "phase_194_retry3_classifier_artifact_backfill_accepted",
    )
    missing_requirements = (
        "request_intake_harness_evidence_missing_until_future_boundary",
        "route_recommendation_readiness_evidence_missing_until_future_boundary",
        "explicit_route_execution_boundary_evidence_missing_until_future_boundary",
        "provider_call_through_route_path_evidence_missing_until_future_boundary",
        "captured_http_status_json_model_marker_evidence_missing_until_future_boundary",
        "persisted_artifact_path_evidence_missing_until_future_boundary",
        "displayed_reviewable_outcome_evidence_missing_until_future_boundary",
    )
    caveats = (
        "route_path_packet_contract_only",
        "phase_194_direct_provider_marker_smoke_is_not_route_mediated_proof",
        "future_route_marker_distinct_from_direct_provider_marker",
        "qwen36_35b_a3b_disallowed_due_to_roger_operational_lockup_evidence",
        "qwen36_27b_remains_fallback_candidate",
        "current_success_criterion_not_met_for_route_mediated_provider_execution",
    )
    return RoutePathProofPacket(
        phase=PHASE,
        artifact_kind=ARTIFACT_KIND,
        prior_direct_marker_proof_phase=PRIOR_DIRECT_MARKER_PROOF_PHASE,
        route_proof_target_model=ROUTE_PROOF_TARGET_MODEL,
        disallowed_model=DISALLOWED_MODEL,
        fallback_candidate=FALLBACK_CANDIDATE,
        prior_direct_marker=PRIOR_DIRECT_MARKER,
        future_route_marker=FUTURE_ROUTE_MARKER,
        future_boundary=FUTURE_BOUNDARY,
        future_required_proof=FUTURE_PROOF,
        required_future_proof_fields=REQUIRED_FUTURE_PROOF_FIELDS,
        accepted_facts=accepted_facts,
        blocked_conditions=("future_route_mediated_operator_boundary_required",),
        missing_requirements=missing_requirements,
        caveats=caveats,
        non_proofs=ROUTE_PATH_PROOF_NON_PROOFS,
        activity_flags=dict(NO_ROUTE_PATH_PROOF_ACTIVITY_FLAGS),
        route_execution_allowed=False,
        provider_execution_allowed=False,
        generation_allowed=False,
        production_readiness=False,
    )


def route_path_proof_packet_to_dict(packet: RoutePathProofPacket) -> dict[str, Any]:
    """Return a JSON-safe packet payload."""

    payload = asdict(packet)
    for key in (
        "required_future_proof_fields",
        "accepted_facts",
        "blocked_conditions",
        "missing_requirements",
        "caveats",
        "non_proofs",
    ):
        payload[key] = list(payload[key])
    payload["activity_flags"] = dict(packet.activity_flags)
    return payload


def review_route_path_proof_capture(captured_result: dict[str, Any]) -> RoutePathProofReview:
    """Review caller-supplied future proof facts without executing anything."""

    required_fields = REQUIRED_FUTURE_PROOF_FIELDS + ("marker", "returned_model")
    missing = tuple(field for field in required_fields if field not in captured_result)
    if missing:
        return _review(
            status="FAIL",
            classification="missing_route_mediated_proof_fields",
            accepted=False,
            blocked_conditions=("route_mediated_proof_incomplete",),
            missing_requirements=tuple(f"missing_{field}" for field in missing),
        )

    if captured_result.get("marker") == PRIOR_DIRECT_MARKER:
        return _review(
            status="FAIL",
            classification="direct_provider_marker_not_route_mediated_proof",
            accepted=False,
            accepted_facts=(f"marker={captured_result['marker']}",),
            blocked_conditions=("direct_provider_smoke_overclaim_rejected",),
            missing_requirements=("distinct_route_mediated_marker_required",),
        )

    if captured_result.get("marker") != FUTURE_ROUTE_MARKER:
        return _review(
            status="FAIL",
            classification="wrong_route_marker",
            accepted=False,
            accepted_facts=(f"marker={captured_result.get('marker')}",),
            blocked_conditions=("route_marker_mismatch",),
        )

    if captured_result.get("returned_model") != ROUTE_PROOF_TARGET_MODEL:
        return _review(
            status="FAIL",
            classification="wrong_route_model",
            accepted=False,
            accepted_facts=(f"returned_model={captured_result.get('returned_model')}",),
            blocked_conditions=("route_model_mismatch",),
        )

    return _review(
        status="PASS",
        classification="route_mediated_marker_smoke_shape_review_only",
        accepted=True,
        accepted_facts=(
            f"marker={FUTURE_ROUTE_MARKER}",
            f"returned_model={ROUTE_PROOF_TARGET_MODEL}",
            "route_mediated_proof_fields_present",
        ),
        caveats=("review_only_does_not_execute_route",),
    )


def _review(
    *,
    status: str,
    classification: str,
    accepted: bool,
    accepted_facts: tuple[str, ...] = (),
    blocked_conditions: tuple[str, ...] = (),
    missing_requirements: tuple[str, ...] = (),
    caveats: tuple[str, ...] = (),
) -> RoutePathProofReview:
    return RoutePathProofReview(
        status=status,
        classification=classification,
        accepted=accepted,
        accepted_facts=_dedupe(accepted_facts),
        blocked_conditions=_dedupe(blocked_conditions),
        missing_requirements=_dedupe(missing_requirements),
        caveats=_dedupe(("captured_result_review_only",) + caveats),
        non_proofs=ROUTE_PATH_PROOF_NON_PROOFS,
        route_execution_allowed=False,
        provider_execution_allowed=False,
        generation_allowed=False,
        production_readiness=False,
    )
