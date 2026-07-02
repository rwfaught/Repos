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
)
from orchestrator.packet_cli_residue_guard import inspect_packet_cli_generated_residue


class Phase300PatchApplyAuthorizationRecordNegativeEdgeContractTests(unittest.TestCase):
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
            "candidate_id": "candidate_phase300",
            "candidate_status": "candidate_only",
            "source_packet_id": "packet_phase300",
            "source_run_id": "run_phase300",
            "source_task_id": "task_phase300",
            "source_execution_artifact_id": "artifact_phase300",
            "source_execution_artifact_path": "data/artifacts/phase300.json",
            "source_verifier_result_path": "data/verifier_results/phase300.json",
            "current_success_review_reference": {
                "task_id": "task_phase300",
                "run_id": "run_phase300",
                "classification": "completed_current_state_success",
                "ready_for_operator_review": True,
            },
            "operator_decision_record_id": "decision_phase300",
            "operator_decision_record_path": "data/operator_decisions/phase300.json",
            "operator_decision": "accept_packet_result",
            "eligibility_record": {
                "status": "eligible",
                "task_id": "task_phase300",
                "packet_id": "packet_phase300",
                "run_id": "run_phase300",
                "accepted_packet_decision": "accept_packet_result",
            },
            "proposed_patch_evidence_payload": {
                "evidence_id": "patch_evidence_phase300",
                "proposed_changes": [
                    {
                        "path": "src/phase300.txt",
                        "description": "Negative-edge authorization evidence.",
                    }
                ],
                "unified_diff": "--- a/src/phase300.txt\n+++ b/src/phase300.txt\n",
                "rationale": "Structured authorization evidence.",
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

    def _promotion(self, **overrides):
        promotion = {
            "artifact_type": "patch_proposal_candidate_promotion_record",
            "promotion_record_id": "promotion_phase300",
            "promotion_status": "candidate_ready_for_later_patch_proposal_boundary",
            "operator_decision": "promote_to_patch_proposal_candidate_ready",
            "operator_note": "Promote for authorization edge coverage.",
            "candidate_id": "candidate_phase300",
            "source_packet_id": "packet_phase300",
            "source_run_id": "run_phase300",
            "source_task_id": "task_phase300",
            "source_execution_artifact_id": "artifact_phase300",
            "source_execution_artifact_path": "data/artifacts/phase300.json",
            "source_verifier_result_path": "data/verifier_results/phase300.json",
            "operator_decision_record_id": "decision_phase300",
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
            "draft_proposal_id": "draft_phase300",
            "draft_proposal_status": "draft_only",
            "source_candidate_id": "candidate_phase300",
            "source_promotion_record_id": "promotion_phase300",
            "source_packet_id": "packet_phase300",
            "source_run_id": "run_phase300",
            "source_task_id": "task_phase300",
            "source_execution_artifact_id": "artifact_phase300",
            "source_execution_artifact_path": "data/artifacts/phase300.json",
            "source_verifier_result_path": "data/verifier_results/phase300.json",
            "current_success_review_reference": {
                "task_id": "task_phase300",
                "run_id": "run_phase300",
                "classification": "completed_current_state_success",
                "ready_for_operator_review": True,
            },
            "operator_decision_record_id": "decision_phase300",
            "operator_decision_record_path": "data/operator_decisions/phase300.json",
            "phase_288_eligibility_reference": candidate["eligibility_record"],
            "phase_289_candidate_reference": candidate,
            "phase_290_promotion_reference": promotion,
            "proposed_patch_evidence_payload": candidate[
                "proposed_patch_evidence_payload"
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
            "linked_evidence": [],
            "caveats": ["authorization_eligibility_only"],
            "non_proofs": ["authorization_eligibility_is_not_apply_authorization"],
            "patch_apply_authorized": False,
            "patch_applied": False,
        }
        eligibility.update(overrides)
        return eligibility

    def _payload(self, draft=None, **overrides):
        draft = draft or self._draft()
        payload = {
            "authorization_id": "authorization_phase300",
            "draft_proposal": draft,
            "authorization_eligibility": self._eligibility(draft),
            "authorization_decision": AUTHORIZE_APPLY,
            "operator_authorization_note": "Operator decision for negative-edge contract.",
        }
        payload.update(overrides)
        return payload

    def _blocked(self, payload):
        sentinel = self.root / "sentinel_keep.txt"
        sentinel.write_text("do not delete", encoding="utf-8")
        result = create_draft_patch_proposal_apply_authorization_record(payload)

        self.assertFalse(result["operator_apply_authorization_record_created"])
        self.assertEqual(result["authorization_status"], "blocked")
        self.assertTrue(result["reason_code"])
        self.assertFalse(result["patch_applied"])
        self.assertFalse(result["apply_result_created"])
        self.assertFalse(result["patch_task_finalized"])
        self.assertFalse(result["provider_executed"])
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["runtime_executed"])
        self.assertFalse(result["platform_invoked"])
        self.assertFalse(result["production_readiness_claimed"])
        self.assertFalse(result["semantic_correctness_claimed"])
        self.assertFalse(result["autonomous_ai_coding_claimed"])
        self.assertTrue(sentinel.exists())
        self.assertFalse((self.auth_dir / "authorization_phase300.json").exists())
        return result

    def test_missing_draft_proposal_blocks(self):
        result = self._blocked(
            {
                "authorization_decision": AUTHORIZE_APPLY,
                "operator_authorization_note": "Need draft.",
                "authorization_eligibility": {"authorization_eligibility_status": "authorization_eligible"},
            }
        )

        self.assertIn("draft_proposal_missing", result["blocked_conditions"])

    def test_draft_not_draft_only_already_authorized_or_applied_blocks(self):
        cases = [
            (self._draft(draft_proposal_status="final"), "draft_only_status_required"),
            (self._draft(not_authorized_for_apply=False), "existing_apply_authorization_rejected"),
            (self._draft(not_applied=False), "existing_apply_rejected"),
        ]
        for draft, reason in cases:
            with self.subTest(reason=reason):
                result = self._blocked(self._payload(draft))
                self.assertIn(reason, result["blocked_conditions"])

    def test_missing_ineligible_and_blocked_phase296_readbacks_block(self):
        draft = self._draft()
        cases = [
            ({}, "authorization_eligibility_required"),
            (
                self._payload(
                    draft,
                    authorization_eligibility=self._eligibility(
                        draft,
                        authorization_eligibility_status="authorization_ineligible",
                    ),
                ),
                "authorization_eligibility_not_clean",
            ),
            (
                self._payload(
                    draft,
                    authorization_eligibility=self._eligibility(
                        draft,
                        authorization_eligibility_status="authorization_blocked",
                    ),
                ),
                "authorization_eligibility_not_clean",
            ),
        ]
        for payload, reason in cases:
            with self.subTest(reason=reason):
                if not payload:
                    payload = self._payload(draft)
                    payload.pop("authorization_eligibility")
                result = self._blocked(payload)
                self.assertIn(reason, result["blocked_conditions"])

    def test_mismatched_draft_candidate_task_artifact_verifier_current_success_and_decision_block(self):
        cases = [
            (
                self._payload(
                    self._draft(),
                    authorization_eligibility=self._eligibility(
                        self._draft(),
                        draft_proposal_id="draft_other",
                    ),
                ),
                "authorization_eligibility_draft_mismatch",
            ),
            (
                self._payload(self._draft(candidate=self._candidate(candidate_id="candidate_other"))),
                "candidate_evidence_mismatch",
            ),
            (
                self._payload(self._draft(candidate=self._candidate(source_task_id="task_other"))),
                "candidate_evidence_mismatch",
            ),
            (
                self._payload(self._draft(candidate=self._candidate(source_execution_artifact_id="artifact_other"))),
                "candidate_evidence_mismatch",
            ),
            (
                self._payload(self._draft(candidate=self._candidate(source_verifier_result_path="other.json"))),
                "candidate_evidence_mismatch",
            ),
            (
                self._payload(
                    self._draft(
                        current_success_review_reference={
                            "task_id": "task_other",
                            "run_id": "run_phase300",
                            "classification": "completed_current_state_success",
                            "ready_for_operator_review": True,
                        }
                    )
                ),
                "current_success_reference_mismatch",
            ),
            (
                self._payload(self._draft(candidate=self._candidate(operator_decision="reject_packet_result"))),
                "accepted_packet_decision_mismatch",
            ),
        ]
        for payload, reason in cases:
            with self.subTest(reason=reason):
                result = self._blocked(payload)
                self.assertIn(reason, result["blocked_conditions"])

    def test_rejected_deferred_candidate_and_authorization_decisions_are_deterministic(self):
        for promotion_status, decision in [
            ("candidate_rejected", "reject_candidate"),
            ("candidate_deferred", "defer_candidate"),
        ]:
            result = self._blocked(
                self._payload(
                    self._draft(
                        promotion=self._promotion(
                            promotion_status=promotion_status,
                            operator_decision=decision,
                        )
                    )
                )
            )
            self.assertIn(
                "latest_negative_candidate_promotion_decision",
                result["blocked_conditions"],
            )

        for decision, expected_status in [
            (REJECT_APPLY_AUTHORIZATION, "apply_authorization_rejected"),
            (DEFER_APPLY_AUTHORIZATION, "apply_authorization_deferred"),
        ]:
            result = create_draft_patch_proposal_apply_authorization_record(
                self._payload(authorization_decision=decision)
            )
            self.assertEqual(result["authorization_status"], expected_status)
            self.assertFalse(result["patch_apply_authorized"])

    def test_missing_empty_or_unsupported_authorization_decision_and_note_block(self):
        for payload, reason in [
            (
                self._payload(operator_authorization_note=""),
                "operator_authorization_note_required",
            ),
            (
                self._payload(authorization_decision=""),
                "unsupported_authorization_decision",
            ),
            (
                self._payload(authorization_decision="approve_the_thing"),
                "unsupported_authorization_decision",
            ),
        ]:
            result = self._blocked(payload)
            self.assertIn(reason, result["blocked_conditions"])

    def test_missing_ambiguous_and_unsafe_patch_payloads_block(self):
        bad_payloads = [
            ({}, "structured_patch_payload_missing"),
            (
                {
                    "proposed_changes": [{"description": "missing path"}],
                    "unified_diff": "--- a/x\n+++ b/x\n",
                    "rationale": "Ambiguous.",
                },
                "ambiguous_patch_payload_rejected",
            ),
            (
                {
                    "proposed_changes": [{"path": "../src/phase300.txt"}],
                    "unified_diff": "--- a/x\n+++ b/x\n",
                    "rationale": "Traversal.",
                },
                "path_traversal_rejected",
            ),
            (
                {
                    "proposed_changes": [{"path": "/src/phase300.txt"}],
                    "unified_diff": "--- a/x\n+++ b/x\n",
                    "rationale": "Absolute.",
                },
                "absolute_patch_path_rejected",
            ),
            (
                {
                    "proposed_changes": [{"path": "C:\\src\\phase300.txt"}],
                    "unified_diff": "--- a/x\n+++ b/x\n",
                    "rationale": "Windows absolute.",
                },
                "absolute_patch_path_rejected",
            ),
            (
                {
                    "proposed_changes": [{"path": "src\\phase300.txt"}],
                    "unified_diff": "--- a/x\n+++ b/x\n",
                    "rationale": "Windows separator.",
                },
                "unsafe_patch_path_rejected",
            ),
        ]
        for payload, reason in bad_payloads:
            with self.subTest(reason=reason):
                result = self._blocked(
                    self._payload(self._draft(proposed_patch_evidence_payload=payload))
                )
                self.assertIn(reason, result["blocked_conditions"])

    def test_claim_smuggling_blocks_without_proofs_or_apply_side_effects(self):
        cases = [
            ({"model_name": "qwen3.6:27b"}, "provider_model_runtime_platform_claim_rejected"),
            ({"semantic_correctness_claimed": True}, "semantic_correctness_claim_is_non_proof"),
            ({"autonomous_ai_coding_claimed": True}, "autonomous_ai_coding_claim_rejected"),
            ({"production_readiness_claimed": True}, "production_readiness_claim_rejected"),
            ({"patch_apply_authorized": True}, "existing_apply_authorization_rejected"),
            ({"apply_result_created": True}, "apply_result_smuggling_rejected"),
            ({"patch_task_finalized": True}, "finalization_smuggling_rejected"),
        ]
        for override, reason in cases:
            with self.subTest(reason=reason):
                result = self._blocked(self._payload(self._draft(**override)))
                self.assertIn(reason, result["blocked_conditions"])

    def test_authorization_cannot_smuggle_apply_execution_in_text(self):
        result = self._blocked(
            self._payload(operator_authorization_note="Apply patch and finalize now.")
        )

        self.assertIn("apply_execution_smuggling_rejected", result["blocked_conditions"])
        self.assertIn("finalization_smuggling_rejected", result["blocked_conditions"])

    def test_duplicate_authorization_blocks_with_exact_reason(self):
        result = self._blocked(
            self._payload(
                authorization_records=[
                    {
                        "authorization_id": "authorization_old",
                        "draft_proposal_id": "draft_phase300",
                        "authorization_decision": AUTHORIZE_APPLY,
                    }
                ]
            )
        )

        self.assertIn(
            "duplicate_apply_authorization_record_rejected",
            result["blocked_conditions"],
        )

    def test_path_traversal_and_absolute_ids_block(self):
        for bad_id in ("../draft", "/draft", "C:\\draft", "draft\\nested"):
            with self.subTest(bad_id=bad_id):
                result = self._blocked(self._payload(self._draft(draft_proposal_id=bad_id)))
                self.assertIn(
                    "path_traversal_or_absolute_id_rejected",
                    result["blocked_conditions"],
                )

    def test_generated_residue_guard_reports_without_cleanup_deletion_or_archive(self):
        output = self.root / "outputs" / "phase300.txt"
        output.parent.mkdir(parents=True)
        output.write_text("generated", encoding="utf-8")

        result = inspect_packet_cli_generated_residue(self.root)

        self.assertTrue(result["residue_present"])
        self.assertEqual(result["generated_paths"], ["outputs/phase300.txt"])
        self.assertFalse(result["cleanup_performed"])
        self.assertFalse(result["delete_performed"])
        self.assertFalse(result["archive_performed"])


if __name__ == "__main__":
    unittest.main()
