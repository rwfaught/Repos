import unittest
from unittest.mock import patch

from orchestrator.draft_patch_proposal_apply_authorization_eligibility import (
    AUTHORIZATION_BLOCKED,
    AUTHORIZATION_ELIGIBLE,
    evaluate_draft_patch_proposal_apply_authorization_eligibility,
)


class Phase296DraftPatchProposalApplyAuthorizationEligibilityReadbackTests(
    unittest.TestCase
):
    def _candidate(self, **overrides):
        candidate = {
            "artifact_type": "packet_result_patch_proposal_candidate",
            "candidate_id": "candidate_phase296",
            "candidate_status": "candidate_only",
            "source_packet_id": "packet_phase296",
            "source_run_id": "run_phase296",
            "source_task_id": "task_phase296",
            "source_execution_artifact_id": "artifact_phase296",
            "source_execution_artifact_path": "data/artifacts/phase296.json",
            "source_verifier_result_path": "data/verifier_results/phase296.json",
            "current_success_review_reference": {
                "task_id": "task_phase296",
                "run_id": "run_phase296",
                "classification": "completed_current_state_success",
                "ready_for_operator_review": True,
            },
            "operator_decision_record_id": "decision_phase296",
            "operator_decision_record_path": "data/operator_decisions/phase296.json",
            "operator_decision": "accept_packet_result",
            "eligibility_record": {
                "status": "eligible",
                "task_id": "task_phase296",
                "packet_id": "packet_phase296",
                "run_id": "run_phase296",
                "accepted_packet_decision": "accept_packet_result",
            },
            "proposed_patch_evidence_payload": {
                "evidence_id": "patch_evidence_phase296",
                "proposed_changes": [
                    {
                        "path": "src/phase296.txt",
                        "description": "Eligibility-only evidence.",
                    }
                ],
                "unified_diff": "--- a/src/phase296.txt\n+++ b/src/phase296.txt\n",
                "rationale": "Structured eligibility readback evidence.",
            },
            "linked_evidence": [
                {
                    "evidence_type": "execution_artifact",
                    "evidence_id": "artifact_phase296",
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
            "promotion_record_id": "promotion_phase296",
            "promotion_status": "candidate_ready_for_later_patch_proposal_boundary",
            "operator_decision": "promote_to_patch_proposal_candidate_ready",
            "operator_note": "Promote for eligibility-only readback.",
            "candidate_id": "candidate_phase296",
            "source_packet_id": "packet_phase296",
            "source_run_id": "run_phase296",
            "source_task_id": "task_phase296",
            "source_execution_artifact_id": "artifact_phase296",
            "source_execution_artifact_path": "data/artifacts/phase296.json",
            "source_verifier_result_path": "data/verifier_results/phase296.json",
            "operator_decision_record_id": "decision_phase296",
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
            "draft_proposal_id": "draft_phase296",
            "draft_proposal_status": "draft_only",
            "source_candidate_id": "candidate_phase296",
            "source_promotion_record_id": "promotion_phase296",
            "source_packet_id": "packet_phase296",
            "source_run_id": "run_phase296",
            "source_task_id": "task_phase296",
            "source_execution_artifact_id": "artifact_phase296",
            "source_execution_artifact_path": "data/artifacts/phase296.json",
            "source_verifier_result_path": "data/verifier_results/phase296.json",
            "current_success_review_reference": {
                "task_id": "task_phase296",
                "run_id": "run_phase296",
                "classification": "completed_current_state_success",
                "ready_for_operator_review": True,
            },
            "operator_decision_record_id": "decision_phase296",
            "operator_decision_record_path": "data/operator_decisions/phase296.json",
            "phase_288_eligibility_reference": candidate["eligibility_record"],
            "phase_289_candidate_reference": candidate,
            "phase_290_promotion_reference": promotion,
            "proposed_patch_evidence_payload": candidate[
                "proposed_patch_evidence_payload"
            ],
            "linked_evidence": [
                {
                    "evidence_type": "phase_289_candidate_artifact",
                    "evidence_id": "candidate_phase296",
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

    def _readback(self, draft=None, **extra):
        payload = {"draft_proposal": draft or self._draft()}
        payload.update(extra)
        return evaluate_draft_patch_proposal_apply_authorization_eligibility(payload)

    def _blocked(self, draft=None, **extra):
        result = self._readback(draft, **extra)
        self.assertEqual(result["authorization_eligibility_status"], AUTHORIZATION_BLOCKED)
        self.assertFalse(result["patch_apply_authorized"])
        self.assertFalse(result["patch_applied"])
        self.assertFalse(result["provider_executed"])
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["runtime_executed"])
        self.assertFalse(result["platform_invoked"])
        self.assertTrue(result["explicit_no_authorization_statement"])
        self.assertTrue(result["explicit_no_apply_statement"])
        return result

    def test_valid_draft_proposal_returns_authorization_eligible(self):
        result = self._readback()

        self.assertEqual(result["authorization_eligibility_status"], AUTHORIZATION_ELIGIBLE)
        self.assertEqual(
            result["reason_code"],
            "draft_patch_proposal_has_authorization_eligibility_evidence",
        )
        self.assertEqual(result["missing_evidence"], [])
        self.assertIn("authorization_eligibility_is_not_apply_authorization", result["non_proofs"])

    def test_missing_draft_proposal_blocks(self):
        result = evaluate_draft_patch_proposal_apply_authorization_eligibility({})

        self.assertEqual(result["authorization_eligibility_status"], AUTHORIZATION_BLOCKED)
        self.assertIn("draft_proposal_missing", result["blocked_conditions"])

    def test_draft_already_marked_authorized_blocks(self):
        result = self._blocked(self._draft(not_authorized_for_apply=False))

        self.assertIn("existing_apply_authorization_rejected", result["blocked_conditions"])

    def test_draft_already_marked_applied_blocks(self):
        result = self._blocked(self._draft(not_applied=False))

        self.assertIn("existing_apply_rejected", result["blocked_conditions"])

    def test_draft_missing_promoted_candidate_link_blocks(self):
        draft = self._draft(phase_290_promotion_reference={}, source_promotion_record_id="")

        result = self._blocked(draft)

        self.assertIn("promoted_candidate_link_missing", result["blocked_conditions"])

    def test_candidate_evidence_mismatch_blocks(self):
        candidate = self._candidate(source_task_id="task_other")
        draft = self._draft(candidate=candidate)

        result = self._blocked(draft)

        self.assertIn("candidate_evidence_mismatch", result["blocked_conditions"])

    def test_accepted_packet_decision_mismatch_blocks(self):
        candidate = self._candidate(operator_decision="reject_packet_result")
        draft = self._draft(candidate=candidate)

        result = self._blocked(draft)

        self.assertIn("accepted_packet_decision_mismatch", result["blocked_conditions"])

    def test_missing_structured_patch_payload_blocks(self):
        draft = self._draft(proposed_patch_evidence_payload={})

        result = self._blocked(draft)

        self.assertIn("structured_patch_payload_missing", result["blocked_conditions"])

    def test_ambiguous_patch_payload_blocks(self):
        payload = dict(self._candidate()["proposed_patch_evidence_payload"])
        payload["proposed_changes"] = [{"description": "missing path"}]
        draft = self._draft(proposed_patch_evidence_payload=payload)

        result = self._blocked(draft)

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

    def test_eligibility_readback_explicitly_says_no_authorization_granted(self):
        result = self._readback()

        self.assertIn("No apply authorization", result["explicit_no_authorization_statement"])
        self.assertFalse(result["apply_authorization_created"])
        self.assertFalse(result["patch_apply_authorized"])

    def test_eligibility_readback_does_not_invoke_apply(self):
        with patch.dict("sys.modules", {"orchestrator.patch_apply_engine": None}):
            result = self._readback()

        self.assertEqual(result["authorization_eligibility_status"], AUTHORIZATION_ELIGIBLE)
        self.assertFalse(result["patch_applied"])

    def test_latest_negative_candidate_promotion_decision_blocks_eligibility(self):
        result = self._blocked(
            self._draft(),
            promotion_records=[
                self._promotion(created_at="2026-07-02T01:00:00+00:00"),
                self._promotion(
                    promotion_record_id="promotion_phase296_reject",
                    promotion_status="candidate_rejected",
                    operator_decision="reject_candidate",
                    created_at="2026-07-02T02:00:00+00:00",
                ),
            ],
        )

        self.assertIn(
            "latest_negative_candidate_promotion_decision",
            result["blocked_conditions"],
        )

    def test_path_traversal_and_absolute_ids_block(self):
        for bad_id in ("../draft", "/draft", "C:\\draft", "draft\\nested"):
            with self.subTest(bad_id=bad_id):
                draft = self._draft(draft_proposal_id=bad_id)
                result = self._blocked(draft)
                self.assertIn(
                    "path_traversal_or_absolute_id_rejected",
                    result["blocked_conditions"],
                )


if __name__ == "__main__":
    unittest.main()
