from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.case_packet as case_packet
from orchestrator.controlled_dossier_workflow import (
    BLOCKED_CLASSIFICATION,
    COMPLETED_CLASSIFICATION,
    run_controlled_dossier_workflow,
)


def fictional_hvac_workflow_input() -> dict:
    """A compact, explicit subset of the fictional Ozarks Comfort dry run."""
    sources = [
        (
            "fs-owner",
            {
                "source_type": "interview",
                "label": "Fictional owner interview",
                "status": "reported",
                "limitations": ["self-report, not measured"],
                "permitted_use": ["structured analysis"],
            },
        ),
        (
            "fs-coordinator",
            {
                "source_type": "interview",
                "label": "Fictional coordinator interview",
                "status": "reported",
                "limitations": ["peak-period perspective"],
                "permitted_use": ["structured analysis"],
            },
        ),
        (
            "fs-form",
            {
                "source_type": "observed_record",
                "label": "Fictional current intake form",
                "status": "supplied",
                "limitations": ["does not establish usage frequency"],
                "permitted_use": ["workflow review"],
            },
        ),
        (
            "fs-privacy",
            {
                "source_type": "constraint_record",
                "label": "Fictional privacy and review constraints",
                "status": "supplied",
                "limitations": [],
                "permitted_use": ["constraint review"],
            },
        ),
    ]
    statements = [
        (
            "st-form-missing-fields",
            {
                "text": "The observed form lacks equipment and safety fields.",
                "classification": "observed_record",
                "source_references": ["fs-form"],
                "confidence_or_qualification": "direct fictional form inspection",
                "confirmation_posture": "confirmed_fixture_record",
                "materiality": "material",
            },
        ),
        (
            "st-owner-burden",
            {
                "text": "Owner estimates about one hour of cleanup daily.",
                "classification": "reported_estimate",
                "source_references": ["fs-owner"],
                "confidence_or_qualification": "unmeasured owner estimate",
                "confirmation_posture": "unconfirmed",
                "materiality": "material",
            },
        ),
        (
            "st-coordinator-burden",
            {
                "text": "Coordinator estimates two hours of peak-period cleanup daily.",
                "classification": "reported_estimate",
                "source_references": ["fs-coordinator"],
                "confidence_or_qualification": "peak-period estimate",
                "confirmation_posture": "unconfirmed",
                "materiality": "material",
            },
        ),
        (
            "st-human-review",
            {
                "text": "Official job records require a human-approved editable draft.",
                "classification": "constraint",
                "source_references": ["fs-privacy"],
                "confidence_or_qualification": "explicit fictional control",
                "confirmation_posture": "confirmed_fixture_constraint",
                "materiality": "material",
            },
        ),
    ]
    return {
        "case_packet": {
            "case_id": "fictional-ozarks-controlled-workflow",
            "case_type": "fictional_small_business_dossier",
            "title": "Fictional Ozarks Comfort controlled dossier",
            "objective": "Assess one narrow, human-reviewed routine intake pilot.",
            "status": "review_ready",
            "next_step": "owner reviews the bounded planning recommendation",
            "counterparties": [],
            "source_materials": [{"entry_id": entry_id, "value": value} for entry_id, value in sources],
            "extracted_facts": [{"entry_id": entry_id, "value": value} for entry_id, value in statements],
            "timeline_events": [],
            "open_issues": [],
            "missing_evidence": [],
            "contradictions": [],
            "drafts": [],
            "decisions": [],
            "workflow_case_frame": {
                "included_scope": ["routine non-emergency intake", "human-reviewed summary drafts"],
                "excluded_scope": ["customer messaging", "scheduling integration", "technician-note expansion"],
                "decision_owner": "fictional owner",
                "review_posture": "review before pilot planning",
            },
        },
        "analytical_records": {
            "constraint_register": [
                {
                    "constraint_id": "constraint-human-review",
                    "text": "Human approval is required before an official job record changes.",
                    "type": "control",
                    "source_or_owner_reference": "fs-privacy",
                    "hardness": "hard",
                    "status": "active",
                }
            ],
            "contradiction_register": [
                {
                    "contradiction_id": "contradiction-cleanup-estimate",
                    "statement_references": ["st-owner-burden", "st-coordinator-burden"],
                    "description": "Reported cleanup estimates differ.",
                    "materiality": "material",
                    "resolution_status": "unresolved",
                    "effect_on_assessment": "Do not claim measured savings.",
                }
            ],
            "missing_information_register": [
                {
                    "gap_id": "gap-measured-baseline",
                    "question": "What is the measured incomplete-intake and clarification baseline?",
                    "why_it_matters": "It is required before a value claim.",
                    "status": "not_collected",
                    "effect_if_unresolved": "No savings or frequency claim.",
                    "blocking_level": "qualification",
                }
            ],
            "problem_frame": {
                "problem_id": "problem-routine-intake",
                "problem_statement": "Routine intake reconstruction creates avoidable handoff burden.",
                "affected_context": "fictional HVAC service-request intake",
                "supporting_statement_references": ["st-form-missing-fields", "st-owner-burden"],
                "qualifying_statement_references": ["st-coordinator-burden"],
                "judgment_note": "Caller supplied problem frame, not a measured causal finding.",
            },
            "candidates": [
                {
                    "candidate_id": "candidate-structured-form",
                    "description": "Structured intake form and completion checklist.",
                    "mechanism": "Collect required fields before technician handoff.",
                    "scope": "routine non-emergency service requests",
                    "dependencies": ["owner-approved required fields"],
                    "constraint_compatibility": [{"constraint_id": "constraint-human-review", "status": "compatible"}],
                    "assessment_dimensions": ["reversibility", "privacy"],
                    "supporting_references": ["st-form-missing-fields"],
                    "weakening_references": ["st-owner-burden"],
                    "unresolved_gap_references": ["gap-measured-baseline"],
                    "required_authorization_ids": ["authorization-pilot-planning"],
                    "identity_status": "active",
                },
                {
                    "candidate_id": "candidate-human-reviewed-summary",
                    "description": "Human-reviewed intake summary draft.",
                    "mechanism": "Present a draft for coordinator correction before official use.",
                    "scope": "routine non-emergency service requests only",
                    "dependencies": ["review checklist", "privacy rules"],
                    "constraint_compatibility": [{"constraint_id": "constraint-human-review", "status": "compatible"}],
                    "assessment_dimensions": ["reversibility", "human review"],
                    "supporting_references": ["st-human-review", "st-form-missing-fields"],
                    "weakening_references": ["st-coordinator-burden"],
                    "unresolved_gap_references": ["gap-measured-baseline"],
                    "required_authorization_ids": ["authorization-pilot-planning"],
                    "identity_status": "active",
                },
            ],
            "assessments": [
                {
                    "assessment_id": "assessment-summary-reversibility",
                    "candidate_reference": "candidate-human-reviewed-summary",
                    "dimension": "reversibility",
                    "rating": "favorable",
                    "rationale": "The draft layer can stop while the structured form remains.",
                    "evidence_references": ["st-human-review"],
                    "gap_references": ["gap-measured-baseline"],
                    "judgment_note": "Caller supplied assessment.",
                }
            ],
            "prioritization_judgment": {
                "prioritization_id": "prioritization-fictional-owner",
                "selected_candidate_id": "candidate-human-reviewed-summary",
                "no_recommendation": False,
                "rationale": "A bounded sidecar preserves review and reversibility.",
                "decisive_factors": ["human review", "no integration", "reversibility"],
                "tradeoffs": ["does not establish savings"],
                "judgment_owner": "fictional owner",
                "version": "fictional-v1",
            },
            "recommendation_claims": [
                {
                    "claim_id": "recommendation-routine-intake-pilot",
                    "text": "Plan a routine-only human-reviewed intake summary pilot.",
                    "materiality": "material",
                    "judgment_posture": "judged",
                    "judgment_owner": "fictional owner",
                    "statement_references": ["st-form-missing-fields", "st-human-review"],
                    "qualification_references": ["st-owner-burden"],
                    "contradiction_references": ["contradiction-cleanup-estimate"],
                    "gap_references": ["gap-measured-baseline"],
                }
            ],
            "evidence_links": [
                {
                    "evidence_link_id": "link-recommendation-form",
                    "subject_reference": {"subject_type": "recommendation_claim", "subject_id": "recommendation-routine-intake-pilot"},
                    "source_reference": "fs-form",
                    "source_locator": "required-field review",
                },
                {
                    "evidence_link_id": "link-recommendation-constraint",
                    "subject_reference": {"subject_type": "recommendation_claim", "subject_id": "recommendation-routine-intake-pilot"},
                    "source_reference": "fs-privacy",
                    "source_locator": "human approval requirement",
                },
                {
                    "evidence_link_id": "link-human-review-constraint",
                    "subject_reference": {"subject_type": "statement", "subject_id": "st-human-review"},
                    "source_reference": "fs-privacy",
                    "source_locator": "official-record rule",
                },
            ],
            "decision_gates": [
                {
                    "gate_id": "gate-privacy-and-cost",
                    "description": "Owner reviews final pilot form, privacy rules, and cost ceiling.",
                    "status": "open",
                    "gap_references": ["gap-measured-baseline"],
                }
            ],
            "authorizations": [
                {
                    "authorization_id": "authorization-pilot-planning",
                    "status": "authorized",
                    "owner": "fictional owner",
                    "scope": "planning only; no technical implementation",
                }
            ],
            "non_authorizations": [
                {"item": "No model testing or provider selection."},
                {"item": "No scheduling-system connection or customer messaging."},
            ],
            "non_proofs": [
                "No measured savings baseline.",
                "No recommendation correctness proof.",
                "No provider or model execution.",
            ],
            "next_bounded_action": {
                "action": "Owner reviews the pilot form, privacy rules, and cost ceiling.",
                "owner": "fictional owner",
            },
            "disposition": {
                "status": "accept_for_planning_with_revisions",
                "owner": "fictional owner",
                "note": "Routine non-emergency scope only; the form remains if the draft layer stops.",
                "accepted_items": ["pilot planning", "form and measurement definition"],
                "not_authorized_items": ["technical implementation", "external data transfer", "scheduling integration"],
                "separate_future_decisions": ["provider selection", "pilot launch approval", "purchase approval"],
            },
            "revisions": [],
        },
    }


class ControlledDossierWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.case_dir = Path(self.temporary.name)
        self.patch = patch.object(case_packet, "CASE_PACKETS_DIR", self.case_dir)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.temporary.cleanup()

    def test_complete_fictional_workflow_persists_reloads_and_returns_one_reviewable_result(self):
        workflow_input = fictional_hvac_workflow_input()

        result = run_controlled_dossier_workflow(workflow_input)

        self.assertTrue(result["completed"])
        self.assertEqual(COMPLETED_CLASSIFICATION, result["workflow_classification"])
        self.assertEqual(workflow_input["case_packet"], result["original_bounded_case"])
        self.assertEqual(
            workflow_input["case_packet"]["source_materials"],
            result["persisted_reloaded_identity_state"]["source_materials"],
        )
        self.assertEqual(
            workflow_input["case_packet"]["extracted_facts"],
            result["persisted_reloaded_identity_state"]["extracted_facts"],
        )
        self.assertEqual(3, len(result["evidence_links"]))
        package = result["synthesis_result"]["recommendation_package"]
        self.assertEqual("unresolved", package["contradictions"][0]["resolution_status"])
        self.assertEqual("not_collected", package["missing_information"][0]["status"])
        self.assertEqual(
            ["No model testing or provider selection.", "No scheduling-system connection or customer messaging."],
            [item["item"] for item in package["explicit_non_authorizations"]],
        )
        self.assertIn("workflow_does_not_execute_a_provider_model_or_runtime", result["explicit_non_proofs"])

    def test_repeated_equivalent_execution_is_deterministic_and_does_not_mutate_caller_input(self):
        workflow_input = fictional_hvac_workflow_input()
        original = copy.deepcopy(workflow_input)

        first = run_controlled_dossier_workflow(workflow_input)
        second = run_controlled_dossier_workflow(workflow_input)

        self.assertEqual(original, workflow_input)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_invalid_evidence_reference_blocks_after_reloaded_records_are_adapted(self):
        workflow_input = fictional_hvac_workflow_input()
        workflow_input["analytical_records"]["evidence_links"][0]["source_reference"] = "missing-source"

        result = run_controlled_dossier_workflow(workflow_input)

        self.assertFalse(result["completed"])
        self.assertEqual(BLOCKED_CLASSIFICATION, result["workflow_classification"])
        self.assertIn(
            "workflow_synthesis_blocked:evidence_link_source_reference_missing:missing-source",
            result["validation_errors"],
        )

    def test_absent_required_authorization_blocks_without_converting_recommendation_to_authorization(self):
        workflow_input = fictional_hvac_workflow_input()
        workflow_input["analytical_records"]["authorizations"][0]["status"] = "pending"

        result = run_controlled_dossier_workflow(workflow_input)

        self.assertFalse(result["completed"])
        self.assertIn(
            "workflow_synthesis_blocked:required_authorization_absent:authorization-pilot-planning",
            result["validation_errors"],
        )

    def test_hard_constraint_violation_blocks(self):
        workflow_input = fictional_hvac_workflow_input()
        workflow_input["analytical_records"]["candidates"][1]["constraint_compatibility"][0]["status"] = "violated"

        result = run_controlled_dossier_workflow(workflow_input)

        self.assertFalse(result["completed"])
        self.assertIn(
            "workflow_synthesis_blocked:hard_constraint_violated:candidate-human-reviewed-summary:constraint-human-review",
            result["validation_errors"],
        )

    def test_missing_explicit_fact_identity_blocks_without_synthesis_or_matching(self):
        workflow_input = fictional_hvac_workflow_input()
        workflow_input["case_packet"]["extracted_facts"][0] = {
            "value": workflow_input["case_packet"]["extracted_facts"][0]["value"]
        }

        result = run_controlled_dossier_workflow(workflow_input)

        self.assertFalse(result["completed"])
        self.assertIn("workflow_extracted_fact_entry_id_required:0", result["validation_errors"])
        self.assertIsNone(result["synthesis_result"])

    def test_disposition_requires_acceptance_non_authorizations_and_separate_decisions(self):
        workflow_input = fictional_hvac_workflow_input()
        workflow_input["analytical_records"]["disposition"]["not_authorized_items"] = []

        result = run_controlled_dossier_workflow(workflow_input)

        self.assertFalse(result["completed"])
        self.assertIn("workflow_disposition_not_authorized_items_must_be_non_empty_list", result["validation_errors"])


if __name__ == "__main__":
    unittest.main()
