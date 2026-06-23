import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.manual_review_cli import build_manual_review_cli_output


def valid_general_answer_input(**overrides):
    value = {
        "request_id": "ga-real-257",
        "request_type": "general_answer",
        "risk_level": "low",
        "user_intent_summary": "Explain what the lightweight general-answer report-only lane can currently do.",
        "accepted_facts": ["operator_provided_structured_input=true"],
        "caveats": ["real_input_report_only_cli_adapter=true"],
        "recommended_next_action": "surface_lightweight_general_answer_report_for_manual_review",
    }
    value.update(overrides)
    return value


class Phase257GeneralAnswerRealInputReviewArtifactPersistenceTests(unittest.TestCase):
    def write_json(self, value):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
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

    def test_help_text_includes_explicit_persistence_option(self):
        result = build_manual_review_cli_output(["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("--write-review-json <artifact_json_path>", result.output_text)
        self.assertIn("--general-answer-input <json_path>", result.output_text)

    def test_valid_input_with_write_review_json_exits_zero_and_creates_artifact(self):
        input_path = self.write_json(valid_general_answer_input())
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertTrue(artifact_path.exists())

    def test_artifact_json_contains_required_report_only_shape(self):
        input_path = self.write_json(valid_general_answer_input())
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(payload["phase"], "PHASE_257")
        self.assertEqual(payload["artifact_kind"], "general_answer_real_input_review_artifact_persistence")
        self.assertEqual(payload["request_id"], "ga-real-257")
        self.assertEqual(payload["request_type"], "general_answer")
        self.assertTrue(payload["accepted"])
        self.assertFalse(payload["blocked"])
        self.assertEqual(payload["cli_result_status"], "accepted")
        self.assertEqual(payload["exit_code_intent"], 0)
        self.assertIn("Assessment", payload["manual_review_text"])
        self.assertIn("Lightweight General Answer Report", payload["manual_review_text"])
        self.assertTrue(payload["lightweight_answer_report_present"])
        self.assertIsInstance(payload["lightweight_answer_report_payload"], dict)
        self.assertIn("not_semantic_correctness_proof", payload["non_proofs"])
        self.assertIn("real_input_report_only_cli_adapter=true", payload["caveats"])
        self.assertTrue(all(flag is False for flag in payload["no_activity_flags"].values()))
        self.assertFalse(payload["production_readiness"])
        self.assertEqual(payload["source_input_kind"], "structured_local_general_answer_json")
        self.assertTrue(payload["report_only"])
        self.assertFalse(payload["runtime_execution"])
        self.assertFalse(payload["provider_execution"])
        self.assertFalse(payload["model_execution"])
        self.assertFalse(payload["rag_lookup"])
        self.assertFalse(payload["web_lookup"])
        self.assertFalse(payload["scheduler_execution"])
        self.assertFalse(payload["connector_execution"])
        self.assertFalse(payload["worker_dispatch"])
        self.assertFalse(payload["codex_dispatch"])
        self.assertFalse(payload["service_api_ui"])
        self.assertFalse(payload["lightweight_answer_report_payload"]["production_readiness"])

    def test_stdout_still_contains_existing_review_sections_and_lightweight_report(self):
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
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, result.output_text)

    def test_phase_256_valid_real_input_still_passes_without_persistence(self):
        input_path = self.write_json(valid_general_answer_input())

        result = build_manual_review_cli_output(["--general-answer-input", input_path])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertIn("Lightweight General Answer Report", result.output_text)

    def test_wrong_request_type_is_rejected_without_accepted_lightweight_report(self):
        input_path = self.write_json(valid_general_answer_input(request_type="coding_task"))
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse(result.accepted)
        self.assertIn("wrong_request_type", result.error_text)
        self.assertNotIn("Lightweight General Answer Report", result.output_text)
        self.assertFalse(artifact_path.exists())

    def test_high_risk_input_is_rejected_without_accepted_lightweight_report(self):
        input_path = self.write_json(valid_general_answer_input(risk_level="high"))
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("high_or_critical_risk", result.error_text)
        self.assertNotIn("Lightweight General Answer Report", result.output_text)
        self.assertFalse(artifact_path.exists())

    def test_external_or_execution_requirements_are_rejected_conservatively(self):
        blockers = {
            "requires_file_mutation": "requires_file_mutation",
            "requires_provider_execution": "requires_provider_model_or_runtime_execution",
            "requires_model_execution": "requires_provider_model_or_runtime_execution",
            "requires_runtime_execution": "requires_provider_model_or_runtime_execution",
            "requires_rag_lookup": "requires_local_documents_or_rag",
            "requires_local_documents": "requires_local_documents_or_rag",
            "requires_web_lookup": "requires_web_lookup",
            "requires_scheduling": "requires_scheduling",
            "requires_reminder": "requires_scheduling",
            "requires_external_connector": "requires_external_connector",
            "requires_connector": "requires_external_connector",
            "production_readiness": "claims_production_readiness",
        }

        for field, expected_blocker in blockers.items():
            with self.subTest(field=field):
                input_path = self.write_json(valid_general_answer_input(**{field: True}))
                artifact_path = self.artifact_path()
                result = build_manual_review_cli_output(
                    ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
                )

                self.assertNotEqual(result.exit_code, 0)
                self.assertIn(expected_blocker, result.error_text)
                self.assertNotIn("Lightweight General Answer Report", result.output_text)
                self.assertFalse(artifact_path.exists())

    def test_invalid_artifact_path_fails_deterministically_without_success_claim(self):
        input_path = self.write_json(valid_general_answer_input())
        missing_parent = Path(tempfile.gettempdir()) / "phase257_missing_parent" / "artifact.json"
        if missing_parent.parent.exists():
            self.skipTest("missing-parent path unexpectedly exists")

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(missing_parent)]
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse(result.accepted)
        self.assertIn("could not write review JSON artifact", result.error_text)
        self.assertNotIn("Lightweight General Answer Report", result.output_text)
        self.assertFalse(missing_parent.exists())

    def test_fixture_behavior_remains_intact(self):
        direct = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])
        coding = build_manual_review_cli_output(["--fixture", "safe_coding_source_test_mutation"])

        self.assertEqual(direct.exit_code, 0)
        self.assertIn("Lightweight General Answer Report", direct.output_text)
        self.assertEqual(coding.exit_code, 0)
        self.assertNotIn("Lightweight General Answer Report", coding.output_text)


if __name__ == "__main__":
    unittest.main()
