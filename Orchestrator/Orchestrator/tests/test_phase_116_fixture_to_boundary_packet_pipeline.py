import copy
import inspect
import unittest

from orchestrator import fixture_packet_pipeline
from orchestrator.fixture_packet_pipeline import (
    FixtureBoundaryPacketPipelineResult,
    run_fixture_to_boundary_packet_pipeline,
    run_structured_intake_to_boundary_packet_pipeline,
)
from orchestrator.prompt_to_envelope import PromptInferenceFixture
from orchestrator.route_proposal import RequestIntakeRecord


class Phase116FixtureToBoundaryPacketPipelineTests(unittest.TestCase):
    def fixture(self, fixture_id="phase116_fixture", request_type="general_answer", **overrides):
        base = {
            "fixture_id": fixture_id,
            "raw_prompt": "Trace-only prompt text.",
            "declared_request_type": request_type,
            "expected_required_capabilities": ("direct_answer",),
            "expected_risk_level": "low",
            "expected_missing_inputs": (),
            "expected_next_action": "prepare_fixture_intake_for_admission_review",
        }
        base.update(overrides)
        return PromptInferenceFixture(**base)

    def structured_intake(self, request_id="phase116_structured", request_type="coding_task", **overrides):
        base = {
            "request_id": request_id,
            "observed_request_summary": "Structured fixture-to-packet intake.",
            "request_type": request_type,
            "confidence": 0.9,
            "required_capabilities": ("source_inspection", "patch_proposal", "filesystem_mutation_authority"),
            "missing_inputs": (),
            "risk_level": "low",
            "execution_policy": "structured_intake_pipeline_only",
            "recommended_next_action": "route_to_future_operator_confirmed_coding_boundary",
            "requires_operator_confirmation": True,
            "requires_external_connector": False,
            "allowed_to_answer_directly": False,
            "allowed_to_mutate_files": True,
            "allowed_to_schedule": False,
            "allowed_to_use_local_documents": False,
            "allowed_to_use_web": False,
            "reasoning_summary_for_operator": "Structured intake for packet drafting only.",
            "caveats": (),
            "intake_source": "structured_operator_intake",
        }
        base.update(overrides)
        return RequestIntakeRecord(**base)

    def assert_no_activity(self, result):
        self.assertFalse(any(result.no_activity_flags.values()))
        self.assertIn("fixture_packet_pipeline_is_not_worker_execution", result.non_proofs)
        self.assertIn("fixture_packet_pipeline_does_not_invoke_codex", result.non_proofs)
        self.assertIn("fixture_packet_pipeline_does_not_select_concrete_substrate", result.non_proofs)

    def test_module_exposes_required_contract(self):
        self.assertIs(fixture_packet_pipeline.FixtureBoundaryPacketPipelineResult, FixtureBoundaryPacketPipelineResult)
        self.assertIs(
            fixture_packet_pipeline.run_fixture_to_boundary_packet_pipeline,
            run_fixture_to_boundary_packet_pipeline,
        )
        self.assertIs(
            fixture_packet_pipeline.run_structured_intake_to_boundary_packet_pipeline,
            run_structured_intake_to_boundary_packet_pipeline,
        )

    def test_safe_direct_answer_fixture_reaches_direct_answer_packet_without_execution_authority(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase116_direct", expected_allowed_to_answer_directly=True)
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.packet_draft.packet_kind, "direct_answer_response")
        self.assertIn("BOUNDARY:", result.packet_text)
        self.assertFalse(result.intake_admission_result.execution_authority)
        self.assert_no_activity(result)

    def test_safe_coding_report_only_fixture_reaches_bounded_report_packet(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture(
                "phase116_report",
                "planning_request",
                expected_required_capabilities=("planning_report",),
                expected_next_action="prepare_non_executing_coding_report",
            )
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.packet_draft.packet_kind, "coding_worker_report_only")
        self.assertIn("read-only repository scope declared by coordinator", result.packet_draft.allowed_files)
        self.assert_no_activity(result)

    def test_coding_mutation_fixture_reaches_bounded_mutation_packet_draft_only(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture(
                "phase116_mutation",
                "coding_task",
                expected_required_capabilities=("source_inspection", "patch_proposal", "filesystem_mutation_authority"),
                expected_requires_confirmation=True,
                expected_allowed_to_mutate_files=True,
                expected_explicit_mutation_permission=True,
                expected_next_action="route_to_future_operator_confirmed_coding_boundary",
            )
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.packet_draft.packet_kind, "coding_worker_source_test_mutation")
        self.assertIn("coordinator_must_finalize_allowed_files_before_dispatch", result.caveats)
        self.assert_no_activity(result)

    def test_unknown_capabilities_reject_through_full_pipeline_without_packet_draft(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase116_unknown", "planning_request", expected_required_capabilities=("future_unknown",))
        )

        self.assertFalse(result.accepted)
        self.assertIsNone(result.packet_draft)
        self.assertEqual(result.packet_text, "")
        self.assertIn("unknown_required_capabilities", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_blocked_external_capabilities_do_not_produce_product_execution_packet(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture(
                "phase116_web",
                "research_request",
                expected_required_capabilities=("web_research",),
                expected_allowed_to_use_web=True,
                expected_explicit_web_boundary=True,
            )
        )

        self.assertFalse(result.accepted)
        self.assertIsNone(result.packet_draft)
        self.assertIn("blocked_or_external_required_capabilities", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_ambiguous_fixture_stops_conservatively_before_packet_drafting(self):
        result = run_fixture_to_boundary_packet_pipeline(
            PromptInferenceFixture(fixture_id="phase116_ambiguous", raw_prompt="Please do the thing.")
        )

        self.assertFalse(result.accepted)
        self.assertIsNone(result.packet_draft)
        self.assertEqual(result.intake_admission_result.pipeline_stage, "fixture_needs_clarification")
        self.assertIn("declared_request_type_required", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_raw_prompt_text_alone_is_not_inferred_into_route_or_packet(self):
        result = run_fixture_to_boundary_packet_pipeline(
            {"fixture_id": "phase116_raw_only", "raw_prompt": "Browse, schedule, and execute this."}
        )

        self.assertFalse(result.accepted)
        self.assertIsNone(result.intake_admission_result.candidate_route)
        self.assertIsNone(result.packet_draft)
        self.assertIn("fixture_packet_pipeline_is_not_live_prompt_inference", result.non_proofs)
        self.assert_no_activity(result)

    def test_substrate_smuggling_fixture_is_blocked_without_dispatch_packet(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture(
                "phase116_smuggling",
                "coding_task",
                expected_required_capabilities=("source_inspection",),
                expected_next_action="run with Codex provider",
            )
        )

        self.assertFalse(result.accepted)
        self.assertIsNone(result.packet_draft)
        self.assertIn("substrate_smuggling_blocked", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_platform_provider_model_runtime_fixture_is_external_or_blocked_only(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture(
                "phase116_platform",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("provider_model", "platform_runtime"),
            )
        )

        self.assertFalse(result.accepted)
        self.assertIsNone(result.packet_draft)
        self.assertIn("provider_model_runtime_platform_requires_separate_boundary", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_production_execution_fixture_is_blocked(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture(
                "phase116_production",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("production_execution",),
                expected_explicit_production_boundary=True,
            )
        )

        self.assertFalse(result.accepted)
        self.assertIn("production_execution_blocked", result.blocked_conditions)
        self.assertIsNone(result.packet_draft)
        self.assert_no_activity(result)

    def test_pipeline_preserves_capability_assessment_from_layers(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase116_assessment", expected_allowed_to_answer_directly=True)
        )

        self.assertEqual(result.capability_assessment, result.boundary_packet_result.capability_assessment)
        self.assertEqual(result.capability_assessment, result.intake_admission_result.capability_assessment)
        self.assertFalse(result.capability_assessment["authorized_execution"])
        self.assert_no_activity(result)

    def test_pipeline_preserves_non_proofs_and_no_activity_flags(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase116_nonproofs", expected_allowed_to_answer_directly=True)
        )

        self.assertIn("packet_drafting_is_not_worker_execution", result.non_proofs)
        self.assertIn("pipeline_is_not_route_execution", result.non_proofs)
        self.assertEqual(set(result.no_activity_flags.values()), {False})

    def test_pipeline_distinguishes_fixture_intake_admission_packet_and_execution_authority(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase116_stages", expected_allowed_to_answer_directly=True)
        )

        self.assertEqual(result.fixture_or_intake_source, "prompt_fixture")
        self.assertIsNotNone(result.intake_admission_result.fixture_decision)
        self.assertIsNotNone(result.intake_admission_result.intake_record)
        self.assertIsNotNone(result.intake_admission_result.admission_decision)
        self.assertIsNotNone(result.boundary_packet_result.packet_draft)
        self.assertFalse(result.intake_admission_result.execution_authority)

    def test_structured_intake_can_run_through_to_packet_posture_without_fixture(self):
        result = run_structured_intake_to_boundary_packet_pipeline(
            self.structured_intake(
                "phase116_structured",
                caveats=("allowed_files: orchestrator/fixture_packet_pipeline.py",),
            )
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.fixture_or_intake_source, "structured_intake")
        self.assertIsNone(result.intake_admission_result.fixture_decision)
        self.assertEqual(result.packet_draft.packet_kind, "coding_worker_source_test_mutation")
        self.assert_no_activity(result)

    def test_packet_text_includes_required_sections_for_packet_bearing_outcomes(self):
        result = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase116_text", expected_allowed_to_answer_directly=True)
        )

        for expected in (
            "BOUNDARY:",
            "ROLE:",
            "PURPOSE:",
            "EXCLUSIONS:",
            "VALIDATION:",
            "REPORT FORMAT:",
            "NON-PROOFS:",
            "STOP CONDITIONS:",
        ):
            self.assertIn(expected, result.packet_text)

    def test_module_does_not_import_forbidden_execution_provider_platform_runtime_libraries(self):
        source = inspect.getsource(fixture_packet_pipeline)

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

    def test_regression_with_phase115_packet_and_phase114_admission_behavior(self):
        fixture = self.fixture(
            "phase116_regression",
            "planning_request",
            expected_required_capabilities=("planning_report",),
            expected_next_action="prepare_non_executing_coding_report",
        )
        before = copy.deepcopy(fixture)
        result = run_fixture_to_boundary_packet_pipeline(fixture)

        self.assertEqual(fixture, before)
        self.assertTrue(result.intake_admission_result.accepted)
        self.assertTrue(result.boundary_packet_result.accepted)
        self.assertEqual(result.packet_draft.packet_kind, "coding_worker_report_only")


if __name__ == "__main__":
    unittest.main()
