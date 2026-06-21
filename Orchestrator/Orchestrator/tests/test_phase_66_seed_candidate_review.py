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
    assess_decomposition_handoff_admission,
    judge_intake,
    review_case_packet_seed_candidate,
)
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase66SeedCandidateReviewTests(unittest.TestCase):
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

    def test_a_valid_admissible_handoff_seed_is_ready_for_operator_creation_review(self):
        intake_result = judge_intake(self._proceed_input())
        admission = assess_decomposition_handoff_admission(intake_result)
        review = review_case_packet_seed_candidate(intake_result)

        self.assertEqual(admission.get("admission"), "admissible")
        self.assertEqual(review.get("seed_review"), "ready_for_operator_creation_review")
        self.assertTrue(review.get("ready_for_operator_creation_review"))
        self.assertEqual(review.get("source_outcome"), "proceed")
        self.assertEqual(review.get("next_action"), "operator_may_choose_explicit_case_packet_creation_boundary")
        self.assertFalse(review.get("mutation_performed"))
        self.assertFalse(review.get("execution_performed"))
        self.assertFalse(review.get("case_packet_created"))
        self.assertFalse(review.get("task_created"))
        self.assertFalse(review.get("planner_invoked"))

        summary = review.get("seed_summary")
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary.get("seed_status"), "candidate_only_not_created")
        self.assertEqual(summary.get("creation_status"), "not_created")
        self.assertEqual(summary.get("source_intake_linkage"), "judge_intake.proceed")

    def test_b_vague_seed_needs_operator_clarification(self):
        intake_result = judge_intake(self._proceed_input())
        handoff = dict(intake_result["decomposition_handoff"])
        seed = dict(handoff["case_packet_seed_candidate"])
        seed["objective_text"] = ""
        handoff["case_packet_seed_candidate"] = seed

        review = review_case_packet_seed_candidate(handoff)

        self.assertEqual(review.get("seed_review"), "needs_operator_clarification")
        self.assertFalse(review.get("ready_for_operator_creation_review"))
        self.assertIn("seed_objective_text", review.get("missing_requirements", []))
        self.assertFalse(review.get("case_packet_created"))
        self.assertFalse(review.get("task_created"))

    def test_c_hidden_case_packet_creation_is_blocked(self):
        intake_result = judge_intake(self._proceed_input())
        handoff = dict(intake_result["decomposition_handoff"])
        seed = dict(handoff["case_packet_seed_candidate"])
        seed["creation_status"] = "created"
        handoff["case_packet_seed_candidate"] = seed

        review = review_case_packet_seed_candidate(handoff)

        self.assertEqual(review.get("seed_review"), "blocked")
        self.assertFalse(review.get("ready_for_operator_creation_review"))
        self.assertIn("phase65_admission_not_admissible", review.get("blocked_conditions", []))
        self.assertFalse(review.get("case_packet_created"))
        self.assertFalse(review.get("task_created"))

    def test_d_seed_lacking_source_lineage_is_blocked(self):
        intake_result = judge_intake(self._proceed_input())
        handoff = dict(intake_result["decomposition_handoff"])
        handoff.pop("source_intake_linkage")

        admission = assess_decomposition_handoff_admission(handoff)
        review = review_case_packet_seed_candidate(handoff)

        self.assertEqual(admission.get("admission"), "admissible")
        self.assertEqual(review.get("seed_review"), "blocked")
        self.assertFalse(review.get("ready_for_operator_creation_review"))
        self.assertIn("missing_source_intake_linkage", review.get("blocked_conditions", []))
        self.assertFalse(review.get("case_packet_created"))

    def test_e_cli_seed_review_is_read_only_and_matches_direct_result(self):
        intake_result = judge_intake(self._proceed_input())
        input_path = self._write_temp_input(intake_result)

        before = self._snapshot_mutation_surface()
        text = self._capture_main(["main.py", "case-packet-seed-review", str(input_path)])
        after = self._snapshot_mutation_surface()
        cli_payload = json.loads(text)

        self.assertEqual(cli_payload, review_case_packet_seed_candidate(intake_result))
        self.assertEqual(cli_payload.get("seed_review"), "ready_for_operator_creation_review")
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
