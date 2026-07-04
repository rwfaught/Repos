import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_ready_state_readback import (
    BOUNDARY,
    MARKER,
    NAME,
    read_product_task_packet_handoff_packet_ready_state_readback,
)


MARKER_TEXT = "PHASE365_PRODUCT_TASK_PACKET_HANDOFF_PACKET_READY_STATE_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase365HandoffPacketReadyStateReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_ready_state_readback()

    def test_deterministic_identity(self):
        self.assertEqual(
            self.readback,
            read_product_task_packet_handoff_packet_ready_state_readback(),
        )
        self.assertEqual(self.readback["phase"], 365)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_ready_state_posture_is_non_executing(self):
        self.assertIn("deterministic and non-executing", self.readback["ready_state_purpose"])
        self.assertFalse(self.readback["ready_state_recommendation"]["execution_authority"])
        self.assertIn(
            "readiness is a recommendation/status field, not execution authority",
            self.readback["readiness_recommendation_and_inference"],
        )

    def test_accepted_facts_are_separated_from_inference(self):
        self.assertTrue(self.readback["accepted_facts"])
        self.assertTrue(self.readback["readiness_recommendation_and_inference"])
        self.assertNotEqual(
            self.readback["accepted_facts"],
            self.readback["readiness_recommendation_and_inference"],
        )

    def test_readiness_gates_and_blocking_conditions_are_represented(self):
        for gate in (
            "exact current boundary present",
            "source basis through Phase 364 identified",
            "accepted facts separated from inference/recommendation",
            "selected next boundary is explicit and bounded",
            "production readiness remains false",
        ):
            self.assertIn(gate, self.readback["readiness_gates"])
        for condition in (
            "missing boundary",
            "incomplete validation evidence",
            "dirty working tree outside explicit mutation boundary",
            "lockout violation",
            "request to treat ready-state as execution authority",
        ):
            self.assertIn(condition, self.readback["blocking_conditions"])

    def test_ready_state_recommendation_does_not_equal_execution_authority(self):
        recommendation = self.readback["ready_state_recommendation"]
        self.assertEqual(recommendation["status"], "ready_for_next_bounded_move_readback_only")
        self.assertFalse(recommendation["execution_authority"])
        self.assertIn(
            "ready-state readback is not execution authority",
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
            "semantic_correctness_proven",
            "production_readiness_proven",
            "official_capsule_proof_superseded_phase_335",
        ):
            self.assertIn(flag, self.readback["false_activity_flags"])
            self.assertFalse(self.readback["false_activity_flags"][flag])

    def test_non_proofs_and_production_readiness_are_preserved(self):
        for caveat in (
            "ready-state readback is not execution authority",
            "ready for next bounded move is not handoff execution",
            "ready for next bounded move is not worker dispatch",
            "ready for next bounded move is not patch application",
            "ready for next bounded move is not route selection execution",
            "ready for next bounded move is not provider/model execution",
            "ready for next bounded move is not next-boundary execution",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["non_proof_caveats"])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No Phase 366 implementation", self.readback["lockout_text"])

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
            "orchestrator/product_task_packet_handoff_packet_ready_state_readback.py",
            "tests/test_phase_365_product_task_packet_handoff_packet_ready_state_readback.py",
            "docs/PHASE_365.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
