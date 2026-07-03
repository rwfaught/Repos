import importlib
import sys
import unittest

from orchestrator.backbone_mapping_operator_decision_boundary import (
    BACKBONE_MAPPING_OPERATOR_BLOCKED_DECISIONS,
    BACKBONE_MAPPING_OPERATOR_RECOMMENDED_NEXT_BOUNDARY,
    assess_backbone_mapping_operator_decision_boundary,
    read_backbone_mapping_operator_decision_boundary_status,
)


PATCH_LOOP_MODULES = (
    "orchestrator.packet_result_patch_proposal_eligibility",
    "orchestrator.packet_result_patch_proposal_candidate",
    "orchestrator.patch_proposal_candidate_promotion",
    "orchestrator.promoted_candidate_draft_patch_proposal",
    "orchestrator.draft_patch_proposal_apply_authorization_eligibility",
    "orchestrator.draft_patch_proposal_apply_authorization_record",
    "orchestrator.authorized_draft_patch_apply",
    "orchestrator.authorized_bounded_apply_result_verification",
    "orchestrator.verified_bounded_apply_task_finalization",
)


class Phase320BackboneMappingOperatorDecisionBoundaryTests(unittest.TestCase):
    def _blocked_decision_map(self):
        assessment = assess_backbone_mapping_operator_decision_boundary()
        return {
            item["decision"]: item
            for item in assessment["blocked_decisions"]
        }

    def test_decision_boundary_assessment_exists_and_is_deterministic(self):
        first = assess_backbone_mapping_operator_decision_boundary()
        second = read_backbone_mapping_operator_decision_boundary_status()

        self.assertEqual(first, second)
        self.assertTrue(first["backbone_mapping_operator_decision_boundary"])

    def test_backbone_v0_declaration_is_blocked(self):
        blocked = self._blocked_decision_map()

        self.assertEqual(blocked["declare_backbone_v0"]["status"], "blocked")
        self.assertEqual(
            blocked["declare_backbone_v0"]["reason_code"],
            "backbone_v0_not_declared",
        )
        self.assertFalse(assess_backbone_mapping_operator_decision_boundary()["backbone_v0_declared"])

    def test_adapter_execution_is_blocked(self):
        blocked = self._blocked_decision_map()

        self.assertEqual(blocked["execute_adapters"]["status"], "blocked")
        self.assertEqual(
            blocked["execute_adapters"]["reason_code"],
            "adapter_execution_disabled",
        )

    def test_patch_loop_migration_is_blocked(self):
        blocked = self._blocked_decision_map()

        self.assertEqual(blocked["migrate_patch_loop"]["status"], "blocked")
        self.assertEqual(
            blocked["migrate_patch_loop"]["reason_code"],
            "patch_loop_not_migrated",
        )

    def test_semantic_correctness_and_production_readiness_claims_are_blocked(self):
        blocked = self._blocked_decision_map()

        self.assertEqual(
            blocked["claim_semantic_correctness"]["reason_code"],
            "semantic_correctness_not_proven",
        )
        self.assertEqual(
            blocked["claim_production_readiness"]["reason_code"],
            "production_readiness_not_proven",
        )

    def test_provider_model_runtime_platform_claims_are_blocked(self):
        blocked = self._blocked_decision_map()

        self.assertEqual(
            blocked["claim_provider_model_runtime_platform_execution"]["status"],
            "blocked",
        )
        self.assertEqual(
            blocked["claim_provider_model_runtime_platform_execution"]["reason_code"],
            "provider_model_runtime_platform_not_executed",
        )

    def test_required_blocked_decisions_are_present(self):
        blocked = self._blocked_decision_map()

        for decision in BACKBONE_MAPPING_OPERATOR_BLOCKED_DECISIONS:
            self.assertIn(decision, blocked)
            self.assertEqual(blocked[decision]["status"], "blocked")

    def test_non_proofs_from_phase_319_readback_are_preserved(self):
        assessment = assess_backbone_mapping_operator_decision_boundary()

        self.assertIn(
            "code_patching_mapping_is_not_semantic_correctness",
            assessment["non_proofs"],
        )
        self.assertIn(
            "code_patching_mapping_does_not_declare_backbone_v0",
            assessment["non_proofs"],
        )

    def test_decision_surface_exposes_allowed_blocked_and_deferred_decisions(self):
        assessment = assess_backbone_mapping_operator_decision_boundary()

        self.assertTrue(assessment["allowed_next_moves"])
        self.assertTrue(assessment["blocked_decisions"])
        self.assertTrue(assessment["deferred_decisions"])

    def test_cross_domain_fixture_mapping_is_recommended_next_move(self):
        assessment = assess_backbone_mapping_operator_decision_boundary()

        self.assertEqual(
            assessment["recommended_next_boundary"],
            BACKBONE_MAPPING_OPERATOR_RECOMMENDED_NEXT_BOUNDARY,
        )
        self.assertIn(
            BACKBONE_MAPPING_OPERATOR_RECOMMENDED_NEXT_BOUNDARY,
            assessment["allowed_next_boundaries"],
        )
        self.assertEqual(
            assessment["allowed_next_moves"][0]["decision"],
            "cross_domain_fixture_mapping_proof_boundary",
        )

    def test_docs_only_backbone_v0_criteria_is_not_immediate_declaration(self):
        assessment = assess_backbone_mapping_operator_decision_boundary()
        deferred = {
            item["decision"]: item
            for item in assessment["deferred_decisions"]
        }

        self.assertEqual(
            deferred["docs_only_backbone_v0_criteria_phase"]["status"],
            "deferred",
        )
        self.assertEqual(
            deferred["docs_only_backbone_v0_criteria_phase"]["reason_code"],
            "single_bounded_context_only",
        )

    def test_official_clean_capsule_proof_is_future_requirement_not_current_proof(self):
        assessment = assess_backbone_mapping_operator_decision_boundary()

        self.assertTrue(assessment["official_clean_capsule_required_before_declaration"])
        self.assertFalse(assessment["official_capsule_proof_current"])

    def test_decision_boundary_does_not_import_or_execute_patch_loop_modules(self):
        before = {name for name in PATCH_LOOP_MODULES if name in sys.modules}

        module = importlib.import_module(
            "orchestrator.backbone_mapping_operator_decision_boundary"
        )
        module.assess_backbone_mapping_operator_decision_boundary()

        after = {name for name in PATCH_LOOP_MODULES if name in sys.modules}
        self.assertEqual(after - before, set())


if __name__ == "__main__":
    unittest.main()
