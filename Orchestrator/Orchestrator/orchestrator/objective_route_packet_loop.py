"""Objective-to-route-to-owner-packet loop for the local-first V1 candidate."""

from __future__ import annotations

import hashlib
import re
from copy import deepcopy
from typing import Any

from orchestrator.capability_routing_triage import (
    EXPLICIT_NON_PROOFS as ROUTING_NON_PROOFS,
    CapabilityTriageTask,
    classify_capability_task,
)
from orchestrator.dossier_case_mapping import adapt_case_packet_to_dossier_case
from orchestrator.dossier_case_task_readiness import build_neutral_task_readiness_report_dict


LOOP_NON_PROOFS = tuple(dict.fromkeys(ROUTING_NON_PROOFS + (
    "not natural-language intent understanding",
    "not arbitrary objective admission",
    "not owner approval",
    "not packet persistence",
)))

_SIGNALS = {
    "deterministic": ("classify", "count", "sort", "validate", "check", "parse", "fixed labels"),
    "local_model": ("summarize", "summary", "draft", "rewrite", "outline", "notes", "policy", "brief", "staff review"),
    "frontier": ("architect", "architecture", "multi-module", "refactor", "migration", "compatibility", "complex code"),
    "external": ("api", "crm", "calendar", "integrat", "live system", "database", "send", "sync", "dispatch"),
    "human": ("regulated", "medical", "legal", "financial decision", "high stakes", "sensitive", "personal data"),
}


