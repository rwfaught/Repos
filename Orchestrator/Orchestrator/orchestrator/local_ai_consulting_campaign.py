"""Deterministic multi-scenario local AI consulting campaign prototype."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from orchestrator.dossier_case_mapping import adapt_case_packet_to_dossier_case
from orchestrator.dossier_case_task_readiness import (
    build_neutral_task_readiness_report_dict,
)

BOUNDARY = "GPT56_SANDBOX_AUTONOMOUS_MULTI_STAGE_PRODUCT_CAMPAIGN"
ARCHITECTURE_DECISION = "D_PARTIAL_ADAPTER_READBACK_BRIDGE"
OWNER_REVIEW_GATE = "owner_review_required_before_implementation"
SANDBOX_ONLY_STATUS = "sandbox_only_not_production_proof"

EXPLICIT_NON_PROOFS = (
    "not runtime/provider/model execution",
    "not semantic business competence",
    "not production readiness",
    "not a first product wedge selection",
    "not Phase 387 resumption",
    "not external integration execution",
    "not real business or customer data",
)

REQUIRED_SCENARIO_FIELDS = (
    "scenario_id",
    "business_profile",
    "owner_objective",
    "current_tools_and_systems",
    "workflow_pain_points",
    "data_sensitivity",
    "constraints",
    "requested_external_integrations",
    "opportunities",
    "risks",
    "blocked_items",
    "owner_review_gates",
    "phased_roadmap",
    "explicit_non_proofs",
)


def _base_scenario(
    scenario_id: str,
    business_profile: str,
    owner_objective: str,
    current_tools_and_systems: list[str],
    workflow_pain_points: list[str],
    data_sensitivity: str,
    constraints: list[str],
    requested_external_integrations: list[str],
    opportunities: list[str],
    risks: list[str],
    blocked_items: list[str],
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "business_profile": business_profile,
        "owner_objective": owner_objective,
        "current_tools_and_systems": current_tools_and_systems,
        "workflow_pain_points": workflow_pain_points,
        "data_sensitivity": data_sensitivity,
        "constraints": constraints,
        "requested_external_integrations": requested_external_integrations,
        "opportunities": opportunities,
        "risks": risks,
        "blocked_items": blocked_items,
        "owner_review_gates": [
            "owner confirms the objective and source inputs",
            "owner approves the review boundary before implementation",
            "a human reviews every proposed output before use",
        ],
        "phased_roadmap": [
            "phase_0_owner_review: confirm objective, inputs, and stop conditions",
            "phase_1_local_fixture: inspect a redacted or fictional sample locally",
            "phase_2_human_readback: review the packet and revise the boundary",
            "phase_3_deferred_integration_review: assess external dependencies separately",
        ],
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def build_consulting_scenario_library() -> dict[str, dict[str, Any]]:
    """Return four deterministic fictional consulting scenarios."""
    return {
        "internal_knowledge_helpdesk": _base_scenario(
            "internal_knowledge_helpdesk",
            "small professional-services office with an internal policy and FAQ corpus",
            "Reduce repeated internal questions by organizing supplied policy excerpts into a reviewable answer outline.",
            ["shared policy folder", "internal FAQ document", "staff email used as source material"],
            ["answers are repeated across staff", "policy excerpts are hard to find", "source ownership is unclear"],
            "low_internal_only",
            ["use fictional or redacted excerpts", "answer remains a draft for staff review"],
            [],
            ["extract cited topics from supplied excerpts", "draft a staff-facing answer outline", "flag missing source ownership"],
            ["stale policy language", "answer may omit an exception", "staff may treat a draft as authoritative"],
            ["live knowledge-base synchronization", "automatic policy interpretation", "unreviewed staff instructions"],
        ),
        "owner_reviewed_drafting_reporting": _base_scenario(
            "owner_reviewed_drafting_reporting",
            "owner-operated service business preparing recurring internal status reports",
            "Turn supplied notes into a draft weekly report while keeping decisions and final wording with the owner.",
            ["owner notes", "spreadsheet export supplied by the owner", "existing report template"],
            ["report preparation is repetitive", "notes use inconsistent labels", "unresolved items are easy to miss"],
            "moderate_internal_operational",
            ["owner supplies the source notes", "no automatic publication", "drafts must show missing inputs"],
            [],
            ["normalize supplied notes into sections", "draft a report outline", "surface unresolved items for owner review"],
            ["incorrect aggregation", "missing context", "draft language could imply an approved decision"],
            ["automatic report distribution", "financial or legal conclusions", "editing the source system"],
        ),
        "regulated_sensitive_data": _base_scenario(
            "regulated_sensitive_data",
            "fictional regulated practice handling sensitive personal records",
            "Identify whether a narrowly redacted internal summarization exercise is worth owner and compliance review.",
            ["restricted case-management system", "sensitive records", "formal compliance procedures"],
            ["review work is slow", "records contain sensitive identifiers", "approval requirements vary by record type"],
            "high_regulated_sensitive",
            ["no sensitive records enter this sandbox", "redaction and compliance review are prerequisites"],
            [],
            ["enumerate a redacted workflow", "separate administrative from sensitive steps", "prepare owner questions"],
            ["privacy exposure", "incorrect interpretation", "regulatory or professional harm"],
            ["processing real records", "automated recommendations", "production use before compliance approval"],
        ),
        "external_integration_heavy": _base_scenario(
            "external_integration_heavy",
            "small field-service company asking for cross-system scheduling assistance",
            "Assess whether a local draft could reduce scheduling coordination without touching live systems.",
            ["CRM", "calendar", "dispatch board", "phone and email systems"],
            ["information is spread across systems", "schedule changes are time-sensitive", "ownership of final updates is unclear"],
            "moderate_external_operational",
            ["no credentials or live records", "integration contracts must be reviewed separately", "human dispatch decision remains required"],
            ["CRM", "calendar", "dispatch", "phone", "email"],
            ["map the information needed for a future review", "draft a non-executing coordination checklist", "identify integration questions"],
            ["stale cross-system data", "duplicate or conflicting updates", "unintended operational commitments"],
            ["live reads or writes", "automatic booking or dispatch", "outbound calling or messaging"],
        ),
    }


def _missing_inputs(scenario: dict[str, Any]) -> list[str]:
    return [
        field for field in REQUIRED_SCENARIO_FIELDS
        if field not in scenario or scenario[field] is None or scenario[field] == ""
    ]


def _readiness_status(
    missing_inputs: list[str],
    blocked_by_sensitivity: bool,
    blocked_by_external_integration: bool,
) -> str:
    if missing_inputs:
        return "missing_input"
    if blocked_by_sensitivity:
        return "blocked_by_sensitivity"
    if blocked_by_external_integration:
        return "blocked_by_external_integration"
    return "owner_review_ready"


def classify_consulting_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Classify a scenario without calling a model or executing a workflow."""
    missing_inputs = _missing_inputs(scenario)
    sensitivity_blocked = scenario.get("data_sensitivity") == "high_regulated_sensitive"
    integration_blocked = bool(scenario.get("requested_external_integrations"))
    structural_complete = not missing_inputs

    readiness_status = _readiness_status(
        missing_inputs,
        sensitivity_blocked,
        integration_blocked,
    )

    return {
        "scenario_id": scenario.get("scenario_id", "unnamed_scenario"),
        "structural_complete": structural_complete,
        "missing_inputs": missing_inputs,
        "owner_review_ready": readiness_status == "owner_review_ready",
        "blocked_by_sensitivity": sensitivity_blocked,
        "blocked_by_external_integration": integration_blocked,
        "readiness_status": readiness_status,
        "sandbox_only_status": SANDBOX_ONLY_STATUS,
        "sandbox_only_not_production_proof": True,
        "owner_review_gate": OWNER_REVIEW_GATE,
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def _build_neutral_case_packet(
    scenario: dict[str, Any],
    review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "case_id": f"consulting-{scenario['scenario_id']}",
        "case_type": "local_ai_consulting_scenario",
        "title": f"{scenario['scenario_id']} consulting review",
        "objective": scenario.get("owner_objective", ""),
        "counterparties": ["fictional business owner/operator"],
        "source_materials": list(scenario.get("current_tools_and_systems", [])),
        "extracted_facts": list(scenario.get("workflow_pain_points", [])),
        "timeline_events": list(scenario.get("phased_roadmap", [])),
        "open_issues": list(scenario.get("owner_review_gates", [])) + list(review["missing_inputs"]),
        "missing_evidence": list(review["missing_inputs"]),
        "contradictions": list(scenario.get("risks", [])),
        "drafts": list(scenario.get("opportunities", [])),
        "decisions": [OWNER_REVIEW_GATE],
        "status": review["readiness_status"],
        "next_step": "owner reviews the packet and confirms the next bounded step",
    }


def build_owner_packet(scenario: dict[str, Any]) -> dict[str, Any]:
    """Build the owner-facing categories for one scenario."""
    review = classify_consulting_scenario(scenario)
    blocked_by_sensitivity = review["blocked_by_sensitivity"]
    blocked_by_integration = review["blocked_by_external_integration"]
    safe_to_explore = [] if blocked_by_sensitivity else list(scenario.get("opportunities", []))
    return {
        "packet_name": "local_ai_consulting_owner_review_packet",
        "boundary": BOUNDARY,
        "scenario_id": scenario.get("scenario_id", "unnamed_scenario"),
        "business_profile": scenario.get("business_profile", ""),
        "owner_objective": scenario.get("owner_objective", ""),
        "current_tools_and_systems": list(scenario.get("current_tools_and_systems", [])),
        "workflow_pain_points": list(scenario.get("workflow_pain_points", [])),
        "data_sensitivity": scenario.get("data_sensitivity", ""),
        "constraints": list(scenario.get("constraints", [])),
        "safe_to_explore_locally": safe_to_explore,
        "needs_owner_approval": list(scenario.get("owner_review_gates", [])),
        "needs_more_information": list(review["missing_inputs"]),
        "requires_external_integration": list(scenario.get("requested_external_integrations", [])),
        "do_not_automate_yet": list(scenario.get("blocked_items", [])),
        "risks": list(scenario.get("risks", [])),
        "phased_roadmap": list(scenario.get("phased_roadmap", [])),
        "not_proven": list(EXPLICIT_NON_PROOFS),
        "self_review": review,
        "owner_approval_required": True,
        "execution_authorized": False,
        "blocked_by_sensitivity": blocked_by_sensitivity,
        "blocked_by_external_integration": blocked_by_integration,
    }


def review_owner_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Re-read owner-packet state and expose a deterministic readiness result."""
    missing = list(packet.get("needs_more_information", []))
    blocked_by_sensitivity = bool(packet.get("blocked_by_sensitivity"))
    blocked_by_integration = bool(packet.get("blocked_by_external_integration"))
    structural_complete = not missing

    status = _readiness_status(missing, blocked_by_sensitivity, blocked_by_integration)

    return {
        "review_name": "local_ai_consulting_owner_packet_readiness_review",
        "scenario_id": packet.get("scenario_id", "unnamed_scenario"),
        "structurally_complete": structural_complete,
        "missing_inputs": missing,
        "missing_input": bool(missing),
        "owner_review_ready": status == "owner_review_ready",
        "blocked_by_sensitivity": blocked_by_sensitivity,
        "blocked_by_external_integration": blocked_by_integration,
        "readiness_status": status,
        "sandbox_only_status": SANDBOX_ONLY_STATUS,
        "owner_approval_required": True,
        "execution_authorized": False,
        "sandbox_only_not_production_proof": True,
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def build_consulting_scenario_readback(scenario: dict[str, Any]) -> dict[str, Any]:
    """Build one owner packet plus the neutral dossier/case comparison."""
    scenario_copy = deepcopy(scenario)
    owner_packet = build_owner_packet(scenario_copy)
    self_review = review_owner_packet(owner_packet)
    case_packet = _build_neutral_case_packet(scenario_copy, self_review)
    adapted = adapt_case_packet_to_dossier_case(case_packet)
    neutral_readiness = build_neutral_task_readiness_report_dict(case_packet)
    return {
        "scenario": scenario_copy,
        "owner_packet": owner_packet,
        "self_review": self_review,
        "neutral_dossier_case_bridge": {
            "case_packet": case_packet,
            "adapted_dossier_case": adapted,
            "neutral_task_readiness": neutral_readiness,
            "architecture_posture": "adapter bridge only; neutral dossier/case semantics remain authoritative",
        },
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def build_local_ai_consulting_campaign_readback() -> dict[str, Any]:
    """Return the complete deterministic multi-stage campaign readback."""
    library = build_consulting_scenario_library()
    scenario_readbacks = {
        scenario_id: build_consulting_scenario_readback(scenario)
        for scenario_id, scenario in library.items()
    }
    status_by_scenario = {
        scenario_id: readback["self_review"]["readiness_status"]
        for scenario_id, readback in scenario_readbacks.items()
    }
    return {
        "campaign_name": "local_ai_consulting_multi_stage_campaign",
        "boundary": BOUNDARY,
        "architecture_decision": {
            "decision": ARCHITECTURE_DECISION,
            "rationale": "Use a consulting-specific owner packet and self-review layer, then compare through the existing neutral adapter and readiness report.",
            "neutral_case_semantics_authoritative": True,
        },
        "scenario_count": len(scenario_readbacks),
        "scenario_readbacks": scenario_readbacks,
        "comparison": {
            "readiness_status_by_scenario": status_by_scenario,
            "owner_review_ready_scenarios": [
                scenario_id for scenario_id, status in status_by_scenario.items()
                if status == "owner_review_ready"
            ],
            "blocked_scenarios": [
                scenario_id for scenario_id, status in status_by_scenario.items()
                if status.startswith("blocked_by_")
            ],
            "missing_input_scenarios": [
                scenario_id for scenario_id, status in status_by_scenario.items()
                if status == "missing_input"
            ],
        },
        "product_wedge_posture": "no first product wedge selected",
        "phase_387_posture": "Phase 387 remains unset/not resumed",
        "execution_posture": {
            "runtime_provider_model_execution": False,
            "external_integration_execution": False,
            "production_task_execution": False,
        },
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def build_local_ai_consulting_operator_readback(
    scenario_id: str | None = None,
) -> dict[str, Any]:
    """Return the smallest operator-facing readback for one or all scenarios."""
    campaign = build_local_ai_consulting_campaign_readback()
    if scenario_id is None:
        return {
            "readback_name": "local_ai_consulting_operator_campaign_readback",
            "selection": "all",
            "campaign": campaign,
            "next_action": "operator reviews the comparison and selects one bounded scenario for deeper review",
            "execution_authorized": False,
            "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        }

    selected = campaign["scenario_readbacks"].get(scenario_id)
    if selected is None:
        return {
            "readback_name": "local_ai_consulting_operator_campaign_readback",
            "selection": scenario_id,
            "found": False,
            "available_scenarios": sorted(campaign["scenario_readbacks"]),
            "next_action": "operator selects an available scenario or supplies a corrected scenario identifier",
            "execution_authorized": False,
            "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        }

    review = selected["self_review"]
    return {
        "readback_name": "local_ai_consulting_operator_campaign_readback",
        "selection": scenario_id,
        "found": True,
        "readiness_status": review["readiness_status"],
        "owner_review_ready": review["owner_review_ready"],
        "blocked_conditions": [
            condition for condition, present in (
                ("missing_input", review["missing_input"]),
                ("blocked_by_sensitivity", review["blocked_by_sensitivity"]),
                ("blocked_by_external_integration", review["blocked_by_external_integration"]),
            ) if present
        ],
        "owner_packet": selected["owner_packet"],
        "neutral_dossier_case_bridge": selected["neutral_dossier_case_bridge"],
        "next_action": (
            "operator reviews the owner packet before any implementation"
            if review["owner_review_ready"]
            else "operator resolves the listed blocker or keeps this scenario deferred"
        ),
        "execution_authorized": False,
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def render_local_ai_consulting_operator_readback_markdown(
    readback: dict[str, Any] | None = None,
) -> str:
    """Render a concise, deterministic operator/PM readback."""
    payload = readback or build_local_ai_consulting_operator_readback()
    lines = [
        "# Local AI Consulting Operator Readback",
        "",
        f"Selection: `{payload['selection']}`",
        f"Execution authorized: `{payload['execution_authorized']}`",
    ]
    if not payload.get("found", True):
        lines.extend([
            "",
            "## Selection Result",
            "Scenario not found.",
            "",
            "Available scenarios:",
            *[f"- `{item}`" for item in payload["available_scenarios"]],
        ])
    elif payload["selection"] == "all":
        comparison = payload["campaign"]["comparison"]
        lines.extend([
            "",
            "## Campaign Comparison",
            f"Scenarios reviewed: `{payload['campaign']['scenario_count']}`",
            f"Owner-review-ready: `{', '.join(comparison['owner_review_ready_scenarios']) or 'none'}`",
            f"Blocked: `{', '.join(comparison['blocked_scenarios']) or 'none'}`",
            f"Next action: {payload['next_action']}",
        ])
    else:
        lines.extend([
            "",
            "## Scenario Result",
            f"Readiness: `{payload['readiness_status']}`",
            f"Owner-review-ready: `{payload['owner_review_ready']}`",
            f"Blocked conditions: `{', '.join(payload['blocked_conditions']) or 'none'}`",
            f"Next action: {payload['next_action']}",
        ])
    lines.extend([
        "",
        "## Explicit Non-Proofs",
        *[f"- {item}" for item in payload["explicit_non_proofs"]],
    ])
    return "\n".join(lines)
