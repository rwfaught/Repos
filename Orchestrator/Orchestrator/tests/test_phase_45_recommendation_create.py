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


class Phase45RecommendationCreateTests(unittest.TestCase):
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

    def _write_recommendation_record(self, run_id: str, reviewer_task_id: str, recommendation_type: str, reason: str):
        RECOMMENDATIONS_DIR.mkdir(parents=True, exist_ok=True)
        path = RECOMMENDATIONS_DIR / f"{reviewer_task_id}_{uuid4().hex[:8]}.json"
        payload = {
            "reviewer_task_id": reviewer_task_id,
            "run_id": run_id,
            "provider": "mock",
            "recommendation": {
                "recommendation_type": recommendation_type,
                "reason": reason,
            },
            "timestamp": "2026-04-19T00:00:00+00:00",
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

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

    def test_a_create_followup_from_manual_followup(self):
        run = create_run("phase45 manual followup create")
        source = self._create_source_task(run["id"], self._task_id("task_phase45_source_manual"))
        reviewer_id = self._task_id("task_phase45_reviewer_manual")
        self._create_reviewer_emitter_task(run["id"], reviewer_id, source.id, source.execution_artifact_id or "")
        self._persist_recommendation(reviewer_id, "manual_followup", "Follow-up is needed.")

        artifacts_before = self._snapshot_counts()["artifacts"]
        task_ids_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(
            sys,
            "argv",
            ["main.py", "recommendation-create", "--reviewer-task", reviewer_id],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_recommendation_task()

        text = output.getvalue()
        self.assertIn("Created task from recommendation-backed draft.", text)
        task_ids_after = {task.id for task in load_tasks_for_run(run["id"])}
        created_ids = task_ids_after - task_ids_before
        self.assertEqual(len(created_ids), 1)
        created = load_task(next(iter(created_ids)))
        self.assertEqual(created.role, "reviewer")
        self.assertTrue(created.title.startswith("Follow-up review for"))
        self.assertEqual(created.status, "queued")
        self.assertEqual(created.source_task_id, source.id)
        self.assertEqual(self._snapshot_counts()["artifacts"], artifacts_before)

    def test_b_create_repair_from_repair_candidate(self):
        run = create_run("phase45 repair create")
        source = self._create_source_task(run["id"], self._task_id("task_phase45_source_repair"))
        reviewer_id = self._task_id("task_phase45_reviewer_repair")
        self._create_reviewer_emitter_task(run["id"], reviewer_id, source.id, source.execution_artifact_id or "")
        self._persist_recommendation(reviewer_id, "repair_candidate", "Repair is needed.")

        artifacts_before = self._snapshot_counts()["artifacts"]
        task_ids_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(
            sys,
            "argv",
            ["main.py", "recommendation-create", "--reviewer-task", reviewer_id, "--run", run["id"]],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_recommendation_task()

        text = output.getvalue()
        self.assertIn("Created task from recommendation-backed draft.", text)
        task_ids_after = {task.id for task in load_tasks_for_run(run["id"])}
        created_ids = task_ids_after - task_ids_before
        self.assertEqual(len(created_ids), 1)
        created = load_task(next(iter(created_ids)))
        self.assertEqual(created.role, "coder")
        self.assertTrue(created.title.startswith("Repair for"))
        self.assertEqual(created.status, "queued")
        self.assertEqual(created.source_task_id, source.id)
        self.assertEqual(self._snapshot_counts()["artifacts"], artifacts_before)

    def test_c_accept_result_does_not_create_task(self):
        run = create_run("phase45 accept non-creative")
        source = self._create_source_task(run["id"], self._task_id("task_phase45_source_accept"))
        reviewer_id = self._task_id("task_phase45_reviewer_accept")
        self._create_reviewer_emitter_task(run["id"], reviewer_id, source.id, source.execution_artifact_id or "")
        self._persist_recommendation(reviewer_id, "accept_result", "Looks good.")

        counts_before = self._snapshot_counts()
        task_ids_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(sys, "argv", ["main.py", "recommendation-create", "--reviewer-task", reviewer_id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_recommendation_task()

        self.assertIn("does not support task creation", output.getvalue())
        self.assertEqual(task_ids_before, {task.id for task in load_tasks_for_run(run["id"])})
        self.assertEqual(self._snapshot_counts(), counts_before)

    def test_d_unsupported_recommendation_type(self):
        run = create_run("phase45 unsupported type")
        source = self._create_source_task(run["id"], self._task_id("task_phase45_source_unsupported"))
        reviewer_id = self._task_id("task_phase45_reviewer_unsupported")
        self._create_reviewer_emitter_task(run["id"], reviewer_id, source.id, source.execution_artifact_id or "")
        self._write_recommendation_record(
            run_id=run["id"],
            reviewer_task_id=reviewer_id,
            recommendation_type="unknown_future_type",
            reason="Unknown type.",
        )

        counts_before = self._snapshot_counts()
        task_ids_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(
            sys,
            "argv",
            ["main.py", "recommendation-create", "--reviewer-task", reviewer_id, "--run", run["id"]],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_recommendation_task()

        self.assertIn("Unsupported recommendation type for explicit creation", output.getvalue())
        self.assertEqual(task_ids_before, {task.id for task in load_tasks_for_run(run["id"])})
        self.assertEqual(self._snapshot_counts(), counts_before)

    def test_e_no_matching_recommendation_record(self):
        run = create_run("phase45 no matching recommendation")
        missing_reviewer_id = self._task_id("task_phase45_missing_reviewer")
        counts_before = self._snapshot_counts()
        task_ids_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(
            sys,
            "argv",
            ["main.py", "recommendation-create", "--reviewer-task", missing_reviewer_id, "--run", run["id"]],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_recommendation_task()

        self.assertIn("No matching recommendation record found", output.getvalue())
        self.assertEqual(task_ids_before, {task.id for task in load_tasks_for_run(run["id"])})
        self.assertEqual(self._snapshot_counts(), counts_before)

    def test_f_no_active_run_message_and_no_mutation(self):
        state = load_state()
        state["active_run_id"] = None
        save_state(state)
        state_before = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        counts_before = self._snapshot_counts()

        with patch.object(
            sys,
            "argv",
            ["main.py", "recommendation-create", "--reviewer-task", self._task_id("task_phase45_no_active")],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_recommendation_task()

        self.assertIn("No active run. Use --run <run_id> or create/select an active run.", output.getvalue())
        state_after = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        self.assertEqual(state_before, state_after)
        self.assertEqual(counts_before, self._snapshot_counts())


if __name__ == "__main__":
    unittest.main()
