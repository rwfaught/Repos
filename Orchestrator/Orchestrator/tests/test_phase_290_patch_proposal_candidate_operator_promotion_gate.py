import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.patch_proposal_candidate_promotion as promotion_module
from orchestrator.patch_proposal_candidate_promotion import (
    create_patch_proposal_candidate_promotion_record,
    load_patch_proposal_candidate_promotion_record,
)


class Phase290PatchProposalCandidateOperatorPromotionGateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.promotion_dir = self.root / "promotions"
        self.dir_patch = patch.object(
            promotion_module,
            "PATCH_PROPOSAL_CANDIDATE_PROMOTIONS_DIR",
            self.promotion_dir,
        )
        self.dir_patch.start()
        self.addCleanup(self.dir_patch.stop)

    def _candidate(self, **overrides):
        candidate = {
            "artifact_type": "packet_result_patch_proposal_candidate",
            "candidate_id": "candidate_phase290",
            "candidate_status": "candidate_only",
            "source_packet_id": "packet_phase290",
            "source_run_id": "run_phase290",
            "source_task_id": "task_phase290",
            "source_execution_artifact_id": "artifact_phase290",
            "source_execution_artifact_path": str(self.root / "artifact.json"),
            "source_verifier_result_path": str(self.root / "verifier.json"),
            "operator_decision_record_id": "decision_phase290",
            "eligibility_record": {
                "status": "eligible",
                "task_id": "task_phase290",
                "packet_id": "packet_phase290",
                "run_id": "run_phase290",
                "no_apply_authorization": True,
            },
            "no_apply_authorization": True,
            "candidate_is_not_patch_authorization": True,
            "candidate_is_not_patch_apply_request": True,
            "patch_apply_authorized": False,
            "patch_applied": False,
            "non_proofs": ["no_semantic_correctness_proof"],
        }
        candidate.update(overrides)
        return candidate

    def _record(self, decision="promote_to_patch_proposal_candidate_ready", **overrides):
        data = {
            "operator_decision": decision,
            "operator_note": "Reviewed the candidate for a later boundary.",
            "candidate": self._candidate(),
        }
        data.update(overrides)
        return create_patch_proposal_candidate_promotion_record(data)

    def test_promotion_record_persists_for_valid_candidate_with_reason(self):
        result = self._record()
        loaded = load_patch_proposal_candidate_promotion_record(result["promotion_record_id"])

        self.assertTrue(result["promotion_record_created"])
        self.assertEqual(
            loaded["promotion_status"],
            "candidate_ready_for_later_patch_proposal_boundary",
        )
        self.assertEqual(loaded["candidate_id"], "candidate_phase290")

    def test_rejection_record_persists_for_candidate_with_reason(self):
        result = self._record("reject_candidate")
        loaded = load_patch_proposal_candidate_promotion_record(result["promotion_record_id"])

        self.assertEqual(result["promotion_status"], "candidate_rejected")
        self.assertEqual(loaded["operator_decision"], "reject_candidate")

    def test_defer_record_persists_for_candidate_with_reason(self):
        result = self._record("defer_candidate")
        loaded = load_patch_proposal_candidate_promotion_record(result["promotion_record_id"])

        self.assertEqual(result["promotion_status"], "candidate_deferred")
        self.assertEqual(loaded["operator_decision"], "defer_candidate")

    def test_missing_note_reason_blocks(self):
        result = self._record(operator_note="")

        self.assertFalse(result["promotion_record_created"])
        self.assertEqual(result["reason_code"], "promotion_note_required")

    def test_ineligible_candidate_blocks_promotion(self):
        result = self._record(candidate=self._candidate(eligibility_record={"status": "ineligible"}))

        self.assertFalse(result["promotion_record_created"])
        self.assertIn("eligible_candidate_required", result["blocked_conditions"])

    def test_stale_or_mismatched_candidate_evidence_blocks(self):
        result = self._record(candidate=self._candidate(source_verifier_result_path=""))

        self.assertFalse(result["promotion_record_created"])
        self.assertIn("candidate_verifier_result_required", result["blocked_conditions"])

    def test_accepted_packet_decision_alone_cannot_promote_without_explicit_decision(self):
        result = create_patch_proposal_candidate_promotion_record(
            {
                "operator_note": "Acceptance alone is not enough.",
                "candidate": self._candidate(),
            }
        )

        self.assertFalse(result["promotion_record_created"])
        self.assertEqual(result["reason_code"], "unsupported_promotion_decision")

    def test_promotion_does_not_authorize_apply(self):
        result = self._record()

        self.assertTrue(result["no_apply_authorization"])
        self.assertTrue(result["promotion_is_not_patch_apply_authorization"])
        self.assertFalse(result["patch_apply_authorized"])

    def test_promotion_does_not_invoke_apply(self):
        with patch.dict("sys.modules", {"orchestrator.patch_apply": None}):
            result = self._record()

        self.assertTrue(result["promotion_record_created"])
        self.assertFalse(result["patch_applied"])

    def test_no_draft_or_proposal_artifact_is_created(self):
        result = self._record()
        loaded = load_patch_proposal_candidate_promotion_record(result["promotion_record_id"])

        self.assertFalse(result["patch_proposal_created"])
        self.assertFalse(loaded["patch_proposal_created"])
        self.assertNotEqual(loaded["artifact_type"], "patch_proposal")

    def test_rejected_and_deferred_candidates_are_surfaced_in_readback(self):
        rejected = self._record("reject_candidate")
        deferred = self._record("defer_candidate")

        self.assertEqual(rejected["promotion_status"], "candidate_rejected")
        self.assertEqual(deferred["promotion_status"], "candidate_deferred")

    def test_semantic_autonomous_model_provider_runtime_claims_remain_non_proofs(self):
        result = self._record()
        loaded = load_patch_proposal_candidate_promotion_record(result["promotion_record_id"])
        serialized = json.dumps(loaded, sort_keys=True)

        self.assertIn("no_semantic_correctness_proof", serialized)
        self.assertIn("no_autonomous_ai_coding_proof", serialized)
        self.assertFalse(loaded["provider_executed"])
        self.assertFalse(loaded["model_executed"])
        self.assertFalse(loaded["runtime_executed"])
        self.assertFalse(loaded["platform_invoked"])


if __name__ == "__main__":
    unittest.main()
