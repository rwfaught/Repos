import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_next_boundary_selection_readback import (
    BOUNDARY,
    MARKER,
    NAME,
    RECOMMENDED_NEXT_BOUNDARY,
    read_product_task_packet_handoff_packet_next_boundary_selection_readback,
)


MARKER_TEXT = "PHASE364_PRODUCT_TASK_PACKET_HANDOFF_PACKET_NEXT_BOUNDARY_SELECTION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase364HandoffPacketNextBoundarySelectionReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_next_boundary_selection_readback()

    def test_deterministic_identity(self):
        self.assertEqual(
            self.readback,
            read_product_task_packet_handoff_packet_next_boundary_selection_readback(),
        )
        self.assertEqual(self.readback["phase"], 364)
        self.assertEqual(self.readback["name"], NAME)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_source_basis_and_spine_include_phase_363(self):
        for phase in (
            "phase_349",
            "phase_351",
            "phase_352",
            "phase_354",
            "phase_355",
            "phase_356",
            "phase_357",
            "phase_358",
            "phase_359",
            "phase_360",
            "phase_361",
            "phase_362",
            "phase_363",
        ):
            self.assertIn(phase, self.readback["source_basis"])
        self.assertIn(
            "handoff_packet_operator_decision_readback_phase_363",
            self.readback["completed_packet_spine"],
        )

    def test_posture_is_readback_recommendation_only(self):
        self.assertIn(
            "next-boundary selection readback is not next-boundary execution",
            self.readback["next_boundary_selection_purpose"],
        )
        self.assertIn(
            "selecting a future boundary means only that a future explicitly bounded move may be prepared",
            self.readback["selector_authority_limits"],
        )

    def test_accepted_facts_are_separated_from_inference_and_recommendation(self):
        self.assertTrue(self.readback["accepted_facts"])
        self.assertTrue(self.readback["inference_and_recommendation"])
        self.assertNotEqual(
            self.readback["accepted_facts"],
            self.readback["inference_and_recommendation"],
        )

    def test_candidates_and_selection_gates_exist(self):
        for category in (
            "review/finalization readback",
            "handoff packet issuance readback",
            "worker prompt preparation readback",
            "operator push/ref verification prep",
            "deferral/handoff-to-new-session preparation",
            "blocked/no-op selection",
        ):
            self.assertIn(category, self.readback["candidate_boundary_categories"])
        self.assertTrue(self.readback["candidate_next_boundaries"])
        self.assertIn(
            "candidate boundary is explicit and bounded",
            self.readback["valid_selection_gates"],
        )
        self.assertIn("lockouts are preserved", self.readback["valid_selection_gates"])

    def test_evidence_and_defer_gates_include_required_conditions(self):
        for requirement in (
            "exact current boundary present",
            "accepted operator decision state present",
            "reviewed handoff packet status present",
            "accepted facts separated from inference",
            "candidate next boundary stated",
        ):
            self.assertIn(requirement, self.readback["selection_evidence_requirements"])
        for gate in (
            "context saturation requiring handoff",
            "remote-before mismatch",
            "unclear expected HEAD/origin",
            "incomplete validation evidence",
            "unresolved failed checker or brittle review harness",
            "missing caveats",
            "ambiguous candidate boundary",
            "missing source basis",
            "operator uncertainty about current state",
            "dirty working tree outside explicit mutation boundary",
        ):
            self.assertIn(gate, self.readback["defer_selection_gates"])

    def test_reject_and_block_gates_preserve_non_proofs(self):
        for gate in (
            "proof overclaim",
            "source/capsule/Git truth conflation",
            "worker PASS treated as coordinator ratification",
            "test PASS treated as semantic correctness",
            "pushed commit treated as production readiness",
            "Source Files snapshot treated as official capsule proof",
            "request for live/runtime/provider/model/platform/domain execution",
            "request to treat selected boundary as already executed",
        ):
            self.assertIn(gate, self.readback["reject_selection_gates"])
        for gate in (
            "dirty working tree not inside explicit mutation boundary",
            "remote main changed before push",
            "unexpected changed files",
            "validation failure",
            "missing marker",
            "lockout violation",
            "source/capsule/Git truth conflation",
            "request to start Phase 365 before Phase 364 is settled",
        ):
            self.assertIn(gate, self.readback["block_selection_gates"])

    def test_false_flags_non_proofs_and_production_readiness(self):
        for flag in (
            "next_boundary_selected_as_live_execution",
            "next_boundary_executed",
            "handoff_executed",
            "handoff_packet_executed",
            "worker_dispatched",
            "patch_applied",
            "route_selection_executed",
            "provider_model_executed",
            "runtime_provider_model_platform_executed",
            "domain_general_intake_implemented",
            "source_files_refreshed",
            "capsule_export_package_refreshed",
            "semantic_correctness_proven",
            "production_readiness_proven",
            "official_capsule_proof_superseded_phase_335",
        ):
            self.assertIn(flag, self.readback["false_activity_flags"])
            self.assertFalse(self.readback["false_activity_flags"][flag])
        self.assertFalse(self.readback["production_readiness"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No capsule/export/package refresh", self.readback["lockout_text"])
        self.assertIn("No Phase 365 implementation", self.readback["lockout_text"])

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
            "orchestrator/product_task_packet_handoff_packet_next_boundary_selection_readback.py",
            "tests/test_phase_364_product_task_packet_handoff_packet_next_boundary_selection_readback.py",
            "docs/PHASE_364.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))
        self.assertEqual(self.readback["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)


if __name__ == "__main__":
    unittest.main()
