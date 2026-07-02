import unittest

from orchestrator.authorized_draft_patch_apply import (
    execute_authorized_draft_patch_apply,
    read_authorized_draft_patch_apply_attempt_status,
)
from tests.test_phase_303_authorized_draft_patch_proposal_bounded_apply_execution import (
    Phase303AuthorizedDraftPatchProposalBoundedApplyExecutionTests,
)


class Phase305AuthorizedBoundedApplyAttemptReadbackTests(
    Phase303AuthorizedDraftPatchProposalBoundedApplyExecutionTests
):
    def test_readback_shows_applied_attempt_status_and_links(self):
        self._target()
        authorization = self._authorization_record()
        attempt = self._attempt(authorization)

        readback = read_authorized_draft_patch_apply_attempt_status(
            attempt["apply_attempt_id"]
        )

        self.assertTrue(readback["authorized_bounded_apply_attempt_readback_surface"])
        self.assertEqual(readback["apply_attempt_id"], attempt["apply_attempt_id"])
        self.assertEqual(readback["draft_proposal_id"], "draft_phase303")
        self.assertEqual(readback["authorization_id"], authorization["authorization_id"])
        self.assertEqual(readback["bounded_apply_status"], "applied")
        self.assertEqual(readback["files_attempted"], ["src/phase303.txt"])
        self.assertEqual(
            readback["reason_code"],
            "bounded_patch_apply_attempt_applied",
        )
        self.assertEqual(
            readback["linked_evidence_chain"]["source_task_id"],
            "task_phase303",
        )

    def test_readback_preserves_not_verified_and_not_finalized_fields(self):
        self._target()
        attempt = self._attempt()

        readback = read_authorized_draft_patch_apply_attempt_status(
            apply_attempt_record=attempt
        )

        self.assertTrue(readback["patch_not_verified"])
        self.assertTrue(readback["not_finalized"])
        self.assertTrue(readback["semantic_correctness_not_proven"])
        self.assertTrue(readback["production_readiness_not_proven"])
        self.assertTrue(readback["no_finalization_in_this_phase"])
        self.assertFalse(readback["verification_satisfied"])
        self.assertFalse(readback["patch_task_finalized"])

    def test_readback_shows_blocked_attempt_reason_without_apply_claims(self):
        blocked = execute_authorized_draft_patch_apply("authorization_missing_phase305")

        readback = read_authorized_draft_patch_apply_attempt_status(
            apply_attempt_record=blocked
        )

        self.assertEqual(readback["bounded_apply_status"], "blocked")
        self.assertEqual(readback["reason_code"], "apply_authorization_record_missing")
        self.assertTrue(readback["patch_not_verified"])
        self.assertTrue(readback["not_finalized"])
        self.assertFalse(readback["provider_executed"])
        self.assertFalse(readback["model_executed"])
        self.assertFalse(readback["runtime_executed"])
        self.assertFalse(readback["platform_invoked"])

    def test_readback_reports_missing_attempt_id_as_blocked(self):
        readback = read_authorized_draft_patch_apply_attempt_status(
            "missing_phase305_attempt"
        )

        self.assertEqual(readback["bounded_apply_status"], "blocked")
        self.assertEqual(readback["reason_code"], "apply_attempt_record_missing")
        self.assertTrue(readback["patch_not_verified"])
        self.assertTrue(readback["not_finalized"])

    def test_readback_selects_latest_matching_attempt_by_timestamp(self):
        old = {
            "artifact_type": "authorized_draft_patch_apply_attempt",
            "apply_attempt_id": "attempt_phase305_old",
            "source_authorization_id": "authorization_phase305",
            "draft_proposal_id": "draft_phase305",
            "apply_status": "blocked",
            "reason_code": "old_block",
            "files_attempted": [],
            "linked_evidence_chain": {"source_task_id": "task_old"},
            "bounded_target_information": {},
            "patch_not_verified": True,
            "not_finalized": True,
            "semantic_correctness_not_proven": True,
            "production_readiness_not_proven": True,
            "no_finalization_in_this_phase": True,
            "timestamp": "2026-07-02T01:00:00+00:00",
            "caveats": [],
            "non_proofs": [],
        }
        new = {
            **old,
            "apply_attempt_id": "attempt_phase305_new",
            "apply_status": "applied",
            "reason_code": "new_applied",
            "files_attempted": ["src/phase305.txt"],
            "timestamp": "2026-07-02T02:00:00+00:00",
        }

        readback = read_authorized_draft_patch_apply_attempt_status(
            apply_attempt_records=[old, new],
            draft_proposal_id="draft_phase305",
            authorization_id="authorization_phase305",
        )

        self.assertEqual(readback["apply_attempt_id"], "attempt_phase305_new")
        self.assertEqual(readback["bounded_apply_status"], "applied")
        self.assertEqual(readback["files_attempted"], ["src/phase305.txt"])

    def test_readback_filter_mismatch_blocks_without_finalization(self):
        attempt = {
            "artifact_type": "authorized_draft_patch_apply_attempt",
            "apply_attempt_id": "attempt_phase305_filter",
            "source_authorization_id": "authorization_phase305",
            "draft_proposal_id": "draft_phase305",
            "apply_status": "applied",
            "reason_code": "bounded_patch_apply_attempt_applied",
            "files_attempted": ["src/phase305.txt"],
            "linked_evidence_chain": {},
            "bounded_target_information": {},
            "patch_not_verified": True,
            "not_finalized": True,
            "semantic_correctness_not_proven": True,
            "production_readiness_not_proven": True,
            "no_finalization_in_this_phase": True,
            "timestamp": "2026-07-02T02:00:00+00:00",
            "caveats": [],
            "non_proofs": [],
        }

        readback = read_authorized_draft_patch_apply_attempt_status(
            apply_attempt_record=attempt,
            draft_proposal_id="draft_other",
        )

        self.assertEqual(readback["bounded_apply_status"], "blocked")
        self.assertEqual(readback["reason_code"], "apply_attempt_record_missing")
        self.assertTrue(readback["patch_not_verified"])
        self.assertTrue(readback["not_finalized"])


if __name__ == "__main__":
    unittest.main()
