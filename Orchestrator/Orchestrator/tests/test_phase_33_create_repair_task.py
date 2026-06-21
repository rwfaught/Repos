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


class Phase33CreateRepairTaskTests(unittest.TestCase):
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

    def test_a_create_repair_task_from_verification_failed_result(self):
        run = create_run("phase33 verification failed source")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="origin_source_task_vf",
            source_artifact_id="origin_artifact_vf",
            recommendation_type="repair_candidate",
            reason="source reason vf",
        )
        source.status = "verification_failed"
        source.execution_artifact_id = "artifact_failed_vf"
        source.files_in_scope = ["src/repair_target.py", "tests/test_repair_target.py"]
        save_task(source)

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(sys, "argv", ["main.py", "create-repair-task", "--task", source.id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_repair_task()

        text = output.getvalue()
        self.assertIn("Created repair task.", text)
        self.assertIn("Created from failed recommendation-derived result.", text)

        tasks_after = load_tasks_for_run(run["id"])
        created = [task for task in tasks_after if task.id not in tasks_before]
        self.assertEqual(len(created), 1)

        repair = created[0]
        self.assertEqual(repair.run_id, run["id"])
        self.assertEqual(repair.role, "coder")
        self.assertEqual(repair.status, "queued")
        self.assertEqual(repair.source_task_id, source.id)
        self.assertEqual(repair.source_artifact_id, source.execution_artifact_id)
        self.assertEqual(repair.files_in_scope, source.files_in_scope)
        self.assertIn(f"Repair for {source.id}", repair.title)
        self.assertIn(source.id, repair.review_reason or "")
        self.assertIn(f"Repair should address artifact {source.execution_artifact_id}", repair.review_reason or "")
        self.assertEqual(repair.recommendation_type, "repair_candidate")
        self.assertTrue(is_recommendation_created_task(repair))

    def test_b_create_repair_task_from_execution_failed_result(self):
        run = create_run("phase33 execution failed source")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="origin_source_task_ef",
            source_artifact_id="origin_artifact_ef",
            recommendation_type="manual_followup",
            reason="source reason ef",
        )
        source.status = "execution_failed"
        source.execution_artifact_id = "artifact_failed_ef"
        save_task(source)

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(sys, "argv", ["main.py", "create-repair-task", "--task", source.id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_repair_task()

        self.assertIn("Created repair task.", output.getvalue())

        tasks_after = load_tasks_for_run(run["id"])
        created = [task for task in tasks_after if task.id not in tasks_before]
        self.assertEqual(len(created), 1)
        repair = created[0]
        self.assertEqual(repair.status, "queued")
        self.assertEqual(repair.source_task_id, source.id)
        self.assertEqual(repair.source_artifact_id, source.execution_artifact_id)
        self.assertEqual(repair.role, "coder")

    def test_c_reject_needs_review_result(self):
        run = create_run("phase33 reject needs_review")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_non_failed",
            source_artifact_id="artifact_non_failed",
            recommendation_type="repair_candidate",
            reason="reason",
        )
        source.status = "needs_review"
        save_task(source)

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(sys, "argv", ["main.py", "create-repair-task", "--task", source.id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_repair_task()

        self.assertIn("Task status is not eligible for repair-task creation", output.getvalue())
        tasks_after = {task.id for task in load_tasks_for_run(run["id"])}
        self.assertEqual(tasks_after, tasks_before)

    def test_d_reject_ordinary_task(self):
        run = create_run("phase33 reject ordinary")
        ordinary = self._create_ordinary_task(run["id"], self._task_id("task_phase33_ordinary"), status="verification_failed")

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(sys, "argv", ["main.py", "create-repair-task", "--task", ordinary.id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_repair_task()

        self.assertIn("Task is not recommendation-derived", output.getvalue())
        tasks_after = {task.id for task in load_tasks_for_run(run["id"])}
        self.assertEqual(tasks_after, tasks_before)

    def test_e_reject_missing_task_id(self):
        missing_id = self._task_id("task_phase33_missing")
        with patch.object(sys, "argv", ["main.py", "create-repair-task", "--task", missing_id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_repair_task()

        self.assertIn(f"Task not found: {missing_id}", output.getvalue())

    def test_f_no_queue_execution_behavior_change(self):
        run = create_run("phase33 no queue policy change")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_for_queue_behavior",
            source_artifact_id="artifact_for_queue_behavior",
            recommendation_type="repair_candidate",
            reason="reason",
        )
        source.status = "verification_failed"
        source.execution_artifact_id = "artifact_failed_queue"
        save_task(source)

        with patch.object(sys, "argv", ["main.py", "create-repair-task", "--task", source.id]):
            with redirect_stdout(io.StringIO()):
                main.create_repair_task()

        repair = None
        for task in load_tasks_for_run(run["id"]):
            if task.source_task_id == source.id and task.title.startswith("Repair for"):
                repair = task
                break

        self.assertIsNotNone(repair)
        self.assertEqual(repair.status, "queued")

        next_task = get_next_task(run["id"])
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.id, repair.id)

        engine.process_next_task(provider_name="mock")
        self.assertNotEqual(load_task(repair.id).status, "queued")

    def test_g_create_repair_task_from_failed_result_without_artifact(self):
        run = create_run("phase33 failed without artifact")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="origin_source_task_no_artifact",
            source_artifact_id="upstream_artifact_no_artifact",
            recommendation_type="repair_candidate",
            reason="source reason no artifact",
        )
        source.status = "verification_failed"
        source.execution_artifact_id = None
        save_task(source)

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}

        with patch.object(sys, "argv", ["main.py", "create-repair-task", "--task", source.id]):
            with redirect_stdout(io.StringIO()):
                main.create_repair_task()

        tasks_after = load_tasks_for_run(run["id"])
        created = [task for task in tasks_after if task.id not in tasks_before]
        self.assertEqual(len(created), 1)
        repair = created[0]
        self.assertEqual(repair.source_task_id, source.id)
        self.assertIsNone(repair.source_artifact_id)
        self.assertEqual(repair.files_in_scope, [])
        self.assertIn("No failed-result artifact was persisted for that source task.", repair.review_reason or "")
        self.assertEqual(repair.recommendation_identity, "recommendation_created")
        repair.recommendation_reason = None
        save_task(repair)
        repair = load_task(repair.id)
        self.assertTrue(is_recommendation_created_task(repair))

    def test_h_duplicate_repair_task_queued_is_blocked(self):
        run = create_run("phase33 duplicate repair blocked")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_dup_repair",
            source_artifact_id="artifact_dup_repair",
            recommendation_type="repair_candidate",
            reason="reason",
        )
        source.status = "verification_failed"
        source.execution_artifact_id = "artifact_failed_dup"
        save_task(source)

        with patch.object(sys, "argv", ["main.py", "create-repair-task", "--task", source.id]):
            with redirect_stdout(io.StringIO()):
                main.create_repair_task()

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}
        with patch.object(sys, "argv", ["main.py", "create-repair-task", "--task", source.id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_repair_task()

        text = output.getvalue()
        self.assertIn("Equivalent repair task already exists; no new task created.", text)
        self.assertIn("Existing Task ID:", text)
        self.assertIn("Existing Title:", text)
        self.assertIn("Existing Status: queued", text)
        tasks_after = {task.id for task in load_tasks_for_run(run["id"])}
        self.assertEqual(tasks_after, tasks_before)

    def test_i_repair_recreation_allowed_after_completed(self):
        run = create_run("phase33 duplicate repair completed allows recreate")
        source = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="source_dup_repair_completed",
            source_artifact_id="artifact_dup_repair_completed",
            recommendation_type="repair_candidate",
            reason="reason",
        )
        source.status = "verification_failed"
        source.execution_artifact_id = "artifact_failed_completed"
        save_task(source)

        with patch.object(sys, "argv", ["main.py", "create-repair-task", "--task", source.id]):
            with redirect_stdout(io.StringIO()):
                main.create_repair_task()

        first_repair = None
        for task in load_tasks_for_run(run["id"]):
            if task.source_task_id == source.id and task.recommendation_type == "repair_candidate":
                first_repair = task
                break
        self.assertIsNotNone(first_repair)
        first_repair.status = "completed"
        save_task(first_repair)

        tasks_before = {task.id for task in load_tasks_for_run(run["id"])}
        with patch.object(sys, "argv", ["main.py", "create-repair-task", "--task", source.id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.create_repair_task()

        self.assertIn("Created repair task.", output.getvalue())
        tasks_after = load_tasks_for_run(run["id"])
        created = [task for task in tasks_after if task.id not in tasks_before]
        self.assertEqual(len(created), 1)


if __name__ == "__main__":
    unittest.main()
