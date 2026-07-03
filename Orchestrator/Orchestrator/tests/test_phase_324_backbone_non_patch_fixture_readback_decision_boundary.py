import unittest

from orchestrator.backbone_research_claim_fixture_decision_boundary import (
    RESEARCH_CLAIM_FIXTURE_BLOCKED_DECISIONS,
    RESEARCH_CLAIM_FIXTURE_RECOMMENDED_NEXT_BOUNDARY_AFTER_STOP,
    assess_research_claim_fixture_decision_boundary,
    read_research_claim_fixture_decision_boundary_status,
)
from orchestrator.backbone_research_claim_fixture_mapping import (
    RESEARCH_CLAIM_FIXTURE_NON_PROOFS,
    ResearchClaimFixtureBackboneStageMapping,
    ordered_research_claim_fixture_backbone_stage_mappings,
    read_research_claim_fixture_backbone_operator_readback,
)


class Phase324BackboneNonPatchFixtureReadbackDecisionBoundaryTests(unittest.TestCase):
    def _blocked_decision_map(self):
        assessment = assess_research_claim_fixture_decision_boundary()
        return {item["decision"]: item for item in assessment["blocked_decisions"]}

    def test_operator_readback_exists_and_is_deterministic(self):
        first = read_research_claim_fixture_backbone_operator_readback()
        second = read_research_claim_fixture_backbone_operator_readback()

        self.assertEqual(first, second)
        self.assertTrue(first["research_claim_fixture_backbone_operator_readback"])

    def test_readback_reports_fixture_context_and_ordered_stages(self):
        readback = read_research_claim_fixture_backbone_operator_readback()
        expected_stage_names = [
            mapping.stage_name
            for mapping in ordered_research_claim_fixture_backbone_stage_mappings()
        ]

        self.assertEqual(readback["bounded_context"], "research_claim_packet_fixture")
        self.assertEqual(readback["mapped_stage_names"], expected_stage_names)
        self.assertEqual(
            readback["mapped_stage_names"],
            readback["expected_backbone_stage_names"],
        )
        self.assertEqual(readback["status_counts"]["incomplete"], 0)

    def test_readback_preserves_false_execution_and_mutation_claims(self):
        readback = read_research_claim_fixture_backbone_operator_readback()

        self.assertFalse(readback["backbone_v0_declared"])
        self.assertFalse(readback["adapter_execution_allowed"])
        self.assertFalse(readback["adapters_executable_through_mapping"])
        self.assertFalse(readback["real_domain_action_executed"])
        self.assertFalse(readback["live_record_mutated"])

    def test_readback_exposes_reference_only_fixture_evidence(self):
        readback = read_research_claim_fixture_backbone_operator_readback()
        evidence = readback["fixture_evidence_strings"]

        self.assertTrue(evidence["evidence_is_reference_only"])
        self.assertIn(
            "fixtures/research_claim_packet/static_claim_packet.json",
            evidence["fixture_sources"],
        )
        self.assertIn("docs/PHASE_322.md", evidence["phase_docs"])
        self.assertIn(
            "tests/test_phase_322_backbone_non_patch_fixture_mapping.py",
            evidence["phase_tests"],
        )

    def test_readback_preserves_non_proofs_and_negative_edge_reasons(self):
        readback = read_research_claim_fixture_backbone_operator_readback()

        self.assertEqual(tuple(readback["non_proofs"]), RESEARCH_CLAIM_FIXTURE_NON_PROOFS)
        self.assertIn(
            "official_capsule_claim_rejected",
            readback["possible_negative_edge_reason_codes"],
        )
        self.assertIn(
            "fixture_specific_native_field_rejected",
            readback["possible_negative_edge_reason_codes"],
        )
        self.assertFalse(readback["official_capsule_proof_current"])

    def test_incomplete_readback_reports_blocked_conditions_without_v0(self):
        incomplete_mapping = ResearchClaimFixtureBackboneStageMapping(
            stage_name="readback",
            fixture_sources=(),
            phase_docs=("docs/PHASE_322.md",),
            phase_tests=("tests/test_phase_322_backbone_non_patch_fixture_mapping.py",),
        )

        readback = read_research_claim_fixture_backbone_operator_readback(
            [incomplete_mapping]
        )

        self.assertEqual(readback["status_counts"]["incomplete"], 1)
        self.assertIn("fixture_source_missing", readback["blocked_conditions"])
        self.assertFalse(readback["backbone_v0_declared"])

    def test_decision_boundary_assessment_exists_and_is_deterministic(self):
        first = assess_research_claim_fixture_decision_boundary()
        second = read_research_claim_fixture_decision_boundary_status()

        self.assertEqual(first, second)
        self.assertTrue(first["research_claim_fixture_decision_boundary"])

    def test_required_blocked_decisions_are_present(self):
        blocked = self._blocked_decision_map()

        for decision in RESEARCH_CLAIM_FIXTURE_BLOCKED_DECISIONS:
            self.assertIn(decision, blocked)
            self.assertEqual(blocked[decision]["status"], "blocked")

    def test_decision_boundary_blocks_v0_execution_mutation_and_claims(self):
        blocked = self._blocked_decision_map()

        self.assertEqual(
            blocked["declare_backbone_v0"]["reason_code"],
            "backbone_v0_not_declared",
        )
        self.assertEqual(
            blocked["execute_real_domain_actions"]["reason_code"],
            "real_domain_execution_not_allowed",
        )
        self.assertEqual(
            blocked["mutate_live_records"]["reason_code"],
            "live_record_mutation_not_allowed",
        )
        self.assertEqual(
            blocked["claim_semantic_correctness"]["reason_code"],
            "semantic_correctness_not_proven",
        )
        self.assertEqual(
            blocked["claim_production_readiness"]["reason_code"],
            "production_readiness_not_proven",
        )

    def test_decision_boundary_preserves_campaign_stop_after_phase_324(self):
        assessment = assess_research_claim_fixture_decision_boundary()

        self.assertTrue(assessment["campaign_stop_required_after_phase_324"])
        self.assertEqual(
            assessment["recommended_next_boundary_after_campaign_stop"],
            RESEARCH_CLAIM_FIXTURE_RECOMMENDED_NEXT_BOUNDARY_AFTER_STOP,
        )
        self.assertNotIn("V0_DECLARATION", RESEARCH_CLAIM_FIXTURE_RECOMMENDED_NEXT_BOUNDARY_AFTER_STOP)

    def test_decision_boundary_preserves_expected_non_proofs(self):
        assessment = assess_research_claim_fixture_decision_boundary()

        self.assertIn(
            "research_claim_fixture_mapping_is_not_semantic_correctness",
            assessment["non_proofs"],
        )
        self.assertFalse(assessment["backbone_v0_declared"])
        self.assertFalse(assessment["official_capsule_proof_current"])
        self.assertFalse(assessment["provider_model_runtime_platform_execution_claimed"])
        self.assertFalse(assessment["service_api_ui_dashboard_auth_deployment_claimed"])


if __name__ == "__main__":
    unittest.main()
