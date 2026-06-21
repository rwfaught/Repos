import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch

import main
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR
from orchestrator.run_manager import create_run, create_task_from_recommendation, load_task, save_task
from orchestrator.state import STATE_PATH, save_state
from orchestrator.task_schema import create_task


RECOMMENDATIONS_DIR = DATA_DIR / "reviewer_recommendations"


class Phase30RecommendationExecutionResultsTests(unittest.TestCase):
    def _task_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:8]}"

    def _create_task(
        self,
        run_id: str,
        task_id: str,
        role: str,
        *,
        status: str = "queued",
        source_task_id: str | None = None,
        source_artifact_id: str | None = None,
        recommendation_type: str | None = None,
        recommendation_reason: str | None = None,
    ):
        task = create_task(
            {
                "id": task_id,
                "run_id": run_id,
                "title": f"Test task {task_id}",
                "role": role,
                "status": status,
                "dependencies": [],
                "success_criteria": ["test success"],
                "files_in_scope": [],
                "retry_count": 0,
                "source_task_id": source_task_id,
                "source_artifact_id": source_artifact_id,
                "recommendation_type": recommendation_type,
                "recommendation_reason": recommendation_reason,
            }
        )
        save_task(task)
        return task

    def _count_json_files(self, path: Path) -> int:
        if not path.exists():
            return 0
        return len(list(path.glob("*.json")))

    def test_a_shows_executed_recommendation_derived_task_results(self):
        run = create_run("phase30 executed recommendation results")
        task = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_exec_results",
            source_artifact_id="artifact_exec_results",
            recommendation_type="repair_candidate",
            reason="repair reason",
        )
        task.status = "completed"
        save_task(task)

        with patch.object(
            sys,
            "argv",
            ["main.py", "recommendation-execution-results", "--run", run["id"]],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_execution_results()

        text = output.getvalue()
        self.assertIn(f"Recommendation execution results for run: {run['id']}", text)
        self.assertIn("Executed recommendation-derived tasks: 1", text)
        self.assertIn(f"Task ID: {task.id}", text)
        self.assertIn("Final Status: completed", text)
        self.assertIn("Recommendation Type: repair_candidate", text)
        self.assertIn("Source Task ID: source_exec_results", text)
        self.assertIn("Source Artifact ID: artifact_exec_results", text)

    def test_b_excludes_not_yet_executed_recommendation_tasks(self):
        run = create_run("phase30 queued recommendation excluded")
        queued_task = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_queued",
            source_artifact_id="artifact_queued",
            recommendation_type="manual_followup",
            reason="queued reason",
        )

        with patch.object(
            sys,
            "argv",
            ["main.py", "recommendation-execution-results", "--run", run["id"]],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_execution_results()

        text = output.getvalue()
        self.assertIn("Executed recommendation-derived tasks: 0", text)
        self.assertIn("No executed recommendation-derived tasks found for this run.", text)
        self.assertNotIn(queued_task.id, text)

    def test_c_no_recommendation_tasks_shows_clear_no_results_message(self):
        run = create_run("phase30 no recommendation tasks")
        self._create_task(
            run_id=run["id"],
            task_id=self._task_id("task_phase30_ordinary"),
            role="coder",
            status="completed",
        )

        with patch.object(
            sys,
            "argv",
            ["main.py", "recommendation-execution-results", "--run", run["id"]],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_execution_results()

        text = output.getvalue()
        self.assertIn("Executed recommendation-derived tasks: 0", text)
        self.assertIn("No executed recommendation-derived tasks found for this run.", text)

    def test_d_no_active_run_without_run_argument_stops_cleanly(self):
        with patch.object(sys, "argv", ["main.py", "recommendation-execution-results"]):
            with patch("main.load_state", return_value={"workspace_initialized": True, "active_run_id": None}):
                output = io.StringIO()
                with redirect_stdout(output):
                    main.print_recommendation_execution_results()

        self.assertIn("No active run. Use --run <run_id> or create/select an active run.", output.getvalue())

    def test_e_command_is_read_only(self):
        run = create_run("phase30 read-only")
        task = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_read_only",
            source_artifact_id="artifact_read_only",
            recommendation_type="repair_candidate",
            reason="read-only reason",
        )
        task.status = "execution_failed"
        save_task(task)

        save_state({"workspace_initialized": True, "active_run_id": run["id"]})
        state_before = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        task_before = json.dumps(load_task(task.id).__dict__, sort_keys=True)
        counts_before = {
            "runs": self._count_json_files(RUNS_DIR),
            "tasks": self._count_json_files(TASKS_DIR),
            "artifacts": self._count_json_files(ARTIFACTS_DIR),
            "recommendations": self._count_json_files(RECOMMENDATIONS_DIR),
        }

        with patch.object(sys, "argv", ["main.py", "recommendation-execution-results", "--run", run["id"]]):
            with redirect_stdout(io.StringIO()):
                main.print_recommendation_execution_results()

        state_after = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        task_after = json.dumps(load_task(task.id).__dict__, sort_keys=True)
        counts_after = {
            "runs": self._count_json_files(RUNS_DIR),
            "tasks": self._count_json_files(TASKS_DIR),
            "artifacts": self._count_json_files(ARTIFACTS_DIR),
            "recommendations": self._count_json_files(RECOMMENDATIONS_DIR),
        }

        self.assertEqual(state_after, state_before)
        self.assertEqual(task_after, task_before)
        self.assertEqual(counts_after, counts_before)


if __name__ == "__main__":
    unittest.main()
