import unittest

from orchestrator.local_ai_consulting_audit_packet import (
    AUDIT_INTAKE_REQUIRED_FIELDS,
    BOUNDARY,
    EXPLICIT_NON_PROOFS,
    NO_FIRST_PRODUCT_WEDGE_SELECTED,
    OFFER,
    PHASE_387_REMAINS_UNSET,
    SCENARIO,
    build_audit_intake,
    build_audit_review_gate,
    build_dossier_case_bridge_readback,
    build_client_readable_audit_report,
    build_internal_implementation_packet,
    build_local_ai_consulting_audit_flow,
    build_local_ai_consulting_case_packet,
    build_local_ai_consulting_fixture_library,
    build_local_ai_consulting_readback,
    build_springfield_hvac_fixture,
    classify_do_not_automate_yet,
    classify_risk_privacy_posture,
)


class LocalAIConsultingAuditPacketTests(unittest.TestCase):
    def test_fixture_library_and_intake_contain_required_fields(self):
        library = build_local_ai_consulting_fixture_library()
        fixture = build_springfield_hvac_fixture()
        intake = build_audit_intake()

        self.assertIn("springfield_hvac", library)
        self.assertEqual(fixture["scenario"], SCENARIO)
        self.assertEqual(intake["boundary"], BOUNDARY)
        self.assertEqual(intake["offer"], OFFER)
        self.assertEqual(set(AUDIT_INTAKE_REQUIRED_FIELDS), set(intake) - {
            "intake_name", "fixture_name", "intake_status", "boundary",
            "scenario", "phase_387_posture", "product_wedge_posture",
        })

    def test_intake_and_each_generated_surface_are_deterministic(self):
        self.assertEqual(build_audit_intake(), build_audit_intake())
        self.assertEqual(build_audit_review_gate(), build_audit_review_gate())
        self.assertEqual(build_internal_implementation_packet(), build_internal_implementation_packet())
        self.assertEqual(build_client_readable_audit_report(), build_client_readable_audit_report())
        self.assertEqual(build_local_ai_consulting_readback(), build_local_ai_consulting_readback())
        self.assertEqual(build_local_ai_consulting_audit_flow(), build_local_ai_consulting_audit_flow())

    def test_risk_privacy_posture_is_preserved_and_requires_review(self):
        classification = classify_risk_privacy_posture()
        fixture = build_springfield_hvac_fixture()

        self.assertEqual(classification["classification"], "bounded_but_human_review_required")
        self.assertTrue(classification["review_required"])
        self.assertEqual(classification["controls"], fixture["risk_privacy_posture"])
        self.assertIn("privacy and redaction", classification["risk_categories"])
        self.assertIn("no autonomous action", classification["automation_boundary"])

    def test_do_not_automate_yet_items_are_preserved(self):
        classification = classify_do_not_automate_yet()
        fixture = build_springfield_hvac_fixture()

        self.assertEqual(
            [item["item"] for item in classification["items"]],
            fixture["do_not_automate_yet"],
        )
        self.assertTrue(classification["human_decision_required"])
        self.assertFalse(classification["external_integration_allowed"])

    def test_review_gate_preserves_questions_contradictions_and_blocks_execution(self):
        intake = build_audit_intake()
        gate = build_audit_review_gate(intake)

        self.assertEqual(gate["review_decision"], "ready_for_owner_review")
        self.assertEqual(gate["missing_required_intake_fields"], [])
        self.assertTrue(intake["open_questions"])
        self.assertTrue(intake["contradictions_or_unclear_claims"])
        self.assertTrue(gate["operator_approval_required"])
        self.assertFalse(gate["execution_authorized"])

    def test_case_packet_bridge_reuses_neutral_dossier_and_readiness_surfaces(self):
        intake = build_audit_intake()
        case_packet = build_local_ai_consulting_case_packet(intake)
        bridge = build_dossier_case_bridge_readback(intake)

        for field in (
            "case_id", "case_type", "title", "objective", "source_materials",
            "extracted_facts", "timeline_events", "open_issues",
            "missing_evidence", "contradictions", "drafts", "decisions",
            "status", "next_step",
        ):
            self.assertIn(field, case_packet)
        self.assertEqual(bridge["neutral_task_readiness"]["missing_required_neutral_fields"], [])
        self.assertTrue(bridge["neutral_task_readiness"]["structurally_ready_for_domain_specific_work"])
        self.assertEqual(bridge["neutral_task_readiness"]["open_questions"], intake["open_questions"])
        self.assertEqual(bridge["neutral_task_readiness"]["contradictions"], intake["contradictions_or_unclear_claims"])
        self.assertFalse(bridge["neutral_task_readiness"]["product_wedge_selected"])
        self.assertFalse(bridge["neutral_task_readiness"]["phase_387_implemented"])
        self.assertTrue(all(bridge["preservation_checks"].values()))

    def test_bridge_is_deterministic_and_declares_adapter_posture(self):
        first = build_dossier_case_bridge_readback()
        second = build_dossier_case_bridge_readback()

        self.assertEqual(first, second)
        self.assertIn("adapter bridge only", first["architecture_posture"])
        self.assertIn("not semantic correctness", first["explicit_non_proofs"])

    def test_internal_packet_contains_readback_and_governance_posture(self):
        packet = build_internal_implementation_packet()

        for field in (
            "audit_id", "objective", "business_profile", "source_materials",
            "workflow_facts", "friction_nodes", "repeated_tasks",
            "candidate_ai_interventions", "risk_privacy_posture",
            "risk_privacy_classification", "open_questions",
            "contradictions_or_unclear_claims", "recommended_first_implementation",
            "do_not_automate_yet", "do_not_automate_yet_classification",
            "explicit_non_proofs", "review_gate", "operator_next_action",
        ):
            self.assertIn(field, packet)

        self.assertFalse(packet["execution_posture"]["runtime_provider_model_execution"])
        self.assertFalse(packet["execution_posture"]["production_readiness"])
        self.assertFalse(packet["execution_posture"]["first_product_wedge_selected"])
        self.assertFalse(packet["execution_posture"]["phase_387_resumed"])

    def test_client_report_and_full_flow_work_from_intake_to_report(self):
        flow = build_local_ai_consulting_audit_flow()
        report = flow["client_readable_audit_report"]

        for field in (
            "audit_objective", "business_snapshot", "source_basis", "workflow_facts",
            "workflow_friction", "repeated_tasks", "candidate_ai_interventions",
            "risk_privacy_posture", "risk_privacy_classification",
            "recommended_first_implementation", "what_not_to_automate_yet",
            "what_not_to_automate_yet_classification",
            "questions_roger_should_ask_the_owner",
            "contradictions_or_unclear_claims", "review_gate_summary",
            "neutral_dossier_case_readiness",
            "operator_next_action", "explicit_non_proofs",
        ):
            self.assertIn(field, report)

        self.assertIn("missed-call", report["recommended_first_implementation"])
        self.assertEqual(report["review_gate_summary"]["review_decision"], "ready_for_owner_review")

    def test_non_proofs_product_wedge_and_phase_postures_are_explicit(self):
        readback = build_local_ai_consulting_readback()

        self.assertEqual(readback["product_wedge_posture"], NO_FIRST_PRODUCT_WEDGE_SELECTED)
        self.assertEqual(readback["phase_387_posture"], PHASE_387_REMAINS_UNSET)
        self.assertEqual(tuple(readback["explicit_non_proofs"]), EXPLICIT_NON_PROOFS)
        self.assertIn("not runtime/provider/model execution", readback["explicit_non_proofs"])
        self.assertIn("not production readiness", readback["explicit_non_proofs"])
        self.assertFalse(readback["review_gate"]["product_wedge_selected"])
        self.assertFalse(readback["review_gate"]["phase_387_resumed"])

    def test_no_runtime_or_provider_model_execution_is_implied(self):
        readback = build_local_ai_consulting_readback()
        packet = readback["internal_implementation_packet"]
        report = readback["client_readable_audit_report"]

        self.assertFalse(packet["execution_posture"]["runtime_provider_model_execution"])
        self.assertFalse(packet["execution_posture"]["production_readiness"])
        self.assertFalse(report["review_gate_summary"]["execution_authorized"])
        self.assertIn("no autonomous action", packet["risk_privacy_classification"]["automation_boundary"])


if __name__ == "__main__":
    unittest.main()
