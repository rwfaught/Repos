import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_operator_approval_readback import (
    BOUNDARY,
    MARKER,
    NAME,
    read_product_task_packet_handoff_packet_operator_approval_readback,
)


MARKER_TEXT = "PHASE368_PRODUCT_TASK_PACKET_HANDOFF_PACKET_OPERATOR_APPROVAL_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase368HandoffPacketOperatorApprovalReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_operator_approval_readback()

    def test_identity_is_deterministic(self):
        self.assertEqual(self.readback, read_product_task_packet_handoff_packet_operator_approval_readback())
        self.assertEqual(self.readback["phase"], 368)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_operator_approval_posture_is_readback_only(self):
        self.assertIn("readback only", self.readback["purpose"])
        self.assertFalse(self.readback["approval_status"]["operator_action_performed"])
        self.assertFalse(self.readback["approval_status"]["approval_status_is_execution"])
        self.assertFalse(self.readback["approval_status"]["execution_authorized_now"])

    def test_accepted_facts_are_separated_from_approval_inference(self):
        self.assertNotEqual(self.readback["accepted_facts"], self.readback["approval_inputs"])
        self.assertNotEqual(self.readback["accepted_facts"], self.readback["approval_inference_and_recommendation"])

    def test_approval_gates_missing_approval_and_decision_requirements_are_represented(self):
        self.assertIn("operator approval requirement represented", self.readback["approval_gates"])
        self.assertIn("missing approval represented", self.readback["approval_gates"])
        self.assertIn("no operator action is performed by Phase 368", self.readback["missing_approval"])
        self.assertIn("explicit future execution boundary", self.readback["operator_decision_requirements"])

    def test_false_activity_flags_remain_false(self):
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)
        for flag in (
            "operator_action_performed",
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
            "operator approval readback is not operator action",
            "approval status is not execution",
            "operator approval readback is not handoff execution",
            "operator approval readback is not handoff packet execution",
            "operator approval readback is not worker dispatch",
            "operator approval readback is not patch application",
            "operator approval readback is not route selection execution",
            "operator approval readback is not provider/model execution",
            "operator approval readback is not next-boundary execution",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["non_proof_caveats"])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No Phase 369 implementation", self.readback["lockout_text"])

    def test_future_phase_absence_doctrine_does_not_assert_permanent_absence(self):
        self.assertIn("tests must not assert permanent absence of future phases", self.readback["future_phase_assertion_doctrine"])
        self.assertIn("tests may assert that the current phase did not implement the future phase", self.readback["future_phase_assertion_doctrine"])

    def test_marker_appears_in_source_test_docs_and_ledgers(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_packet_operator_approval_readback.py",
            "tests/test_phase_368_product_task_packet_handoff_packet_operator_approval_readback.py",
            "docs/PHASE_368.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
