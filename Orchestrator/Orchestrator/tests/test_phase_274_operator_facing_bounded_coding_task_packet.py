import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.current_success_result_review as result_review
import orchestrator.paths as project_paths
import orchestrator.run_manager as run_manager
from orchestrator import engine
from orchestrator.operator_coding_task_packet import run_operator_coding_task_packet


class Phase274OperatorFacingBoundedCodingTaskPacketTests(unittest.TestCase):
    def _packet(self, **overrides):
        packet = {
            "packet_id": "packet_phase274",
            "run_id": "run_phase274",
            "task_id": "task_phase274_packet",
            "title": "Operator-facing bounded coding task packet",
            "files_in_scope": ["outputs/phase274.txt"],
            "success_criteria": [
                "Write the bounded deterministic Phase 274 output.",
                "Expose current-success readback and next actions.",
            ],
            "expected_output": "PHASE274 operator packet proof\n",
        }
        packet.update(overrides)
        return packet

    def _run_in_temp_project(self, packet):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        tasks_dir = root / "data" / "tasks"
        artifacts_dir = root / "data" / "artifacts"
        verifier_dir = root / "data" / "verifier_results"

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

        result = run_operator_coding_task_packet(packet)
        return root, tasks_dir, artifacts_dir, verifier_dir, result

    def test_legacy_direct_packet_isolated_until_explicit_worker_migration(self):
        root, tasks_dir, artifacts_dir, verifier_dir, result = self._run_in_temp_project(
            self._packet()
        )

        self.assertTrue(result["operator_coding_task_packet_surface"])
        self.assertFalse(result["accepted"])
        self.assertTrue(result["blocked"])
        self.assertIn("explicit_worker_provider_required", result["blocked_conditions"])
        self.assertFalse((root / "outputs" / "phase274.txt").exists())
        self.assertFalse(tasks_dir.exists())
        self.assertFalse(artifacts_dir.exists())
        self.assertFalse(verifier_dir.exists())
        self.assertEqual(
            result["operator_response_surface"],
            "blocked_operator_coding_task_packet_options",
        )

        self.assertFalse(result["no_activity_flags"]["semantic_correctness_claimed"])
        self.assertFalse(result["no_activity_flags"]["model_executed"])
        self.assertFalse(result["no_activity_flags"]["runtime_executed"])
        self.assertFalse(result["no_activity_flags"]["autonomous_ai_coding_claimed"])
        self.assertFalse(result["no_activity_flags"]["production_readiness_claimed"])
        self.assertIn("no_semantic_correctness_proof", result["non_proofs"])
        self.assertIn("no_live_provider_model_proof", result["non_proofs"])

    def test_invalid_packets_block_before_persistence(self):
        missing_task_id = self._packet()
        del missing_task_id["task_id"]

        invalid_packets = [
            (
                "missing_required_task_id",
                missing_task_id,
                "missing_required_packet_fields",
                "task_id",
            ),
            ("empty_task_id", self._packet(task_id=""), None, None),
            ("empty_files_in_scope", self._packet(files_in_scope=[]), None, None),
            ("empty_success_criteria", self._packet(success_criteria=[]), None, None),
            (
                "absolute_path",
                self._packet(files_in_scope=["/tmp/outside.txt"]),
                None,
                None,
            ),
            (
                "parent_traversal_path",
                self._packet(files_in_scope=["../outside.txt"]),
                None,
                None,
            ),
            ("unsupported_provider", self._packet(provider_name="ollama"), None, None),
            (
                "unsupported_model_request",
                self._packet(model_name="qwen3.6:27b"),
                None,
                None,
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
                _, tasks_dir, artifacts_dir, verifier_dir, result = (
                    self._run_in_temp_project(packet)
                )

                self.assertTrue(result["operator_coding_task_packet_surface"])
                self.assertFalse(result["accepted"])
                self.assertTrue(result["blocked"])
                self.assertTrue(result["blocked_conditions"])
                if condition is not None:
                    self.assertIn(condition, result["blocked_conditions"])
                if missing_requirement is not None:
                    self.assertIn(missing_requirement, result["missing_requirements"])
                self.assertFalse(tasks_dir.exists())
                self.assertFalse(artifacts_dir.exists())
                self.assertFalse(verifier_dir.exists())


if __name__ == "__main__":
    unittest.main()
