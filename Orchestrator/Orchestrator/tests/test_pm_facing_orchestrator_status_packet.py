import unittest

from orchestrator.pm_facing_orchestrator_status_packet import (
    BOUNDARY,
    RECOMMENDED_NEXT_BOUNDARY,
    build_pm_facing_orchestrator_status_packet_dict,
    render_pm_facing_orchestrator_status_packet_markdown,
)


class PmFacingOrchestratorStatusPacketTests(unittest.TestCase):
    def test_packet_builds_with_exact_boundary(self):
        packet = build_pm_facing_orchestrator_status_packet_dict()

        self.assertEqual(packet["boundary"], BOUNDARY)
        self.assertEqual(packet["boundary"], "PM_FACING_ORCHESTRATOR_STATUS_PACKET_SOURCE_TEST_DOCS")

    def test_status_packet_explains_can_and_cannot_do(self):
        packet = build_pm_facing_orchestrator_status_packet_dict(
            {"closeout_decision": "dry_mvp_loop_closeout_pass"}
        )

        self.assertEqual(packet["overall_status"], "dry_mvp_loop_structurally_present")
        self.assertTrue(any("broad operator goal" in item for item in packet["what_orchestrator_can_do_now"]))
        self.assertTrue(any("queued report-only task" in item for item in packet["what_orchestrator_can_do_now"]))
        self.assertTrue(any("cannot yet call a local model" in item for item in packet["what_orchestrator_cannot_do_yet"]))
        self.assertTrue(any("cannot yet mutate" in item for item in packet["what_orchestrator_cannot_do_yet"]))

    def test_false_posture_is_preserved(self):
        packet = build_pm_facing_orchestrator_status_packet_dict()

        for flag in (
            "first_product_wedge_selected",
            "phase_387_implemented",
            "runtime_required",
            "provider_model_required",
            "worker_dispatched",
            "real_worker_executed",
            "mutation_authorized",
            "production_readiness_claimed",
        ):
            self.assertIs(packet[flag], False, flag)

    def test_rendered_markdown_is_pm_legible(self):
        rendered = render_pm_facing_orchestrator_status_packet_markdown(
            build_pm_facing_orchestrator_status_packet_dict(
                {"closeout_decision": "dry_mvp_loop_closeout_pass"}
            )
        )

        for heading in (
            "## Practical PM Assessment",
            "## What Orchestrator Can Do Now",
            "## What Orchestrator Cannot Do Yet",
            "## Recommended Next Moves",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("credible skeleton", rendered)
        self.assertIn("real_worker_executed=False", rendered)

    def test_recommended_next_boundary_points_to_integrated_acceptance(self):
        packet = build_pm_facing_orchestrator_status_packet_dict()

        self.assertEqual(packet["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertEqual(packet["recommended_next_boundary"], "DRY_MVP_INTEGRATED_ACCEPTANCE_SOURCE_TEST_DOCS")
        self.assertTrue(
            any("integrated dry MVP acceptance" in item for item in packet["recommended_next_moves"])
        )


if __name__ == "__main__":
    unittest.main()
