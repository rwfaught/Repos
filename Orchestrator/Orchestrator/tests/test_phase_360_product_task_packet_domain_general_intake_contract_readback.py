import unittest
from pathlib import Path

from orchestrator.product_task_packet_domain_general_intake_contract_readback import (
    BOUNDARY,
    MARKER,
    read_product_task_packet_domain_general_intake_contract_readback,
)


MARKER_TEXT = "PHASE360_PRODUCT_TASK_PACKET_DOMAIN_GENERAL_INTAKE_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
NEXT_BOUNDARY = "PHASE361_PRODUCT_TASK_PACKET_HANDOFF_CONTRACT_READBACK_SOURCE_TEST_DOCS"


class Phase360DomainGeneralIntakeContractReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_domain_general_intake_contract_readback()

    def test_deterministic_identity(self):
        self.assertEqual(self.readback, read_product_task_packet_domain_general_intake_contract_readback())
        self.assertEqual(self.readback["phase"], 360)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_source_basis_and_spine(self):
        for phase in ("phase_349", "phase_351", "phase_352", "phase_354", "phase_355", "phase_356", "phase_357", "phase_358", "phase_359"):
            self.assertIn(phase, self.readback["source_basis"])
        self.assertIn("provider_policy_contract_readback_phase_359", self.readback["completed_packet_spine"])

    def test_phase_specific_contracts_exist(self):
        self.assertTrue(self.readback["intake_input_doctrine"])
        self.assertTrue(self.readback["intake_output_doctrine"])
        self.assertTrue(self.readback["intake_stop_gates"])
        self.assertIn("no live business-data access", self.readback["intake_input_doctrine"])
        self.assertIn("no real domain execution", self.readback["intake_output_doctrine"])

    def test_invalid_claims_and_stop_conditions(self):
        self.assertIn("intake contract means domain-general intake implementation exists", self.readback["invalid_claims"])
        for stop in (
            "live business-data access request",
            "live Obsidian/PKMS access request",
            "runtime/provider/model/platform request",
            "proof overclaim",
            "dirty working tree",
            "remote-before mismatch",
            "source/capsule/Git truth conflation",
            "context saturation/handoff needed",
        ):
            self.assertIn(stop, self.readback["stop_conditions"])

    def test_false_flags_caveats_truth_and_next_boundary(self):
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)
        for caveat in (
            "readback is not execution",
            "eligibility is not implementation",
            "contract is not runtime enforcement",
            "worker PASS is evidence, not coordinator ratification",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["required_report_caveats"])
        self.assertIn("Phase 335", self.readback["source_capsule_git_truth_separation"]["official clean product capsule proofs"])
        self.assertEqual(self.readback["recommended_next_boundary"], NEXT_BOUNDARY)

    def test_marker_appears_in_source_test_docs(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_domain_general_intake_contract_readback.py",
            "tests/test_phase_360_product_task_packet_domain_general_intake_contract_readback.py",
            "docs/PHASE_360.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
