import tempfile
import unittest
from pathlib import Path

from orchestrator.dry_mvp_commit_readiness_review import (
    BOUNDARY,
    EXPECTED_MVP_FILES,
    RECOMMENDED_NEXT_BOUNDARY,
    build_dry_mvp_commit_readiness_review_dict,
    render_dry_mvp_commit_readiness_review_markdown,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DryMvpCommitReadinessReviewTests(unittest.TestCase):
    def test_review_passes_when_acceptance_and_expected_files_are_present(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = build_dry_mvp_commit_readiness_review_dict(
                output_dir=directory,
                project_root=PROJECT_ROOT,
            )

        self.assertEqual(packet["boundary"], BOUNDARY)
        self.assertEqual(packet["readiness_status"], "dry_mvp_ready_for_roger_commit_decision")
        self.assertEqual(packet["blocked_conditions"], [])
        self.assertEqual(packet["missing_requirements"], [])
        self.assertEqual(packet["expected_file_inventory"]["expected_file_count"], len(EXPECTED_MVP_FILES))
        self.assertEqual(packet["expected_file_inventory"]["missing_files"], [])

    def test_review_blocks_when_integrated_acceptance_has_not_passed(self):
        acceptance = {
            "acceptance_status": "dry_mvp_integrated_acceptance_blocked",
            "commit_readiness_assessment": "not_ready_for_commit_review_until_blockers_are_repaired",
        }
        packet = build_dry_mvp_commit_readiness_review_dict(
            acceptance_packet=acceptance,
            project_root=PROJECT_ROOT,
        )

        self.assertEqual(packet["readiness_status"], "dry_mvp_not_ready_for_roger_commit_decision")
        self.assertIn("integrated_acceptance_not_passed", packet["blocked_conditions"])
        self.assertIn(
            "acceptance_packet_not_ready_for_human_commit_review",
            packet["blocked_conditions"],
        )

    def test_review_blocks_when_expected_files_are_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            acceptance = {
                "acceptance_status": "dry_mvp_integrated_acceptance_pass",
                "commit_readiness_assessment": "ready_for_human_commit_review_not_committed",
            }
            packet = build_dry_mvp_commit_readiness_review_dict(
                acceptance_packet=acceptance,
                project_root=directory,
            )

        self.assertEqual(packet["readiness_status"], "dry_mvp_not_ready_for_roger_commit_decision")
        self.assertIn("expected_mvp_files_missing", packet["blocked_conditions"])
        self.assertIn("orchestrator/dry_mvp_commit_readiness_review.py", packet["missing_requirements"])

    def test_false_posture_flags_remain_false(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = build_dry_mvp_commit_readiness_review_dict(
                output_dir=directory,
                project_root=PROJECT_ROOT,
            )

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
            "commit_performed",
            "push_performed",
        ):
            self.assertIs(packet[flag], False, flag)

    def test_renderer_is_commit_decision_legible(self):
        with tempfile.TemporaryDirectory() as directory:
            rendered = render_dry_mvp_commit_readiness_review_markdown(
                build_dry_mvp_commit_readiness_review_dict(
                    output_dir=directory,
                    project_root=PROJECT_ROOT,
                )
            )

        for heading in (
            "## MVP Milestone Assessment",
            "## Source Acceptance",
            "## Expected File Inventory",
            "## Validation Commands",
            "## Roger Commit Decision Options",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("dry_mvp_ready_for_roger_commit_decision", rendered)
        self.assertIn("commit_performed=False", rendered)
        self.assertIn("push_performed=False", rendered)

    def test_recommended_next_boundary_is_roger_commit_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = build_dry_mvp_commit_readiness_review_dict(
                output_dir=directory,
                project_root=PROJECT_ROOT,
            )

        self.assertEqual(packet["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertEqual(packet["recommended_next_boundary"], "ROGER_DRY_MVP_COMMIT_DECISION_OPERATOR_REVIEW")


if __name__ == "__main__":
    unittest.main()
