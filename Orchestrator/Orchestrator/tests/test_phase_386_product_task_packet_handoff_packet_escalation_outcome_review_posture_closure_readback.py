import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_escalation_outcome_review_posture_closure_readback import (
    BOUNDARY,
    CAMPAIGN_CAP_STATUS,
    MARKER,
    NAME,
    RECOMMENDED_NEXT_BOUNDARY,
    read_product_task_packet_handoff_packet_escalation_outcome_review_posture_closure_readback,
)


MARKER_TEXT = "PHASE386_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_OUTCOME_REVIEW_POSTURE_CLOSURE_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
PRODUCT_NEXT_BOUNDARY = "PHASE387_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_OUTCOME_REVIEW_POSTURE_REVIEW_READBACK_SOURCE_TEST_DOCS"


class Phase386HandoffPacketEscalationOutcomeReviewPostureClosureReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_escalation_outcome_review_posture_closure_readback()

    def test_identity_is_deterministic(self):
        self.assertEqual(self.readback, read_product_task_packet_handoff_packet_escalation_outcome_review_posture_closure_readback())
        self.assertEqual(self.readback["phase"], 386)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_product_next_boundary_is_separate_from_campaign_cap(self):
        self.assertEqual(RECOMMENDED_NEXT_BOUNDARY, PRODUCT_NEXT_BOUNDARY)
        self.assertEqual(self.readback["recommended_next_boundary"], PRODUCT_NEXT_BOUNDARY)
        self.assertEqual(self.readback["review_posture_closure_status"]["recommended_next_boundary"], PRODUCT_NEXT_BOUNDARY)
        self.assertEqual(CAMPAIGN_CAP_STATUS, "CAMPAIGN_CAP_REACHED_NO_PHASE_387_AUTHORIZED")
        self.assertEqual(self.readback["campaign_cap_status"], CAMPAIGN_CAP_STATUS)
        self.assertEqual(self.readback["review_posture_closure_status"]["campaign_cap_status"], CAMPAIGN_CAP_STATUS)

    def test_posture_closure_is_readback_only(self):
        self.assertIn("readback only", self.readback["purpose"])
        self.assertEqual(self.readback["review_posture_closure_status"]["status"], "escalation_outcome_review_posture_closure_readback_only")
        self.assertTrue(self.readback["review_posture_closure_status"]["posture_closure_recorded"])
        self.assertFalse(self.readback["review_posture_closure_status"]["operational_closure_performed"])
        self.assertFalse(self.readback["review_posture_closure_status"]["review_executed"])
        self.assertTrue(self.readback["review_posture_closure_status"]["campaign_cap_reached"])

    def test_inputs_and_unresolved_conditions_are_represented(self):
        self.assertIn("Phase 385 review posture blocker status", self.readback["review_posture_closure_inputs"])
        self.assertIn("review blockers remain unresolved", self.readback["unresolved_conditions"])
        self.assertIn("stop the rolling campaign at Phase 386 per packet cap", self.readback["recommendation_and_inference"])

    def test_false_activity_flags_remain_false(self):
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)
        for flag in (
            "operational_closure_performed",
            "review_executed",
            "review_blockers_resolved",
            "live_evidence_collected",
            "worker_dispatched",
            "provider_model_executed",
            "source_files_refreshed",
            "capsule_export_package_refreshed",
        ):
            self.assertIn(flag, self.readback["false_activity_flags"])

    def test_non_proofs_and_production_readiness_are_preserved(self):
        for caveat in (
            "escalation outcome review posture closure readback is not operational closure",
            "escalation outcome review posture closure readback is not review execution",
            "escalation outcome review posture closure status is not blocker resolution",
            "escalation outcome review posture closure status is not worker dispatch",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["non_proof_caveats"])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No runtime/provider/model/platform execution", self.readback["lockout_text"])
        self.assertIn("No operational posture closure", self.readback["lockout_text"])
        self.assertIn("No review execution", self.readback["lockout_text"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No cleanup/delete/archive", self.readback["lockout_text"])
        self.assertIn("No Phase 387 implementation", self.readback["lockout_text"])

    def test_future_phase_absence_doctrine_does_not_assert_permanent_absence(self):
        self.assertIn("tests must not assert permanent absence of future phases", self.readback["future_phase_assertion_doctrine"])
        self.assertIn("campaign cap prevents Phase 386 from authorizing Phase 387 implementation", self.readback["future_phase_assertion_doctrine"])
        self.assertIn("Phase 387 implementation requires a later explicit coordinator boundary", self.readback["future_phase_assertion_doctrine"])

    def test_marker_appears_in_source_test_docs_and_ledgers(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_packet_escalation_outcome_review_posture_closure_readback.py",
            "tests/test_phase_386_product_task_packet_handoff_packet_escalation_outcome_review_posture_closure_readback.py",
            "docs/PHASE_386.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
