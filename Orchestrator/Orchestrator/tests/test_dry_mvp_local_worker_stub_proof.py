import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.dry_mvp_local_worker_stub_proof import (
    BOUNDARY,
    EXPLICIT_NON_PROOFS,
    RECOMMENDED_NEXT_BOUNDARY,
    WORKER_RESULT_CLASSIFICATION,
    run_dry_mvp_local_worker_stub_proof,
)


class DryMvpLocalWorkerStubProofTests(unittest.TestCase):
    def _input_packet(self) -> dict:
        return {
            "task_id": "dry-mvp-worker-stub-task",
            "task_title": "Produce deterministic local-worker stub proof",
            "files_in_scope": [
                "orchestrator/dry_mvp_local_worker_stub_proof.py",
                "tests/test_dry_mvp_local_worker_stub_proof.py",
            ],
        }

    def _authorization(self) -> dict:
        return {
            "authorized": True,
            "authorization_text": "Operator authorizes deterministic local-worker stub proof only.",
        }

    def test_happy_path_writes_exactly_one_json_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_dry_mvp_local_worker_stub_proof(
                input_packet=self._input_packet(),
                boundary=BOUNDARY,
                operator_authorization=self._authorization(),
                output_dir=directory,
            )
            files = sorted(Path(directory).glob("*.json"))

            self.assertEqual(result["proof_status"], "created")
            self.assertTrue(result["artifact_created"])
            self.assertTrue(result["artifact_persisted"])
            self.assertEqual(len(files), 1)

            persisted = json.loads(files[0].read_text(encoding="utf-8"))

        self.assertEqual(persisted["artifact_id"], result["artifact_id"])
        self.assertEqual(persisted["boundary"], BOUNDARY)
        self.assertEqual(persisted["packet_name"], "dry_mvp_local_worker_stub_proof")

    def test_artifact_contains_required_proof_identity_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_dry_mvp_local_worker_stub_proof(
                input_packet=self._input_packet(),
                boundary=BOUNDARY,
                operator_authorization=self._authorization(),
                output_dir=directory,
            )
        artifact = result["artifact"]

        self.assertEqual(artifact["artifact_kind"], "dry_mvp_deterministic_local_worker_stub_proof")
        self.assertEqual(artifact["boundary"], BOUNDARY)
        self.assertEqual(artifact["input_task_id"], "dry-mvp-worker-stub-task")
        self.assertEqual(
            artifact["input_task_title"],
            "Produce deterministic local-worker stub proof",
        )
        self.assertEqual(artifact["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)

    def test_worker_ran_flag_is_true_only_for_deterministic_local_stub(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_dry_mvp_local_worker_stub_proof(
                input_packet=self._input_packet(),
                boundary=BOUNDARY,
                operator_authorization=self._authorization(),
                output_dir=directory,
            )

        self.assertTrue(result["worker_ran"])
        self.assertEqual(result["worker_kind"], "deterministic_local_worker_stub")
        self.assertEqual(result["worker_result_classification"], WORKER_RESULT_CLASSIFICATION)
        self.assertTrue(result["artifact"]["worker_result"]["worker_ran"])
        self.assertEqual(
            result["artifact"]["worker_result"]["worker_kind"],
            "deterministic_local_worker_stub",
        )

    def test_external_execution_and_overclaim_flags_are_false(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_dry_mvp_local_worker_stub_proof(
                input_packet=self._input_packet(),
                boundary=BOUNDARY,
                operator_authorization=self._authorization(),
                output_dir=directory,
            )

        for flag in (
            "provider_model_executed",
            "local_model_executed",
            "runtime_executed",
            "platform_executed",
            "subprocess_executed",
            "codex_dispatched",
            "file_mutation_executed",
            "production_task_executed",
            "semantic_correctness_proven",
            "production_readiness_claimed",
            "phase_387_implemented",
            "product_wedge_selected",
        ):
            self.assertIs(result[flag], False, flag)
            self.assertIs(result["artifact"]["activity_flags"][flag], False, flag)

    def test_explicit_non_proofs_are_present(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_dry_mvp_local_worker_stub_proof(
                input_packet=self._input_packet(),
                boundary=BOUNDARY,
                operator_authorization=self._authorization(),
                output_dir=directory,
            )

        for non_proof in EXPLICIT_NON_PROOFS:
            self.assertIn(non_proof, result["explicit_non_proofs"])
            self.assertIn(non_proof, result["artifact"]["explicit_non_proofs"])
        self.assertIn("no provider/model execution", result["explicit_non_proofs"])
        self.assertIn("no file mutation execution proof", result["explicit_non_proofs"])

    def test_missing_or_wrong_boundary_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_dry_mvp_local_worker_stub_proof(
                input_packet=self._input_packet(),
                boundary="WRONG_BOUNDARY",
                operator_authorization=self._authorization(),
                output_dir=directory,
            )
            files = sorted(Path(directory).glob("*.json"))

        self.assertEqual(result["proof_status"], "blocked")
        self.assertFalse(result["worker_ran"])
        self.assertIn("boundary_mismatch", result["blocked_conditions"])
        self.assertEqual(files, [])

    def test_missing_authorization_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_dry_mvp_local_worker_stub_proof(
                input_packet=self._input_packet(),
                boundary=BOUNDARY,
                operator_authorization=None,
                output_dir=directory,
            )
            files = sorted(Path(directory).glob("*.json"))

        self.assertEqual(result["proof_status"], "blocked")
        self.assertIn("operator_local_worker_authorization_required", result["blocked_conditions"])
        self.assertIn("operator_local_worker_authorization", result["missing_requirements"])
        self.assertEqual(files, [])

    def test_missing_output_directory_blocks(self):
        result = run_dry_mvp_local_worker_stub_proof(
            input_packet=self._input_packet(),
            boundary=BOUNDARY,
            operator_authorization=self._authorization(),
            output_dir=None,
        )

        self.assertEqual(result["proof_status"], "blocked")
        self.assertIn("output_dir_required", result["blocked_conditions"])
        self.assertFalse(result["artifact_persisted"])

    def test_existing_artifact_blocks_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            first = run_dry_mvp_local_worker_stub_proof(
                input_packet=self._input_packet(),
                boundary=BOUNDARY,
                operator_authorization=self._authorization(),
                output_dir=directory,
            )
            second = run_dry_mvp_local_worker_stub_proof(
                input_packet=self._input_packet(),
                boundary=BOUNDARY,
                operator_authorization=self._authorization(),
                output_dir=directory,
            )
            files = sorted(Path(directory).glob("*.json"))

        self.assertEqual(first["proof_status"], "created")
        self.assertEqual(second["proof_status"], "blocked")
        self.assertIn("local_worker_stub_proof_artifact_already_exists", second["blocked_conditions"])
        self.assertEqual(len(files), 1)

    def test_malformed_or_minimal_inputs_fail_cleanly(self):
        with tempfile.TemporaryDirectory() as directory:
            non_dict = run_dry_mvp_local_worker_stub_proof(
                input_packet=None,
                boundary=BOUNDARY,
                operator_authorization=self._authorization(),
                output_dir=directory,
            )
            missing_title = run_dry_mvp_local_worker_stub_proof(
                input_packet={"task_id": "task-without-title"},
                boundary=BOUNDARY,
                operator_authorization=self._authorization(),
                output_dir=directory,
            )
            files = sorted(Path(directory).glob("*.json"))

        self.assertEqual(non_dict["proof_status"], "blocked")
        self.assertIn("input_packet_required", non_dict["blocked_conditions"])
        self.assertEqual(missing_title["proof_status"], "blocked")
        self.assertIn("input_packet_missing_required_task_fields", missing_title["blocked_conditions"])
        self.assertIn("task_title", missing_title["missing_requirements"])
        self.assertEqual(files, [])

    def test_returned_dict_and_persisted_json_agree_on_core_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_dry_mvp_local_worker_stub_proof(
                input_packet=self._input_packet(),
                boundary=BOUNDARY,
                operator_authorization=self._authorization(),
                output_dir=directory,
            )
            persisted = json.loads(Path(result["artifact_path"]).read_text(encoding="utf-8"))

        for field in (
            "artifact_id",
            "boundary",
            "packet_name",
            "proof_status",
            "input_task_id",
            "input_task_title",
            "worker_ran",
            "worker_result_classification",
            "recommended_next_boundary",
        ):
            self.assertEqual(persisted[field], result["artifact"][field])


if __name__ == "__main__":
    unittest.main()
