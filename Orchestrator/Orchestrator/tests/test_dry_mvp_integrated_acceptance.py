import tempfile
import unittest
from pathlib import Path

from orchestrator.dry_mvp_integrated_acceptance import (
    BOUNDARY,
    RECOMMENDED_NEXT_BOUNDARY,
    build_dry_mvp_integrated_acceptance_dict,
    render_dry_mvp_integrated_acceptance_markdown,
)
from orchestrator.dry_mvp_loop_demo import run_dry_mvp_loop_demo


class DryMvpIntegratedAcceptanceTests(unittest.TestCase):
    def test_acceptance_passes_for_full_dry_demo_loop(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = build_dry_mvp_integrated_acceptance_dict(output_dir=directory)
            files = sorted(Path(directory).rglob("*.json"))

            self.assertEqual(packet["acceptance_status"], "dry_mvp_integrated_acceptance_pass")
            self.assertEqual(packet["boundary"], BOUNDARY)
            self.assertEqual(packet["artifact_inventory"]["json_file_count"], 2)
            self.assertEqual(len(files), 2)
            self.assertTrue(packet["artifact_inventory"]["paths_under_output_dir"])
            self.assertTrue(packet["artifact_inventory"]["has_task_json"])
            self.assertTrue(packet["artifact_inventory"]["has_artifact_json"])

    def test_stage_statuses_are_checked_as_one_chain(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = build_dry_mvp_integrated_acceptance_dict(output_dir=directory)

        self.assertEqual(packet["stage_statuses"]["demo_status"], "dry_mvp_demo_pass")
        self.assertEqual(packet["stage_statuses"]["task_creation"], "created")
        self.assertEqual(
            packet["stage_statuses"]["queued_task_review"],
            "ready_for_operator_execution_authorization_review",
        )
        self.assertEqual(packet["stage_statuses"]["dry_run"], "created")
        self.assertEqual(packet["stage_statuses"]["result_review"], "accepted_as_dry_loop_artifact")
        self.assertEqual(packet["stage_statuses"]["closeout"], "dry_mvp_loop_closeout_pass")
        self.assertEqual(packet["stage_statuses"]["pm_status"], "dry_mvp_loop_structurally_present")

    def test_acceptance_blocks_when_demo_status_is_stale_or_broken(self):
        with tempfile.TemporaryDirectory() as directory:
            demo = run_dry_mvp_loop_demo(directory)
            demo["dry_run"]["dry_run_status"] = "blocked"
            packet = build_dry_mvp_integrated_acceptance_dict(demo_result=demo)

        self.assertEqual(packet["acceptance_status"], "dry_mvp_integrated_acceptance_blocked")
        self.assertIn("dry_run_not_created", packet["blocked_conditions"])
        self.assertEqual(
            packet["commit_readiness_assessment"],
            "not_ready_for_commit_review_until_blockers_are_repaired",
        )

    def test_acceptance_blocks_when_required_non_proofs_are_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            demo = run_dry_mvp_loop_demo(directory)
            demo["non_proofs"] = []
            demo["closeout"]["explicit_non_proofs"] = []
            demo["pm_status"]["explicit_non_proofs"] = []
            demo["dry_run"]["explicit_non_proofs"] = []
            packet = build_dry_mvp_integrated_acceptance_dict(demo_result=demo)

        self.assertEqual(packet["acceptance_status"], "dry_mvp_integrated_acceptance_blocked")
        self.assertIn("no runtime/provider/model execution", packet["missing_requirements"])
        self.assertIn("no first product wedge selection", packet["missing_requirements"])

    def test_false_posture_flags_remain_false(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = build_dry_mvp_integrated_acceptance_dict(output_dir=directory)

        for flag in (
            "runtime_required",
            "provider_model_required",
            "worker_dispatched",
            "real_worker_executed",
            "task_execution_authorized",
            "mutation_authorized",
            "local_model_executed",
            "frontier_model_executed",
            "semantic_correctness_proven",
            "production_readiness_claimed",
            "phase_387_implemented",
            "first_product_wedge_selected",
        ):
            self.assertIs(packet[flag], False, flag)

    def test_renderer_is_operator_legible(self):
        with tempfile.TemporaryDirectory() as directory:
            rendered = render_dry_mvp_integrated_acceptance_markdown(
                build_dry_mvp_integrated_acceptance_dict(output_dir=directory)
            )

        for heading in (
            "## Stage Statuses",
            "## Artifact Inventory",
            "## Invariants Checked",
            "## Explicit Non-Proofs",
            "## Posture",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("dry_mvp_integrated_acceptance_pass", rendered)
        self.assertIn("ready_for_human_commit_review_not_committed", rendered)
        self.assertIn("worker_dispatched=False", rendered)

    def test_recommended_next_boundary_is_readonly_commit_readiness(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = build_dry_mvp_integrated_acceptance_dict(output_dir=directory)

        self.assertEqual(packet["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertEqual(packet["recommended_next_boundary"], "DRY_MVP_COMMIT_READINESS_REVIEW_SOURCE_TEST_DOCS")


if __name__ == "__main__":
    unittest.main()
