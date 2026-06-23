import inspect
import json
import tempfile
import unittest
from pathlib import Path

from orchestrator import manual_review_cli
from orchestrator.manual_review_cli import build_manual_review_cli_output


REQUIRED_FALSE_ACTIVITY_FLAGS = (
    "mutation_performed",
    "execution_performed",
    "provider_executed",
    "model_executed",
    "runtime_executed",
    "wsl_executed",
    "installer_executed",
    "discord_executed",
    "bridge_executed",
    "adapter_executed",
    "platform_executed",
    "export_performed",
    "package_performed",
    "cleanup_performed",
    "deletion_performed",
    "archive_performed",
    "rag_lookup_performed",
    "web_lookup_performed",
    "scheduler_executed",
    "connector_executed",
    "worker_dispatched",
    "codex_dispatched",
)

REQUIRED_NON_PROOFS = (
    "not_semantic_correctness_proof",
    "not_model_backed_generation",
    "not_provider_execution",
    "not_runtime_execution",
    "not_live_router_proof",
    "not_rag_or_local_lookup",
    "not_web_lookup",
    "not_scheduler_or_reminder_execution",
    "not_connector_execution",
    "not_worker_dispatch",
    "not_codex_dispatch",
    "not_production_readiness",
)

FORBIDDEN_IMPORTS = (
    "import requests",
    "import subprocess",
    "import openai",
    "import ollama",
    "import discord",
    "import click",
    "import typer",
    "from orchestrator.provider",
    "from orchestrator.platform",
    "from orchestrator.connector",
    "from orchestrator.scheduler",
    "from orchestrator.service",
    "from orchestrator.api",
    "from orchestrator.ui",
    "from orchestrator.openclaw",
    "from orchestrator.hermes",
    "from orchestrator.wsl",
)


def valid_general_answer_input(**overrides):
    value = {
        "request_id": "ga-real-001",
        "request_type": "general_answer",
        "risk_level": "low",
        "user_intent_summary": "Explain what the lightweight general-answer report-only lane can currently do.",
        "accepted_facts": ["operator_provided_structured_input=true"],
        "caveats": ["real_input_report_only_cli_adapter=true"],
        "recommended_next_action": "surface_lightweight_general_answer_report_for_manual_review",
    }
    value.update(overrides)
    return value


