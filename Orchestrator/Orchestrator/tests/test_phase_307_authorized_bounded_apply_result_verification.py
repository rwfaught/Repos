import unittest
from unittest.mock import Mock, patch

from orchestrator.authorized_bounded_apply_result_verification import (
    MECHANICALLY_VERIFIED,
    VERIFICATION_BLOCKED,
    VERIFICATION_FAILED,
    verify_authorized_bounded_apply_result,
)
from tests.test_phase_303_authorized_draft_patch_proposal_bounded_apply_execution import (
    Phase303AuthorizedDraftPatchProposalBoundedApplyExecutionTests,
)


class Phase307AuthorizedBoundedApplyResultVerificationTests(
    Phase303AuthorizedDraftPatchProposalBoundedApplyExecutionTests
):
    def _verified_attempt(self):
        target = self._target()
        authorization = self._authorization_record()
        attempt = self._attempt(authorization)
        verification = verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt,
            authorization_record=authorization,
        )
        return target, authorization, attempt, verification

    def test_applied_attempt_with_bounded_expected_changes_is_mechanically_verified(self):
        _target, authorization, attempt, verification = self._verified_attempt()

        self.assertEqual(verification["verification_status"], MECHANICALLY_VERIFIED)
        self.assertTrue(verification["patch_verified_mechanically"])
        self.assertEqual(verification["apply_attempt_id"], attempt["apply_attempt_id"])
        self.assertEqual(verification["authorization_id"], authorization["authorization_id"])
        self.assertEqual(verification["draft_proposal_id"], "draft_phase303")
        self.assertEqual(verification["files_expected"], ["src/phase303.txt"])
        self.assertEqual(verification["files_observed"], ["src/phase303.txt"])
        self.assertEqual(verification["unexpected_files"], [])

    def test_failed_attempt_with_matching_failure_reason_is_mechanically_verified(self):
        authorization = self._authorization_record()
        attempt = {
            **self._attempt(
                authorization,
                apply_engine=Mock(side_effect=ValueError("expected failure")),
            ),
            "apply_status": "failed",
            "reason_code": "bounded_patch_apply_engine_failed",
        }

        verification = verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt,
            authorization_record=authorization,
        )

        self.assertEqual(verification["verification_status"], MECHANICALLY_VERIFIED)
        self.assertEqual(
            verification["reason_code"],
            "failed_state_preserved:bounded_patch_apply_engine_failed",
        )
        self.assertTrue(verification["patch_verified_mechanically"])

    def test_blocked_attempt_with_matching_block_reason_is_mechanically_verified(self):
        authorization = self._authorization_record()
        attempt = self._attempt(
            authorization,
            existing_apply_attempts=[
                {
                    "source_authorization_id": authorization["authorization_id"],
                    "draft_proposal_id": "draft_phase303",
                }
            ],
        )
        attempt["apply_attempt_id"] = "attempt_phase307_blocked"

        verification = verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt,
            authorization_record=authorization,
        )

        self.assertEqual(verification["verification_status"], MECHANICALLY_VERIFIED)
        self.assertEqual(
            verification["reason_code"],
            "blocked_state_preserved:existing_apply_attempt_rejected",
        )
        self.assertTrue(verification["patch_verified_mechanically"])

    def test_missing_apply_attempt_blocks_verification(self):
        verification = verify_authorized_bounded_apply_result("missing_phase307")

        self.assertEqual(verification["verification_status"], VERIFICATION_BLOCKED)
        self.assertEqual(verification["reason_code"], "apply_attempt_record_missing")

    def test_missing_authorization_link_blocks(self):
        self._target()
        attempt = self._attempt()
        attempt.pop("source_authorization_id")
        attempt.pop("authorization_id")

        verification = verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt
        )

        self.assertEqual(verification["reason_code"], "authorization_link_missing")
        self.assertEqual(verification["verification_status"], VERIFICATION_BLOCKED)

    def test_mismatched_evidence_chain_blocks(self):
        self._target()
        authorization = self._authorization_record()
        attempt = self._attempt(authorization)
        attempt["linked_evidence_chain"] = {
            **attempt["linked_evidence_chain"],
            "source_packet_id": "packet_other",
        }

        verification = verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt,
            authorization_record=authorization,
        )

        self.assertEqual(verification["reason_code"], "source_packet_id_mismatch")
        self.assertEqual(verification["verification_status"], VERIFICATION_BLOCKED)

    def test_unbounded_file_path_blocks(self):
        authorization = self._authorization_record()
        attempt = {
            "artifact_type": "authorized_draft_patch_apply_attempt",
            "apply_attempt_id": "attempt_phase307_unbounded",
            "source_authorization_id": authorization["authorization_id"],
            "draft_proposal_id": "draft_phase303",
            "apply_status": "applied",
            "reason_code": "bounded_patch_apply_attempt_applied",
            "files_attempted": ["../outside.txt"],
            "linked_evidence_chain": self._attempt(authorization)["linked_evidence_chain"],
            "bounded_target_information": {},
            "phase_99_apply_result_reference": {"files_changed": ["../outside.txt"]},
        }

        verification = verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt,
            authorization_record=authorization,
        )

        self.assertEqual(
            verification["reason_code"],
            "unbounded_file_path_blocks_verification",
        )
        self.assertEqual(verification["verification_status"], VERIFICATION_BLOCKED)

    def test_unexpected_changed_file_blocks(self):
        self._target()
        authorization = self._authorization_record()
        attempt = self._attempt(authorization)
        attempt["phase_99_apply_result_reference"]["files_changed"] = [
            "src/phase303.txt",
            "src/unexpected.txt",
        ]

        verification = verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt,
            authorization_record=authorization,
        )

        self.assertEqual(
            verification["reason_code"],
            "unexpected_changed_file_blocks_verification",
        )
        self.assertEqual(verification["unexpected_files"], ["src/unexpected.txt"])

    def test_missing_expected_changed_file_fails_verification(self):
        self._target()
        authorization = self._authorization_record()
        attempt = self._attempt(authorization)
        attempt["phase_99_apply_result_reference"]["files_changed"] = []

        verification = verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt,
            authorization_record=authorization,
        )

        self.assertEqual(
            verification["reason_code"],
            "missing_observed_changed_file_fails_verification",
        )
        self.assertEqual(verification["verification_status"], VERIFICATION_FAILED)

    def test_changed_content_mismatch_fails_verification(self):
        target, authorization, _attempt, verification = self._verified_attempt()
        self.assertEqual(verification["verification_status"], MECHANICALLY_VERIFIED)
        target.write_text("tampered\n", encoding="utf-8")

        reverification = verify_authorized_bounded_apply_result(
            apply_attempt_record=_attempt,
            authorization_record=authorization,
        )

        self.assertEqual(
            reverification["reason_code"],
            "changed_content_mismatch_fails_verification",
        )
        self.assertEqual(reverification["verification_status"], VERIFICATION_FAILED)

    def test_existing_finalization_record_blocks_verification(self):
        _target, authorization, attempt, _verification = self._verified_attempt()

        verification = verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt,
            authorization_record=authorization,
            finalization_records=[
                {
                    "authorization_id": authorization["authorization_id"],
                    "apply_attempt_id": attempt["apply_attempt_id"],
                }
            ],
        )

        self.assertEqual(
            verification["reason_code"],
            "existing_finalization_record_blocks_verification",
        )
        self.assertTrue(verification["not_finalized"])

    def test_semantic_correctness_claim_remains_non_proof(self):
        _target, _authorization, _attempt, verification = self._verified_attempt()

        self.assertTrue(verification["semantic_correctness_not_proven"])
        self.assertFalse(verification["semantic_correctness_claimed"])
        self.assertIn(
            "mechanical_verification_is_not_semantic_correctness",
            verification["non_proofs"],
        )

    def test_production_readiness_claim_remains_non_proof(self):
        _target, _authorization, _attempt, verification = self._verified_attempt()

        self.assertTrue(verification["production_readiness_not_proven"])
        self.assertFalse(verification["production_readiness_claimed"])
        self.assertIn(
            "mechanical_verification_is_not_production_readiness",
            verification["non_proofs"],
        )

    def test_verification_output_explicitly_says_not_finalized(self):
        _target, _authorization, _attempt, verification = self._verified_attempt()

        self.assertTrue(verification["not_finalized"])
        self.assertTrue(verification["no_finalization_in_this_phase"])
        self.assertFalse(verification["patch_task_finalized"])

    def test_no_finalization_function_is_invoked(self):
        with patch(
            "orchestrator.patch_apply_task_finalization.finalize_verified_patch_apply_task"
        ) as finalize:
            _target, _authorization, _attempt, verification = self._verified_attempt()

        finalize.assert_not_called()
        self.assertEqual(verification["verification_status"], MECHANICALLY_VERIFIED)

    def test_phase_100_and_101_spines_are_not_invoked_from_phase_307(self):
        with patch(
            "orchestrator.patch_apply_result_review.review_patch_apply_result"
        ) as review, patch(
            "orchestrator.patch_apply_task_finalization.finalize_verified_patch_apply_task"
        ) as finalize:
            _target, _authorization, _attempt, verification = self._verified_attempt()

        review.assert_not_called()
        finalize.assert_not_called()
        self.assertEqual(verification["verification_status"], MECHANICALLY_VERIFIED)


if __name__ == "__main__":
    unittest.main()
