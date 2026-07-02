import unittest

from orchestrator.verified_bounded_apply_task_finalization import (
    FINALIZATION_BLOCKED,
    FINALIZATION_COMPLETED,
    finalize_verified_bounded_apply_task,
    load_verified_bounded_apply_task_finalization,
)
from tests.test_phase_307_authorized_bounded_apply_result_verification import (
    Phase307AuthorizedBoundedApplyResultVerificationTests,
)


class Phase311VerifiedBoundedApplyTaskFinalizationRecordTests(
    Phase307AuthorizedBoundedApplyResultVerificationTests
):
    def _verified(self):
        _target, _authorization, _attempt, verification = self._verified_attempt()
        return verification

    def _finalize(self, verification=None, **kwargs):
        return finalize_verified_bounded_apply_task(
            verification_record=verification or self._verified(),
            finalization_note=kwargs.pop(
                "finalization_note",
                "Finalize under mechanical verification evidence only.",
            ),
            **kwargs,
        )

    def test_mechanically_verified_apply_result_persists_finalization_record(self):
        finalization = self._finalize()

        self.assertTrue(finalization["finalization_created"])
        self.assertEqual(finalization["finalization_status"], FINALIZATION_COMPLETED)
        self.assertEqual(
            load_verified_bounded_apply_task_finalization(finalization["finalization_id"]),
            finalization,
        )

    def test_finalization_links_to_full_evidence_chain(self):
        verification = self._verified()
        finalization = self._finalize(verification)
        refs = finalization["packet_task_artifact_verifier_current_success_references"]

        self.assertEqual(finalization["verification_id"], verification["verification_id"])
        self.assertEqual(finalization["apply_attempt_id"], verification["apply_attempt_id"])
        self.assertEqual(finalization["authorization_id"], verification["authorization_id"])
        self.assertEqual(finalization["draft_proposal_id"], "draft_phase303")
        self.assertEqual(finalization["candidate_id"], "candidate_phase303")
        self.assertEqual(refs["packet_id"], "packet_phase303")
        self.assertEqual(refs["task_id"], "task_phase303")
        self.assertEqual(refs["execution_artifact_id"], "artifact_phase303")
        self.assertEqual(refs["verifier_result_path"], "data/verifier_results/phase303.json")
        self.assertEqual(refs["operator_decision_record_id"], "decision_phase303")
        self.assertEqual(finalization["files_mechanically_verified"], ["src/phase303.txt"])

    def test_missing_verification_blocks(self):
        result = finalize_verified_bounded_apply_task(
            finalization_note="Finalize under mechanical verification evidence only."
        )

        self.assertEqual(result["finalization_status"], FINALIZATION_BLOCKED)
        self.assertEqual(result["reason_code"], "verification_record_missing")

    def test_verification_failed_blocks(self):
        verification = {**self._verified(), "verification_status": "verification_failed"}

        result = self._finalize(verification)

        self.assertEqual(result["reason_code"], "verification_not_mechanically_verified")
        self.assertFalse(result["finalization_created"])

    def test_verification_blocked_blocks(self):
        verification = {**self._verified(), "verification_status": "verification_blocked"}

        result = self._finalize(verification)

        self.assertEqual(result["reason_code"], "verification_not_mechanically_verified")

    def test_missing_apply_attempt_link_blocks(self):
        verification = {**self._verified(), "apply_attempt_id": ""}

        result = self._finalize(verification)

        self.assertEqual(result["reason_code"], "apply_attempt_id_missing")

    def test_missing_authorization_link_blocks(self):
        verification = {**self._verified(), "authorization_id": ""}

        result = self._finalize(verification)

        self.assertEqual(result["reason_code"], "authorization_id_missing")

    def test_mismatched_draft_candidate_packet_evidence_blocks(self):
        cases = [
            ("phase_294_draft_proposal_id", "draft_other", "draft_proposal_id_mismatch"),
            ("phase_289_candidate_id", "", "phase_289_candidate_id_missing"),
            ("source_packet_id", "", "source_packet_id_missing"),
        ]
        for field, value, reason in cases:
            with self.subTest(field=field):
                verification = self._verified()
                verification["linked_evidence_chain"] = {
                    **verification["linked_evidence_chain"],
                    field: value,
                }
                result = self._finalize(verification)
                self.assertEqual(result["reason_code"], reason)

    def test_unexpected_files_block(self):
        verification = {**self._verified(), "unexpected_files": ["src/unexpected.txt"]}

        result = self._finalize(verification)

        self.assertEqual(result["reason_code"], "unexpected_files_block_finalization")

    def test_unbounded_paths_block(self):
        verification = {**self._verified(), "files_observed": ["../outside.txt"]}

        result = self._finalize(verification)

        self.assertEqual(result["reason_code"], "unbounded_path_blocks_finalization")

    def test_prior_finalization_blocks_duplicate_finalization(self):
        verification = self._verified()

        result = self._finalize(
            verification,
            existing_finalizations=[
                {
                    "verification_id": verification["verification_id"],
                    "apply_attempt_id": verification["apply_attempt_id"],
                }
            ],
        )

        self.assertEqual(result["reason_code"], "prior_finalization_exists")

    def test_missing_finalization_note_blocks(self):
        result = self._finalize(finalization_note=" ")

        self.assertEqual(result["reason_code"], "finalization_note_required")
        self.assertFalse(result["finalization_created"])

    def test_semantic_correctness_claim_remains_non_proof(self):
        verification = {**self._verified(), "semantic_correctness_claimed": True}

        result = self._finalize(verification)

        self.assertEqual(result["reason_code"], "semantic_correctness_claim_is_non_proof")
        self.assertTrue(result["semantic_correctness_not_proven"])

    def test_production_readiness_claim_remains_non_proof(self):
        verification = {**self._verified(), "production_readiness_claimed": True}

        result = self._finalize(verification)

        self.assertEqual(result["reason_code"], "production_readiness_claim_rejected")
        self.assertTrue(result["production_readiness_not_proven"])

    def test_finalization_record_explicitly_preserves_non_proofs(self):
        finalization = self._finalize()

        self.assertTrue(finalization["semantic_correctness_not_proven"])
        self.assertTrue(finalization["production_readiness_not_proven"])
        self.assertTrue(finalization["model_provider_runtime_not_proven"])
        self.assertTrue(finalization["autonomous_ai_coding_not_proven"])
        self.assertTrue(finalization["backbone_v0_not_declared"])
        self.assertIn("finalization_is_not_semantic_correctness", finalization["non_proofs"])

    def test_phase_101_finalization_spine_regression_remains_compatible(self):
        finalization = self._finalize()

        self.assertEqual(
            finalization["reason_code"],
            "mechanically_verified_bounded_apply_task_finalized",
        )
        self.assertIn(
            "phase_101_style_task_state_finalization_not_invoked",
            finalization["caveats"],
        )


if __name__ == "__main__":
    unittest.main()
