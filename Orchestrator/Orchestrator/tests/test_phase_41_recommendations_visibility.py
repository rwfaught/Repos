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


class Phase41RecommendationVisibilityTests(unittest.TestCase):
    def _task_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:8]}"

    def _create_reviewer_emitter_task(self, run_id: str, task_id: str):
        task = create_task(
            {
                "id": task_id,
                "run_id": run_id,
                "title": f"Reviewer task {task_id}",
                "role": "reviewer",
                "status": "queued",
                "dependencies": [],
                "success_criteria": ["return a recommendation"],
                "files_in_scope": [],
                "retry_count": 0,
                "source_task_id": f"source_{task_id}",
                "source_artifact_id": f"artifact_{task_id}",
            }
        )
        save_task(task)
        return task

    def _persist_recommendation_for_task(
        self,
        task_id: str,
        recommendation_type: str = "manual_followup",
        reason: str = "Needs manual follow-up.",
    ) -> None:
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

    def test_a_shows_recommendations_for_active_run(self):
        run = create_run("phase41 active run recommendations")
        reviewer_task_id = self._task_id("task_phase41_active")
        self._create_reviewer_emitter_task(run["id"], reviewer_task_id)
        self._persist_recommendation_for_task(
            reviewer_task_id,
            recommendation_type="manual_followup",
            reason="Active run recommendation.",
        )

        with patch.object(sys, "argv", ["main.py", "recommendations"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendations()

        text = output.getvalue()
        self.assertIn(f"Reviewer recommendations for run: {run['id']}", text)
        self.assertIn("Count: 1", text)
        self.assertIn(f"Reviewer Task: {reviewer_task_id}", text)
        self.assertIn("Run ID:", text)
        self.assertIn("Type: manual_followup", text)
        self.assertIn("Reason: Active run recommendation.", text)
        self.assertIn("Timestamp:", text)

    def test_b_scopes_recommendations_for_explicit_run(self):
        run_a = create_run("phase41 explicit run A")
        task_a = self._task_id("task_phase41_explicit_a")
        self._create_reviewer_emitter_task(run_a["id"], task_a)
        self._persist_recommendation_for_task(task_a, reason="Recommendation for run A.")

        run_b = create_run("phase41 explicit run B")
        task_b = self._task_id("task_phase41_explicit_b")
        self._create_reviewer_emitter_task(run_b["id"], task_b)
        self._persist_recommendation_for_task(task_b, reason="Recommendation for run B.")

        with patch.object(sys, "argv", ["main.py", "recommendations", "--run", run_a["id"]]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendations()

        text = output.getvalue()
        self.assertIn(f"Reviewer recommendations for run: {run_a['id']}", text)
        self.assertIn(f"Reviewer Task: {task_a}", text)
        self.assertNotIn(f"Reviewer Task: {task_b}", text)
        self.assertNotIn(run_b["id"], text)

    def test_c_no_matching_recommendations_prints_clear_message_and_no_mutation(self):
        run = create_run("phase41 no matching recommendations")
        before_counts = self._snapshot_counts()

        with patch.object(sys, "argv", ["main.py", "recommendations", "--run", run["id"]]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendations()

        self.assertIn(f"Reviewer recommendations for run: {run['id']}", output.getvalue())
        self.assertIn("No recommendation records found for this run.", output.getvalue())
        self.assertEqual(self._snapshot_counts(), before_counts)

    def test_d_no_active_run_prints_clear_message_and_no_mutation(self):
        state = load_state()
        state["active_run_id"] = None
        save_state(state)
        state_before = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        before_counts = self._snapshot_counts()

        with patch.object(sys, "argv", ["main.py", "recommendations"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendations()

        self.assertIn("No active run. Use --run <run_id> or create/select an active run.", output.getvalue())
        state_after = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        self.assertEqual(state_after, state_before)
        self.assertEqual(self._snapshot_counts(), before_counts)


if __name__ == "__main__":
    unittest.main()
