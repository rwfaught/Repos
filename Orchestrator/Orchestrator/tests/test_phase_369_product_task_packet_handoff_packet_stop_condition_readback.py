import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_stop_condition_readback import (
    BOUNDARY,
    MARKER,
    NAME,
    read_product_task_packet_handoff_packet_stop_condition_readback,
)


MARKER_TEXT = "PHASE369_PRODUCT_TASK_PACKET_HANDOFF_PACKET_STOP_CONDITION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase369HandoffPacketStopConditionReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_stop_condition_readback()

    def test_identity_is_deterministic(self):
        self.assertEqual(self.readback, read_product_task_packet_handoff_packet_stop_condition_readback())
        self.assertEqual(self.readback["phase"], 369)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_stop_condition_posture_is_readback_only(self):
        self.assertIn("readback only", self.readback["purpose"])
        self.assertFalse(self.readback["stop_recommendation"]["stop_executed"])
        self.assertFalse(self.readback["stop_recommendation"]["cleanup_delete_archive_performed"])

    def test_stop_triggers_blockers_and_escalation_are_represented(self):
        self.assertIn("failed precheck", self.readback["stop_triggers"])
        self.assertIn("unexpected changed file", self.readback["stop_triggers"])
        self.assertIn("stop trigger present", self.readback["blocking_conditions"])
        self.assertIn("report the stop trigger", self.readback["required_escalation"])

    def test_false_activity_flags_remain_false(self):
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)
        for flag in (
            "stop_executed",
            "cleanup_delete_archive_performed",
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
            "stop-condition readback is not stop execution",
            "stop-condition readback is not cleanup/delete/archive",
            "stop-condition readback is not handoff execution",
            "stop-condition readback is not handoff packet execution",
            "stop-condition readback is not worker dispatch",
            "stop-condition readback is not patch application",
            "stop-condition readback is not route selection execution",
            "stop-condition readback is not provider/model execution",
            "stop-condition readback is not next-boundary execution",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["non_proof_caveats"])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No cleanup/delete/archive", self.readback["lockout_text"])
        self.assertIn("No Phase 370 implementation", self.readback["lockout_text"])

    def test_future_phase_absence_doctrine_does_not_assert_permanent_absence(self):
        self.assertIn("tests must not assert permanent absence of future phases", self.readback["future_phase_assertion_doctrine"])
        self.assertIn("tests may assert that the current phase did not implement the future phase", self.readback["future_phase_assertion_doctrine"])

    def test_marker_appears_in_source_test_docs_and_ledgers(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_packet_stop_condition_readback.py",
            "tests/test_phase_369_product_task_packet_handoff_packet_stop_condition_readback.py",
            "docs/PHASE_369.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
