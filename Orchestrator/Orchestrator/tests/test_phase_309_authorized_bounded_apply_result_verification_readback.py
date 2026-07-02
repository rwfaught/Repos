import unittest

from orchestrator.authorized_bounded_apply_result_verification import (
    read_authorized_bounded_apply_result_verification_status,
    verify_authorized_bounded_apply_result,
)
from tests.test_phase_307_authorized_bounded_apply_result_verification import (
    Phase307AuthorizedBoundedApplyResultVerificationTests,
)


class Phase309AuthorizedBoundedApplyResultVerificationReadbackTests(
    Phase307AuthorizedBoundedApplyResultVerificationTests
):
    def _verification(self):
        self._target()
        authorization = self._authorization_record()
        attempt = self._attempt(authorization)
        verification = verify_authorized_bounded_apply_result(
            apply_attempt_record=attempt,
            authorization_record=authorization,
        )
        return authorization, attempt, verification

    def test_readback_shows_verification_status_and_links(self):
        authorization, attempt, verification = self._verification()

        readback = read_authorized_bounded_apply_result_verification_status(
            verification_record=verification
        )

        self.assertTrue(
            readback["authorized_bounded_apply_result_verification_readback_surface"]
        )
        self.assertEqual(readback["verification_id"], verification["verification_id"])
        self.assertEqual(readback["apply_attempt_id"], attempt["apply_attempt_id"])
        self.assertEqual(readback["authorization_id"], authorization["authorization_id"])
        self.assertEqual(readback["draft_proposal_id"], "draft_phase303")
        self.assertEqual(readback["verification_status"], "mechanically_verified")
        self.assertEqual(readback["reason_code"], "applied_attempt_mechanically_verified")
        self.assertEqual(readback["files_expected"], ["src/phase303.txt"])
        self.assertEqual(readback["files_observed"], ["src/phase303.txt"])
        self.assertEqual(readback["unexpected_files"], [])
        self.assertTrue(readback["patch_verified_mechanically"])

    def test_readback_preserves_non_proofs_and_not_finalized(self):
        _authorization, _attempt, verification = self._verification()

        readback = read_authorized_bounded_apply_result_verification_status(
            verification_record=verification
        )

        self.assertTrue(readback["semantic_correctness_not_proven"])
        self.assertTrue(readback["production_readiness_not_proven"])
        self.assertTrue(readback["not_finalized"])
        self.assertTrue(readback["no_finalization_in_this_phase"])
        self.assertFalse(readback["patch_task_finalized"])
        self.assertTrue(readback["no_finalization_claimed"])
        self.assertFalse(readback["provider_executed"])
        self.assertFalse(readback["model_executed"])
        self.assertFalse(readback["runtime_executed"])
        self.assertFalse(readback["platform_invoked"])

    def test_readback_reports_missing_verification_id_as_blocked(self):
        readback = read_authorized_bounded_apply_result_verification_status(
            "missing_phase309_verification"
        )

        self.assertEqual(readback["verification_status"], "verification_blocked")
        self.assertEqual(readback["reason_code"], "verification_record_missing")
        self.assertTrue(readback["not_finalized"])

    def test_readback_selects_latest_matching_verification_by_timestamp(self):
        old = {
            "artifact_type": "authorized_bounded_apply_result_verification",
            "verification_id": "verification_phase309_old",
            "apply_attempt_id": "attempt_phase309",
            "authorization_id": "authorization_phase309",
            "draft_proposal_id": "draft_phase309",
            "verification_status": "verification_failed",
            "reason_code": "old_reason",
            "files_expected": [],
            "files_observed": [],
            "unexpected_files": [],
            "patch_verified_mechanically": False,
            "semantic_correctness_not_proven": True,
            "production_readiness_not_proven": True,
            "not_finalized": True,
            "no_finalization_in_this_phase": True,
            "timestamp": "2026-07-02T01:00:00+00:00",
            "caveats": [],
            "non_proofs": [],
        }
        new = {
            **old,
            "verification_id": "verification_phase309_new",
            "verification_status": "mechanically_verified",
            "reason_code": "new_reason",
            "files_expected": ["src/phase309.txt"],
            "files_observed": ["src/phase309.txt"],
            "patch_verified_mechanically": True,
            "timestamp": "2026-07-02T02:00:00+00:00",
        }

        readback = read_authorized_bounded_apply_result_verification_status(
            verification_records=[old, new],
            apply_attempt_id="attempt_phase309",
            authorization_id="authorization_phase309",
            draft_proposal_id="draft_phase309",
        )

        self.assertEqual(readback["verification_id"], "verification_phase309_new")
        self.assertEqual(readback["verification_status"], "mechanically_verified")
        self.assertEqual(readback["files_expected"], ["src/phase309.txt"])

    def test_readback_filter_mismatch_blocks_without_finalization(self):
        _authorization, _attempt, verification = self._verification()

        readback = read_authorized_bounded_apply_result_verification_status(
            verification_record=verification,
            apply_attempt_id="attempt_other_phase309",
        )

        self.assertEqual(readback["verification_status"], "verification_blocked")
        self.assertEqual(readback["reason_code"], "verification_record_missing")
        self.assertTrue(readback["not_finalized"])
        self.assertFalse(readback["patch_task_finalized"])


if __name__ == "__main__":
    unittest.main()
