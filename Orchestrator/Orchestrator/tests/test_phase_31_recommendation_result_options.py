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


class Phase31RecommendationResultOptionsTests(unittest.TestCase):
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

    def test_a_run_scope_shows_post_execution_result_with_options(self):
        run = create_run("phase31 result options run scope")
        task = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_phase31_completed",
            source_artifact_id="artifact_phase31_completed",
            recommendation_type="repair_candidate",
            reason="phase31 reason",
        )
        task.status = "completed"
        save_task(task)

        with patch.object(sys, "argv", ["main.py", "recommendation-result-options", "--run", run["id"]]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_result_options()

        text = output.getvalue()
        self.assertIn(f"Recommendation result options (Run: {run['id']})", text)
        self.assertIn("Post-execution recommendation-derived results: 1", text)
        self.assertIn(f"Task ID: {task.id}", text)
        self.assertIn("Final Status: completed", text)
        self.assertIn("Operator Response Options:", text)
        self.assertIn("- No immediate follow-up required.", text)
        self.assertIn("- Review result if desired.", text)

    def test_b_unexecuted_recommendation_tasks_are_excluded(self):
        run = create_run("phase31 queued exclusion")
        queued_task = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_phase31_queued",
            source_artifact_id="artifact_phase31_queued",
            recommendation_type="manual_followup",
            reason="queued option reason",
        )

        with patch.object(sys, "argv", ["main.py", "recommendation-result-options", "--run", run["id"]]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_result_options()

        text = output.getvalue()
        self.assertIn("Post-execution recommendation-derived results: 0", text)
        self.assertIn("No post-execution recommendation-derived results found for this scope.", text)
        self.assertNotIn(queued_task.id, text)

    def test_c_distinct_statuses_map_to_distinct_option_sets(self):
        run = create_run("phase31 status mapping")

        completed_task = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_phase31_completed_map",
            source_artifact_id="artifact_phase31_completed_map",
            recommendation_type="repair_candidate",
            reason="status map completed",
        )
        completed_task.status = "completed"
        save_task(completed_task)

        failed_task = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_phase31_failed_map",
            source_artifact_id="artifact_phase31_failed_map",
            recommendation_type="manual_followup",
            reason="status map failed",
        )
        failed_task.status = "verification_failed"
        save_task(failed_task)

        needs_review_task = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_phase31_needs_review_map",
            source_artifact_id="artifact_phase31_needs_review_map",
            recommendation_type="manual_followup",
            reason="status map needs review",
        )
        needs_review_task.status = "needs_review"
        save_task(needs_review_task)

        execution_failed_task = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_phase31_execution_failed_map",
            source_artifact_id="artifact_phase31_execution_failed_map",
            recommendation_type="repair_candidate",
            reason="status map execution failed",
        )
        execution_failed_task.status = "execution_failed"
        save_task(execution_failed_task)

        with patch.object(sys, "argv", ["main.py", "recommendation-result-options", "--run", run["id"]]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_result_options()

        text = output.getvalue()
        self.assertIn("Final Status: completed", text)
        self.assertIn("- No immediate follow-up required.", text)
        self.assertIn("Final Status: needs_review", text)
        self.assertIn("- Create follow-up review task explicitly if needed.", text)
        self.assertIn("Final Status: verification_failed", text)
        self.assertIn("- Inspect failure details.", text)
        self.assertIn("- Create repair task explicitly if needed.", text)
        self.assertIn("Final Status: execution_failed", text)
        self.assertIn("- Inspect execution failure.", text)

    def test_d_no_active_run_without_selector_stops_cleanly(self):
        with patch.object(sys, "argv", ["main.py", "recommendation-result-options"]):
            with patch("main.load_state", return_value={"workspace_initialized": True, "active_run_id": None}):
                output = io.StringIO()
                with redirect_stdout(output):
                    main.print_recommendation_result_options()

        self.assertIn(
            "No active run. Use --run <run_id>, --task <task_id>, or create/select an active run.",
            output.getvalue(),
        )

    def test_e_command_is_read_only(self):
        run = create_run("phase31 read-only")
        task = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_phase31_readonly",
            source_artifact_id="artifact_phase31_readonly",
            recommendation_type="repair_candidate",
            reason="readonly",
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

        with patch.object(sys, "argv", ["main.py", "recommendation-result-options", "--task", task.id]):
            with redirect_stdout(io.StringIO()):
                main.print_recommendation_result_options()

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
