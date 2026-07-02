import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.packet_result_patch_proposal_candidate as candidate_module
import orchestrator.patch_proposal_candidate_promotion as promotion_module
from orchestrator.packet_cli_residue_guard import inspect_packet_cli_generated_residue
from orchestrator.packet_result_patch_proposal_candidate import (
    create_packet_result_patch_proposal_candidate,
)
from orchestrator.packet_result_patch_proposal_eligibility import (
    evaluate_packet_result_patch_proposal_eligibility,
)
from orchestrator.patch_proposal_candidate_promotion import (
    create_patch_proposal_candidate_promotion_record,
)


class Phase291PacketToPatchBridgeNegativeEdgeContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.artifact_path = self.root / "artifact.json"
        self.verifier_path = self.root / "verifier.json"
        self.artifact_path.write_text("{}", encoding="utf-8")
        self.verifier_path.write_text("{}", encoding="utf-8")
        self.candidate_dir = self.root / "candidates"
        self.promotion_dir = self.root / "promotions"
        self.candidate_patch = patch.object(
            candidate_module,
            "PACKET_PATCH_PROPOSAL_CANDIDATES_DIR",
            self.candidate_dir,
        )
        self.promotion_patch = patch.object(
            promotion_module,
            "PATCH_PROPOSAL_CANDIDATE_PROMOTIONS_DIR",
            self.promotion_dir,
        )
        self.candidate_patch.start()
        self.promotion_patch.start()
        self.addCleanup(self.candidate_patch.stop)
        self.addCleanup(self.promotion_patch.stop)

    def _eligibility_input(self, **overrides):
        data = {
            "task_id": "task_phase291",
            "packet_id": "packet_phase291",
            "run_id": "run_phase291",
            "packet_result": {
                "packet_id": "packet_phase291",
                "run_id": "run_phase291",
                "task_id": "task_phase291",
                "status": "completed",
                "execution_artifact_id": "artifact_phase291",
                "execution_artifact_path": str(self.artifact_path),
                "verifier_result_path": str(self.verifier_path),
                "patch_candidate_evidence": {
                    "evidence_id": "evidence_phase291",
                    "proposed_changes": [{"path": "src/phase291.txt", "description": "Candidate evidence."}],
                    "unified_diff": "--- a/src/phase291.txt\n+++ b/src/phase291.txt\n",
                    "rationale": "Structured evidence.",
                },
            },
            "current_success_review": {
                "task_id": "task_phase291",
                "run_id": "run_phase291",
                "final_outcome_classification": "completed_current_state_success",
                "ready_for_operator_review": True,
                "artifact_summary": {
                    "artifact_id": "artifact_phase291",
                    "artifact_path": str(self.artifact_path),
                },
                "verification_summary": {"verifier_result_path": str(self.verifier_path)},
            },
            "operator_decision_summary": {
                "operator_decision_record_present": True,
                "operator_decision": "accepted",
                "accepted": True,
                "rejected": False,
                "operator_decision_record_id": "decision_phase291",
                "operator_decision_record_path": str(self.root / "decision.json"),
                "operator_note_present": True,
                "packet_id": "packet_phase291",
                "run_id": "run_phase291",
                "task_id": "task_phase291",
                "execution_artifact_id": "artifact_phase291",
                "verifier_result_path": str(self.verifier_path),
                "current_success_review_classification": "completed_current_state_success",
            },
        }
        data.update(overrides)
        return data

    def _candidate(self, **overrides):
        result = create_packet_result_patch_proposal_candidate(
            {
                "candidate_note": "Candidate-only note.",
                "eligibility_input": self._eligibility_input(),
            }
        )
        candidate = {
            "candidate_id": result["candidate_id"],
            "candidate_status": "candidate_only",
            "source_task_id": "task_phase291",
            "source_execution_artifact_id": "artifact_phase291",
            "source_verifier_result_path": str(self.verifier_path),
            "eligibility_record": {"status": "eligible"},
            "no_apply_authorization": True,
            "patch_apply_authorized": False,
            "patch_applied": False,
        }
        candidate.update(overrides)
        return candidate

    def test_missing_accepted_decision_blocks_with_reason_code(self):
        data = self._eligibility_input(operator_decision_summary={})

        result = evaluate_packet_result_patch_proposal_eligibility(data)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("operator_decision_missing", result["blocked_conditions"])

    def test_rejected_decision_returns_ineligible_shape(self):
        data = self._eligibility_input()
        data["operator_decision_summary"].update({"accepted": False, "rejected": True, "operator_decision": "rejected"})

        result = evaluate_packet_result_patch_proposal_eligibility(data)

        self.assertEqual(result["status"], "ineligible")
        self.assertEqual(result["reason_code"], "operator_decision_not_accepted")

    def test_deferred_or_rejected_candidate_blocks_promotion(self):
        result = create_patch_proposal_candidate_promotion_record(
            {
                "operator_decision": "promote_to_patch_proposal_candidate_ready",
                "operator_note": "Try to promote rejected candidate.",
                "candidate": self._candidate(candidate_status="candidate_rejected"),
            }
        )

        self.assertFalse(result["promotion_record_created"])
        self.assertIn("candidate_only_status_required", result["blocked_conditions"])

    def test_multiple_latest_decision_rejected_is_ineligible_when_supplied(self):
        data = self._eligibility_input()
        data["operator_decision_summary"].update({"accepted": False, "rejected": True, "operator_decision": "rejected"})

        result = evaluate_packet_result_patch_proposal_eligibility(data)

        self.assertEqual(result["status"], "ineligible")
        self.assertIn("accepted_operator_decision", result["missing_evidence"])

    def test_mismatched_task_artifact_and_verifier_links_block(self):
        data = self._eligibility_input(task_id="task_phase291_other")
        data["operator_decision_summary"]["task_id"] = "task_phase291"
        data["operator_decision_summary"]["execution_artifact_id"] = "other_artifact"
        data["operator_decision_summary"]["verifier_result_path"] = str(self.root / "other_verifier.json")

        result = evaluate_packet_result_patch_proposal_eligibility(data)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("decision_evidence_link_mismatch", result["blocked_conditions"])

    def test_missing_current_success_eligibility_candidate_and_promotion_records_block(self):
        eligibility = evaluate_packet_result_patch_proposal_eligibility(
            self._eligibility_input(current_success_review={"final_outcome_classification": "blocked"})
        )
        candidate = create_packet_result_patch_proposal_candidate(
            {"candidate_note": "No eligible source.", "eligibility": {"status": "blocked", "reason_code": "missing_eligibility_record"}}
        )
        promotion = create_patch_proposal_candidate_promotion_record(
            {"operator_decision": "promote_to_patch_proposal_candidate_ready", "operator_note": "Missing candidate."}
        )

        self.assertEqual(eligibility["status"], "blocked")
        self.assertFalse(candidate["candidate_artifact_created"])
        self.assertFalse(promotion["promotion_record_created"])

    def test_path_traversal_posix_absolute_windows_absolute_and_separators_block(self):
        bad_ids = ["../candidate", "/candidate", "C:\\candidate", "candidate\\nested"]
        for bad_id in bad_ids:
            result = create_packet_result_patch_proposal_candidate(
                {
                    "candidate_id": bad_id,
                    "candidate_note": "Unsafe id.",
                    "eligibility_input": self._eligibility_input(),
                }
            )
            self.assertFalse(result["candidate_artifact_created"], bad_id)
            self.assertEqual(result["reason_code"], "candidate_id_invalid", bad_id)

    def test_smuggled_claims_block_or_remain_non_proofs(self):
        for field in ("model_name", "provider", "runtime", "platform", "production_readiness_claimed", "semantic_correctness_claimed", "autonomous_ai_coding_claimed", "apply_authorized"):
            result = evaluate_packet_result_patch_proposal_eligibility(
                self._eligibility_input(**{field: True})
            )
            self.assertEqual(result["status"], "blocked", field)
            self.assertFalse(result["patch_apply_authorized"], field)
            self.assertIn("no_semantic_correctness_proof", result["non_proofs"], field)

    def test_attempt_to_invoke_apply_from_candidate_or_promotion_path_blocks(self):
        candidate = self._candidate(patch_apply_authorized=True)
        result = create_patch_proposal_candidate_promotion_record(
            {
                "operator_decision": "promote_to_patch_proposal_candidate_ready",
                "operator_note": "Apply smuggling should block.",
                "candidate": candidate,
            }
        )

        self.assertFalse(result["promotion_record_created"])
        self.assertIn("apply_authorization_smuggling_rejected", result["blocked_conditions"])
        self.assertFalse(result["patch_applied"])

    def test_no_cleanup_deletion_or_apply_occurs_for_negative_shapes(self):
        result = create_patch_proposal_candidate_promotion_record(
            {
                "operator_decision": "promote_to_patch_proposal_candidate_ready",
                "operator_note": "Already applied should block.",
                "candidate": self._candidate(patch_applied=True),
            }
        )

        self.assertFalse(result["promotion_record_created"])
        self.assertFalse(result["patch_applied"])
        self.assertFalse(result["patch_apply_authorized"])

    def test_generated_residue_is_reported_without_cleanup(self):
        output = self.root / "outputs" / "phase291.txt"
        output.parent.mkdir(parents=True)
        output.write_text("generated", encoding="utf-8")

        result = inspect_packet_cli_generated_residue(self.root)

        self.assertTrue(result["residue_present"])
        self.assertEqual(result["generated_paths"], ["outputs/phase291.txt"])
        self.assertFalse(result["cleanup_performed"])
        self.assertFalse(result["delete_performed"])
        self.assertFalse(result["archive_performed"])

    def test_error_readback_shapes_include_reason_codes_and_no_provider_claims(self):
        result = evaluate_packet_result_patch_proposal_eligibility(
            self._eligibility_input(task_id="../unsafe")
        )

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason_code"], "task_id_invalid_or_missing")
        self.assertFalse(result["provider_executed"])
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["runtime_executed"])
        self.assertFalse(result["platform_invoked"])


if __name__ == "__main__":
    unittest.main()
