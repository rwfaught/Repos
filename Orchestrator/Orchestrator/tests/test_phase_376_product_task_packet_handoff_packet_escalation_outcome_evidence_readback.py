import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_escalation_outcome_evidence_readback import (
    BOUNDARY,
    MARKER,
    NAME,
    read_product_task_packet_handoff_packet_escalation_outcome_evidence_readback,
)


MARKER_TEXT = "PHASE376_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_OUTCOME_EVIDENCE_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase376HandoffPacketEscalationOutcomeEvidenceReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_escalation_outcome_evidence_readback()

    def test_identity_is_deterministic(self):
        self.assertEqual(self.readback, read_product_task_packet_handoff_packet_escalation_outcome_evidence_readback())
        self.assertEqual(self.readback["phase"], 376)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_evidence_posture_is_readback_only(self):
        self.assertIn("readback only", self.readback["purpose"])
        self.assertEqual(self.readback["evidence_status"]["status"], "escalation_outcome_evidence_readback_only")
        self.assertFalse(self.readback["evidence_status"]["live_evidence_collected"])
        self.assertFalse(self.readback["evidence_status"]["outcome_action_executed"])
        self.assertFalse(self.readback["evidence_status"]["escalation_executed"])

    def test_inputs_and_blockers_are_represented(self):
        self.assertIn("static accepted facts", self.readback["evidence_inputs"])
        self.assertIn("request for live task execution", self.readback["blocking_conditions"])
        self.assertIn("record escalation outcome evidence posture for review only", self.readback["recommendation_and_inference"])

    def test_false_activity_flags_remain_false(self):
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)
        for flag in (
            "live_evidence_collected",
            "outcome_action_executed",
            "escalation_executed",
            "handoff_executed",
            "worker_dispatched",
            "provider_model_executed",
            "source_files_refreshed",
            "capsule_export_package_refreshed",
        ):
            self.assertIn(flag, self.readback["false_activity_flags"])

    def test_non_proofs_and_production_readiness_are_preserved(self):
        for caveat in (
            "escalation outcome evidence readback is not live evidence collection",
            "escalation outcome evidence readback is not escalation execution",
            "escalation outcome evidence status is not worker dispatch",
            "escalation outcome evidence status is not cleanup/delete/archive",
            "escalation outcome evidence status is not Source Files refresh",
            "escalation outcome evidence status is not capsule/export/package refresh",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["non_proof_caveats"])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No runtime/provider/model/platform execution", self.readback["lockout_text"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No cleanup/delete/archive", self.readback["lockout_text"])
        self.assertIn("No Phase 377 implementation", self.readback["lockout_text"])

    def test_future_phase_absence_doctrine_does_not_assert_permanent_absence(self):
        self.assertIn("tests must not assert permanent absence of future phases", self.readback["future_phase_assertion_doctrine"])
        self.assertIn("tests may assert that the current phase did not implement the future phase", self.readback["future_phase_assertion_doctrine"])

    def test_marker_appears_in_source_test_docs_and_ledgers(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_packet_escalation_outcome_evidence_readback.py",
            "tests/test_phase_376_product_task_packet_handoff_packet_escalation_outcome_evidence_readback.py",
            "docs/PHASE_376.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
