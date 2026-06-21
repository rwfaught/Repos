import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from orchestrator.current_success_result_review import review_current_success_task_result
from orchestrator.task_schema import Task
import orchestrator.run_manager as run_manager
import orchestrator.artifact_store as artifact_store
import orchestrator.current_success_result_review as result_review


class Phase78CurrentSuccessResultReviewTests(unittest.TestCase):
    def _task(self, status="completed", artifact_id="artifact_phase78"):
        return Task(
            id="task_phase78",
            run_id="run_phase78",
            title="Bounded current-success demo task",
            role="coder",
            status=status,
            dependencies=[],
            success_criteria=["Produce bounded output."],
            files_in_scope=["phase78_demo.py"],
            retry_count=0,
            expected_output="bounded output",
            execution_artifact_id=artifact_id,
            verification_checks=[{"check": "file_contains_text", "target": "phase78_demo.py", "text": "PHASE78"}],
        )

    def test_completed_task_with_artifact_and_verifier_surfaces_operator_options(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = root / "tasks"
            artifacts = root / "artifacts"
            verifiers = root / "verifier_results"
            tasks.mkdir()
            artifacts.mkdir()
            verifiers.mkdir()

            task = self._task()
            artifact_payload = {
                "artifact_id": "artifact_phase78",
                "task_id": "task_phase78",
                "run_id": "run_phase78",
                "role": "coder",
                "status": "success",
                "output": "bounded output",
            }
            verifier_payload = {
                "task_id": "task_phase78",
                "run_id": "run_phase78",
                "verification_result": {
                    "overall_passed": True,
                    "checks": [
                        {
                            "name": "file_contains_text",
                            "passed": True,
                            "message": "Required text is present.",
                            "evidence": {"path": "phase78_demo.py", "contains_text": True},
                        }
                    ],
                    "messages": ["Required text is present."],
                },
            }

            with patch.object(run_manager, "TASKS_DIR", tasks), \
                 patch.object(result_review, "ARTIFACTS_DIR", artifacts), \
                 patch.object(result_review, "VERIFIER_RESULTS_DIR", verifiers):
                run_manager.save_task(task)
                (artifacts / "artifact_phase78.json").write_text(json.dumps(artifact_payload), encoding="utf-8")
                (verifiers / "task_phase78_20260612T000000000000Z.json").write_text(json.dumps(verifier_payload), encoding="utf-8")

                result = review_current_success_task_result({"task_id": "task_phase78"})

            self.assertTrue(result.get("current_success_result_review_surface"))
            self.assertTrue(result.get("ready_for_operator_review"))
            self.assertEqual(result.get("final_outcome_classification"), "completed_current_state_success")
            self.assertEqual(result.get("operator_response_surface"), "completed_result_response_options")
            self.assertEqual(result.get("artifact_summary", {}).get("artifact_id"), "artifact_phase78")
            self.assertTrue(result.get("verification_summary", {}).get("overall_passed"))
            self.assertFalse(result.get("task_mutated"))
            self.assertFalse(result.get("execution_performed"))
            self.assertFalse(result.get("provider_executed"))

    def test_missing_verifier_result_blocks_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = root / "tasks"
            artifacts = root / "artifacts"
            verifiers = root / "verifier_results"
            tasks.mkdir()
            artifacts.mkdir()
            verifiers.mkdir()

            with patch.object(run_manager, "TASKS_DIR", tasks), \
                 patch.object(result_review, "ARTIFACTS_DIR", artifacts), \
                 patch.object(result_review, "VERIFIER_RESULTS_DIR", verifiers):
                run_manager.save_task(self._task())
                (artifacts / "artifact_phase78.json").write_text(
                    json.dumps({"artifact_id": "artifact_phase78", "task_id": "task_phase78", "run_id": "run_phase78", "role": "coder", "status": "success", "output": "bounded output"}),
                    encoding="utf-8",
                )
                result = review_current_success_task_result({"task_id": "task_phase78"})

            self.assertEqual(result.get("final_outcome_classification"), "blocked")
            self.assertIn("current_success_required_record_missing", result.get("blocked_conditions", []))
            self.assertIn("verifier_result_file", result.get("missing_requirements", []))

    def test_verification_failure_classifies_cleanly_when_records_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = root / "tasks"
            artifacts = root / "artifacts"
            verifiers = root / "verifier_results"
            tasks.mkdir()
            artifacts.mkdir()
            verifiers.mkdir()

            with patch.object(run_manager, "TASKS_DIR", tasks), \
                 patch.object(result_review, "ARTIFACTS_DIR", artifacts), \
                 patch.object(result_review, "VERIFIER_RESULTS_DIR", verifiers):
                run_manager.save_task(self._task(status="verification_failed"))
                (artifacts / "artifact_phase78.json").write_text(
                    json.dumps({"artifact_id": "artifact_phase78", "task_id": "task_phase78", "run_id": "run_phase78", "role": "coder", "status": "success", "output": "bounded output"}),
                    encoding="utf-8",
                )
                (verifiers / "task_phase78_20260612T000000000000Z.json").write_text(
                    json.dumps({
                        "task_id": "task_phase78",
                        "run_id": "run_phase78",
                        "verification_result": {
                            "overall_passed": False,
                            "checks": [{"name": "file_contains_text", "passed": False, "message": "Required text is not present.", "evidence": {}}],
                            "messages": ["Required text is not present."],
                        },
                    }),
                    encoding="utf-8",
                )
                result = review_current_success_task_result({"task_id": "task_phase78"})

            self.assertTrue(result.get("ready_for_operator_review"))
            self.assertEqual(result.get("final_outcome_classification"), "verification_failure")
            self.assertEqual(result.get("operator_response_surface"), "verification_failure_response_options")


if __name__ == "__main__":
    unittest.main()
