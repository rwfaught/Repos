import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import orchestrator.artifact_store as artifact_store
import orchestrator.draft_patch_proposal_apply_authorization_record as record_module
import orchestrator.paths as project_paths
from orchestrator.authorized_draft_patch_apply import (
    execute_authorized_draft_patch_apply,
    load_authorized_draft_patch_apply_attempt,
)
from orchestrator.draft_patch_proposal_apply_authorization_record import (
    AUTHORIZE_APPLY,
    DEFER_APPLY_AUTHORIZATION,
    REJECT_APPLY_AUTHORIZATION,
    create_draft_patch_proposal_apply_authorization_record,
    load_draft_patch_proposal_apply_authorization_record,
)


class Phase303AuthorizedDraftPatchProposalBoundedApplyExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.auth_dir = self.root / "authorizations"
        self.artifacts_dir = self.root / "data" / "artifacts"
        self.project_patch = patch.object(project_paths, "PROJECT_ROOT", self.root)
        self.artifact_patch = patch.object(
            artifact_store,
            "ARTIFACTS_DIR",
            self.artifacts_dir,
        )
        self.dir_patch = patch.object(
            record_module,
            "DRAFT_PATCH_PROPOSAL_APPLY_AUTHORIZATIONS_DIR",
            self.auth_dir,
        )
        self.project_patch.start()
        self.artifact_patch.start()
        self.dir_patch.start()
        self.addCleanup(self.project_patch.stop)
        self.addCleanup(self.artifact_patch.stop)
        self.addCleanup(self.dir_patch.stop)

    def _patch_payload(self, **overrides):
        payload = {
            "evidence_id": "patch_evidence_phase303",
            "proposed_changes": [
                {
                    "operation_id": "replace_phase303_text",
                    "path": "src/phase303.txt",
                    "expected_before": "before",
                    "replacement_after": "after",
                    "description": "Apply exact bounded text.",
                }
            ],
            "unified_diff": "--- a/src/phase303.txt\n+++ b/src/phase303.txt\n",
            "rationale": "Structured apply-attempt evidence.",
        }
        payload.update(overrides)
        return payload

    def _candidate(self, **overrides):
        payload = overrides.pop("proposed_patch_evidence_payload", self._patch_payload())
        candidate = {
            "artifact_type": "packet_result_patch_proposal_candidate",
            "candidate_id": "candidate_phase303",
            "candidate_status": "candidate_only",
            "source_packet_id": "packet_phase303",
            "source_run_id": "run_phase303",
            "source_task_id": "task_phase303",
            "source_execution_artifact_id": "artifact_phase303",
            "source_execution_artifact_path": "data/artifacts/phase303.json",
            "source_verifier_result_path": "data/verifier_results/phase303.json",
            "current_success_review_reference": {
                "task_id": "task_phase303",
                "run_id": "run_phase303",
                "classification": "completed_current_state_success",
                "ready_for_operator_review": True,
            },
            "operator_decision_record_id": "decision_phase303",
            "operator_decision_record_path": "data/operator_decisions/phase303.json",
            "operator_decision": "accept_packet_result",
            "eligibility_record": {
                "status": "eligible",
                "task_id": "task_phase303",
                "packet_id": "packet_phase303",
                "run_id": "run_phase303",
                "accepted_packet_decision": "accept_packet_result",
            },
            "proposed_patch_evidence_payload": payload,
            "linked_evidence": [
                {
                    "evidence_type": "execution_artifact",
                    "evidence_id": "artifact_phase303",
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
            "promotion_record_id": "promotion_phase303",
            "promotion_status": "candidate_ready_for_later_patch_proposal_boundary",
            "operator_decision": "promote_to_patch_proposal_candidate_ready",
            "operator_note": "Promote for Phase 303 bounded apply attempt.",
            "candidate_id": "candidate_phase303",
            "source_packet_id": "packet_phase303",
            "source_run_id": "run_phase303",
            "source_task_id": "task_phase303",
            "source_execution_artifact_id": "artifact_phase303",
            "source_execution_artifact_path": "data/artifacts/phase303.json",
            "source_verifier_result_path": "data/verifier_results/phase303.json",
            "operator_decision_record_id": "decision_phase303",
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
            "draft_proposal_id": "draft_phase303",
            "draft_proposal_status": "draft_only",
            "source_candidate_id": candidate["candidate_id"],
            "source_promotion_record_id": promotion["promotion_record_id"],
            "source_packet_id": "packet_phase303",
            "source_run_id": "run_phase303",
            "source_task_id": "task_phase303",
            "source_execution_artifact_id": "artifact_phase303",
            "source_execution_artifact_path": "data/artifacts/phase303.json",
            "source_verifier_result_path": "data/verifier_results/phase303.json",
            "current_success_review_reference": {
                "task_id": "task_phase303",
                "run_id": "run_phase303",
                "classification": "completed_current_state_success",
                "ready_for_operator_review": True,
            },
            "operator_decision_record_id": "decision_phase303",
            "operator_decision_record_path": "data/operator_decisions/phase303.json",
            "phase_288_eligibility_reference": candidate["eligibility_record"],
            "phase_289_candidate_reference": candidate,
            "phase_290_promotion_reference": promotion,
            "proposed_patch_evidence_payload": candidate[
                "proposed_patch_evidence_payload"
            ],
            "linked_evidence": [
                {
                    "evidence_type": "phase_289_candidate_artifact",
                    "evidence_id": candidate["candidate_id"],
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
            "unified_diff": candidate["proposed_patch_evidence_payload"].get(
                "unified_diff", ""
            ),
            "rationale": candidate["proposed_patch_evidence_payload"].get(
                "rationale", ""
            ),
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
            "authorization_id": "authorization_phase303",
            "draft_proposal": draft,
            "authorization_eligibility": self._eligibility(draft),
            "authorization_decision": decision,
            "operator_authorization_note": "Operator explicitly authorizes the bounded apply attempt.",
        }
        payload.update(overrides)
        return create_draft_patch_proposal_apply_authorization_record(payload)

    def _authorization_record(self, draft=None, decision=AUTHORIZE_APPLY, **overrides):
        result = self._create(draft=draft or self._draft(), decision=decision, **overrides)
        if result.get("operator_apply_authorization_record_created"):
            return load_draft_patch_proposal_apply_authorization_record(
                result["authorization_id"]
            )
        fallback_draft = draft or self._draft()
        return {
            "artifact_type": "draft_patch_proposal_apply_authorization_record",
            "authorization_id": "authorization_phase303",
            "authorization_decision": decision,
            "operator_decision": decision,
            "authorization_status": (
                "authorized_for_later_bounded_apply"
                if decision == AUTHORIZE_APPLY
                else "apply_authorization_rejected"
            ),
            "draft_proposal_id": fallback_draft["draft_proposal_id"],
            "eligibility_record": self._eligibility(fallback_draft),
            "phase_296_authorization_eligibility_reference": self._eligibility(
                fallback_draft
            ),
            "phase_294_draft_proposal_reference": fallback_draft,
            "linked_evidence": [],
            "caveats": ["test_negative_authorization_record"],
            "non_proofs": ["no_semantic_correctness_proof"],
            "timestamp": "2026-07-02T00:00:00+00:00",
        }

    def _target(self, text="before\n"):
        target = self.root / "src" / "phase303.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def _attempt(self, authorization=None, **kwargs):
        authorization = authorization or self._authorization_record()
        return execute_authorized_draft_patch_apply(
            authorization["authorization_id"],
            authorization_record=authorization,
            **kwargs,
        )

    def test_active_authorization_with_valid_draft_invokes_bounded_apply_and_records_applied_attempt(self):
        target = self._target()
        authorization = self._authorization_record()

        attempt = self._attempt(authorization)

        self.assertEqual(target.read_text(encoding="utf-8"), "after\n")
        self.assertEqual(attempt["apply_status"], "applied")
        self.assertTrue(attempt["apply_attempt_created"])
        self.assertEqual(attempt["source_authorization_id"], authorization["authorization_id"])
        self.assertEqual(load_authorized_draft_patch_apply_attempt(attempt["apply_attempt_id"]), attempt)

    def test_apply_attempt_links_authorization_draft_candidate_and_packet_evidence_chain(self):
        self._target()
        attempt = self._attempt()
        chain = attempt["linked_evidence_chain"]

        self.assertEqual(chain["phase_294_draft_proposal_id"], "draft_phase303")
        self.assertEqual(chain["phase_289_candidate_id"], "candidate_phase303")
        self.assertEqual(chain["source_packet_id"], "packet_phase303")
        self.assertEqual(chain["source_task_id"], "task_phase303")
        self.assertEqual(chain["source_execution_artifact_id"], "artifact_phase303")
        self.assertEqual(chain["operator_decision_record_id"], "decision_phase303")

    def test_missing_authorization_blocks(self):
        attempt = execute_authorized_draft_patch_apply("authorization_missing")

        self.assertEqual(attempt["apply_status"], "blocked")
        self.assertEqual(attempt["reason_code"], "apply_authorization_record_missing")

    def test_rejected_authorization_blocks(self):
        authorization = self._authorization_record(decision=REJECT_APPLY_AUTHORIZATION)

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "apply_authorization_not_authorize_apply")
        self.assertEqual(attempt["apply_status"], "blocked")

    def test_deferred_authorization_blocks(self):
        authorization = self._authorization_record(decision=DEFER_APPLY_AUTHORIZATION)

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "apply_authorization_not_authorize_apply")
        self.assertEqual(attempt["apply_status"], "blocked")

    def test_stale_authorization_blocks(self):
        authorization = self._authorization_record()
        newer = {
            **authorization,
            "authorization_id": "authorization_phase303_newer",
            "authorization_decision": DEFER_APPLY_AUTHORIZATION,
            "authorization_status": "apply_authorization_deferred",
            "timestamp": "2099-01-01T00:00:00+00:00",
        }

        attempt = self._attempt(
            authorization,
            authorization_records=[authorization, newer],
        )

        self.assertEqual(attempt["reason_code"], "latest_apply_authorization_not_active")

    def test_mismatched_authorization_draft_links_block(self):
        authorization = {
            **self._authorization_record(),
            "draft_proposal_id": "draft_other",
        }

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "authorization_draft_link_mismatch")

    def test_draft_already_applied_blocks(self):
        draft = self._draft(not_applied=False, patch_applied=True)
        authorization = self._authorization_record(draft=draft)

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "draft_already_applied_rejected")

    def test_missing_structured_patch_payload_blocks(self):
        authorization = self._authorization_record(
            draft=self._draft(proposed_patch_evidence_payload={})
        )

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "structured_patch_payload_missing")

    def test_ambiguous_patch_payload_blocks(self):
        payload = self._patch_payload(
            proposed_changes=[{"path": "src/phase303.txt", "expected_before": "before"}]
        )
        authorization = self._authorization_record(
            draft=self._draft(proposed_patch_evidence_payload=payload)
        )

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "ambiguous_patch_payload_rejected")

    def test_unsupported_patch_operation_blocks_as_ambiguous(self):
        payload = self._patch_payload(
            proposed_changes=[
                {
                    "operation_id": "unsupported_phase303",
                    "path": "src/phase303.txt",
                    "expected_before": "before",
                    "replacement_after": "after",
                    "mode": "delete_tree",
                }
            ]
        )
        authorization = self._authorization_record(
            draft=self._draft(proposed_patch_evidence_payload=payload)
        )

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "ambiguous_patch_payload_rejected")

    def test_unbounded_target_path_blocks(self):
        payload = self._patch_payload(
            proposed_changes=[
                {
                    "operation_id": "bad_phase303",
                    "path": "",
                    "expected_before": "before",
                    "replacement_after": "after",
                }
            ]
        )
        authorization = self._authorization_record(
            draft=self._draft(proposed_patch_evidence_payload=payload)
        )

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "ambiguous_patch_payload_rejected")

    def test_path_traversal_blocks(self):
        payload = self._patch_payload(
            proposed_changes=[
                {
                    "operation_id": "traversal_phase303",
                    "path": "../outside.txt",
                    "expected_before": "before",
                    "replacement_after": "after",
                }
            ]
        )
        authorization = self._authorization_record(
            draft=self._draft(proposed_patch_evidence_payload=payload)
        )

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "path_traversal_rejected")

    def test_posix_absolute_path_blocks(self):
        payload = self._patch_payload(
            proposed_changes=[
                {
                    "operation_id": "posix_abs_phase303",
                    "path": "/tmp/outside.txt",
                    "expected_before": "before",
                    "replacement_after": "after",
                }
            ]
        )
        authorization = self._authorization_record(
            draft=self._draft(proposed_patch_evidence_payload=payload)
        )

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "absolute_patch_path_rejected")

    def test_windows_absolute_path_blocks(self):
        payload = self._patch_payload(
            proposed_changes=[
                {
                    "operation_id": "windows_abs_phase303",
                    "path": "C:\\outside.txt",
                    "expected_before": "before",
                    "replacement_after": "after",
                }
            ]
        )
        authorization = self._authorization_record(
            draft=self._draft(proposed_patch_evidence_payload=payload)
        )

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "absolute_patch_path_rejected")

    def test_provider_model_runtime_platform_smuggling_blocks(self):
        authorization = self._authorization_record(draft=self._draft(model_name="qwen3.6:27b"))

        attempt = self._attempt(authorization)

        self.assertEqual(
            attempt["reason_code"],
            "provider_model_runtime_platform_claim_rejected",
        )

    def test_semantic_correctness_claim_remains_non_proof(self):
        authorization = self._authorization_record(
            draft=self._draft(semantic_correctness_claimed=True)
        )

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "semantic_correctness_claim_is_non_proof")
        self.assertTrue(attempt["semantic_correctness_not_proven"])

    def test_production_readiness_claim_remains_non_proof(self):
        authorization = self._authorization_record(
            draft=self._draft(production_readiness_claimed=True)
        )

        attempt = self._attempt(authorization)

        self.assertEqual(attempt["reason_code"], "production_readiness_claim_rejected")
        self.assertTrue(attempt["production_readiness_not_proven"])

    def test_apply_attempt_explicitly_says_not_verified(self):
        self._target()
        attempt = self._attempt()

        self.assertTrue(attempt["patch_not_verified"])
        self.assertFalse(attempt["verification_satisfied"])
        self.assertFalse(attempt["apply_result_verified"])

    def test_apply_attempt_explicitly_says_not_finalized(self):
        self._target()
        attempt = self._attempt()

        self.assertTrue(attempt["not_finalized"])
        self.assertTrue(attempt["no_finalization_in_this_phase"])
        self.assertFalse(attempt["patch_task_finalized"])

    def test_no_finalization_function_is_invoked(self):
        self._target()
        engine = Mock(
            return_value={
                "apply_id": "phase99_apply_mock",
                "applied": True,
                "verification_satisfied": False,
                "task_completed": False,
            }
        )

        attempt = self._attempt(apply_engine=engine)

        engine.assert_called_once()
        self.assertEqual(attempt["apply_status"], "applied")
        self.assertFalse(attempt["patch_task_finalized"])

    def test_phase_99_patch_apply_spine_regression_remains_compatible(self):
        target = self._target()

        attempt = self._attempt()

        self.assertEqual(target.read_text(encoding="utf-8"), "after\n")
        self.assertEqual(
            attempt["phase_99_apply_result_reference"]["source"],
            "bounded_operator_authorized_patch_apply",
        )

    def test_phase_100_101_verification_finalization_are_not_invoked(self):
        self._target()

        attempt = self._attempt()

        self.assertTrue(attempt["patch_not_verified"])
        self.assertTrue(attempt["not_finalized"])
        self.assertFalse(attempt["phase_99_apply_result_reference"]["verification_satisfied"])
        self.assertFalse(attempt["phase_99_apply_result_reference"]["task_completed"])


if __name__ == "__main__":
    unittest.main()
