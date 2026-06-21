import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import main
from orchestrator import engine
from orchestrator.paths import ARTIFACTS_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.run_manager import create_run, load_task, save_task
from orchestrator.state import STATE_PATH, load_state, save_state
from orchestrator.task_schema import create_task

RECOMMENDATIONS_DIR = Path("data/reviewer_recommendations")


class Phase43RecommendationActionsTests(unittest.TestCase):
    def _task_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:8]}"

    def _create_reviewer_emitter_task(self, run_id: str, task_id: str) -> None:
        task = create_task(
            {
                "id": task_id,
                "run_id": run_id,
                "title": f"Reviewer task {task_id}",
                "role": "reviewer",
                "status": "queued",
                "dependencies": [],
                "success_criteria": ["return recommendation json"],
                "files_in_scope": [],
                "retry_count": 0,
                "source_task_id": f"source_{task_id}",
                "source_artifact_id": f"artifact_{task_id}",
            }
        )
        save_task(task)

    def _persist_recommendation(self, task_id: str, recommendation_type: str, reason: str) -> None:
        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": json.dumps(
                    {
                        "recommendation_type": recommendation_type,
                        "reason": reason,
                    }
                ),
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(task_id), provider_name="mock")

    def _count_json_files(self, directory: Path) -> int:
        if not directory.exists():
            return 0
        return len(list(directory.glob("*.json")))

    def _snapshot_counts(self) -> dict[str, int]:
        return {
            "runs": self._count_json_files(RUNS_DIR),
            "tasks": self._count_json_files(TASKS_DIR),
            "artifacts": self._count_json_files(ARTIFACTS_DIR),
            "verifier_results": self._count_json_files(VERIFIER_RESULTS_DIR),
            "recommendations": self._count_json_files(RECOMMENDATIONS_DIR),
        }

    def test_a_shows_candidate_actions_for_active_run(self):
        run = create_run("phase43 active run actions")
        task_accept = self._task_id("task_phase43_accept")
        task_followup = self._task_id("task_phase43_followup")
        task_repair = self._task_id("task_phase43_repair")

        self._create_reviewer_emitter_task(run["id"], task_accept)
        self._create_reviewer_emitter_task(run["id"], task_followup)
        self._create_reviewer_emitter_task(run["id"], task_repair)

        self._persist_recommendation(task_accept, "accept_result", "Result looks good.")
        self._persist_recommendation(task_followup, "manual_followup", "Needs manual validation.")
        self._persist_recommendation(task_repair, "repair_candidate", "Patch is required.")

        counts_before = self._snapshot_counts()
        with patch.object(sys, "argv", ["main.py", "recommendation-actions"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_actions()
        counts_after = self._snapshot_counts()

        text = output.getvalue()
        self.assertIn(f"Recommendation actions for run: {run['id']}", text)
        self.assertIn("Total recommendation records: 3", text)
        self.assertIn("accept_result (1):", text)
        self.assertIn("manual_followup (1):", text)
        self.assertIn("repair_candidate (1):", text)
        self.assertIn(f"reviewer_task_id={task_accept}", text)
        self.assertIn("candidate_action=Result may be accepted; no immediate follow-up action required.", text)
        self.assertIn(f"reviewer_task_id={task_followup}", text)
        self.assertIn("candidate_action=Follow-up review task could be created explicitly.", text)
        self.assertIn(f"reviewer_task_id={task_repair}", text)
        self.assertIn("candidate_action=Repair task could be created explicitly.", text)
        self.assertEqual(counts_after, counts_before)

    def test_b_explicit_run_scopes_actions(self):
        run_a = create_run("phase43 explicit run A")
        task_a = self._task_id("task_phase43_run_a")
        self._create_reviewer_emitter_task(run_a["id"], task_a)
        self._persist_recommendation(task_a, "manual_followup", "A only.")

        run_b = create_run("phase43 explicit run B")
        task_b = self._task_id("task_phase43_run_b")
        self._create_reviewer_emitter_task(run_b["id"], task_b)
        self._persist_recommendation(task_b, "repair_candidate", "B only.")

        with patch.object(sys, "argv", ["main.py", "recommendation-actions", "--run", run_a["id"]]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_actions()

        text = output.getvalue()
        self.assertIn(f"Recommendation actions for run: {run_a['id']}", text)
        self.assertIn(f"reviewer_task_id={task_a}", text)
        self.assertNotIn(f"reviewer_task_id={task_b}", text)
        self.assertNotIn("B only.", text)

    def test_c_no_matching_recommendations_message_and_no_mutation(self):
        run = create_run("phase43 no matching")
        counts_before = self._snapshot_counts()

        with patch.object(sys, "argv", ["main.py", "recommendation-actions", "--run", run["id"]]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_actions()

        self.assertIn(f"Recommendation actions for run: {run['id']}", output.getvalue())
        self.assertIn("No recommendation records found for this run.", output.getvalue())
        self.assertEqual(self._snapshot_counts(), counts_before)

    def test_d_no_active_run_message_and_no_mutation(self):
        state = load_state()
        state["active_run_id"] = None
        save_state(state)
        state_before = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        counts_before = self._snapshot_counts()

        with patch.object(sys, "argv", ["main.py", "recommendation-actions"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_actions()

        self.assertIn("No active run. Use --run <run_id> or create/select an active run.", output.getvalue())
        state_after = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        self.assertEqual(state_before, state_after)
        self.assertEqual(counts_before, self._snapshot_counts())


if __name__ == "__main__":
    unittest.main()
