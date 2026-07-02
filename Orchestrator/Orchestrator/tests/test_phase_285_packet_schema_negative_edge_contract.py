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
from orchestrator.operator_coding_task_packet import run_operator_coding_task_packet
from orchestrator.operator_coding_task_packet_cli import main
from orchestrator.task_schema import Task


class Phase285PacketSchemaNegativeEdgeContractTests(unittest.TestCase):
    def _packet(self, **overrides):
        packet = {
            "packet_id": "packet_phase285",
            "run_id": "run_phase285",
            "task_id": "task_phase285",
            "title": "Phase 285 packet schema negative contract",
            "files_in_scope": ["outputs/phase285.txt"],
            "success_criteria": ["Produce deterministic output."],
            "expected_output": "PHASE285\n",
            "provider_name": "local_file",
            "execution_policy": "filesystem_mutation",
        }
        packet.update(overrides)
        return packet

    def _patched_project(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        tasks_dir = root / "data" / "tasks"
        artifacts_dir = root / "data" / "artifacts"
        verifier_dir = root / "data" / "verifier_results"
        patches = [
            patch.object(project_paths, "PROJECT_ROOT", root),
            patch.object(run_manager, "TASKS_DIR", tasks_dir),
            patch.object(artifact_store, "ARTIFACTS_DIR", artifacts_dir),
            patch.object(engine, "VERIFIER_RESULTS_DIR", verifier_dir),
            patch.object(result_review, "ARTIFACTS_DIR", artifacts_dir),
            patch.object(result_review, "VERIFIER_RESULTS_DIR", verifier_dir),
        ]
        return temporary, root, tasks_dir, artifacts_dir, verifier_dir, patches

    def _run_cli_with_file_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            packet_path = Path(directory) / "packet.json"
            packet_path.write_text(text, encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--packet-json", str(packet_path)])
            return exit_code, json.loads(stdout.getvalue())

    def _run_direct_blocked(self, packet):
        temporary, _root, _tasks, _artifacts, _verifiers, patches = self._patched_project()
        with temporary:
            with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
                return run_operator_coding_task_packet(packet)

    def assertBlockedShape(self, result, condition):
        self.assertTrue(result.get("blocked"))
        self.assertFalse(result.get("accepted"))
        self.assertIn(condition, result.get("blocked_conditions", []))
        self.assertFalse(result.get("no_activity_flags", {}).get("model_executed"))
        self.assertFalse(result.get("no_activity_flags", {}).get("runtime_executed"))
        self.assertFalse(result.get("no_activity_flags", {}).get("platform_invoked"))
        self.assertIn("no_semantic_correctness_proof", result.get("non_proofs", []))

    def test_cli_malformed_and_non_object_json_have_deterministic_blocked_shape(self):
        malformed_exit, malformed = self._run_cli_with_file_text("{not json")
        array_exit, array_payload = self._run_cli_with_file_text("[]")

        self.assertEqual(malformed_exit, 1)
        self.assertBlockedShape(malformed, "malformed_packet_json")
        self.assertEqual(array_exit, 1)
        self.assertBlockedShape(array_payload, "packet_json_must_be_object")

    def test_direct_non_object_and_missing_required_fields_block(self):
        non_object = run_operator_coding_task_packet(["not", "object"])
        missing = self._run_direct_blocked({"packet_id": "packet_phase285"})

        self.assertBlockedShape(non_object, "packet_must_be_json_object")
        self.assertBlockedShape(missing, "missing_required_packet_fields")
        self.assertIn("task_id", missing["missing_requirements"])

    def test_empty_expected_output_blocks(self):
        result = self._run_direct_blocked(self._packet(expected_output=""))

        self.assertBlockedShape(result, "missing_required_packet_fields")
        self.assertIn("expected_output", result["missing_requirements"])

    def test_reused_task_id_blocks_before_persistence_overwrite(self):
        temporary, _root, tasks_dir, _artifacts, _verifiers, patches = self._patched_project()
        with temporary:
            with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
                tasks_dir.mkdir(parents=True)
                run_manager.save_task(
                    Task(
                        id="task_phase285",
                        run_id="existing_run",
                        title="Existing task",
                        role="coder",
                        status="queued",
                        dependencies=[],
                        success_criteria=["Existing"],
                        files_in_scope=["outputs/existing.txt"],
                        retry_count=0,
                        expected_output="existing",
                    )
                )
                result = run_operator_coding_task_packet(self._packet())

        self.assertBlockedShape(result, "task_id_already_exists")

    def test_declared_path_negative_edges_block(self):
        cases = [
            ("windows_separator", "outputs\\phase285.txt"),
            ("posix_absolute", "/tmp/phase285.txt"),
            ("parent_traversal", "../outside.txt"),
        ]

        for case_name, declared_path in cases:
            with self.subTest(case_name=case_name):
                result = self._run_direct_blocked(self._packet(files_in_scope=[declared_path]))
                self.assertBlockedShape(result, "declared_file_path_invalid")

    def test_provider_runtime_policy_negative_edges_block(self):
        cases = [
            ("provider", self._packet(provider_name="ollama"), "unsupported_provider_name"),
            ("runtime_smuggling", self._packet(runtime="local_runtime"), "provider_model_runtime_platform_request_rejected"),
            ("model_smuggling", self._packet(model_name="qwen"), "provider_model_runtime_platform_request_rejected"),
            ("policy", self._packet(execution_policy="read_only"), "unsupported_execution_policy"),
        ]

        for case_name, packet, condition in cases:
            with self.subTest(case_name=case_name):
                result = self._run_direct_blocked(packet)
                self.assertBlockedShape(result, condition)

    def test_cli_and_direct_function_share_blocked_condition_for_invalid_packet(self):
        packet = self._packet(task_id="bad/task")
        direct = self._run_direct_blocked(packet)

        with tempfile.TemporaryDirectory() as directory:
            packet_path = Path(directory) / "packet.json"
            packet_path.write_text(json.dumps(packet), encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--packet-json", str(packet_path)])
            cli = json.loads(stdout.getvalue())

        self.assertEqual(exit_code, 1)
        self.assertBlockedShape(direct, "task_id_invalid")
        self.assertBlockedShape(cli, "task_id_invalid")
        self.assertEqual(cli["blocked_conditions"], direct["blocked_conditions"])

    def test_no_proof_no_activity_flags_preserved_for_blocked_packet(self):
        result = self._run_direct_blocked(self._packet(platform_name="platform"))

        self.assertBlockedShape(result, "provider_model_runtime_platform_request_rejected")
        self.assertFalse(result["no_activity_flags"]["autonomous_ai_coding_claimed"])
        self.assertFalse(result["no_activity_flags"]["production_readiness_claimed"])
        self.assertFalse(result["no_activity_flags"]["semantic_correctness_claimed"])
        self.assertIn("no_autonomous_ai_coding_proof", result["non_proofs"])
        self.assertIn("no_runtime_platform_proof", result["non_proofs"])


if __name__ == "__main__":
    unittest.main()
