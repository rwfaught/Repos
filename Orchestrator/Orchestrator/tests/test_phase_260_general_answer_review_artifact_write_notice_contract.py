import inspect
import json
import tempfile
import unittest
from pathlib import Path

from orchestrator import manual_review_cli
from orchestrator.manual_review_cli import build_manual_review_cli_output


ARTIFACT_NOTICE = "Review JSON Artifact Written:"

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
        "request_id": "ga-real-260",
        "request_type": "general_answer",
        "risk_level": "low",
        "user_intent_summary": "Explain what the lightweight general-answer report-only lane can currently do.",
        "accepted_facts": ["operator_provided_structured_input=true"],
        "caveats": ["real_input_report_only_cli_adapter=true"],
        "recommended_next_action": "surface_lightweight_general_answer_report_for_manual_review",
    }
    value.update(overrides)
    return value


class Phase260GeneralAnswerReviewArtifactWriteNoticeTests(unittest.TestCase):
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

    def test_valid_structured_input_with_write_review_json_exits_zero_creates_artifact_and_notices_path(self):
        input_path = self.write_json(valid_general_answer_input())
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertTrue(artifact_path.exists())
        self.assertIn(ARTIFACT_NOTICE, result.output_text)
        self.assertIn(str(artifact_path), result.output_text)

    def test_success_notice_preserves_existing_review_sections_and_lightweight_report(self):
        input_path = self.write_json(valid_general_answer_input())
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        for expected in (
            "Assessment",
            "Accepted Facts",
            "Decision",
            "NBM",
            "RESPONSE_METADATA",
            "Lightweight General Answer Report",
            "PHASE_235",
            "general_answer_lightweight_report_only_contract",
            ARTIFACT_NOTICE,
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, result.output_text)

    def test_valid_structured_input_without_write_review_json_omits_notice(self):
        input_path = self.write_json(valid_general_answer_input())

        result = build_manual_review_cli_output(["--general-answer-input", input_path])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertIn("Lightweight General Answer Report", result.output_text)
        self.assertNotIn(ARTIFACT_NOTICE, result.output_text)

    def test_bom_prefixed_valid_input_with_write_review_json_creates_artifact_and_notices_path(self):
        input_path = self.write_json(valid_general_answer_input(), encoding="utf-8-sig")
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(artifact_path.exists())
        self.assertIn(ARTIFACT_NOTICE, result.output_text)
        self.assertIn(str(artifact_path), result.output_text)

    def test_invalid_artifact_path_fails_without_success_notice(self):
        input_path = self.write_json(valid_general_answer_input())
        missing_parent = Path(tempfile.gettempdir()) / "phase260_missing_parent" / "artifact.json"
        if missing_parent.parent.exists():
            self.skipTest("missing-parent path unexpectedly exists")

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(missing_parent)]
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse(result.accepted)
        self.assertIn("could not write review JSON artifact", result.error_text)
        self.assertNotIn(ARTIFACT_NOTICE, result.output_text)
        self.assertFalse(missing_parent.exists())

    def test_unsafe_input_is_rejected_without_success_notice(self):
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

    def test_fixture_safe_direct_answer_remains_intact_without_success_notice(self):
        result = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Lightweight General Answer Report", result.output_text)
        self.assertNotIn(ARTIFACT_NOTICE, result.output_text)

    def test_fixture_safe_coding_source_test_mutation_remains_intact_without_success_notice(self):
        result = build_manual_review_cli_output(["--fixture", "safe_coding_source_test_mutation"])

        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("Lightweight General Answer Report", result.output_text)
        self.assertNotIn(ARTIFACT_NOTICE, result.output_text)

    def test_cli_module_avoids_forbidden_imports_and_surfaces(self):
        source = inspect.getsource(manual_review_cli)

        for forbidden in FORBIDDEN_IMPORTS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
