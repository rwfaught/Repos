import unittest

from orchestrator.goal_intake_to_bounded_task_packet import (
    BOUNDARY,
    DOGWALKING_APP_GOAL,
    EXPLICIT_NON_PROOFS,
    PKMS_REORGANIZATION_GOAL,
    RECOMMENDED_NEXT_BOUNDARY,
    build_goal_intake_to_bounded_task_packet_dict,
    render_goal_intake_to_bounded_task_packet_markdown,
)


class GoalIntakeToBoundedTaskPacketTests(unittest.TestCase):
    def test_packet_builds_as_dict_with_exact_boundary(self):
        packet = build_goal_intake_to_bounded_task_packet_dict()

        self.assertIsInstance(packet, dict)
        self.assertEqual(packet["boundary"], BOUNDARY)
        self.assertEqual(
            packet["boundary"],
            "GOAL_INTAKE_TO_BOUNDED_TASK_PACKET_VERTICAL_SLICE_SOURCE_TEST_DOCS",
        )

    def test_dogwalking_goal_produces_reviewable_bounded_task_packet(self):
        packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)

        self.assertEqual(
            packet["intake_status"],
            "candidate_task_packet_ready_for_operator_review",
        )
        self.assertIsInstance(packet["next_bounded_task_packet"], dict)
        self.assertFalse(packet["next_bounded_task_packet"]["dispatch_authorized"])
        self.assertTrue(packet["next_bounded_task_packet"]["operator_approval_required"])
        self.assertIn("no file mutation", packet["next_bounded_task_packet"]["files_in_scope"])
        self.assertIn("dogwalking", packet["operator_goal"])
        self.assertIn("payment and liability posture", packet["missing_inputs"])

    def test_pkms_goal_stops_for_clarification_without_task_packet(self):
        packet = build_goal_intake_to_bounded_task_packet_dict(PKMS_REORGANIZATION_GOAL)

        self.assertEqual(packet["intake_status"], "needs_operator_clarification")
        self.assertIsNone(packet["next_bounded_task_packet"])
        self.assertIn("PKMS root path", packet["missing_inputs"])
        self.assertIn("bulk file mutation", packet["risk_flags"])
        self.assertTrue(
            any("allowed mutation scope" in question for question in packet["clarification_questions"])
        )

    def test_route_posture_preserves_local_first_and_frontier_escalation_logic(self):
        packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
        route = packet["route_posture"]

        self.assertEqual(route["recommended_route"], "human_reviewed_bounded_worker_packet")
        self.assertIn("local", route["local_first_posture"])
        self.assertIn("frontier", route["frontier_escalation_posture"])
        self.assertFalse(route["execution_allowed"])

    def test_clarification_route_does_not_dispatch(self):
        packet = build_goal_intake_to_bounded_task_packet_dict(PKMS_REORGANIZATION_GOAL)
        route = packet["route_posture"]

        self.assertEqual(route["recommended_route"], "ask_operator_clarifying_questions")
        self.assertIn("do_not_dispatch", route["local_first_posture"])
        self.assertFalse(route["execution_allowed"])
        self.assertFalse(packet["task_dispatched"])

    def test_false_flags_remain_false(self):
        packet = build_goal_intake_to_bounded_task_packet_dict()

        for flag in (
            "runtime_required",
            "provider_model_required",
            "live_coordinator_reasoning_claimed",
            "autonomous_decomposition_claimed",
            "task_dispatched",
            "mutation_authorized",
            "local_model_executed",
            "frontier_model_executed",
            "semantic_correctness_proven",
            "production_readiness_claimed",
            "phase_387_implemented",
            "first_product_wedge_selected",
        ):
            self.assertIs(packet[flag], False, flag)

    def test_explicit_non_proofs_are_visible(self):
        packet = build_goal_intake_to_bounded_task_packet_dict()

        for non_proof in EXPLICIT_NON_PROOFS:
            self.assertIn(non_proof, packet["explicit_non_proofs"])
        for required in (
            "no runtime/provider/model execution",
            "no live coordinator reasoning proof",
            "no autonomous task dispatch proof",
            "no local model capability proof",
            "no frontier model escalation proof",
            "no production readiness proof",
            "no first product wedge selection",
        ):
            self.assertIn(required, packet["explicit_non_proofs"])

    def test_rendered_markdown_is_roger_legible(self):
        rendered = render_goal_intake_to_bounded_task_packet_markdown()

        for heading in (
            "## What Went In",
            "## What Orchestrator Did",
            "## Missing Inputs",
            "## Clarification Questions",
            "## What Came Out",
            "## What Roger Can Judge",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("Recommended route", rendered)
        self.assertIn("Local-first posture", rendered)
        self.assertIn("Frontier escalation posture", rendered)
        self.assertIn("recommended_next_boundary=", rendered)

    def test_recommended_next_boundary_is_readonly_review(self):
        packet = build_goal_intake_to_bounded_task_packet_dict()

        self.assertEqual(packet["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertTrue(packet["recommended_next_boundary"].endswith("_REVIEW_READONLY"))


if __name__ == "__main__":
    unittest.main()
