import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import orchestrator.packet_cli_residue_guard as residue_guard
import orchestrator.paths as project_paths
from orchestrator.operator_coding_task_packet_cli import main
from orchestrator.packet_cli_residue_guard import inspect_packet_cli_generated_residue


class Phase284PacketCliPreRunResidueGuardTests(unittest.TestCase):
    def test_clean_repo_generated_residue_free_case_reports_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = inspect_packet_cli_generated_residue(root)

        self.assertTrue(result["packet_cli_generated_residue_guard_surface"])
        self.assertFalse(result["residue_present"])
        self.assertEqual(result["generated_paths"], [])
        self.assertTrue(result["report_only"])
        self.assertFalse(result["cleanup_performed"])
        self.assertFalse(result["delete_performed"])
        self.assertFalse(result["archive_performed"])
        self.assertFalse(result["cleanup_authority_claimed"])

    def test_known_generated_residue_reports_exact_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "outputs" / "phase277_golden_smoke.txt"
            output.parent.mkdir(parents=True)
            output.write_text("generated", encoding="utf-8")
            result = inspect_packet_cli_generated_residue(root)

        self.assertTrue(result["residue_present"])
        self.assertEqual(result["generated_paths"], ["outputs/phase277_golden_smoke.txt"])
        self.assertEqual(result["residue_classes"]["outputs"], ["outputs/phase277_golden_smoke.txt"])

    def test_multiple_residue_classes_all_surfaced_without_deletion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [
                root / "outputs" / "phase280.txt",
                root / "data" / "tasks" / "task_phase277_golden_smoke.json",
                root / "data" / "artifacts" / "artifact_phase277.json",
                root / "data" / "verifier_results" / "task_phase277_20260701T000000000000Z.json",
            ]
            for path in paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("generated", encoding="utf-8")
            (root / "data" / "tasks" / ".gitkeep").write_text("", encoding="utf-8")

            result = inspect_packet_cli_generated_residue(root)

            self.assertTrue(result["residue_present"])
            self.assertEqual(
                result["generated_paths"],
                [
                    "data/artifacts/artifact_phase277.json",
                    "data/tasks/task_phase277_golden_smoke.json",
                    "data/verifier_results/task_phase277_20260701T000000000000Z.json",
                    "outputs/phase280.txt",
                ],
            )
            self.assertTrue(all(path.exists() for path in paths))
            self.assertNotIn("data/tasks/.gitkeep", result["generated_paths"])

    def test_guard_does_not_claim_cleanup_or_provider_runtime_activity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "outputs").mkdir()
            (root / "outputs" / "phase280.txt").write_text("generated", encoding="utf-8")

            result = inspect_packet_cli_generated_residue(root)

        self.assertFalse(result["no_activity_flags"]["cleanup_performed"])
        self.assertFalse(result["no_activity_flags"]["delete_performed"])
        self.assertFalse(result["no_activity_flags"]["archive_performed"])
        self.assertFalse(result["no_activity_flags"]["model_executed"])
        self.assertFalse(result["no_activity_flags"]["runtime_executed"])
        self.assertFalse(result["no_activity_flags"]["platform_invoked"])
        self.assertFalse(result["no_activity_flags"]["live_provider_invoked"])
        self.assertIn("no_cleanup_delete_archive_authority", result["non_proofs"])
        self.assertIn("no_live_provider_model_proof", result["non_proofs"])

    def test_cli_residue_guard_prints_deterministic_json_without_packet_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "outputs" / "phase284.txt"
            output.parent.mkdir(parents=True)
            output.write_text("generated", encoding="utf-8")

            with patch.object(project_paths, "PROJECT_ROOT", root), \
                 patch.object(residue_guard, "PROJECT_ROOT", root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["--residue-guard"])
                payload = json.loads(stdout.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["packet_cli_generated_residue_guard_surface"])
        self.assertEqual(payload["generated_paths"], ["outputs/phase284.txt"])
        self.assertFalse(payload["no_activity_flags"]["model_executed"])


if __name__ == "__main__":
    unittest.main()
