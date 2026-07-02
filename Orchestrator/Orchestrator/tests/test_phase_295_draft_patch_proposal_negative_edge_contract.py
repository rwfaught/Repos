import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.promoted_candidate_draft_patch_proposal as draft_module
from orchestrator.packet_cli_residue_guard import inspect_packet_cli_generated_residue
from orchestrator.promoted_candidate_draft_patch_proposal import (
    create_promoted_candidate_draft_patch_proposal,
)


class Phase295DraftPatchProposalNegativeEdgeContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.draft_dir = self.root / "drafts"
        self.dir_patch = patch.object(
            draft_module,
            "DRAFT_PATCH_PROPOSALS_DIR",
            self.draft_dir,
        )
        self.dir_patch.start()
        self.addCleanup(self.dir_patch.stop)

    def _candidate(self, **overrides):
        candidate = {
            "artifact_type": "packet_result_patch_proposal_candidate",
            "candidate_id": "candidate_phase295",
            "candidate_status": "candidate_only",
            "source_packet_id": "packet_phase295",
            "source_run_id": "run_phase295",
            "source_task_id": "task_phase295",
            "source_execution_artifact_id": "artifact_phase295",
            "source_execution_artifact_path": str(self.root / "artifact.json"),
            "source_verifier_result_path": str(self.root / "verifier.json"),
            "current_success_review_reference": {
                "task_id": "task_phase295",
                "run_id": "run_phase295",
                "classification": "completed_current_state_success",
                "ready_for_operator_review": True,
            },
            "operator_decision_record_id": "decision_phase295",
            "operator_decision_record_path": str(self.root / "decision.json"),
            "eligibility_record": {
                "status": "eligible",
                "task_id": "task_phase295",
                "packet_id": "packet_phase295",
                "run_id": "run_phase295",
            },
            "proposed_patch_evidence_payload": {
                "evidence_id": "patch_evidence_phase295",
                "proposed_changes": [
                    {
                        "path": "src/phase295.txt",
                        "description": "Draft-only negative-edge evidence.",
                    }
                ],
                "unified_diff": "--- a/src/phase295.txt\n+++ b/src/phase295.txt\n",
                "rationale": "Structured draft proposal evidence.",
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
            "promotion_record_id": "promotion_phase295",
            "promotion_status": "candidate_ready_for_later_patch_proposal_boundary",
            "operator_decision": "promote_to_patch_proposal_candidate_ready",
            "operator_note": "Promote for a later draft-only boundary.",
            "candidate_id": "candidate_phase295",
            "source_packet_id": "packet_phase295",
            "source_run_id": "run_phase295",
            "source_task_id": "task_phase295",
            "source_execution_artifact_id": "artifact_phase295",
            "source_execution_artifact_path": str(self.root / "artifact.json"),
            "source_verifier_result_path": str(self.root / "verifier.json"),
            "operator_decision_record_id": "decision_phase295",
            "no_apply_authorization": True,
            "promotion_is_not_patch_apply_authorization": True,
            "patch_apply_authorized": False,
            "patch_applied": False,
            "non_proofs": ["no_semantic_correctness_proof"],
        }
        promotion.update(overrides)
        return promotion

    def _input(self, **overrides):
        data = {
            "draft_proposal_id": "draft_phase295",
            "draft_note": "Create a draft-only negative-edge proposal artifact.",
            "candidate": self._candidate(),
            "promotion_record": self._promotion(),
        }
        data.update(overrides)
        return data

    def _blocked(self, data):
        sentinel = self.root / "sentinel_keep.txt"
        sentinel.write_text("do not delete", encoding="utf-8")
        result = create_promoted_candidate_draft_patch_proposal(data)

        self.assertFalse(result["draft_patch_proposal_created"])
        self.assertIn(result["draft_proposal_status"], {"blocked"})
        self.assertTrue(result["reason_code"])
        self.assertTrue(result["not_authorized_for_apply"])
        self.assertTrue(result["not_applied"])
        self.assertFalse(result["patch_apply_authorized"])
        self.assertFalse(result["patch_applied"])
        self.assertFalse(result["provider_executed"])
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["runtime_executed"])
        self.assertFalse(result["platform_invoked"])
        self.assertFalse(result["semantic_correctness_claimed"])
        self.assertFalse(result["autonomous_ai_coding_claimed"])
        self.assertFalse(result["production_readiness_claimed"])
        self.assertTrue(sentinel.exists())
        self.assertFalse((self.draft_dir / "draft_phase295.json").exists())
        return result

    def test_missing_candidate_returns_deterministic_reason(self):
        result = self._blocked({"draft_note": "Need a candidate."})

        self.assertEqual(result["reason_code"], "candidate_required")
        self.assertIn("candidate_required", result["blocked_conditions"])

    def test_rejected_deferred_and_missing_promotion_note_block(self):
        cases = [
            (
                self._promotion(
                    promotion_status="candidate_rejected",
                    operator_decision="reject_candidate",
                ),
                "promoted_candidate_required",
            ),
            (
                self._promotion(
                    promotion_status="candidate_deferred",
                    operator_decision="defer_candidate",
                ),
                "promoted_candidate_required",
            ),
            (self._promotion(operator_note=""), "promotion_note_required"),
        ]

        for promotion, reason in cases:
            with self.subTest(reason=reason):
                result = self._blocked(self._input(promotion_record=promotion))
                self.assertIn(reason, result["blocked_conditions"])

    def test_latest_reject_or_defer_promotion_beats_older_promote(self):
        result = self._blocked(
            self._input(
                promotion_record=None,
                promotion_records=[
                    self._promotion(created_at="2026-07-02T01:00:00+00:00"),
                    self._promotion(
                        promotion_record_id="promotion_phase295_reject",
                        promotion_status="candidate_rejected",
                        operator_decision="reject_candidate",
                        created_at="2026-07-02T02:00:00+00:00",
                    ),
                ],
            )
        )

        self.assertIn("promoted_candidate_required", result["blocked_conditions"])

    def test_mismatched_task_artifact_verifier_current_success_and_decision_block(self):
        cases = [
            (
                self._candidate(source_task_id="task_other"),
                self._promotion(),
                "promotion_candidate_evidence_mismatch",
            ),
            (
                self._candidate(source_execution_artifact_id="artifact_other"),
                self._promotion(),
                "promotion_candidate_evidence_mismatch",
            ),
            (
                self._candidate(source_verifier_result_path=str(self.root / "other.json")),
                self._promotion(),
                "promotion_candidate_evidence_mismatch",
            ),
            (
                self._candidate(
                    current_success_review_reference={
                        "task_id": "task_other",
                        "run_id": "run_phase295",
                        "classification": "completed_current_state_success",
                        "ready_for_operator_review": True,
                    }
                ),
                self._promotion(),
                "current_success_reference_mismatch",
            ),
            (
                self._candidate(operator_decision_record_id=""),
                self._promotion(),
                "operator_decision_reference_required",
            ),
        ]

        for candidate, promotion, reason in cases:
            with self.subTest(reason=reason):
                result = self._blocked(
                    self._input(candidate=candidate, promotion_record=promotion)
                )
                self.assertIn(reason, result["blocked_conditions"])

    def test_missing_references_and_patch_payloads_block_with_exact_reason_codes(self):
        cases = [
            (
                self._candidate(current_success_review_reference={}),
                "current_success_reference_required",
            ),
            (self._candidate(eligibility_record={}), "eligible_candidate_required"),
            (
                self._candidate(operator_decision_record_path=""),
                "operator_decision_reference_required",
            ),
            (
                self._candidate(proposed_patch_evidence_payload={}),
                "structured_patch_payload_missing",
            ),
            (
                self._candidate(
                    proposed_patch_evidence_payload={
                        "proposed_changes": [{"description": "missing path"}],
                        "unified_diff": "--- a/x\n+++ b/x\n",
                        "rationale": "Ambiguous patch.",
                    }
                ),
                "ambiguous_patch_payload_rejected",
            ),
        ]

        for candidate, reason in cases:
            with self.subTest(reason=reason):
                result = self._blocked(self._input(candidate=candidate))
                self.assertIn(reason, result["blocked_conditions"])

    def test_path_traversal_absolute_paths_and_windows_separators_block(self):
        for bad_path, reason in [
            ("../src/phase295.txt", "path_traversal_rejected"),
            ("/src/phase295.txt", "absolute_patch_path_rejected"),
            ("C:\\src\\phase295.txt", "absolute_patch_path_rejected"),
            ("src\\phase295.txt", "unsafe_patch_path_rejected"),
        ]:
            with self.subTest(bad_path=bad_path):
                payload = dict(self._candidate()["proposed_patch_evidence_payload"])
                payload["proposed_changes"] = [{"path": bad_path}]
                result = self._blocked(
                    self._input(
                        candidate=self._candidate(
                            proposed_patch_evidence_payload=payload
                        )
                    )
                )
                self.assertIn(reason, result["blocked_conditions"])

    def test_provider_semantic_autonomous_production_and_apply_smuggling_block(self):
        cases = [
            ("model_name", "qwen3.6:27b", "provider_model_runtime_platform_claim_rejected"),
            ("semantic_correctness_claimed", True, "semantic_correctness_claim_is_non_proof"),
            ("autonomous_ai_coding_claimed", True, "autonomous_ai_coding_claim_rejected"),
            ("production_readiness_claimed", True, "production_readiness_claim_rejected"),
            ("patch_apply_authorized", True, "apply_authorization_smuggling_rejected"),
        ]

        for field, value, reason in cases:
            with self.subTest(field=field):
                result = self._blocked(self._input(candidate=self._candidate(**{field: value})))
                self.assertIn(reason, result["blocked_conditions"])

    def test_text_claim_smuggling_and_attempted_apply_invocation_do_not_authorize(self):
        payload = dict(self._candidate()["proposed_patch_evidence_payload"])
        payload["rationale"] = "This is production ready and authorized for apply."

        with patch.dict("sys.modules", {"orchestrator.patch_apply_engine": None}):
            result = self._blocked(
                self._input(
                    candidate=self._candidate(proposed_patch_evidence_payload=payload)
                )
            )

        self.assertIn("production_readiness_claim_rejected", result["blocked_conditions"])
        self.assertIn(
            "patch_apply_authorization_claim_rejected",
            result["blocked_conditions"],
        )
        self.assertFalse(result["patch_applied"])

    def test_generated_residue_guard_reports_without_cleanup_or_deletion(self):
        output = self.root / "outputs" / "phase295.txt"
        output.parent.mkdir(parents=True)
        output.write_text("generated", encoding="utf-8")

        result = inspect_packet_cli_generated_residue(self.root)

        self.assertTrue(result["residue_present"])
        self.assertEqual(result["generated_paths"], ["outputs/phase295.txt"])
        self.assertFalse(result["cleanup_performed"])
        self.assertFalse(result["delete_performed"])
        self.assertFalse(result["archive_performed"])

    def test_success_still_returns_draft_only_not_authorized_shape(self):
        result = create_promoted_candidate_draft_patch_proposal(self._input())

        self.assertTrue(result["draft_patch_proposal_created"])
        self.assertEqual(result["draft_proposal_status"], "draft_only")
        self.assertTrue(result["draft_only"])
        self.assertTrue(result["not_authorized_for_apply"])
        self.assertFalse(result["patch_apply_authorized"])
        self.assertFalse(result["patch_applied"])


if __name__ == "__main__":
    unittest.main()
