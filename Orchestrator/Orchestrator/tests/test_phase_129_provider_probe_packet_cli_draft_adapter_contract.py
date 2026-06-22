import unittest

from orchestrator.manual_review_cli import build_manual_review_cli_output


FORBIDDEN_EXECUTION_CLAIMS = (
    "provider_executed=true",
    "model_executed=true",
    "runtime_executed=true",
    "platform_executed=true",
    "worker_dispatched=true",
    "codex_dispatched=true",
    "rag_lookup_performed=true",
    "web_lookup_performed=true",
    "scheduler_executed=true",
    "connector_executed=true",
    "route_executed=true",
    "production_readiness=true",
)

FULL_PROBE_ARGS = [
    "--fixture",
    "safe_direct_answer",
    "--draft-provider-probe-packet",
    "--authorize-probe-boundary",
    "--probe-kind",
    "read_only_future_probe_plan",
    "--probe-surface",
    "provider_runtime_surface",
    "--probe-scope",
    "read_only_probe_command_draft",
    "--expected-evidence",
    "captured_future_probe_output",
]


class Phase129ProviderProbePacketCliDraftAdapterContractTests(unittest.TestCase):
    def assert_no_forbidden_execution_claims(self, text: str):
        rendered = text.lower()
        for forbidden in FORBIDDEN_EXECUTION_CLAIMS:
            self.assertNotIn(forbidden, rendered)

    def test_existing_safe_direct_answer_fixture_still_renders_default_probe_status(self):
        result = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Router Policy", result.output_text)
        self.assertIn("Provider Probe Packet", result.output_text)
        self.assertIn("accepted=False", result.output_text)
        self.assertIn("operator_authorized_probe_boundary", result.output_text)
        self.assertIn("allowed_probe_scope", result.output_text)
        self.assertIn("expected_evidence", result.output_text)
        self.assert_no_forbidden_execution_claims(result.output_text)

    def test_draft_probe_packet_without_authorization_remains_blocked(self):
        result = build_manual_review_cli_output(
            [
                "--fixture",
                "safe_direct_answer",
                "--draft-provider-probe-packet",
                "--probe-kind",
                "read_only_future_probe_plan",
                "--probe-surface",
                "provider_runtime_surface",
                "--probe-scope",
                "read_only_probe_command_draft",
                "--expected-evidence",
                "captured_future_probe_output",
            ]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("accepted=False", result.output_text)
        self.assertIn("operator_authorized_probe_boundary", result.output_text)
        self.assertIn("probe_packet_missing_required_authority_or_scope", result.output_text)
        self.assert_no_forbidden_execution_claims(result.output_text)

    def test_authorized_probe_packet_without_scope_or_evidence_remains_blocked(self):
        result = build_manual_review_cli_output(
            [
                "--fixture",
                "safe_direct_answer",
                "--draft-provider-probe-packet",
                "--authorize-probe-boundary",
                "--probe-kind",
                "read_only_future_probe_plan",
                "--probe-surface",
                "provider_runtime_surface",
            ]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("accepted=False", result.output_text)
        self.assertIn("allowed_probe_scope", result.output_text)
        self.assertIn("expected_evidence", result.output_text)
        self.assert_no_forbidden_execution_claims(result.output_text)

    def test_full_explicit_probe_packet_command_drafts_paperwork_only(self):
        result = build_manual_review_cli_output(FULL_PROBE_ARGS)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Provider Probe Packet", result.output_text)
        self.assertIn("accepted=True", result.output_text)
        self.assertIn("provider_catalog_key=local_model_candidate", result.output_text)
        self.assertIn("provider_allowed_boundary=future_local_provider_model_probe_boundary", result.output_text)
        self.assertIn("coordinator_acceptance_required=True", result.output_text)
        self.assertTrue(all(flag is False for flag in result.no_activity_flags.values()))
        self.assert_no_forbidden_execution_claims(result.output_text)

    def test_coding_worker_fixture_with_probe_packet_flags_does_not_dispatch(self):
        args = list(FULL_PROBE_ARGS)
        args[1] = "safe_coding_source_test_mutation"
        result = build_manual_review_cli_output(args)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("provider_catalog_key=worker_codex_boundary", result.output_text)
        self.assertIn("worker_execution=false", result.output_text)
        self.assertTrue(all(flag is False for flag in result.no_activity_flags.values()))
        self.assert_no_forbidden_execution_claims(result.output_text)

    def test_block_and_clarification_fixtures_do_not_draft_accepted_probe_packets(self):
        for fixture_id in ("production_execution_blocked", "ambiguous_needs_clarification"):
            with self.subTest(fixture_id=fixture_id):
                args = list(FULL_PROBE_ARGS)
                args[1] = fixture_id
                result = build_manual_review_cli_output(args)

                self.assertNotEqual(result.exit_code, 0)
                self.assertIn("Provider Probe Packet", result.output_text)
                self.assertIn("accepted=False", result.output_text)
                self.assertIn("router_recommendation_not_probe_eligible", result.output_text)
                self.assert_no_forbidden_execution_claims(result.output_text)

    def test_help_text_documents_probe_packet_paperwork_only(self):
        result = build_manual_review_cli_output(["--help"])
        text = result.output_text.lower()

        self.assertEqual(result.exit_code, 0)
        self.assertIn("--draft-provider-probe-packet", result.output_text)
        self.assertIn("provider probe packet drafting is paperwork only", text)
        self.assertIn("no probe, provider, model, runtime", text)


if __name__ == "__main__":
    unittest.main()
