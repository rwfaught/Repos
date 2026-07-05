import unittest

from orchestrator.founder_native_setting_causal_court_micro_scenario import (
    BOUNDARY,
    RECOMMENDED_NEXT_BOUNDARY,
    build_causal_court_micro_scenario,
    build_causal_court_micro_scenario_dict,
)
from orchestrator.founder_native_setting_human_control_infrastructure_expansion import (
    CONTRADICTION_AREA,
    EXPANSION_NAME,
)


class FounderNativeSettingCausalCourtMicroScenarioTests(unittest.TestCase):
    def test_boundary_and_recommended_next_boundary_are_exact(self):
        scenario = build_causal_court_micro_scenario()

        self.assertEqual(
            scenario.boundary,
            "FOUNDER_NATIVE_SETTING_CAUSAL_COURT_MICRO_SCENARIO_SOURCE_TEST_DOCS",
        )
        self.assertEqual(scenario.boundary, BOUNDARY)
        self.assertEqual(
            scenario.recommended_next_boundary,
            "FOUNDER_NATIVE_SETTING_CAUSAL_COURT_MICRO_SCENARIO_REVIEW_READONLY",
        )
        self.assertEqual(scenario.recommended_next_boundary, RECOMMENDED_NEXT_BOUNDARY)

    def test_source_expansion_and_contradiction_area_are_preserved(self):
        scenario = build_causal_court_micro_scenario()

        self.assertEqual(scenario.source_expansion_name, EXPANSION_NAME)
        self.assertEqual(scenario.source_contradiction_area, CONTRADICTION_AREA)
        self.assertEqual(
            scenario.source_contradiction_area,
            "human_control_vs_infrastructure_complexity",
        )

    def test_output_shape_contains_required_fields(self):
        payload = build_causal_court_micro_scenario_dict()

        for field in (
            "scenario_name",
            "boundary",
            "setting_title",
            "source_expansion_name",
            "source_contradiction_area",
            "case_title",
            "case_type",
            "infrastructure_domain",
            "incident_summary",
            "time_pressure",
            "machine_recommendation",
            "human_override_options",
            "human_decision_point",
            "selected_incident_path",
            "explanation_standard_conflict",
            "causal_chain_fragments",
            "affected_parties",
            "causal_court_questions",
            "accountability_candidates",
            "accountability_failure_modes_triggered",
            "human_override_doctrine_test",
            "story_pressure_generated",
            "why_this_tests_the_setting",
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

    def test_scenario_is_one_concrete_case_not_unrelated_scenarios(self):
        scenario = build_causal_court_micro_scenario()

        self.assertEqual(
            scenario.case_title,
            "The Six-Minute New Jakarta Fusion-Grid Override",
        )
        self.assertEqual(scenario.infrastructure_domain, "fusion grids")
        self.assertIn("New Jakarta", scenario.incident_summary)
        self.assertIsInstance(scenario.selected_incident_path, str)
        self.assertNotIn("scenario_options", scenario.to_dict())

    def test_required_structured_material_is_present(self):
        scenario = build_causal_court_micro_scenario()

        self.assertTrue(scenario.incident_summary)
        self.assertTrue(scenario.time_pressure)
        self.assertTrue(scenario.machine_recommendation)
        self.assertGreaterEqual(len(scenario.human_override_options), 3)
        self.assertTrue(scenario.human_decision_point)
        self.assertTrue(scenario.explanation_standard_conflict)
        self.assertGreaterEqual(len(scenario.causal_chain_fragments), 4)
        self.assertGreaterEqual(len(scenario.affected_parties), 4)
        self.assertGreaterEqual(len(scenario.causal_court_questions), 5)
        self.assertGreaterEqual(len(scenario.accountability_candidates), 5)
        self.assertGreaterEqual(len(scenario.accountability_failure_modes_triggered), 4)
        self.assertGreaterEqual(len(scenario.human_override_doctrine_test), 6)
        self.assertGreaterEqual(len(scenario.story_pressure_generated), 4)
        self.assertGreaterEqual(len(scenario.why_this_tests_the_setting), 4)
        self.assertGreaterEqual(len(scenario.next_work_items), 3)

    def test_required_concepts_are_structurally_preserved(self):
        surface = str(build_causal_court_micro_scenario_dict())

        for concept in (
            "Causal Court",
            "explanation standards",
            "fake accountability",
            "infrastructure paralysis",
            "command-chain law",
            "human override",
            "performative human sovereignty",
        ):
            self.assertIn(concept, surface)

    def test_explicit_non_proofs_are_preserved(self):
        scenario = build_causal_court_micro_scenario()

        for non_proof in (
            "no semantic correctness proof",
            "no model reasoning proof",
            "no runtime/provider/model proof",
            "no production readiness proof",
            "no Phase 387 implementation",
            "no first product wedge selection",
            "no game/worldbuilding/design wedge selection",
            "no claims/disputes/appeals wedge selection",
            "no live model generation",
            "no provider calls",
            "no Source Files refresh/export/capsule proof",
        ):
            self.assertIn(non_proof, scenario.explicit_non_proofs)

    def test_false_flags_remain_false(self):
        scenario = build_causal_court_micro_scenario()

        self.assertFalse(scenario.first_product_wedge_selected)
        self.assertFalse(scenario.phase_387_implemented)
        self.assertFalse(scenario.runtime_required)
        self.assertFalse(scenario.provider_model_required)


if __name__ == "__main__":
    unittest.main()
