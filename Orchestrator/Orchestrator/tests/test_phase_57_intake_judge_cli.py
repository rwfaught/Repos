import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import main
from orchestrator.intake import judge_intake
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase57IntakeJudgeCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_dir = DATA_DIR / "phase57_intake_inputs"
        self.fixture_dir.mkdir(parents=True, exist_ok=True)

    def _input_path(self, prefix: str) -> Path:
        return self.fixture_dir / f"{prefix}_{uuid4().hex[:8]}.json"

    def _write_input(self, prefix: str, payload: dict) -> Path:
        path = self._input_path(prefix)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

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
            "recommendations": self._count_json_files(DATA_DIR / "reviewer_recommendations"),
            "state_text": STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else "",
        }

    def test_a_proceed_through_local_control_surface(self):
        intake_input = {
            "objective_text": "Summarize the provided release notes into a short report.",
            "provided_artifacts": ["release_notes.md"],
            "confirmed_context": {
                "required_artifacts": ["release_notes.md"],
                "source_format": "markdown",
                "output_format": "summary",
            },
            "available_capabilities": ["local_files"],
        }
        input_path = self._write_input("proceed", intake_input)

        text = self._capture_main(["main.py", "intake-judge", str(input_path)])
        payload = json.loads(text)

        self.assertEqual(payload.get("outcome"), "proceed")
        self.assertTrue(payload.get("decomposition_permitted"))
        self.assertEqual(payload.get("next_action"), "begin_decomposition")

    def test_b_clarify_through_local_control_surface(self):
        intake_input = {
            "objective_text": "Generate a report from my source data.",
            "provided_artifacts": ["input_export.csv"],
            "confirmed_context": {
                "required_artifacts": ["input_export.csv"],
                "requires_output_format": True,
            },
            "available_capabilities": ["local_files"],
        }
        input_path = self._write_input("clarify", intake_input)

        text = self._capture_main(["main.py", "intake-judge", str(input_path)])
        payload = json.loads(text)

        self.assertEqual(payload.get("outcome"), "clarify")
        self.assertFalse(payload.get("decomposition_permitted"))
        self.assertTrue(payload.get("clarification_request"))

    def test_c_blocked_through_local_control_surface(self):
        intake_input = {
            "objective_text": "Sync inbox items and produce a digest.",
            "provided_artifacts": [],
            "confirmed_context": {
                "required_connector": "gmail_connector",
            },
            "available_capabilities": ["local_files"],
        }
        input_path = self._write_input("blocked", intake_input)

        text = self._capture_main(["main.py", "intake-judge", str(input_path)])
        payload = json.loads(text)

        self.assertEqual(payload.get("outcome"), "blocked")
        self.assertFalse(payload.get("decomposition_permitted"))
        self.assertTrue(payload.get("blocked_reason"))

    def test_d_no_hidden_state_mutation(self):
        intake_input = {
            "objective_text": "Generate a report from my source data.",
            "provided_artifacts": ["input_export.csv"],
            "confirmed_context": {
                "required_artifacts": ["input_export.csv"],
                "requires_output_format": True,
            },
            "available_capabilities": ["local_files"],
        }
        input_path = self._write_input("no_mutation", intake_input)

        before = self._snapshot_mutation_surface()
        _ = self._capture_main(["main.py", "intake-judge", str(input_path)])
        after = self._snapshot_mutation_surface()

        self.assertEqual(before, after)

    def test_e_service_control_surface_semantic_parity(self):
        intake_input = {
            "objective_text": "Pull activity from Slack and summarize unresolved threads.",
            "provided_artifacts": [],
            "confirmed_context": {
                "required_connector": "slack_connector",
            },
            "available_capabilities": ["local_files"],
        }
        input_path = self._write_input("parity", intake_input)

        direct = judge_intake(intake_input)
        text = self._capture_main(["main.py", "intake-judge", str(input_path)])
        cli_payload = json.loads(text)

        self.assertEqual(cli_payload, direct)


if __name__ == "__main__":
    unittest.main()
