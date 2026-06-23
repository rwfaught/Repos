import contextlib
import inspect
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from orchestrator import tiny_vertical_tracer_cli
from orchestrator.tiny_vertical_tracer_cli import (
    TINY_VERTICAL_TRACER_CLI_NON_PROOFS,
    TinyVerticalTracerCliResult,
    main,
    run_tiny_vertical_tracer_cli,
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

REQUIRED_FALSE_AUTHORITY_FIELDS = (
    "provider_selection_allowed",
    "provider_execution_allowed",
    "route_execution_allowed",
    "generation_allowed",
    "production_readiness",
)

REQUIRED_FALSE_ACTIVITY_FLAGS = (
    "provider_selected",
    "provider_executed",
    "model_selected",
    "model_executed",
    "generation_performed",
    "api_generate_called",
    "api_show_called",
    "api_chat_called",
    "api_tags_called",
    "runtime_executed",
    "platform_executed",
    "route_executed",
    "worker_dispatched",
    "codex_dispatched",
    "rag_lookup_performed",
    "web_lookup_performed",
    "scheduler_executed",
    "connector_executed",
    "wsl_executed",
    "openclaw_executed",
    "hermes_executed",
    "discord_executed",
    "export_performed",
    "package_performed",
    "cleanup_performed",
    "deletion_performed",
    "archive_performed",
    "production_executed",
)


class Phase176TinyVerticalTracerCliAdapterContractTests(unittest.TestCase):
    def test_module_exposes_required_names(self):
        self.assertIs(tiny_vertical_tracer_cli.TinyVerticalTracerCliResult, TinyVerticalTracerCliResult)
        self.assertIs(
            tiny_vertical_tracer_cli.TINY_VERTICAL_TRACER_CLI_NON_PROOFS,
            TINY_VERTICAL_TRACER_CLI_NON_PROOFS,
        )
        self.assertIs(tiny_vertical_tracer_cli.run_tiny_vertical_tracer_cli, run_tiny_vertical_tracer_cli)
        self.assertIs(tiny_vertical_tracer_cli.main, main)

        result = run_tiny_vertical_tracer_cli(["--help"])
        self.assertIsInstance(result, TinyVerticalTracerCliResult)
        self.assertIsInstance(result.exit_code, int)

    def test_list_fixtures_returns_safe_direct_answer_and_exit_code_zero(self):
        result = run_tiny_vertical_tracer_cli(["--list-fixtures"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.listed_fixtures, ("safe_direct_answer",))
        self.assertIn("- safe_direct_answer", result.output_text)
        self.assertFalse(result.accepted)

    def test_safe_direct_answer_renders_report_text_without_persistence(self):
        result = run_tiny_vertical_tracer_cli(["--fixture", "safe_direct_answer"])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.accepted)
        self.assertIsNone(result.written_json_path)
        self.assertIsNone(result.written_text_path)
        self.assertIn("phase=PHASE_169", result.output_text)
        self.assertIn("artifact_kind=tiny_vertical_tracer_dry_report", result.output_text)
        self.assertIn("fixture_id=safe_direct_answer", result.output_text)
        self.assertIn("recommended_route=local_first_answer", result.output_text)
        self.assertIn("provider_catalog_key=local_model_candidate", result.output_text)
        self.assertIn("model_metadata_evidence_name=qwen3.6:27b", result.output_text)
        self.assertIn(
            "route_selection_readiness=future_probe_ready_qwen36_27b_evidence_registered",
            result.output_text,
        )
        self.assertIn("readiness_status=not_ready_for_execution", result.output_text)
        self.assertIn(
            "outcome_classification=dry_vertical_flow_reviewable_not_executable",
            result.output_text,
        )
        self.assertFalse(result.activity_flags["dry_artifact_persisted"])

    def test_write_artifact_writes_json_only_into_caller_supplied_temp_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_tiny_vertical_tracer_cli(
                ["--fixture", "safe_direct_answer", "--write-artifact", "--out-dir", temp_dir]
            )
            temp_path = Path(temp_dir).resolve()
            written_path = Path(result.written_json_path).resolve()
            written_files = [path for path in temp_path.rglob("*") if path.is_file()]

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(len(written_files), 1)
            self.assertEqual(written_path, written_files[0].resolve())
            self.assertEqual(written_path.parent, temp_path)
            self.assertTrue(written_path.name.endswith(".json"))
            self.assertIn(f"written_json_path={result.written_json_path}", result.output_text)

    def test_written_json_reloads_and_contains_required_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_tiny_vertical_tracer_cli(
                ["--fixture", "safe_direct_answer", "--write-artifact", "--out-dir", temp_dir]
            )
            with open(result.written_json_path, encoding="utf-8") as handle:
                reloaded = json.load(handle)

        expected = {
            "phase": "PHASE_169",
            "artifact_kind": "tiny_vertical_tracer_dry_report",
            "fixture_id": "safe_direct_answer",
            "recommended_route": "local_first_answer",
            "provider_catalog_key": "local_model_candidate",
            "model_metadata_evidence_name": "qwen3.6:27b",
            "route_selection_readiness": "future_probe_ready_qwen36_27b_evidence_registered",
            "readiness_status": "not_ready_for_execution",
            "outcome_classification": "dry_vertical_flow_reviewable_not_executable",
            "persistence_classification": "test_dry_artifact_persistence_not_route_execution",
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(reloaded[key], value)

    def test_required_qwen36_27b_evidence_keys_are_present(self):
        result = run_tiny_vertical_tracer_cli(["--fixture", "safe_direct_answer"])

        self.assertIn(
            "phase_159_retry1_qwen36_27b_generate_marker_smoke",
            result.payload["provider_evidence_keys"],
        )
        self.assertIn(
            "phase_162_qwen36_27b_show_metadata_visibility",
            result.payload["provider_evidence_keys"],
        )

    def test_all_execution_authority_fields_remain_false(self):
        result = run_tiny_vertical_tracer_cli(["--fixture", "safe_direct_answer"])

        for field in REQUIRED_FALSE_AUTHORITY_FIELDS:
            with self.subTest(field=field):
                self.assertFalse(result.payload[field])

    def test_activity_flags_remain_false_except_written_artifact_persistence(self):
        dry_result = run_tiny_vertical_tracer_cli(["--fixture", "safe_direct_answer"])
        for flag in REQUIRED_FALSE_ACTIVITY_FLAGS:
            with self.subTest(flag=flag):
                self.assertFalse(dry_result.activity_flags[flag])
        self.assertFalse(dry_result.activity_flags["dry_artifact_persisted"])

        with tempfile.TemporaryDirectory() as temp_dir:
            written_result = run_tiny_vertical_tracer_cli(
                ["--fixture", "safe_direct_answer", "--write-artifact", "--out-dir", temp_dir]
            )

        for flag in REQUIRED_FALSE_ACTIVITY_FLAGS:
            with self.subTest(written_flag=flag):
                self.assertFalse(written_result.activity_flags[flag])
        self.assertTrue(written_result.activity_flags["dry_artifact_persisted"])

    def test_unknown_fixture_returns_nonzero_and_no_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_tiny_vertical_tracer_cli(
                ["--fixture", "not_a_fixture", "--write-artifact", "--out-dir", temp_dir]
            )
            written_files = [path for path in Path(temp_dir).rglob("*") if path.is_file()]

        self.assertNotEqual(result.exit_code, 0)
        self.assertEqual(result.fixture_id, "not_a_fixture")
        self.assertIn("Unknown tiny vertical tracer fixture", result.error_text)
        self.assertEqual(written_files, [])
        self.assertIsNone(result.written_json_path)

    def test_write_artifact_without_out_dir_returns_nonzero(self):
        result = run_tiny_vertical_tracer_cli(["--fixture", "safe_direct_answer", "--write-artifact"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("requires caller-supplied --out-dir", result.error_text)
        self.assertIsNone(result.written_json_path)

    def test_module_source_does_not_import_forbidden_runtime_or_provider_surfaces(self):
        source = inspect.getsource(tiny_vertical_tracer_cli)

        for forbidden in FORBIDDEN_IMPORTS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_module_entrypoint_works_for_safe_direct_answer(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "orchestrator.tiny_vertical_tracer_cli",
                "--fixture",
                "safe_direct_answer",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("phase=PHASE_169", completed.stdout)
        self.assertIn("fixture_id=safe_direct_answer", completed.stdout)
        self.assertIn("provider_execution_allowed=False", completed.stdout)
        self.assertIn("route_execution_allowed=False", completed.stdout)
        self.assertEqual(completed.stderr, "")

    def test_main_prints_to_stdout_without_provider_runtime_subprocess_use(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = main(["--fixture", "safe_direct_answer"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Tiny Vertical Tracer Dry Report", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
