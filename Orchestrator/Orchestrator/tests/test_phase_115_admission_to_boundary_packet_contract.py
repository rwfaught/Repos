import copy
import inspect
import unittest

from orchestrator import boundary_packet
from orchestrator.boundary_packet import (
    BoundaryPacketDraft,
    BoundaryPacketDraftResult,
    build_boundary_packet_draft,
    render_boundary_packet_text,
)
from orchestrator.intake_admission_pipeline import run_fixture_admission_pipeline, run_structured_intake_admission_pipeline
from orchestrator.prompt_to_envelope import PromptInferenceFixture
from orchestrator.route_proposal import RequestIntakeRecord


class Phase115AdmissionToBoundaryPacketContractTests(unittest.TestCase):
    def fixture(self, fixture_id="phase115_fixture", request_type="general_answer", **overrides):
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

    def structured_intake(self, request_id="phase115_structured", request_type="coding_task", **overrides):
        base = {
            "request_id": request_id,
            "observed_request_summary": "Structured packet draft intake.",
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
        self.assertIn("packet_drafting_is_not_execution", result.non_proofs)
        self.assertIn("packet_drafting_is_not_substrate_selection", result.non_proofs)

    def test_module_exposes_required_contract(self):
        self.assertIs(boundary_packet.BoundaryPacketDraft, BoundaryPacketDraft)
        self.assertIs(boundary_packet.BoundaryPacketDraftResult, BoundaryPacketDraftResult)
        self.assertIs(boundary_packet.build_boundary_packet_draft, build_boundary_packet_draft)
        self.assertIs(boundary_packet.render_boundary_packet_text, render_boundary_packet_text)

    def test_non_accepted_admission_result_does_not_produce_worker_packet(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture("phase115_unknown", "planning_request", expected_required_capabilities=("unknown_capability",))
        )
        result = build_boundary_packet_draft(pipeline)

        self.assertFalse(result.accepted)
        self.assertIsNone(result.packet_draft)
        self.assertIn("unknown_required_capabilities", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_accepted_direct_answer_admission_produces_response_posture_without_execution_authority(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture("phase115_direct", expected_allowed_to_answer_directly=True)
        )
        result = build_boundary_packet_draft(pipeline)

        self.assertTrue(result.accepted)
        self.assertEqual(result.packet_draft.packet_kind, "direct_answer_response")
        self.assertEqual(result.packet_draft.allowed_files, ("no file mutation",))
        self.assert_no_activity(result)

    def test_accepted_coding_report_only_admission_produces_bounded_report_only_packet(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture(
                "phase115_report",
                "planning_request",
                expected_required_capabilities=("planning_report",),
                expected_next_action="prepare_non_executing_coding_report",
            )
        )
        result = build_boundary_packet_draft(pipeline)

        self.assertTrue(result.accepted)
        self.assertEqual(result.packet_draft.packet_kind, "coding_worker_report_only")
        self.assertIn("read-only repository scope declared by coordinator", result.packet_draft.allowed_files)
        self.assert_no_activity(result)

    def test_accepted_docs_only_mutation_posture_produces_docs_only_packet(self):
        pipeline = run_structured_intake_admission_pipeline(
            self.structured_intake(
                "phase115_docs",
                caveats=("docs_only_mutation", "allowed_files: docs/PHASE_115.md"),
            )
        )
        result = build_boundary_packet_draft(pipeline)

        self.assertTrue(result.accepted)
        self.assertEqual(result.packet_draft.packet_kind, "coding_worker_docs_only_mutation")
        self.assertEqual(result.packet_draft.allowed_files, ("docs/PHASE_115.md",))
        self.assertIn("No worker execution.", result.packet_draft.explicit_exclusions)
        self.assertIn("Boundary", result.packet_draft.report_format)
        self.assert_no_activity(result)

    def test_accepted_source_test_mutation_posture_produces_source_test_packet(self):
        pipeline = run_structured_intake_admission_pipeline(
            self.structured_intake(
                "phase115_source",
                caveats=(
                    "allowed_files: orchestrator/boundary_packet.py",
                    "allowed_files: tests/test_phase_115_admission_to_boundary_packet_contract.py",
                ),
            )
        )
        result = build_boundary_packet_draft(pipeline)

        self.assertTrue(result.accepted)
        self.assertEqual(result.packet_draft.packet_kind, "coding_worker_source_test_mutation")
        self.assertIn("orchestrator/boundary_packet.py", result.packet_draft.allowed_files)
        self.assertIn("targeted py_compile/unittest commands declared by coordinator", result.packet_draft.validation_commands)
        self.assert_no_activity(result)

    def test_external_platform_provider_model_runtime_posture_does_not_create_product_worker_packet(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture(
                "phase115_platform",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("provider_model", "platform_runtime"),
            )
        )
        result = build_boundary_packet_draft(pipeline)

        self.assertFalse(result.accepted)
        self.assertIsNone(result.packet_draft)
        self.assertIn("provider_model_runtime_platform_requires_separate_boundary", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_blocked_external_capabilities_do_not_produce_product_execution_packet(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture(
                "phase115_web",
                "research_request",
                expected_required_capabilities=("web_research",),
                expected_allowed_to_use_web=True,
                expected_explicit_web_boundary=True,
            )
        )
        result = build_boundary_packet_draft(pipeline)

        self.assertFalse(result.accepted)
        self.assertIsNone(result.packet_draft)
        self.assertIn("blocked_or_external_required_capabilities", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_unknown_capabilities_do_not_produce_packet(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture("phase115_unknown2", "planning_request", expected_required_capabilities=("future_unknown",))
        )
        result = build_boundary_packet_draft(pipeline)

        self.assertFalse(result.accepted)
        self.assertIsNone(result.packet_draft)
        self.assertIn("unknown_required_capabilities", result.blocked_conditions)
        self.assert_no_activity(result)

    def test_packet_text_includes_required_sections(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture("phase115_text", expected_allowed_to_answer_directly=True)
        )
        result = build_boundary_packet_draft(pipeline)
        text = render_boundary_packet_text(result.packet_draft)

        for expected in (
            "ROLE:",
            "REPO:",
            "BOUNDARY:",
            "PURPOSE:",
            "ALLOWED FILES OR FILE CLASSES:",
            "EXCLUSIONS:",
            "VALIDATION:",
            "REPORT FORMAT:",
            "NON-PROOFS:",
            "STOP CONDITIONS:",
        ):
            self.assertIn(expected, text)

    def test_packet_draft_preserves_capability_assessment_and_non_proofs(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture("phase115_preserve", expected_allowed_to_answer_directly=True)
        )
        result = build_boundary_packet_draft(pipeline)

        self.assertEqual(result.capability_assessment, pipeline.capability_assessment)
        self.assertIn("packet_drafting_is_not_coordinator_acceptance", result.packet_draft.non_proofs)
        self.assertIn("accepted_route_is_not_execution_authority", result.packet_draft.non_proofs)

    def test_packet_drafting_does_not_select_concrete_substrate(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture("phase115_no_substrate", expected_allowed_to_answer_directly=True)
        )
        text = render_boundary_packet_text(build_boundary_packet_draft(pipeline).packet_draft).lower()

        for forbidden in (
            "selected_provider",
            "selected_model",
            "selected_runtime",
            "selected_platform",
            "selected_worker_substrate",
            "invoke codex",
            "invoke hermes",
            "invoke openclaw",
            "run ollama",
        ):
            self.assertNotIn(forbidden, text)

    def test_packet_drafting_preserves_no_activity_flags(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture("phase115_flags", expected_allowed_to_answer_directly=True)
        )
        result = build_boundary_packet_draft(pipeline)

        self.assertEqual(set(result.no_activity_flags.values()), {False})
        self.assert_no_activity(result)

    def test_packet_drafting_does_not_mutate_input_pipeline_or_admission_object(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture("phase115_immutable", expected_allowed_to_answer_directly=True)
        )
        before = copy.deepcopy(pipeline)
        admission_before = copy.deepcopy(pipeline.admission_decision)

        build_boundary_packet_draft(pipeline)

        self.assertEqual(pipeline, before)
        self.assertEqual(pipeline.admission_decision, admission_before)

    def test_module_does_not_import_forbidden_execution_provider_platform_runtime_libraries(self):
        source = inspect.getsource(boundary_packet)

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

    def test_regression_with_phase114_safe_coding_report_pipeline_output(self):
        pipeline = run_fixture_admission_pipeline(
            self.fixture(
                "phase115_regression",
                "planning_request",
                expected_required_capabilities=("planning_report",),
                expected_next_action="prepare_non_executing_coding_report",
            )
        )
        result = build_boundary_packet_draft(pipeline)

        self.assertTrue(pipeline.accepted)
        self.assertTrue(result.accepted)
        self.assertEqual(result.packet_draft.packet_kind, "coding_worker_report_only")
        self.assertEqual(result.packet_draft.next_review_boundary, "coordinator_review_required_before_any_dispatch_or_acceptance")


if __name__ == "__main__":
    unittest.main()
