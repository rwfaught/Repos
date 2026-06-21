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
from orchestrator.intake import judge_intake
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase64IntakeHandoffTests(unittest.TestCase):
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

    def test_a_proceed_result_emits_decomposition_handoff(self):
        payload = judge_intake(self._proceed_input())

        self.assertEqual(payload.get("outcome"), "proceed")
        self.assertTrue(payload.get("decomposition_permitted"))
        self.assertEqual(payload.get("next_action"), "begin_decomposition")

        handoff = payload.get("decomposition_handoff")
        self.assertIsInstance(handoff, dict)
        self.assertEqual(
            handoff.get("objective_text"),
            "Summarize the provided release notes into a short report.",
        )
        self.assertEqual(handoff.get("provided_artifacts"), ["release_notes.md"])
        self.assertEqual(
            handoff.get("confirmed_context"),
            {
                "required_artifacts": ["release_notes.md"],
                "source_format": "markdown",
                "output_format": "summary",
            },
        )
        self.assertEqual(handoff.get("handoff_status"), "ready_for_bounded_decomposition")
        self.assertEqual(handoff.get("authorized_next_action"), "begin_decomposition")
        self.assertEqual(
            handoff.get("operator_decision_required"),
            "approve_bounded_decomposition_before_case_packet_creation",
        )

        seed = handoff.get("case_packet_seed_candidate")
        self.assertIsInstance(seed, dict)
        self.assertEqual(seed.get("objective_text"), handoff.get("objective_text"))
        self.assertEqual(seed.get("provided_artifacts"), handoff.get("provided_artifacts"))
        self.assertEqual(seed.get("confirmed_context"), handoff.get("confirmed_context"))
        self.assertEqual(seed.get("seed_status"), "candidate_only_not_created")
        self.assertEqual(seed.get("creation_status"), "not_created")

    def test_b_cli_output_is_operator_legible_and_matches_direct_result(self):
        intake_input = self._proceed_input()
        input_path = self._write_temp_input(intake_input)

        direct = judge_intake(intake_input)
        text = self._capture_main(["main.py", "intake-judge", str(input_path)])
        cli_payload = json.loads(text)

        self.assertEqual(cli_payload, direct)
        self.assertIn("decomposition_handoff", cli_payload)
        self.assertIn("case_packet_seed_candidate", cli_payload["decomposition_handoff"])

    def test_c_intake_handoff_does_not_create_tasks_or_case_packets(self):
        intake_input = self._proceed_input()
        input_path = self._write_temp_input(intake_input)

        before = self._snapshot_mutation_surface()
        text = self._capture_main(["main.py", "intake-judge", str(input_path)])
        after = self._snapshot_mutation_surface()
        payload = json.loads(text)

        self.assertEqual(payload.get("outcome"), "proceed")
        self.assertIn("decomposition_handoff", payload)
        self.assertEqual(before, after)

    def test_d_clarify_and_blocked_do_not_authorize_decomposition(self):
        clarify_payload = judge_intake({"objective_text": ""})
        self.assertEqual(clarify_payload.get("outcome"), "clarify")
        self.assertFalse(clarify_payload.get("decomposition_permitted"))
        self.assertNotIn("decomposition_handoff", clarify_payload)

        blocked_payload = judge_intake(
            {
                "objective_text": "Sync inbox items and produce a digest.",
                "provided_artifacts": [],
                "confirmed_context": {"required_connector": "gmail_connector"},
                "available_capabilities": ["local_files"],
            }
        )
        self.assertEqual(blocked_payload.get("outcome"), "blocked")
        self.assertFalse(blocked_payload.get("decomposition_permitted"))
        self.assertNotIn("decomposition_handoff", blocked_payload)


if __name__ == "__main__":
    unittest.main()
