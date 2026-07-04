import unittest
from pathlib import Path

from orchestrator.product_task_packet_handoff_contract_readback import (
    BOUNDARY,
    MARKER,
    read_product_task_packet_handoff_contract_readback,
)


MARKER_TEXT = "PHASE361_PRODUCT_TASK_PACKET_HANDOFF_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"


class Phase361HandoffContractReadbackTests(unittest.TestCase):
    def setUp(self):
        self.readback = read_product_task_packet_handoff_contract_readback()

    def test_deterministic_identity(self):
        self.assertEqual(self.readback, read_product_task_packet_handoff_contract_readback())
        self.assertEqual(self.readback["phase"], 361)
        self.assertEqual(self.readback["boundary"], BOUNDARY)
        self.assertEqual(self.readback["marker"], MARKER)

    def test_source_basis_and_completed_spine_include_phase_360(self):
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
        ):
            self.assertIn(phase, self.readback["source_basis"])
        self.assertIn(
            "domain_general_intake_contract_readback_phase_360",
            self.readback["completed_packet_spine"],
        )

    def test_handoff_contract_sections_exist(self):
        for key in (
            "handoff_contract_purpose",
            "handoff_prerequisites",
            "handoff_payload_doctrine",
            "handoff_recipient_doctrine",
            "handoff_authority_limits",
            "handoff_stop_gates",
        ):
            self.assertTrue(self.readback[key])

    def test_handoff_doctrine_preserves_non_execution(self):
        self.assertIn(
            "handoff contract readback is not handoff execution",
            self.readback["handoff_authority_limits"],
        )
        self.assertIn(
            "handoff eligibility is not worker dispatch",
            self.readback["handoff_authority_limits"],
        )
        self.assertIn(
            "handoff payload is not task execution",
            self.readback["handoff_payload_doctrine"],
        )
        self.assertIn(
            "handoff recipient description is not provider/model execution",
            self.readback["handoff_recipient_doctrine"],
        )

    def test_stop_gates_include_required_conditions(self):
        for stop in (
            "missing boundary",
            "dirty working tree",
            "remote-before mismatch",
            "proof overclaim",
            "source/capsule/Git truth conflation",
            "context saturation/handoff needed",
            "request for live/runtime/provider/model/platform/domain execution",
        ):
            self.assertIn(stop, self.readback["handoff_stop_gates"])

    def test_invalid_claims_reject_handoff_overclaims(self):
        for claim in (
            "handoff contract readback means handoff execution occurred",
            "handoff eligibility means worker dispatch occurred",
            "handoff payload means task execution occurred",
            "handoff recipient description means provider/model execution occurred",
            "worker PASS means coordinator ratification",
            "test PASS means semantic correctness",
            "pushed commit means production readiness",
            "Git repo truth means Source Files handoff snapshot truth",
            "Source Files handoff snapshot means official capsule proof",
            "Phase 361 supersedes Phase 335 capsule proof",
        ):
            self.assertIn(claim, self.readback["invalid_handoff_claims"])

    def test_all_false_activity_flags_are_false(self):
        for value in self.readback["false_activity_flags"].values():
            self.assertFalse(value)

    def test_caveats_truth_separation_lockouts_and_next_boundary(self):
        for caveat in (
            "readback is not execution",
            "handoff contract readback is not handoff execution",
            "handoff eligibility is not worker dispatch",
            "worker PASS is evidence, not coordinator ratification",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
        ):
            self.assertIn(caveat, self.readback["required_report_caveats"])
        self.assertIn(
            "Phase 335",
            self.readback["source_capsule_git_truth_separation"][
                "official clean product capsule proofs"
            ],
        )
        self.assertTrue(self.readback["recommended_next_boundary"])
        self.assertIn("No Source Files refresh", self.readback["lockout_text"])
        self.assertIn("No official capsule proof beyond Phase 335", self.readback["lockout_text"])

    def test_marker_appears_in_source_test_docs_and_ledgers(self):
        root = Path(__file__).resolve().parents[1]
        for rel in (
            "orchestrator/product_task_packet_handoff_contract_readback.py",
            "tests/test_phase_361_product_task_packet_handoff_contract_readback.py",
            "docs/PHASE_361.md",
            "docs/PHASE_INDEX.md",
            "docs/ACTION_LOG.md",
            "docs/SOURCE_MANIFEST.md",
            "docs/TRACKS_AND_OPEN_THREADS.md",
        ):
            self.assertIn(MARKER_TEXT, (root / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
