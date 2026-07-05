import unittest

from orchestrator.founder_native_setting_dossier_output import (
    BOUNDARY,
    DRAFT_REPAIR_OR_RECOMMENDATION,
    OUTPUT_NAME,
    build_human_override_setting_dossier_output,
    build_human_override_setting_dossier_output_dict,
    render_human_override_setting_dossier_markdown,
)
from orchestrator.founder_native_setting_fixture import (
    DEMO_CANDIDATE,
    SETTING_TITLE,
    build_human_override_setting_fixture,
)


REQUIRED_OUTPUT_FIELDS = (
    "canon_facts",
    "contradictions",
    "missing_canon",
    "open_questions",
    "draft_repair_or_recommendation",
    "next_work_items",
    "explicit_non_proofs",
)

KEY_ANCHORS = (
    "Three-Hour Override",
    "forty-seven countries",
    "Harvest Refusal",
    "Hand Guilds",
    "Asterion-12",
    "Lunar Quarantine Authority",
    "New Jakarta",
    "Floor Nations",
    "Geneva Mercy Exception",
    "Mercy Brokers",
)


class FounderNativeSettingDossierOutputTests(unittest.TestCase):
    def test_output_consumes_existing_fixture(self):
        fixture = build_human_override_setting_fixture()
        output = build_human_override_setting_dossier_output()

        self.assertEqual(output.output_name, OUTPUT_NAME)
        self.assertEqual(output.boundary, BOUNDARY)
        self.assertEqual(output.demo_candidate, DEMO_CANDIDATE)
        self.assertEqual(output.setting_title, SETTING_TITLE)
        for extracted_fact in fixture.adapted_dossier_case["extracted_facts"]:
            self.assertIn(extracted_fact, output.canon_facts)
        self.assertEqual(output.contradictions, tuple(fixture.adapted_dossier_case["contradictions"]))
        self.assertEqual(output.missing_canon, tuple(fixture.adapted_dossier_case["missing_canon"]))
        self.assertEqual(output.open_questions, tuple(fixture.adapted_dossier_case["open_questions"]))

    def test_output_dict_has_required_visible_sections(self):
        payload = build_human_override_setting_dossier_output_dict()

        for field in REQUIRED_OUTPUT_FIELDS:
            self.assertIn(field, payload)

        self.assertIsInstance(payload["canon_facts"], list)
        self.assertIsInstance(payload["contradictions"], list)
        self.assertIsInstance(payload["missing_canon"], list)
        self.assertIsInstance(payload["open_questions"], list)
        self.assertIsInstance(payload["next_work_items"], list)
        self.assertIsInstance(payload["explicit_non_proofs"], list)

    def test_output_preserves_key_setting_anchors(self):
        payload = build_human_override_setting_dossier_output_dict()
        surface = " ".join(str(value) for value in payload.values())

        for anchor in KEY_ANCHORS:
            self.assertIn(anchor, surface)

    def test_source_facts_are_separate_from_recommendation(self):
        output = build_human_override_setting_dossier_output()
        canon_surface = " ".join(str(fact) for fact in output.canon_facts)

        self.assertIn("forty-seven countries", canon_surface)
        self.assertIn("Geneva Mercy Exception", canon_surface)
        self.assertEqual(output.draft_repair_or_recommendation, DRAFT_REPAIR_OR_RECOMMENDATION)
        self.assertNotIn(output.draft_repair_or_recommendation, canon_surface)

    def test_contradictions_missing_canon_and_open_questions_are_preserved(self):
        output = build_human_override_setting_dossier_output()

        self.assertEqual(len(output.contradictions), 5)
        self.assertEqual(len(output.missing_canon), 5)
        self.assertEqual(len(output.open_questions), 5)
        self.assertIn(
            "Asterion-12 is too dangerous to use openly, yet too useful or embedded to destroy.",
            output.contradictions,
        )
        self.assertTrue(
            any("valid explanation" in missing for missing in output.missing_canon)
        )
        self.assertTrue(
            any("bureaucratic theater" in question for question in output.open_questions)
        )

    def test_draft_repair_is_source_grounded_and_limited(self):
        output = build_human_override_setting_dossier_output()

        self.assertIn("post-AI sovereignty", output.draft_repair_or_recommendation)
        self.assertIn("real human control", output.draft_repair_or_recommendation)
        self.assertIn("bureaucratic ritual", output.draft_repair_or_recommendation)
        self.assertIn("negotiated dependency", output.draft_repair_or_recommendation)

    def test_output_preserves_no_wedge_no_phase_387_and_no_runtime_posture(self):
        output = build_human_override_setting_dossier_output()

        self.assertEqual(output.product_wedge_selection, "no_first_product_wedge_selected")
        self.assertFalse(output.first_product_wedge_selected)
        self.assertFalse(output.phase_387_implemented)
        self.assertFalse(output.runtime_required)
        self.assertFalse(output.provider_model_required)
        self.assertIn("no first product wedge selection", output.explicit_non_proofs)
        self.assertIn("no Phase 387 implementation", output.explicit_non_proofs)
        self.assertIn("no runtime proof", output.explicit_non_proofs)
        self.assertIn("no provider/model proof", output.explicit_non_proofs)
        self.assertIn("no game/worldbuilding/design wedge selection", output.explicit_non_proofs)
        self.assertIn("no semantic correctness proof", output.explicit_non_proofs)
        self.assertIn("no production readiness proof", output.explicit_non_proofs)
        self.assertIn("no live model generation", output.explicit_non_proofs)

    def test_markdown_renderer_exposes_visible_dossier_sections(self):
        text = render_human_override_setting_dossier_markdown()

        self.assertIn("# The Human Override Setting Consistency Dossier", text)
        for section in (
            "## Canon Facts",
            "## Contradictions",
            "## Missing Canon",
            "## Open Questions",
            "## Draft Repair Or Recommendation",
            "## Next Work Items",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(section, text)

    def test_markdown_renderer_preserves_anchors_and_posture(self):
        text = render_human_override_setting_dossier_markdown()

        for anchor in KEY_ANCHORS:
            self.assertIn(anchor, text)

        self.assertIn("product_wedge_selection=no_first_product_wedge_selected", text)
        self.assertIn("first_product_wedge_selected=false", text)
        self.assertIn("phase_387_implemented=false", text)
        self.assertIn("runtime_required=false", text)
        self.assertIn("provider_model_required=false", text)


if __name__ == "__main__":
    unittest.main()
