import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_escalation_outcome_review_posture_evidence_readback import (
    BOUNDARY,
    MARKER,
    NAME,
    RECOMMENDED_NEXT_BOUNDARY,
    read_product_task_packet_handoff_packet_escalation_outcome_review_posture_evidence_readback,
)


MARKER_TEXT = "PHASE384_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_OUTCOME_REVIEW_POSTURE_EVIDENCE_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
PRODUCT_NEXT_BOUNDARY = "PHASE385_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_OUTCOME_REVIEW_POSTURE_BLOCKER_READBACK_SOURCE_TEST_DOCS"


class Phase384HandoffPacketEscalationOutcomeReviewPostureEvidenceReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_escalation_outcome_review_posture_evidence_readback()

    def test_identity_is_deterministic(self):
        self.assertEqual(self.readback, read_product_task_packet_handoff_packet_escalation_outcome_review_posture_evidence_readback())
        self.assertEqual(self.readback["phase"], 384)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_product_next_boundary_is_posture_blocker(self):
        self.assertEqual(RECOMMENDED_NEXT_BOUNDARY, PRODUCT_NEXT_BOUNDARY)
        self.assertEqual(self.readback["recommended_next_boundary"], PRODUCT_NEXT_BOUNDARY)
        self.assertEqual(self.readback["review_posture_evidence_status"]["recommended_next_boundary"], PRODUCT_NEXT_BOUNDARY)
        self.assertFalse(self.readback["review_posture_evidence_status"]["campaign_cap_is_product_next_boundary"])

    def test_posture_evidence_is_readback_only(self):
        self.assertIn("readback only", self.readback["purpose"])
        self.assertEqual(self.readback["review_posture_evidence_status"]["status"], "escalation_outcome_review_posture_evidence_readback_only")
        self.assertTrue(self.readback["review_posture_evidence_status"]["posture_evidence_recorded"])
        self.assertFalse(self.readback["review_posture_evidence_status"]["live_evidence_collected"])
        self.assertFalse(self.readback["review_posture_evidence_status"]["review_executed"])

    def test_inputs_and_blocking_conditions_are_represented(self):
        self.assertIn("Phase 383 accepted facts", self.readback["review_posture_evidence_inputs"])
        self.assertIn("marker registration across source/test/docs/ledgers", self.readback["review_posture_evidence_inputs"])
        self.assertIn("actual posture evidence collection requires a later explicit execution boundary", self.readback["blocking_conditions"])
        self.assertIn("treat posture evidence as static source/test/docs data", self.readback["recommendation_and_inference"])

    def test_false_activity_flags_remain_false(self):
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)
        for flag in (
            "live_evidence_collected",
            "review_executed",
            "review_blockers_resolved",
            "worker_dispatched",
            "provider_model_executed",
            "source_files_refreshed",
            "capsule_export_package_refreshed",
        ):
            self.assertIn(flag, self.readback["false_activity_flags"])

    def test_non_proofs_and_production_readiness_are_preserved(self):
        for caveat in (
            "escalation outcome review posture evidence readback is not live evidence collection",
            "escalation outcome review posture evidence readback is not review execution",
            "escalation outcome review posture evidence status is not worker dispatch",
            "escalation outcome review posture evidence status is not cleanup/delete/archive",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["non_proof_caveats"])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No live evidence collection", self.readback["lockout_text"])
        self.assertIn("No runtime/provider/model/platform execution", self.readback["lockout_text"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No Phase 385 implementation", self.readback["lockout_text"])

    def test_future_phase_absence_doctrine_does_not_assert_permanent_absence(self):
        self.assertIn("tests must not assert permanent absence of future phases", self.readback["future_phase_assertion_doctrine"])
        self.assertIn("future Phase 385 files may exist after a later legitimate boundary implements them", self.readback["future_phase_assertion_doctrine"])

    def test_marker_appears_in_source_test_docs_and_ledgers(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_packet_escalation_outcome_review_posture_evidence_readback.py",
            "tests/test_phase_384_product_task_packet_handoff_packet_escalation_outcome_review_posture_evidence_readback.py",
            "docs/PHASE_384.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
