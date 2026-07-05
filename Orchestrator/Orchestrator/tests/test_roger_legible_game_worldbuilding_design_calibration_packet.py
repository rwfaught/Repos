import unittest

from orchestrator.roger_legible_game_worldbuilding_design_calibration_packet import (
    BOUNDARY,
    RECOMMENDED_NEXT_BOUNDARY,
    build_roger_legible_game_worldbuilding_design_calibration_packet_dict,
    render_roger_legible_game_worldbuilding_design_calibration_packet_markdown,
)


class RogerLegibleGameWorldbuildingDesignCalibrationPacketTests(unittest.TestCase):
    def test_packet_builds_as_dict_with_exact_boundary(self):
        packet = build_roger_legible_game_worldbuilding_design_calibration_packet_dict()

        self.assertIsInstance(packet, dict)
        self.assertEqual(
            packet["boundary"],
            "ROGER_LEGIBLE_GAME_WORLDBUILDING_DESIGN_CALIBRATION_PACKET_SOURCE_TEST_DOCS",
        )
        self.assertEqual(packet["boundary"], BOUNDARY)

    def test_required_sections_exist(self):
        packet = build_roger_legible_game_worldbuilding_design_calibration_packet_dict()

        for section in (
            "boundary",
            "purpose",
            "input_summary",
            "source_facts",
            "deterministic_structuring_step",
            "output_artifact",
            "coherence_pressures",
            "missing_or_underspecified_material",
            "roger_judgment_questions",
            "good_result_bad_result_criteria",
            "explicit_non_proofs",
            "open_threads",
            "recommended_next_boundary",
        ):
            self.assertIn(section, packet)

    def test_purpose_is_non_empty_and_calibration_legible(self):
        packet = build_roger_legible_game_worldbuilding_design_calibration_packet_dict()

        self.assertIsInstance(packet["purpose"], str)
        self.assertTrue(packet["purpose"].strip())
        self.assertIn("Roger", packet["purpose"])
        self.assertIn("calibration", packet["purpose"])

    def test_distinguishes_deterministic_structuring_from_live_creative_reasoning(self):
        packet = build_roger_legible_game_worldbuilding_design_calibration_packet_dict()
        step = packet["deterministic_structuring_step"]
        surface = str(packet)

        self.assertEqual(
            step["classification"],
            "deterministic_structuring_not_live_creative_reasoning",
        )
        self.assertIn("deterministically groups", step["what_orchestrator_does"])
        self.assertIn("does not perform live creative reasoning", surface)
        self.assertFalse(packet["live_creative_reasoning_claimed"])

    def test_source_facts_are_separated_from_coherence_pressures(self):
        packet = build_roger_legible_game_worldbuilding_design_calibration_packet_dict()

        self.assertGreaterEqual(len(packet["source_facts"]), 5)
        self.assertLessEqual(len(packet["source_facts"]), 10)
        self.assertNotEqual(packet["source_facts"], packet["coherence_pressures"])
        self.assertTrue(all(isinstance(item, str) for item in packet["source_facts"]))
        self.assertTrue(
            all("source_basis" in item for item in packet["coherence_pressures"])
        )

    def test_packet_does_not_generate_new_canon(self):
        packet = build_roger_legible_game_worldbuilding_design_calibration_packet_dict()
        surface = str(packet)

        self.assertFalse(packet["new_canon_generated"])
        self.assertIn("no new canon generated", surface)
        self.assertIn("without inventing new canon", surface)

    def test_required_false_flags_remain_false(self):
        packet = build_roger_legible_game_worldbuilding_design_calibration_packet_dict()

        self.assertFalse(packet["first_product_wedge_selected"])
        self.assertFalse(packet["phase_387_implemented"])
        self.assertFalse(packet["runtime_required"])
        self.assertFalse(packet["provider_model_required"])
        self.assertFalse(packet["game_worldbuilding_design_wedge_selected"])
        self.assertFalse(packet["claims_disputes_appeals_wedge_selected"])
        self.assertFalse(packet["new_canon_generated"])
        self.assertFalse(packet["live_creative_reasoning_claimed"])

    def test_required_explicit_non_proofs_are_preserved(self):
        packet = build_roger_legible_game_worldbuilding_design_calibration_packet_dict()

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

    def test_game_worldbuilding_design_is_calibration_candidate_not_selected_wedge(self):
        packet = build_roger_legible_game_worldbuilding_design_calibration_packet_dict()
        surface = str(packet)

        self.assertIn(
            "Game / Worldbuilding / Design remains only a calibration domain candidate",
            surface,
        )
        self.assertIn("without selecting a product wedge", surface)
        self.assertFalse(packet["game_worldbuilding_design_wedge_selected"])

    def test_recommended_next_boundary_is_review_only(self):
        packet = build_roger_legible_game_worldbuilding_design_calibration_packet_dict()

        self.assertEqual(packet["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertTrue(packet["recommended_next_boundary"].endswith("_REVIEW_READONLY"))

    def test_rendered_markdown_preserves_founder_facing_calibration_shape(self):
        rendered = (
            render_roger_legible_game_worldbuilding_design_calibration_packet_markdown()
        )

        for heading in (
            "## What Went In",
            "## Source Facts",
            "## What Orchestrator Did",
            "## What Came Out",
            "## Coherence Pressures",
            "## Missing Or Underspecified Material",
            "## What Roger Can Judge",
            "## Good Result",
            "## Bad Or Fake Result",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("Purpose: Give Roger a deterministic calibration packet", rendered)
        self.assertIn("deterministic_structuring_not_live_creative_reasoning", rendered)
        self.assertIn("no Game / Worldbuilding / Design wedge selection", rendered)
        self.assertIn("recommended_next_boundary=", rendered)


if __name__ == "__main__":
    unittest.main()
