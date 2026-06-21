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


class Phase42RecommendationSummaryTests(unittest.TestCase):
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

    def test_a_active_run_summary_groups_and_lists_entries(self):
        run = create_run("phase42 active run summary")

        manual_task_id = self._task_id("task_phase42_manual")
        self._create_reviewer_emitter_task(run["id"], manual_task_id)
        self._persist_recommendation(
            task_id=manual_task_id,
            recommendation_type="manual_followup",
            reason="Manual follow-up required.",
        )

        repair_task_id = self._task_id("task_phase42_repair")
        self._create_reviewer_emitter_task(run["id"], repair_task_id)
        self._persist_recommendation(
            task_id=repair_task_id,
            recommendation_type="repair_candidate",
            reason="Repair candidate identified.",
        )

        with patch.object(sys, "argv", ["main.py", "recommendation-summary"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_summary()

        text = output.getvalue()
        self.assertIn(f"Recommendation summary for run: {run['id']}", text)
        self.assertIn("Total recommendation records: 2", text)
        self.assertIn("Counts by recommendation type:", text)
        self.assertIn("- accept_result: 0", text)
        self.assertIn("- manual_followup: 1", text)
        self.assertIn("- repair_candidate: 1", text)
        self.assertIn("manual_followup (1):", text)
        self.assertIn("repair_candidate (1):", text)
        self.assertIn(f"reviewer_task_id={manual_task_id}", text)
        self.assertIn("reason=Manual follow-up required.", text)
        self.assertIn(f"reviewer_task_id={repair_task_id}", text)
        self.assertIn("reason=Repair candidate identified.", text)
        self.assertIn("timestamp=", text)

    def test_b_explicit_run_filter_scopes_summary(self):
        run_a = create_run("phase42 explicit summary A")
        task_a = self._task_id("task_phase42_a")
        self._create_reviewer_emitter_task(run_a["id"], task_a)
        self._persist_recommendation(task_a, "manual_followup", "Summary for run A.")

        run_b = create_run("phase42 explicit summary B")
        task_b = self._task_id("task_phase42_b")
        self._create_reviewer_emitter_task(run_b["id"], task_b)
        self._persist_recommendation(task_b, "repair_candidate", "Summary for run B.")

        with patch.object(sys, "argv", ["main.py", "recommendation-summary", "--run", run_a["id"]]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_summary()

        text = output.getvalue()
        self.assertIn(f"Recommendation summary for run: {run_a['id']}", text)
        self.assertIn(f"reviewer_task_id={task_a}", text)
        self.assertNotIn(f"reviewer_task_id={task_b}", text)
        self.assertNotIn("Summary for run B.", text)

    def test_c_no_matching_recommendations_message_and_no_mutation(self):
        run = create_run("phase42 no matching recommendations")
        before_counts = self._snapshot_counts()

        with patch.object(sys, "argv", ["main.py", "recommendation-summary", "--run", run["id"]]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_summary()

        text = output.getvalue()
        self.assertIn(f"Recommendation summary for run: {run['id']}", text)
        self.assertIn("No recommendation records found for this run.", text)
        self.assertEqual(self._snapshot_counts(), before_counts)

    def test_d_no_active_run_message_and_no_mutation(self):
        state = load_state()
        state["active_run_id"] = None
        save_state(state)
        state_before = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        before_counts = self._snapshot_counts()

        with patch.object(sys, "argv", ["main.py", "recommendation-summary"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.print_recommendation_summary()

        self.assertIn("No active run. Use --run <run_id> or create/select an active run.", output.getvalue())
        state_after = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        self.assertEqual(state_before, state_after)
        self.assertEqual(before_counts, self._snapshot_counts())


if __name__ == "__main__":
    unittest.main()
