import inspect
import json
import tempfile
import unittest
from pathlib import Path

from orchestrator import general_answer_local_first_policy, manual_review_cli
from orchestrator.general_answer_local_first_policy import build_general_answer_local_first_fallback_policy
from orchestrator.manual_review_cli import build_manual_review_cli_output


ARTIFACT_NOTICE = "Review JSON Artifact Written:"

FALSE_POLICY_FLAGS = (
    "execution_authorized",
    "answer_generation_authorized",
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
    "import socket",
    "import urllib",
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
        "request_id": "ga-real-265",
        "request_type": "general_answer",
        "risk_level": "low",
        "user_intent_summary": "Explain what the lightweight general-answer report-only lane can currently do.",
        "accepted_facts": ["operator_provided_structured_input=true"],
        "caveats": ["real_input_report_only_cli_adapter=true"],
        "recommended_next_action": "surface_lightweight_general_answer_report_for_manual_review",
    }
    value.update(overrides)
    return value


class Phase265GeneralAnswerLocalFirstFallbackPolicyTests(unittest.TestCase):
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

    def assert_policy_is_non_executing(self, policy):
        self.assertTrue(policy["report_only"])
        for flag in FALSE_POLICY_FLAGS:
            with self.subTest(flag=flag):
                self.assertIn(flag, policy)
                self.assertFalse(policy[flag])

    def test_low_risk_general_answer_with_local_facts_is_report_only_candidate(self):
        policy = build_general_answer_local_first_fallback_policy(valid_general_answer_input())

        self.assertEqual(policy["request_type"], "general_answer")
        self.assertTrue(policy["local_first_policy_enabled"])
        self.assertEqual(policy["recommended_answer_posture"], "local_report_only_answer_candidate")
        self.assertEqual(policy["fallback_posture"], "manual_review")
        self.assertFalse(policy["clarification_required"])
        self.assertFalse(policy["block_required"])
        self.assertEqual(policy["missing_requirements"], [])
        self.assertEqual(policy["blockers"], [])
        self.assertIn("sufficient_local_facts_observed", policy["caveats"])
        self.assert_policy_is_non_executing(policy)

    def test_missing_accepted_facts_clarifies_before_answer(self):
        policy = build_general_answer_local_first_fallback_policy(valid_general_answer_input(accepted_facts=[]))

        self.assertEqual(policy["recommended_answer_posture"], "clarify_before_answer")
        self.assertTrue(policy["clarification_required"])
        self.assertFalse(policy["block_required"])
        self.assertIn("accepted_facts", policy["missing_requirements"])
        self.assert_policy_is_non_executing(policy)

    def test_missing_user_intent_clarifies_before_answer(self):
        policy = build_general_answer_local_first_fallback_policy(valid_general_answer_input(user_intent_summary=""))

        self.assertEqual(policy["recommended_answer_posture"], "clarify_before_answer")
        self.assertTrue(policy["clarification_required"])
        self.assertIn("user_intent_summary", policy["missing_requirements"])
        self.assert_policy_is_non_executing(policy)

    def test_provider_model_runtime_requests_are_blocked_without_execution_authority(self):
        blockers = {
            "requires_provider_execution": "provider_execution_requested",
            "provider_execution_required": "provider_execution_requested",
            "requires_model_execution": "model_execution_requested",
            "model_execution_required": "model_execution_requested",
            "requires_runtime_execution": "runtime_execution_requested",
            "runtime_execution_required": "runtime_execution_requested",
        }

        for field, expected in blockers.items():
            with self.subTest(field=field):
                policy = build_general_answer_local_first_fallback_policy(valid_general_answer_input(**{field: True}))

                self.assertEqual(policy["recommended_answer_posture"], "blocked_execution_request")
                self.assertTrue(policy["block_required"])
                self.assertIn(expected, policy["blockers"])
                self.assert_policy_is_non_executing(policy)

    def test_lookup_scheduler_connector_dispatch_and_service_requests_are_blocked(self):
        blockers = {
            "requires_rag_lookup": "rag_lookup_requested",
            "allowed_to_use_local_documents": "rag_lookup_requested",
            "requires_web_lookup": "web_lookup_requested",
            "allowed_to_use_web": "web_lookup_requested",
            "requires_scheduling": "scheduler_execution_requested",
            "allowed_to_schedule": "scheduler_execution_requested",
            "requires_external_connector": "connector_execution_requested",
            "requires_worker_dispatch": "worker_dispatch_requested",
            "requires_codex_dispatch": "codex_dispatch_requested",
            "requires_service_api_ui": "service_api_ui_requested",
        }

        for field, expected in blockers.items():
            with self.subTest(field=field):
                policy = build_general_answer_local_first_fallback_policy(valid_general_answer_input(**{field: True}))

                self.assertEqual(policy["recommended_answer_posture"], "blocked_execution_request")
                self.assertTrue(policy["block_required"])
                self.assertIn(expected, policy["blockers"])
                self.assert_policy_is_non_executing(policy)

    def test_high_risk_general_answer_manual_review_or_block(self):
        policy = build_general_answer_local_first_fallback_policy(valid_general_answer_input(risk_level="high"))

        self.assertEqual(policy["recommended_answer_posture"], "manual_review_or_block")
        self.assertTrue(policy["block_required"])
        self.assertIn("high_or_critical_risk", policy["blockers"])
        self.assert_policy_is_non_executing(policy)

    def test_unknown_risk_general_answer_manual_review_or_block(self):
        policy = build_general_answer_local_first_fallback_policy(valid_general_answer_input(risk_level="medium"))

        self.assertEqual(policy["recommended_answer_posture"], "manual_review_or_block")
        self.assertTrue(policy["block_required"])
        self.assertIn("unknown_or_non_low_risk", policy["blockers"])
        self.assert_policy_is_non_executing(policy)

    def test_non_general_answer_is_not_applicable(self):
        policy = build_general_answer_local_first_fallback_policy(valid_general_answer_input(request_type="coding_task"))

        self.assertFalse(policy["local_first_policy_enabled"])
        self.assertEqual(policy["recommended_answer_posture"], "not_applicable")
        self.assertEqual(policy["fallback_posture"], "route_by_request_type")
        self.assertFalse(policy["block_required"])
        self.assert_policy_is_non_executing(policy)

    def test_successful_real_input_artifact_includes_local_first_policy_payload(self):
        input_path = self.write_json(valid_general_answer_input())
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        policy = payload["general_answer_local_first_policy"]

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertIn(ARTIFACT_NOTICE, result.output_text)
        self.assertEqual(policy["recommended_answer_posture"], "local_report_only_answer_candidate")
        self.assertEqual(policy["fallback_posture"], "manual_review")
        self.assert_policy_is_non_executing(policy)

    def test_artifact_preserves_existing_artifact_persistence_policy_payload(self):
        input_path = self.write_json(valid_general_answer_input())
        artifact_path = self.artifact_path()

        build_manual_review_cli_output(["--general-answer-input", input_path, "--write-review-json", str(artifact_path)])
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        persistence_policy = payload["artifact_persistence_policy"]

        self.assertTrue(persistence_policy["artifact_persistence_requested"])
        self.assertEqual(persistence_policy["artifact_path_source"], "caller_supplied")
        self.assertFalse(persistence_policy["default_artifact_path_enabled"])
        self.assertTrue(persistence_policy["artifact_write_notice_on_success"])

    def test_without_write_review_json_no_artifact_or_notice_is_created(self):
        input_path = self.write_json(valid_general_answer_input())
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(["--general-answer-input", input_path])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertFalse(artifact_path.exists())
        self.assertNotIn(ARTIFACT_NOTICE, result.output_text)

    def test_rejected_input_does_not_write_policy_artifact(self):
        input_path = self.write_json(valid_general_answer_input(requires_provider_execution=True))
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse(result.accepted)
        self.assertIn("requires_provider_model_or_runtime_execution", result.error_text)
        self.assertFalse(artifact_path.exists())
        self.assertNotIn(ARTIFACT_NOTICE, result.output_text)

    def test_fixture_behavior_has_no_artifact_policy_payload_or_notice(self):
        direct = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])
        coding = build_manual_review_cli_output(["--fixture", "safe_coding_source_test_mutation"])

        self.assertEqual(direct.exit_code, 0)
        self.assertIn("Lightweight General Answer Report", direct.output_text)
        self.assertNotIn(ARTIFACT_NOTICE, direct.output_text)
        self.assertNotIn("general_answer_local_first_policy", direct.output_text)
        self.assertEqual(coding.exit_code, 0)
        self.assertNotIn("Lightweight General Answer Report", coding.output_text)
        self.assertNotIn(ARTIFACT_NOTICE, coding.output_text)

    def test_bom_prefixed_real_input_still_creates_policy_artifact_and_notice(self):
        input_path = self.write_json(valid_general_answer_input(), encoding="utf-8-sig")
        artifact_path = self.artifact_path()

        result = build_manual_review_cli_output(
            ["--general-answer-input", input_path, "--write-review-json", str(artifact_path)]
        )
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))

        self.assertEqual(result.exit_code, 0)
        self.assertIn(ARTIFACT_NOTICE, result.output_text)
        self.assertEqual(
            payload["general_answer_local_first_policy"]["recommended_answer_posture"],
            "local_report_only_answer_candidate",
        )

    def test_policy_payload_is_json_serializable_and_has_required_stable_fields(self):
        policy = build_general_answer_local_first_fallback_policy(valid_general_answer_input())
        required_fields = (
            "request_type",
            "local_first_policy_enabled",
            "report_only",
            "execution_authorized",
            "answer_generation_authorized",
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
            "recommended_answer_posture",
            "fallback_posture",
            "clarification_required",
            "block_required",
            "missing_requirements",
            "blockers",
            "caveats",
        )

        json.dumps(policy, sort_keys=True)
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, policy)

    def test_policy_and_cli_modules_avoid_forbidden_imports_and_surfaces(self):
        source = inspect.getsource(general_answer_local_first_policy) + "\n" + inspect.getsource(manual_review_cli)

        for forbidden in FORBIDDEN_IMPORTS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
