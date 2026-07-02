import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.packet_result_patch_proposal_candidate as candidate_module
from orchestrator.packet_result_patch_proposal_candidate import (
    create_packet_result_patch_proposal_candidate,
    load_packet_result_patch_proposal_candidate,
)


class Phase289PacketResultPatchProposalCandidateArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.candidate_dir = self.root / "packet_patch_proposal_candidates"
        self.dir_patch = patch.object(
            candidate_module,
            "PACKET_PATCH_PROPOSAL_CANDIDATES_DIR",
            self.candidate_dir,
        )
        self.dir_patch.start()
        self.addCleanup(self.dir_patch.stop)
        self.artifact_path = self.root / "artifact.json"
        self.verifier_path = self.root / "verifier.json"
        self.artifact_path.write_text("{}", encoding="utf-8")
        self.verifier_path.write_text("{}", encoding="utf-8")

    def _eligibility_input(self):
        return {
            "task_id": "task_phase289",
            "packet_id": "packet_phase289",
            "run_id": "run_phase289",
            "packet_result": {
                "packet_id": "packet_phase289",
                "run_id": "run_phase289",
                "task_id": "task_phase289",
                "status": "completed",
                "execution_artifact_id": "artifact_phase289",
                "execution_artifact_path": str(self.artifact_path),
                "verifier_result_path": str(self.verifier_path),
                "patch_candidate_evidence": {
                    "evidence_id": "patch_candidate_evidence_phase289",
                    "proposed_changes": [
                        {
                            "path": "src/phase289.txt",
                            "description": "Bounded candidate-only evidence.",
                        }
                    ],
                    "unified_diff": "--- a/src/phase289.txt\n+++ b/src/phase289.txt\n",
                    "rationale": "Structured evidence for candidate persistence.",
                },
            },
            "current_success_review": {
                "task_id": "task_phase289",
                "run_id": "run_phase289",
                "final_outcome_classification": "completed_current_state_success",
                "ready_for_operator_review": True,
                "artifact_summary": {
                    "artifact_id": "artifact_phase289",
                    "artifact_path": str(self.artifact_path),
                },
                "verification_summary": {
                    "verifier_result_path": str(self.verifier_path),
                    "overall_passed": True,
                },
            },
            "operator_decision_summary": {
                "operator_decision_record_present": True,
                "operator_decision": "accepted",
                "accepted": True,
                "rejected": False,
                "operator_decision_record_id": "decision_phase289",
                "operator_decision_record_path": str(self.root / "decision.json"),
                "decided_at": "2026-07-01T00:00:00+00:00",
                "operator_note_present": True,
                "packet_id": "packet_phase289",
                "run_id": "run_phase289",
                "task_id": "task_phase289",
                "execution_artifact_id": "artifact_phase289",
                "verifier_result_path": str(self.verifier_path),
                "current_success_review_classification": "completed_current_state_success",
            },
        }

    def _create(self, **overrides):
        data = {
            "candidate_note": "Persist this as candidate-only evidence.",
            "eligibility_input": self._eligibility_input(),
        }
        data.update(overrides)
        return create_packet_result_patch_proposal_candidate(data)

    def test_eligible_accepted_packet_result_persists_candidate_artifact(self):
        result = self._create(candidate_id="candidate_phase289")
        loaded = load_packet_result_patch_proposal_candidate("candidate_phase289")

        self.assertTrue(result["candidate_artifact_created"])
        self.assertEqual(result["candidate_status"], "candidate_only")
        self.assertEqual(loaded["candidate_status"], "candidate_only")
        self.assertEqual(loaded["candidate_note"], "Persist this as candidate-only evidence.")

    def test_candidate_links_to_all_source_evidence(self):
        result = self._create(candidate_id="candidate_links_phase289")
        loaded = json.loads(Path(result["candidate_path"]).read_text(encoding="utf-8"))

        self.assertEqual(loaded["source_packet_id"], "packet_phase289")
        self.assertEqual(loaded["source_run_id"], "run_phase289")
        self.assertEqual(loaded["source_task_id"], "task_phase289")
        self.assertEqual(loaded["source_execution_artifact_id"], "artifact_phase289")
        self.assertEqual(loaded["source_verifier_result_path"], str(self.verifier_path))
        self.assertEqual(loaded["operator_decision_record_id"], "decision_phase289")
        self.assertEqual(loaded["eligibility_record"]["status"], "eligible")

    def test_ineligible_result_blocks_candidate_creation(self):
        eligibility_input = self._eligibility_input()
        eligibility_input["packet_result"]["patch_candidate_evidence"] = {}

        result = self._create(eligibility_input=eligibility_input)

        self.assertFalse(result["candidate_artifact_created"])
        self.assertEqual(result["candidate_status"], "blocked")
        self.assertIn("eligible_packet_result_required", result["blocked_conditions"])

    def test_rejected_result_blocks_candidate_creation(self):
        eligibility_input = self._eligibility_input()
        eligibility_input["operator_decision_summary"].update(
            {"operator_decision": "rejected", "accepted": False, "rejected": True}
        )

        result = self._create(eligibility_input=eligibility_input)

        self.assertFalse(result["candidate_artifact_created"])
        self.assertIn("operator_decision_not_accepted", result["blocked_conditions"])

    def test_mismatched_decision_evidence_blocks_candidate_creation(self):
        eligibility_input = self._eligibility_input()
        eligibility_input["operator_decision_summary"]["verifier_result_path"] = str(
            self.root / "other_verifier.json"
        )

        result = self._create(eligibility_input=eligibility_input)

        self.assertFalse(result["candidate_artifact_created"])
        self.assertIn("decision_evidence_link_mismatch", result["blocked_conditions"])

    def test_missing_candidate_note_blocks(self):
        result = self._create(candidate_note="")

        self.assertFalse(result["candidate_artifact_created"])
        self.assertEqual(result["reason_code"], "candidate_note_required")

    def test_candidate_output_explicitly_says_not_patch_authorization(self):
        result = self._create()

        self.assertTrue(result["no_apply_authorization"])
        self.assertTrue(result["candidate_is_not_patch_authorization"])
        self.assertFalse(result["patch_apply_authorized"])

    def test_candidate_output_explicitly_says_no_apply(self):
        result = self._create()

        self.assertTrue(result["candidate_is_not_patch_apply_request"])
        self.assertFalse(result["patch_applied"])

    def test_no_patch_apply_modules_are_invoked(self):
        with patch.dict("sys.modules", {"orchestrator.patch_apply": None}):
            result = self._create()

        self.assertTrue(result["candidate_artifact_created"])
        self.assertFalse(result["patch_applied"])

    def test_no_semantic_autonomous_model_provider_runtime_claims_appear(self):
        result = self._create()
        loaded = load_packet_result_patch_proposal_candidate(result["candidate_id"])
        serialized = json.dumps(loaded, sort_keys=True)

        self.assertIn("no_semantic_correctness_proof", serialized)
        self.assertIn("no_autonomous_ai_coding_proof", serialized)
        self.assertFalse(loaded["provider_executed"])
        self.assertFalse(loaded["model_executed"])
        self.assertFalse(loaded["runtime_executed"])
        self.assertFalse(loaded["platform_invoked"])

    def test_path_traversal_candidate_id_is_blocked(self):
        result = self._create(candidate_id="../candidate_phase289")

        self.assertFalse(result["candidate_artifact_created"])
        self.assertEqual(result["reason_code"], "candidate_id_invalid")

    def test_absolute_candidate_id_is_blocked(self):
        result = self._create(candidate_id="C:\\candidate_phase289")

        self.assertFalse(result["candidate_artifact_created"])
        self.assertEqual(result["reason_code"], "candidate_id_invalid")

    def test_candidate_summary_can_be_loaded_for_readback(self):
        result = self._create(candidate_id="candidate_readback_phase289")
        loaded = load_packet_result_patch_proposal_candidate("candidate_readback_phase289")

        self.assertEqual(loaded["candidate_id"], result["candidate_id"])
        self.assertEqual(loaded["candidate_status"], "candidate_only")


if __name__ == "__main__":
    unittest.main()
