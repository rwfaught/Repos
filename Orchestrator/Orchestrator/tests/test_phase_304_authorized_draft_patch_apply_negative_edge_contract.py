import unittest

from orchestrator.draft_patch_proposal_apply_authorization_record import (
    AUTHORIZE_APPLY,
    DEFER_APPLY_AUTHORIZATION,
    REJECT_APPLY_AUTHORIZATION,
)
from orchestrator.authorized_draft_patch_apply import execute_authorized_draft_patch_apply
from tests.test_phase_303_authorized_draft_patch_proposal_bounded_apply_execution import (
    Phase303AuthorizedDraftPatchProposalBoundedApplyExecutionTests,
)


class Phase304AuthorizedDraftPatchApplyNegativeEdgeContractTests(
    Phase303AuthorizedDraftPatchProposalBoundedApplyExecutionTests
):
    def _blocked_attempt(self, authorization=None, **kwargs):
        attempt = self._attempt(authorization=authorization, **kwargs)
        self.assertIn(attempt["apply_status"], {"blocked", "failed"})
        self.assertIsInstance(attempt["reason_code"], str)
        self.assertTrue(attempt["reason_code"])
        self.assertTrue(attempt["patch_not_verified"])
        self.assertTrue(attempt["not_finalized"])
        self.assertTrue(attempt["semantic_correctness_not_proven"])
        self.assertTrue(attempt["production_readiness_not_proven"])
        self.assertFalse(attempt["patch_task_finalized"])
        self.assertFalse(attempt["verification_satisfied"])
        self.assertFalse(attempt["provider_executed"])
        self.assertFalse(attempt["model_executed"])
        self.assertFalse(attempt["runtime_executed"])
        self.assertFalse(attempt["platform_invoked"])
        return attempt

    def test_missing_phase_299_authorization_record_blocks_with_shape(self):
        attempt = execute_authorized_draft_patch_apply("authorization_phase304_missing")
        self.assertEqual(attempt["apply_status"], "blocked")
        self.assertTrue(attempt["patch_not_verified"])
        self.assertTrue(attempt["not_finalized"])

        self.assertEqual(attempt["reason_code"], "apply_authorization_record_missing")

    def test_reject_and_defer_authorizations_block_with_reason_codes(self):
        for decision in (REJECT_APPLY_AUTHORIZATION, DEFER_APPLY_AUTHORIZATION):
            with self.subTest(decision=decision):
                authorization = self._authorization_record(
                    decision=decision,
                    authorization_id=f"authorization_phase304_{decision}",
                )
                attempt = self._blocked_attempt(authorization)

                self.assertEqual(
                    attempt["reason_code"],
                    "apply_authorization_not_authorize_apply",
                )

    def test_latest_reject_or_defer_blocks_even_when_older_authorization_exists(self):
        authorization = self._authorization_record()
        for decision, status in (
            (REJECT_APPLY_AUTHORIZATION, "apply_authorization_rejected"),
            (DEFER_APPLY_AUTHORIZATION, "apply_authorization_deferred"),
        ):
            with self.subTest(decision=decision):
                newer = {
                    **authorization,
                    "authorization_id": f"authorization_phase304_latest_{decision}",
                    "authorization_decision": decision,
                    "authorization_status": status,
                    "timestamp": "2099-01-01T00:00:00+00:00",
                }
                attempt = self._blocked_attempt(
                    authorization,
                    authorization_records=[authorization, newer],
                )

                self.assertEqual(
                    attempt["reason_code"],
                    "latest_apply_authorization_not_active",
                )

    def test_mismatched_authorization_id_blocks(self):
        original = self._authorization_record()
        authorization = {
            **original,
            "authorization_id": "authorization_phase304_other",
        }

        attempt = execute_authorized_draft_patch_apply(
            original["authorization_id"],
            authorization_record=authorization,
        )
        self.assertEqual(attempt["apply_status"], "blocked")

        self.assertEqual(attempt["reason_code"], "authorization_id_mismatch")

    def test_mismatched_candidate_id_blocks(self):
        draft = self._draft(source_candidate_id="candidate_other")
        authorization = self._authorization_record(draft=draft)

        attempt = self._blocked_attempt(authorization)

        self.assertEqual(attempt["reason_code"], "candidate_id_mismatch")

    def test_mismatched_task_packet_artifact_and_current_success_references_block(self):
        cases = [
            ("source_task_id", "candidate_source_task_id_mismatch"),
            ("source_packet_id", "candidate_source_packet_id_mismatch"),
            (
                "source_execution_artifact_id",
                "candidate_source_execution_artifact_id_mismatch",
            ),
            ("current_success_task", "current_success_task_id_mismatch"),
        ]
        for field, reason in cases:
            with self.subTest(field=field):
                if field == "current_success_task":
                    draft = self._draft(
                        current_success_review_reference={
                            "task_id": "task_other",
                            "run_id": "run_phase303",
                            "classification": "completed_current_state_success",
                            "ready_for_operator_review": True,
                        }
                    )
                else:
                    candidate = self._candidate(**{field: "other_reference"})
                    draft = self._draft(candidate=candidate)
                authorization = self._authorization_record(
                    draft=draft,
                    authorization_id=f"authorization_phase304_{field}",
                )

                attempt = self._blocked_attempt(authorization)

                self.assertEqual(attempt["reason_code"], reason)

    def test_missing_phase_296_eligibility_blocks(self):
        authorization = {
            **self._authorization_record(),
            "phase_296_authorization_eligibility_reference": {},
            "eligibility_record": {},
        }

        attempt = self._blocked_attempt(authorization)

        self.assertEqual(attempt["reason_code"], "authorization_eligibility_not_clean")

    def test_missing_structured_patch_payload_and_unsupported_operation_block(self):
        missing = self._authorization_record(
            draft=self._draft(proposed_patch_evidence_payload={})
        )
        unsupported = self._authorization_record(
            draft=self._draft(
                proposed_patch_evidence_payload=self._patch_payload(
                    proposed_changes=[
                        {
                            "operation_id": "unsupported_phase304",
                            "path": "src/phase303.txt",
                            "expected_before": "before",
                            "replacement_after": "after",
                            "unsupported": "delete_tree",
                        }
                    ]
                )
            ),
            authorization_id="authorization_phase304_unsupported",
        )

        self.assertEqual(
            self._blocked_attempt(missing)["reason_code"],
            "structured_patch_payload_missing",
        )
        self.assertEqual(
            self._blocked_attempt(unsupported)["reason_code"],
            "ambiguous_patch_payload_rejected",
        )

    def test_windows_separator_and_absolute_paths_block_before_cleanup_or_write(self):
        for path, reason in (
            ("src\\phase303.txt", "unsafe_patch_path_rejected"),
            ("C:\\outside.txt", "absolute_patch_path_rejected"),
            ("/tmp/outside.txt", "absolute_patch_path_rejected"),
            ("../outside.txt", "path_traversal_rejected"),
        ):
            with self.subTest(path=path):
                target = self._target()
                authorization = self._authorization_record(
                    draft=self._draft(
                        proposed_patch_evidence_payload=self._patch_payload(
                            proposed_changes=[
                                {
                                    "operation_id": "path_phase304",
                                    "path": path,
                                    "expected_before": "before",
                                    "replacement_after": "after",
                                }
                            ]
                        )
                    ),
                    authorization_id=f"authorization_phase304_{abs(hash(path))}",
                )

                attempt = self._blocked_attempt(authorization)

                self.assertEqual(attempt["reason_code"], reason)
                self.assertEqual(target.read_text(encoding="utf-8"), "before\n")

    def test_smuggled_claims_never_become_proofs(self):
        cases = [
            ("model_name", "qwen3.6:27b", "provider_model_runtime_platform_claim_rejected"),
            ("semantic_correctness_claimed", True, "semantic_correctness_claim_is_non_proof"),
            ("autonomous_ai_coding_claimed", True, "autonomous_ai_coding_claim_rejected"),
            ("production_readiness_claimed", True, "production_readiness_claim_rejected"),
            ("patch_task_finalized", True, "finalization_smuggling_rejected"),
            ("verification_satisfied", True, "apply_result_verification_smuggling_rejected"),
        ]
        for field, value, reason in cases:
            with self.subTest(field=field):
                authorization = self._authorization_record(
                    draft=self._draft(**{field: value}),
                    authorization_id=f"authorization_phase304_{field}",
                )

                attempt = self._blocked_attempt(authorization)

                self.assertEqual(attempt["reason_code"], reason)

    def test_existing_apply_attempt_blocks_duplicate_apply(self):
        authorization = self._authorization_record()
        existing = {
            "apply_attempt_id": "attempt_phase304_existing",
            "source_authorization_id": authorization["authorization_id"],
            "draft_proposal_id": authorization["draft_proposal_id"],
            "apply_status": "applied",
        }

        attempt = self._blocked_attempt(
            authorization,
            existing_apply_attempts=[existing],
        )

        self.assertEqual(attempt["reason_code"], "existing_apply_attempt_rejected")

    def test_phase_284_generated_residue_report_blocks_without_deletion(self):
        draft = self._draft(
            phase_284_generated_residue_guard={"generated_residue_detected": True}
        )
        authorization = self._authorization_record(draft=draft)

        attempt = self._blocked_attempt(authorization)

        self.assertEqual(
            attempt["reason_code"],
            "phase_284_generated_residue_guard_reported",
        )

    def test_authorize_apply_success_shape_remains_not_verified_and_not_finalized(self):
        self._target()
        authorization = self._authorization_record(decision=AUTHORIZE_APPLY)

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["apply_status"], "applied")
        self.assertTrue(attempt["patch_not_verified"])
        self.assertTrue(attempt["not_finalized"])
        self.assertFalse(attempt["phase_99_apply_result_reference"]["task_completed"])
        self.assertFalse(
            attempt["phase_99_apply_result_reference"]["verification_satisfied"]
        )


if __name__ == "__main__":
    unittest.main()
