import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.draft_patch_proposal_apply_authorization_record as record_module
from orchestrator.draft_patch_proposal_apply_authorization_record import (
    AUTHORIZE_APPLY,
    DEFER_APPLY_AUTHORIZATION,
    REJECT_APPLY_AUTHORIZATION,
    create_draft_patch_proposal_apply_authorization_record,
    read_draft_patch_proposal_apply_authorization_status,
)
from tests.test_phase_299_draft_patch_proposal_operator_apply_authorization_record import (
    Phase299DraftPatchProposalOperatorApplyAuthorizationRecordTests,
)


class Phase301PatchApplyAuthorizationReadbackTests(
    Phase299DraftPatchProposalOperatorApplyAuthorizationRecordTests
):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.auth_dir = self.root / "authorizations"
        self.dir_patch = patch.object(
            record_module,
            "DRAFT_PATCH_PROPOSAL_APPLY_AUTHORIZATIONS_DIR",
            self.auth_dir,
        )
        self.dir_patch.start()
        self.addCleanup(self.dir_patch.stop)

    def test_latest_authorized_record_readback_is_active_and_not_applied(self):
        result = self._create()
        readback = read_draft_patch_proposal_apply_authorization_status(
            result["draft_proposal_id"]
        )

        self.assertEqual(readback["authorization_id"], result["authorization_id"])
        self.assertEqual(readback["latest_authorization_decision"], AUTHORIZE_APPLY)
        self.assertTrue(readback["authorization_active"])
        self.assertTrue(readback["patch_not_applied"])
        self.assertTrue(readback["no_apply_execution_in_this_phase"])
        self.assertFalse(readback["patch_applied"])
        self.assertFalse(readback["apply_result_created"])
        self.assertFalse(readback["patch_task_finalized"])

    def test_latest_reject_and_defer_readbacks_are_not_active(self):
        for decision, field in [
            (REJECT_APPLY_AUTHORIZATION, "authorization_rejected"),
            (DEFER_APPLY_AUTHORIZATION, "authorization_deferred"),
        ]:
            with self.subTest(decision=decision):
                result = self._create(
                    decision=decision,
                    authorization_id=f"authorization_phase301_{decision}",
                )
                readback = read_draft_patch_proposal_apply_authorization_status(
                    result["draft_proposal_id"]
                )
                self.assertEqual(readback["latest_authorization_decision"], decision)
                self.assertFalse(readback["authorization_active"])
                self.assertTrue(readback[field])

    def test_readback_reports_latest_record_by_timestamp(self):
        draft = self._draft()
        older = self._create(
            draft=draft,
            authorization_id="authorization_phase301_old",
            authorization_decision=AUTHORIZE_APPLY,
        )
        newer = self._create(
            draft=draft,
            authorization_id="authorization_phase301_new",
            authorization_decision=DEFER_APPLY_AUTHORIZATION,
            authorization_records=[],
        )
        records = [
            {
                **older,
                "artifact_type": "draft_patch_proposal_apply_authorization_record",
                "draft_proposal_id": draft["draft_proposal_id"],
                "timestamp": "2026-07-02T01:00:00+00:00",
            },
            {
                **newer,
                "artifact_type": "draft_patch_proposal_apply_authorization_record",
                "draft_proposal_id": draft["draft_proposal_id"],
                "timestamp": "2026-07-02T02:00:00+00:00",
            },
        ]

        readback = read_draft_patch_proposal_apply_authorization_status(
            draft["draft_proposal_id"],
            authorization_records=records,
        )

        self.assertEqual(readback["authorization_id"], "authorization_phase301_new")
        self.assertTrue(readback["authorization_deferred"])

    def test_missing_authorization_record_readback_is_blocked_without_apply(self):
        readback = read_draft_patch_proposal_apply_authorization_status("draft_missing")

        self.assertTrue(readback["authorization_blocked"])
        self.assertEqual(readback["reason_code"], "apply_authorization_record_missing")
        self.assertTrue(readback["patch_not_applied"])
        self.assertTrue(readback["no_apply_execution_in_this_phase"])
        self.assertFalse(readback["provider_executed"])
        self.assertFalse(readback["model_executed"])
        self.assertFalse(readback["runtime_executed"])
        self.assertFalse(readback["platform_invoked"])


if __name__ == "__main__":
    unittest.main()
