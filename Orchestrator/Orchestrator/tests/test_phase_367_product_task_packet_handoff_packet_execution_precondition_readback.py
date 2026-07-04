import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_execution_precondition_readback import (
    BOUNDARY,
    MARKER,
    NAME,
    read_product_task_packet_handoff_packet_execution_precondition_readback,
)


MARKER_TEXT = "PHASE367_PRODUCT_TASK_PACKET_HANDOFF_PACKET_EXECUTION_PRECONDITION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase367HandoffPacketExecutionPreconditionReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_execution_precondition_readback()

    def test_identity_is_deterministic(self):
        self.assertEqual(self.readback, read_product_task_packet_handoff_packet_execution_precondition_readback())
        self.assertEqual(self.readback["phase"], 367)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_precondition_posture_is_readback_only(self):
        self.assertIn("readback only", self.readback["purpose"])
        self.assertFalse(self.readback["precondition_status"]["execution_precondition_readback_is_execution"])
        self.assertFalse(self.readback["precondition_status"]["packet_executable_now"])

    def test_facts_preconditions_and_inference_are_separated(self):
        self.assertNotEqual(self.readback["accepted_facts"], self.readback["required_preconditions"])
        self.assertNotEqual(
            self.readback["accepted_facts"],
            self.readback["precondition_inference_and_recommendation"],
        )
        self.assertIn("execution authority is not execution", self.readback["non_proof_caveats"])

    def test_required_and_missing_preconditions_are_represented(self):
        self.assertIn("explicit later execution boundary", self.readback["required_preconditions"])
        self.assertIn("no later execution boundary exists in Phase 367", self.readback["missing_preconditions"])
        self.assertIn("missing explicit later execution boundary", self.readback["blocking_conditions"])

    def test_false_activity_flags_remain_false(self):
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)
        for flag in (
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
            "execution precondition readback is not execution",
            "execution precondition readback is not handoff execution",
            "execution precondition readback is not handoff packet execution",
            "execution precondition readback is not worker dispatch",
            "execution precondition readback is not patch application",
            "execution precondition readback is not route selection execution",
            "execution precondition readback is not provider/model execution",
            "execution precondition readback is not next-boundary execution",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["non_proof_caveats"])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No Phase 368 implementation", self.readback["lockout_text"])

    def test_future_phase_absence_doctrine_does_not_assert_permanent_absence(self):
        self.assertIn("tests must not assert permanent absence of future phases", self.readback["future_phase_assertion_doctrine"])
        self.assertIn("tests may assert that the current phase did not implement the future phase", self.readback["future_phase_assertion_doctrine"])

    def test_marker_appears_in_source_test_docs_and_ledgers(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_packet_execution_precondition_readback.py",
            "tests/test_phase_367_product_task_packet_handoff_packet_execution_precondition_readback.py",
            "docs/PHASE_367.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
