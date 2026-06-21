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
from orchestrator.intake import (
    authorize_case_packet_creation_from_seed_review,
    judge_intake,
    review_case_packet_seed_candidate,
)
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase67CreationAuthorizationTests(unittest.TestCase):
    def _write_temp_input(self, payload: dict) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
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

    def _ready_seed_review(self) -> dict:
        intake_result = judge_intake(self._proceed_input())
        return review_case_packet_seed_candidate(intake_result)

    def test_a_ready_seed_plus_explicit_approval_is_creation_authorized_without_persistence(self):
        seed_review = self._ready_seed_review()
        result = authorize_case_packet_creation_from_seed_review(
            {
                "seed_review_result": seed_review,
                "operator_case_packet_creation_decision": "authorize_case_packet_creation",
            }
        )

        self.assertEqual(result.get("creation_authorization"), "creation_authorized")
        self.assertTrue(result.get("case_packet_creation_authorized"))
        self.assertEqual(result.get("next_action"), "operator_may_choose_explicit_case_packet_persistence_boundary")
        self.assertFalse(result.get("case_packet_created"))
        self.assertFalse(result.get("case_packet_persisted"))
        self.assertFalse(result.get("task_created"))
        self.assertFalse(result.get("planner_invoked"))
        self.assertFalse(result.get("mutation_performed"))
        self.assertFalse(result.get("execution_performed"))

    def test_b_ready_seed_without_operator_approval_needs_operator_decision(self):
        result = authorize_case_packet_creation_from_seed_review({"seed_review_result": self._ready_seed_review()})

        self.assertEqual(result.get("creation_authorization"), "needs_operator_decision")
        self.assertFalse(result.get("case_packet_creation_authorized"))
        self.assertIn("operator_case_packet_creation_decision", result.get("missing_requirements", []))
        self.assertFalse(result.get("case_packet_created"))
        self.assertFalse(result.get("task_created"))

    def test_c_non_ready_seed_review_is_blocked(self):
        seed_review = dict(self._ready_seed_review())
        seed_review["seed_review"] = "needs_operator_clarification"
        seed_review["ready_for_operator_creation_review"] = False

        result = authorize_case_packet_creation_from_seed_review(
            {
                "seed_review_result": seed_review,
                "operator_case_packet_creation_decision": "authorize_case_packet_creation",
            }
        )

        self.assertEqual(result.get("creation_authorization"), "blocked")
        self.assertFalse(result.get("case_packet_creation_authorized"))
        self.assertIn("phase66_seed_review_not_ready", result.get("blocked_conditions", []))

    def test_d_seed_review_implying_case_packet_creation_is_blocked(self):
        seed_review = dict(self._ready_seed_review())
        seed_review["case_packet_created"] = True

        result = authorize_case_packet_creation_from_seed_review(
            {
                "seed_review_result": seed_review,
                "operator_case_packet_creation_decision": "authorize_case_packet_creation",
            }
        )

        self.assertEqual(result.get("creation_authorization"), "blocked")
        self.assertIn("seed_review_implies_case_packet_creation", result.get("blocked_conditions", []))
        self.assertFalse(result.get("case_packet_creation_authorized"))

    def test_e_seed_review_implying_task_or_planner_activity_is_blocked(self):
        seed_review = dict(self._ready_seed_review())
        seed_review["task_created"] = True
        seed_review["planner_invoked"] = True

        result = authorize_case_packet_creation_from_seed_review(
            {
                "seed_review_result": seed_review,
                "operator_case_packet_creation_decision": "authorize_case_packet_creation",
            }
        )

        self.assertEqual(result.get("creation_authorization"), "blocked")
        self.assertIn("seed_review_implies_task_creation", result.get("blocked_conditions", []))
        self.assertIn("seed_review_implies_planner_invocation", result.get("blocked_conditions", []))

    def test_f_seed_review_implying_runtime_or_platform_behavior_is_blocked(self):
        seed_review = dict(self._ready_seed_review())
        seed_review["requested_behavior"] = "run model through OpenClaw bridge"

        result = authorize_case_packet_creation_from_seed_review(
            {
                "seed_review_result": seed_review,
                "operator_case_packet_creation_decision": "authorize_case_packet_creation",
            }
        )

        self.assertEqual(result.get("creation_authorization"), "blocked")
        self.assertIn("unsupported_execution_or_platform_request", result.get("blocked_conditions", []))

    def test_g_cli_creation_authorization_is_read_only_and_matches_direct_result(self):
        payload = {
            "seed_review_result": self._ready_seed_review(),
            "operator_case_packet_creation_decision": "authorize_case_packet_creation",
        }
        input_path = self._write_temp_input(payload)

        before = self._snapshot_mutation_surface()
        text = self._capture_main(["main.py", "case-packet-creation-authorize", str(input_path)])
        after = self._snapshot_mutation_surface()
        cli_payload = json.loads(text)

        self.assertEqual(cli_payload, authorize_case_packet_creation_from_seed_review(payload))
        self.assertEqual(cli_payload.get("creation_authorization"), "creation_authorized")
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
