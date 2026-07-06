import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from orchestrator.dry_mvp_loop_cli import main
from orchestrator.dry_mvp_loop_demo import render_dry_mvp_loop_demo_text, run_dry_mvp_loop_demo


class DryMvpLoopDemoCliTests(unittest.TestCase):
    def test_demo_writes_only_to_caller_supplied_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_dry_mvp_loop_demo(directory)
            files = sorted(Path(directory).rglob("*.json"))

        self.assertEqual(result["demo_status"], "dry_mvp_demo_pass")
        self.assertEqual(result["closeout"]["closeout_decision"], "dry_mvp_loop_closeout_pass")
        self.assertEqual(len(files), 2)
        self.assertTrue(any(path.parent.name == "tasks" for path in files))
        self.assertTrue(any(path.parent.name == "artifacts" for path in files))

    def test_text_render_is_compact_and_status_focused(self):
        with tempfile.TemporaryDirectory() as directory:
            text = render_dry_mvp_loop_demo_text(run_dry_mvp_loop_demo(directory))

        self.assertIn("DRY MVP LOOP DEMO", text)
        self.assertIn("status=dry_mvp_demo_pass", text)
        self.assertIn("closeout=dry_mvp_loop_closeout_pass", text)
        self.assertIn("no real worker execution proof", text)

    def test_cli_text_outputs_success(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["--out-dir", directory, "--format", "text"])

        self.assertEqual(code, 0)
        self.assertIn("status=dry_mvp_demo_pass", output.getvalue())

    def test_cli_json_outputs_parseable_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["--out-dir", directory, "--format", "json"])
            payload = json.loads(output.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["demo_status"], "dry_mvp_demo_pass")
        self.assertEqual(payload["pm_status"]["overall_status"], "dry_mvp_loop_structurally_present")


if __name__ == "__main__":
    unittest.main()
