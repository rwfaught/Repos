import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_escalation_outcome_review_blocker_readback import (
    BOUNDARY,
    MARKER,
    NAME,
    read_product_task_packet_handoff_packet_escalation_outcome_review_blocker_readback,
)


MARKER_TEXT = "PHASE381_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_OUTCOME_REVIEW_BLOCKER_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase381HandoffPacketEscalationOutcomeReviewBlockerReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_escalation_outcome_review_blocker_readback()

    def test_identity_is_deterministic(self):
        self.assertEqual(self.readback, read_product_task_packet_handoff_packet_escalation_outcome_review_blocker_readback())
        self.assertEqual(self.readback["phase"], 381)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_review_blocker_posture_is_readback_only(self):
        self.assertIn("readback only", self.readback["purpose"])
        self.assertEqual(self.readback["review_blocker_status"]["status"], "escalation_outcome_review_blocker_readback_only")
        self.assertTrue(self.readback["review_blocker_status"]["review_blockers_recorded"])
        self.assertFalse(self.readback["review_blocker_status"]["review_blockers_resolved"])
        self.assertFalse(self.readback["review_blocker_status"]["review_executed"])

    def test_inputs_and_evidence_are_represented(self):
        self.assertIn("request for review execution", self.readback["review_blocker_inputs"])
        self.assertIn("review blocker reason", self.readback["required_evidence"])
        self.assertIn("require a later explicit boundary for blocker resolution", self.readback["recommendation_and_inference"])

    def test_false_activity_flags_remain_false(self):
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)
        for flag in (
            "review_blockers_resolved",
            "review_executed",
            "outcome_action_executed",
            "worker_dispatched",
            "provider_model_executed",
            "source_files_refreshed",
            "capsule_export_package_refreshed",
        ):
            self.assertIn(flag, self.readback["false_activity_flags"])

    def test_non_proofs_and_production_readiness_are_preserved(self):
        for caveat in (
            "escalation outcome review blocker readback is not blocker resolution",
            "escalation outcome review blocker readback is not review execution",
            "escalation outcome review blocker status is not worker dispatch",
            "escalation outcome review blocker status is not cleanup/delete/archive",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["non_proof_caveats"])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No runtime/provider/model/platform execution", self.readback["lockout_text"])
        self.assertIn("No review blocker resolution", self.readback["lockout_text"])
        self.assertIn("No review execution", self.readback["lockout_text"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No cleanup/delete/archive", self.readback["lockout_text"])
        self.assertIn("No Phase 382 implementation", self.readback["lockout_text"])

    def test_future_phase_absence_doctrine_does_not_assert_permanent_absence(self):
        self.assertIn("tests must not assert permanent absence of future phases", self.readback["future_phase_assertion_doctrine"])
        self.assertIn("tests may assert that the current phase did not implement the future phase", self.readback["future_phase_assertion_doctrine"])

    def test_marker_appears_in_source_test_docs_and_ledgers(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_packet_escalation_outcome_review_blocker_readback.py",
            "tests/test_phase_381_product_task_packet_handoff_packet_escalation_outcome_review_blocker_readback.py",
            "docs/PHASE_381.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
