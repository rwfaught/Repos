import copy
import json
import unittest

from orchestrator.local_ai_consulting_campaign import (
    ARCHITECTURE_DECISION,
    EXPLICIT_NON_PROOFS,
    REQUIRED_SCENARIO_FIELDS,
    build_consulting_scenario_library,
    build_local_ai_consulting_campaign_readback,
    build_owner_packet,
    classify_consulting_scenario,
    review_owner_packet,
)


class LocalAIConsultingCampaignTests(unittest.TestCase):
    def test_library_has_required_four_fixture_scenarios(self):
        library = build_consulting_scenario_library()

        self.assertEqual(
            set(library),
            {
                "internal_knowledge_helpdesk",
                "owner_reviewed_drafting_reporting",
                "regulated_sensitive_data",
                "external_integration_heavy",
            },
        )
        for scenario in library.values():
            self.assertEqual(set(REQUIRED_SCENARIO_FIELDS), set(scenario))

    def test_low_risk_complete_flow_is_owner_review_ready(self):
        scenario = build_consulting_scenario_library()["internal_knowledge_helpdesk"]
        packet = build_owner_packet(scenario)
        review = review_owner_packet(packet)

        self.assertTrue(review["structurally_complete"])
        self.assertTrue(review["owner_review_ready"])
        self.assertFalse(review["execution_authorized"])
        self.assertTrue(packet["safe_to_explore_locally"])
        self.assertTrue(packet["needs_owner_approval"])

    def test_missing_inputs_are_visible_and_block_readiness(self):
        scenario = copy.deepcopy(build_consulting_scenario_library()["owner_reviewed_drafting_reporting"])
        scenario["owner_objective"] = ""

        review = classify_consulting_scenario(scenario)

        self.assertEqual(review["readiness_status"], "missing_input")
        self.assertIn("owner_objective", review["missing_inputs"])
        self.assertFalse(review["owner_review_ready"])

    def test_sensitive_data_blocks_automation_but_preserves_owner_questions(self):
        scenario = build_consulting_scenario_library()["regulated_sensitive_data"]
        packet = build_owner_packet(scenario)
        review = review_owner_packet(packet)

        self.assertEqual(review["readiness_status"], "blocked_by_sensitivity")
        self.assertTrue(review["blocked_by_sensitivity"])
        self.assertFalse(packet["safe_to_explore_locally"])
        self.assertTrue(packet["needs_owner_approval"])
        self.assertTrue(packet["do_not_automate_yet"])

    def test_external_integration_scenario_is_deferred(self):
        scenario = build_consulting_scenario_library()["external_integration_heavy"]
        packet = build_owner_packet(scenario)
        review = review_owner_packet(packet)

        self.assertEqual(review["readiness_status"], "blocked_by_external_integration")
        self.assertTrue(review["blocked_by_external_integration"])
        self.assertEqual(
            packet["requires_external_integration"],
            scenario["requested_external_integrations"],
        )
        self.assertFalse(packet["execution_authorized"])

    def test_owner_review_gate_is_explicit_for_drafting_reporting(self):
        scenario = build_consulting_scenario_library()["owner_reviewed_drafting_reporting"]
        packet = build_owner_packet(scenario)

        self.assertTrue(packet["owner_approval_required"])
        self.assertIn("owner approves the review boundary before implementation", packet["needs_owner_approval"])
        self.assertFalse(packet["execution_authorized"])

    def test_campaign_output_is_deterministic_and_compares_all_scenarios(self):
        first = build_local_ai_consulting_campaign_readback()
        second = build_local_ai_consulting_campaign_readback()

        self.assertEqual(first, second)
        self.assertEqual(first["scenario_count"], 4)
        self.assertEqual(first["architecture_decision"]["decision"], ARCHITECTURE_DECISION)
        self.assertEqual(
            first["comparison"]["readiness_status_by_scenario"],
            {
                "internal_knowledge_helpdesk": "owner_review_ready",
                "owner_reviewed_drafting_reporting": "owner_review_ready",
                "regulated_sensitive_data": "blocked_by_sensitivity",
                "external_integration_heavy": "blocked_by_external_integration",
            },
        )
        json.dumps(first, sort_keys=True)

    def test_neutral_bridge_preserves_objective_and_declares_structural_only_readiness(self):
        campaign = build_local_ai_consulting_campaign_readback()
        readback = campaign["scenario_readbacks"]["internal_knowledge_helpdesk"]
        scenario = readback["scenario"]
        bridge = readback["neutral_dossier_case_bridge"]

        self.assertEqual(bridge["adapted_dossier_case"]["objective"], scenario["owner_objective"])
        self.assertTrue(bridge["neutral_task_readiness"]["structurally_ready_for_domain_specific_work"])
        self.assertFalse(bridge["neutral_task_readiness"]["product_wedge_selected"])
        self.assertIn("adapter bridge only", bridge["architecture_posture"])

    def test_non_proofs_and_lockouts_survive_every_campaign_readback(self):
        campaign = build_local_ai_consulting_campaign_readback()

        self.assertEqual(tuple(campaign["explicit_non_proofs"]), EXPLICIT_NON_PROOFS)
        self.assertEqual(campaign["product_wedge_posture"], "no first product wedge selected")
        self.assertEqual(campaign["phase_387_posture"], "Phase 387 remains unset/not resumed")
        self.assertFalse(campaign["execution_posture"]["runtime_provider_model_execution"])
        self.assertFalse(campaign["execution_posture"]["external_integration_execution"])
        for readback in campaign["scenario_readbacks"].values():
            self.assertTrue(readback["self_review"]["sandbox_only_not_production_proof"])
            self.assertFalse(readback["owner_packet"]["execution_authorized"])
            self.assertEqual(tuple(readback["explicit_non_proofs"]), EXPLICIT_NON_PROOFS)


if __name__ == "__main__":
    unittest.main()
