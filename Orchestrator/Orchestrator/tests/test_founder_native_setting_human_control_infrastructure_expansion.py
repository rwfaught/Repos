import unittest

from orchestrator.founder_native_setting_contradiction_analysis import ANALYSIS_NAME
from orchestrator.founder_native_setting_human_control_infrastructure_expansion import (
    BOUNDARY,
    CONTRADICTION_AREA,
    RECOMMENDED_NEXT_BOUNDARY,
    build_human_control_infrastructure_complexity_expansion,
    build_human_control_infrastructure_complexity_expansion_dict,
)
from orchestrator.founder_native_setting_fixture import SETTING_TITLE


class FounderNativeSettingHumanControlInfrastructureExpansionTests(unittest.TestCase):
    def test_boundary_and_contradiction_area_are_exact(self):
        expansion = build_human_control_infrastructure_complexity_expansion()

        self.assertEqual(
            expansion.boundary,
            "FOUNDER_NATIVE_SETTING_HUMAN_CONTROL_INFRASTRUCTURE_COMPLEXITY_EXPANSION_SOURCE_TEST_DOCS",
        )
        self.assertEqual(expansion.contradiction_area, "human_control_vs_infrastructure_complexity")

    def test_output_shape_and_parent_analysis_are_preserved(self):
        payload = build_human_control_infrastructure_complexity_expansion_dict()

        for field in (
            "expansion_name",
            "boundary",
            "setting_title",
            "parent_analysis_name",
            "contradiction_area",
            "central_design_engine_contradiction",
            "core_claim",
            "infrastructure_domains",
            "explanation_standards",
            "accountability_failure_modes",
            "causal_court_functions",
            "human_override_doctrine_implications",
            "generated_story_or_worldbuilding_pressures",
            "next_work_items",
            "explicit_non_proofs",
            "product_wedge_selection",
            "first_product_wedge_selected",
            "phase_387_implemented",
            "runtime_required",
            "provider_model_required",
            "recommended_next_boundary",
        ):
            self.assertIn(field, payload)

        self.assertEqual(payload["setting_title"], SETTING_TITLE)
        self.assertEqual(payload["parent_analysis_name"], ANALYSIS_NAME)

    def test_expansion_preserves_required_non_proofs(self):
        expansion = build_human_control_infrastructure_complexity_expansion()

        for non_proof in (
            "no semantic correctness proof",
            "no model reasoning proof",
            "no runtime/provider/model proof",
            "no production readiness proof",
            "no Phase 387 implementation",
            "no first product wedge selection",
        ):
            self.assertIn(non_proof, expansion.explicit_non_proofs)

    def test_flags_remain_false(self):
        expansion = build_human_control_infrastructure_complexity_expansion()

        self.assertFalse(expansion.first_product_wedge_selected)
        self.assertFalse(expansion.phase_387_implemented)
        self.assertFalse(expansion.runtime_required)
        self.assertFalse(expansion.provider_model_required)

    def test_structured_material_is_present_for_required_categories(self):
        expansion = build_human_control_infrastructure_complexity_expansion()

        self.assertGreaterEqual(len(expansion.infrastructure_domains), 4)
        self.assertGreaterEqual(len(expansion.explanation_standards), 4)
        self.assertGreaterEqual(len(expansion.accountability_failure_modes), 5)
        self.assertGreaterEqual(len(expansion.causal_court_functions), 4)
        self.assertGreaterEqual(len(expansion.human_override_doctrine_implications), 5)
        self.assertGreaterEqual(len(expansion.generated_story_or_worldbuilding_pressures), 5)
        self.assertGreaterEqual(len(expansion.next_work_items), 3)

    def test_content_deepens_human_control_infrastructure_complexity(self):
        expansion = build_human_control_infrastructure_complexity_expansion()
        surface = str(expansion.to_dict())

        for concept in (
            "Causal Courts",
            "explanation standards",
            "fake accountability",
            "command-chain law",
            "infrastructure paralysis",
            "human override",
            "performative human sovereignty",
        ):
            self.assertIn(concept, surface)

    def test_infrastructure_domains_include_expected_civilization_systems(self):
        expansion = build_human_control_infrastructure_complexity_expansion()
        domain_names = {domain.name for domain in expansion.infrastructure_domains}

        self.assertIn("fusion grids", domain_names)
        self.assertIn("orbital traffic", domain_names)
        self.assertIn("synthetic agriculture", domain_names)
        self.assertIn("weather buffering", domain_names)

    def test_recommended_next_boundary_is_exact(self):
        expansion = build_human_control_infrastructure_complexity_expansion()

        self.assertEqual(expansion.recommended_next_boundary, RECOMMENDED_NEXT_BOUNDARY)
        self.assertEqual(
            expansion.recommended_next_boundary,
            "FOUNDER_NATIVE_SETTING_HUMAN_CONTROL_INFRASTRUCTURE_COMPLEXITY_REVIEW_READONLY",
        )


if __name__ == "__main__":
    unittest.main()
