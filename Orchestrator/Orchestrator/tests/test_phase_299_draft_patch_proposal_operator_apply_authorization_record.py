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
    load_draft_patch_proposal_apply_authorization_record,
)


class Phase299DraftPatchProposalOperatorApplyAuthorizationRecordTests(unittest.TestCase):
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

    def _candidate(self, **overrides):
        candidate = {
            "artifact_type": "packet_result_patch_proposal_candidate",
            "candidate_id": "candidate_phase299",
            "candidate_status": "candidate_only",
            "source_packet_id": "packet_phase299",
            "source_run_id": "run_phase299",
            "source_task_id": "task_phase299",
            "source_execution_artifact_id": "artifact_phase299",
            "source_execution_artifact_path": "data/artifacts/phase299.json",
            "source_verifier_result_path": "data/verifier_results/phase299.json",
            "current_success_review_reference": {
                "task_id": "task_phase299",
                "run_id": "run_phase299",
                "classification": "completed_current_state_success",
                "ready_for_operator_review": True,
            },
            "operator_decision_record_id": "decision_phase299",
            "operator_decision_record_path": "data/operator_decisions/phase299.json",
            "operator_decision": "accept_packet_result",
            "eligibility_record": {
                "status": "eligible",
                "task_id": "task_phase299",
                "packet_id": "packet_phase299",
                "run_id": "run_phase299",
                "accepted_packet_decision": "accept_packet_result",
            },
            "proposed_patch_evidence_payload": {
                "evidence_id": "patch_evidence_phase299",
                "proposed_changes": [
                    {
                        "path": "src/phase299.txt",
                        "description": "Authorization-only evidence.",
                    }
                ],
                "unified_diff": "--- a/src/phase299.txt\n+++ b/src/phase299.txt\n",
                "rationale": "Structured authorization record evidence.",
            },
            "linked_evidence": [
                {
                    "evidence_type": "execution_artifact",
                    "evidence_id": "artifact_phase299",
                }
            ],
            "caveats": ["source_test_docs_only"],
            "no_apply_authorization": True,
            "candidate_is_not_patch_authorization": True,
            "candidate_is_not_patch_apply_request": True,
            "patch_apply_authorized": False,
            "patch_applied": False,
            "non_proofs": ["no_semantic_correctness_proof"],
        }
        candidate.update(overrides)
        return candidate

    def _promotion(self, **overrides):
        promotion = {
            "artifact_type": "patch_proposal_candidate_promotion_record",
            "promotion_record_id": "promotion_phase299",
            "promotion_status": "candidate_ready_for_later_patch_proposal_boundary",
            "operator_decision": "promote_to_patch_proposal_candidate_ready",
            "operator_note": "Promote for authorization-only record.",
            "candidate_id": "candidate_phase299",
            "source_packet_id": "packet_phase299",
            "source_run_id": "run_phase299",
            "source_task_id": "task_phase299",
            "source_execution_artifact_id": "artifact_phase299",
            "source_execution_artifact_path": "data/artifacts/phase299.json",
            "source_verifier_result_path": "data/verifier_results/phase299.json",
            "operator_decision_record_id": "decision_phase299",
            "no_apply_authorization": True,
            "promotion_is_not_patch_apply_authorization": True,
            "patch_apply_authorized": False,
            "patch_applied": False,
            "non_proofs": ["no_semantic_correctness_proof"],
        }
        promotion.update(overrides)
        return promotion

    def _draft(self, **overrides):
        candidate = overrides.pop("candidate", self._candidate())
        promotion = overrides.pop("promotion", self._promotion())
        draft = {
            "promoted_candidate_draft_patch_proposal_surface": True,
            "artifact_type": "draft_patch_proposal",
            "draft_proposal_id": "draft_phase299",
            "draft_proposal_status": "draft_only",
            "source_candidate_id": "candidate_phase299",
            "source_promotion_record_id": "promotion_phase299",
            "source_packet_id": "packet_phase299",
            "source_run_id": "run_phase299",
            "source_task_id": "task_phase299",
            "source_execution_artifact_id": "artifact_phase299",
            "source_execution_artifact_path": "data/artifacts/phase299.json",
            "source_verifier_result_path": "data/verifier_results/phase299.json",
            "current_success_review_reference": {
                "task_id": "task_phase299",
                "run_id": "run_phase299",
                "classification": "completed_current_state_success",
                "ready_for_operator_review": True,
            },
            "operator_decision_record_id": "decision_phase299",
            "operator_decision_record_path": "data/operator_decisions/phase299.json",
            "phase_288_eligibility_reference": candidate["eligibility_record"],
            "phase_289_candidate_reference": candidate,
            "phase_290_promotion_reference": promotion,
            "proposed_patch_evidence_payload": candidate[
                "proposed_patch_evidence_payload"
            ],
            "linked_evidence": [
                {
                    "evidence_type": "phase_289_candidate_artifact",
                    "evidence_id": "candidate_phase299",
                }
            ],
            "caveats": ["source_test_docs_only"],
            "non_proofs": ["no_semantic_correctness_proof"],
            "draft_only": True,
            "not_authorized_for_apply": True,
            "not_applied": True,
            "no_apply_authorization": True,
            "patch_apply_authorized": False,
            "patch_applied": False,
        }
        draft.update(overrides)
        return draft

    def _eligibility(self, draft=None, **overrides):
        draft = draft or self._draft()
        eligibility = {
            "draft_patch_proposal_apply_authorization_eligibility_surface": True,
            "draft_proposal_id": draft["draft_proposal_id"],
            "authorization_eligibility_status": "authorization_eligible",
            "reason_code": "draft_patch_proposal_has_authorization_eligibility_evidence",
            "missing_evidence": [],
            "linked_evidence": [
                {
                    "evidence_type": "phase_289_candidate_artifact",
                    "evidence_id": draft["source_candidate_id"],
                }
            ],
            "caveats": ["authorization_eligibility_only"],
            "non_proofs": ["authorization_eligibility_is_not_apply_authorization"],
            "patch_apply_authorized": False,
            "patch_applied": False,
        }
        eligibility.update(overrides)
        return eligibility

    def _create(self, draft=None, decision=AUTHORIZE_APPLY, **overrides):
        draft = draft or self._draft()
        payload = {
            "authorization_id": "authorization_phase299",
            "draft_proposal": draft,
            "authorization_eligibility": self._eligibility(draft),
            "authorization_decision": decision,
            "operator_authorization_note": "Operator explicitly authorizes the later bounded apply attempt.",
        }
        payload.update(overrides)
        return create_draft_patch_proposal_apply_authorization_record(payload)

    def _blocked(self, draft=None, **overrides):
        result = self._create(draft, **overrides)
        self.assertFalse(result["operator_apply_authorization_record_created"])
        self.assertFalse(result["patch_applied"])
        self.assertFalse(result["apply_result_created"])
        self.assertFalse(result["patch_task_finalized"])
        self.assertFalse(result["provider_executed"])
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["runtime_executed"])
        self.assertFalse(result["platform_invoked"])
        return result

    def test_eligible_draft_with_explicit_authorize_apply_persists_record(self):
        result = self._create()
        loaded = load_draft_patch_proposal_apply_authorization_record(
            result["authorization_id"]
        )

        self.assertTrue(result["operator_apply_authorization_record_created"])
        self.assertTrue(result["apply_authorization_created"])
        self.assertEqual(result["authorization_decision"], AUTHORIZE_APPLY)
        self.assertEqual(loaded["authorization_status"], "authorized_for_later_bounded_apply")
        self.assertFalse(loaded["patch_applied"])

    def test_authorization_record_links_to_full_evidence_chain(self):
        result = self._create()
        loaded = load_draft_patch_proposal_apply_authorization_record(
            result["authorization_id"]
        )

        self.assertEqual(loaded["draft_proposal_id"], "draft_phase299")
        self.assertEqual(loaded["source_packet_id"], "packet_phase299")
        self.assertEqual(loaded["source_run_id"], "run_phase299")
        self.assertEqual(loaded["source_task_id"], "task_phase299")
        self.assertEqual(loaded["source_execution_artifact_id"], "artifact_phase299")
        self.assertEqual(loaded["source_verifier_result_path"], "data/verifier_results/phase299.json")
        self.assertEqual(
            loaded["operator_packet_acceptance_decision_reference"][
                "operator_decision_record_id"
            ],
            "decision_phase299",
        )
        self.assertEqual(
            loaded["phase_289_candidate_reference"]["candidate_id"],
            "candidate_phase299",
        )
        self.assertEqual(
            loaded["phase_290_promotion_reference"]["promotion_record_id"],
            "promotion_phase299",
        )

    def test_rejected_authorization_decision_persists_rejection_record(self):
        result = self._create(decision=REJECT_APPLY_AUTHORIZATION)
        loaded = load_draft_patch_proposal_apply_authorization_record(
            result["authorization_id"]
        )

        self.assertEqual(loaded["authorization_status"], "apply_authorization_rejected")
        self.assertFalse(loaded["apply_authorization_created"])
        self.assertFalse(loaded["patch_apply_authorized"])

    def test_deferred_authorization_decision_persists_defer_record(self):
        result = self._create(decision=DEFER_APPLY_AUTHORIZATION)
        loaded = load_draft_patch_proposal_apply_authorization_record(
            result["authorization_id"]
        )

        self.assertEqual(loaded["authorization_status"], "apply_authorization_deferred")
        self.assertFalse(loaded["apply_authorization_created"])
        self.assertFalse(loaded["patch_apply_authorized"])

    def test_missing_operator_note_reason_blocks(self):
        result = self._blocked(operator_authorization_note="")

        self.assertIn("operator_authorization_note_required", result["blocked_conditions"])

    def test_ineligible_phase_296_readback_blocks_authorization(self):
        draft = self._draft()
        result = self._blocked(
            draft,
            authorization_eligibility=self._eligibility(
                draft,
                authorization_eligibility_status="authorization_ineligible",
            ),
        )

        self.assertIn("authorization_eligibility_not_clean", result["blocked_conditions"])

    def test_mismatched_draft_eligibility_links_block(self):
        draft = self._draft()
        result = self._blocked(
            draft,
            authorization_eligibility=self._eligibility(
                draft,
                draft_proposal_id="draft_other",
            ),
        )

        self.assertIn("authorization_eligibility_draft_mismatch", result["blocked_conditions"])

    def test_draft_already_authorized_blocks_duplicate_authorization(self):
        result = self._blocked(self._draft(not_authorized_for_apply=False))

        self.assertIn("existing_apply_authorization_rejected", result["blocked_conditions"])

    def test_draft_already_applied_blocks_authorization(self):
        result = self._blocked(self._draft(not_applied=False))

        self.assertIn("existing_apply_rejected", result["blocked_conditions"])

    def test_missing_structured_patch_payload_blocks(self):
        result = self._blocked(self._draft(proposed_patch_evidence_payload={}))

        self.assertIn("structured_patch_payload_missing", result["blocked_conditions"])

    def test_ambiguous_patch_payload_blocks(self):
        payload = dict(self._candidate()["proposed_patch_evidence_payload"])
        payload["proposed_changes"] = [{"description": "missing path"}]
        result = self._blocked(self._draft(proposed_patch_evidence_payload=payload))

        self.assertIn("ambiguous_patch_payload_rejected", result["blocked_conditions"])

    def test_provider_model_runtime_platform_smuggling_blocks(self):
        result = self._blocked(self._draft(model_name="qwen3.6:27b"))

        self.assertIn(
            "provider_model_runtime_platform_claim_rejected",
            result["blocked_conditions"],
        )

    def test_semantic_correctness_claim_remains_non_proof(self):
        result = self._blocked(self._draft(semantic_correctness_claimed=True))

        self.assertIn("semantic_correctness_claim_is_non_proof", result["blocked_conditions"])
        self.assertIn("no_semantic_correctness_proof", result["non_proofs"])

    def test_production_readiness_claim_remains_non_proof(self):
        result = self._blocked(self._draft(production_readiness_claimed=True))

        self.assertIn("production_readiness_claim_rejected", result["blocked_conditions"])
        self.assertIn("no_production_readiness_proof", result["non_proofs"])

    def test_authorization_record_explicitly_says_patch_not_applied(self):
        result = self._create()
        loaded = load_draft_patch_proposal_apply_authorization_record(
            result["authorization_id"]
        )

        self.assertIn("patch not applied", loaded["explicit_authorization_only_statement"])
        self.assertFalse(loaded["patch_applied"])

    def test_authorization_record_does_not_call_patch_apply_engine(self):
        with patch.dict("sys.modules", {"orchestrator.patch_apply_engine": None}):
            result = self._create()

        self.assertTrue(result["operator_apply_authorization_record_created"])
        self.assertFalse(result["patch_applied"])
        self.assertFalse(result["apply_result_created"])

    def test_duplicate_authorization_record_blocks_with_exact_reason(self):
        existing = {
            "authorization_id": "authorization_old",
            "draft_proposal_id": "draft_phase299",
            "authorization_decision": AUTHORIZE_APPLY,
        }

        result = self._blocked(authorization_records=[existing])

        self.assertIn(
            "duplicate_apply_authorization_record_rejected",
            result["blocked_conditions"],
        )

    def test_path_traversal_and_absolute_ids_block(self):
        for bad_id in ("../draft", "/draft", "C:\\draft", "draft\\nested"):
            with self.subTest(bad_id=bad_id):
                result = self._blocked(self._draft(draft_proposal_id=bad_id))
                self.assertIn(
                    "path_traversal_or_absolute_id_rejected",
                    result["blocked_conditions"],
                )


if __name__ == "__main__":
    unittest.main()
