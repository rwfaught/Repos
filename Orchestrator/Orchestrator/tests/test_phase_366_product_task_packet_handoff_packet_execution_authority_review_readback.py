import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_execution_authority_review_readback import (
    BOUNDARY,
    MARKER,
    NAME,
    read_product_task_packet_handoff_packet_execution_authority_review_readback,
)


MARKER_TEXT = "PHASE366_PRODUCT_TASK_PACKET_HANDOFF_PACKET_EXECUTION_AUTHORITY_REVIEW_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase366HandoffPacketExecutionAuthorityReviewReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_execution_authority_review_readback()

    def test_deterministic_identity(self):
        self.assertEqual(
            self.readback,
            read_product_task_packet_handoff_packet_execution_authority_review_readback(),
        )
        self.assertEqual(self.readback["phase"], 366)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_execution_authority_review_posture_is_non_executing(self):
        self.assertIn("deterministic and non-executing", self.readback["execution_authority_review_purpose"])
        self.assertFalse(self.readback["authority_status_recommendation"]["execution_authority_granted"])
        self.assertIn(
            "execution authority is absent in this phase",
            self.readback["authority_inference_and_recommendation"],
        )

    def test_ready_state_is_distinguished_from_execution_authority(self):
        recommendation = self.readback["authority_status_recommendation"]
        self.assertEqual(recommendation["ready_state_status"], "ready_for_next_bounded_move_readback_only")
        self.assertFalse(recommendation["ready_state_is_execution_authority"])
        self.assertIn("Ready state is not execution authority", self.readback["accepted_facts"])
        self.assertIn("ready state is not execution authority", self.readback["non_proof_caveats"])

    def test_accepted_facts_are_separated_from_authority_inference(self):
        self.assertTrue(self.readback["accepted_facts"])
        self.assertTrue(self.readback["authority_inputs"])
        self.assertTrue(self.readback["authority_inference_and_recommendation"])
        self.assertNotEqual(
            self.readback["accepted_facts"],
            self.readback["authority_inference_and_recommendation"],
        )

    def test_authority_gates_and_blocking_conditions_are_represented(self):
        for gate in (
            "exact current boundary present",
            "source basis through Phase 365 identified",
            "accepted facts separated from authority inference/recommendation",
            "ready-state status distinguished from execution authority",
            "missing authority represented as blocking condition",
            "production readiness remains false",
        ):
            self.assertIn(gate, self.readback["authority_gates"])
        for condition in (
            "missing boundary",
            "missing authority inputs",
            "missing explicit execution-authority evidence",
            "ready-state status treated as execution authority",
            "lockout violation",
        ):
            self.assertIn(condition, self.readback["blocking_conditions"])

    def test_authority_recommendation_does_not_equal_execution(self):
        recommendation = self.readback["authority_status_recommendation"]
        self.assertEqual(recommendation["status"], "execution_authority_absent_readback_only")
        self.assertFalse(recommendation["execution_authority_granted"])
        self.assertFalse(recommendation["authorized_to_execute_handoff_packet"])
        self.assertIn(
            "execution-authority review is not execution",
            self.readback["non_proof_caveats"],
        )

    def test_false_activity_flags_remain_false(self):
        for flag in (
            "handoff_executed",
            "handoff_packet_executed",
            "worker_dispatched",
            "patch_applied",
            "route_selection_executed",
            "provider_model_executed",
            "runtime_provider_model_platform_executed",
            "service_api_ui_dashboard_auth_deployment_executed",
            "next_boundary_executed",
            "source_files_refreshed",
            "capsule_export_package_refreshed",
            "execution_authority_granted",
            "semantic_correctness_proven",
            "production_readiness_proven",
            "official_capsule_proof_superseded_phase_335",
        ):
            self.assertIn(flag, self.readback["false_activity_flags"])
            self.assertFalse(self.readback["false_activity_flags"][flag])

    def test_non_proofs_and_production_readiness_are_preserved(self):
        for caveat in (
            "execution-authority review is not execution",
            "execution-authority review is not handoff execution",
            "execution-authority review is not handoff packet execution",
            "execution-authority review is not worker dispatch",
            "execution-authority review is not patch application",
            "execution-authority review is not route selection execution",
            "execution-authority review is not provider/model execution",
            "execution-authority review is not next-boundary execution",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["non_proof_caveats"])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No Phase 367 implementation", self.readback["lockout_text"])

    def test_future_phase_absence_doctrine_does_not_assert_permanent_absence(self):
        self.assertIn(
            "tests must not assert permanent absence of future phases",
            self.readback["future_phase_assertion_doctrine"],
        )
        self.assertIn(
            "tests may assert that the current phase did not implement the future phase",
            self.readback["future_phase_assertion_doctrine"],
        )

    def test_marker_appears_in_source_test_docs_and_ledgers(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_packet_execution_authority_review_readback.py",
            "tests/test_phase_366_product_task_packet_handoff_packet_execution_authority_review_readback.py",
            "docs/PHASE_366.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
