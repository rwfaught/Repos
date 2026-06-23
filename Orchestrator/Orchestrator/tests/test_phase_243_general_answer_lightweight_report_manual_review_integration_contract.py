import unittest

from orchestrator.manual_review_runner import run_named_fixture_review


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
    "not_codex_dispatch",
    "not_production_readiness",
)


class Phase243GeneralAnswerLightweightReportManualReviewIntegrationTests(unittest.TestCase):
    def test_safe_direct_answer_includes_phase_235_lightweight_report_payload(self):
        result = run_named_fixture_review("safe_direct_answer")

        self.assertTrue(result.accepted)
        self.assertIsNotNone(result.lightweight_answer_report_payload)
        payload = result.lightweight_answer_report_payload
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["phase"], "PHASE_235")
        self.assertEqual(payload["artifact_kind"], "general_answer_lightweight_report_only_contract")
        self.assertEqual(payload["request_type"], "general_answer")
        self.assertFalse(payload["production_readiness"])

    def test_safe_direct_answer_rendered_text_includes_lightweight_report_section(self):
        result = run_named_fixture_review("safe_direct_answer")

        self.assertIn("Assessment", result.review_text)
        self.assertIn("Router Policy", result.review_text)
        self.assertIn("Lightweight General Answer Report", result.review_text)
        self.assertIn("- phase=PHASE_235", result.review_text)
        self.assertIn("- artifact_kind=general_answer_lightweight_report_only_contract", result.review_text)

    def test_lightweight_report_activity_flags_remain_false(self):
        result = run_named_fixture_review("safe_direct_answer")
        payload = result.lightweight_answer_report_payload

        for flag in REQUIRED_FALSE_ACTIVITY_FLAGS:
            with self.subTest(flag=flag):
                self.assertIn(flag, payload["activity_flags"])
                self.assertFalse(payload["activity_flags"][flag])
        for flag in ("provider_executed", "model_executed", "worker_dispatched", "codex_dispatched"):
            self.assertFalse(result.no_activity_flags[flag])

    def test_lightweight_report_non_proofs_are_preserved_in_payload_and_runner_result(self):
        result = run_named_fixture_review("safe_direct_answer")
        payload = result.lightweight_answer_report_payload

        for non_proof in REQUIRED_NON_PROOFS:
            with self.subTest(non_proof=non_proof):
                self.assertIn(non_proof, payload["non_proofs"])
                self.assertIn(non_proof, result.non_proofs)

    def test_coding_fixture_does_not_receive_accepted_lightweight_answer_report(self):
        result = run_named_fixture_review("safe_coding_source_test_mutation")

        self.assertTrue(result.accepted)
        self.assertEqual(result.request_type, "coding_task")
        self.assertIsNone(result.lightweight_answer_report_payload)
        self.assertNotIn("Lightweight General Answer Report", result.review_text)

    def test_blocked_direct_answer_like_fixture_does_not_smuggle_lightweight_acceptance(self):
        result = run_named_fixture_review("ambiguous_needs_clarification")

        self.assertFalse(result.accepted)
        self.assertIsNone(result.lightweight_answer_report_payload)
        self.assertNotIn("Lightweight General Answer Report", result.review_text)


if __name__ == "__main__":
    unittest.main()
