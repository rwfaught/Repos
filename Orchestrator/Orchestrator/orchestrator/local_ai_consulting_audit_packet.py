"""Deterministic, non-executing local AI consulting audit packet prototype."""

from __future__ import annotations

from typing import Any

from orchestrator.dossier_case_mapping import adapt_case_packet_to_dossier_case
from orchestrator.dossier_case_task_readiness import (
    build_neutral_task_readiness_report_dict,
)

BOUNDARY = "GPT56_LOCAL_AI_CONSULTING_SANDBOX_VERTICAL_SLICE"
SCENARIO = "Fictional Springfield HVAC Service Company"
OFFER = "$150 Local AI Efficiency Audit"
TARGET_USER = "Roger, acting as a local AI consultant for small businesses"
NO_FIRST_PRODUCT_WEDGE_SELECTED = "no first product wedge selected"
PHASE_387_REMAINS_UNSET = "Phase 387 remains unset/not resumed"
FLOW_NAME = "local_ai_consulting_audit_intake_to_report"

AUDIT_INTAKE_REQUIRED_FIELDS = (
    "audit_id",
    "offer",
    "target_user",
    "objective",
    "business_profile",
    "source_materials",
    "workflow_facts",
    "friction_nodes",
    "repeated_tasks",
    "candidate_ai_interventions",
    "risk_privacy_posture",
    "open_questions",
    "contradictions_or_unclear_claims",
    "recommended_first_implementation",
    "do_not_automate_yet",
    "explicit_non_proofs",
    "operator_next_action",
)

EXPLICIT_NON_PROOFS = (
    "not runtime/provider/model execution",
    "not semantic correctness",
    "not production readiness",
    "not a first product wedge selection",
    "not external integration code",
    "not real business or customer data",
)


def build_springfield_hvac_fixture() -> dict[str, Any]:
    """Return the complete fictional audit input and bounded recommendation."""
    return {
        "objective": "Identify one low-risk workflow where a local AI assistant could reduce missed follow-up without sending messages autonomously.",
        "business_profile": {
            "business_name": "Springfield HVAC Service Company",
            "business_type": "fictional local HVAC service company",
            "staff_context": "owner-operator, dispatcher, and field technicians",
            "data_posture": "fictional scenario; no customer records included",
        },
        "source_materials": [
            "fictional owner interview notes",
            "fictional missed-call log summary",
            "fictional service-inquiry follow-up notes",
        ],
        "workflow_facts": [
            "New calls and web inquiries arrive while staff are dispatching technicians.",
            "Follow-up is reconstructed later from notes, voicemail, and memory.",
            "A human should review any draft before it is sent or entered into a system.",
        ],
        "friction_nodes": [
            "missed calls are easy to lose during busy periods",
            "customer context is scattered across short notes",
            "urgency and appointment details may be unclear",
        ],
        "repeated_tasks": [
            "summarize the inquiry",
            "identify missing details and urgency signals",
            "draft a neutral follow-up checklist or message",
        ],
        "candidate_ai_interventions": [
            "turn supplied notes into a structured inquiry summary",
            "draft a staff-facing follow-up recommendation for review",
            "flag missing address, service need, timing, and callback information",
        ],
        "risk_privacy_posture": [
            "use fictional or redacted inputs for this sandbox",
            "keep human approval before any customer-facing action",
            "do not infer emergency status or make promises about pricing or arrival",
            "do not connect to phone, CRM, email, calendar, or dispatch systems",
        ],
        "open_questions": [
            "Which inquiry fields does the owner consider mandatory before follow-up?",
            "Who approves a draft and how quickly must it be reviewed?",
            "Which cases require escalation rather than a draft?",
        ],
        "contradictions_or_unclear_claims": [
            "The fictional notes say follow-up is both same-day and end-of-day; timing is unverified.",
            "The notes do not establish whether every missed call has a voicemail.",
            "The scenario does not prove that drafting is the highest-value intervention.",
        ],
        "recommended_first_implementation": "Staff-facing missed-call and service-inquiry follow-up draft assistant using supplied notes, with explicit human review and no sending or system writeback.",
        "do_not_automate_yet": [
            "emergency or safety triage",
            "pricing, warranty, or eligibility commitments",
            "appointment booking, cancellation, or dispatch decisions",
            "customer identity resolution or CRM writeback",
            "autonomous texting, emailing, or calling",
        ],
        "operator_next_action": "Ask Roger to validate the mandatory inquiry fields, approval owner, escalation cases, and timing claim before any implementation boundary is proposed.",
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "boundary": BOUNDARY,
        "scenario": SCENARIO,
        "phase_387_posture": PHASE_387_REMAINS_UNSET,
        "product_wedge_posture": NO_FIRST_PRODUCT_WEDGE_SELECTED,
    }


def build_local_ai_consulting_fixture_library() -> dict[str, dict[str, Any]]:
    """Return the deterministic fictional scenario library."""
    return {"springfield_hvac": build_springfield_hvac_fixture()}


