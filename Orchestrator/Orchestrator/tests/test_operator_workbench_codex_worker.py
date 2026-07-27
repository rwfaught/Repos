from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from orchestrator import operator_workbench_codex_worker as adapter


class WorkbenchCodexWorkerTests(unittest.TestCase):
    def test_adapter_uses_fixed_binary_and_emits_canonical_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            target = workspace / "workbench_fixtures" / "proof.txt"
            binary = workspace / "codex.exe"
            binary.write_text("test binary", encoding="utf-8")
            payload = {"task_id": "task", "run_id": "run", "objective": "write proof", "expected_output": "exact\n", "success_criteria": ["exact"], "allowed_paths": [str(target)], "worker_workspace": str(workspace), "trust_posture": "trusted_local_unsandboxed"}
            def write_target(command, **_):
                target.parent.mkdir(); target.write_text("exact\n", encoding="utf-8")
                (workspace / ".agents").mkdir()
                (workspace / ".git").write_text("native residue", encoding="utf-8")
                return type("Done", (), {"returncode": 0, "stdout": "done", "stderr": ""})()
            with patch.object(adapter, "CODEX_BINARY", binary), patch("sys.stdin", __import__("io").StringIO(json.dumps(payload))), patch("sys.stdout", __import__("io").StringIO()) as stdout, patch("orchestrator.operator_workbench_codex_worker.subprocess.run", side_effect=write_target) as run:
                self.assertEqual(0, adapter.main())
                result = json.loads(stdout.getvalue())
            self.assertEqual("success", result["status"])
            self.assertEqual([str(target.resolve())], result["changed_paths"])
            self.assertEqual([".agents", ".git"], result["adapter_cleanup"]["known_native_cli_residue_removed"])
            self.assertFalse((workspace / ".agents").exists())
            self.assertFalse((workspace / ".git").exists())
            self.assertEqual(str(binary), run.call_args.args[0][0])
            self.assertEqual(["--ask-for-approval", "never", "exec"], run.call_args.args[0][1:4])
            self.assertIn("--sandbox", run.call_args.args[0])
            self.assertIn("workspace-write", run.call_args.args[0])
            self.assertIn("--ephemeral", run.call_args.args[0])

    def test_adapter_rejects_target_outside_fixture_prefix(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            payload = {"task_id": "task", "run_id": "run", "objective": "write proof", "expected_output": "exact", "allowed_paths": [str(workspace / "other.txt")], "worker_workspace": str(workspace), "trust_posture": "trusted_local_unsandboxed"}
            with patch("sys.stdin", __import__("io").StringIO(json.dumps(payload))), patch("sys.stderr", __import__("io").StringIO()):
                self.assertEqual(1, adapter.main())


if __name__ == "__main__":
    unittest.main()
