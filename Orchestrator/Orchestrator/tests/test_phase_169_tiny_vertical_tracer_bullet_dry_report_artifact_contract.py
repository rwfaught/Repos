import inspect
import json
import tempfile
import unittest

from orchestrator import tiny_vertical_tracer
from orchestrator.tiny_vertical_tracer import (
    TinyVerticalTracerDryReport,
    TinyVerticalTracerDryReportResult,
    build_tiny_vertical_tracer_dry_report,
    render_tiny_vertical_tracer_dry_report_text,
    tiny_vertical_tracer_dry_report_to_dict,
    write_tiny_vertical_tracer_dry_report,
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


class Phase169TinyVerticalTracerBulletDryReportArtifactContractTests(unittest.TestCase):
    def test_module_exposes_required_contract_names(self):
        self.assertIs(tiny_vertical_tracer.TinyVerticalTracerDryReport, TinyVerticalTracerDryReport)
        self.assertIs(tiny_vertical_tracer.TinyVerticalTracerDryReportResult, TinyVerticalTracerDryReportResult)
        self.assertIs(tiny_vertical_tracer.build_tiny_vertical_tracer_dry_report, build_tiny_vertical_tracer_dry_report)
        self.assertIs(
            tiny_vertical_tracer.tiny_vertical_tracer_dry_report_to_dict,
            tiny_vertical_tracer_dry_report_to_dict,
        )
        self.assertIs(
            tiny_vertical_tracer.render_tiny_vertical_tracer_dry_report_text,
            render_tiny_vertical_tracer_dry_report_text,
        )
        self.assertIs(tiny_vertical_tracer.write_tiny_vertical_tracer_dry_report, write_tiny_vertical_tracer_dry_report)

    def test_building_safe_direct_answer_dry_tracer_succeeds(self):
        result = build_tiny_vertical_tracer_dry_report("safe_direct_answer")

        self.assertTrue(result.accepted)
        self.assertEqual(result.report.phase, "PHASE_169")
        self.assertEqual(result.report.artifact_kind, "tiny_vertical_tracer_dry_report")
        self.assertEqual(result.report.fixture_id, "safe_direct_answer")
        self.assertEqual(result.report.outcome_classification, "dry_vertical_flow_reviewable_not_executable")
        self.assertEqual(result.payload["phase"], "PHASE_169")

    def test_report_includes_full_vertical_sequence(self):
        report = build_tiny_vertical_tracer_dry_report().report

        for expected in (
            "fixture/intake/manual review",
            "route recommendation",
            "provider evidence envelope",
            "route-selection readiness",
            "coordinator review report",
            "persisted/reviewable dry artifact",
            "outcome classification",
        ):
            self.assertIn(expected, report.vertical_sequence)

        self.assertEqual(report.pipeline_stage, "boundary_packet_draft_created")
        self.assertEqual(report.route_admission, "accepted")
        self.assertEqual(report.recommended_route, "local_first_answer")
        self.assertTrue(report.coordinator_review_report_id.startswith("review_"))

    def test_report_carries_qwen36_27b_evidence_keys(self):
        report = build_tiny_vertical_tracer_dry_report().report

        self.assertIn("phase_159_retry1_qwen36_27b_generate_marker_smoke", report.provider_evidence_keys)
        self.assertIn("phase_162_qwen36_27b_show_metadata_visibility", report.provider_evidence_keys)
        self.assertIn("PHASE_159_RETRY_1_OPERATOR_PROOF", report.provider_evidence_source_phases)
        self.assertIn("PHASE_162_OPERATOR_PROOF", report.provider_evidence_source_phases)

    def test_report_carries_expected_provider_and_readiness_posture(self):
        report = build_tiny_vertical_tracer_dry_report().report

        self.assertEqual(report.provider_catalog_key, "local_model_candidate")
        self.assertEqual(report.model_metadata_evidence_name, "qwen3.6:27b")
        self.assertEqual(report.route_selection_readiness, "future_probe_ready_qwen36_27b_evidence_registered")
        self.assertEqual(report.readiness_status, "not_ready_for_execution")
        self.assertEqual(
            report.next_required_boundary,
            "future_bounded_route_selection_readiness_recommendation_envelope_review",
        )
        self.assertEqual(report.next_required_proof, "bounded_route_selection_readiness_recommendation_envelope_review")

    def test_all_execution_authority_remains_false(self):
        report = build_tiny_vertical_tracer_dry_report().report

        self.assertFalse(report.provider_selection_allowed)
        self.assertFalse(report.provider_execution_allowed)
        self.assertFalse(report.route_execution_allowed)
        self.assertFalse(report.generation_allowed)
        self.assertFalse(report.production_readiness)
        for flag in (
            "provider_selected",
            "provider_executed",
            "model_selected",
            "model_executed",
            "runtime_executed",
            "route_executed",
            "worker_dispatched",
            "production_executed",
        ):
            with self.subTest(flag=flag):
                self.assertFalse(report.activity_flags[flag])

    def test_rendered_text_includes_required_review_sections(self):
        rendered = build_tiny_vertical_tracer_dry_report().rendered_text

        for expected in ("Assessment", "Accepted Facts", "Decision", "NBM", "Deliverable/Command", "RESPONSE_METADATA"):
            self.assertIn(expected, rendered)
        self.assertIn("Tiny Vertical Tracer Dry Report", rendered)
        self.assertIn("outcome_classification=dry_vertical_flow_reviewable_not_executable", rendered)

    def test_persistence_helper_writes_json_to_temp_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = write_tiny_vertical_tracer_dry_report(temp_dir)

            self.assertIsNotNone(result.written_path)
            with open(result.written_path, encoding="utf-8") as handle:
                reloaded = json.load(handle)

        self.assertEqual(reloaded["phase"], "PHASE_169")
        self.assertEqual(reloaded["artifact_kind"], "tiny_vertical_tracer_dry_report")
        self.assertEqual(reloaded["fixture_id"], "safe_direct_answer")
        self.assertEqual(reloaded["request_id"], result.report.request_id)
        self.assertEqual(reloaded["provider_catalog_key"], "local_model_candidate")
        self.assertEqual(reloaded["model_metadata_evidence_name"], "qwen3.6:27b")
        self.assertEqual(reloaded["persistence_classification"], "test_dry_artifact_persistence_not_route_execution")
        self.assertTrue(reloaded["activity_flags"]["dry_artifact_persisted"])
        self.assertFalse(reloaded["activity_flags"]["route_executed"])
        self.assertFalse(reloaded["activity_flags"]["production_executed"])

    def test_module_does_not_import_forbidden_execution_runtime_provider_platform_surfaces(self):
        source = inspect.getsource(tiny_vertical_tracer)

        for forbidden in FORBIDDEN_IMPORTS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
