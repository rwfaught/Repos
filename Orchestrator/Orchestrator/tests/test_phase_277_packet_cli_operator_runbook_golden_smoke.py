import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.current_success_result_review as result_review
import orchestrator.paths as project_paths
import orchestrator.run_manager as run_manager
from orchestrator import engine
from orchestrator.operator_coding_task_packet_cli import main


class Phase277PacketCliOperatorRunbookGoldenSmokeTests(unittest.TestCase):
    def _extract_first_json_fence(self, runbook_text):
        match = re.search(r"```json\s*(\{.*?\})\s*```", runbook_text, re.DOTALL)
        self.assertIsNotNone(match, "runbook must contain a fenced JSON packet")
        return json.loads(match.group(1))

    def test_legacy_runbook_is_preserved_but_cannot_execute_implicitly(self):
        repo_root = Path(__file__).resolve().parents[1]
        runbook_path = repo_root / "docs" / "OPERATOR_CODING_TASK_PACKET_CLI_RUNBOOK.md"

        self.assertTrue(runbook_path.exists())
        runbook_text = runbook_path.read_text(encoding="utf-8")
        self.assertIn(
            "python -m orchestrator.operator_coding_task_packet_cli --packet-json <path>",
            runbook_text,
        )
        self.assertIn(
            "Deterministic `local_file` behavior is local filesystem behavior",
            runbook_text,
        )

        packet = self._extract_first_json_fence(runbook_text)
        self.assertEqual(packet["provider_name"], "local_file")
        self.assertNotIn("model_name", packet)
        self.assertNotIn("runtime", packet)
        self.assertNotIn("platform", packet)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks_dir = root / "data" / "tasks"
            artifacts_dir = root / "data" / "artifacts"
            verifier_dir = root / "data" / "verifier_results"
            packet_dir = root / "operator_packet"
            packet_dir.mkdir()
            packet_path = packet_dir / "packet.json"
            packet_path.write_text(
                json.dumps(packet, indent=2, sort_keys=True),
                encoding="utf-8",
            )

            patches = (
                patch.object(project_paths, "PROJECT_ROOT", root),
                patch.object(run_manager, "TASKS_DIR", tasks_dir),
                patch.object(artifact_store, "ARTIFACTS_DIR", artifacts_dir),
                patch.object(engine, "VERIFIER_RESULTS_DIR", verifier_dir),
                patch.object(result_review, "ARTIFACTS_DIR", artifacts_dir),
                patch.object(result_review, "VERIFIER_RESULTS_DIR", verifier_dir),
            )
            for active_patch in patches:
                active_patch.start()
                self.addCleanup(active_patch.stop)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--packet-json", str(packet_path)])
            result = json.loads(stdout.getvalue())

            self.assertEqual(exit_code, 1)
            self.assertTrue(packet_path.exists())
            self.assertTrue(result["operator_coding_task_packet_surface"])
            self.assertFalse(result["accepted"])
            self.assertTrue(result["blocked"])
            self.assertIn("explicit_worker_provider_required", result["blocked_conditions"])

            output_path = root / "outputs" / "phase277_golden_smoke.txt"
            self.assertFalse(output_path.exists())
            self.assertFalse(tasks_dir.exists())
            self.assertFalse(artifacts_dir.exists())
            self.assertFalse(verifier_dir.exists())

            no_activity_flags = result["no_activity_flags"]
            for flag_name in (
                "model_executed",
                "runtime_executed",
                "platform_invoked",
                "live_provider_invoked",
                "ollama_invoked",
                "openclaw_invoked",
                "hermes_invoked",
                "discord_invoked",
                "installer_invoked",
                "autonomous_ai_coding_claimed",
                "production_readiness_claimed",
                "semantic_correctness_claimed",
            ):
                self.assertFalse(no_activity_flags[flag_name])

            self.assertIn("no_semantic_correctness_proof", result["non_proofs"])
            self.assertIn("no_live_provider_model_proof", result["non_proofs"])
            self.assertIn("no_runtime_platform_proof", result["non_proofs"])
            self.assertIn(
                "local_file_is_deterministic_local_behavior_not_model_backed_generation",
                result["non_proofs"],
            )


if __name__ == "__main__":
    unittest.main()
