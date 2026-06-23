import inspect
import unittest

from orchestrator import lightweight_answer_report
from orchestrator.lightweight_answer_report import (
    ARTIFACT_KIND,
    PHASE,
    build_lightweight_general_answer_report,
    render_lightweight_general_answer_report,
)


REQUIRED_FALSE_ACTIVITY_FLAGS = (
    "mutation_performed",
    "execution_performed",
    "provider_executed",
    "model_executed",
    "runtime_executed",
    "wsl_executed",
    "ollama_executed",
    "hermes_executed",
    "openclaw_executed",
    "discord_executed",
    "rag_lookup_performed",
    "web_lookup_performed",
    "scheduler_executed",
    "connector_executed",
    "worker_dispatched",
    "codex_dispatched",
    "export_performed",
    "package_performed",
    "cleanup_performed",
    "deletion_performed",
    "archive_performed",
    "production_executed",
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
    "not_production_readiness",
)

FORBIDDEN_IMPORTS = (
    "import requests",
    "import subprocess",
    "import openai",
    "import ollama",
    "import discord",
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


def valid_request(**overrides):
    request = {
        "request_id": "ga-001",
        "request_type": "general_answer",
        "risk_level": "low",
        "user_intent_summary": "Explain what the current report-only lane can do.",
        "accepted_facts": ["structured_request=true"],
        "recommended_next_action": "surface_report_only_answer_to_operator",
    }
    request.update(overrides)
    return request


class Phase235GeneralAnswerLightweightReportOnlyContractTests(unittest.TestCase):
    def test_valid_low_risk_general_answer_request_is_accepted(self):
        result = build_lightweight_general_answer_report(valid_request())

        self.assertTrue(result.accepted)
        self.assertTrue(result.report.accepted)
        self.assertEqual(result.report.phase, PHASE)
        self.assertEqual(result.report.artifact_kind, ARTIFACT_KIND)
        self.assertEqual(result.report.request_type, "general_answer")
        self.assertEqual(result.report.outcome_classification, "general_answer_lightweight_report_only_accepted")
        self.assertIn("structured_request=true", result.report.accepted_facts)

    def test_accepted_result_has_required_reviewable_shape(self):
        result = build_lightweight_general_answer_report(valid_request())

        self.assertEqual(result.payload["phase"], "PHASE_235")
        self.assertEqual(result.payload["artifact_kind"], "general_answer_lightweight_report_only_contract")
        self.assertEqual(result.payload["request_type"], "general_answer")
        self.assertFalse(result.payload["production_readiness"])
        self.assertIn("Lightweight General Answer Report", result.rendered_text)
        self.assertIn("Report", result.rendered_text)
        self.assertIn(result.report.report_text, result.rendered_text)
        self.assertEqual(render_lightweight_general_answer_report(result.report), result.rendered_text)

    def test_activity_flags_remain_false_for_runtime_and_external_surfaces(self):
        result = build_lightweight_general_answer_report(valid_request())

        for flag in REQUIRED_FALSE_ACTIVITY_FLAGS:
            with self.subTest(flag=flag):
                self.assertIn(flag, result.report.activity_flags)
                self.assertFalse(result.report.activity_flags[flag])

    def test_non_proofs_preserve_report_only_limits(self):
        result = build_lightweight_general_answer_report(valid_request())

        for non_proof in REQUIRED_NON_PROOFS:
            with self.subTest(non_proof=non_proof):
                self.assertIn(non_proof, result.report.non_proofs)

    def test_wrong_request_type_is_blocked(self):
        result = build_lightweight_general_answer_report(valid_request(request_type="coding_task"))

        self.assertFalse(result.accepted)
        self.assertIn("wrong_request_type", result.report.blocked_conditions)
        self.assertEqual(result.report.outcome_classification, "general_answer_lightweight_report_only_blocked")

    def test_high_or_critical_risk_is_blocked(self):
        for risk in ("high", "critical"):
            with self.subTest(risk=risk):
                result = build_lightweight_general_answer_report(valid_request(risk_level=risk))

                self.assertFalse(result.accepted)
                self.assertIn("high_or_critical_risk", result.report.blocked_conditions)

    def test_missing_request_id_and_intent_are_missing_requirements(self):
        result = build_lightweight_general_answer_report(valid_request(request_id="", user_intent_summary=""))

        self.assertFalse(result.accepted)
        self.assertIn("request_id", result.report.missing_requirements)
        self.assertIn("user_intent_summary", result.report.missing_requirements)

    def test_external_or_executing_requirements_are_blocked(self):
        blockers = {
            "requires_file_mutation": "requires_file_mutation",
            "requires_scheduling": "requires_scheduling",
            "requires_local_documents": "requires_local_documents_or_rag",
            "requires_rag_lookup": "requires_local_documents_or_rag",
            "requires_web_lookup": "requires_web_lookup",
            "requires_external_connector": "requires_external_connector",
            "requires_provider_execution": "requires_provider_model_or_runtime_execution",
            "requires_model_execution": "requires_provider_model_or_runtime_execution",
            "requires_runtime_execution": "requires_provider_model_or_runtime_execution",
            "production_readiness": "claims_production_readiness",
        }

        for field, expected_blocker in blockers.items():
            with self.subTest(field=field):
                result = build_lightweight_general_answer_report(valid_request(**{field: True}))

                self.assertFalse(result.accepted)
                self.assertIn(expected_blocker, result.report.blocked_conditions)

    def test_module_source_does_not_import_runtime_provider_or_platform_surfaces(self):
        source = inspect.getsource(lightweight_answer_report)

        for forbidden in FORBIDDEN_IMPORTS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
