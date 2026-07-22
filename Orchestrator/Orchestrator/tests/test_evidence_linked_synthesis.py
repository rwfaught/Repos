from __future__ import annotations

import copy
import json
import unittest

from orchestrator.evidence_linked_synthesis import (
    TRANSFORMATION_POSTURES,
    build_evidence_linked_synthesis_package,
)


def hvac_packet():
    """A deliberately structured subset of the fictional Ozarks Comfort dossier."""
    return {
        "case_frame": {"case_id": "ozarks-intake-pilot", "objective": "Reduce avoidable reconstruction in routine service-request intake.", "included_scope": ["routine non-emergency intake", "human-reviewed summaries"], "excluded_scope": ["autonomous customer communication", "scheduling-system modification"], "decision_owner": "fictional owner", "review_posture": "review before pilot planning"},
        "source_inventory": [
            {"source_id": "fs-01", "source_type": "interview", "label": "Owner interview", "status": "reported", "limitations": ["fictional reported statement"], "permitted_use": ["structured analysis"]},
            {"source_id": "fs-02", "source_type": "interview", "label": "Coordinator interview", "status": "reported", "limitations": ["peak-period estimate"], "permitted_use": ["structured analysis"]},
            {"source_id": "fs-11", "source_type": "constraint_record", "label": "Privacy and access constraints", "status": "supplied", "limitations": [], "permitted_use": ["constraint review"]},
        ],
        "statement_register": [
            {"statement_id": "s-owner-cleanup", "text": "Owner guesses at least one hour daily of cleanup.", "classification": "reported_estimate", "source_references": ["fs-01"], "confidence_or_qualification": "owner estimate, not measured", "confirmation_posture": "unconfirmed", "materiality": "material"},
            {"statement_id": "s-coordinator-cleanup", "text": "Coordinator estimates two hours daily during summer.", "classification": "reported_estimate", "source_references": ["fs-02"], "confidence_or_qualification": "peak-period estimate", "confirmation_posture": "unconfirmed", "materiality": "material"},
            {"statement_id": "s-human-review", "text": "Coordinator would correct a summary before saving.", "classification": "reported_statement", "source_references": ["fs-02"], "confidence_or_qualification": "reported workflow preference", "confirmation_posture": "unconfirmed", "materiality": "material"},
            {"statement_id": "s-no-autonomy", "text": "Official records require human approval.", "classification": "constraint", "source_references": ["fs-11"], "confidence_or_qualification": "supplied constraint", "confirmation_posture": "confirmed", "materiality": "material"},
        ],
        "constraint_register": [{"constraint_id": "c-human-review", "text": "Human approval before official job record.", "type": "control", "source_or_owner_reference": "fs-11", "hardness": "hard", "status": "active"}],
        "contradiction_register": [{"contradiction_id": "x-cleanup", "statement_references": ["s-owner-cleanup", "s-coordinator-cleanup"], "description": "Cleanup burden estimates differ.", "materiality": "material", "resolution_status": "unresolved", "effect_on_assessment": "Do not claim measured savings."}],
        "missing_information_register": [{"gap_id": "g-turnaround", "question": "What is the measured estimate turnaround distribution?", "why_it_matters": "Needed before claiming faster estimates.", "status": "unknown", "effect_if_unresolved": "No measured value claim.", "blocking_level": "qualification"}],
        "problem_frame": {"problem_id": "p-intake", "problem_statement": "Routine intake reconstruction creates avoidable handoff burden.", "affected_context": "service request intake", "supporting_statement_references": ["s-owner-cleanup", "s-coordinator-cleanup"], "qualifying_statement_references": ["s-human-review"], "judgment_note": "Caller supplied framing; burden is not a measurement."},
        "candidates": [{"candidate_id": "candidate-form-summary", "description": "Structured form with a human-reviewed summary draft.", "mechanism": "Collect required fields and produce a reviewable draft.", "scope": "routine non-emergency requests only", "dependencies": ["owner review"], "constraint_compatibility": [{"constraint_id": "c-human-review", "status": "compatible"}], "assessment_dimensions": ["reversibility", "privacy"], "supporting_references": ["s-human-review"], "weakening_references": ["s-owner-cleanup"], "unresolved_gap_references": ["g-turnaround"], "required_authorization_ids": ["a-pilot-planning"], "identity_status": "active"}],
        "assessments": [{"assessment_id": "a1", "candidate_reference": "candidate-form-summary", "dimension": "reversibility", "rating": "favorable", "rationale": "The form remains usable if the summary layer is stopped.", "evidence_references": ["s-human-review"], "gap_references": ["g-turnaround"], "judgment_note": "Caller supplied assessment."}],
        "prioritization_judgment": {"prioritization_id": "j1", "selected_candidate_id": "candidate-form-summary", "no_recommendation": False, "rationale": "Small reversible scope preserves human control.", "decisive_factors": ["reversibility", "human review"], "tradeoffs": ["does not prove savings"], "judgment_owner": "fictional owner", "version": "2026-07-17"},
        "recommendation_claims": [
            {"claim_id": "r1", "text": "Plan a routine-only human-reviewed intake pilot.", "materiality": "material", "judgment_posture": "judged", "judgment_owner": "fictional owner", "statement_references": ["s-human-review"], "qualification_references": ["s-owner-cleanup"], "contradiction_references": ["x-cleanup"], "gap_references": ["g-turnaround"]},
            {"claim_id": "r1-revised", "text": "Plan a routine non-emergency-only human-reviewed intake pilot.", "materiality": "material", "judgment_posture": "judged", "judgment_owner": "fictional owner", "statement_references": ["s-human-review"], "qualification_references": ["s-owner-cleanup"], "contradiction_references": ["x-cleanup"], "gap_references": ["g-turnaround"]},
        ],
        "evidence_links": [
            {"evidence_link_id": "el-r1", "subject_reference": {"subject_type": "recommendation_claim", "subject_id": "r1"}, "source_reference": "fs-02", "source_locator": "interview statement 12"},
            {"evidence_link_id": "el-r1-revised", "subject_reference": {"subject_type": "recommendation_claim", "subject_id": "r1-revised"}, "source_reference": "fs-11", "source_locator": "constraint 13"},
        ],
        "decision_gates": [{"gate_id": "gate-cost", "description": "Owner approves cost ceiling before technical work.", "status": "open", "gap_references": ["g-turnaround"]}],
        "authorizations": [{"authorization_id": "a-pilot-planning", "status": "authorized", "owner": "fictional owner", "scope": "implementation planning only"}],
        "non_authorizations": [{"item": "No autonomous customer communication."}, {"item": "No scheduling-system connection."}],
        "non_proofs": ["No measured savings.", "No recommendation correctness proof."],
        "next_bounded_action": {"action": "Review pilot form and data policy.", "owner": "fictional owner"},
        "disposition": {"status": "accept_with_revisions", "owner": "fictional owner", "note": "Routine non-emergency scope only."},
        "revisions": [{"revision_id": "rev1", "original_recommendation_id": "r1", "revised_recommendation_id": "r1-revised", "reason": "Disposition excluded safety-sensitive cases."}],
    }


