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
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, VERIFIER_RESULTS_DIR
from orchestrator.recommendation_store import load_recommendation_records_for_run
from orchestrator.run_manager import (
    create_run,
    get_next_task,
    load_recommendation_created_tasks_for_run,
    load_task,
    load_tasks_for_run,
    save_task,
)
from orchestrator.task_schema import create_task


class Phase51CurrentSuccessValidationTests(unittest.TestCase):
    RECOMMENDATIONS_DIR = DATA_DIR / "reviewer_recommendations"

    def _task_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:8]}"

    def _create_task(
        self,
        run_id: str,
        task_id: str,
        role: str,
        files_in_scope: list[str],
        *,
        expected_output: str | None = None,
        source_task_id: str | None = None,
        source_artifact_id: str | None = None,
    ):
        task = create_task(
            {
                "id": task_id,
                "run_id": run_id,
                "title": f"Phase51 task {task_id}",
                "role": role,
                "status": "queued",
                "dependencies": [],
                "success_criteria": ["phase51 validation"],
                "files_in_scope": files_in_scope,
                "retry_count": 0,
                "expected_output": expected_output,
                "source_task_id": source_task_id,
                "source_artifact_id": source_artifact_id,
            }
        )
        save_task(task)
        return task

    def _artifacts_for_task(self, task_id: str) -> list[dict]:
        if not ARTIFACTS_DIR.exists():
            return []
        artifacts: list[dict] = []
        for path in ARTIFACTS_DIR.glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if str(payload.get("task_id")) == task_id:
                artifacts.append(payload)
        return artifacts

    def _verifier_results_for_task(self, task_id: str) -> list[dict]:
        if not VERIFIER_RESULTS_DIR.exists():
            return []
        records: list[dict] = []
        for path in VERIFIER_RESULTS_DIR.glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if str(payload.get("task_id")) == task_id:
                records.append(payload)
        return records

    def _capture(self, argv: list[str], fn) -> str:
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                fn()
            return output.getvalue()

    def test_a_successful_bounded_run_persists_clear_outcome_artifact_and_verification(self):
        run = create_run("phase51 scenario A successful bounded run")
        task_id = self._task_id("task_phase51_success")
        self._create_task(
            run_id=run["id"],
            task_id=task_id,
            role="coder",
            files_in_scope=["main.py"],
        )

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "Implemented bounded change and validated expected behavior with clear evidence.",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(task_id), provider_name="mock")

        updated = load_task(task_id)
        self.assertEqual(updated.status, "completed")
        self.assertTrue(str(updated.execution_artifact_id or "").strip())

        artifacts = self._artifacts_for_task(task_id)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].get("status"), "success")

        verifier_records = self._verifier_results_for_task(task_id)
        self.assertEqual(len(verifier_records), 1)
        verification = verifier_records[0].get("verification_result", {})
        self.assertTrue(verification.get("overall_passed"))

    def test_b_verification_failure_persists_artifact_and_clear_non_success_outcome(self):
        run = create_run("phase51 scenario B verification failure")
        task_id = self._task_id("task_phase51_verification_failed")
        self._create_task(
            run_id=run["id"],
            task_id=task_id,
            role="coder",
            files_in_scope=["phase51_missing_file_for_verifier.txt"],
        )

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "Execution produced output but referenced file is intentionally missing.",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(task_id), provider_name="mock")

        updated = load_task(task_id)
        self.assertEqual(updated.status, "verification_failed")
        self.assertTrue(str(updated.execution_artifact_id or "").strip())

        artifacts = self._artifacts_for_task(task_id)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].get("status"), "success")

        verifier_records = self._verifier_results_for_task(task_id)
        self.assertEqual(len(verifier_records), 1)
        verification = verifier_records[0].get("verification_result", {})
        self.assertFalse(verification.get("overall_passed"))

    def test_c_review_landing_persists_structured_recommendation_and_surfaces_are_legible(self):
        run = create_run("phase51 scenario C review landing")
        source_task_id = self._task_id("task_phase51_source_for_review")
        self._create_task(
            run_id=run["id"],
            task_id=source_task_id,
            role="coder",
            files_in_scope=["main.py"],
            expected_output="must_include_expected_phrase",
        )

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "This output is long enough for adequacy length checks but intentionally misses the expected phrase.",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(source_task_id), provider_name="mock")

        source_updated = load_task(source_task_id)
        self.assertEqual(source_updated.status, "needs_review")

        tasks_for_run = load_tasks_for_run(run["id"])
        reviewer_tasks = [
            task
            for task in tasks_for_run
            if task.role == "reviewer" and str(task.source_task_id or "") == source_task_id
        ]
        self.assertEqual(len(reviewer_tasks), 1)
        reviewer_task_id = reviewer_tasks[0].id

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": json.dumps(
                    {
                        "recommendation_type": "manual_followup",
                        "reason": "Source task output did not include the required phrase.",
                    }
                ),
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(reviewer_task_id), provider_name="mock")

        reviewer_updated = load_task(reviewer_task_id)
        self.assertEqual(reviewer_updated.status, "completed")

        records = [
            record
            for record in load_recommendation_records_for_run(run["id"])
            if str(record.get("reviewer_task_id")) == reviewer_task_id
        ]
        self.assertEqual(len(records), 1)
        record = records[0]
        recommendation = record.get("recommendation", {})
        self.assertEqual(recommendation.get("recommendation_type"), "manual_followup")
        self.assertEqual(
            recommendation.get("reason"),
            "Source task output did not include the required phrase.",
        )

        recommendations_text = self._capture(
            ["main.py", "recommendations", "--run", run["id"]],
            main.print_recommendations,
        )
        self.assertIn(f"Reviewer Task: {reviewer_task_id}", recommendations_text)
        self.assertIn("Type: manual_followup", recommendations_text)
        self.assertIn("Reason: Source task output did not include the required phrase.", recommendations_text)

        actions_text = self._capture(
            ["main.py", "recommendation-actions", "--run", run["id"]],
            main.print_recommendation_actions,
        )
        self.assertIn(f"reviewer_task_id={reviewer_task_id}", actions_text)
        self.assertIn("recommendation_type=manual_followup", actions_text)
        self.assertIn("Follow-up review task could be created explicitly.", actions_text)

    def test_d_no_hidden_behavior_change_in_review_landing_path(self):
        run = create_run("phase51 scenario D no hidden behavior change")
        first_task_id = self._task_id("task_phase51_no_hidden_first")
        second_task_id = self._task_id("task_phase51_no_hidden_second")

        self._create_task(
            run_id=run["id"],
            task_id=first_task_id,
            role="coder",
            files_in_scope=["main.py"],
            expected_output="required_phrase_for_review",
        )
        self._create_task(
            run_id=run["id"],
            task_id=second_task_id,
            role="coder",
            files_in_scope=["main.py"],
        )

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "Output is intentionally adequate-length but does not satisfy required expected output.",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(first_task_id), provider_name="mock")

        tasks_for_run = load_tasks_for_run(run["id"])
        reviewer_tasks = [
            task
            for task in tasks_for_run
            if task.role == "reviewer" and str(task.source_task_id or "") == first_task_id
        ]
        self.assertEqual(len(reviewer_tasks), 1)

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": json.dumps(
                    {
                        "recommendation_type": "repair_candidate",
                        "reason": "A repair task may be needed after manual verification.",
                    }
                ),
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(reviewer_tasks[0].id), provider_name="mock")

        tasks_after = load_tasks_for_run(run["id"])
        self.assertEqual(len(tasks_after), 3)

        second_task = load_task(second_task_id)
        self.assertEqual(second_task.status, "queued")

        next_task = get_next_task(run["id"])
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.id, second_task_id)

        auto_created_recommendation_tasks = load_recommendation_created_tasks_for_run(run["id"])
        self.assertEqual(auto_created_recommendation_tasks, [])

        records = load_recommendation_records_for_run(run["id"])
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertFalse(bool(record.get("accepted", False)))
        self.assertFalse(bool(record.get("archived", False)))


if __name__ == "__main__":
    unittest.main()
