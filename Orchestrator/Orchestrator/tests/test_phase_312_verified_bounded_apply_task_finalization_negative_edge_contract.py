import unittest

from orchestrator.verified_bounded_apply_task_finalization import (
    FINALIZATION_BLOCKED,
    finalize_verified_bounded_apply_task,
)
from tests.test_phase_311_verified_bounded_apply_task_finalization_record import (
    Phase311VerifiedBoundedApplyTaskFinalizationRecordTests,
)


class Phase312VerifiedBoundedApplyTaskFinalizationNegativeEdgeTests(
    Phase311VerifiedBoundedApplyTaskFinalizationRecordTests
):
    def _blocked(self, verification=None, **kwargs):
        return finalize_verified_bounded_apply_task(
            verification_record=verification if verification is not None else self._verified(),
            finalization_note=kwargs.pop(
                "finalization_note",
                "Finalize under mechanical verification evidence only.",
            ),
            persist=False,
            **kwargs,
        )

    def test_missing_verification_returns_deterministic_blocked_shape(self):
        result = finalize_verified_bounded_apply_task(
            finalization_note="Finalize under mechanical verification evidence only.",
            persist=False,
        )

        self.assertEqual(result["finalization_status"], FINALIZATION_BLOCKED)
        self.assertEqual(result["reason_code"], "verification_record_missing")
        self.assertTrue(result["semantic_correctness_not_proven"])

    def test_failed_or_blocked_verification_cannot_finalize(self):
        for status in ("verification_failed", "verification_blocked"):
            with self.subTest(status=status):
                result = self._blocked({**self._verified(), "verification_status": status})
                self.assertEqual(
                    result["reason_code"],
                    "verification_not_mechanically_verified",
                )

    def test_mismatched_verification_id_blocks(self):
        verification = self._verified()

        result = finalize_verified_bounded_apply_task(
            "verification_other_phase312",
            verification_record=verification,
            finalization_note="Finalize under mechanical verification evidence only.",
            persist=False,
        )

        self.assertEqual(result["reason_code"], "verification_id_mismatch")

    def test_mismatched_apply_attempt_authorization_draft_candidate_and_packet_links_block(self):
        cases = [
            ("apply_attempt_id", "", "apply_attempt_id_missing"),
            ("authorization_id", "", "authorization_id_missing"),
            ("draft_proposal_id", "", "draft_proposal_id_missing"),
            ("phase_294_draft_proposal_id", "draft_other", "draft_proposal_id_mismatch"),
            ("phase_289_candidate_id", "", "phase_289_candidate_id_missing"),
            ("source_packet_id", "", "source_packet_id_missing"),
            ("source_task_id", "", "source_task_id_missing"),
            ("source_execution_artifact_id", "", "source_execution_artifact_id_missing"),
            ("source_verifier_result_path", "", "source_verifier_result_path_missing"),
        ]
        for field, value, reason in cases:
            with self.subTest(field=field):
                verification = self._verified()
                if field in verification:
                    verification[field] = value
                else:
                    verification["linked_evidence_chain"] = {
                        **verification["linked_evidence_chain"],
                        field: value,
                    }
                result = self._blocked(verification)
                self.assertEqual(result["reason_code"], reason)

    def test_missing_expected_files_list_blocks(self):
        result = self._blocked({**self._verified(), "files_expected": []})

        self.assertEqual(result["reason_code"], "expected_files_missing")

    def test_unexpected_files_present_blocks(self):
        result = self._blocked(
            {**self._verified(), "unexpected_files": ["src/unexpected.txt"]}
        )

        self.assertEqual(result["reason_code"], "unexpected_files_block_finalization")

    def test_unbounded_path_blocks(self):
        result = self._blocked({**self._verified(), "files_observed": ["../outside.txt"]})

        self.assertEqual(result["reason_code"], "unbounded_path_blocks_finalization")

    def test_prior_or_duplicate_finalization_blocks(self):
        verification = self._verified()
        first = self._blocked(verification)
        self.assertTrue(first["finalization_created"])

        duplicate = self._blocked(
            verification,
            existing_finalizations=[first],
        )

        self.assertEqual(duplicate["reason_code"], "prior_finalization_exists")

    def test_missing_note_blocks(self):
        result = self._blocked(finalization_note="")

        self.assertEqual(result["reason_code"], "finalization_note_required")

    def test_unsupported_finalization_status_blocks(self):
        result = self._blocked(requested_finalization_status="complete_task_now")

        self.assertEqual(result["reason_code"], "unsupported_finalization_status")

    def test_semantic_autonomous_production_provider_and_backbone_smuggling_blocks(self):
        cases = [
            ("semantic_correctness_claimed", True, "semantic_correctness_claim_is_non_proof"),
            ("autonomous_ai_coding_claimed", True, "autonomous_ai_coding_claim_rejected"),
            ("production_readiness_claimed", True, "production_readiness_claim_rejected"),
            ("model_name", "qwen3.6:27b", "provider_model_runtime_platform_claim_rejected"),
            ("backbone_v0_declared", True, "backbone_v0_declaration_rejected"),
        ]
        for field, value, reason in cases:
            with self.subTest(field=field):
                verification = {**self._verified(), field: value}
                result = self._blocked(verification)
                self.assertEqual(result["reason_code"], reason)
                self.assertTrue(result["semantic_correctness_not_proven"])
                self.assertTrue(result["production_readiness_not_proven"])
                self.assertTrue(result["backbone_v0_not_declared"])

    def test_note_smuggling_blocks(self):
        result = self._blocked(finalization_note="This is production ready.")

        self.assertEqual(result["reason_code"], "production_readiness_claim_rejected")

    def test_phase_284_generated_residue_guard_blocks(self):
        verification = self._verified()
        verification["linked_evidence_chain"] = {
            **verification["linked_evidence_chain"],
            "phase_284_generated_residue_guard": {"generated_residue_detected": True},
        }

        result = self._blocked(verification)

        self.assertEqual(
            result["reason_code"],
            "phase_284_generated_residue_guard_reported",
        )

    def test_blocked_record_preserves_caveats_and_non_proofs(self):
        result = self._blocked({**self._verified(), "verification_status": "verification_failed"})

        self.assertFalse(result["finalization_created"])
        self.assertTrue(result["semantic_correctness_not_proven"])
        self.assertTrue(result["production_readiness_not_proven"])
        self.assertTrue(result["model_provider_runtime_not_proven"])
        self.assertTrue(result["backbone_v0_not_declared"])
        self.assertIn("finalization_is_not_semantic_correctness", result["non_proofs"])


if __name__ == "__main__":
    unittest.main()
