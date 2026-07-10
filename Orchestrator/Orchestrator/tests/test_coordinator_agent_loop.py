import json
import unittest

from orchestrator.local_model_provider_stub import DisabledLocalModelProvider, StaticLocalModelProvider
from orchestrator.local_model_provider_adapter import InjectedLocalModelProvider
from orchestrator.coordinator_agent_loop import (
    CapabilityRoute,
    OperatorPrompt,
    ReviewEvaluation,
    WorkerResult,
    create_coordinator_closeout,
    evaluate_worker_result,
    run_dry_coordinator_loop,
)


def model_response_for(objective, prompt_id="prompt-001"):
    return {
        "contract_version": "local_model_reasoning_v1",
        "request_id": prompt_id,
        "objective": objective,
        "normalized_objective": objective.lower(),
        "capability_task": {
            "task_id": "task-001",
            "title": "Classify supplied labels",
            "objective": objective,
            "complexity": "simple",
            "code_generation_required": False,
            "long_context_required": False,
            "safety_risk": "low",
            "privacy_sensitivity": "internal",
            "external_tool_or_api_need": False,
            "live_runtime_execution_need": False,
            "tolerance_for_mistakes": "medium",
            "deterministic_validation_available": True,
            "local_model_output_reviewable": True,
        },
        "matched_signals": {"deterministic": ["fixed labels"]},
        "confidence": 0.91,
        "clarification_needed": [],
        "risk_flags": [],
        "assumptions": [],
    }


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

    def test_validated_model_stub_interpretation_is_consumed_before_deterministic_policy(self):
        objective = "Classify this fixed status list into three labels"
        loop = run_dry_coordinator_loop(
            objective,
            reasoning_provider=StaticLocalModelProvider(model_response_for(objective)),
        )

        intake = loop["intake_interpretation"]
        self.assertEqual(intake["reasoning_mode"], "validated_model_stub")
        self.assertEqual(intake["interpretation_source"], "validated_local_model_stub_response")
        self.assertEqual(intake["reasoning_validation_status"], "accepted")
        self.assertEqual(loop["capability_route"]["route_name"], "deterministic_code_only")
        self.assertFalse(loop["execution_posture"]["model_execution"])
        self.assertFalse(loop["execution_posture"]["provider_execution"])

    def test_embedded_raw_model_candidate_is_normalized_and_preserved_in_intake(self):
        import json

        objective = "Classify this fixed status list into three labels"
        raw = "<think></think>\n" + json.dumps(model_response_for(objective)) + "\n[end of text]"
        loop = run_dry_coordinator_loop(
            objective,
            reasoning_provider=StaticLocalModelProvider(raw),
        )

        intake = loop["intake_interpretation"]
        self.assertEqual(intake["reasoning_mode"], "validated_model_raw_output")
        self.assertEqual(intake["reasoning_output_classification"], "extracted_embedded_json")
        self.assertEqual(intake["reasoning_raw_output"], raw)
        self.assertTrue(loop["operator_review_packet"]["raw_output_preserved"])

    def test_injected_provider_evidence_is_advisory_and_route_remains_deterministic(self):
        objective = "Classify this fixed status list into three labels"
        raw = "<think>\n\n</think>\n" + json.dumps(model_response_for(objective)) + " [end of text]"
        loop = run_dry_coordinator_loop(objective, reasoning_provider=InjectedLocalModelProvider(lambda request: raw))
        review = loop["operator_review_packet"]
        self.assertTrue(review["provider_attempted"])
        self.assertTrue(review["model_candidate_admitted"])
        self.assertEqual(review["fallback_status"], "not_required")
        self.assertTrue(review["raw_output_reference"].startswith("sha256:"))
        self.assertEqual(loop["capability_route"]["route_name"], "deterministic_code_only")
        self.assertFalse(loop["coordinator_plan"]["execution_authorized"])
        self.assertFalse(loop["worker_handoff"]["dispatched"])
        self.assertFalse(loop["execution_posture"]["provider_execution"])

    def test_injected_transport_failure_preserves_deterministic_fallback(self):
        objective = "Classify this fixed status list into three labels"
        def failing(request):
            raise RuntimeError("down")
        loop = run_dry_coordinator_loop(objective, reasoning_provider=InjectedLocalModelProvider(failing))
        intake = loop["intake_interpretation"]
        self.assertEqual(intake["reasoning_provider_status"], "transport_exception")
        self.assertEqual(intake["reasoning_fallback_status"], "deterministic_fallback")
        self.assertEqual(loop["capability_route"]["route_name"], "deterministic_code_only")
        self.assertFalse(loop["worker_handoff"]["dispatched"])

    def test_ambiguous_raw_wrapper_falls_back_without_authority(self):
        import json

        objective = "Classify this fixed status list into three labels"
        raw = "Here is the answer:\n" + json.dumps(model_response_for(objective))
        loop = run_dry_coordinator_loop(
            objective,
            reasoning_provider=StaticLocalModelProvider(raw),
        )

        intake = loop["intake_interpretation"]
        self.assertEqual(intake["reasoning_mode"], "deterministic_fallback")
        self.assertEqual(intake["reasoning_output_classification"], "quarantined_ambiguous_output")
        self.assertEqual(loop["capability_route"]["route_name"], "deterministic_code_only")
        self.assertFalse(loop["execution_posture"]["worker_dispatch"])

    def test_disabled_or_malformed_model_reasoning_falls_back_deterministically(self):
        objective = "Classify this fixed status list into three labels"
        disabled = run_dry_coordinator_loop(objective, reasoning_provider=DisabledLocalModelProvider())
        malformed = run_dry_coordinator_loop(
            objective,
            reasoning_provider=StaticLocalModelProvider({"execution_authorized": True}),
        )

        self.assertEqual(disabled["intake_interpretation"]["reasoning_mode"], "deterministic_fallback")
        self.assertEqual(disabled["intake_interpretation"]["reasoning_validation_status"], "not_attempted")
        self.assertEqual(disabled["capability_route"]["route_name"], "deterministic_code_only")
        self.assertEqual(malformed["intake_interpretation"]["reasoning_validation_status"], "rejected")
        self.assertIn("unsupported_response_fields:execution_authorized", malformed["intake_interpretation"]["reasoning_validation_reasons"])

    def test_operator_review_packet_bridges_control_flow_to_neutral_case_surface(self):
        loop = run_dry_coordinator_loop("Classify this fixed status list into three labels")

        packet = loop["operator_review_packet"]
        self.assertEqual(packet["decision"], "accept")
        self.assertTrue(packet["neutral_dossier_case"]["bridge_present"])
        self.assertTrue(packet["neutral_dossier_case"]["structurally_ready_for_domain_specific_work"])
        self.assertFalse(packet["execution_authorized"])
        self.assertEqual(packet["handoff_status"], "prepared_not_dispatched")
        self.assertFalse(packet["dispatched"])
        self.assertIn("worker handoff must remain prepared_not_dispatched", packet["owner_approval_gates"])

    def test_unknown_objective_has_no_case_bridge_until_clarified(self):
        loop = run_dry_coordinator_loop("Please handle this thing")

        packet = loop["operator_review_packet"]
        self.assertEqual(packet["decision"], "blocked")
        self.assertFalse(packet["neutral_dossier_case"]["bridge_present"])
        self.assertIn("clarification_required_task_type", packet["blocked_or_deferred"])

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