class Phase256GeneralAnswerRealInputReportOnlyCliAdapterTests(unittest.TestCase):
    def write_json(self, value):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
        with handle:
            json.dump(value, handle)
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        return handle.name

    def test_help_text_includes_general_answer_input_option(self):
        result = build_manual_review_cli_output(["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("--general-answer-input <json_path>", result.output_text)
        self.assertIn("--list-fixtures", result.output_text)
        self.assertIn("--fixture <fixture_id>", result.output_text)

    def test_valid_structured_general_answer_input_returns_existing_review_shape(self):
        path = self.write_json(valid_general_answer_input())
        result = build_manual_review_cli_output(["--general-answer-input", path])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        for expected in (
            "Assessment",
            "Accepted Facts",
            "Decision",
            "NBM",
            "RESPONSE_METADATA",
            "Lightweight General Answer Report",
            "PHASE_235",
            "general_answer_lightweight_report_only_contract",
            "request_type=general_answer",
            "production_readiness=False",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, result.output_text)

    def test_valid_structured_input_preserves_no_activity_flags(self):
        path = self.write_json(valid_general_answer_input())
        result = build_manual_review_cli_output(["--general-answer-input", path])

        for flag in REQUIRED_FALSE_ACTIVITY_FLAGS:
            with self.subTest(flag=flag):
                self.assertIn(flag, result.no_activity_flags)
                self.assertFalse(result.no_activity_flags[flag])

    def test_valid_structured_input_preserves_lightweight_non_proofs(self):
        path = self.write_json(valid_general_answer_input())
        result = build_manual_review_cli_output(["--general-answer-input", path])

        for non_proof in REQUIRED_NON_PROOFS:
            with self.subTest(non_proof=non_proof):
                self.assertIn(non_proof, result.output_text)
                self.assertIn(non_proof, result.non_proofs)

    def test_wrong_request_type_is_rejected_before_accepted_lightweight_report(self):
        path = self.write_json(valid_general_answer_input(request_type="coding_task"))
        result = build_manual_review_cli_output(["--general-answer-input", path])

        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse(result.accepted)
        self.assertIn("wrong_request_type", result.error_text)
        self.assertNotIn("Lightweight General Answer Report", result.output_text)
        self.assertIn("runner_review_started=false", result.output_text)

    def test_high_risk_input_is_rejected_before_accepted_lightweight_report(self):
        path = self.write_json(valid_general_answer_input(risk_level="high"))
        result = build_manual_review_cli_output(["--general-answer-input", path])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("high_or_critical_risk", result.error_text)
        self.assertNotIn("Lightweight General Answer Report", result.output_text)

    def test_unknown_risk_input_is_rejected_conservatively(self):
        path = self.write_json(valid_general_answer_input(risk_level="medium"))
        result = build_manual_review_cli_output(["--general-answer-input", path])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("not_low_risk_general_answer", result.error_text)
        self.assertNotIn("Lightweight General Answer Report", result.output_text)

    def test_external_or_execution_requirements_are_rejected_conservatively(self):
        blockers = {
            "requires_file_mutation": "requires_file_mutation",
            "allowed_to_mutate_files": "requires_file_mutation",
            "requires_mutation": "requires_file_mutation",
            "requires_scheduling": "requires_scheduling",
            "allowed_to_schedule": "requires_scheduling",
            "requires_reminder": "requires_scheduling",
            "requires_local_documents": "requires_local_documents_or_rag",
            "requires_rag_lookup": "requires_local_documents_or_rag",
            "allowed_to_use_local_documents": "requires_local_documents_or_rag",
            "requires_web_lookup": "requires_web_lookup",
            "allowed_to_use_web": "requires_web_lookup",
            "requires_external_connector": "requires_external_connector",
            "requires_connector": "requires_external_connector",
            "requires_provider_execution": "requires_provider_model_or_runtime_execution",
            "requires_model_execution": "requires_provider_model_or_runtime_execution",
            "requires_runtime_execution": "requires_provider_model_or_runtime_execution",
            "provider_execution_required": "requires_provider_model_or_runtime_execution",
            "model_execution_required": "requires_provider_model_or_runtime_execution",
            "runtime_execution_required": "requires_provider_model_or_runtime_execution",
            "production_readiness": "claims_production_readiness",
            "claims_production_readiness": "claims_production_readiness",
        }

        for field, expected_blocker in blockers.items():
            with self.subTest(field=field):
                path = self.write_json(valid_general_answer_input(**{field: True}))
                result = build_manual_review_cli_output(["--general-answer-input", path])

                self.assertNotEqual(result.exit_code, 0)
                self.assertIn(expected_blocker, result.error_text)
                self.assertNotIn("Lightweight General Answer Report", result.output_text)

    def test_missing_required_fields_are_rejected_before_runner_call(self):
        path = self.write_json(valid_general_answer_input(request_id="", user_intent_summary=""))
        result = build_manual_review_cli_output(["--general-answer-input", path])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("request_id", result.error_text)
        self.assertIn("user_intent_summary", result.error_text)
        self.assertIn("runner_review_started=false", result.output_text)

    def test_malformed_json_returns_deterministic_nonzero_without_review(self):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
        with handle:
            handle.write("{not-json")
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))

        result = build_manual_review_cli_output(["--general-answer-input", handle.name])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("malformed JSON", result.error_text)
        self.assertNotIn("Assessment", result.output_text)
        self.assertFalse(result.accepted)

    def test_missing_file_path_returns_deterministic_nonzero_without_review(self):
        result = build_manual_review_cli_output(["--general-answer-input"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("requires exactly one JSON path", result.error_text)
        self.assertNotIn("Assessment", result.output_text)
        self.assertFalse(result.accepted)

    def test_missing_file_returns_deterministic_nonzero_without_review(self):
        missing_path = str(Path(tempfile.gettempdir()) / "phase256_missing_general_answer_input.json")
        Path(missing_path).unlink(missing_ok=True)
        result = build_manual_review_cli_output(["--general-answer-input", missing_path])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("could not read general-answer input", result.error_text)
        self.assertNotIn("Assessment", result.output_text)
        self.assertFalse(result.accepted)

    def test_existing_fixture_behavior_still_passes(self):
        direct = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])
        coding = build_manual_review_cli_output(["--fixture", "safe_coding_source_test_mutation"])

        self.assertEqual(direct.exit_code, 0)
        self.assertIn("Lightweight General Answer Report", direct.output_text)
        self.assertEqual(coding.exit_code, 0)
        self.assertNotIn("Lightweight General Answer Report", coding.output_text)

    def test_cli_module_avoids_forbidden_imports_and_surfaces(self):
        source = inspect.getsource(manual_review_cli)

        for forbidden in FORBIDDEN_IMPORTS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
