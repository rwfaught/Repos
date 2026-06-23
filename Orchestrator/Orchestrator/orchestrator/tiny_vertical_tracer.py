"""Tiny deterministic vertical tracer dry report artifact contract.

This module builds a reviewable dry artifact from the existing in-process
manual review harness. It does not execute providers, models, routes, workers,
runtime surfaces, network calls, exports, packages, cleanup, deletion,
archive, or production behavior.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from orchestrator.manual_review_runner import run_named_fixture_review


PHASE = "PHASE_169"
ARTIFACT_KIND = "tiny_vertical_tracer_dry_report"
DEFAULT_FIXTURE_ID = "safe_direct_answer"
OUTCOME_CLASSIFICATION = "dry_vertical_flow_reviewable_not_executable"

NO_TRACER_ACTIVITY_FLAGS = {
    "provider_selected": False,
    "provider_executed": False,
    "model_selected": False,
    "model_executed": False,
    "generation_performed": False,
    "api_generate_called": False,
    "api_show_called": False,
    "api_chat_called": False,
    "api_tags_called": False,
    "runtime_executed": False,
    "platform_executed": False,
    "route_executed": False,
    "worker_dispatched": False,
    "codex_dispatched": False,
    "rag_lookup_performed": False,
    "web_lookup_performed": False,
    "scheduler_executed": False,
    "connector_executed": False,
    "wsl_executed": False,
    "openclaw_executed": False,
    "hermes_executed": False,
    "discord_executed": False,
    "export_performed": False,
    "package_performed": False,
    "cleanup_performed": False,
    "deletion_performed": False,
    "archive_performed": False,
    "production_executed": False,
    "dry_artifact_persisted": False,
}

TRACER_NON_PROOFS = (
    "tiny_vertical_tracer_is_not_provider_execution",
    "tiny_vertical_tracer_is_not_model_execution",
    "tiny_vertical_tracer_is_not_route_execution",
    "tiny_vertical_tracer_is_not_worker_dispatch",
    "tiny_vertical_tracer_is_not_runtime_probe",
    "tiny_vertical_tracer_is_not_ollama_call",
    "tiny_vertical_tracer_is_not_export_or_package",
    "tiny_vertical_tracer_is_not_production_readiness",
)


@dataclass(frozen=True)
class TinyVerticalTracerDryReport:
    phase: str
    artifact_kind: str
    artifact_id: str
    fixture_id: str
    request_id: str
    request_type: str
    pipeline_stage: str
    route_admission: str
    recommended_route: str
    provider_catalog_key: str
    provider_evidence_status: str
    provider_evidence_keys: tuple[str, ...]
    provider_evidence_source_phases: tuple[str, ...]
    model_metadata_evidence_name: str
    route_selection_readiness: str
    readiness_status: str
    next_required_boundary: str
    next_required_proof: str
    outcome_classification: str
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
    vertical_sequence: tuple[str, ...]
    coordinator_review_report_id: str
    coordinator_review_text: str


@dataclass(frozen=True)
class TinyVerticalTracerDryReportResult:
    accepted: bool
    report: TinyVerticalTracerDryReport
    payload: dict[str, Any]
    rendered_text: str
    written_path: str | None = None


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _all_false_flags(*flag_sets: dict[str, bool]) -> dict[str, bool]:
    flags = dict(NO_TRACER_ACTIVITY_FLAGS)
    for flag_set in flag_sets:
        for key, value in flag_set.items():
            flags[key] = flags.get(key, False) or bool(value)
    return flags


def build_tiny_vertical_tracer_dry_report(
    fixture_id: str = DEFAULT_FIXTURE_ID,
) -> TinyVerticalTracerDryReportResult:
    """Build a deterministic dry report from the existing review harness."""

    review_result = run_named_fixture_review(fixture_id)
    if review_result.review_report_result is None:
        raise ValueError("fixture did not produce a coordinator review report")

    coordinator_report = review_result.review_report_result.report
    router = coordinator_report.router_policy_recommendation
    readiness = coordinator_report.route_selection_readiness_summary
    provider_evidence = coordinator_report.provider_evidence_summary

    flags = _all_false_flags(
        review_result.no_activity_flags,
        coordinator_report.no_activity_flags,
        router.get("activity_flags", {}),
        router.get("provider_evidence_activity_flags", {}),
        readiness.get("activity_flags", {}),
        provider_evidence.get("activity_flags", {}),
    )
    accepted_facts = _dedupe(
        tuple(coordinator_report.accepted_facts)
        + (
            f"fixture_id={fixture_id}",
            f"recommended_route={router['recommended_route']}",
            f"provider_catalog_key={router['provider_catalog_key']}",
            f"model_metadata_evidence_name={router['model_metadata_evidence_name']}",
            f"route_selection_readiness={readiness['route_selection_readiness']}",
            "dry_artifact_persistence_requires_caller_supplied_path",
        )
    )
    non_proofs = _dedupe(TRACER_NON_PROOFS + review_result.non_proofs + tuple(coordinator_report.non_proofs))
    caveats = _dedupe(
        review_result.caveats
        + coordinator_report.caveats
        + (
            "dry_report_artifact_only",
            "caller_supplied_persistence_path_only",
        )
    )

    report = TinyVerticalTracerDryReport(
        phase=PHASE,
        artifact_kind=ARTIFACT_KIND,
        artifact_id=f"{PHASE.lower()}_{fixture_id}_dry_report",
        fixture_id=fixture_id,
        request_id=review_result.request_id,
        request_type=review_result.request_type,
        pipeline_stage=coordinator_report.pipeline_stage,
        route_admission=coordinator_report.route_admission,
        recommended_route=router["recommended_route"],
        provider_catalog_key=router["provider_catalog_key"],
        provider_evidence_status=router["provider_evidence_status"],
        provider_evidence_keys=tuple(router["provider_evidence_keys"]),
        provider_evidence_source_phases=tuple(router["provider_evidence_source_phases"]),
        model_metadata_evidence_name=router["model_metadata_evidence_name"],
        route_selection_readiness=readiness["route_selection_readiness"],
        readiness_status=readiness["readiness_status"],
        next_required_boundary=readiness["next_required_boundary"],
        next_required_proof=readiness["next_required_proof"],
        outcome_classification=OUTCOME_CLASSIFICATION,
        accepted_facts=accepted_facts,
        blocked_conditions=_dedupe(
            tuple(review_result.blocked_conditions)
            + tuple(coordinator_report.blocked_conditions)
            + tuple(readiness["blocked_conditions"])
        ),
        missing_requirements=_dedupe(
            tuple(review_result.missing_requirements)
            + tuple(coordinator_report.missing_requirements)
            + tuple(router["missing_requirements"])
        ),
        caveats=caveats,
        non_proofs=non_proofs,
        activity_flags=flags,
        provider_selection_allowed=readiness["provider_selection_allowed"] is True,
        provider_execution_allowed=readiness["provider_execution_allowed"] is True,
        route_execution_allowed=readiness["route_execution_allowed"] is True,
        generation_allowed=readiness["generation_allowed"] is True,
        production_readiness=readiness["production_readiness"] is True,
        vertical_sequence=(
            "fixture/intake/manual review",
            "route recommendation",
            "provider evidence envelope",
            "route-selection readiness",
            "coordinator review report",
            "persisted/reviewable dry artifact",
            "outcome classification",
        ),
        coordinator_review_report_id=coordinator_report.report_id,
        coordinator_review_text=review_result.review_text,
    )
    payload = tiny_vertical_tracer_dry_report_to_dict(report)
    return TinyVerticalTracerDryReportResult(
        accepted=review_result.accepted,
        report=report,
        payload=payload,
        rendered_text=render_tiny_vertical_tracer_dry_report_text(report),
    )


def tiny_vertical_tracer_dry_report_to_dict(report: TinyVerticalTracerDryReport) -> dict[str, Any]:
    """Return a JSON-safe dry report payload."""

    payload = asdict(report)
    for key in (
        "provider_evidence_keys",
        "provider_evidence_source_phases",
        "accepted_facts",
        "blocked_conditions",
        "missing_requirements",
        "caveats",
        "non_proofs",
        "vertical_sequence",
    ):
        payload[key] = list(payload[key])
    payload["activity_flags"] = dict(report.activity_flags)
    return payload


def render_tiny_vertical_tracer_dry_report_text(report: TinyVerticalTracerDryReport) -> str:
    """Render the dry tracer plus the coordinator review sections."""

    lines = [
        "Tiny Vertical Tracer Dry Report",
        f"- phase={report.phase}",
        f"- artifact_kind={report.artifact_kind}",
        f"- fixture_id={report.fixture_id}",
        f"- request_id={report.request_id}",
        f"- request_type={report.request_type}",
        f"- pipeline_stage={report.pipeline_stage}",
        f"- route_admission={report.route_admission}",
        f"- recommended_route={report.recommended_route}",
        f"- provider_catalog_key={report.provider_catalog_key}",
        f"- provider_evidence_status={report.provider_evidence_status}",
        f"- provider_evidence_keys={', '.join(report.provider_evidence_keys)}",
        f"- provider_evidence_source_phases={', '.join(report.provider_evidence_source_phases)}",
        f"- model_metadata_evidence_name={report.model_metadata_evidence_name}",
        f"- route_selection_readiness={report.route_selection_readiness}",
        f"- readiness_status={report.readiness_status}",
        f"- next_required_boundary={report.next_required_boundary}",
        f"- next_required_proof={report.next_required_proof}",
        f"- outcome_classification={report.outcome_classification}",
        f"- provider_selection_allowed={report.provider_selection_allowed}",
        f"- provider_execution_allowed={report.provider_execution_allowed}",
        f"- route_execution_allowed={report.route_execution_allowed}",
        f"- generation_allowed={report.generation_allowed}",
        f"- production_readiness={report.production_readiness}",
        "",
        "Vertical Sequence",
        *[f"- {stage}" for stage in report.vertical_sequence],
        "",
        report.coordinator_review_text,
    ]
    return "\n".join(lines)


def write_tiny_vertical_tracer_dry_report(
    output_path: str | Path,
    fixture_id: str = DEFAULT_FIXTURE_ID,
) -> TinyVerticalTracerDryReportResult:
    """Write the dry report JSON to a caller-supplied path or directory."""

    result = build_tiny_vertical_tracer_dry_report(fixture_id)
    target = Path(output_path)
    if target.exists() and target.is_dir():
        target = target / f"{result.report.artifact_id}.json"
    elif not target.suffix:
        target.mkdir(parents=True, exist_ok=True)
        target = target / f"{result.report.artifact_id}.json"
    else:
        target.parent.mkdir(parents=True, exist_ok=True)

    payload = dict(result.payload)
    payload["persistence_classification"] = "test_dry_artifact_persistence_not_route_execution"
    payload["activity_flags"] = dict(payload["activity_flags"])
    payload["activity_flags"]["dry_artifact_persisted"] = True
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return TinyVerticalTracerDryReportResult(
        accepted=result.accepted,
        report=result.report,
        payload=payload,
        rendered_text=result.rendered_text,
        written_path=str(target),
    )
