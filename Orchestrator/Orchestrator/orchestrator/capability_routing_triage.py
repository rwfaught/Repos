"""Deterministic, local-first capability routing triage.

This module recommends an executor posture from explicit task requirements. It
does not call a model, provider, API, runtime, worker, or external service.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import Any


ROUTES = (
    "deterministic_code_only",
    "local_model_candidate",
    "frontier_model_or_codex_required",
    "external_api_required",
    "human_review_or_blocked",
)

EXPLICIT_NON_PROOFS = (
    "not model execution",
    "not provider or API execution",
    "not Qwen 3.6 27B loadability or competence proof",
    "not Codex or frontier-model execution",
    "not route authorization or dispatch",
    "not semantic correctness",
    "not production readiness",
    "not product-wedge selection",
    "not Phase 387 resumption",
)

_ALLOWED_VALUES = {
    "complexity": {"simple", "moderate", "high"},
    "safety_risk": {"low", "medium", "high", "critical"},
    "privacy_sensitivity": {"public", "internal", "sensitive", "regulated"},
    "tolerance_for_mistakes": {"high", "medium", "low", "zero"},
}


@dataclass(frozen=True)
class CapabilityTriageTask:
    task_id: str
    title: str
    objective: str
    complexity: str
    code_generation_required: bool
    long_context_required: bool
    safety_risk: str
    privacy_sensitivity: str
    external_tool_or_api_need: bool
    live_runtime_execution_need: bool
    tolerance_for_mistakes: str
    deterministic_validation_available: bool
    local_model_output_reviewable: bool


def _normalize_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _coerce_task(value: CapabilityTriageTask | dict[str, Any]) -> CapabilityTriageTask | None:
    if isinstance(value, CapabilityTriageTask):
        return value
    if not isinstance(value, dict):
        return None
    return CapabilityTriageTask(
        task_id=_normalize_text(value.get("task_id")),
        title=_normalize_text(value.get("title")),
        objective=_normalize_text(value.get("objective")),
        complexity=_normalize_text(value.get("complexity")).lower(),
        code_generation_required=value.get("code_generation_required") is True,
        long_context_required=value.get("long_context_required") is True,
        safety_risk=_normalize_text(value.get("safety_risk")).lower(),
        privacy_sensitivity=_normalize_text(value.get("privacy_sensitivity")).lower(),
        external_tool_or_api_need=value.get("external_tool_or_api_need") is True,
        live_runtime_execution_need=value.get("live_runtime_execution_need") is True,
        tolerance_for_mistakes=_normalize_text(value.get("tolerance_for_mistakes")).lower(),
        deterministic_validation_available=value.get("deterministic_validation_available") is True,
        local_model_output_reviewable=value.get("local_model_output_reviewable") is True,
    )


def _missing_or_invalid(task: CapabilityTriageTask) -> tuple[list[str], list[str]]:
    missing = [
        field for field in ("task_id", "title", "objective", "complexity", "safety_risk",
                            "privacy_sensitivity", "tolerance_for_mistakes")
        if not getattr(task, field)
    ]
    invalid = [
        f"{field}_invalid" for field, allowed in _ALLOWED_VALUES.items()
        if getattr(task, field) not in allowed
    ]
    return missing, invalid


def _recommend(
    task: CapabilityTriageTask | None,
    *,
    route: str,
    rationale: str,
    next_action: str,
    blockers: tuple[str, ...] = (),
    missing: tuple[str, ...] = (),
) -> dict[str, Any]:
    assert route in ROUTES
    task_data = asdict(task) if task is not None else {}
    return {
        "task": task_data,
        "route": route,
        "rationale": rationale,
        "next_bounded_action": next_action,
        "blocked_or_deferred_conditions": list(blockers),
        "missing_or_invalid_requirements": list(missing),
        "recommendation_before_execution": True,
        "execution_authorized": False,
        "local_first_posture": True,
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def classify_capability_task(
    task: CapabilityTriageTask | dict[str, Any],
) -> dict[str, Any]:
    """Return a deterministic capability route and operator next action."""
    normalized = _coerce_task(task)
    if normalized is None:
        return _recommend(
            None,
            route="human_review_or_blocked",
            rationale="A structured capability triage task is required before routing.",
            next_action="provide the required task capability fields for owner review",
            blockers=("unstructured_task_requirements",),
            missing=("structured_task",),
        )

    missing, invalid = _missing_or_invalid(normalized)
    if missing or invalid:
        return _recommend(
            normalized,
            route="human_review_or_blocked",
            rationale="Routing is underdetermined because required capability fields are missing or invalid.",
            next_action="clarify the missing or invalid capability fields before selecting an executor",
            blockers=("capability_triage_underdetermined",),
            missing=tuple(missing + invalid),
        )

    if normalized.safety_risk in {"high", "critical"} or normalized.privacy_sensitivity == "regulated":
        return _recommend(
            normalized,
            route="human_review_or_blocked",
            rationale="High-consequence or regulated work requires owner review before any model or executor recommendation can advance.",
            next_action="owner reviews the risk, privacy boundary, source material, and stop conditions",
            blockers=("high_consequence_review_required",),
        )

    if normalized.external_tool_or_api_need:
        return _recommend(
            normalized,
            route="external_api_required",
            rationale="The task depends on an external tool or API that is outside this local-only triage boundary.",
            next_action="defer integration work and draft a separate owner-approved external-service boundary",
            blockers=("external_service_boundary_required",),
        )

    if normalized.live_runtime_execution_need:
        return _recommend(
            normalized,
            route="human_review_or_blocked",
            rationale="Live runtime execution is required, but runtime authority is not granted by capability triage.",
            next_action="owner decides whether to authorize a separate runtime execution boundary",
            blockers=("live_runtime_boundary_required",),
        )

    if normalized.code_generation_required and (
        normalized.complexity == "high"
        or normalized.long_context_required
        or not normalized.deterministic_validation_available
        or normalized.tolerance_for_mistakes == "zero"
    ):
        return _recommend(
            normalized,
            route="frontier_model_or_codex_required",
            rationale="The task combines code generation with high complexity, long context, weak deterministic validation, or zero mistake tolerance.",
            next_action="prepare a bounded architecture/coding review packet for explicit frontier or Codex authorization",
            blockers=("stronger_reasoning_boundary_recommended",),
        )

    if (
        normalized.complexity == "simple"
        and not normalized.code_generation_required
        and not normalized.long_context_required
        and normalized.deterministic_validation_available
    ):
        return _recommend(
            normalized,
            route="deterministic_code_only",
            rationale="The task is simple, locally bounded, and has deterministic validation available, so model generation adds unnecessary risk and cost.",
            next_action="run or prepare the deterministic local check and return its inspectable result",
        )

    if normalized.local_model_output_reviewable:
        return _recommend(
            normalized,
            route="local_model_candidate",
            rationale="The task is moderate-risk, does not require external execution, and any local-model draft can be reviewed before action.",
            next_action="prepare a redacted local-model attempt packet with human review before use",
            blockers=("local_model_attempt_requires_separate_authorized_boundary",),
        )

    return _recommend(
        normalized,
        route="human_review_or_blocked",
        rationale="The task lacks a safe reviewable local output path under the stated requirements.",
        next_action="owner clarifies the review boundary or reframes the task into a deterministic local step",
        blockers=("reviewability_requirement_not_met",),
    )


def build_capability_routing_fixture_library() -> dict[str, dict[str, Any]]:
    """Return five deterministic fixtures spanning the route decisions."""
    return {
        "simple_deterministic_classification": {
            "task_id": "simple_deterministic_classification",
            "title": "Classify a supplied status list",
            "objective": "Map each supplied status to one of three fixed labels.",
            "complexity": "simple",
            "code_generation_required": False,
            "long_context_required": False,
            "safety_risk": "low",
            "privacy_sensitivity": "internal",
            "external_tool_or_api_need": False,
            "live_runtime_execution_need": False,
            "tolerance_for_mistakes": "medium",
            "deterministic_validation_available": True,
            "local_model_output_reviewable": True,
        },
        "local_model_drafting_candidate": {
            "task_id": "local_model_drafting_candidate",
            "title": "Draft a reviewed internal summary",
            "objective": "Summarize supplied redacted notes into a draft owner-facing brief.",
            "complexity": "moderate",
            "code_generation_required": False,
            "long_context_required": False,
            "safety_risk": "low",
            "privacy_sensitivity": "internal",
            "external_tool_or_api_need": False,
            "live_runtime_execution_need": False,
            "tolerance_for_mistakes": "medium",
            "deterministic_validation_available": False,
            "local_model_output_reviewable": True,
        },
        "frontier_coding_architecture": {
            "task_id": "frontier_coding_architecture",
            "title": "Design a cross-module architecture change",
            "objective": "Propose and implement a multi-module migration with compatibility constraints.",
            "complexity": "high",
            "code_generation_required": True,
            "long_context_required": True,
            "safety_risk": "medium",
            "privacy_sensitivity": "internal",
            "external_tool_or_api_need": False,
            "live_runtime_execution_need": False,
            "tolerance_for_mistakes": "low",
            "deterministic_validation_available": False,
            "local_model_output_reviewable": True,
        },
        "sensitive_high_risk_review": {
            "task_id": "sensitive_high_risk_review",
            "title": "Review a regulated decision draft",
            "objective": "Assess a redacted draft that could affect a regulated case outcome.",
            "complexity": "moderate",
            "code_generation_required": False,
            "long_context_required": True,
            "safety_risk": "high",
            "privacy_sensitivity": "regulated",
            "external_tool_or_api_need": False,
            "live_runtime_execution_need": False,
            "tolerance_for_mistakes": "zero",
            "deterministic_validation_available": False,
            "local_model_output_reviewable": True,
        },
        "external_api_integration_deferred": {
            "task_id": "external_api_integration_deferred",
            "title": "Coordinate records across a live CRM API",
            "objective": "Read and reconcile live scheduling records across an external CRM and calendar.",
            "complexity": "moderate",
            "code_generation_required": True,
            "long_context_required": False,
            "safety_risk": "medium",
            "privacy_sensitivity": "internal",
            "external_tool_or_api_need": True,
            "live_runtime_execution_need": True,
            "tolerance_for_mistakes": "low",
            "deterministic_validation_available": False,
            "local_model_output_reviewable": True,
        },
    }


def build_capability_routing_summary() -> dict[str, Any]:
    fixtures = build_capability_routing_fixture_library()
    recommendations = {
        task_id: classify_capability_task(task)
        for task_id, task in fixtures.items()
    }
    route_by_task = {
        task_id: recommendation["route"]
        for task_id, recommendation in recommendations.items()
    }
    return {
        "summary_name": "capability_routing_triage_summary",
        "task_count": len(recommendations),
        "route_by_task": route_by_task,
        "tasks_by_route": {
            route: [task_id for task_id, selected in route_by_task.items() if selected == route]
            for route in ROUTES
        },
        "recommended_next_review_task": "local_model_drafting_candidate",
        "execution_authorized": False,
        "local_first_posture": True,
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def build_capability_routing_review_report(task_id: str) -> dict[str, Any]:
    fixtures = build_capability_routing_fixture_library()
    task = fixtures.get(task_id)
    if task is None:
        return {
            "summary_name": "capability_routing_triage_review_report",
            "task_id": task_id,
            "found": False,
            "available_tasks": sorted(fixtures),
            "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        }
    recommendation = classify_capability_task(task)
    return {
        "summary_name": "capability_routing_triage_review_report",
        "task_id": task_id,
        "found": True,
        "task": deepcopy(task),
        "routing_recommendation": recommendation,
        "capability_factors": {
            key: value for key, value in task.items()
            if key not in {"task_id", "title", "objective"}
        },
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def render_capability_routing_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Capability Routing Triage",
        "",
        f"Task: `{payload.get('task_id', 'summary')}`",
        "Execution authorized: `False`",
    ]
    if payload.get("summary_name") == "capability_routing_triage_summary":
        lines.extend([
            "",
            "## Routing Dashboard",
            f"Tasks reviewed: `{payload['task_count']}`",
            f"Recommended next review: `{payload['recommended_next_review_task']}`",
            "",
            "### Tasks by Route",
            *[
                f"- `{route}`: {', '.join(task_ids) or 'none'}"
                for route, task_ids in payload["tasks_by_route"].items()
            ],
        ])
    elif not payload.get("found", True):
        lines.extend([
            "",
            "Task not found.",
            "Available tasks:",
            *[f"- `{task_id}`" for task_id in payload["available_tasks"]],
        ])
    else:
        task = payload["task"]
        recommendation = payload["routing_recommendation"]
        blocker_lines = [f"- {item}" for item in recommendation["blocked_or_deferred_conditions"]]
        lines.extend([
            "",
            "## Task Summary",
            f"Title: {task['title']}",
            f"Objective: {task['objective']}",
            "",
            "## Routing Decision",
            f"Route: `{recommendation['route']}`",
            f"Rationale: {recommendation['rationale']}",
            f"Next bounded action: {recommendation['next_bounded_action']}",
            "",
            "## Capability Factors",
            *[f"- {key}: `{value}`" for key, value in payload["capability_factors"].items()],
            "",
            "## Blockers or Deferrals",
            *(blocker_lines or ["- none"]),
        ])
    lines.extend([
        "",
        "## Explicit Non-Proofs",
        *[f"- {item}" for item in payload["explicit_non_proofs"]],
    ])
    return "\n".join(lines)
