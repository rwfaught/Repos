import tempfile
import unittest
from pathlib import Path

from orchestrator.dry_mvp_milestone_closeout import (
    BOUNDARY,
    RECOMMENDED_NEXT_BOUNDARY,
    build_dry_mvp_milestone_closeout_dict,
    render_dry_mvp_milestone_closeout_markdown,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DryMvpMilestoneCloseoutTests(unittest.TestCase):
    def test_closeout_passes_when_commit_readiness_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = build_dry_mvp_milestone_closeout_dict(
                output_dir=directory,
                project_root=PROJECT_ROOT,
            )

        self.assertEqual(packet["boundary"], BOUNDARY)
        self.assertEqual(
            packet["milestone_status"],
            "dry_mvp_source_test_docs_milestone_complete_pending_roger_commit_decision",
        )
        self.assertEqual(packet["blocked_conditions"], [])
        self.assertIn("integrated acceptance check", packet["what_is_complete"])
        self.assertIn("full CURRENT_SUCCESS_CRITERION.md proof for a real bounded task run", packet["what_is_not_complete"])

    def test_closeout_blocks_when_readiness_has_not_passed(self):
        packet = build_dry_mvp_milestone_closeout_dict(
            readiness_packet={
                "readiness_status": "dry_mvp_not_ready_for_roger_commit_decision",
                "missing_requirements": ["example_missing_file"],
            }
        )

        self.assertEqual(packet["milestone_status"], "dry_mvp_milestone_not_closed")
        self.assertIn("commit_readiness_review_not_passed", packet["blocked_conditions"])
        self.assertIn("example_missing_file", packet["missing_requirements"])

    def test_closeout_preserves_non_proofs_and_false_flags(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = build_dry_mvp_milestone_closeout_dict(
                output_dir=directory,
                project_root=PROJECT_ROOT,
            )

        self.assertIn("no full current-success-criterion proof", packet["explicit_non_proofs"])
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
            "full_current_success_criterion_claimed",
            "phase_387_implemented",
            "first_product_wedge_selected",
            "commit_performed",
            "push_performed",
        ):
            self.assertIs(packet[flag], False, flag)

    def test_renderer_is_pm_legible(self):
        with tempfile.TemporaryDirectory() as directory:
            rendered = render_dry_mvp_milestone_closeout_markdown(
                build_dry_mvp_milestone_closeout_dict(
                    output_dir=directory,
                    project_root=PROJECT_ROOT,
                )
            )

        for heading in (
            "## What Is Complete",
            "## What Is Not Complete",
            "## Milestone Requirements",
            "## Roger Decision Needed",
            "## Explicit Non-Proofs",
            "## Posture",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("dry_mvp_source_test_docs_milestone_complete_pending_roger_commit_decision", rendered)
        self.assertIn("full_current_success_criterion_claimed=False", rendered)

    def test_recommended_next_boundary_is_roger_commit_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = build_dry_mvp_milestone_closeout_dict(
                output_dir=directory,
                project_root=PROJECT_ROOT,
            )

        self.assertEqual(packet["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertEqual(packet["recommended_next_boundary"], "ROGER_DRY_MVP_COMMIT_DECISION_OPERATOR_REVIEW")


if __name__ == "__main__":
    unittest.main()
