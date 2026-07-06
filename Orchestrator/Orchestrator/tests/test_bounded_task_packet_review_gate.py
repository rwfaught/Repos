import unittest

from orchestrator.bounded_task_packet_review_gate import (
    BOUNDARY,
    EXPLICIT_NON_PROOFS,
    RECOMMENDED_NEXT_BOUNDARY,
    build_bounded_task_packet_review_gate_dict,
    render_bounded_task_packet_review_gate_markdown,
)
from orchestrator.goal_intake_to_bounded_task_packet import (
    DOGWALKING_APP_GOAL,
    PKMS_REORGANIZATION_GOAL,
    build_goal_intake_to_bounded_task_packet_dict,
)


class BoundedTaskPacketReviewGateTests(unittest.TestCase):
    def test_review_gate_builds_as_dict_with_exact_boundary(self):
        review = build_bounded_task_packet_review_gate_dict()

        self.assertIsInstance(review, dict)
        self.assertEqual(review["boundary"], BOUNDARY)
        self.assertEqual(review["boundary"], "BOUNDED_TASK_PACKET_REVIEW_GATE_SOURCE_TEST_DOCS")

    def test_dogwalking_packet_is_ready_for_roger_approval_not_execution(self):
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
        review = build_bounded_task_packet_review_gate_dict(goal_packet)

        self.assertEqual(review["review_decision"], "ready_for_roger_approval")
        self.assertEqual(review["blocked_conditions"], [])
        self.assertEqual(review["missing_requirements"], [])
        self.assertTrue(review["roger_approval_surface"]["approval_required_before_dispatch"])
        self.assertFalse(review["worker_dispatched"])
        self.assertFalse(review["task_execution_authorized"])
        self.assertFalse(review["mutation_authorized"])

    def test_pkms_clarification_packet_remains_blocked_without_task_packet(self):
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(PKMS_REORGANIZATION_GOAL)
        review = build_bounded_task_packet_review_gate_dict(goal_packet)

        self.assertEqual(review["review_decision"], "blocked_for_operator_clarification")
        self.assertIn("intake_requires_operator_clarification", review["blocked_conditions"])
        self.assertIn("PKMS root path", review["missing_requirements"])
        self.assertEqual(review["task_packet_summary"], {})
        self.assertFalse(review["worker_dispatched"])

    def test_missing_task_packet_fields_require_repair(self):
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
        del goal_packet["next_bounded_task_packet"]["success_criteria"]

        review = build_bounded_task_packet_review_gate_dict(goal_packet)

        self.assertEqual(review["review_decision"], "needs_packet_repair")
        self.assertIn("bounded_task_packet_missing_required_fields", review["blocked_conditions"])
        self.assertIn("success_criteria", review["missing_requirements"])

    def test_missing_file_scope_requires_repair(self):
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
        del goal_packet["next_bounded_task_packet"]["files_in_scope"]

        review = build_bounded_task_packet_review_gate_dict(goal_packet)

        self.assertEqual(review["review_decision"], "needs_packet_repair")
        self.assertIn("bounded_task_packet_missing_required_fields", review["blocked_conditions"])
        self.assertIn("files_in_scope", review["missing_requirements"])

    def test_dispatch_authority_smuggling_requires_repair(self):
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
        goal_packet["next_bounded_task_packet"]["dispatch_authorized"] = True

        review = build_bounded_task_packet_review_gate_dict(goal_packet)

        self.assertEqual(review["review_decision"], "needs_packet_repair")
        self.assertIn(
            "dispatch_authorization_must_remain_false_before_operator_approval",
            review["blocked_conditions"],
        )
        self.assertFalse(review["task_execution_authorized"])

    def test_operator_approval_flag_is_required(self):
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
        goal_packet["next_bounded_task_packet"]["operator_approval_required"] = False

        review = build_bounded_task_packet_review_gate_dict(goal_packet)

        self.assertEqual(review["review_decision"], "needs_packet_repair")
        self.assertIn("operator_approval_required_flag_missing", review["blocked_conditions"])
        self.assertIn("operator_approval_required_true", review["missing_requirements"])

    def test_roger_approval_surface_has_actionable_answers(self):
        review = build_bounded_task_packet_review_gate_dict()
        answers = review["roger_approval_surface"]["allowed_answers"]

        for answer in (
            "approve_next_boundary",
            "request_packet_repair",
            "answer_clarification_questions",
            "stop_or_reframe_goal",
        ):
            self.assertIn(answer, answers)

    def test_false_flags_remain_false(self):
        review = build_bounded_task_packet_review_gate_dict()

        for flag in (
            "runtime_required",
            "provider_model_required",
            "worker_dispatched",
            "task_execution_authorized",
            "mutation_authorized",
            "local_model_executed",
            "frontier_model_executed",
            "semantic_correctness_proven",
            "production_readiness_claimed",
            "phase_387_implemented",
            "first_product_wedge_selected",
        ):
            self.assertIs(review[flag], False, flag)

    def test_explicit_non_proofs_are_visible(self):
        review = build_bounded_task_packet_review_gate_dict()

        for non_proof in EXPLICIT_NON_PROOFS:
            self.assertIn(non_proof, review["explicit_non_proofs"])
        for required in (
            "no autonomous task dispatch proof",
            "no worker execution proof",
            "no local model capability proof",
            "no frontier model escalation proof",
            "no first product wedge selection",
        ):
            self.assertIn(required, review["explicit_non_proofs"])

    def test_rendered_markdown_preserves_gate_shape(self):
        rendered = render_bounded_task_packet_review_gate_markdown()

        for heading in (
            "## Source Intake",
            "## Review Decision",
            "## Blocked Conditions",
            "## Missing Requirements",
            "## Roger Approval Surface",
            "## Task Packet Summary",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("### Files In Scope", rendered)
        self.assertIn("Decision: ready_for_roger_approval", rendered)
        self.assertIn("Approval required before dispatch: True", rendered)
        self.assertIn("worker_dispatched=False", rendered)
        self.assertIn("recommended_next_boundary=", rendered)

    def test_recommended_next_boundary_is_readonly_review(self):
        review = build_bounded_task_packet_review_gate_dict()

        self.assertEqual(review["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertTrue(review["recommended_next_boundary"].endswith("_REVIEW_READONLY"))


if __name__ == "__main__":
    unittest.main()
