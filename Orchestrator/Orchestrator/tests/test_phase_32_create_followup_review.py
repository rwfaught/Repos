import io
import sys
import unittest
from contextlib import redirect_stdout
from uuid import uuid4
from unittest.mock import patch

import main
from orchestrator import engine
from orchestrator.run_manager import (
    create_run,
    create_task_from_recommendation,
    get_next_task,
    is_recommendation_created_task,
    load_task,
    load_tasks_for_run,
    save_task,
)
from orchestrator.task_schema import create_task


class Phase32CreateFollowupReviewTests(unittest.TestCase):
    def _task_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:8]}"

    def _create_ordinary_task(self, run_id: str, task_id: str, status: str = "queued"):
        task = create_task(
            {
                "id": task_id,
                "run_id": run_id,
                "title": f"Ordinary task {task_id}",
                "role": "coder",
                "status": status,
                "dependencies": [],
                "success_criteria": ["ordinary success"],
                "files_in_scope": [],
                "retry_count": 0,
            }
        )
        save_task(task)
        return task

    def test_a_create_followup_review_from_eligible_needs_review_result(self):
        run = create_run("phase32 eligible source")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="origin_source_task",
            source_artifact_id="origin_artifact",
            recommendation_type="repair_candidate",
            reason="source reason",
        )
        source.status = "needs_review"
        source.execution_artifact_id = "artifact_needs_review_result"
        source.files_in_scope = ["src/feature.py", "tests/test_feature.py"]
        save_task(source)

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(sys, "argv", ["main.py", "create-followup-review", "--task", source.id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_followup_review()

        text = output.getvalue()
        self.assertIn("Created follow-up review task.", text)
        self.assertIn("Created from needs_review recommendation-derived result.", text)

        tasks_after = load_tasks_for_run(run["id"])
        created = [task for task in tasks_after if task.id not in tasks_before]
        self.assertEqual(len(created), 1)

        followup = created[0]
        self.assertEqual(followup.run_id, run["id"])
        self.assertEqual(followup.role, "reviewer")
        self.assertEqual(followup.status, "queued")
        self.assertEqual(followup.source_task_id, source.id)
        self.assertEqual(followup.source_artifact_id, source.execution_artifact_id)
        self.assertEqual(followup.files_in_scope, source.files_in_scope)
        self.assertIn(f"Follow-up review for {source.id}", followup.title)
        self.assertIn(source.id, followup.review_reason or "")
        self.assertIn(f"Inspect artifact {source.execution_artifact_id}", followup.review_reason or "")
        self.assertEqual(followup.recommendation_type, "manual_followup")
        self.assertTrue(is_recommendation_created_task(followup))

    def test_b_reject_non_needs_review_recommendation_result(self):
        run = create_run("phase32 reject non-needs-review")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_non_needs_review",
            source_artifact_id="artifact_non_needs_review",
            recommendation_type="manual_followup",
            reason="reason",
        )
        source.status = "completed"
        save_task(source)

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(sys, "argv", ["main.py", "create-followup-review", "--task", source.id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_followup_review()

        self.assertIn("Task status is not needs_review", output.getvalue())
        tasks_after = {task.id for task in load_tasks_for_run(run["id"])}
        self.assertEqual(tasks_after, tasks_before)

    def test_c_reject_ordinary_task(self):
        run = create_run("phase32 reject ordinary")
        ordinary = self._create_ordinary_task(run["id"], self._task_id("task_phase32_ordinary"), status="needs_review")

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(sys, "argv", ["main.py", "create-followup-review", "--task", ordinary.id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_followup_review()

        self.assertIn("Task is not recommendation-derived", output.getvalue())
        tasks_after = {task.id for task in load_tasks_for_run(run["id"])}
        self.assertEqual(tasks_after, tasks_before)

    def test_d_reject_missing_task_id(self):
        missing_id = self._task_id("task_phase32_missing")
        with patch.object(sys, "argv", ["main.py", "create-followup-review", "--task", missing_id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_followup_review()

        self.assertIn(f"Task not found: {missing_id}", output.getvalue())

    def test_e_next_behavior_unchanged_no_auto_execution(self):
        run = create_run("phase32 no queue policy change")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_for_next_behavior",
            source_artifact_id="artifact_for_next_behavior",
            recommendation_type="repair_candidate",
            reason="reason",
        )
        source.status = "needs_review"
        source.execution_artifact_id = "artifact_needs_review_queue"
        save_task(source)

        with patch.object(sys, "argv", ["main.py", "create-followup-review", "--task", source.id]):
            with redirect_stdout(io.StringIO()):
                main.create_followup_review()

        followup = None
        for task in load_tasks_for_run(run["id"]):
            if task.source_task_id == source.id and task.title.startswith("Follow-up review for"):
                followup = task
                break

        self.assertIsNotNone(followup)
        self.assertEqual(followup.status, "queued")

        next_task = get_next_task(run["id"])
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.id, followup.id)

        engine.process_next_task(provider_name="mock")
        self.assertEqual(load_task(followup.id).status, "needs_review")

    def test_f_create_followup_review_from_needs_review_result_without_artifact(self):
        run = create_run("phase32 needs_review without artifact")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_without_artifact",
            source_artifact_id="upstream_artifact_without_artifact",
            recommendation_type="manual_followup",
            reason="reason",
        )
        source.status = "needs_review"
        source.execution_artifact_id = None
        save_task(source)

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(sys, "argv", ["main.py", "create-followup-review", "--task", source.id]):
            with redirect_stdout(io.StringIO()):
                main.create_followup_review()

        tasks_after = load_tasks_for_run(run["id"])
        created = [task for task in tasks_after if task.id not in tasks_before]
        self.assertEqual(len(created), 1)
        followup = created[0]
        self.assertEqual(followup.source_task_id, source.id)
        self.assertIsNone(followup.source_artifact_id)
        self.assertEqual(followup.files_in_scope, [])
        self.assertIn("No result artifact was persisted for that source task.", followup.review_reason or "")
        self.assertEqual(followup.recommendation_identity, "recommendation_created")
        followup.recommendation_reason = None
        save_task(followup)
        followup = load_task(followup.id)
        self.assertTrue(is_recommendation_created_task(followup))

    def test_g_duplicate_followup_review_queued_is_blocked(self):
        run = create_run("phase32 duplicate followup blocked")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_dup_followup",
            source_artifact_id="artifact_dup_followup",
            recommendation_type="repair_candidate",
            reason="reason",
        )
        source.status = "needs_review"
        source.execution_artifact_id = "artifact_needs_review_dup"
        save_task(source)

        with patch.object(sys, "argv", ["main.py", "create-followup-review", "--task", source.id]):
            with redirect_stdout(io.StringIO()):
                main.create_followup_review()

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}
        with patch.object(sys, "argv", ["main.py", "create-followup-review", "--task", source.id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_followup_review()

        text = output.getvalue()
        self.assertIn("Equivalent follow-up review task already exists; no new task created.", text)
        self.assertIn("Existing Task ID:", text)
        self.assertIn("Existing Title:", text)
        self.assertIn("Existing Status: queued", text)
        tasks_after = {task.id for task in load_tasks_for_run(run["id"])}
        self.assertEqual(tasks_after, tasks_before)

    def test_h_followup_review_recreation_allowed_after_completed(self):
        run = create_run("phase32 duplicate followup completed allows recreate")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_dup_followup_completed",
            source_artifact_id="artifact_dup_followup_completed",
            recommendation_type="repair_candidate",
            reason="reason",
        )
        source.status = "needs_review"
        source.execution_artifact_id = "artifact_needs_review_completed"
        save_task(source)

        with patch.object(sys, "argv", ["main.py", "create-followup-review", "--task", source.id]):
            with redirect_stdout(io.StringIO()):
                main.create_followup_review()

        first_followup = None
        for task in load_tasks_for_run(run["id"]):
            if task.source_task_id == source.id and task.recommendation_type == "manual_followup":
                first_followup = task
                break
        self.assertIsNotNone(first_followup)
        first_followup.status = "completed"
        save_task(first_followup)

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}
        with patch.object(sys, "argv", ["main.py", "create-followup-review", "--task", source.id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_followup_review()

        self.assertIn("Created follow-up review task.", output.getvalue())
        tasks_after = load_tasks_for_run(run["id"])
        created = [task for task in tasks_after if task.id not in tasks_before]
        self.assertEqual(len(created), 1)


if __name__ == "__main__":
    unittest.main()
