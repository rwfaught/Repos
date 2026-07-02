import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.promoted_candidate_draft_patch_proposal as draft_module
from orchestrator.promoted_candidate_draft_patch_proposal import (
    create_promoted_candidate_draft_patch_proposal,
    load_draft_patch_proposal,
)


class Phase294PromotedCandidateDraftPatchProposalArtifactTests(unittest.TestCase):
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
            "candidate_id": "candidate_phase294",
            "candidate_status": "candidate_only",
            "source_packet_id": "packet_phase294",
            "source_run_id": "run_phase294",
            "source_task_id": "task_phase294",
            "source_execution_artifact_id": "artifact_phase294",
            "source_execution_artifact_path": str(self.root / "artifact.json"),
            "source_verifier_result_path": str(self.root / "verifier.json"),
            "current_success_review_reference": {
                "task_id": "task_phase294",
                "run_id": "run_phase294",
                "classification": "completed_current_state_success",
                "ready_for_operator_review": True,
            },
            "operator_decision_record_id": "decision_phase294",
            "operator_decision_record_path": str(self.root / "decision.json"),
            "eligibility_record": {
                "status": "eligible",
                "task_id": "task_phase294",
                "packet_id": "packet_phase294",
                "run_id": "run_phase294",
                "reason_code": "accepted_packet_result_has_patch_candidate_evidence",
            },
            "candidate_note": "Candidate-only note.",
            "proposed_patch_evidence_payload": {
                "evidence_id": "patch_evidence_phase294",
                "proposed_changes": [
                    {
                        "path": "src/phase294.txt",
                        "description": "Draft-only evidence.",
                    }
                ],
                "unified_diff": "--- a/src/phase294.txt\n+++ b/src/phase294.txt\n",
                "rationale": "Structured draft proposal evidence.",
            },
            "linked_evidence": [
                {
                    "evidence_type": "execution_artifact",
                    "evidence_id": "artifact_phase294",
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
            "promotion_record_id": "promotion_phase294",
            "promotion_status": "candidate_ready_for_later_patch_proposal_boundary",
            "operator_decision": "promote_to_patch_proposal_candidate_ready",
            "operator_note": "Promote for a later draft-only boundary.",
            "candidate_id": "candidate_phase294",
            "source_packet_id": "packet_phase294",
            "source_run_id": "run_phase294",
            "source_task_id": "task_phase294",
            "source_execution_artifact_id": "artifact_phase294",
            "source_execution_artifact_path": str(self.root / "artifact.json"),
            "source_verifier_result_path": str(self.root / "verifier.json"),
            "operator_decision_record_id": "decision_phase294",
            "no_apply_authorization": True,
            "promotion_is_not_patch_apply_authorization": True,
            "patch_apply_authorized": False,
            "patch_applied": False,
            "non_proofs": ["no_semantic_correctness_proof"],
        }
        promotion.update(overrides)
        return promotion

    def _create(self, **overrides):
        data = {
            "draft_proposal_id": "draft_phase294",
            "draft_note": "Create a draft-only proposal artifact.",
            "candidate": self._candidate(),
            "promotion_record": self._promotion(),
        }
        data.update(overrides)
        return create_promoted_candidate_draft_patch_proposal(data)

    def test_promoted_candidate_with_sufficient_evidence_creates_draft_artifact(self):
        result = self._create()
        loaded = load_draft_patch_proposal("draft_phase294")

        self.assertTrue(result["draft_patch_proposal_created"])
        self.assertEqual(result["draft_proposal_status"], "draft_only")
        self.assertEqual(loaded["artifact_type"], "draft_patch_proposal")
        self.assertEqual(loaded["source_candidate_id"], "candidate_phase294")

    def test_draft_links_to_packet_task_artifact_verifier_decision_and_bridge_evidence(self):
        result = self._create()
        loaded = json.loads(Path(result["draft_proposal_path"]).read_text(encoding="utf-8"))

        self.assertEqual(loaded["source_packet_id"], "packet_phase294")
        self.assertEqual(loaded["source_run_id"], "run_phase294")
        self.assertEqual(loaded["source_task_id"], "task_phase294")
        self.assertEqual(loaded["source_execution_artifact_id"], "artifact_phase294")
        self.assertEqual(loaded["source_verifier_result_path"], str(self.root / "verifier.json"))
        self.assertEqual(loaded["operator_decision_record_id"], "decision_phase294")
        self.assertEqual(loaded["phase_288_eligibility_reference"]["status"], "eligible")
        self.assertEqual(loaded["phase_289_candidate_reference"]["candidate_id"], "candidate_phase294")
        self.assertEqual(loaded["phase_290_promotion_reference"]["promotion_record_id"], "promotion_phase294")

    def test_unpromoted_candidate_blocks_draft_creation(self):
        result = self._create(promotion_record={})

        self.assertFalse(result["draft_patch_proposal_created"])
        self.assertEqual(result["reason_code"], "promotion_record_required")

    def test_rejected_candidate_blocks_draft_creation(self):
        result = self._create(
            promotion_record=self._promotion(
                promotion_status="candidate_rejected",
                operator_decision="reject_candidate",
            )
        )

        self.assertFalse(result["draft_patch_proposal_created"])
        self.assertIn("promoted_candidate_required", result["blocked_conditions"])

    def test_deferred_candidate_blocks_draft_creation(self):
        result = self._create(
            promotion_record=self._promotion(
                promotion_status="candidate_deferred",
                operator_decision="defer_candidate",
            )
        )

        self.assertFalse(result["draft_patch_proposal_created"])
        self.assertIn("promoted_candidate_required", result["blocked_conditions"])

    def test_stale_or_mismatched_promotion_blocks_draft_creation(self):
        result = self._create(
            promotion_record=self._promotion(source_verifier_result_path="other.json")
        )

        self.assertFalse(result["draft_patch_proposal_created"])
        self.assertIn("promotion_candidate_evidence_mismatch", result["blocked_conditions"])

    def test_missing_draft_note_reason_blocks(self):
        result = self._create(draft_note="")

        self.assertFalse(result["draft_patch_proposal_created"])
        self.assertEqual(result["reason_code"], "draft_note_required")

    def test_missing_structured_patch_payload_blocks_with_exact_missing_fields(self):
        candidate = self._candidate(proposed_patch_evidence_payload={"proposed_changes": []})

        result = self._create(candidate=candidate)

        self.assertFalse(result["draft_patch_proposal_created"])
        self.assertEqual(result["reason_code"], "structured_patch_payload_missing")
        self.assertIn("proposed_patch_evidence_payload.unified_diff", result["missing_requirements"])
        self.assertIn("proposed_patch_evidence_payload.rationale", result["missing_requirements"])

    def test_draft_status_is_draft_only(self):
        result = self._create()

        self.assertEqual(result["draft_proposal_status"], "draft_only")
        self.assertTrue(result["draft_only"])

    def test_draft_is_marked_not_authorized_for_apply(self):
        result = self._create()
        loaded = load_draft_patch_proposal(result["draft_proposal_id"])

        self.assertTrue(result["not_authorized_for_apply"])
        self.assertTrue(loaded["not_authorized_for_apply"])
        self.assertFalse(loaded["patch_apply_authorized"])

    def test_draft_is_marked_not_applied(self):
        result = self._create()
        loaded = load_draft_patch_proposal(result["draft_proposal_id"])

        self.assertTrue(result["not_applied"])
        self.assertTrue(loaded["not_applied"])
        self.assertFalse(loaded["patch_applied"])

    def test_no_apply_function_path_is_invoked(self):
        with patch.dict("sys.modules", {"orchestrator.patch_apply_engine": None}):
            result = self._create()

        self.assertTrue(result["draft_patch_proposal_created"])
        self.assertFalse(result["patch_applied"])

    def test_no_semantic_correctness_claim_becomes_proof(self):
        result = self._create()
        loaded = load_draft_patch_proposal(result["draft_proposal_id"])

        self.assertIn("no_semantic_correctness_proof", loaded["non_proofs"])
        self.assertFalse(loaded["semantic_correctness_claimed"])

    def test_no_autonomous_model_provider_runtime_platform_claim_appears(self):
        result = self._create()
        loaded = load_draft_patch_proposal(result["draft_proposal_id"])

        self.assertIn("no_autonomous_ai_coding_proof", loaded["non_proofs"])
        self.assertFalse(loaded["provider_executed"])
        self.assertFalse(loaded["model_executed"])
        self.assertFalse(loaded["runtime_executed"])
        self.assertFalse(loaded["platform_invoked"])

    def test_path_traversal_and_absolute_draft_ids_are_blocked(self):
        for bad_id in ("../draft", "/draft", "C:\\draft", "draft\\nested"):
            result = self._create(draft_proposal_id=bad_id)
            self.assertFalse(result["draft_patch_proposal_created"], bad_id)
            self.assertEqual(result["reason_code"], "draft_proposal_id_invalid", bad_id)


if __name__ == "__main__":
    unittest.main()
