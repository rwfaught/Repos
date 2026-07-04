import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_escalation_readback import (
    BOUNDARY,
    MARKER,
    NAME,
    read_product_task_packet_handoff_packet_escalation_readback,
)


MARKER_TEXT = "PHASE370_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase370HandoffPacketEscalationReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_escalation_readback()

    def test_identity_is_deterministic(self):
        self.assertEqual(self.readback, read_product_task_packet_handoff_packet_escalation_readback())
        self.assertEqual(self.readback["phase"], 370)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_escalation_posture_is_readback_only(self):
        self.assertIn("readback only", self.readback["purpose"])
        self.assertFalse(self.readback["escalation_status"]["escalation_executed"])
        self.assertFalse(self.readback["escalation_status"]["worker_dispatched"])
        self.assertFalse(self.readback["escalation_status"]["cleanup_delete_archive_performed"])

    def test_escalation_triggers_recommendations_and_evidence_are_represented(self):
        self.assertIn("failed precheck", self.readback["escalation_triggers"])
        self.assertIn("report blocker with evidence", self.readback["escalation_recommendations"])
        self.assertIn("trigger evidence", self.readback["required_evidence"])
        self.assertIn("request to execute escalation", self.readback["blocked_escalation_conditions"])

    def test_false_activity_flags_remain_false(self):
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)
        for flag in (
            "escalation_executed",
            "handoff_executed",
            "handoff_packet_executed",
            "worker_dispatched",
            "patch_applied",
            "route_selection_executed",
            "provider_model_executed",
            "runtime_provider_model_platform_executed",
            "next_boundary_executed",
            "cleanup_delete_archive_performed",
            "source_files_refreshed",
            "capsule_export_package_refreshed",
        ):
            self.assertIn(flag, self.readback["false_activity_flags"])

    def test_non_proofs_and_production_readiness_are_preserved(self):
        for caveat in (
            "escalation readback is not escalation execution",
            "escalation readback is not handoff execution",
            "escalation readback is not handoff packet execution",
            "escalation readback is not worker dispatch",
            "escalation readback is not patch application",
            "escalation readback is not route selection execution",
            "escalation readback is not provider/model execution",
            "escalation readback is not next-boundary execution",
            "escalation readback is not cleanup/delete/archive",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["non_proof_caveats"])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No cleanup/delete/archive", self.readback["lockout_text"])
        self.assertIn("No Phase 371 implementation", self.readback["lockout_text"])

    def test_future_phase_absence_doctrine_does_not_assert_permanent_absence(self):
        self.assertIn("tests must not assert permanent absence of future phases", self.readback["future_phase_assertion_doctrine"])
        self.assertIn("tests may assert that the current phase did not implement the future phase", self.readback["future_phase_assertion_doctrine"])

    def test_marker_appears_in_source_test_docs_and_ledgers(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_packet_escalation_readback.py",
            "tests/test_phase_370_product_task_packet_handoff_packet_escalation_readback.py",
            "docs/PHASE_370.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