def architecture_packet():
    packet = hvac_packet()
    packet["case_frame"].update({"case_id": "architecture-review", "objective": "Choose a bounded migration approach for an internal service.", "included_scope": ["design review"], "excluded_scope": ["production deployment"], "decision_owner": "architecture council"})
    packet["source_inventory"] = [{"source_id": "adr-1", "source_type": "design_record", "label": "Architecture decision record", "status": "supplied", "limitations": ["load test absent"], "permitted_use": ["review"]}]
    for statement in packet["statement_register"]:
        statement["source_references"] = ["adr-1"]
    packet["statement_register"][0].update({"text": "The current service has a single deployment boundary.", "classification": "observed_record"})
    packet["statement_register"][1].update({"text": "The team estimates staged migration is lower risk.", "classification": "reported_estimate"})
    packet["statement_register"][2]["text"] = "The council requires review before changing the interface."
    packet["statement_register"][3]["text"] = "Production changes require explicit approval."
    packet["constraint_register"][0].update({"text": "No production deployment without approval.", "source_or_owner_reference": "adr-1"})
    packet["evidence_links"][0]["source_reference"] = "adr-1"
    packet["evidence_links"][1]["source_reference"] = "adr-1"
    return packet


class EvidenceLinkedSynthesisTests(unittest.TestCase):
    def test_valid_hvac_packet_succeeds_and_preserves_distinct_uncertainty(self):
        packet = hvac_packet()
        result = build_evidence_linked_synthesis_package(packet)
        package = result["recommendation_package"]
        self.assertTrue(result["successful_synthesis"])
        self.assertEqual("ready", result["synthesis_status"])
        self.assertEqual("unresolved", package["contradictions"][0]["resolution_status"])
        claim = package["recommendation_claims"][0]
        self.assertEqual(["s-human-review"], claim["evidence_basis"])
        self.assertEqual(["s-owner-cleanup"], claim["qualifications"])
        self.assertEqual(["x-cleanup"], claim["contradicting_basis"])
        self.assertEqual(["g-turnaround"], claim["unresolved_gaps"])
        self.assertEqual(
            ["s-owner-cleanup"],
            package["candidate_comparison"][0]["weakening_references"],
        )
        self.assertEqual("unknown", package["missing_information"][0]["status"])
        self.assertIn("No measured savings.", package["explicit_non_proofs"]["items"])
        self.assertIn(package["recommendation_claims"][0]["judgment_posture"], TRANSFORMATION_POSTURES)

    def test_materially_different_architecture_fixture_uses_same_contract(self):
        result = build_evidence_linked_synthesis_package(architecture_packet())
        self.assertTrue(result["successful_synthesis"])
        self.assertEqual("architecture-review", result["recommendation_package"]["case_frame"]["case_id"])

    def test_statement_value_and_assessment_classification_are_accepted(self):
        packet = hvac_packet()
        packet["statement_register"][0]["value"] = packet["statement_register"][0].pop("text")
        packet["assessments"][0]["classification"] = packet["assessments"][0].pop("rating")
        result = build_evidence_linked_synthesis_package(packet)
        self.assertTrue(result["successful_synthesis"])
        self.assertEqual(
            "Owner guesses at least one hour daily of cleanup.",
            result["recommendation_package"]["evidence_summary"]["statements"][0]["text"],
        )
        self.assertEqual(
            "favorable",
            result["recommendation_package"]["risks_and_failure_modes"]["assessments"][0]["rating"],
        )

    def test_unsupported_material_claim_blocks(self):
        packet = hvac_packet()
        packet["evidence_links"] = []
        result = build_evidence_linked_synthesis_package(packet)
        self.assertFalse(result["successful_synthesis"])
        self.assertIn("material_recommendation_claim_requires_registered_basis:r1", result["validation_errors"])

    def test_missing_association_target_blocks_without_repair(self):
        packet = hvac_packet()
        packet["evidence_links"][0]["source_reference"] = "missing-source"
        packet["evidence_links"][1]["subject_reference"]["subject_id"] = "missing-claim"
        result = build_evidence_linked_synthesis_package(packet)
        self.assertIn("evidence_link_source_reference_missing:missing-source", result["validation_errors"])
        self.assertIn("evidence_link_subject_reference_missing:missing-claim", result["validation_errors"])

    def test_critical_gap_and_hard_constraint_violation_block(self):
        packet = hvac_packet()
        packet["missing_information_register"][0]["blocking_level"] = "critical"
        packet["candidates"][0]["constraint_compatibility"][0]["status"] = "violated"
        result = build_evidence_linked_synthesis_package(packet)
        self.assertIn("critical_gap_blocks_synthesis:g-turnaround", result["validation_errors"])
        self.assertIn("hard_constraint_violated:candidate-form-summary:c-human-review", result["validation_errors"])

    def test_not_applicable_is_explicit_and_not_inferred_from_absence(self):
        packet = hvac_packet()
        packet["missing_information_register"][0]["status"] = "not_applicable"
        packet["missing_information_register"][0]["blocking_level"] = "critical"
        result = build_evidence_linked_synthesis_package(packet)
        self.assertTrue(result["successful_synthesis"])
        self.assertEqual("not_applicable", result["recommendation_package"]["missing_information"][0]["status"])

    def test_retired_identity_missing_authorization_and_bad_revision_block(self):
        packet = hvac_packet()
        packet["candidates"][0]["identity_status"] = "retired"
        packet["authorizations"][0]["status"] = "pending"
        packet["revisions"][0]["revised_recommendation_id"] = "r1"
        result = build_evidence_linked_synthesis_package(packet)
        self.assertIn("selected_candidate_identity_not_active:candidate-form-summary", result["validation_errors"])
        self.assertIn("required_authorization_absent:a-pilot-planning", result["validation_errors"])
        self.assertIn("revision_must_reference_distinct_original_and_revised_recommendations:rev1", result["validation_errors"])

    def test_output_is_deterministic_and_input_is_unchanged(self):
        packet = hvac_packet()
        original = copy.deepcopy(packet)
        first = build_evidence_linked_synthesis_package(packet)
        second = build_evidence_linked_synthesis_package(packet)
        self.assertEqual(packet, original)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        self.assertIn("evidence_link_does_not_establish_truth", first["recommendation_package"]["evidence_associations"]["non_proofs"])


if __name__ == "__main__":
    unittest.main()
