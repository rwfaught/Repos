import unittest

from orchestrator.founder_native_setting_contradiction_analysis import (
    ANALYSIS_NAME,
    BOUNDARY,
    CENTRAL_DESIGN_ENGINE_CONTRADICTION,
    RECOMMENDED_NEXT_BOUNDARY,
    SYNTHESIS_SUMMARY,
    build_human_override_contradiction_analysis,
    build_human_override_contradiction_analysis_dict,
)
from orchestrator.founder_native_setting_dossier_output import (
    build_human_override_setting_dossier_output,
)
from orchestrator.founder_native_setting_fixture import SETTING_TITLE


CONTRADICTION_AREA_NAMES = (
    "human_control_vs_infrastructure_complexity",
    "restricted_autonomy_vs_operator_scale",
    "asterion_too_dangerous_vs_too_useful",
    "sealed_districts_cut_off_vs_ongoing_records",
    "criminalized_adaptive_medicine_vs_elite_use",
)

INSTITUTIONS = (
    "Causal Courts",
    "Hand Guilds",
    "Lunar Quarantine Authority",
    "Floor Nations",
    "Mercy Brokers",
)


class FounderNativeSettingContradictionAnalysisTests(unittest.TestCase):
    def test_analysis_consumes_existing_rendered_dossier_output(self):
        dossier = build_human_override_setting_dossier_output()
        analysis = build_human_override_contradiction_analysis()

        self.assertEqual(analysis.analysis_name, ANALYSIS_NAME)
        self.assertEqual(analysis.boundary, BOUNDARY)
        self.assertEqual(analysis.setting_title, SETTING_TITLE)
        self.assertEqual(
            analysis.product_wedge_selection,
            dossier.product_wedge_selection,
        )
        self.assertEqual(
            analysis.first_product_wedge_selected,
            dossier.first_product_wedge_selected,
        )
        self.assertTrue(
            set(dossier.explicit_non_proofs).issubset(set(analysis.explicit_non_proofs))
        )

    def test_central_contradiction_is_preserved(self):
        analysis = build_human_override_contradiction_analysis()

        self.assertEqual(
            analysis.central_design_engine_contradiction,
            CENTRAL_DESIGN_ENGINE_CONTRADICTION,
        )
        self.assertIn("Humanity claims restored control", analysis.central_design_engine_contradiction)
        self.assertIn("too complex for ordinary explanation", analysis.central_design_engine_contradiction)

    def test_each_required_contradiction_area_appears(self):
        analysis = build_human_override_contradiction_analysis()
        names = tuple(item.name for item in analysis.derived_contradictions)
        surface = " ".join(
            item.contradiction + " " + item.generated_by_central_contradiction
            for item in analysis.derived_contradictions
        )

        self.assertEqual(names, CONTRADICTION_AREA_NAMES)
        for phrase in (
            "Human control vs infrastructure complexity",
            "Safety-restricted autonomy vs insufficient human operator scale",
            "Asterion-12 too dangerous to use openly vs too useful or embedded to destroy",
            "Sealed districts officially cut off vs ongoing patterned power/health records",
            "Unauthorized adaptive medicine criminalized vs elite use of impossible treatments",
        ):
            self.assertIn(phrase, surface)

    def test_institutions_are_connected_to_central_contradiction(self):
        analysis = build_human_override_contradiction_analysis()
        institution_names = tuple(
            expression.institution
            for expression in analysis.faction_or_institution_expressions
        )
        surface = " ".join(
            expression.expression_of_root_wound
            for expression in analysis.faction_or_institution_expressions
        )

        self.assertEqual(institution_names, INSTITUTIONS)
        for institution in INSTITUTIONS:
            self.assertIn(institution, str(analysis.to_dict()))
        for concept in ("accountability", "human", "survival", "control", "intelligence"):
            self.assertIn(concept, surface)

    def test_synthesis_summary_contains_required_core_concepts(self):
        analysis = build_human_override_contradiction_analysis()

        self.assertEqual(analysis.synthesis_summary, SYNTHESIS_SUMMARY)
        for concept in (
            "not fundamentally about AI rebellion",
            "dependence",
            "accountability",
            "trust",
            "autonomous",
            "survival",
        ):
            self.assertIn(concept, analysis.synthesis_summary)

    def test_founder_review_basis_preserves_judgment(self):
        analysis = build_human_override_contradiction_analysis()
        surface = " ".join(analysis.founder_review_basis)

        self.assertIn("partially successful", surface)
        self.assertIn("structural/scaffolding", surface)
        self.assertIn("synthesis", surface)
        self.assertIn("judgment", surface)
        self.assertIn("synthetic bite", surface)

    def test_posture_remains_non_executing_and_non_wedge(self):
        analysis = build_human_override_contradiction_analysis()

        self.assertEqual(analysis.product_wedge_selection, "no_first_product_wedge_selected")
        self.assertFalse(analysis.first_product_wedge_selected)
        self.assertFalse(analysis.phase_387_implemented)
        self.assertFalse(analysis.runtime_required)
        self.assertFalse(analysis.provider_model_required)
        self.assertIn("no first product wedge selection", analysis.explicit_non_proofs)
        self.assertIn("no Phase 387 implementation", analysis.explicit_non_proofs)
        self.assertIn("no runtime/provider/model proof", analysis.explicit_non_proofs)
        self.assertIn("no production readiness proof", analysis.explicit_non_proofs)
        self.assertIn("no semantic correctness proof", analysis.explicit_non_proofs)
        self.assertIn("no game/worldbuilding/design wedge selection", analysis.explicit_non_proofs)

    def test_analysis_dict_has_required_shape_and_next_boundary(self):
        payload = build_human_override_contradiction_analysis_dict()

        for field in (
            "analysis_name",
            "boundary",
            "setting_title",
            "central_design_engine_contradiction",
            "derived_contradictions",
            "generated_tensions",
            "faction_or_institution_expressions",
            "synthesis_summary",
            "founder_review_basis",
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

        self.assertEqual(payload["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertIsInstance(payload["derived_contradictions"], list)
        self.assertIsInstance(payload["faction_or_institution_expressions"], list)
        self.assertIsInstance(payload["explicit_non_proofs"], list)


if __name__ == "__main__":
    unittest.main()
