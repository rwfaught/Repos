import json
import unittest

from orchestrator.objective_route_packet_loop import (
    build_objective_route_packet,
    infer_objective_capability_task,
    render_objective_route_packet_markdown,
)


class ObjectiveRoutePacketLoopTests(unittest.TestCase):
    CASES = {
        "Classify this fixed status list into three labels": "deterministic_code_only",
        "Summarize these internal policy notes for staff review": "local_model_candidate",
        "Design a multi-module architecture migration with compatibility constraints": "frontier_model_or_codex_required",
        "Review this regulated financial decision with sensitive personal data": "human_review_or_blocked",
        "Sync live CRM records through an external API": "external_api_required",
    }

    def test_objective_signal_inference_is_deterministic(self):
        for objective in self.CASES:
            first = infer_objective_capability_task(objective)
            second = infer_objective_capability_task(objective)
            with self.subTest(objective=objective):
                self.assertEqual(first, second)
                self.assertTrue(first["capability_task"])
                self.assertTrue(first["matched_signals"])

    def test_objectives_reach_expected_routes(self):
        for objective, expected_route in self.CASES.items():
            loop = build_objective_route_packet(objective)
            with self.subTest(objective=objective):
                self.assertEqual(loop["route_readback"]["route"], expected_route)
                self.assertIsNotNone(loop["owner_review_packet"])
                self.assertFalse(loop["route_readback"]["execution_authorized"])

    def test_loop_connects_route_to_packet_and_neutral_bridge(self):
        loop = build_objective_route_packet("Summarize these internal policy notes for staff review")
        packet = loop["owner_review_packet"]
        bridge = loop["neutral_dossier_case_bridge"]

        self.assertEqual(packet["route"], "local_model_candidate")
        self.assertTrue(packet["safe_to_attempt_locally"])
        self.assertTrue(packet["owner_review_required"])
        self.assertTrue(packet["deterministic_first"])
        self.assertTrue(bridge["neutral_task_readiness"]["structurally_ready_for_domain_specific_work"])
        self.assertFalse(bridge["neutral_task_readiness"]["product_wedge_selected"])
        self.assertIn("neutral dossier/case adapter remains authoritative", bridge["architecture_posture"])
        json.dumps(loop, sort_keys=True)

    def test_route_posture_explains_executor_choices(self):
        expectations = {
            "Summarize these internal policy notes for staff review": (True, False, False, True),
            "Design a multi-module architecture migration with compatibility constraints": (False, True, False, True),
            "Sync live CRM records through an external API": (False, False, True, True),
        }
        for objective, expected in expectations.items():
            posture = build_objective_route_packet(objective)["route_readback"]["posture"]
            with self.subTest(objective=objective):
                self.assertEqual(
                    (
                        posture["local_model_attempt_appropriate"],
                        posture["frontier_or_codex_needed"],
                        posture["external_api_needed"],
                        posture["human_review_required"],
                    ),
                    expected,
                )

    def test_unknown_objective_is_honestly_blocked_for_clarification(self):
        loop = build_objective_route_packet("Please handle this thing")

        self.assertEqual(loop["route_readback"]["route"], "human_review_or_blocked")
        self.assertIsNone(loop["owner_review_packet"])
        self.assertIn("task_type", loop["objective_intake"]["clarification_needed"])
        self.assertIn("not natural-language intent understanding", loop["explicit_non_proofs"])

    def test_markdown_is_operator_readable_and_not_raw_json(self):
        rendered = render_objective_route_packet_markdown(
            build_objective_route_packet("Summarize these internal policy notes for staff review")
        )

        self.assertIn("# Objective-to-Route V1 Candidate Readback", rendered)
        self.assertIn("## Routing Decision", rendered)
        self.assertIn("## Deterministic First", rendered)
        self.assertIn("## Owner-Review Packet", rendered)
        self.assertIn("## Next Bounded Action", rendered)
        self.assertIn("not model execution", rendered)
        self.assertNotIn('"route":', rendered)


if __name__ == "__main__":
    unittest.main()
