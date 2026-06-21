import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.paths as project_paths
import orchestrator.run_manager as run_manager
from orchestrator import engine
from orchestrator.task_schema import Task
from providers.local_file_provider import LocalFileProvider


class Phase94PathAndRecordIdentityContainmentTests(unittest.TestCase):
    def _task(self, task_id: str, files_in_scope: list[str] | None = None) -> Task:
        return Task(
            id=task_id,
            run_id="run_phase94",
            title="Contain paths and record identities",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Keep filesystem access inside declared stores."],
            files_in_scope=files_in_scope or [],
            retry_count=0,
            expected_output="phase 94 output\n",
        )

    def test_unsafe_task_ids_cannot_save_or_load_outside_tasks_dir(self):
        unsafe_ids = [
            "",
            " task",
            "task ",
            "../escape",
            "..\\escape",
            "/tmp/escape",
            "C:\\escape",
            ".",
            "..",
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks_dir = root / "tasks"
            outside = root / "escape.json"
            outside.write_text("outside", encoding="utf-8")

            with patch.object(run_manager, "TASKS_DIR", tasks_dir):
                for task_id in unsafe_ids:
                    with self.subTest(task_id=task_id):
                        with self.assertRaises(ValueError):
                            run_manager.save_task(self._task(task_id))
                        with self.assertRaises(ValueError):
                            run_manager.load_task(task_id)

            self.assertEqual(outside.read_text(encoding="utf-8"), "outside")
            self.assertFalse(tasks_dir.exists())

    def test_unsafe_artifact_ids_cannot_resolve_outside_artifacts_dir(self):
        unsafe_ids = [
            "",
            " artifact",
            "artifact ",
            "../escape",
            "..\\escape",
            "/tmp/escape",
            "C:\\escape",
            ".",
            "..",
        ]
        with tempfile.TemporaryDirectory() as directory:
            artifacts_dir = Path(directory) / "artifacts"
            with patch.object(artifact_store, "ARTIFACTS_DIR", artifacts_dir):
                for artifact_id in unsafe_ids:
                    with self.subTest(artifact_id=artifact_id):
                        with self.assertRaises(ValueError):
                            artifact_store.artifact_path(artifact_id)

                safe_path = artifact_store.artifact_path("artifact_phase94.safe-1")

            self.assertEqual(safe_path.parent, artifacts_dir.resolve())
            self.assertEqual(safe_path.name, "artifact_phase94.safe-1.json")

    def test_declared_absolute_path_is_rejected_by_normal_verification(self):
        task = self._task("task_phase94_absolute", ["/tmp/phase94-outside.txt"])
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(project_paths, "PROJECT_ROOT", Path(directory)):
                with self.assertRaises(ValueError):
                    engine._verify_task_outputs(task)

    def test_declared_parent_traversal_is_rejected_by_normal_verification(self):
        task = self._task("task_phase94_parent", ["../phase94-outside.txt"])
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(project_paths, "PROJECT_ROOT", Path(directory)):
                with self.assertRaises(ValueError):
                    engine._verify_task_outputs(task)

    def test_safe_relative_declared_file_still_verifies(self):
        task = self._task("task_phase94_safe", ["nested/safe.txt"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "nested" / "safe.txt"
            target.parent.mkdir(parents=True)
            target.write_text("safe", encoding="utf-8")

            with patch.object(project_paths, "PROJECT_ROOT", root):
                result = engine._verify_task_outputs(task)

            self.assertTrue(result.overall_passed)
            self.assertEqual(
                project_paths.resolve_declared_project_path("nested/safe.txt"),
                (project_paths.PROJECT_ROOT / "nested" / "safe.txt").resolve(),
            )

    def test_local_file_provider_uses_shared_bounded_resolution(self):
        provider = LocalFileProvider()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(project_paths, "PROJECT_ROOT", root):
                safe_task = self._task("task_phase94_provider_safe", ["output/safe.txt"])
                safe_result = provider.execute("coder", safe_task)
                absolute_result = provider.execute(
                    "coder",
                    self._task("task_phase94_provider_absolute", [str(root.parent / "outside.txt")]),
                )
                traversal_result = provider.execute(
                    "coder",
                    self._task("task_phase94_provider_parent", ["../outside.txt"]),
                )

            self.assertEqual(safe_result["status"], "success")
            self.assertEqual((root / "output" / "safe.txt").read_text(encoding="utf-8"), "phase 94 output\n")
            self.assertEqual(absolute_result["status"], "error")
            self.assertIn("must be relative", absolute_result["error"])
            self.assertEqual(traversal_result["status"], "error")
            self.assertIn("parent traversal", traversal_result["error"])
            self.assertFalse((root.parent / "outside.txt").exists())


if __name__ == "__main__":
    unittest.main()
