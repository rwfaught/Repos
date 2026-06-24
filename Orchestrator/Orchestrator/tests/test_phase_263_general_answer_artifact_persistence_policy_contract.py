import inspect
import json
import tempfile
import unittest
from pathlib import Path

from orchestrator import general_answer_artifact_policy, manual_review_cli
from orchestrator.general_answer_artifact_policy import build_general_answer_artifact_persistence_policy
from orchestrator.manual_review_cli import build_manual_review_cli_output


ARTIFACT_NOTICE = "Review JSON Artifact Written:"

NON_EXECUTION_FALSE_FLAGS = (
    "production_readiness",
    "provider_execution",
    "model_execution",
    "runtime_execution",
    "rag_lookup",
    "web_lookup",
    "scheduler_execution",
    "connector_execution",
    "worker_dispatch",
    "codex_dispatch",
    "service_api_ui",
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
        "request_id": "ga-real-263",
        "request_type": "general_answer",
        "risk_level": "low",
        "user_intent_summary": "Explain what the lightweight general-answer report-only lane can currently do.",
        "accepted_facts": ["operator_provided_structured_input=true"],
        "caveats": ["real_input_report_only_cli_adapter=true"],
        "recommended_next_action": "surface_lightweight_general_answer_report_for_manual_review",
    }
    value.update(overrides)
    return value


class Phase263GeneralAnswerArtifactPersistencePolicyTests(unittest.TestCase):
    def write_json(self, value, *, encoding="utf-8"):
        handle = tempfile.NamedTemporaryFile("w", encoding=encoding, suffix=".json", delete=False)
        with handle:
            json.dump(value, handle)
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        return handle.name

    def artifact_path(self):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
        path = Path(handle.name)
        handle.close()
        path.unlink(missing_ok=True)
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        return path

    def test_policy_without_artifact_path_reports_no_persistence_requested(self):
        policy = build_general_answer_artifact_persistence_policy(None)

        self.assertFalse(policy["artifact_persistence_requested"])
        self.assertEqual(policy["artifact_path_source"], "none")
        self.assertFalse(policy["artifact_path_required"])

    def test_policy_without_artifact_path_disables_default_artifact_path(self):
        policy = build_general_answer_artifact_persistence_policy(None)

        self.assertFalse(policy["default_artifact_path_enabled"])
        self.assertIsNone(policy["default_artifact_path"])

    def test_policy_without_artifact_path_reports_no_success_notice(self):
        policy = build_general_answer_artifact_persistence_policy(None)

        self.assertFalse(policy["artifact_write_notice_on_success"])
        self.assertFalse(policy["artifact_write_notice_when_omitted"])

    def test_policy_with_caller_supplied_path_reports_persistence_requested(self):
        policy = build_general_answer_artifact_persistence_policy("artifact.json")

        self.assertTrue(policy["artifact_persistence_requested"])
        self.assertTrue(policy["artifact_path_required"])

    def test_policy_with_caller_supplied_path_reports_caller_supplied_source(self):
        policy = build_general_answer_artifact_persistence_policy("artifact.json")

        self.assertEqual(policy["artifact_path_source"], "caller_supplied")

    def test_policy_with_caller_supplied_path_still_disables_default_path(self):
        policy = build_general_answer_artifact_persistence_policy("artifact.json")

        self.assertFalse(policy["default_artifact_path_enabled"])
        self.assertIsNone(policy["default_artifact_path"])

    def test_policy_with_caller_supplied_path_reports_success_notice_on_success(self):
        policy = build_general_answer_artifact_persistence_policy("artifact.json")

        self.assertTrue(policy["artifact_write_notice_on_success"])
        self.assertFalse(policy["artifact_write_notice_when_omitted"])
        self.assertFalse(policy["artifact_write_notice_for_rejected_input"])

    def test_policy_preserves_report_only_and_non_execution_flags(self):
        policy = build_general_answer_artifact_persistence_policy("artifact.json")

        self.assertTrue(policy["report_only"])
        for flag in NON_EXECUTION_FALSE_FLAGS:
            with self.subTest(flag=flag):
                self.assertFalse(policy[flag])
        self.assertFalse(policy["fixture_mode_artifact_persistence"])

    def test_valid_input_without_write_review_json_creates_no_artifact_and_no_notice(self):
        input_path = self.write_json(valid_general_answer_input())
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(["--general-answer-input", input_path])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertFalse(artifact_path.exists())
        self.assertNotIn(ARTIFACT_NOTICE, result.output_text)

    def test_valid_input_with_write_review_json_creates_artifact_notices_and_includes_policy(self):
        input_path = self.write_json(valid_general_answer_input())
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        policy = payload["artifact_persistence_policy"]

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertTrue(artifact_path.exists())
        self.assertIn(ARTIFACT_NOTICE, result.output_text)
        self.assertIn(str(artifact_path), result.output_text)
        self.assertTrue(policy["artifact_persistence_requested"])
        self.assertEqual(policy["artifact_path_source"], "caller_supplied")
        self.assertFalse(policy["default_artifact_path_enabled"])
        self.assertTrue(policy["artifact_write_notice_on_success"])
        self.assertTrue(policy["report_only"])
        for flag in NON_EXECUTION_FALSE_FLAGS:
            with self.subTest(flag=flag):
                self.assertFalse(policy[flag])

    def test_bom_valid_input_with_write_review_json_still_creates_artifact_and_notice(self):
        input_path = self.write_json(valid_general_answer_input(), encoding="utf-8-sig")
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(artifact_path.exists())
        self.assertIn(ARTIFACT_NOTICE, result.output_text)

    def test_unsafe_rejected_input_has_no_notice_and_no_persistence_success(self):
        input_path = self.write_json(valid_general_answer_input(requires_provider_execution=True))
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse(result.accepted)
        self.assertIn("requires_provider_model_or_runtime_execution", result.error_text)
        self.assertNotIn(ARTIFACT_NOTICE, result.output_text)
        self.assertFalse(artifact_path.exists())

    def test_fixture_mode_has_no_notice_and_no_persistence_success(self):
        direct = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])
        coding = build_manual_review_cli_output(["--fixture", "safe_coding_source_test_mutation"])

        self.assertEqual(direct.exit_code, 0)
        self.assertIn("Lightweight General Answer Report", direct.output_text)
        self.assertNotIn(ARTIFACT_NOTICE, direct.output_text)
        self.assertEqual(coding.exit_code, 0)
        self.assertNotIn("Lightweight General Answer Report", coding.output_text)
        self.assertNotIn(ARTIFACT_NOTICE, coding.output_text)

    def test_policy_and_cli_modules_avoid_forbidden_imports_and_surfaces(self):
        source = inspect.getsource(general_answer_artifact_policy) + "\n" + inspect.getsource(manual_review_cli)

        for forbidden in FORBIDDEN_IMPORTS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
