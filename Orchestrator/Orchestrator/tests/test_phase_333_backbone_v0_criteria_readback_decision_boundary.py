import unittest

from orchestrator.backbone_v0_criteria import (
    BACKBONE_V0_CRITERIA_READBACK_RECOMMENDED_NEXT_BOUNDARY,
    read_backbone_v0_criteria_operator_readback,
)
from orchestrator.backbone_v0_criteria_decision_boundary import (
    BACKBONE_V0_CRITERIA_BLOCKED_DECISIONS,
    assess_backbone_v0_criteria_decision_boundary,
    read_backbone_v0_criteria_decision_boundary_status,
)


class Phase333BackboneV0CriteriaReadbackDecisionBoundaryTests(unittest.TestCase):
    def _blocked_decision_map(self):
        assessment = assess_backbone_v0_criteria_decision_boundary()
        return {item["decision"]: item for item in assessment["blocked_decisions"]}

    def test_criteria_readback_exists_and_is_deterministic(self):
        first = read_backbone_v0_criteria_operator_readback()
        second = read_backbone_v0_criteria_operator_readback()

        self.assertEqual(first, second)
        self.assertTrue(first["backbone_v0_criteria_operator_readback"])

    def test_readback_reports_criteria_status_and_missing_requirements(self):
        readback = read_backbone_v0_criteria_operator_readback()

        self.assertEqual(readback["criteria_count"], 13)
        self.assertTrue(
            readback["current_satisfaction_status"][
                "all_criteria_satisfied_for_definition"
            ]
        )
        self.assertEqual(readback["missing_requirements"], [])
        self.assertFalse(readback["backbone_v0_declared"])
        self.assertFalse(readback["backbone_v0_declaration_allowed_now"])

    def test_readback_reports_deferred_and_allowed_next_decisions(self):
        readback = read_backbone_v0_criteria_operator_readback()

        self.assertIn("backbone_v0_declaration", readback["deferred_decisions"])
        self.assertIn(
            "official_declaration_export_or_capsule_claim",
            readback["deferred_decisions"],
        )
        self.assertEqual(
            readback["allowed_next_decisions"],
            ["read_only_declaration_readiness_assessment"],
        )

    def test_decision_boundary_exists_and_is_deterministic(self):
        first = assess_backbone_v0_criteria_decision_boundary()
        second = read_backbone_v0_criteria_decision_boundary_status()

        self.assertEqual(first, second)
        self.assertTrue(first["backbone_v0_criteria_decision_boundary"])

    def test_required_blocked_decisions_are_present(self):
        blocked = self._blocked_decision_map()

        for decision in BACKBONE_V0_CRITERIA_BLOCKED_DECISIONS:
            self.assertIn(decision, blocked)
            self.assertEqual(blocked[decision]["status"], "blocked")

    def test_decision_boundary_blocks_declaration_and_live_or_runtime_claims(self):
        blocked = self._blocked_decision_map()

        self.assertEqual(
            blocked["declare_backbone_v0"]["reason_code"],
            "backbone_v0_not_declared",
        )
        self.assertEqual(
            blocked["claim_semantic_correctness"]["reason_code"],
            "semantic_correctness_not_proven",
        )
        self.assertEqual(
            blocked["claim_production_readiness"]["reason_code"],
            "production_readiness_not_proven",
        )
        self.assertEqual(
            blocked["claim_provider_model_runtime_platform_execution"]["reason_code"],
            "provider_model_runtime_platform_not_executed",
        )
        self.assertEqual(
            blocked["access_live_obsidian_vault"]["reason_code"],
            "live_obsidian_vault_access_not_allowed",
        )

    def test_decision_boundary_recommends_phase_334_read_only(self):
        assessment = assess_backbone_v0_criteria_decision_boundary()

        self.assertEqual(
            assessment["recommended_next_boundary"],
            BACKBONE_V0_CRITERIA_READBACK_RECOMMENDED_NEXT_BOUNDARY,
        )
        self.assertEqual(
            assessment["recommended_next_boundary"],
            "PHASE334_BACKBONE_V0_DECLARATION_READINESS_ASSESSMENT_READONLY",
        )
        self.assertNotIn("DECLARATION_SOURCE", assessment["recommended_next_boundary"])

    def test_non_proofs_and_capsule_absence_are_preserved(self):
        assessment = assess_backbone_v0_criteria_decision_boundary()

        self.assertFalse(assessment["official_capsule_proof_current"])
        self.assertFalse(assessment["semantic_correctness_claimed"])
        self.assertFalse(assessment["production_readiness_claimed"])
        self.assertFalse(assessment["provider_model_runtime_platform_execution_claimed"])
        self.assertFalse(assessment["service_api_ui_dashboard_auth_deployment_claimed"])
        self.assertIn(
            "criteria_do_not_declare_backbone_v0",
            assessment["non_proofs"],
        )


if __name__ == "__main__":
    unittest.main()
