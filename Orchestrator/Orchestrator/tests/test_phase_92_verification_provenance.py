import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.paths as project_paths
import orchestrator.reviewer_output as reviewer_output
import orchestrator.run_manager as run_manager
from orchestrator import engine
from orchestrator.task_schema import Task


class Phase92VerificationProvenanceTests(unittest.TestCase):
    def _task(
        self,
        task_id: str,
        *,
        files_in_scope: list[str],
        requires_causal_change: bool,
    ) -> Task:
        return Task(
            id=task_id,
            run_id="run_phase92",
            title="Verify causal filesystem change",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Require bounded causal filesystem evidence."],
            files_in_scope=files_in_scope,
            retry_count=0,
            requires_causal_change=requires_causal_change,
        )

    def _provider_result(self, task: Task, *, status: str = "success") -> dict:
        return {
            "status": status,
            "output": (
                "Provider completed the bounded operation with inspectable evidence."
                if status == "success"
                else None
            ),
            "provider": "mocked",
            "metadata": {"task_id": task.id},
            "error": None if status == "success" else "Provider failed.",
        }

    def _run(
        self,
        task: Task,
        *,
        prepare=None,
        provider_side_effect=None,
        provider_status: str = "success",
    ) -> tuple[Task, dict, Path]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks_dir = root / "data" / "tasks"
            artifacts_dir = root / "data" / "artifacts"
            verifier_dir = root / "data" / "verifier_results"
            recommendations_dir = root / "data" / "reviewer_recommendations"

            if prepare is not None:
                prepare(root)

            def dispatch_side_effect(dispatched_task, provider_name="mocked"):
                if provider_side_effect is not None:
                    provider_side_effect(root)
                return self._provider_result(dispatched_task, status=provider_status)

            with (
                patch.object(project_paths, "PROJECT_ROOT", root),
                patch.object(run_manager, "TASKS_DIR", tasks_dir),
                patch.object(artifact_store, "ARTIFACTS_DIR", artifacts_dir),
                patch.object(engine, "VERIFIER_RESULTS_DIR", verifier_dir),
                patch.object(
                    reviewer_output,
                    "REVIEWER_RECOMMENDATIONS_DIR",
                    recommendations_dir,
                ),
                patch("orchestrator.engine.dispatch_task", side_effect=dispatch_side_effect),
            ):
                run_manager.save_task(task)
                engine.process_task_by_id(run_manager.load_task(task.id), provider_name="mocked")
                updated = run_manager.load_task(task.id)
                verifier_files = sorted(verifier_dir.glob("*.json"))
                self.assertEqual(len(verifier_files), 1)
                verifier_record = json.loads(
                    verifier_files[0].read_text(encoding="utf-8")
                )
                target_path = root / task.files_in_scope[0] if task.files_in_scope else root

        return updated, verifier_record, target_path

    def test_preexisting_compliant_target_without_provider_write_is_rejected(self):
        task = self._task(
            "task_phase92_preexisting_no_write",
            files_in_scope=["existing.py"],
            requires_causal_change=True,
        )

        updated, record, _ = self._run(
            task,
            prepare=lambda root: (root / "existing.py").write_text(
                "value = 1\n", encoding="utf-8"
            ),
        )

        self.assertEqual(updated.status, "verification_failed")
        verification = record["verification_result"]
        self.assertFalse(verification["causal_change_passed"])
        self.assertEqual(verification["changed_targets"], [])

    def test_same_content_rewrite_is_rejected(self):
        task = self._task(
            "task_phase92_same_content",
            files_in_scope=["same.py"],
            requires_causal_change=True,
        )

        updated, record, _ = self._run(
            task,
            prepare=lambda root: (root / "same.py").write_text(
                "value = 1\n", encoding="utf-8"
            ),
            provider_side_effect=lambda root: (root / "same.py").write_text(
                "value = 1\n", encoding="utf-8"
            ),
        )

        self.assertEqual(updated.status, "verification_failed")
        target = record["verification_result"]["causal_change_targets"][0]
        self.assertEqual(target["sha256_before"], target["sha256_after"])

    def test_new_target_creation_passes(self):
        task = self._task(
            "task_phase92_created",
            files_in_scope=["created.py"],
            requires_causal_change=True,
        )

        updated, record, _ = self._run(
            task,
            provider_side_effect=lambda root: (root / "created.py").write_text(
                "value = 1\n", encoding="utf-8"
            ),
        )

        self.assertEqual(updated.status, "completed")
        verification = record["verification_result"]
        self.assertTrue(verification["causal_change_passed"])
        self.assertEqual(verification["changed_targets"], ["created.py"])
        target = verification["causal_change_targets"][0]
        self.assertFalse(target["existed_before"])
        self.assertTrue(target["existed_after"])

    def test_existing_target_hash_change_passes(self):
        task = self._task(
            "task_phase92_modified",
            files_in_scope=["modified.py"],
            requires_causal_change=True,
        )

        updated, record, _ = self._run(
            task,
            prepare=lambda root: (root / "modified.py").write_text(
                "value = 1\n", encoding="utf-8"
            ),
            provider_side_effect=lambda root: (root / "modified.py").write_text(
                "value = 2\n", encoding="utf-8"
            ),
        )

        self.assertEqual(updated.status, "completed")
        target = record["verification_result"]["causal_change_targets"][0]
        self.assertTrue(target["existed_before"])
        self.assertTrue(target["existed_after"])
        self.assertNotEqual(target["sha256_before"], target["sha256_after"])

    def test_empty_scope_cannot_complete_when_causal_change_is_required(self):
        task = self._task(
            "task_phase92_empty_scope",
            files_in_scope=[],
            requires_causal_change=True,
        )

        updated, record, _ = self._run(task)

        self.assertEqual(updated.status, "verification_failed")
        verification = record["verification_result"]
        self.assertFalse(verification["causal_change_passed"])
        self.assertEqual(verification["causal_change_targets"], [])

    def test_verifier_record_binds_artifact_and_causal_evidence(self):
        task = self._task(
            "task_phase92_record",
            files_in_scope=["record.py"],
            requires_causal_change=True,
        )

        updated, record, _ = self._run(
            task,
            provider_side_effect=lambda root: (root / "record.py").write_text(
                "value = 1\n", encoding="utf-8"
            ),
        )

        self.assertEqual(updated.status, "completed")
        self.assertEqual(record["execution_artifact_id"], updated.execution_artifact_id)
        verification = record["verification_result"]
        self.assertEqual(
            verification["execution_artifact_id"],
            updated.execution_artifact_id,
        )
        self.assertTrue(verification["causal_change_required"])
        self.assertTrue(verification["causal_change_passed"])
        self.assertEqual(verification["changed_targets"], ["record.py"])
        self.assertNotIn("content", verification["causal_change_targets"][0])

    def test_default_task_preserves_state_only_verification(self):
        task = self._task(
            "task_phase92_default",
            files_in_scope=["existing.py"],
            requires_causal_change=False,
        )

        updated, record, _ = self._run(
            task,
            prepare=lambda root: (root / "existing.py").write_text(
                "value = 1\n", encoding="utf-8"
            ),
        )

        self.assertEqual(updated.status, "completed")
        verification = record["verification_result"]
        self.assertTrue(verification["overall_passed"])
        self.assertFalse(verification["causal_change_required"])
        self.assertNotIn("causal_change_passed", verification)

    def test_provider_failure_precedes_causal_verification_failure(self):
        task = self._task(
            "task_phase92_provider_failure",
            files_in_scope=["missing.py"],
            requires_causal_change=True,
        )

        updated, record, _ = self._run(task, provider_status="error")

        self.assertEqual(updated.status, "execution_failed")
        self.assertFalse(record["verification_result"]["causal_change_passed"])


if __name__ == "__main__":
    unittest.main()
