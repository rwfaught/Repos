import copy
import inspect
import unittest

from orchestrator import manual_review_runner
from orchestrator.manual_review_runner import (
    ManualReviewRunResult,
    get_builtin_review_fixture,
    list_builtin_review_fixtures,
    run_fixture_review,
    run_named_fixture_review,
    run_structured_intake_review,
)
from orchestrator.prompt_to_envelope import PromptInferenceFixture
from orchestrator.route_proposal import RequestIntakeRecord


REQUIRED_FIXTURE_IDS = (
    "safe_direct_answer",
    "safe_coding_report_only",
    "safe_coding_docs_only_mutation",
    "safe_coding_source_test_mutation",
    "unknown_capability_blocked",
    "substrate_smuggling_blocked",
    "platform_provider_external_boundary",
    "production_execution_blocked",
    "ambiguous_needs_clarification",
)


class Phase118ManualReviewRunnerContractTests(unittest.TestCase):
    def assert_no_activity(self, result):
        self.assertFalse(any(result.no_activity_flags.values()))
        self.assertIn("runner_is_not_service_api_ui", result.non_proofs)
        self.assertIn("runner_is_not_worker_execution", result.non_proofs)
        self.assertIn("runner_does_not_invoke_codex_or_relay", result.non_proofs)

    def test_module_exposes_required_contract(self):
        self.assertIs(manual_review_runner.ManualReviewRunResult, ManualReviewRunResult)
        self.assertIs(manual_review_runner.list_builtin_review_fixtures, list_builtin_review_fixtures)
        self.assertIs(manual_review_runner.get_builtin_review_fixture, get_builtin_review_fixture)
        self.assertIs(manual_review_runner.run_named_fixture_review, run_named_fixture_review)
        self.assertIs(manual_review_runner.run_fixture_review, run_fixture_review)
        self.assertIs(manual_review_runner.run_structured_intake_review, run_structured_intake_review)

    def test_builtin_fixture_ids_are_deterministic_and_complete(self):
        first = list_builtin_review_fixtures()
        second = list_builtin_review_fixtures()

        self.assertEqual(first, second)
        self.assertEqual(first, tuple(sorted(first)))
        for fixture_id in REQUIRED_FIXTURE_IDS:
            self.assertIn(fixture_id, first)

    def test_get_builtin_review_fixture_returns_defensive_copy(self):
        first = get_builtin_review_fixture("safe_direct_answer")
        second = get_builtin_review_fixture("safe_direct_answer")

        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        first["kind"] = "mutated"
        self.assertEqual(get_builtin_review_fixture("safe_direct_answer")["kind"], "fixture")

    def test_unknown_fixture_id_fails_conservatively_without_execution(self):
        result = run_named_fixture_review("not_a_fixture")

        self.assertFalse(result.accepted)
        self.assertIsNone(result.pipeline_result)
        self.assertIn("unknown_builtin_review_fixture", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_safe_direct_answer_produces_review_text_without_execution_authority(self):
        result = run_named_fixture_review("safe_direct_answer")

        self.assertTrue(result.accepted)
        self.assertEqual(result.request_type, "general_answer")
        self.assertIn("direct_answer_response", result.review_text)
        self.assertIn("worker_execution=false", result.review_text)
        self.assert_no_activity(result)

    def test_safe_coding_report_only_produces_report_only_posture(self):
        result = run_named_fixture_review("safe_coding_report_only")

        self.assertTrue(result.accepted)
        self.assertEqual(result.pipeline_result.packet_draft.packet_kind, "coding_worker_report_only")
        self.assertIn("coding_worker_report_only", result.review_text)
        self.assert_no_activity(result)

    def test_safe_coding_docs_only_mutation_produces_draft_only_docs_packet_without_mutation(self):
        result = run_named_fixture_review("safe_coding_docs_only_mutation")

        self.assertTrue(result.accepted)
        self.assertEqual(result.pipeline_result.packet_draft.packet_kind, "coding_worker_docs_only_mutation")
        self.assertIn("docs/PHASE_118.md", result.review_text)
        self.assert_no_activity(result)

    def test_safe_coding_source_test_mutation_produces_draft_only_source_test_packet(self):
        result = run_named_fixture_review("safe_coding_source_test_mutation")

        self.assertTrue(result.accepted)
        self.assertEqual(result.pipeline_result.packet_draft.packet_kind, "coding_worker_source_test_mutation")
        self.assertIn("orchestrator/manual_review_runner.py", result.review_text)
        self.assert_no_activity(result)

    def test_unknown_capability_blocked_remains_blocked(self):
        result = run_named_fixture_review("unknown_capability_blocked")

        self.assertFalse(result.accepted)
        self.assertIn("unknown_required_capabilities", result.blocked_conditions)
        self.assertIsNone(result.pipeline_result.packet_draft)
        self.assert_no_activity(result)

    def test_substrate_smuggling_blocked_remains_blocked(self):
        result = run_named_fixture_review("substrate_smuggling_blocked")

        self.assertFalse(result.accepted)
        self.assertIn("substrate_smuggling_blocked", result.blocked_conditions)
        self.assertIsNone(result.pipeline_result.packet_draft)
        self.assert_no_activity(result)

    def test_platform_provider_external_boundary_is_not_product_execution(self):
        result = run_named_fixture_review("platform_provider_external_boundary")

        self.assertFalse(result.accepted)
        self.assertIn("provider_model_runtime_platform_requires_separate_boundary", result.blocked_conditions)
        self.assertIsNone(result.pipeline_result.packet_draft)
        self.assert_no_activity(result)

    def test_production_execution_blocked_remains_blocked(self):
        result = run_named_fixture_review("production_execution_blocked")

        self.assertFalse(result.accepted)
        self.assertIn("production_execution_blocked", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_ambiguous_needs_clarification_remains_clarification_posture(self):
        result = run_named_fixture_review("ambiguous_needs_clarification")

        self.assertFalse(result.accepted)
        self.assertIn("declared_request_type_required", result.blocked_conditions)
        self.assertIn("not_admitted", result.review_text)
        self.assert_no_activity(result)

    def test_run_fixture_review_accepts_explicit_fixture_dictionary(self):
        fixture_dict = {
            "fixture_id": "explicit_fixture_dict",
            "raw_prompt": "Trace-only prompt.",
            "declared_request_type": "general_answer",
            "expected_required_capabilities": ("direct_answer",),
            "expected_risk_level": "low",
            "expected_allowed_to_answer_directly": True,
        }
        before = copy.deepcopy(fixture_dict)
        result = run_fixture_review(fixture_dict)

        self.assertTrue(result.accepted)
        self.assertEqual(fixture_dict, before)
        self.assertIn("Assessment", result.review_text)
        self.assert_no_activity(result)

    def test_run_structured_intake_review_accepts_structured_intake_record(self):
        intake = RequestIntakeRecord(
            request_id="explicit_structured_intake",
            observed_request_summary="Manual review structured intake.",
            request_type="general_answer",
            confidence=0.9,
            required_capabilities=("direct_answer",),
            missing_inputs=(),
            risk_level="low",
            execution_policy="manual_review_only",
            recommended_next_action="answer_directly_without_execution",
            requires_operator_confirmation=False,
            requires_external_connector=False,
            allowed_to_answer_directly=True,
            allowed_to_mutate_files=False,
            allowed_to_schedule=False,
            allowed_to_use_local_documents=False,
            allowed_to_use_web=False,
            reasoning_summary_for_operator="Manual review only.",
            caveats=("manual_review_only",),
            intake_source="manual_review_test",
        )
        result = run_structured_intake_review(intake)

        self.assertTrue(result.accepted)
        self.assertEqual(result.request_id, "explicit_structured_intake")
        self.assertIn("RESPONSE_METADATA", result.review_text)
        self.assert_no_activity(result)

    def test_review_text_includes_required_sections(self):
        result = run_named_fixture_review("safe_direct_answer")

        for expected in ("Assessment", "Accepted Facts", "Decision", "NBM", "Deliverable/Command", "RESPONSE_METADATA"):
            self.assertIn(expected, result.review_text)

    def test_runner_preserves_non_proofs_and_no_activity_flags(self):
        result = run_named_fixture_review("safe_direct_answer")

        self.assertIn("review_report_is_not_execution", result.non_proofs)
        self.assertIn("fixture_packet_pipeline_is_not_route_execution", result.non_proofs)
        self.assertEqual(set(result.no_activity_flags.values()), {False})

    def test_runner_does_not_select_concrete_substrate(self):
        result = run_named_fixture_review("safe_direct_answer")
        text = result.review_text.lower()

        for forbidden in (
            "selected_provider",
            "selected_model",
            "selected_runtime",
            "selected_platform",
            "selected_worker_substrate",
            "invoke codex",
            "invoke relay",
            "run ollama",
            "filesystem executor",
            "production executor",
        ):
            self.assertNotIn(forbidden, text)

    def test_runner_does_not_mutate_input_fixture_or_intake_objects(self):
        fixture = PromptInferenceFixture(
            fixture_id="immutable_fixture",
            raw_prompt="Trace-only prompt.",
            declared_request_type="general_answer",
            expected_required_capabilities=("direct_answer",),
            expected_risk_level="low",
            expected_allowed_to_answer_directly=True,
        )
        before = copy.deepcopy(fixture)

        run_fixture_review(fixture)

        self.assertEqual(fixture, before)

    def test_module_does_not_import_forbidden_execution_provider_platform_runtime_service_cli_libraries(self):
        source = inspect.getsource(manual_review_runner)

        for forbidden in (
            "import requests",
            "import subprocess",
            "import openai",
            "import ollama",
            "import discord",
            "import argparse",
            "import click",
            "from orchestrator.provider",
            "from orchestrator.platform",
            "from orchestrator.connector",
            "from orchestrator.scheduler",
            "from orchestrator.service",
            "from orchestrator.api",
            "from orchestrator.ui",
            "from orchestrator.openclaw",
            "from orchestrator.hermes",
        ):
            self.assertNotIn(forbidden, source)

    def test_regression_with_phase117_report_and_phase116_pipeline(self):
        result = run_named_fixture_review("safe_coding_report_only")

        self.assertTrue(result.pipeline_result.accepted)
        self.assertTrue(result.review_report_result.accepted)
        self.assertEqual(result.review_report_result.report.packet_kind, "coding_worker_report_only")
        self.assertIn("coordinator_ratification=false", result.review_text)


if __name__ == "__main__":
    unittest.main()
