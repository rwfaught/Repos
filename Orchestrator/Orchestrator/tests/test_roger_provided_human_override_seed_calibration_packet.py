import unittest

from orchestrator.roger_provided_human_override_seed_calibration_packet import (
    BOUNDARY,
    RECOMMENDED_NEXT_BOUNDARY,
    build_roger_provided_human_override_seed_calibration_packet_dict,
    render_roger_provided_human_override_seed_calibration_packet_markdown,
)


class RogerProvidedHumanOverrideSeedCalibrationPacketTests(unittest.TestCase):
    def test_packet_builds_as_dict_with_exact_boundary(self):
        packet = build_roger_provided_human_override_seed_calibration_packet_dict()

        self.assertIsInstance(packet, dict)
        self.assertEqual(
            packet["boundary"],
            "ROGER_PROVIDED_HUMAN_OVERRIDE_REAL_SEED_FIXTURE_PACKET_SOURCE_TEST_DOCS",
        )
        self.assertEqual(packet["boundary"], BOUNDARY)

    def test_input_is_roger_provided_source_material(self):
        packet = build_roger_provided_human_override_seed_calibration_packet_dict()

        self.assertEqual(
            packet["input_source"]["source_classification"],
            "roger_provided_source_material_not_generic_fixture",
        )
        self.assertEqual(packet["input_source"]["working_title"], "The Human Override")

    def test_required_sections_exist(self):
        packet = build_roger_provided_human_override_seed_calibration_packet_dict()

        for section in (
            "boundary",
            "purpose",
            "input_source",
            "source_facts_preserved",
            "deterministic_structuring_step",
            "inferences_and_coherence_pressures",
            "missing_or_underspecified_material",
            "world_logic_pressure_test",
            "design_pressure_test",
            "hard_choice_engine",
            "roger_judgment_questions",
            "good_result_bad_result_criteria",
            "explicit_non_proofs",
            "open_threads",
            "recommended_next_boundary",
        ):
            self.assertIn(section, packet)

    def test_required_source_anchors_are_preserved(self):
        packet = build_roger_provided_human_override_seed_calibration_packet_dict()
        surface = str(packet)

        for anchor in (
            "The Human Override",
            "The Causal Dark",
            "Mercy Exception",
            "The Three-Hour Override",
            "Asterion's Tomb",
            "2092 and 2098",
            "Three-Hour Override occurred in 2083",
            "General-purpose autonomous agents are tightly restricted",
            "human-recognizable causality",
            "The Causal Courts",
            "Asterion-12 was sealed in a lunar vault in 2089",
            "The Lunar Quarantine Authority",
            "The Hand Guilds",
            "sealed districts",
            "Geneva Mercy Exception",
            "Mercy Brokers",
            "claims restored sovereignty while secretly relying on forbidden intelligences",
        ):
            self.assertIn(anchor, surface)

    def test_source_facts_are_separated_from_pressure_test_inferences(self):
        packet = build_roger_provided_human_override_seed_calibration_packet_dict()
        source_facts = packet["source_facts_preserved"]["canon_facts"]
        pressures = packet["inferences_and_coherence_pressures"]

        self.assertNotEqual(source_facts, pressures)
        self.assertTrue(all(isinstance(item, str) for item in source_facts))
        self.assertTrue(
            all(
                item["classification"] == "pressure_test_inference_not_canon"
                for item in pressures
            )
        )

    def test_required_pressure_points_are_preserved_as_inferences(self):
        packet = build_roger_provided_human_override_seed_calibration_packet_dict()
        surface = str(packet)

        for pressure in (
            "human accountability versus machine-scale complexity",
            "not AI versus humanity",
            "Causal Courts are a strong central frame",
            "Mercy Economy is emotionally accessible",
            "Asterion should remain gravitational",
            "not become the answer key",
            "Explainability should remain partly legitimate and partly theatrical",
        ):
            self.assertIn(pressure, surface)

    def test_required_false_flags_remain_false(self):
        packet = build_roger_provided_human_override_seed_calibration_packet_dict()

        self.assertFalse(packet["first_product_wedge_selected"])
        self.assertFalse(packet["phase_387_implemented"])
        self.assertFalse(packet["runtime_required"])
        self.assertFalse(packet["provider_model_required"])
        self.assertFalse(packet["game_worldbuilding_design_wedge_selected"])
        self.assertFalse(packet["claims_disputes_appeals_wedge_selected"])
        self.assertFalse(packet["new_canon_generated"])
        self.assertFalse(packet["live_creative_reasoning_claimed"])
        self.assertFalse(packet["asterion_mystery_solved"])
        self.assertFalse(packet["semantic_correctness_proven"])

    def test_required_explicit_non_proofs_are_preserved(self):
        packet = build_roger_provided_human_override_seed_calibration_packet_dict()

        for non_proof in (
            "no runtime/provider/model proof",
            "no semantic correctness proof",
            "no production readiness proof",
            "no Phase 387 implementation",
            "no first product wedge selection",
            "no Game / Worldbuilding / Design wedge selection",
            "no claims/disputes/appeals wedge selection",
            "no Source Files refresh/export/capsule proof",
            "no live creative reasoning proof",
            "no new canon generation proof",
        ):
            self.assertIn(non_proof, packet["explicit_non_proofs"])

    def test_asterion_mystery_remains_unsolved(self):
        packet = build_roger_provided_human_override_seed_calibration_packet_dict()
        surface = str(packet)

        self.assertFalse(packet["asterion_mystery_solved"])
        self.assertIn("Do not solve the Asterion mystery", surface)
        self.assertIn("Asterion remains a gravitational mystery", surface)

    def test_recommended_next_boundary_is_review_only(self):
        packet = build_roger_provided_human_override_seed_calibration_packet_dict()

        self.assertEqual(packet["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertTrue(packet["recommended_next_boundary"].endswith("_REVIEW_READONLY"))

    def test_rendered_markdown_preserves_real_seed_packet_shape(self):
        rendered = render_roger_provided_human_override_seed_calibration_packet_markdown()

        for heading in (
            "## Input Source",
            "## Source Facts Preserved",
            "## Deterministic Structuring Step",
            "## Inferences And Coherence Pressures",
            "## Missing Or Underspecified Material",
            "## World Logic Pressure Test",
            "## Design Pressure Test",
            "## Hard Choice Engine",
            "## Roger Judgment Questions",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("roger_provided_source_material_not_generic_fixture", rendered)
        self.assertIn("deterministic_real_seed_preservation_not_live_reasoning", rendered)
        self.assertIn("recommended_next_boundary=", rendered)


if __name__ == "__main__":
    unittest.main()
