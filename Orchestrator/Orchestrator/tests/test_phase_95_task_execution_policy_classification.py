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
from orchestrator.task_schema import (
    FILESYSTEM_MUTATION_EXECUTION_POLICY,
    REPORT_ONLY_EXECUTION_POLICY,
    Task,
    create_task,
    deserialize_task,
    serialize_task,
)


class Phase95TaskExecutionPolicyClassificationTests(unittest.TestCase):
    def _task(self, task_id: str, **overrides) -> Task:
        task = Task(
            id=task_id,
            run_id="run_phase95",
            title="Classify task execution policy",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Preserve bounded execution policy semantics."],
            files_in_scope=[],
            retry_count=0,
            expected_output="phase 95 bounded mutation\n",
        )
        for key, value in overrides.items():
            setattr(task, key, value)
        return task

    def _task_payload(self, **overrides) -> dict:
        payload = {
            "id": "task_phase95_schema",
            "run_id": "run_phase95",
            "title": "Schema policy task",
            "role": "coder",
            "status": "queued",
            "dependencies": [],
            "success_criteria": [],
            "files_in_scope": [],
            "retry_count": 0,
        }
        payload.update(overrides)
        return payload

    def _run(self, task: Task, provider_name: str = "mock"):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        tasks_dir = root / "data" / "tasks"
        artifacts_dir = root / "data" / "artifacts"
        verifier_dir = root / "data" / "verifier_results"
        recommendations_dir = root / "data" / "reviewer_recommendations"

        patches = (
            patch.object(project_paths, "PROJECT_ROOT", root),
            patch.object(run_manager, "TASKS_DIR", tasks_dir),
            patch.object(artifact_store, "ARTIFACTS_DIR", artifacts_dir),
            patch.object(engine, "VERIFIER_RESULTS_DIR", verifier_dir),
            patch.object(
                reviewer_output,
                "REVIEWER_RECOMMENDATIONS_DIR",
                recommendations_dir,
            ),
        )
        for active_patch in patches:
            active_patch.start()
            self.addCleanup(active_patch.stop)
        self.addCleanup(temporary.cleanup)

        run_manager.save_task(task)
        engine.process_task_by_id(run_manager.load_task(task.id), provider_name=provider_name)
        updated = run_manager.load_task(task.id)
        verifier_files = sorted(verifier_dir.glob("*.json"))
        record = (
            json.loads(verifier_files[0].read_text(encoding="utf-8"))
            if verifier_files
            else None
        )
        artifact_files = sorted(artifacts_dir.glob("*.json"))
        artifact = (
            json.loads(artifact_files[0].read_text(encoding="utf-8"))
            if artifact_files
            else None
        )
        return root, updated, record, artifact

    def test_missing_execution_policy_defaults_to_report_only(self):
        task = create_task(self._task_payload())
        self.assertEqual(task.execution_policy, REPORT_ONLY_EXECUTION_POLICY)
        self.assertFalse(task.requires_causal_change)

    def test_report_only_policy_serializes_and_deserializes(self):
        task = create_task(
            self._task_payload(execution_policy=REPORT_ONLY_EXECUTION_POLICY)
        )
        restored = deserialize_task(serialize_task(task))
        self.assertEqual(restored.execution_policy, REPORT_ONLY_EXECUTION_POLICY)
        self.assertFalse(restored.requires_causal_change)

    def test_filesystem_mutation_policy_serializes_and_enforces_causal_change(self):
        task = create_task(
            self._task_payload(
                execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
                requires_causal_change=False,
            )
        )
        restored = deserialize_task(serialize_task(task))
        self.assertEqual(
            restored.execution_policy,
            FILESYSTEM_MUTATION_EXECUTION_POLICY,
        )
        self.assertTrue(restored.requires_causal_change)

    def test_unknown_execution_policy_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown execution_policy"):
            create_task(self._task_payload(execution_policy="unsafe_unknown"))

    def test_filesystem_mutation_with_empty_scope_fails_without_dispatch(self):
        task = self._task(
            "task_phase95_empty",
            execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
            requires_causal_change=False,
        )
        with patch("orchestrator.engine.dispatch_task") as dispatch:
            _, updated, record, artifact = self._run(task)

        dispatch.assert_not_called()
        self.assertEqual(updated.status, "verification_failed")
        self.assertTrue(updated.requires_causal_change)
        self.assertIsNone(artifact)
        self.assertEqual(record["execution_policy"], FILESYSTEM_MUTATION_EXECUTION_POLICY)
        self.assertFalse(record["verification_result"]["overall_passed"])

    def test_filesystem_mutation_with_local_file_change_completes_with_proof(self):
        task = self._task(
            "task_phase95_changed",
            files_in_scope=["outputs/phase95.txt"],
            execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
            requires_causal_change=False,
        )
        root, updated, record, artifact = self._run(task, provider_name="local_file")

        self.assertEqual(updated.status, "completed")
        self.assertTrue(updated.requires_causal_change)
        self.assertEqual(
            (root / "outputs" / "phase95.txt").read_text(encoding="utf-8"),
            task.expected_output,
        )
        verification = record["verification_result"]
        self.assertTrue(verification["causal_change_passed"])
        self.assertEqual(verification["changed_targets"], ["outputs/phase95.txt"])
        self.assertEqual(artifact["execution_policy"], FILESYSTEM_MUTATION_EXECUTION_POLICY)
        self.assertTrue(artifact["requires_causal_change"])

    def test_filesystem_mutation_without_actual_change_cannot_complete(self):
        task = self._task(
            "task_phase95_no_change",
            files_in_scope=["existing.txt"],
            execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "existing.txt"
            target.write_text(task.expected_output, encoding="utf-8")
            with (
                patch.object(project_paths, "PROJECT_ROOT", root),
                patch.object(run_manager, "TASKS_DIR", root / "tasks"),
                patch.object(artifact_store, "ARTIFACTS_DIR", root / "artifacts"),
                patch.object(engine, "VERIFIER_RESULTS_DIR", root / "verifier_results"),
            ):
                run_manager.save_task(task)
                engine.process_task_by_id(
                    run_manager.load_task(task.id),
                    provider_name="local_file",
                )
                updated = run_manager.load_task(task.id)
                record_path = next((root / "verifier_results").glob("*.json"))
                record = json.loads(record_path.read_text(encoding="utf-8"))

        self.assertEqual(updated.status, "verification_failed")
        self.assertFalse(record["verification_result"]["causal_change_passed"])
        self.assertEqual(record["verification_result"]["changed_targets"], [])

    def test_report_only_without_scope_preserves_skipped_verification(self):
        task = self._task(
            "task_phase95_report",
            expected_output=None,
            execution_policy=REPORT_ONLY_EXECUTION_POLICY,
        )
        _, updated, record, artifact = self._run(task)

        self.assertEqual(updated.status, "completed")
        self.assertEqual(artifact["execution_policy"], REPORT_ONLY_EXECUTION_POLICY)
        self.assertTrue(record["verification_result"]["overall_passed"])
        self.assertIn(
            "Verification skipped: no files_in_scope provided.",
            record["verification_result"]["messages"],
        )

    def test_mutation_absolute_and_parent_traversal_targets_are_rejected(self):
        for index, unsafe_target in enumerate(
            ["/tmp/phase95-outside.txt", "../phase95-outside.txt"]
        ):
            with self.subTest(target=unsafe_target):
                task = self._task(
                    f"task_phase95_unsafe_{index}",
                    files_in_scope=[unsafe_target],
                    execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
                )
                with patch("orchestrator.engine.dispatch_task") as dispatch:
                    with self.assertRaises(ValueError):
                        self._run(task)
                dispatch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
