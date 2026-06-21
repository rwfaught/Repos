import json
import unittest
from pathlib import Path

from orchestrator import engine
from orchestrator.paths import DATA_DIR
from orchestrator.run_manager import create_run, load_task, load_tasks_for_run, save_task
from orchestrator.task_schema import create_task


RECOMMENDATIONS_DIR = DATA_DIR / "reviewer_recommendations"


class Phase12ReviewerRecommendationRegressionTests(unittest.TestCase):
    def _recommendation_files(self) -> set[Path]:
        if not RECOMMENDATIONS_DIR.exists():
            return set()
        return set(RECOMMENDATIONS_DIR.glob("*.json"))

    def _create_task(self, run_id: str, task_id: str, role: str, files_in_scope: list[str], expected_output=None):
        task = create_task(
            {
                "id": task_id,
                "run_id": run_id,
                "title": f"Test task {task_id}",
                "role": role,
                "status": "queued",
                "dependencies": [],
                "success_criteria": ["test success"],
                "files_in_scope": files_in_scope,
                "retry_count": 0,
                "expected_output": expected_output,
                "source_task_id": "source_task_for_test" if role == "reviewer" else None,
                "source_artifact_id": "source_artifact_for_test" if role == "reviewer" else None,
            }
        )
        save_task(task)
        return task

    def test_a_valid_reviewer_recommendation_completes_and_persists_record(self):
        run = create_run("phase12 test A")
        task_id = "task_phase12_A"
        self._create_task(run["id"], task_id, "reviewer", ["main.py"])

        records_before = self._recommendation_files()
        original_dispatch = engine.dispatch_task

        def fake_dispatch(task, provider_name="mock", context=None):
            return {
                "status": "success",
                "output": json.dumps(
                    {
                        "recommendation_type": "manual_followup",
                        "reason": "Needs manual review.",
                    }
                ),
                "provider": "mock",
                "metadata": {"task_id": task.id, "role": task.role},
                "error": None,
            }

        try:
            engine.dispatch_task = fake_dispatch
            engine.process_next_task(provider_name="mock")
        finally:
            engine.dispatch_task = original_dispatch

        updated = load_task(task_id)
        self.assertEqual(updated.status, "completed")

        records_after = self._recommendation_files()
        new_records = sorted(records_after - records_before)
        self.assertEqual(len(new_records), 1)
        persisted = json.loads(new_records[0].read_text(encoding="utf-8"))
        self.assertEqual(
            set(persisted["recommendation"].keys()),
            {"recommendation_type", "reason"},
        )
        self.assertEqual(persisted["recommendation"]["recommendation_type"], "manual_followup")

    def test_b_invalid_reviewer_recommendation_fails_without_persisting_record(self):
        run = create_run("phase12 test B")
        task_id = "task_phase12_B"
        self._create_task(run["id"], task_id, "reviewer", ["main.py"])

        records_before = self._recommendation_files()
        original_dispatch = engine.dispatch_task

        def fake_dispatch(task, provider_name="mock", context=None):
            return {
                "status": "success",
                "output": "{not valid json",
                "provider": "mock",
                "metadata": {"task_id": task.id, "role": task.role},
                "error": None,
            }

        try:
            engine.dispatch_task = fake_dispatch
            engine.process_next_task(provider_name="mock")
        finally:
            engine.dispatch_task = original_dispatch

        updated = load_task(task_id)
        self.assertEqual(updated.status, "verification_failed")
        self.assertEqual(self._recommendation_files(), records_before)

    def test_c_reviewer_execution_failure_precedence(self):
        run = create_run("phase12 test C")
        task_id = "task_phase12_C"
        self._create_task(run["id"], task_id, "reviewer", ["main.py"])

        records_before = self._recommendation_files()
        engine.process_next_task(provider_name="no_such_provider")

        updated = load_task(task_id)
        self.assertEqual(updated.status, "execution_failed")
        self.assertEqual(self._recommendation_files(), records_before)

    def test_d_reviewer_verification_failure_precedence(self):
        run = create_run("phase12 test D")
        task_id = "task_phase12_D"
        self._create_task(run["id"], task_id, "reviewer", ["missing/file/task_phase12_D.txt"])

        records_before = self._recommendation_files()
        engine.process_next_task(provider_name="mock")

        updated = load_task(task_id)
        self.assertEqual(updated.status, "verification_failed")
        self.assertEqual(self._recommendation_files(), records_before)

    def test_e_ordinary_task_behavior_unchanged(self):
        run = create_run("phase12 test E")
        task_id = "task_phase12_E"
        self._create_task(
            run["id"],
            task_id,
            "coder",
            ["main.py"],
            expected_output="patch suggestion",
        )

        records_before = self._recommendation_files()
        engine.process_next_task(provider_name="mock")

        updated = load_task(task_id)
        self.assertEqual(updated.status, "needs_review")

        tasks_for_run = load_tasks_for_run(run["id"])
        reviewer_tasks = [task for task in tasks_for_run if task.role == "reviewer"]
        self.assertEqual(len(reviewer_tasks), 1)
        self.assertEqual(self._recommendation_files(), records_before)


if __name__ == "__main__":
    unittest.main()