def build_audit_intake() -> dict[str, Any]:
    """Create the fictional intake record that seeds the complete flow."""
    fixture = build_springfield_hvac_fixture()
    return {
        "intake_name": "local_ai_consulting_audit_intake",
        "audit_id": "springfield-hvac-efficiency-audit-001",
        "offer": OFFER,
        "target_user": TARGET_USER,
        "fixture_name": "springfield_hvac",
        "intake_status": "fictional_structural_intake",
        **fixture,
    }


def classify_risk_privacy_posture(
    intake: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Expose deterministic risk controls without making a live assessment."""
    source = build_audit_intake() if intake is None else intake
    return {
        "classification_name": "local_ai_consulting_risk_privacy_classification",
        "classification": "bounded_but_human_review_required",
        "risk_level": "moderate_workflow_and_privacy_risk",
        "risk_categories": [
            "privacy and redaction",
            "misread urgency or service need",
            "unapproved customer-facing language",
            "incorrect operational commitments",
        ],
        "controls": list(source["risk_privacy_posture"]),
        "automation_boundary": "draft and flag supplied information for staff review; no autonomous action",
        "review_required": True,
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def classify_do_not_automate_yet(
    intake: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify deferred actions while preserving the exact item list."""
    source = build_audit_intake() if intake is None else intake
    return {
        "classification_name": "local_ai_consulting_deferred_automation_classification",
        "classification": "human_decision_or_future_boundary_required",
        "items": [
            {"item": item, "status": "do_not_automate_yet"}
            for item in source["do_not_automate_yet"]
        ],
        "human_decision_required": True,
        "external_integration_allowed": False,
    }


def build_audit_review_gate(
    intake: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Produce a structural owner-review gate for the deterministic intake."""
    source = build_audit_intake() if intake is None else intake
    present = [field for field in AUDIT_INTAKE_REQUIRED_FIELDS if field in source]
    missing = [field for field in AUDIT_INTAKE_REQUIRED_FIELDS if field not in source]
    blockers = [f"missing required intake field: {field}" for field in missing]
    if not source.get("open_questions"):
        blockers.append("open questions must remain visible")
    if not source.get("contradictions_or_unclear_claims"):
        blockers.append("contradictions or unclear claims must remain visible")
    return {
        "gate_name": "local_ai_consulting_owner_review_gate",
        "boundary": BOUNDARY,
        "review_decision": "ready_for_owner_review" if not blockers else "needs_intake_repair",
        "required_intake_fields": list(AUDIT_INTAKE_REQUIRED_FIELDS),
        "present_required_intake_fields": present,
        "missing_required_intake_fields": missing,
        "blockers": blockers,
        "operator_approval_required": True,
        "execution_authorized": False,
        "product_wedge_selected": False,
        "phase_387_resumed": False,
        "recommended_action": source["operator_next_action"],
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def build_local_ai_consulting_case_packet(
    intake: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map consulting intake into the existing neutral case-packet shape."""
    source = build_audit_intake() if intake is None else intake
    business_name = source["business_profile"]["business_name"]
    return {
        "case_id": source.get("audit_id", "local-ai-consulting-sandbox-001"),
        "case_type": "local_ai_consulting_audit",
        "title": f"{business_name} local AI efficiency audit",
        "objective": source["objective"],
        "counterparties": ["fictional business owner/operator"],
        "source_materials": list(source["source_materials"]),
        "extracted_facts": list(source["workflow_facts"]),
        "timeline_events": [
            "fictional intake received",
            "workflow friction captured",
            "owner review required",
        ],
        "open_issues": list(source["open_questions"]),
        "missing_evidence": [
            "owner-confirmed mandatory inquiry fields",
            "verified follow-up timing",
        ],
        "contradictions": list(source["contradictions_or_unclear_claims"]),
        "drafts": [source["recommended_first_implementation"]],
        "decisions": [
            "owner review is required before any implementation boundary",
            NO_FIRST_PRODUCT_WEDGE_SELECTED,
        ],
        "status": "structural_sandbox_review",
        "next_step": source["operator_next_action"],
    }


def build_dossier_case_bridge_readback(
    intake: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the consulting-to-neutral-dossier adapter and readiness readback."""
    source = build_audit_intake() if intake is None else intake
    case_packet = build_local_ai_consulting_case_packet(source)
    adapted = adapt_case_packet_to_dossier_case(case_packet)
    readiness = build_neutral_task_readiness_report_dict(case_packet)
    return {
        "bridge_name": "local_ai_consulting_to_neutral_dossier_case_bridge",
        "boundary": BOUNDARY,
        "source_audit_id": source.get("audit_id", "sandbox-fixture-without-audit-id"),
        "case_packet": case_packet,
        "adapted_dossier_case": adapted,
        "neutral_task_readiness": readiness,
        "preservation_checks": {
            "objective_preserved": adapted["objective"] == source["objective"],
            "source_materials_preserved": adapted["source_materials"] == source["source_materials"],
            "open_questions_preserved": adapted["open_questions"] == source["open_questions"],
            "contradictions_preserved": adapted["contradictions"] == source["contradictions_or_unclear_claims"],
            "recommended_next_step_preserved": adapted["next_work_items"] == [source["operator_next_action"]],
        },
        "architecture_posture": (
            "adapter bridge only; existing neutral dossier/case semantics remain authoritative"
        ),
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def build_internal_implementation_packet(
    fixture: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fixture = build_audit_intake() if fixture is None else fixture
    risk_posture = classify_risk_privacy_posture(fixture)
    deferred_automation = classify_do_not_automate_yet(fixture)
    review_gate = build_audit_review_gate(fixture)
    dossier_bridge = build_dossier_case_bridge_readback(fixture)
    return {
        "packet_name": "local_ai_consulting_internal_implementation_packet",
        "flow_name": FLOW_NAME,
        "boundary": BOUNDARY,
        "audit_id": fixture.get("audit_id", "sandbox-fixture-without-audit-id"),
        "offer": fixture.get("offer", OFFER),
        "target_user": fixture.get("target_user", TARGET_USER),
        "objective": fixture["objective"],
        "business_profile": fixture["business_profile"],
        "source_materials": fixture["source_materials"],
        "workflow_facts": fixture["workflow_facts"],
        "friction_nodes": fixture["friction_nodes"],
        "repeated_tasks": fixture["repeated_tasks"],
        "candidate_ai_interventions": fixture["candidate_ai_interventions"],
        "risk_privacy_posture": fixture["risk_privacy_posture"],
        "risk_privacy_classification": risk_posture,
        "open_questions": fixture["open_questions"],
        "contradictions_or_unclear_claims": fixture["contradictions_or_unclear_claims"],
        "recommended_first_implementation": fixture["recommended_first_implementation"],
        "do_not_automate_yet": fixture["do_not_automate_yet"],
        "do_not_automate_yet_classification": deferred_automation,
        "explicit_non_proofs": fixture["explicit_non_proofs"],
        "operator_next_action": fixture["operator_next_action"],
        "review_gate": review_gate,
        "dossier_case_bridge_readback": dossier_bridge,
        "execution_posture": {
            "runtime_provider_model_execution": False,
            "production_readiness": False,
            "first_product_wedge_selected": False,
            "phase_387_resumed": False,
        },
    }


def build_client_readable_audit_report(
    fixture: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fixture = build_audit_intake() if fixture is None else fixture
    risk_posture = classify_risk_privacy_posture(fixture)
    deferred_automation = classify_do_not_automate_yet(fixture)
    review_gate = build_audit_review_gate(fixture)
    dossier_bridge = build_dossier_case_bridge_readback(fixture)
    return {
        "report_name": "Springfield HVAC Local AI Efficiency Audit",
        "flow_name": FLOW_NAME,
        "boundary": BOUNDARY,
        "audit_id": fixture.get("audit_id", "sandbox-fixture-without-audit-id"),
        "offer": fixture.get("offer", OFFER),
        "business_snapshot": fixture["business_profile"],
        "audit_objective": fixture["objective"],
        "source_basis": fixture["source_materials"],
        "workflow_facts": fixture["workflow_facts"],
        "workflow_friction": fixture["friction_nodes"],
        "repeated_tasks": fixture["repeated_tasks"],
        "candidate_ai_interventions": fixture["candidate_ai_interventions"],
        "risk_privacy_posture": fixture["risk_privacy_posture"],
        "risk_privacy_classification": risk_posture,
        "recommended_first_implementation": fixture["recommended_first_implementation"],
        "what_not_to_automate_yet": fixture["do_not_automate_yet"],
        "what_not_to_automate_yet_classification": deferred_automation,
        "questions_roger_should_ask_the_owner": fixture["open_questions"],
        "contradictions_or_unclear_claims": fixture["contradictions_or_unclear_claims"],
        "operator_next_action": fixture["operator_next_action"],
        "review_gate_summary": {
            "review_decision": review_gate["review_decision"],
            "operator_approval_required": review_gate["operator_approval_required"],
            "execution_authorized": review_gate["execution_authorized"],
        },
        "neutral_dossier_case_readiness": dossier_bridge["neutral_task_readiness"],
        "explicit_non_proofs": fixture["explicit_non_proofs"],
    }


def build_local_ai_consulting_readback() -> dict[str, Any]:
    intake = build_audit_intake()
    review_gate = build_audit_review_gate(intake)
    dossier_bridge = build_dossier_case_bridge_readback(intake)
    return {
        "flow_name": FLOW_NAME,
        "fixture": intake,
        "audit_intake": intake,
        "risk_privacy_classification": classify_risk_privacy_posture(intake),
        "do_not_automate_yet_classification": classify_do_not_automate_yet(intake),
        "review_gate": review_gate,
        "dossier_case_bridge": dossier_bridge,
        "internal_implementation_packet": build_internal_implementation_packet(intake),
        "client_readable_audit_report": build_client_readable_audit_report(intake),
        "product_wedge_posture": NO_FIRST_PRODUCT_WEDGE_SELECTED,
        "phase_387_posture": PHASE_387_REMAINS_UNSET,
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def build_local_ai_consulting_audit_flow() -> dict[str, Any]:
    """Return the complete deterministic intake-to-report product-shaped flow."""
    return build_local_ai_consulting_readback()
