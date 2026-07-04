import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_review_readback import (
    BOUNDARY,
    MARKER,
    RECOMMENDED_NEXT_BOUNDARY,
    read_product_task_packet_handoff_packet_review_readback,
)


MARKER_TEXT = "PHASE362_PRODUCT_TASK_PACKET_HANDOFF_PACKET_REVIEW_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase362HandoffPacketReviewReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_review_readback()

    def test_deterministic_identity(self):
        self.assertEqual(self.readback, read_product_task_packet_handoff_packet_review_readback())
        self.assertEqual(self.readback["phase"], 362)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_source_basis_and_spine_include_phase_361(self):
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
        ):
            self.assertIn(phase, self.readback["source_basis"])
        self.assertIn("handoff_contract_readback_phase_361", self.readback["completed_packet_spine"])

    def test_review_contract_purpose_exists_and_is_not_execution(self):
        self.assertIn("review_contract_purpose", self.readback)
        self.assertIn("readback is not handoff execution", self.readback["review_contract_purpose"])

    def test_required_packet_fields_and_status_vocabulary(self):
        for field in (
            "boundary",
            "role_context",
            "repo_path",
            "expected_head",
            "expected_origin_main",
            "accepted_facts",
            "inference",
            "source_basis",
            "changed_files_or_mutation_status",
            "validation_status",
            "non_proofs",
            "lockouts",
            "next_boundary",
            "caveats_or_open_threads",
        ):
            self.assertIn(field, self.readback["required_handoff_packet_fields"])
        for status in (
            "review_not_started",
            "review_blocked",
            "review_deferred",
            "review_accepted_for_next_boundary",
            "review_rejected",
        ):
            self.assertIn(status, self.readback["review_status_vocabulary"])

    def test_acceptance_gates_are_structural_and_non_proof(self):
        for gate in (
            "required packet fields present",
            "review acceptance is structural eligibility only",
            "future explicitly bounded next move stated",
            "no semantic correctness claim",
            "no production readiness claim",
            "no Source Files refresh claim",
            "no official capsule proof claim beyond Phase 335",
        ):
            self.assertIn(gate, self.readback["review_acceptance_gates"])

    def test_rejection_gates_include_required_overclaims(self):
        for gate in (
            "proof overclaim",
            "source/capsule/Git truth conflation",
            "worker PASS treated as coordinator ratification",
            "test PASS treated as semantic correctness",
            "pushed commit treated as production readiness",
            "Source Files snapshot treated as official capsule proof",
            "request for live/runtime/provider/model/platform/domain execution",
            "request for worker dispatch",
            "request for patch application",
        ):
            self.assertIn(gate, self.readback["review_rejection_gates"])

    def test_deferral_gates_include_required_conditions(self):
        for gate in (
            "context saturation requiring handoff",
            "remote-before mismatch",
            "unclear expected HEAD/origin",
            "incomplete validation evidence",
            "unresolved prior failed checker or brittle review harness",
            "missing caveats",
            "ambiguous next boundary",
        ):
            self.assertIn(gate, self.readback["review_deferral_gates"])

    def test_all_false_activity_flags_are_false(self):
        for flag in (
            "handoff_executed",
            "handoff_packet_review_executed_as_live_action",
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

    def test_lockouts_non_proofs_and_next_boundary(self):
        for caveat in (
            "handoff packet review readback is not handoff execution",
            "review eligibility is not worker dispatch",
            "handoff packet is not a Source Files refresh",
            "handoff packet is not an official capsule",
            "worker PASS is evidence, not coordinator ratification",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["required_report_caveats"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No official capsule proof claim", self.readback["lockout_text"])
        self.assertEqual(self.readback["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)

    def test_marker_appears_in_source_test_docs_and_phase_363_is_not_implemented(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_packet_review_readback.py",
            "tests/test_phase_362_product_task_packet_handoff_packet_review_readback.py",
            "docs/PHASE_362.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))
        self.assertFalse((root / "docs/PHASE_363.md").exists())
        self.assertFalse((root / "orchestrator/product_task_packet_handoff_packet_operator_decision_readback.py").exists())


if __name__ == "__main__":
    unittest.main()