def _objective_id(objective: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", objective.lower()).strip("-")[:32] or "untitled"
    digest = hashlib.sha1(objective.encode("utf-8")).hexdigest()[:8]
    return f"objective-{slug}-{digest}"


def _contains_signal(text: str, signal: str) -> bool:
    return signal in text


def infer_objective_capability_task(objective: str) -> dict[str, Any]:
    """Convert objective text into explicit triage metadata using fixed signals."""
    normalized = " ".join(str(objective or "").lower().split())
    matched = {
        category: [signal for signal in signals if _contains_signal(normalized, signal)]
        for category, signals in _SIGNALS.items()
    }
    matched = {category: signals for category, signals in matched.items() if signals}

    if not normalized:
        return {
            "objective": "",
            "objective_id": "",
            "inference_mode": "empty_objective_blocked",
            "matched_signals": {},
            "capability_task": None,
            "clarification_needed": ["objective_text"],
        }

    title = objective.strip().rstrip(".")[:90]
    task_id = _objective_id(objective)
    categories = set(matched)
    if "human" in categories:
        task = CapabilityTriageTask(
            task_id=task_id, title=title, objective=objective, complexity="moderate",
            code_generation_required=False, long_context_required=True,
            safety_risk="high", privacy_sensitivity="regulated" if "regulated" in normalized else "sensitive",
            external_tool_or_api_need="external" in categories, live_runtime_execution_need=False,
            tolerance_for_mistakes="zero", deterministic_validation_available=False,
            local_model_output_reviewable=True,
        )
        mode = "fixed_signal_inference_high_consequence"
    elif "external" in categories:
        task = CapabilityTriageTask(
            task_id=task_id, title=title, objective=objective, complexity="moderate",
            code_generation_required=True, long_context_required=False,
            safety_risk="medium", privacy_sensitivity="internal",
            external_tool_or_api_need=True, live_runtime_execution_need=True,
            tolerance_for_mistakes="low", deterministic_validation_available=False,
            local_model_output_reviewable=True,
        )
        mode = "fixed_signal_inference_external_dependency"
    elif "frontier" in categories:
        task = CapabilityTriageTask(
            task_id=task_id, title=title, objective=objective, complexity="high",
            code_generation_required=True, long_context_required=True,
            safety_risk="medium", privacy_sensitivity="internal",
            external_tool_or_api_need=False, live_runtime_execution_need=False,
            tolerance_for_mistakes="low", deterministic_validation_available=False,
            local_model_output_reviewable=True,
        )
        mode = "fixed_signal_inference_complex_coding"
    elif "deterministic" in categories and "local_model" not in categories:
        task = CapabilityTriageTask(
            task_id=task_id, title=title, objective=objective, complexity="simple",
            code_generation_required=False, long_context_required=False,
            safety_risk="low", privacy_sensitivity="internal",
            external_tool_or_api_need=False, live_runtime_execution_need=False,
            tolerance_for_mistakes="medium", deterministic_validation_available=True,
            local_model_output_reviewable=True,
        )
        mode = "fixed_signal_inference_deterministic"
    elif "local_model" in categories:
        task = CapabilityTriageTask(
            task_id=task_id, title=title, objective=objective, complexity="moderate",
            code_generation_required=False, long_context_required=False,
            safety_risk="low", privacy_sensitivity="internal",
            external_tool_or_api_need=False, live_runtime_execution_need=False,
            tolerance_for_mistakes="medium", deterministic_validation_available=False,
            local_model_output_reviewable=True,
        )
        mode = "fixed_signal_inference_reviewable_drafting"
    else:
        return {
            "objective": objective,
            "objective_id": task_id,
            "inference_mode": "insufficient_fixed_signals",
            "matched_signals": {},
            "capability_task": None,
            "clarification_needed": ["task_type", "risk_and_privacy_posture", "reviewability"],
        }

    return {
        "objective": objective,
        "objective_id": task_id,
        "inference_mode": mode,
        "matched_signals": matched,
        "capability_task": {
            "task_id": task.task_id,
            "title": task.title,
            "objective": task.objective,
            "complexity": task.complexity,
            "code_generation_required": task.code_generation_required,
            "long_context_required": task.long_context_required,
            "safety_risk": task.safety_risk,
            "privacy_sensitivity": task.privacy_sensitivity,
            "external_tool_or_api_need": task.external_tool_or_api_need,
            "live_runtime_execution_need": task.live_runtime_execution_need,
            "tolerance_for_mistakes": task.tolerance_for_mistakes,
            "deterministic_validation_available": task.deterministic_validation_available,
            "local_model_output_reviewable": task.local_model_output_reviewable,
        },
        "clarification_needed": [],
    }


def _route_posture(route: str) -> dict[str, Any]:
    return {
        "deterministic_code_only": {
            "local_model_attempt_appropriate": False,
            "frontier_or_codex_needed": False,
            "external_api_needed": False,
            "human_review_required": False,
            "deterministic_first": ["validate the objective against the fixed local rule/check", "produce an inspectable result"],
        },
        "local_model_candidate": {
            "local_model_attempt_appropriate": True,
            "frontier_or_codex_needed": False,
            "external_api_needed": False,
            "human_review_required": True,
            "deterministic_first": ["redact or confirm supplied notes", "define the review boundary", "prepare a draft-only packet"],
        },
        "frontier_model_or_codex_required": {
            "local_model_attempt_appropriate": False,
            "frontier_or_codex_needed": True,
            "external_api_needed": False,
            "human_review_required": True,
            "deterministic_first": ["inventory files and constraints", "write acceptance criteria", "separate architecture review from execution"],
        },
        "external_api_required": {
            "local_model_attempt_appropriate": False,
            "frontier_or_codex_needed": False,
            "external_api_needed": True,
            "human_review_required": True,
            "deterministic_first": ["map required fields", "draft a no-credentials integration boundary", "identify owner approval and stop conditions"],
        },
        "human_review_or_blocked": {
            "local_model_attempt_appropriate": False,
            "frontier_or_codex_needed": False,
            "external_api_needed": False,
            "human_review_required": True,
            "deterministic_first": ["preserve the objective and source basis", "list missing decisions and risk controls", "do not advance to execution"],
        },
    }[route]


def _build_neutral_case_packet(objective: str, objective_id: str, recommendation: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": objective_id,
        "case_type": "operator_objective_route_review",
        "title": recommendation["task"].get("title", objective[:90]),
        "objective": objective,
        "counterparties": ["operator/owner"],
        "source_materials": ["operator-supplied objective"],
        "extracted_facts": [f"capability route recommended: {recommendation['route']}"],
        "timeline_events": ["objective observed", "capability route triaged", "owner packet prepared"],
        "open_issues": list(recommendation["blocked_or_deferred_conditions"]),
        "missing_evidence": list(recommendation["missing_or_invalid_requirements"]),
        "contradictions": [],
        "drafts": [],
        "decisions": ["owner review required before execution"],
        "status": recommendation["route"],
        "next_step": recommendation["next_bounded_action"],
    }


def build_objective_route_packet(objective: str) -> dict[str, Any]:
    """Run the complete deterministic objective -> route -> packet readback."""
    intake = infer_objective_capability_task(objective)
    if intake["capability_task"] is None:
        return {
            "loop_name": "objective_to_route_to_owner_packet",
            "objective_intake": intake,
            "route_readback": {
                "route": "human_review_or_blocked",
                "rationale": "The objective does not contain enough fixed signals for safe capability triage.",
                "next_bounded_action": "clarify the objective type, risk/privacy posture, and reviewability",
                "execution_authorized": False,
            },
            "owner_review_packet": None,
            "neutral_dossier_case_bridge": None,
            "explicit_non_proofs": list(LOOP_NON_PROOFS),
        }

    recommendation = classify_capability_task(intake["capability_task"])
    posture = _route_posture(recommendation["route"])
    recommendation = {
        **recommendation,
        "posture": posture,
    }
    case_packet = _build_neutral_case_packet(objective, intake["objective_id"], recommendation)
    bridge = {
        "case_packet": case_packet,
        "adapted_dossier_case": adapt_case_packet_to_dossier_case(case_packet),
        "neutral_task_readiness": build_neutral_task_readiness_report_dict(case_packet),
        "architecture_posture": "neutral dossier/case adapter remains authoritative; no product wedge selected",
    }
    owner_packet = {
        "packet_name": "objective_route_owner_review_packet",
        "objective": objective,
        "route": recommendation["route"],
        "why_this_route": recommendation["rationale"],
        "capability_factors": intake["capability_task"],
        "deterministic_first": posture["deterministic_first"],
        "owner_review_required": posture["human_review_required"],
        "safe_to_attempt_locally": recommendation["route"] in {"deterministic_code_only", "local_model_candidate"},
        "blocked_or_deferred_conditions": recommendation["blocked_or_deferred_conditions"],
        "next_bounded_action": recommendation["next_bounded_action"],
        "evidence_produced": ["objective intake record", "capability route recommendation", "owner-review packet", "neutral dossier/case bridge readback"],
        "execution_authorized": False,
    }
    return {
        "loop_name": "objective_to_route_to_owner_packet",
        "objective_intake": intake,
        "route_readback": recommendation,
        "owner_review_packet": owner_packet,
        "neutral_dossier_case_bridge": bridge,
        "explicit_non_proofs": list(LOOP_NON_PROOFS),
    }


def render_objective_route_packet_markdown(loop: dict[str, Any]) -> str:
    intake = loop["objective_intake"]
    route = loop["route_readback"]
    lines = [
        "# Objective-to-Route V1 Candidate Readback",
        "",
        f"Objective: {intake.get('objective') or '(missing)'}",
        f"Execution authorized: `{route.get('execution_authorized', False)}`",
        "",
        "## Routing Decision",
        f"Recommended route: `{route['route']}`",
        f"Why: {route['rationale']}",
    ]
    if "posture" in route:
        posture = route["posture"]
        lines.extend([
            f"- Local model attempt appropriate: `{posture['local_model_attempt_appropriate']}`",
            f"- Frontier/Codex needed: `{posture['frontier_or_codex_needed']}`",
            f"- External API needed: `{posture['external_api_needed']}`",
            f"- Human review required: `{posture['human_review_required']}`",
            "",
            "## Deterministic First",
            *[f"- {item}" for item in posture["deterministic_first"]],
        ])
    if loop["owner_review_packet"] is not None:
        packet = loop["owner_review_packet"]
        bridge = loop["neutral_dossier_case_bridge"]
        lines.extend([
            "",
            "## Owner-Review Packet",
            f"Safe to attempt locally: `{packet['safe_to_attempt_locally']}`",
            f"Owner review required: `{packet['owner_review_required']}`",
            "Evidence produced:",
            *[f"- {item}" for item in packet["evidence_produced"]],
            "",
            "## Neutral Dossier/Case Relationship",
            f"- {bridge['architecture_posture']}",
            f"- Structural readiness: `{bridge['neutral_task_readiness']['structurally_ready_for_domain_specific_work']}`",
            "",
            "## Next Bounded Action",
            packet["next_bounded_action"],
        ])
    else:
        lines.extend([
            "",
            "## Clarification Required",
            *[f"- {item}" for item in intake["clarification_needed"]],
            "",
            "## Next Bounded Action",
            route["next_bounded_action"],
        ])
    lines.extend([
        "",
        "## Explicit Non-Proofs",
        *[f"- {item}" for item in loop["explicit_non_proofs"]],
    ])
    return "\n".join(lines)
