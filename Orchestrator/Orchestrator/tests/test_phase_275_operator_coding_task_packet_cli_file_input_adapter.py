import io
import json
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


class Phase275OperatorCodingTaskPacketCliFileInputAdapterTests(unittest.TestCase):
    def _packet(self, **overrides):
        packet = {
            "packet_id": "packet_phase275",
            "run_id": "run_phase275",
            "task_id": "task_phase275_packet_cli",
            "title": "Operator coding task packet CLI adapter",
            "files_in_scope": ["outputs/phase275.txt"],
            "success_criteria": [
                "Read an operator packet from local JSON.",
                "Print deterministic JSON output for operator review.",
            ],
            "expected_output": "PHASE275 operator packet CLI proof\n",
        }
        packet.update(overrides)
        return packet

    def _write_packet(self, directory: Path, packet):
        packet_path = directory / "packet.json"
        packet_path.write_text(
            json.dumps(packet, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return packet_path

    def _run_cli_in_temp_project(self, packet):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        tasks_dir = root / "data" / "tasks"
        artifacts_dir = root / "data" / "artifacts"
        verifier_dir = root / "data" / "verifier_results"
        packet_path = self._write_packet(root, packet)

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
        self.addCleanup(temporary.cleanup)

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--packet-json", str(packet_path)])
        result = json.loads(stdout.getvalue())
        return root, tasks_dir, artifacts_dir, verifier_dir, exit_code, result, stdout.getvalue()

    def test_legacy_cli_packet_requires_explicit_canonical_configuration(self):
        (
            root,
            tasks_dir,
            artifacts_dir,
            verifier_dir,
            exit_code,
            result,
            stdout_text,
        ) = self._run_cli_in_temp_project(self._packet())

        self.assertEqual(exit_code, 1)
        self.assertTrue(stdout_text.endswith("\n"))
        self.assertTrue(result["operator_coding_task_packet_surface"])
        self.assertFalse(result["accepted"])
        self.assertTrue(result["blocked"])
        self.assertIn("explicit_worker_provider_required", result["blocked_conditions"])
        self.assertFalse((root / "outputs" / "phase275.txt").exists())
        self.assertFalse(tasks_dir.exists())
        self.assertFalse(artifacts_dir.exists())
        self.assertFalse(verifier_dir.exists())

        self.assertFalse(result["no_activity_flags"]["model_executed"])
        self.assertFalse(result["no_activity_flags"]["runtime_executed"])
        self.assertFalse(result["no_activity_flags"]["platform_invoked"])
        self.assertFalse(result["no_activity_flags"]["live_provider_invoked"])
        self.assertIn("no_live_provider_model_proof", result["non_proofs"])
        self.assertIn("no_runtime_platform_proof", result["non_proofs"])

    def test_cli_blocks_file_and_json_errors_before_packet_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            malformed_path = root / "malformed.json"
            malformed_path.write_text("{not json", encoding="utf-8")
            array_path = root / "array.json"
            array_path.write_text("[]", encoding="utf-8")

            cases = [
                (
                    "missing_file",
                    root / "missing.json",
                    "packet_json_file_unreadable",
                ),
                ("malformed_json", malformed_path, "malformed_packet_json"),
                ("json_array", array_path, "packet_json_must_be_object"),
            ]

            for case_name, packet_path, condition in cases:
                with self.subTest(case_name=case_name):
                    stdout = io.StringIO()
                    with redirect_stdout(stdout):
                        exit_code = main(["--packet-json", str(packet_path)])
                    result = json.loads(stdout.getvalue())

                    self.assertNotEqual(exit_code, 0)
                    self.assertTrue(result["operator_coding_task_packet_cli_surface"])
                    self.assertFalse(result["accepted"])
                    self.assertTrue(result["blocked"])
                    self.assertIn(condition, result["blocked_conditions"])
                    self.assertFalse(result["no_activity_flags"]["model_executed"])
                    self.assertFalse(result["no_activity_flags"]["runtime_executed"])
                    self.assertFalse(result["no_activity_flags"]["platform_invoked"])
                    self.assertFalse(result["no_activity_flags"]["live_provider_invoked"])
                    self.assertIn("no_semantic_correctness_proof", result["non_proofs"])

    def test_cli_invalid_packets_return_nonzero_without_persistence(self):
        missing_task_id = self._packet()
        del missing_task_id["task_id"]

        invalid_packets = [
            (
                "missing_required_task_id",
                missing_task_id,
                "missing_required_packet_fields",
                "task_id",
            ),
            (
                "unsupported_runtime_request",
                self._packet(runtime="local_runtime"),
                "provider_model_runtime_platform_request_rejected",
                "runtime",
            ),
        ]

        for case_name, packet, condition, missing_requirement in invalid_packets:
            with self.subTest(case_name=case_name):
                _, tasks_dir, artifacts_dir, verifier_dir, exit_code, result, _ = (
                    self._run_cli_in_temp_project(packet)
                )

                self.assertNotEqual(exit_code, 0)
                self.assertTrue(result["operator_coding_task_packet_surface"])
                self.assertFalse(result["accepted"])
                self.assertTrue(result["blocked"])
                self.assertIn(condition, result["blocked_conditions"])
                self.assertIn(missing_requirement, result["missing_requirements"])
                self.assertFalse(tasks_dir.exists())
                self.assertFalse(artifacts_dir.exists())
                self.assertFalse(verifier_dir.exists())


if __name__ == "__main__":
    unittest.main()
