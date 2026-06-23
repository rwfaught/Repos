import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.manual_review_cli import build_manual_review_cli_output


def valid_general_answer_input(**overrides):
    value = {
        "request_id": "ga-real-258",
        "request_type": "general_answer",
        "risk_level": "low",
        "user_intent_summary": "Explain what the lightweight general-answer report-only lane can currently do.",
        "accepted_facts": ["operator_provided_structured_input=true"],
        "caveats": ["real_input_report_only_cli_adapter=true"],
        "recommended_next_action": "surface_lightweight_general_answer_report_for_manual_review",
    }
    value.update(overrides)
    return value


class Phase258GeneralAnswerJsonBomToleranceTests(unittest.TestCase):
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

    def test_normal_utf8_structured_general_answer_with_artifact_still_works(self):
        input_path = self.write_json(valid_general_answer_input())
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertTrue(artifact_path.exists())
        self.assertIn("Lightweight General Answer Report", result.output_text)

    def test_bom_prefixed_structured_general_answer_exits_zero_and_creates_artifact(self):
        input_path = self.write_json(valid_general_answer_input(), encoding="utf-8-sig")
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertTrue(artifact_path.exists())

    def test_bom_prefixed_artifact_preserves_required_report_only_flags(self):
        input_path = self.write_json(valid_general_answer_input(), encoding="utf-8-sig")
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(payload["request_type"], "general_answer")
        self.assertTrue(payload["lightweight_answer_report_present"])
        self.assertFalse(payload["production_readiness"])
        self.assertTrue(payload["report_only"])
        self.assertFalse(payload["provider_execution"])
        self.assertFalse(payload["model_execution"])
        self.assertFalse(payload["runtime_execution"])
        self.assertFalse(payload["rag_lookup"])
        self.assertFalse(payload["web_lookup"])
        self.assertFalse(payload["scheduler_execution"])
        self.assertFalse(payload["connector_execution"])
        self.assertFalse(payload["worker_dispatch"])
        self.assertFalse(payload["codex_dispatch"])
        self.assertFalse(payload["service_api_ui"])

    def test_malformed_json_is_still_rejected_nonzero(self):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", suffix=".json", delete=False)
        with handle:
            handle.write("{not-json")
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))

        result = build_manual_review_cli_output(["--general-answer-input", handle.name])

        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse(result.accepted)
        self.assertIn("malformed JSON", result.error_text)
        self.assertNotIn("Lightweight General Answer Report", result.output_text)

    def test_wrong_request_type_is_still_rejected_without_artifact(self):
        input_path = self.write_json(valid_general_answer_input(request_type="coding_task"), encoding="utf-8-sig")
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse(result.accepted)
        self.assertIn("wrong_request_type", result.error_text)
        self.assertFalse(artifact_path.exists())

    def test_unsafe_input_is_still_rejected_without_artifact(self):
        input_path = self.write_json(
            valid_general_answer_input(requires_provider_execution=True),
            encoding="utf-8-sig",
        )
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse(result.accepted)
        self.assertIn("requires_provider_model_or_runtime_execution", result.error_text)
        self.assertFalse(artifact_path.exists())


if __name__ == "__main__":
    unittest.main()
