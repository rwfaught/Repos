import inspect
import unittest

from orchestrator import prompt_to_envelope
from orchestrator.prompt_to_envelope import (
    PromptInferenceDecision,
    PromptInferenceFixture,
    classify_prompt_fixture,
    fixture_to_request_intake,
)
from orchestrator.route_proposal import RequestIntakeRecord, admit_route_proposal


class Phase113PromptToEnvelopeFixtureContractTests(unittest.TestCase):
    def fixture(self, fixture_id="fixture_phase113", request_type="general_answer", **overrides):
        base = {
            "fixture_id": fixture_id,
            "raw_prompt": "Trace-only natural language prompt.",
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

    def assert_no_activity(self, decision):
        self.assertFalse(any(decision.activity_flags.values()))
        self.assertIn("no_route_execution", decision.non_proofs)
        self.assertIn("raw_prompt_text_is_not_parsed_as_authority", decision.non_proofs)

    def test_fixture_module_exposes_required_contract(self):
        self.assertIs(prompt_to_envelope.PromptInferenceFixture, PromptInferenceFixture)
        self.assertIs(prompt_to_envelope.PromptInferenceDecision, PromptInferenceDecision)
        self.assertIs(prompt_to_envelope.classify_prompt_fixture, classify_prompt_fixture)
        self.assertIs(prompt_to_envelope.fixture_to_request_intake, fixture_to_request_intake)

    def test_simple_direct_answer_converts_to_structured_intake_without_execution_authority(self):
        decision = classify_prompt_fixture(
            self.fixture(expected_allowed_to_answer_directly=True)
        )
        intake = fixture_to_request_intake(decision)

        self.assertTrue(decision.accepted)
        self.assertIsInstance(intake, RequestIntakeRecord)
        self.assertEqual(intake.request_type, "general_answer")
        self.assertTrue(intake.allowed_to_answer_directly)
        self.assertFalse(intake.allowed_to_mutate_files)
        self.assert_no_activity(decision)

    def test_coding_report_only_fixture_remains_report_only_and_non_mutating(self):
        decision = classify_prompt_fixture(
            self.fixture(
                "coding_report_only",
                "planning_request",
                expected_required_capabilities=("planning_report",),
                expected_allowed_to_answer_directly=False,
                expected_next_action="prepare_non_executing_coding_report",
            )
        )

        self.assertTrue(decision.accepted)
        self.assertEqual(decision.request_type, "planning_request")
        self.assertFalse(decision.allowed_to_mutate_files)
        self.assertEqual(decision.execution_policy, "fixture_classification_only_no_execution")
        self.assert_no_activity(decision)

    def test_coding_mutation_fixture_requires_explicit_permission_and_remains_non_executing(self):
        blocked = classify_prompt_fixture(
            self.fixture(
                "coding_mutation_blocked",
                "coding_task",
                expected_required_capabilities=("source_inspection", "patch_proposal", "filesystem_mutation_authority"),
                expected_allowed_to_mutate_files=True,
                expected_requires_confirmation=True,
            )
        )
        allowed = classify_prompt_fixture(
            self.fixture(
                "coding_mutation_allowed",
                "coding_task",
                expected_required_capabilities=("source_inspection", "patch_proposal", "filesystem_mutation_authority"),
                expected_allowed_to_mutate_files=True,
                expected_requires_confirmation=True,
                expected_explicit_mutation_permission=True,
            )
        )

        self.assertFalse(blocked.accepted)
        self.assertIn("mutation_requires_explicit_permission_and_confirmation", blocked.blocked_conditions)
        self.assertTrue(allowed.accepted)
        self.assertTrue(allowed.allowed_to_mutate_files)
        self.assert_no_activity(allowed)

    def test_local_document_lookup_requires_source_authority_and_remains_non_executing(self):
        blocked = classify_prompt_fixture(
            self.fixture(
                "local_docs_blocked",
                "local_document_lookup",
                expected_required_capabilities=("local_document_lookup",),
                expected_allowed_to_use_local_documents=True,
            )
        )
        allowed = classify_prompt_fixture(
            self.fixture(
                "local_docs_allowed",
                "local_document_lookup",
                expected_required_capabilities=("local_document_lookup",),
                expected_allowed_to_use_local_documents=True,
                expected_explicit_local_document_authority=True,
            )
        )

        self.assertFalse(blocked.accepted)
        self.assertIn("local_document_lookup_requires_source_authority", blocked.blocked_conditions)
        self.assertTrue(allowed.accepted)
        self.assert_no_activity(allowed)

    def test_web_research_fixture_requires_web_boundary_and_remains_non_executing(self):
        blocked = classify_prompt_fixture(
            self.fixture(
                "web_blocked",
                "research_request",
                expected_required_capabilities=("web_research",),
                expected_allowed_to_use_web=True,
            )
        )
        allowed = classify_prompt_fixture(
            self.fixture(
                "web_allowed",
                "research_request",
                expected_required_capabilities=("web_research",),
                expected_allowed_to_use_web=True,
                expected_explicit_web_boundary=True,
            )
        )

        self.assertFalse(blocked.accepted)
        self.assertIn("web_research_requires_explicit_boundary", blocked.blocked_conditions)
        self.assertTrue(allowed.accepted)
        self.assertIn("web_lookup_not_implemented", allowed.caveats)
        self.assert_no_activity(allowed)

    def test_reminder_scheduler_fixture_requires_confirmation_and_remains_non_executing(self):
        blocked = classify_prompt_fixture(
            self.fixture(
                "reminder_blocked",
                "reminder_request",
                expected_required_capabilities=("scheduling_contract",),
                expected_allowed_to_schedule=True,
            )
        )
        allowed = classify_prompt_fixture(
            self.fixture(
                "reminder_allowed",
                "reminder_request",
                expected_required_capabilities=("scheduling_contract",),
                expected_allowed_to_schedule=True,
                expected_requires_confirmation=True,
                expected_explicit_schedule_confirmation=True,
            )
        )

        self.assertFalse(blocked.accepted)
        self.assertIn("scheduling_requires_explicit_confirmation", blocked.blocked_conditions)
        self.assertTrue(allowed.accepted)
        self.assert_no_activity(allowed)

    def test_connector_required_fixture_routes_to_external_boundary_without_execution(self):
        decision = classify_prompt_fixture(
            self.fixture(
                "connector_required",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("external_connector",),
                expected_requires_external_connector=True,
            )
        )

        self.assertFalse(decision.accepted)
        self.assertIn("connector_requires_explicit_boundary", decision.blocked_conditions)
        self.assert_no_activity(decision)

    def test_platform_runtime_provider_model_fixture_is_blocked_without_execution(self):
        decision = classify_prompt_fixture(
            self.fixture(
                "provider_model_runtime",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("provider_model", "platform_runtime"),
            )
        )

        self.assertFalse(decision.accepted)
        self.assertIn("provider_model_runtime_platform_requires_separate_boundary", decision.blocked_conditions)
        self.assert_no_activity(decision)

    def test_ambiguous_fixture_produces_needs_clarification(self):
        decision = classify_prompt_fixture(
            self.fixture(
                "ambiguous",
                None,
                expected_required_capabilities=(),
                expected_missing_inputs=("declared_request_type",),
            )
        )

        self.assertEqual(decision.route_admission, "needs_clarification")
        self.assertIn("declared_request_type_required", decision.blocked_conditions)
        self.assert_no_activity(decision)

    def test_unsafe_or_unsupported_fixture_is_blocked_or_rejected(self):
        decision = classify_prompt_fixture(
            self.fixture(
                "unsafe",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("unsupported_or_blocked",),
                expected_blocked_reason="unsafe_or_unsupported",
            )
        )

        self.assertFalse(decision.accepted)
        self.assertEqual(decision.route_admission, "rejected")
        self.assertIn("unsupported_or_blocked_capability", decision.blocked_conditions)
        self.assert_no_activity(decision)

    def test_substrate_smuggling_fixture_is_blocked(self):
        decision = classify_prompt_fixture(
            self.fixture(
                "substrate_smuggling",
                "coding_task",
                expected_required_capabilities=("source_inspection",),
                expected_next_action="run with Ollama model",
            )
        )

        self.assertFalse(decision.accepted)
        self.assertIn("substrate_smuggling_blocked", decision.blocked_conditions)
        self.assert_no_activity(decision)

    def test_cleanup_delete_archive_fixture_requires_explicit_permission_and_still_does_not_execute(self):
        blocked = classify_prompt_fixture(
            self.fixture(
                "cleanup_blocked",
                "file_operation",
                expected_required_capabilities=("bounded_file_write",),
                expected_allowed_to_mutate_files=True,
                expected_requires_confirmation=True,
                expected_explicit_mutation_permission=True,
                expected_blocked_reason="cleanup delete archive requested",
            )
        )
        allowed = classify_prompt_fixture(
            self.fixture(
                "cleanup_permission",
                "file_operation",
                expected_required_capabilities=("bounded_file_write",),
                expected_allowed_to_mutate_files=True,
                expected_requires_confirmation=True,
                expected_explicit_mutation_permission=True,
                expected_explicit_cleanup_delete_archive_permission=True,
                expected_blocked_reason="cleanup delete archive requested with permission",
            )
        )

        self.assertFalse(blocked.accepted)
        self.assertIn("cleanup_delete_archive_requires_explicit_permission", blocked.blocked_conditions)
        self.assertTrue(allowed.accepted)
        self.assert_no_activity(allowed)

    def test_export_package_fixture_requires_explicit_permission_and_still_does_not_execute(self):
        blocked = classify_prompt_fixture(
            self.fixture(
                "export_blocked",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("artifact_export_package",),
            )
        )
        allowed = classify_prompt_fixture(
            self.fixture(
                "export_permission",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("artifact_export_package",),
                expected_explicit_export_package_permission=True,
                expected_explicit_connector_boundary=True,
            )
        )

        self.assertFalse(blocked.accepted)
        self.assertIn("export_package_requires_explicit_permission", blocked.blocked_conditions)
        self.assertFalse(allowed.accepted)
        self.assertIn("unsupported_or_requires_connector", allowed.blocked_conditions)
        self.assert_no_activity(allowed)

    def test_production_execution_fixture_is_blocked(self):
        decision = classify_prompt_fixture(
            self.fixture(
                "production_execution",
                "unsupported_or_requires_connector",
                expected_required_capabilities=("production_execution",),
                expected_explicit_production_boundary=True,
            )
        )

        self.assertFalse(decision.accepted)
        self.assertIn("production_execution_blocked", decision.blocked_conditions)
        self.assert_no_activity(decision)

    def test_raw_prompt_text_alone_is_not_inferred_into_a_route(self):
        decision = classify_prompt_fixture(
            PromptInferenceFixture(
                fixture_id="raw_only",
                raw_prompt="Please schedule this and use web research.",
            )
        )

        self.assertFalse(decision.accepted)
        self.assertEqual(decision.route_admission, "needs_clarification")
        self.assertIn("declared_request_type_required", decision.blocked_conditions)
        self.assert_no_activity(decision)

    def test_module_does_not_import_forbidden_execution_provider_platform_libraries(self):
        source = inspect.getsource(prompt_to_envelope)

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

    def test_request_intake_conversion_is_compatible_with_phase111_admission_for_safe_fixture(self):
        intake = fixture_to_request_intake(
            self.fixture(
                "phase111_safe",
                "general_answer",
                expected_required_capabilities=("direct_answer",),
                expected_allowed_to_answer_directly=True,
            )
        )
        decision = admit_route_proposal(intake)

        self.assertTrue(decision.accepted)
        self.assertEqual(decision.route_admission, "accepted")
        self.assertEqual(decision.request_type, "general_answer")
        self.assertFalse(decision.execution_authority)


if __name__ == "__main__":
    unittest.main()
