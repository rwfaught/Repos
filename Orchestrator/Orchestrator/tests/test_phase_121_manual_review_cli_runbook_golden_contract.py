from pathlib import Path
import unittest

from orchestrator.manual_review_cli import build_manual_review_cli_output


RUNBOOK_PATH = Path("docs/MANUAL_REVIEW_CLI_RUNBOOK.md")

REQUIRED_FIXTURE_IDS = (
    "ambiguous_needs_clarification",
    "platform_provider_external_boundary",
    "production_execution_blocked",
    "safe_coding_docs_only_mutation",
    "safe_coding_report_only",
    "safe_coding_source_test_mutation",
    "safe_direct_answer",
    "substrate_smuggling_blocked",
    "unknown_capability_blocked",
)

REQUIRED_COMMANDS = (
    "python -m orchestrator.manual_review_cli --list-fixtures",
    "python -m orchestrator.manual_review_cli --fixture safe_direct_answer",
    "python -m orchestrator.manual_review_cli --fixture safe_coding_report_only",
    "python -m orchestrator.manual_review_cli --fixture production_execution_blocked",
)

REQUIRED_REVIEW_SECTIONS = (
    "Assessment",
    "Accepted Facts",
    "Decision",
    "NBM",
    "Deliverable/Command",
    "RESPONSE_METADATA",
)


def _runbook_text() -> str:
    return RUNBOOK_PATH.read_text(encoding="utf-8")


class Phase121ManualReviewCliRunbookGoldenContractTests(unittest.TestCase):
    def test_runbook_file_exists(self):
        self.assertTrue(RUNBOOK_PATH.exists())

    def test_runbook_documents_all_required_fixture_ids(self):
        text = _runbook_text()

        for fixture_id in REQUIRED_FIXTURE_IDS:
            self.assertIn(fixture_id, text)

    def test_runbook_documents_all_required_commands(self):
        text = _runbook_text()

        for command in REQUIRED_COMMANDS:
            self.assertIn(command, text)

    def test_runbook_documents_required_output_sections(self):
        text = _runbook_text()

        for section in REQUIRED_REVIEW_SECTIONS:
            self.assertIn(section, text)

    def test_runbook_documents_blocked_fixture_nonzero_exit_posture(self):
        text = _runbook_text().lower()

        self.assertIn("blocked or conservative fixtures may return non-zero", text)
        self.assertIn("non-zero for blocked fixtures is not a crash", text)
        self.assertIn("conservative stop behavior", text)

    def test_runbook_documents_required_non_proofs(self):
        text = _runbook_text().lower()

        for phrase in (
            "does not mean coordinator acceptance",
            "worker dispatch",
            "route execution",
            "production readiness",
            "service/api/ui",
        ):
            self.assertIn(phrase, text)

    def test_list_fixtures_matches_documented_required_fixture_ids(self):
        result = build_manual_review_cli_output(["--list-fixtures"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.listed_fixtures, REQUIRED_FIXTURE_IDS)

    def test_safe_direct_answer_golden_output_contains_required_sections(self):
        result = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])

        self.assertEqual(result.exit_code, 0)
        for section in REQUIRED_REVIEW_SECTIONS:
            self.assertIn(section, result.output_text)

    def test_safe_coding_report_only_golden_output_contains_report_only_posture(self):
        result = build_manual_review_cli_output(["--fixture", "safe_coding_report_only"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("coding_worker_report_only", result.output_text)
        self.assertIn("worker_execution=false", result.output_text)

    def test_production_execution_blocked_golden_output_is_conservative(self):
        result = build_manual_review_cli_output(["--fixture", "production_execution_blocked"])
        combined = f"{result.output_text}\n{result.error_text}".lower()

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("production_execution_blocked", combined)
        self.assertIn("stopped conservatively", combined)

    def test_golden_contract_preserves_non_execution_non_proofs(self):
        result = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])

        for non_proof in (
            "cli_adapter_is_not_service_api_ui_productization",
            "cli_adapter_is_not_worker_execution",
            "cli_adapter_does_not_select_provider_model_runtime_platform",
            "cli_adapter_is_not_route_execution",
            "cli_adapter_is_not_production_readiness",
        ):
            self.assertIn(non_proof, result.non_proofs)
        self.assertTrue(all(flag is False for flag in result.no_activity_flags.values()))

    def test_phase_119_120_adapter_behavior_remains_compatible(self):
        list_result = build_manual_review_cli_output(["--list-fixtures"])
        direct_result = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])
        blocked_result = build_manual_review_cli_output(["--fixture", "production_execution_blocked"])

        self.assertEqual(list_result.command, "list-fixtures")
        self.assertEqual(direct_result.command, "fixture")
        self.assertEqual(blocked_result.command, "fixture")
        self.assertTrue(direct_result.accepted)
        self.assertFalse(blocked_result.accepted)


if __name__ == "__main__":
    unittest.main()
