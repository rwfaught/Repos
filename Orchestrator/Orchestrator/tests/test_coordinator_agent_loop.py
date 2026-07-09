import json
import unittest

from orchestrator.coordinator_agent_loop import (
    CapabilityRoute,
    OperatorPrompt,
    ReviewEvaluation,
    WorkerResult,
    create_coordinator_closeout,
    evaluate_worker_result,
    run_dry_coordinator_loop,
)


class CoordinatorAgentLoopTests(unittest.TestCase):
    def test_typed_interfaces_are_present_in_dry_loop(self):
        loop = run_dry_coordinator_loop(
            OperatorPrompt("prompt-001", "Classify this fixed status list into three labels")
        )

        self.assertEqual(loop["intake_interpretation"]["interpretation_source"], "deterministic_stub_intake_future_local_model_seam")
        self.assertEqual(loop["capability_route"]["route_name"], "deterministic_code_only")
        self.assertEqual(loop["coordinator_plan"]["worker_type"], "deterministic_local_worker")
        self.assertEqual(loop["worker_handoff"]["handoff_status"], "prepared_not_dispatched")
        self.assertEqual(loop["review_evaluation"]["action"], "accept")
        self.assertEqual(loop["coordinator_closeout"]["status"], "accept")
        json.dumps(loop, sort_keys=True)

    def test_each_route_selects_expected_worker_type_without_dispatch(self):
        cases = {
            "Classify this fixed status list into three labels": "deterministic_local_worker",
            "Summarize these internal policy notes for staff review": "local_model_worker",
            "Design a multi-module architecture migration with compatibility constraints": "frontier_codex_worker",
            "Sync live CRM records through an external API": "external_api_worker",
            "Review this regulated financial decision with sensitive personal data": "human_review_worker",
        }
        for objective, worker_type in cases.items():
            loop = run_dry_coordinator_loop(objective)
            with self.subTest(objective=objective):
                self.assertEqual(loop["capability_route"]["worker_type"], worker_type)
                self.assertFalse(loop["worker_handoff"]["dispatched"])
                self.assertFalse(loop["execution_posture"]["worker_dispatch"])

    def test_deterministic_result_is_accepted(self):
        loop = run_dry_coordinator_loop("Classify this fixed status list into three labels")

        self.assertEqual(loop["worker_result"]["status"], "success")
        self.assertTrue(loop["worker_result"]["validation_passed"])
        self.assertTrue(loop["review_evaluation"]["result_accepted"])
        self.assertFalse(loop["worker_result"]["execution_performed"])

    def test_bad_result_requests_retry_then_escalates_after_retry_budget(self):
        route = CapabilityRoute(
            "deterministic_code_only", "deterministic_local_worker", "test", True, True, False, ()
        )
        result = WorkerResult("result-1", "handoff-1", "failed", "bad stub", False, False, "validation_failed")

        retry = evaluate_worker_result(route, result, retry_count=0)
        exhausted = evaluate_worker_result(route, result, retry_count=1)

        self.assertEqual(retry.action, "needs_retry")
        self.assertEqual(exhausted.action, "escalate")

    def test_frontier_api_and_human_routes_do_not_execute_and_review_correctly(self):
        expectations = {
            "Design a multi-module architecture migration with compatibility constraints": "escalate",
            "Sync live CRM records through an external API": "escalate",
            "Review this regulated financial decision with sensitive personal data": "blocked",
            "Summarize these internal policy notes for staff review": "needs_operator_clarification",
        }
        for objective, action in expectations.items():
            loop = run_dry_coordinator_loop(objective)
            with self.subTest(objective=objective):
                self.assertEqual(loop["review_evaluation"]["action"], action)
                self.assertFalse(loop["execution_posture"]["model_execution"])
                self.assertFalse(loop["execution_posture"]["provider_execution"])

    def test_unknown_objective_requires_operator_clarification(self):
        loop = run_dry_coordinator_loop("Please handle this thing")

        self.assertEqual(loop["capability_route"]["route_name"], "human_review_or_blocked")
        self.assertEqual(loop["review_evaluation"]["action"], "blocked")
        self.assertIn("resolves", loop["coordinator_closeout"]["next_bounded_action"])

    def test_closeout_preserves_non_execution_posture(self):
        evaluation = ReviewEvaluation("accept", "test accepted", 0, True, False)
        route = CapabilityRoute("deterministic_code_only", "deterministic_local_worker", "test", True, True, False, ())
        closeout = create_coordinator_closeout(route, evaluation)

        self.assertEqual(closeout.status, "accept")
        self.assertFalse(closeout.execution_performed)
        self.assertFalse(closeout.coordinator_closeout_authorized)


if __name__ == "__main__":
    unittest.main()
