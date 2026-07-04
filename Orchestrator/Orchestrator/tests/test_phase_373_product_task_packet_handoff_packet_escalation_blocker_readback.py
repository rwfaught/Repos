import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_escalation_blocker_readback import (
    BOUNDARY,
    MARKER,
    NAME,
    read_product_task_packet_handoff_packet_escalation_blocker_readback,
)


MARKER_TEXT = "PHASE373_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_BLOCKER_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase373HandoffPacketEscalationBlockerReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_escalation_blocker_readback()

    def test_identity_is_deterministic(self):
        self.assertEqual(
            self.readback,
            read_product_task_packet_handoff_packet_escalation_blocker_readback(),
        )
        self.assertEqual(self.readback["phase"], 373)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_blocker_posture_is_readback_only(self):
        self.assertIn("readback only", self.readback["purpose"])
        self.assertEqual(self.readback["blocker_status"]["status"], "escalation_blocker_readback_only")
        self.assertFalse(self.readback["blocker_status"]["blockers_resolved"])
        self.assertFalse(self.readback["blocker_status"]["escalation_executed"])
        self.assertFalse(self.readback["blocker_status"]["worker_dispatched"])

    def test_inputs_evidence_and_blocked_actions_are_represented(self):
        self.assertIn("missing decision input evidence", self.readback["blocker_inputs"])
        self.assertIn("blocker reason", self.readback["required_evidence"])
        self.assertIn("resolve blockers", self.readback["blocked_actions"])
        self.assertIn(
            "record blocker posture for review only",
            self.readback["recommendation_and_inference"],
        )

    def test_false_activity_flags_remain_false(self):
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)
        for flag in (
            "blockers_resolved",
            "escalation_executed",
            "handoff_executed",
            "handoff_packet_executed",
            "worker_dispatched",
            "patch_applied",
            "route_selection_executed",
            "provider_model_executed",
            "runtime_provider_model_platform_executed",
            "next_boundary_executed",
            "source_files_refreshed",
            "capsule_export_package_refreshed",
        ):
            self.assertIn(flag, self.readback["false_activity_flags"])

    def test_non_proofs_and_production_readiness_are_preserved(self):
        for caveat in (
            "escalation blocker readback is not blocker resolution",
            "escalation blocker readback is not escalation execution",
            "escalation blocker status is not worker dispatch",
            "escalation blocker status is not cleanup/delete/archive",
            "escalation blocker status is not Source Files refresh",
            "escalation blocker status is not capsule/export/package refresh",
            "escalation blocker status is not provider/model execution",
            "escalation blocker status is not next-boundary execution",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["non_proof_caveats"])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No runtime/provider/model/platform execution", self.readback["lockout_text"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No cleanup/delete/archive", self.readback["lockout_text"])
        self.assertIn("No Phase 374 implementation", self.readback["lockout_text"])

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
            "orchestrator/product_task_packet_handoff_packet_escalation_blocker_readback.py",
            "tests/test_phase_373_product_task_packet_handoff_packet_escalation_blocker_readback.py",
            "docs/PHASE_373.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
