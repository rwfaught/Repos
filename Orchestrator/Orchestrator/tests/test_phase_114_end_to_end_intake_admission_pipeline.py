import inspect
import unittest

from orchestrator import intake_admission_pipeline
from orchestrator.intake_admission_pipeline import (
    IntakeAdmissionPipelineResult,
    run_fixture_admission_pipeline,
    run_structured_intake_admission_pipeline,
)
from orchestrator.prompt_to_envelope import PromptInferenceFixture
from orchestrator.route_proposal import RequestIntakeRecord


class Phase114EndToEndIntakeAdmissionPipelineTests(unittest.TestCase):
    def fixture(self, fixture_id="phase114_fixture", request_type="general_answer", **overrides):
        base = {
            "fixture_id": fixture_id,
            "raw_prompt": "Trace-only prompt text.",
            "declared_request_type": request_type,
            "expected_required_capabilities": ("direct_answer",),
            "expected_risk_level": "low",
            "expected_missing_inputs": (),
            "expected_requires_confirmation": False,
            "expected_requires_external_connector": False,
            "expected_allowed_to_answer_directly": False,
            "expected_allowed_to_mutate_files": False,
            "expected_allowed_to_schedule": False,
            "expected_allowed_to_use_local_documents": False,
            "expected_allowed_to_use_web": False,
            "expected_next_action": "prepare_fixture_intake_for_admission_review",
        }
        base.update(overrides)
        return PromptInferenceFixture(**base)

    def assert_no_activity(self, result):
        self.assertFalse(result.execution_authority)
        self.assertFalse(any(result.no_activity_flags.values()))
        self.assertIn("pipeline_is_not_route_execution", result.non_proofs)
        self.assertIn("pipeline_does_not_mutate_files", result.non_proofs)

    def test_module_exposes_required_contract(self):
        self.assertIs(intake_admission_pipeline.IntakeAdmissionPipelineResult, IntakeAdmissionPipelineResult)
        self.assertIs(intake_admission_pipeline.run_fixture_admission_pipeline, run_fixture_admission_pipeline)
        self.assertIs(
            intake_admission_pipeline.run_structured_intake_admission_pipeline,
            run_structured_intake_admission_pipeline,
        )

    def test_safe_direct_answer_fixture_completes_full_pipeline_without_execution_authority(self):
        result = run_fixture_admission_pipeline(
            self.fixture(expected_allowed_to_answer_directly=True)
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.pipeline_stage, "route_admission_decided")
        self.assertEqual(result.request_type, "general_answer")
        self.assertIsNotNone(result.fixture_decision)
        self.assertIsNotNone(result.intake_record)
        self.assertIsNotNone(result.candidate_route)
        self.assertIsNotNone(result.admission_decision)
        self.assertFalse(result.admission_decision.execution_authority)
        self.assert_no_activity(result)

    def test_safe_coding_report_only_fixture_completes_as_non_mutating_and_non_executing(self):
        result = run_fixture_admission_pipeline(
            self.fixture(
                "phase114_report",
                "planning_request",
                expected_required_capabilities=("planning_report",),
                expected_next_action="prepare_non_executing_coding_report",
            )
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.request_type, "planning_request")
        self.assertFalse(result.intake_record.allowed_to_mutate_files)
        self.assert_no_activity(result)

    def test_coding_mutation_fixture_produces_admission_posture_not_file_mutation(self):
        result = run_fixture_admission_pipeline(
            self.fixture(
                "phase114_mutation",
                "coding_task",
                expected_required_capabilities=(
                    "source_inspection",
                    "patch_proposal",
                    "filesystem_mutation_authority",
                ),
                expected_requires_confirmation=True,
                expected_allowed_to_mutate_files=True,
                expected_explicit_mutation_permission=True,
                expected_next_action="route_to_future_operator_confirmed_coding_boundary",
            )
        )

        self.assertTrue(result.accepted)
        self.assertTrue(result.intake_record.allowed_to_mutate_files)
        self.assertEqual(result.admission_decision.accepted_route_state, "accepted_route_without_execution_authority")
        self.assert_no_activity(result)

    def test_unknown_capabilities_are_rejected_through_end_to_end_pipeline(self):
        result = run_fixture_admission_pipeline(
            self.fixture(
                "phase114_unknown",
                "planning_request",
                expected_required_capabilities=("planning_report", "future_unknown_capability"),
            )
        )

        self.assertFalse(result.accepted)
        self.assertIn("unknown_required_capabilities", result.blocked_conditions)
        self.assertEqual(result.capability_assessment["unknown_capabilities"], ["future_unknown_capability"])
        self.assert_no_activity(result)

    def test_blocked_external_capabilities_produce_separate_boundary_or_rejection(self):
        result = run_fixture_admission_pipeline(
            self.fixture(
                "phase114_local_docs",
                "local_document_lookup",
                expected_required_capabilities=("local_document_lookup",),
                expected_allowed_to_use_local_documents=True,
                expected_explicit_local_document_authority=True,
                expected_next_action="request_document_lookup_boundary",
            )
        )

        self.assertFalse(result.accepted)
        self.assertIn("blocked_or_external_required_capabilities", result.blocked_conditions)
        self.assertEqual(result.admission_decision.next_boundary_kind, "separate_boundary_required")
        self.assertEqual(result.capability_assessment["blocked_or_external_capabilities"], ["local_document_lookup"])
        self.assert_no_activity(result)

    def test_ambiguous_fixture_stops_before_route_execution(self):
        result = run_fixture_admission_pipeline(
            PromptInferenceFixture(
                fixture_id="phase114_ambiguous",
                raw_prompt="Please do the thing.",
            )
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.pipeline_stage, "fixture_needs_clarification")
        self.assertIsNone(result.intake_record)
        self.assertIsNone(result.candidate_route)
        self.assertIsNone(result.admission_decision)
        self.assertIn("declared_request_type_required", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_raw_prompt_text_alone_is_not_inferred_into_route(self):
        result = run_fixture_admission_pipeline(
            {"fixture_id": "phase114_raw_only", "raw_prompt": "Schedule this and browse the web."}
        )

        self.assertFalse(result.accepted)
        self.assertIsNone(result.candidate_route)
        self.assertIn("declared_request_type_required", result.blocked_conditions)
        self.assertIn("pipeline_is_not_live_prompt_inference", result.non_proofs)
        self.assert_no_activity(result)

    def test_substrate_smuggling_fixture_is_blocked(self):
        result = run_fixture_admission_pipeline(
            self.fixture(
                "phase114_smuggling",
                "coding_task",
                expected_required_capabilities=("source_inspection",),
                expected_next_action="run with Codex provider",
            )
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.pipeline_stage, "fixture_classification_blocked")
        self.assertIn("substrate_smuggling_blocked", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_platform_provider_model_runtime_fixture_is_blocked_without_execution(self):
        result = run_fixture_admission_pipeline(
            self.fixture(
                "phase114_platform",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("provider_model", "platform_runtime"),
            )
        )

        self.assertFalse(result.accepted)
        self.assertIn("provider_model_runtime_platform_requires_separate_boundary", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_production_execution_fixture_is_blocked(self):
        result = run_fixture_admission_pipeline(
            self.fixture(
                "phase114_production",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("production_execution",),
                expected_explicit_production_boundary=True,
            )
        )

        self.assertFalse(result.accepted)
        self.assertIn("production_execution_blocked", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_pipeline_preserves_capability_assessment_from_admission_decision(self):
        result = run_fixture_admission_pipeline(
            self.fixture(
                "phase114_assessment",
                "research_request",
                expected_required_capabilities=("web_research",),
                expected_allowed_to_use_web=True,
                expected_explicit_web_boundary=True,
            )
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.capability_assessment, result.admission_decision.capability_assessment)
        self.assertIn("web_research", result.capability_assessment["blocked_or_external_capabilities"])
        self.assert_no_activity(result)

    def test_pipeline_preserves_non_proofs_and_no_activity_flags(self):
        result = run_fixture_admission_pipeline(
            self.fixture("phase114_nonproofs", expected_allowed_to_answer_directly=True)
        )

        self.assertIn("pipeline_is_not_live_router", result.non_proofs)
        self.assertIn("fixture_classification_is_not_live_prompt_inference", result.non_proofs)
        self.assertIn("accepted_route_is_not_execution_authority", result.non_proofs)
        self.assertEqual(set(result.no_activity_flags.values()), {False})

    def test_pipeline_distinguishes_stages_and_execution_authority(self):
        result = run_fixture_admission_pipeline(
            self.fixture("phase114_stages", expected_allowed_to_answer_directly=True)
        )

        self.assertEqual(result.fixture_decision.route_admission, "fixture_intake_ready")
        self.assertEqual(result.intake_record.request_id, "phase114_stages")
        self.assertEqual(result.candidate_route.proposal_state, "candidate_route_proposed")
        self.assertEqual(result.admission_decision.validated_envelope_state, "validated_envelope_metadata_only")
        self.assertFalse(result.execution_authority)

    def test_structured_intake_can_run_without_fixture_input(self):
        intake = RequestIntakeRecord(
            request_id="phase114_structured",
            observed_request_summary="Already structured direct-answer intake.",
            request_type="general_answer",
            confidence=0.9,
            required_capabilities=("direct_answer",),
            missing_inputs=(),
            risk_level="low",
            execution_policy="structured_intake_pipeline_only",
            recommended_next_action="answer_directly_without_execution",
            requires_operator_confirmation=False,
            requires_external_connector=False,
            allowed_to_answer_directly=True,
            allowed_to_mutate_files=False,
            allowed_to_schedule=False,
            allowed_to_use_local_documents=False,
            allowed_to_use_web=False,
            reasoning_summary_for_operator="Structured intake supplied without fixture classification.",
            caveats=("structured_intake_only",),
            intake_source="structured_operator_intake",
        )
        result = run_structured_intake_admission_pipeline(intake)

        self.assertTrue(result.accepted)
        self.assertIsNone(result.fixture_decision)
        self.assertEqual(result.intake_record, intake)
        self.assertEqual(result.request_type, "general_answer")
        self.assert_no_activity(result)

    def test_module_does_not_import_forbidden_execution_provider_platform_runtime_libraries(self):
        source = inspect.getsource(intake_admission_pipeline)

        for forbidden in (
            "import requests",
            "import subprocess",
            "import openai",
            "import ollama",
            "import discord",
            "from orchestrator.provider",
            "from orchestrator.platform",
            "from orchestrator.connector",
            "from orchestrator.scheduler",
            "from orchestrator.openclaw",
            "from orchestrator.hermes",
        ):
            self.assertNotIn(forbidden, source)

    def test_regression_compatibility_with_phase113_fixture_and_phase111_admission(self):
        result = run_fixture_admission_pipeline(
            self.fixture(
                "phase114_regression",
                "general_answer",
                expected_required_capabilities=("direct_answer",),
                expected_allowed_to_answer_directly=True,
            )
        )

        self.assertTrue(result.fixture_decision.accepted)
        self.assertTrue(result.admission_decision.accepted)
        self.assertEqual(result.admission_decision.route_admission, "accepted")
        self.assertFalse(result.admission_decision.execution_authority)


if __name__ == "__main__":
    unittest.main()
