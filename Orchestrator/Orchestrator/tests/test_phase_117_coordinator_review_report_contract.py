import copy
import ast
import inspect
import unittest

from orchestrator import coordinator_review_report
from orchestrator.coordinator_review_report import (
    CoordinatorReviewReport,
    CoordinatorReviewReportResult,
    build_coordinator_review_report,
    render_coordinator_review_text,
)
from orchestrator.fixture_packet_pipeline import (
    run_fixture_to_boundary_packet_pipeline,
    run_structured_intake_to_boundary_packet_pipeline,
)
from orchestrator.prompt_to_envelope import PromptInferenceFixture
from orchestrator.route_proposal import RequestIntakeRecord


class Phase117CoordinatorReviewReportContractTests(unittest.TestCase):
    def fixture(self, fixture_id="phase117_fixture", request_type="general_answer", **overrides):
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

    def structured_intake(self, request_id="phase117_structured", request_type="coding_task", **overrides):
        base = {
            "request_id": request_id,
            "observed_request_summary": "Structured review report intake.",
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
            "reasoning_summary_for_operator": "Structured intake for report drafting only.",
            "caveats": (),
            "intake_source": "structured_operator_intake",
        }
        base.update(overrides)
        return RequestIntakeRecord(**base)

    def assert_no_activity(self, result):
        self.assertFalse(any(result.no_activity_flags.values()))
        self.assertIn("review_report_is_not_execution", result.non_proofs)
        self.assertIn("review_report_is_not_coordinator_ratification_by_itself", result.non_proofs)

    def test_module_exposes_required_contract(self):
        self.assertIs(coordinator_review_report.CoordinatorReviewReport, CoordinatorReviewReport)
        self.assertIs(coordinator_review_report.CoordinatorReviewReportResult, CoordinatorReviewReportResult)
        self.assertIs(coordinator_review_report.build_coordinator_review_report, build_coordinator_review_report)
        self.assertIs(coordinator_review_report.render_coordinator_review_text, render_coordinator_review_text)

    def test_accepted_safe_direct_answer_pipeline_produces_review_without_execution_authority(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase117_direct", expected_allowed_to_answer_directly=True)
        )
        result = build_coordinator_review_report(pipeline)

        self.assertTrue(result.accepted)
        self.assertEqual(result.report.packet_kind, "direct_answer_response")
        self.assertFalse(result.report.capability_assessment_summary["authorized_execution"])
        self.assert_no_activity(result)

    def test_accepted_coding_report_only_pipeline_preserves_packet_draft_posture(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture(
                "phase117_report",
                "planning_request",
                expected_required_capabilities=("planning_report",),
                expected_next_action="prepare_non_executing_coding_report",
            )
        )
        result = build_coordinator_review_report(pipeline)

        self.assertTrue(result.accepted)
        self.assertEqual(result.report.packet_kind, "coding_worker_report_only")
        self.assertIn("packet_kind=coding_worker_report_only", result.report.accepted_facts)
        self.assert_no_activity(result)

    def test_accepted_mutation_packet_pipeline_remains_draft_only_not_execution(self):
        pipeline = run_structured_intake_to_boundary_packet_pipeline(
            self.structured_intake(
                "phase117_mutation",
                caveats=("allowed_files: orchestrator/coordinator_review_report.py",),
            )
        )
        result = build_coordinator_review_report(pipeline)

        self.assertTrue(result.accepted)
        self.assertEqual(result.report.packet_kind, "coding_worker_source_test_mutation")
        self.assertIn("review_report_is_not_worker_execution", result.non_proofs)
        self.assert_no_activity(result)

    def test_blocked_pipeline_result_still_produces_conservative_review_report(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            PromptInferenceFixture(fixture_id="phase117_ambiguous", raw_prompt="Do it.")
        )
        result = build_coordinator_review_report(pipeline)

        self.assertFalse(result.accepted)
        self.assertIsInstance(result.report, CoordinatorReviewReport)
        self.assertEqual(result.report.packet_kind, "no_packet_draft")
        self.assertIn("declared_request_type_required", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_unknown_capability_pipeline_result_does_not_become_accepted(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase117_unknown", "planning_request", expected_required_capabilities=("future_unknown",))
        )
        result = build_coordinator_review_report(pipeline)

        self.assertFalse(result.accepted)
        self.assertFalse(result.report.accepted)
        self.assertIn("unknown_required_capabilities", result.blocked_conditions)
        self.assertIn("future_unknown", result.report.capability_assessment_summary["unknown_capabilities"])

    def test_platform_provider_model_runtime_posture_remains_external_or_blocked(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture(
                "phase117_platform",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("provider_model", "platform_runtime"),
            )
        )
        result = build_coordinator_review_report(pipeline)

        self.assertFalse(result.accepted)
        self.assertIn("provider_model_runtime_platform_requires_separate_boundary", result.blocked_conditions)
        self.assertEqual(result.report.packet_kind, "no_packet_draft")
        self.assert_no_activity(result)

    def test_production_execution_posture_remains_blocked(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture(
                "phase117_production",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("production_execution",),
                expected_explicit_production_boundary=True,
            )
        )
        result = build_coordinator_review_report(pipeline)

        self.assertFalse(result.accepted)
        self.assertIn("production_execution_blocked", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_review_report_preserves_capability_assessment_summary(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase117_capabilities", expected_allowed_to_answer_directly=True)
        )
        result = build_coordinator_review_report(pipeline)

        self.assertEqual(
            result.report.capability_assessment_summary["requested_capabilities"],
            pipeline.capability_assessment["requested_capabilities"],
        )
        self.assertFalse(result.report.capability_assessment_summary["authorized_execution"])

    def test_review_report_preserves_packet_text_when_present(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase117_packet_text", expected_allowed_to_answer_directly=True)
        )
        result = build_coordinator_review_report(pipeline)

        self.assertIn("BOUNDARY:", result.report.packet_text)
        self.assertEqual(result.report.packet_text, pipeline.packet_text)

    def test_rendered_review_text_includes_required_sections(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase117_render", expected_allowed_to_answer_directly=True)
        )
        text = render_coordinator_review_text(build_coordinator_review_report(pipeline).report)

        for expected in ("Assessment", "Accepted Facts", "Decision", "NBM", "Deliverable/Command", "RESPONSE_METADATA"):
            self.assertIn(expected, text)

    def test_rendered_review_text_states_not_coordinator_ratification(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase117_ratification", expected_allowed_to_answer_directly=True)
        )
        text = render_coordinator_review_text(build_coordinator_review_report(pipeline).report)

        self.assertIn("not coordinator ratification by itself", text)
        self.assertIn("coordinator_ratification=false", text)

    def test_review_report_preserves_non_proofs_and_no_activity_flags(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase117_nonproofs", expected_allowed_to_answer_directly=True)
        )
        result = build_coordinator_review_report(pipeline)

        self.assertIn("review_report_is_not_dispatch", result.non_proofs)
        self.assertIn("fixture_packet_pipeline_is_not_worker_execution", result.non_proofs)
        self.assertEqual(set(result.no_activity_flags.values()), {False})

    def test_review_report_does_not_select_concrete_substrate(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase117_substrate", expected_allowed_to_answer_directly=True)
        )
        text = render_coordinator_review_text(build_coordinator_review_report(pipeline).report).lower()

        for forbidden in (
            "selected_provider",
            "selected_model",
            "selected_runtime",
            "selected_platform",
            "selected_worker_substrate",
            "invoke codex",
            "invoke relay",
            "run ollama",
            "production executor",
        ):
            self.assertNotIn(forbidden, text)

    def test_review_report_does_not_mutate_input_pipeline_result(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture("phase117_immutable", expected_allowed_to_answer_directly=True)
        )
        before = copy.deepcopy(pipeline)

        build_coordinator_review_report(pipeline)

        self.assertEqual(pipeline, before)

    def test_module_does_not_import_forbidden_execution_provider_platform_runtime_service_libraries(self):
        source = inspect.getsource(coordinator_review_report)
        imported_modules = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)

        for forbidden in (
            "requests",
            "subprocess",
            "openai",
            "ollama",
            "discord",
            "orchestrator.provider",
            "orchestrator.platform",
            "orchestrator.connector",
            "orchestrator.scheduler",
            "orchestrator.service",
            "orchestrator.api",
            "orchestrator.ui",
            "orchestrator.openclaw",
            "orchestrator.hermes",
        ):
            self.assertFalse(
                any(name == forbidden or name.startswith(f"{forbidden}.") for name in imported_modules)
            )

    def test_regression_with_phase116_safe_fixture_to_packet_pipeline_output(self):
        pipeline = run_fixture_to_boundary_packet_pipeline(
            self.fixture(
                "phase117_regression",
                "planning_request",
                expected_required_capabilities=("planning_report",),
                expected_next_action="prepare_non_executing_coding_report",
            )
        )
        result = build_coordinator_review_report(pipeline)

        self.assertTrue(pipeline.accepted)
        self.assertTrue(result.accepted)
        self.assertEqual(result.report.packet_kind, "coding_worker_report_only")
        self.assertIn("coordinator_ratification=false", render_coordinator_review_text(result.report))


if __name__ == "__main__":
    unittest.main()
