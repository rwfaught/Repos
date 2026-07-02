import tempfile
import unittest
from pathlib import Path

from orchestrator.packet_result_patch_proposal_eligibility import (
    evaluate_packet_result_patch_proposal_eligibility,
)


class Phase288PacketResultToPatchProposalEligibilityContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.artifact_path = self.root / "artifact.json"
        self.verifier_path = self.root / "verifier.json"
        self.artifact_path.write_text("{}", encoding="utf-8")
        self.verifier_path.write_text("{}", encoding="utf-8")

    def _input(self, **overrides):
        data = {
            "task_id": "task_phase288",
            "packet_id": "packet_phase288",
            "run_id": "run_phase288",
            "packet_result": {
                "packet_id": "packet_phase288",
                "run_id": "run_phase288",
                "task_id": "task_phase288",
                "status": "completed",
                "execution_artifact_id": "artifact_phase288",
                "execution_artifact_path": str(self.artifact_path),
                "verifier_result_path": str(self.verifier_path),
                "patch_candidate_evidence": {
                    "evidence_id": "patch_candidate_evidence_phase288",
                    "proposed_changes": [
                        {
                            "path": "src/phase288.txt",
                            "description": "Bounded candidate evidence only.",
                        }
                    ],
                    "unified_diff": "--- a/src/phase288.txt\n+++ b/src/phase288.txt\n",
                    "rationale": "Candidate evidence is structured for later review.",
                },
            },
            "current_success_review": {
                "task_id": "task_phase288",
                "run_id": "run_phase288",
                "final_outcome_classification": "completed_current_state_success",
                "ready_for_operator_review": True,
                "artifact_summary": {
                    "artifact_id": "artifact_phase288",
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
                "operator_decision_record_id": "decision_phase288",
                "operator_decision_record_path": str(self.root / "decision.json"),
                "decided_at": "2026-07-01T00:00:00+00:00",
                "operator_note_present": True,
                "packet_id": "packet_phase288",
                "run_id": "run_phase288",
                "task_id": "task_phase288",
                "execution_artifact_id": "artifact_phase288",
                "verifier_result_path": str(self.verifier_path),
                "current_success_review_classification": "completed_current_state_success",
            },
        }
        data.update(overrides)
        return data

    def _result(self, **overrides):
        return evaluate_packet_result_patch_proposal_eligibility(self._input(**overrides))

    def test_accepted_completed_packet_with_required_evidence_returns_eligible(self):
        result = self._result()

        self.assertEqual(result["status"], "eligible")
        self.assertTrue(result["eligible"])
        self.assertEqual(result["missing_evidence"], [])
        self.assertEqual(
            result["reason_code"],
            "accepted_packet_result_has_patch_candidate_evidence",
        )

    def test_rejected_packet_result_returns_ineligible(self):
        data = self._input()
        data["operator_decision_summary"].update(
            {"operator_decision": "rejected", "accepted": False, "rejected": True}
        )

        result = evaluate_packet_result_patch_proposal_eligibility(data)

        self.assertEqual(result["status"], "ineligible")
        self.assertEqual(result["reason_code"], "operator_decision_not_accepted")
        self.assertIn("accepted_operator_decision", result["missing_evidence"])

    def test_missing_operator_decision_returns_blocked_with_exact_reason(self):
        result = self._result(operator_decision_summary={})

        self.assertEqual(result["status"], "blocked")
        self.assertIn("operator_decision_record", result["missing_evidence"])
        self.assertIn("operator_decision_missing", result["blocked_conditions"])

    def test_stale_or_mismatched_decision_links_are_blocked(self):
        data = self._input()
        data["operator_decision_summary"]["execution_artifact_id"] = "other_artifact"

        result = evaluate_packet_result_patch_proposal_eligibility(data)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("decision_evidence_link_mismatch", result["blocked_conditions"])
        self.assertIn("matching_execution_artifact_id", result["missing_evidence"])

    def test_missing_artifact_is_blocked(self):
        self.artifact_path.unlink()

        result = self._result()

        self.assertEqual(result["status"], "blocked")
        self.assertIn("execution_artifact_missing", result["blocked_conditions"])

    def test_missing_verifier_is_blocked(self):
        self.verifier_path.unlink()

        result = self._result()

        self.assertEqual(result["status"], "blocked")
        self.assertIn("verifier_result_missing", result["blocked_conditions"])

    def test_not_ready_current_success_is_blocked(self):
        data = self._input()
        data["current_success_review"]["final_outcome_classification"] = "needs_review"

        result = evaluate_packet_result_patch_proposal_eligibility(data)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("current_success_not_ready", result["blocked_conditions"])

    def test_missing_operator_note_is_blocked(self):
        data = self._input()
        data["operator_decision_summary"]["operator_note_present"] = False

        result = evaluate_packet_result_patch_proposal_eligibility(data)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("operator_note_missing", result["blocked_conditions"])

    def test_provider_model_runtime_platform_smuggling_is_blocked(self):
        data = self._input(model_name="qwen3.6:27b")

        result = evaluate_packet_result_patch_proposal_eligibility(data)

        self.assertEqual(result["status"], "blocked")
        self.assertIn(
            "provider_model_runtime_platform_claim_rejected",
            result["blocked_conditions"],
        )

    def test_semantic_correctness_claim_is_rejected_as_non_proof(self):
        data = self._input(semantic_correctness_claimed=True)

        result = evaluate_packet_result_patch_proposal_eligibility(data)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("semantic_correctness_claim_is_non_proof", result["blocked_conditions"])
        self.assertIn("no_semantic_correctness_proof", result["non_proofs"])

    def test_output_explicitly_says_no_patch_apply_authorization(self):
        result = self._result()

        self.assertTrue(result["no_apply_authorization"])
        self.assertFalse(result["patch_apply_authorized"])
        self.assertFalse(result["patch_applied"])

    def test_output_says_packet_acceptance_is_not_patch_authorization(self):
        result = self._result()

        self.assertTrue(result["packet_acceptance_is_not_patch_authorization"])
        self.assertIn(
            "packet_acceptance_is_not_patch_authorization",
            result["non_proofs"],
        )

    def test_current_success_readback_style_path_can_surface_summary(self):
        result = self._result()

        self.assertTrue(result["packet_result_patch_proposal_eligibility_surface"])
        self.assertEqual(result["task_id"], "task_phase288")
        self.assertIn("linked_evidence", result)

    def test_missing_structured_patch_candidate_evidence_is_ineligible(self):
        data = self._input()
        data["packet_result"]["patch_candidate_evidence"] = {
            "proposed_changes": [{"path": "src/phase288.txt", "description": "Only partial."}]
        }

        result = evaluate_packet_result_patch_proposal_eligibility(data)

        self.assertEqual(result["status"], "ineligible")
        self.assertEqual(
            result["reason_code"],
            "structured_patch_candidate_evidence_missing",
        )
        self.assertIn(
            "structured_patch_candidate_evidence.unified_diff",
            result["missing_evidence"],
        )


if __name__ == "__main__":
    unittest.main()
