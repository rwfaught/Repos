import unittest

from orchestrator.authorized_bounded_apply_result_verification import (
    MECHANICALLY_VERIFIED,
    VERIFICATION_BLOCKED,
    VERIFICATION_FAILED,
    verify_authorized_bounded_apply_result,
)
from orchestrator.draft_patch_proposal_apply_authorization_record import (
    DEFER_APPLY_AUTHORIZATION,
    REJECT_APPLY_AUTHORIZATION,
)
from tests.test_phase_307_authorized_bounded_apply_result_verification import (
    Phase307AuthorizedBoundedApplyResultVerificationTests,
)


class Phase308AuthorizedBoundedApplyResultVerificationNegativeEdgeTests(
    Phase307AuthorizedBoundedApplyResultVerificationTests
):
    def _applied_case(self):
        self._target()
        authorization = self._authorization_record()
        attempt = self._attempt(authorization)
        return authorization, attempt

    def _verify(self, authorization, attempt, **kwargs):
        return verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt,
            authorization_record=authorization,
            **kwargs,
        )

    def test_missing_authorization_blocks_with_exact_reason(self):
        self._target()
        authorization, attempt = self._applied_case()
        attempt["source_authorization_id"] = "authorization_missing_phase308"

        verification = verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt
        )

        self.assertEqual(verification["verification_status"], VERIFICATION_BLOCKED)
        self.assertEqual(verification["reason_code"], "authorization_link_missing")

    def test_rejected_authorization_blocks(self):
        authorization, attempt = self._applied_case()
        authorization["authorization_decision"] = REJECT_APPLY_AUTHORIZATION
        authorization["authorization_status"] = "apply_authorization_rejected"

        verification = self._verify(authorization, attempt)

        self.assertEqual(verification["reason_code"], "apply_authorization_not_authorize_apply")
        self.assertEqual(verification["verification_status"], VERIFICATION_BLOCKED)

    def test_deferred_or_stale_authorization_blocks(self):
        authorization, attempt = self._applied_case()
        authorization["authorization_decision"] = DEFER_APPLY_AUTHORIZATION
        authorization["authorization_status"] = "apply_authorization_deferred"

        verification = self._verify(authorization, attempt)

        self.assertEqual(verification["reason_code"], "apply_authorization_not_authorize_apply")
        self.assertEqual(verification["verification_status"], VERIFICATION_BLOCKED)

    def test_mismatched_apply_attempt_id_blocks(self):
        authorization, attempt = self._applied_case()

        verification = verify_authorized_bounded_apply_result(
            "attempt_other_phase308",
            apply_attempt_record=attempt,
            authorization_record=authorization,
        )

        self.assertEqual(verification["reason_code"], "apply_attempt_id_mismatch")
        self.assertEqual(verification["verification_status"], VERIFICATION_BLOCKED)

    def test_mismatched_authorization_id_blocks(self):
        authorization, attempt = self._applied_case()
        authorization["authorization_id"] = "authorization_other_phase308"

        verification = self._verify(authorization, attempt)

        self.assertEqual(verification["reason_code"], "authorization_link_missing")

    def test_mismatched_draft_candidate_task_packet_and_current_success_references_block(self):
        cases = [
            ("draft_proposal_id", "draft_other_phase308", "phase_294_draft_proposal_id_mismatch"),
            (
                "candidate_id",
                "candidate_other_phase308",
                "phase_289_candidate_id_mismatch",
            ),
            ("source_packet_id", "packet_other_phase308", "source_packet_id_mismatch"),
            ("source_task_id", "task_other_phase308", "source_task_id_mismatch"),
            (
                "source_execution_artifact_id",
                "artifact_other_phase308",
                "source_execution_artifact_id_mismatch",
            ),
            (
                "source_verifier_result_path",
                "data/verifier_results/other.json",
                "source_verifier_result_path_mismatch",
            ),
        ]
        for field, value, reason in cases:
            with self.subTest(field=field):
                authorization, attempt = self._applied_case()
                chain_key = {
                    "draft_proposal_id": "phase_294_draft_proposal_id",
                    "candidate_id": "phase_289_candidate_id",
                }.get(field, field)
                attempt["linked_evidence_chain"][chain_key] = value
                verification = self._verify(authorization, attempt)
                self.assertEqual(verification["reason_code"], reason)
                self.assertEqual(verification["verification_status"], VERIFICATION_BLOCKED)

    def test_missing_structured_patch_payload_blocks(self):
        authorization, attempt = self._applied_case()
        authorization["phase_294_draft_proposal_reference"]["proposed_patch_evidence_payload"] = {}

        verification = self._verify(authorization, attempt)

        self.assertEqual(verification["reason_code"], "structured_patch_payload_missing")

    def test_ambiguous_patch_payload_blocks(self):
        authorization, attempt = self._applied_case()
        authorization["phase_294_draft_proposal_reference"]["proposed_patch_evidence_payload"] = {
            "proposed_changes": [{"path": "src/phase303.txt"}]
        }

        verification = self._verify(authorization, attempt)

        self.assertEqual(verification["reason_code"], "ambiguous_patch_payload_rejected")

    def test_unbounded_observed_path_blocks(self):
        authorization, attempt = self._applied_case()
        attempt["phase_99_apply_result_reference"]["files_changed"] = ["../outside.txt"]

        verification = self._verify(authorization, attempt)

        self.assertEqual(verification["reason_code"], "unbounded_file_path_blocks_verification")

    def test_unexpected_observed_file_blocks(self):
        authorization, attempt = self._applied_case()
        attempt["phase_99_apply_result_reference"]["files_changed"] = [
            "src/phase303.txt",
            "src/unexpected_phase308.txt",
        ]

        verification = self._verify(authorization, attempt)

        self.assertEqual(verification["reason_code"], "unexpected_changed_file_blocks_verification")
        self.assertEqual(verification["unexpected_files"], ["src/unexpected_phase308.txt"])

    def test_missing_expected_file_fails(self):
        authorization, attempt = self._applied_case()
        attempt["phase_99_apply_result_reference"]["files_changed"] = []

        verification = self._verify(authorization, attempt)

        self.assertEqual(verification["verification_status"], VERIFICATION_FAILED)
        self.assertEqual(verification["reason_code"], "missing_observed_changed_file_fails_verification")

    def test_content_mismatch_fails(self):
        authorization, attempt = self._applied_case()
        (self.root / "src" / "phase303.txt").write_text("tampered\n", encoding="utf-8")

        verification = self._verify(authorization, attempt)

        self.assertEqual(verification["verification_status"], VERIFICATION_FAILED)
        self.assertEqual(verification["reason_code"], "changed_content_mismatch_fails_verification")

    def test_failed_and_blocked_apply_incorrectly_marked_applied_block(self):
        for applied_value, expected_reason in (
            (False, "applied_attempt_lacks_phase_99_applied_evidence"),
            (True, "verification_smuggling_rejected"),
        ):
            with self.subTest(applied_value=applied_value):
                authorization, attempt = self._applied_case()
                attempt["phase_99_apply_result_reference"]["applied"] = applied_value
                attempt["phase_99_apply_result_reference"]["verification_satisfied"] = applied_value
                verification = self._verify(authorization, attempt)
                self.assertEqual(verification["reason_code"], expected_reason)

    def test_existing_finalization_record_blocks_and_preserves_not_finalized(self):
        authorization, attempt = self._applied_case()

        verification = self._verify(
            authorization,
            attempt,
            finalization_records=[{"apply_attempt_id": attempt["apply_attempt_id"]}],
        )

        self.assertEqual(
            verification["reason_code"],
            "existing_finalization_record_blocks_verification",
        )
        self.assertTrue(verification["not_finalized"])

    def test_provider_runtime_platform_smuggling_blocks(self):
        for field in ("provider", "model_name", "runtime", "platform"):
            with self.subTest(field=field):
                authorization, attempt = self._applied_case()
                attempt[field] = "smuggled"
                verification = self._verify(authorization, attempt)
                self.assertEqual(
                    verification["reason_code"],
                    "provider_model_runtime_platform_claim_rejected",
                )

    def test_semantic_autonomous_production_and_finalization_smuggling_blocks(self):
        cases = [
            ("semantic_correctness_claimed", True, "semantic_correctness_claim_is_non_proof"),
            ("autonomous_ai_coding_claimed", True, "autonomous_ai_coding_claim_rejected"),
            ("production_readiness_claimed", True, "production_readiness_claim_rejected"),
            ("patch_task_finalized", True, "finalization_smuggling_rejected"),
        ]
        for field, value, reason in cases:
            with self.subTest(field=field):
                authorization, attempt = self._applied_case()
                attempt[field] = value
                verification = self._verify(authorization, attempt)
                self.assertEqual(verification["reason_code"], reason)
                self.assertTrue(verification["not_finalized"])

    def test_phase_284_generated_residue_report_blocks(self):
        authorization, attempt = self._applied_case()
        authorization["phase_294_draft_proposal_reference"][
            "phase_284_generated_residue_guard"
        ] = {"generated_residue_detected": True}

        verification = self._verify(authorization, attempt)

        self.assertEqual(
            verification["reason_code"],
            "phase_284_generated_residue_guard_reported",
        )

    def test_valid_phase307_case_still_mechanically_verifies(self):
        authorization, attempt = self._applied_case()

        verification = self._verify(authorization, attempt)

        self.assertEqual(verification["verification_status"], MECHANICALLY_VERIFIED)
        self.assertTrue(verification["patch_verified_mechanically"])


if __name__ == "__main__":
    unittest.main()
