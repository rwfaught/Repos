import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
from orchestrator.case_packet import CASE_PACKETS_DIR
from orchestrator.intake import assess_decomposition_handoff_admission, judge_intake
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase65IntakeAdmissionTests(unittest.TestCase):
    def _write_temp_input(self, payload: dict) -> Path:
        handle = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            encoding="utf-8",
        )
        with handle:
            json.dump(payload, handle, indent=2)
        return Path(handle.name)

    def _capture_main(self, argv: list[str]) -> str:
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                main.main()
            return output.getvalue()

    def _count_json_files(self, directory: Path) -> int:
        if not directory.exists():
            return 0
        return len(list(directory.glob("*.json")))

    def _snapshot_mutation_surface(self) -> dict[str, int | str]:
        return {
            "runs": self._count_json_files(RUNS_DIR),
            "tasks": self._count_json_files(TASKS_DIR),
            "artifacts": self._count_json_files(ARTIFACTS_DIR),
            "verifier_results": self._count_json_files(VERIFIER_RESULTS_DIR),
            "case_packets": self._count_json_files(CASE_PACKETS_DIR),
            "recommendations": self._count_json_files(DATA_DIR / "reviewer_recommendations"),
            "state_text": STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else "",
        }

    def _proceed_input(self) -> dict:
        return {
            "objective_text": "Summarize the provided release notes into a short report.",
            "provided_artifacts": ["release_notes.md"],
            "confirmed_context": {
                "required_artifacts": ["release_notes.md"],
                "source_format": "markdown",
                "output_format": "summary",
            },
            "available_capabilities": ["local_files"],
        }

    def test_a_valid_proceed_handoff_is_admissible(self):
        intake_result = judge_intake(self._proceed_input())
        admission = assess_decomposition_handoff_admission(intake_result)

        self.assertEqual(admission.get("admission"), "admissible")
        self.assertTrue(admission.get("admissible"))
        self.assertEqual(admission.get("source_outcome"), "proceed")
        self.assertEqual(admission.get("next_action"), "operator_may_choose_bounded_case_packet_seed_review")
        self.assertFalse(admission.get("mutation_performed"))
        self.assertFalse(admission.get("execution_performed"))

        summary = admission.get("handoff_summary")
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary.get("case_packet_seed_status"), "candidate_only_not_created")
        self.assertEqual(summary.get("case_packet_creation_status"), "not_created")

    def test_b_non_proceed_intake_results_are_blocked(self):
        clarify_result = judge_intake({"objective_text": ""})
        clarify_admission = assess_decomposition_handoff_admission(clarify_result)
        self.assertEqual(clarify_admission.get("admission"), "blocked")
        self.assertFalse(clarify_admission.get("admissible"))
        self.assertEqual(clarify_admission.get("source_outcome"), "clarify")

        blocked_result = judge_intake(
            {
                "objective_text": "Sync inbox items and produce a digest.",
                "provided_artifacts": [],
                "confirmed_context": {"required_connector": "gmail_connector"},
                "available_capabilities": ["local_files"],
            }
        )
        blocked_admission = assess_decomposition_handoff_admission(blocked_result)
        self.assertEqual(blocked_admission.get("admission"), "blocked")
        self.assertFalse(blocked_admission.get("admissible"))
        self.assertEqual(blocked_admission.get("source_outcome"), "blocked")

    def test_c_malformed_handoff_needs_operator_clarification(self):
        admission = assess_decomposition_handoff_admission(
            {
                "source_intake_outcome": "proceed",
                "handoff_status": "ready_for_bounded_decomposition",
                "authorized_next_action": "begin_decomposition",
            }
        )

        self.assertEqual(admission.get("admission"), "needs_operator_clarification")
        self.assertFalse(admission.get("admissible"))
        self.assertIn("objective", admission.get("reason", "").lower())

    def test_d_hidden_case_packet_creation_is_blocked(self):
        intake_result = judge_intake(self._proceed_input())
        handoff = dict(intake_result["decomposition_handoff"])
        seed = dict(handoff["case_packet_seed_candidate"])
        seed["creation_status"] = "created"
        handoff["case_packet_seed_candidate"] = seed

        admission = assess_decomposition_handoff_admission(handoff)

        self.assertEqual(admission.get("admission"), "blocked")
        self.assertFalse(admission.get("admissible"))
        self.assertIn("hidden", admission.get("reason", "").lower())

    def test_e_cli_admission_is_read_only_and_matches_direct_result(self):
        intake_result = judge_intake(self._proceed_input())
        input_path = self._write_temp_input(intake_result)

        before = self._snapshot_mutation_surface()
        text = self._capture_main(["main.py", "intake-handoff-admit", str(input_path)])
        after = self._snapshot_mutation_surface()
        cli_payload = json.loads(text)

        self.assertEqual(cli_payload, assess_decomposition_handoff_admission(intake_result))
        self.assertEqual(cli_payload.get("admission"), "admissible")
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
