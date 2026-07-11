import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.paths as project_paths
from orchestrator.dispatcher import dispatch_task
from orchestrator.task_schema import Task
from providers.local_file_provider import LocalFileProvider


class Phase79LocalFileProviderTests(unittest.TestCase):
    def _task(self, file_path="demo/phase79_demo.py", expected_output=None):
        return Task(
            id="task_phase79",
            run_id="run_phase79",
            title="Write one bounded Python file",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=[
                "Write the expected content to the declared file in scope.",
                "Do not touch files outside the declared scope.",
            ],
            files_in_scope=[file_path],
            retry_count=0,
            expected_output=expected_output
            or "def phase79_marker():\n    return 'PHASE79_LOCAL_FILE_PROVIDER'\n",
            verification_checks=[
                {
                    "check": "file_contains_text",
                    "target": file_path,
                    "text": "PHASE79_LOCAL_FILE_PROVIDER",
                },
                {
                    "check": "python_syntax",
                    "target": file_path,
                },
            ],
        )

    def test_local_file_provider_writes_expected_output_to_single_scoped_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task = self._task()

            with patch.object(project_paths, "PROJECT_ROOT", root):
                result = LocalFileProvider().execute(role="coder", task=task, context={})
                target = root / "demo" / "phase79_demo.py"

            self.assertEqual(result.get("status"), "success")
            self.assertEqual(result.get("provider"), "local_file")
            self.assertTrue(target.exists())
            self.assertIn("PHASE79_LOCAL_FILE_PROVIDER", target.read_text(encoding="utf-8"))
            self.assertEqual(result.get("output"), task.expected_output)
            self.assertFalse(result.get("metadata", {}).get("runtime_executed"))
            self.assertFalse(result.get("metadata", {}).get("model_executed"))

    def test_dispatcher_routes_local_file_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task = self._task(file_path="phase79_dispatch.py")

            with patch.object(project_paths, "PROJECT_ROOT", root):
                result = dispatch_task(task, provider_name="local_file")
                target = root / "phase79_dispatch.py"

            self.assertEqual(result.get("status"), "success")
            self.assertEqual(result.get("provider"), "local_file")
            self.assertTrue(target.exists())

    def test_local_file_provider_rejects_multiple_files(self):
        task = self._task()
        task.files_in_scope = ["one.py", "two.py"]

        result = LocalFileProvider().execute(role="coder", task=task, context={})

        self.assertEqual(result.get("status"), "error")
        self.assertIn("exactly one file", result.get("error", ""))

    def test_local_file_provider_rejects_parent_traversal(self):
        task = self._task(file_path="../outside.py")

        result = LocalFileProvider().execute(role="coder", task=task, context={})

        self.assertEqual(result.get("status"), "error")
        self.assertEqual(result.get("metadata", {}).get("error_code"), "declared_path_invalid")


if __name__ == "__main__":
    unittest.main()
