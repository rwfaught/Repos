import contextlib
import inspect
import io
import unittest

from orchestrator import manual_review_cli
from orchestrator.manual_review_cli import (
    ManualReviewCliResult,
    build_manual_review_cli_output,
    main,
)
from orchestrator.manual_review_runner import (
    list_builtin_review_fixtures,
    run_named_fixture_review,
)


class Phase119ManualReviewCliAdapterContractTests(unittest.TestCase):
    def test_contract_exports_expected_result_builder_and_main(self):
        self.assertTrue(hasattr(manual_review_cli, "ManualReviewCliResult"))
        self.assertTrue(hasattr(manual_review_cli, "build_manual_review_cli_output"))
        self.assertTrue(hasattr(manual_review_cli, "main"))
        result = build_manual_review_cli_output(["--help"])
        self.assertIsInstance(result, ManualReviewCliResult)
        self.assertIsInstance(result.exit_code, int)

    def test_list_fixtures_returns_stable_phase_118_fixture_ids(self):
        result = build_manual_review_cli_output(["--list-fixtures"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.command, "list-fixtures")
        self.assertEqual(result.listed_fixtures, list_builtin_review_fixtures())
        self.assertIn("safe_direct_answer", result.listed_fixtures)
        self.assertIn("- safe_direct_answer", result.output_text)
        self.assertFalse(result.accepted)

    def test_safe_direct_answer_fixture_renders_review_without_execution(self):
        result = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertIn("Assessment", result.output_text)
        self.assertIn("RESPONSE_METADATA", result.output_text)
        self.assertIn("worker_execution=false", result.output_text)
        self.assertTrue(all(flag is False for flag in result.no_activity_flags.values()))

    def test_report_only_fixture_preserves_packet_posture(self):
        result = build_manual_review_cli_output(["--fixture", "safe_coding_report_only"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("coding_worker_report_only", result.output_text)
        self.assertIn("Decision", result.output_text)

    def test_docs_only_mutation_fixture_preserves_allowed_docs_scope(self):
        result = build_manual_review_cli_output(["--fixture", "safe_coding_docs_only_mutation"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("coding_worker_docs_only_mutation", result.output_text)
        self.assertIn("docs/PHASE_118.md", result.output_text)
        self.assertTrue(all(flag is False for flag in result.no_activity_flags.values()))

    def test_unknown_fixture_fails_conservatively_without_execution(self):
        result = build_manual_review_cli_output(["--fixture", "not_a_fixture"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse(result.accepted)
        self.assertEqual(result.fixture_id, "not_a_fixture")
        self.assertIn("unknown fixture id", result.output_text)
        self.assertIn("stopped conservatively", result.error_text)
        self.assertTrue(all(flag is False for flag in result.no_activity_flags.values()))

    def test_empty_args_and_help_are_deterministic_and_do_not_run_fixture(self):
        empty_result = build_manual_review_cli_output([])
        help_result = build_manual_review_cli_output(["--help"])

        for result in (empty_result, help_result):
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.command, "help")
            self.assertEqual(result.fixture_id, "")
            self.assertEqual(result.listed_fixtures, ())
            self.assertIn("--list-fixtures", result.output_text)
            self.assertNotIn("Assessment", result.output_text)

    def test_fixture_output_contains_required_review_sections(self):
        result = build_manual_review_cli_output(["--fixture", "safe_coding_source_test_mutation"])

        for expected in (
            "Assessment",
            "Accepted Facts",
            "Decision",
            "NBM",
            "Deliverable",
            "RESPONSE_METADATA",
        ):
            self.assertIn(expected, result.output_text)

    def test_preserves_adapter_non_proofs_and_no_activity_flags(self):
        result = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])

        self.assertIn("cli_adapter_is_not_service_api_ui_productization", result.non_proofs)
        self.assertIn("cli_adapter_is_not_route_execution", result.non_proofs)
        self.assertIn("cli_adapter_does_not_select_provider_model_runtime_platform", result.non_proofs)
        self.assertIn("runner_is_not_route_execution", result.non_proofs)
        self.assertTrue(all(flag is False for flag in result.no_activity_flags.values()))

    def test_adapter_does_not_add_substrate_or_provider_selection_text(self):
        result = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])
        rendered = result.output_text.lower()

        for forbidden in (
            "selected_provider",
            "selected_model",
            "selected_runtime",
            "selected_substrate",
            "dispatch_worker=true",
            "route_execution=true",
        ):
            self.assertNotIn(forbidden, rendered)

    def test_builder_does_not_mutate_input_argv(self):
        argv = ["--fixture", "safe_direct_answer"]
        before = list(argv)

        build_manual_review_cli_output(argv)

        self.assertEqual(argv, before)

    def test_main_returns_int_for_supported_commands(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exit_code = main(["--list-fixtures"])

        self.assertIsInstance(exit_code, int)
        self.assertEqual(exit_code, 0)
        self.assertIn("safe_direct_answer", buffer.getvalue())

    def test_adapter_uses_only_allowed_import_domains(self):
        source = inspect.getsource(manual_review_cli)

        for forbidden in (
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
        ):
            self.assertNotIn(forbidden, source)

    def test_fixture_rendering_matches_phase_118_runner_report_text(self):
        fixture_id = "safe_coding_report_only"

        adapter_result = build_manual_review_cli_output(["--fixture", fixture_id])
        runner_result = run_named_fixture_review(fixture_id)

        self.assertEqual(adapter_result.output_text, runner_result.review_text)
        self.assertEqual(adapter_result.accepted, runner_result.accepted)


if __name__ == "__main__":
    unittest.main()
