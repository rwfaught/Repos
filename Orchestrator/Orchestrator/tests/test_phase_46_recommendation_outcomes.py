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
from orchestrator.run_manager import create_run, load_task, load_tasks_for_run, save_task
from orchestrator.state import STATE_PATH, load_state, save_state
from orchestrator.task_schema import create_task

RECOMMENDATIONS_DIR = Path("data/reviewer_recommendations")


class Phase46RecommendationOutcomesTests(unittest.TestCase):
    def _task_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:8]}"

    def _create_source_task(self, run_id: str, task_id: str, status: str = "needs_review"):
        task = create_task(
            {
                "id": task_id,
                "run_id": run_id,
                "title": f"Source task {task_id}",
                "role": "coder",
                "status": status,
                "dependencies": [],
                "success_criteria": ["source success"],
                "files_in_scope": [],
                "retry_count": 0,
                "execution_artifact_id": f"artifact_exec_{task_id}",
            }
        )
        save_task(task)
        return task

    def _create_reviewer_emitter_task(self, run_id: str, task_id: str, source_task_id: str, source_artifact_id: str):
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
                "source_task_id": source_task_id,
                "source_artifact_id": source_artifact_id,
            }
        )
        save_task(task)
        return task

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

    def test_a_shows_materialization_for_active_run(self):
        run = create_run("phase46 active run outcomes")
        source = self._create_source_task(run["id"], self._task_id("task_phase46_source_active"))
        reviewer_id = self._task_id("task_phase46_reviewer_active")
        self._create_reviewer_emitter_task(run["id"], reviewer_id, source.id, source.execution_artifact_id or "")
        self._persist_recommendation(reviewer_id, "manual_followup", "Follow-up is needed.")

        with patch.object(
            sys,
            "argv",
            ["main.py", "recommendation-create", "--reviewer-task", reviewer_id, "--run", run["id"]],
        ):
            create_output = io.StringIO()
            with redirect_stdout(create_output):
                main.create_recommendation_task()
        self.assertIn("Created task from recommendation-backed draft.", create_output.getvalue())

        created_task_ids = [
            task.id
            for task in load_tasks_for_run(run["id"])
            if task.id != reviewer_id and task.source_task_id == source.id and task.role == "reviewer"
        ]
        self.assertTrue(created_task_ids)
        created_task_id = sorted(created_task_ids)[0]

        counts_before = self._snapshot_counts()
        with patch.object(sys, "argv", ["main.py", "recommendation-outcomes"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_outcomes()
        counts_after = self._snapshot_counts()

        text = output.getvalue()
        self.assertIn(f"Recommendation outcomes for run: {run['id']}", text)
        self.assertIn("Total recommendation records: 1", text)
        self.assertIn(f"reviewer_task_id={reviewer_id}", text)
        self.assertIn("recommendation_type=manual_followup", text)
        self.assertIn("materialization_status=materialized", text)
        self.assertIn(f"created_task_id={created_task_id}", text)
        self.assertEqual(counts_after, counts_before)

    def test_b_explicit_run_scopes_outcomes(self):
        run_a = create_run("phase46 explicit run A")
        source_a = self._create_source_task(run_a["id"], self._task_id("task_phase46_source_a"))
        reviewer_a = self._task_id("task_phase46_reviewer_a")
        self._create_reviewer_emitter_task(run_a["id"], reviewer_a, source_a.id, source_a.execution_artifact_id or "")
        self._persist_recommendation(reviewer_a, "manual_followup", "A only.")

        run_b = create_run("phase46 explicit run B")
        source_b = self._create_source_task(run_b["id"], self._task_id("task_phase46_source_b"))
        reviewer_b = self._task_id("task_phase46_reviewer_b")
        self._create_reviewer_emitter_task(run_b["id"], reviewer_b, source_b.id, source_b.execution_artifact_id or "")
        self._persist_recommendation(reviewer_b, "repair_candidate", "B only.")

        with patch.object(sys, "argv", ["main.py", "recommendation-outcomes", "--run", run_a["id"]]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_outcomes()

        text = output.getvalue()
        self.assertIn(f"Recommendation outcomes for run: {run_a['id']}", text)
        self.assertIn(f"reviewer_task_id={reviewer_a}", text)
        self.assertNotIn(f"reviewer_task_id={reviewer_b}", text)
        self.assertNotIn("B only.", text)

    def test_c_no_matching_recommendations_message_and_no_mutation(self):
        run = create_run("phase46 no matching outcomes")
        counts_before = self._snapshot_counts()

        with patch.object(sys, "argv", ["main.py", "recommendation-outcomes", "--run", run["id"]]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_outcomes()

        text = output.getvalue()
        self.assertIn(f"Recommendation outcomes for run: {run['id']}", text)
        self.assertIn("No recommendation records found for this run.", text)
        self.assertEqual(self._snapshot_counts(), counts_before)

    def test_d_no_active_run_message_and_no_mutation(self):
        state = load_state()
        state["active_run_id"] = None
        save_state(state)
        state_before = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        counts_before = self._snapshot_counts()

        with patch.object(sys, "argv", ["main.py", "recommendation-outcomes"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_outcomes()

        text = output.getvalue()
        self.assertIn("No active run. Use --run <run_id> or create/select an active run.", text)
        state_after = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        self.assertEqual(state_after, state_before)
        self.assertEqual(self._snapshot_counts(), counts_before)


if __name__ == "__main__":
    unittest.main()
