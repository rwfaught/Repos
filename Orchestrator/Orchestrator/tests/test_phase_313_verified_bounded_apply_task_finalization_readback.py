import unittest

from orchestrator.verified_bounded_apply_task_finalization import (
    finalize_verified_bounded_apply_task,
    read_verified_bounded_apply_task_finalization_status,
)
from tests.test_phase_311_verified_bounded_apply_task_finalization_record import (
    Phase311VerifiedBoundedApplyTaskFinalizationRecordTests,
)


class Phase313VerifiedBoundedApplyTaskFinalizationReadbackTests(
    Phase311VerifiedBoundedApplyTaskFinalizationRecordTests
):
    def _record(self):
        return finalize_verified_bounded_apply_task(
            verification_record=self._verified(),
            finalization_note="Finalize under mechanical verification evidence only.",
            persist=False,
        )

    def test_readback_shows_finalization_status_and_links(self):
        record = self._record()

        readback = read_verified_bounded_apply_task_finalization_status(
            finalization_record=record
        )

        self.assertTrue(readback["verified_bounded_apply_task_finalization_readback_surface"])
        self.assertEqual(readback["finalization_id"], record["finalization_id"])
        self.assertEqual(readback["finalization_status"], "finalization_record_persisted")
        self.assertEqual(readback["verification_id"], record["verification_id"])
        self.assertEqual(readback["apply_attempt_id"], record["apply_attempt_id"])
        self.assertEqual(readback["authorization_id"], record["authorization_id"])
        self.assertEqual(readback["draft_proposal_id"], "draft_phase303")
        self.assertEqual(readback["candidate_id"], "candidate_phase303")
        refs = readback["packet_task_artifact_verifier_current_success_references"]
        self.assertEqual(refs["packet_id"], "packet_phase303")
        self.assertEqual(refs["task_id"], "task_phase303")
        self.assertEqual(refs["execution_artifact_id"], "artifact_phase303")
        self.assertEqual(refs["verifier_result_path"], "data/verifier_results/phase303.json")
        self.assertEqual(readback["files_mechanically_verified"], ["src/phase303.txt"])
        self.assertEqual(
            readback["operator_or_system_finalization_note"],
            "Finalize under mechanical verification evidence only.",
        )

    def test_readback_preserves_non_proofs(self):
        readback = read_verified_bounded_apply_task_finalization_status(
            finalization_record=self._record()
        )

        self.assertTrue(readback["semantic_correctness_not_proven"])
        self.assertTrue(readback["production_readiness_not_proven"])
        self.assertTrue(readback["model_provider_runtime_not_proven"])
        self.assertTrue(readback["autonomous_ai_coding_not_proven"])
        self.assertTrue(readback["backbone_v0_not_declared"])
        self.assertIn("finalization_is_not_semantic_correctness", readback["non_proofs"])

    def test_readback_missing_finalization_id_blocks(self):
        readback = read_verified_bounded_apply_task_finalization_status(
            "missing_phase313_finalization"
        )

        self.assertEqual(readback["finalization_status"], "finalization_blocked")
        self.assertEqual(readback["reason_code"], "finalization_record_missing")
        self.assertTrue(readback["semantic_correctness_not_proven"])

    def test_readback_selects_latest_matching_finalization(self):
        old = {
            "artifact_type": "verified_bounded_apply_task_finalization",
            "finalization_id": "finalization_phase313_old",
            "finalization_status": "finalization_record_persisted",
            "reason_code": "old",
            "verification_id": "verification_phase313",
            "apply_attempt_id": "attempt_phase313",
            "authorization_id": "authorization_phase313",
            "draft_proposal_id": "draft_phase313",
            "candidate_id": "candidate_phase313",
            "packet_task_artifact_verifier_current_success_references": {"task_id": "task_old"},
            "files_mechanically_verified": [],
            "operator_or_system_finalization_note": "old",
            "semantic_correctness_not_proven": True,
            "production_readiness_not_proven": True,
            "model_provider_runtime_not_proven": True,
            "autonomous_ai_coding_not_proven": True,
            "backbone_v0_not_declared": True,
            "timestamp": "2026-07-02T01:00:00+00:00",
            "caveats": [],
            "non_proofs": [],
        }
        new = {
            **old,
            "finalization_id": "finalization_phase313_new",
            "reason_code": "new",
            "files_mechanically_verified": ["src/phase313.txt"],
            "timestamp": "2026-07-02T02:00:00+00:00",
        }

        readback = read_verified_bounded_apply_task_finalization_status(
            finalization_records=[old, new],
            verification_id="verification_phase313",
            apply_attempt_id="attempt_phase313",
        )

        self.assertEqual(readback["finalization_id"], "finalization_phase313_new")
        self.assertEqual(readback["files_mechanically_verified"], ["src/phase313.txt"])

    def test_readback_filter_mismatch_blocks(self):
        readback = read_verified_bounded_apply_task_finalization_status(
            finalization_record=self._record(),
            verification_id="verification_other_phase313",
        )

        self.assertEqual(readback["finalization_status"], "finalization_blocked")
        self.assertEqual(readback["reason_code"], "finalization_record_missing")
        self.assertTrue(readback["backbone_v0_not_declared"])


if __name__ == "__main__":
    unittest.main()
