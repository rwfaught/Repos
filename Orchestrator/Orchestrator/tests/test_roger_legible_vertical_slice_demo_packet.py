import unittest

from orchestrator.roger_legible_vertical_slice_demo_packet import (
    BOUNDARY,
    RECOMMENDED_NEXT_BOUNDARY,
    build_roger_legible_vertical_slice_demo_packet_dict,
    render_roger_legible_vertical_slice_demo_packet_markdown,
)


class RogerLegibleVerticalSliceDemoPacketTests(unittest.TestCase):
    def test_packet_builds_as_dict_with_exact_boundary(self):
        packet = build_roger_legible_vertical_slice_demo_packet_dict()

        self.assertIsInstance(packet, dict)
        self.assertEqual(
            packet["boundary"],
            "ROGER_LEGIBLE_VERTICAL_SLICE_DEMO_PACKET_SOURCE_TEST_DOCS",
        )
        self.assertEqual(packet["boundary"], BOUNDARY)

    def test_required_sections_exist(self):
        packet = build_roger_legible_vertical_slice_demo_packet_dict()

        for section in (
            "purpose",
            "input",
            "orchestration_step",
            "output_artifact",
            "verification",
            "founder_judgment_questions",
            "explicit_non_proofs",
            "open_threads",
            "recommended_next_boundary",
        ):
            self.assertIn(section, packet)

    def test_purpose_is_non_empty_and_founder_legible(self):
        packet = build_roger_legible_vertical_slice_demo_packet_dict()

        self.assertIsInstance(packet["purpose"], str)
        self.assertTrue(packet["purpose"].strip())
        self.assertIn("Roger", packet["purpose"])
        self.assertIn("milestone demo", packet["purpose"])
        self.assertIn("what remains unproven", packet["purpose"])

    def test_packet_distinguishes_deterministic_packetization_from_live_reasoning(self):
        packet = build_roger_legible_vertical_slice_demo_packet_dict()
        orchestration_step = packet["orchestration_step"]

        self.assertEqual(
            orchestration_step["classification"],
            "deterministic_packetization_not_live_reasoning",
        )
        self.assertIn(
            "deterministic structuring",
            orchestration_step["what_orchestrator_does"],
        )
        self.assertIn(
            "live autonomous reasoning",
            orchestration_step["what_orchestrator_does_not_do"],
        )

    def test_required_false_flags_remain_false(self):
        packet = build_roger_legible_vertical_slice_demo_packet_dict()

        self.assertFalse(packet["first_product_wedge_selected"])
        self.assertFalse(packet["phase_387_implemented"])
        self.assertFalse(packet["runtime_required"])
        self.assertFalse(packet["provider_model_required"])
        self.assertFalse(packet["game_worldbuilding_design_wedge_selected"])
        self.assertFalse(packet["claims_disputes_appeals_wedge_selected"])

    def test_required_explicit_non_proofs_are_preserved(self):
        packet = build_roger_legible_vertical_slice_demo_packet_dict()

        for non_proof in (
            "no runtime/provider/model proof",
            "no semantic correctness proof",
            "no production readiness proof",
            "no Phase 387 implementation",
            "no first product wedge selection",
            "no Game / Worldbuilding / Design wedge selection",
            "no claims/disputes/appeals wedge selection",
            "no Source Files refresh/export/capsule proof",
        ):
            self.assertIn(non_proof, packet["explicit_non_proofs"])

    def test_game_worldbuilding_design_is_calibration_candidate_not_selected_wedge(self):
        packet = build_roger_legible_vertical_slice_demo_packet_dict()
        surface = str(packet)

        self.assertIn(
            "Game / Worldbuilding / Design remains a Roger-legible calibration domain candidate",
            surface,
        )
        self.assertIn("not a selected first product wedge", surface)
        self.assertFalse(packet["game_worldbuilding_design_wedge_selected"])

    def test_human_override_causal_court_is_supporting_material_not_product_direction(self):
        packet = build_roger_legible_vertical_slice_demo_packet_dict()
        surface = str(packet)

        self.assertIn("The Human Override", surface)
        self.assertIn("The Six-Minute New Jakarta Fusion-Grid Override", surface)
        self.assertIn("supporting material, not current product direction", surface)

    def test_recommended_next_boundary_is_review_only(self):
        packet = build_roger_legible_vertical_slice_demo_packet_dict()

        self.assertEqual(packet["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertTrue(packet["recommended_next_boundary"].endswith("_REVIEW_READONLY"))

    def test_rendered_markdown_preserves_founder_facing_demo_shape(self):
        rendered = render_roger_legible_vertical_slice_demo_packet_markdown()

        for heading in (
            "## What Went In",
            "## What Orchestrator Did",
            "## What Came Out",
            "## Verification",
            "## What Roger Can Judge",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("Purpose: Give Roger a compact milestone demo surface", rendered)
        self.assertIn("deterministic_packetization_not_live_reasoning", rendered)
        self.assertIn("Game / Worldbuilding / Design", rendered)
        self.assertIn("recommended_next_boundary=", rendered)


if __name__ == "__main__":
    unittest.main()
