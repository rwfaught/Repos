import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.reviewer_output as reviewer_output
import orchestrator.run_manager as run_manager
from orchestrator import engine
from orchestrator.task_schema import Task


class Phase91ProviderStatusRoutingTests(unittest.TestCase):
    def _task(self, task_id: str) -> Task:
        return Task(
            id=task_id,
            run_id="run_phase91",
            title="Route provider semantic status truthfully",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Preserve provider status semantics."],
            files_in_scope=[],
            retry_count=0,
            expected_output=None,
        )

    def _ollama_result(self, task_id: str, status: str) -> dict:
        return {
            "status": "success",
            "output": json.dumps(
                {
                    "task_id": task_id,
                    "status": status,
                    "summary": f"Task result declared {status} with bounded evidence.",
                    "evidence": [f"Observed a valid {status} result for Phase 91 routing."],
                    "files_touched": [],
                    "caveats": [],
                }
            ),
            "provider": "ollama",
            "metadata": {"task_id": task_id},
            "error": None,
        }

    def _run_with_result(self, task: Task, provider_result: dict) -> tuple[Task, list[Task], list[Path], list[Path]]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks_dir = root / "tasks"
            artifacts_dir = root / "artifacts"
            verifier_dir = root / "verifier_results"
            recommendations_dir = root / "reviewer_recommendations"

            with (
                patch.object(run_manager, "TASKS_DIR", tasks_dir),
                patch.object(artifact_store, "ARTIFACTS_DIR", artifacts_dir),
                patch.object(engine, "VERIFIER_RESULTS_DIR", verifier_dir),
                patch.object(reviewer_output, "REVIEWER_RECOMMENDATIONS_DIR", recommendations_dir),
                patch("orchestrator.engine.dispatch_task", return_value=provider_result),
            ):
                run_manager.save_task(task)
                engine.process_task_by_id(run_manager.load_task(task.id), provider_name="mocked")
                updated = run_manager.load_task(task.id)
                tasks = run_manager.load_tasks_for_run(task.run_id)
                artifact_files = sorted(artifacts_dir.glob("*.json"))
                verifier_files = sorted(verifier_dir.glob("*.json"))

                return updated, tasks, artifact_files, verifier_files

    def test_completed_ollama_envelope_can_complete_after_existing_gates_pass(self):
        task = self._task("task_phase91_completed")
        updated, tasks, artifacts, verifier_results = self._run_with_result(
            task,
            self._ollama_result(task.id, "completed"),
        )

        self.assertEqual(updated.status, "completed")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(len(verifier_results), 1)

    def test_blocked_ollama_envelope_routes_to_needs_review_not_completed(self):
        task = self._task("task_phase91_blocked")
        updated, tasks, artifacts, verifier_results = self._run_with_result(
            task,
            self._ollama_result(task.id, "blocked"),
        )

        self.assertEqual(updated.status, "needs_review")
        self.assertEqual(len([item for item in tasks if item.role == "reviewer"]), 1)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(len(verifier_results), 1)

    def test_needs_review_ollama_envelope_routes_to_needs_review_not_completed(self):
        task = self._task("task_phase91_needs_review")
        updated, tasks, artifacts, verifier_results = self._run_with_result(
            task,
            self._ollama_result(task.id, "needs_review"),
        )

        self.assertEqual(updated.status, "needs_review")
        self.assertEqual(len([item for item in tasks if item.role == "reviewer"]), 1)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(len(verifier_results), 1)

    def test_not_implemented_provider_status_routes_to_execution_failed(self):
        task = self._task("task_phase91_not_implemented")
        provider_result = {
            "status": "not_implemented",
            "output": None,
            "provider": "codex",
            "metadata": {"task_id": task.id, "role": task.role},
            "error": "Codex provider is not implemented.",
        }

        updated, tasks, artifacts, verifier_results = self._run_with_result(task, provider_result)

        self.assertEqual(updated.status, "execution_failed")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(len(verifier_results), 1)


if __name__ == "__main__":
    unittest.main()
