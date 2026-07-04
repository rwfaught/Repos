import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_packet_operator_decision_readback import (
    BOUNDARY,
    MARKER,
    RECOMMENDED_NEXT_BOUNDARY,
    read_product_task_packet_handoff_packet_operator_decision_readback,
)


MARKER_TEXT = "PHASE363_PRODUCT_TASK_PACKET_HANDOFF_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase363HandoffPacketOperatorDecisionReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_packet_operator_decision_readback()

    def test_deterministic_identity(self):
        self.assertEqual(
            self.readback,
            read_product_task_packet_handoff_packet_operator_decision_readback(),
        )
        self.assertEqual(self.readback["phase"], 363)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_source_basis_and_spine_include_phase_362(self):
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
        ):
            self.assertIn(phase, self.readback["source_basis"])
        self.assertIn(
            "handoff_packet_review_readback_phase_362",
            self.readback["completed_packet_spine"],
        )

    def test_decision_contract_purpose_exists_and_is_not_execution(self):
        self.assertIn("decision_contract_purpose", self.readback)
        self.assertIn(
            "operator decision readback is not handoff execution",
            self.readback["decision_contract_purpose"],
        )

    def test_allowed_decision_states_are_conservative(self):
        for status in (
            "decision_not_started",
            "decision_blocked",
            "decision_deferred",
            "decision_rejected",
            "decision_accepted_for_next_boundary",
        ):
            self.assertIn(status, self.readback["allowed_decision_states"])

    def test_decision_evidence_requirements_exist(self):
        for requirement in (
            "exact boundary present",
            "reviewed packet status present",
            "accepted facts separated from inference",
            "source basis identified",
            "expected HEAD/origin stated",
            "remote-before state stated when push may be relevant",
            "validation evidence stated",
            "changed files or mutation status stated",
            "non-proofs preserved",
            "lockouts preserved",
            "caveats/open threads stated",
            "next boundary stated",
        ):
            self.assertIn(requirement, self.readback["decision_evidence_requirements"])

    def test_proceed_gates_are_structural_and_non_proof(self):
        for gate in (
            "required packet fields present",
            "reviewed packet is structurally eligible",
            "expected Git refs are clear",
            "no dirty working tree claim unless explicitly reported",
            "no source/capsule/Git conflation",
            "no proof overclaim",
            "next boundary is explicit and bounded",
            "lockouts are preserved",
            "structural eligibility only",
            "no semantic correctness claim",
            "no production readiness claim",
        ):
            self.assertIn(gate, self.readback["proceed_decision_gates"])

    def test_defer_gates_include_required_conditions(self):
        for gate in (
            "context saturation requiring handoff",
            "remote-before mismatch",
            "unclear expected HEAD/origin",
            "incomplete validation evidence",
            "unresolved failed checker or brittle review harness",
            "missing caveats",
            "ambiguous next boundary",
            "missing source basis",
            "operator uncertainty about current state",
        ):
            self.assertIn(gate, self.readback["defer_decision_gates"])

    def test_reject_gates_include_required_overclaims_and_requests(self):
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
            "request for provider/model execution",
            "request for Source Files refresh as proof",
            "request for capsule/export/package refresh as proof",
        ):
            self.assertIn(gate, self.readback["reject_decision_gates"])

    def test_stop_gates_include_required_conditions(self):
        for gate in (
            "dirty working tree not inside explicit mutation boundary",
            "remote main changed before push",
            "unexpected changed files",
            "validation failure",
            "missing marker",
            "lockout violation",
            "source/capsule/Git truth conflation",
            "request to start Phase 364 before Phase 363 is settled",
        ):
            self.assertIn(gate, self.readback["stop_decision_gates"])

    def test_all_false_activity_flags_are_false(self):
        for flag in (
            "operator_decision_executed_as_live_action",
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

    def test_lockouts_non_proofs_and_next_boundary(self):
        for caveat in (
            "operator decision readback is not handoff execution",
            "decision accepted for next boundary is not worker dispatch",
            "decision accepted for next boundary is not patch application",
            "decision accepted for next boundary is not provider/model execution",
            "decision accepted for next boundary is not route selection execution",
            "review acceptance from Phase 362 is not implementation correctness",
            "worker PASS is evidence, not coordinator ratification",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
            "Git repo truth is distinct from Source Files handoff snapshots",
            "a handoff packet is not an official capsule",
            "Phase 335 remains accepted capsule proof unless explicitly superseded",
        ):
            self.assertIn(caveat, self.readback["required_report_caveats"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No official capsule proof claim", self.readback["lockout_text"])
        self.assertEqual(self.readback["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)

    def test_marker_appears_in_source_test_docs_and_phase_363_remains_non_executing(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_packet_operator_decision_readback.py",
            "tests/test_phase_363_product_task_packet_handoff_packet_operator_decision_readback.py",
            "docs/PHASE_363.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))
        self.assertEqual(
            self.readback["recommended_next_boundary"],
            "PHASE364_PRODUCT_TASK_PACKET_HANDOFF_PACKET_NEXT_BOUNDARY_SELECTION_READBACK_SOURCE_TEST_DOCS",
        )
        self.assertIn("No Phase 364 implementation", self.readback["lockout_text"])
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
