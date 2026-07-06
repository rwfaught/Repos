import tempfile
import unittest

from orchestrator.approved_bounded_task_packet_to_queued_task import create_queued_task_from_approved_bounded_packet
from orchestrator.bounded_task_packet_review_gate import build_bounded_task_packet_review_gate_dict
from orchestrator.dry_mvp_loop_closeout_review import (
    BOUNDARY,
    EXPLICIT_NON_PROOFS,
    RECOMMENDED_NEXT_BOUNDARY,
    build_dry_mvp_loop_closeout_review_dict,
    render_dry_mvp_loop_closeout_review_markdown,
)
from orchestrator.goal_intake_to_bounded_task_packet import DOGWALKING_APP_GOAL, build_goal_intake_to_bounded_task_packet_dict
from orchestrator.queued_task_execution_authorization_review import build_queued_task_execution_authorization_review_dict
from orchestrator.report_only_worker_execution_dry_run import run_report_only_worker_execution_dry_run
from orchestrator.report_only_worker_result_review import build_report_only_worker_result_review_dict


class DryMvpLoopCloseoutReviewTests(unittest.TestCase):
    def _accepted_result_review(self) -> dict:
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
        gate = build_bounded_task_packet_review_gate_dict(goal_packet)
        approval = {
            "decision": "approve_next_boundary",
            "roger_approved": True,
            "approval_note": "Approve queued task creation.",
        }
        authorization = {
            "decision": "authorize_report_only_execution_boundary",
            "roger_authorized": True,
            "authorization_note": "Authorize dry run only.",
        }
        with tempfile.TemporaryDirectory() as task_dir:
            task_creation = create_queued_task_from_approved_bounded_packet(gate, approval, task_dir)
        queued_review = build_queued_task_execution_authorization_review_dict(task_creation)
        with tempfile.TemporaryDirectory() as artifact_dir:
            dry_result = run_report_only_worker_execution_dry_run(queued_review, authorization, artifact_dir)
        return build_report_only_worker_result_review_dict(dry_result)

    def test_closeout_builds_with_exact_boundary(self):
        closeout = build_dry_mvp_loop_closeout_review_dict()

        self.assertEqual(closeout["boundary"], BOUNDARY)
        self.assertEqual(closeout["boundary"], "DRY_MVP_LOOP_CLOSEOUT_REVIEW_SOURCE_TEST_DOCS")

    def test_accepted_result_review_passes_closeout(self):
        closeout = build_dry_mvp_loop_closeout_review_dict(self._accepted_result_review())

        self.assertEqual(closeout["closeout_decision"], "dry_mvp_loop_closeout_pass")
        self.assertEqual(closeout["blocked_conditions"], [])
        self.assertIn("explicit Roger approval can create a queued report-only task record", closeout["proven_dry_capabilities"])
        self.assertIn("whether a later local-worker proof is worth authorizing", closeout["operator_can_now_judge"])

    def test_unaccepted_result_review_blocks_closeout(self):
        closeout = build_dry_mvp_loop_closeout_review_dict(
            {"review_decision": "needs_dry_result_repair", "missing_requirements": ["artifact_id"]}
        )

        self.assertEqual(closeout["closeout_decision"], "dry_mvp_loop_not_ready_for_closeout")
        self.assertIn("dry_worker_result_review_not_accepted", closeout["blocked_conditions"])
        self.assertIn("artifact_id", closeout["missing_requirements"])

    def test_false_flags_and_non_proofs_remain_visible(self):
        closeout = build_dry_mvp_loop_closeout_review_dict(self._accepted_result_review())

        for flag in (
            "runtime_required",
            "provider_model_required",
            "worker_dispatched",
            "real_worker_executed",
            "task_execution_authorized",
            "mutation_authorized",
            "production_readiness_claimed",
            "first_product_wedge_selected",
        ):
            self.assertIs(closeout[flag], False, flag)
        for non_proof in EXPLICIT_NON_PROOFS:
            self.assertIn(non_proof, closeout["explicit_non_proofs"])

    def test_rendered_markdown_preserves_closeout_shape(self):
        rendered = render_dry_mvp_loop_closeout_review_markdown(
            build_dry_mvp_loop_closeout_review_dict(self._accepted_result_review())
        )

        for heading in (
            "## Closeout Decision",
            "## Dry Loop Stages",
            "## Proven Dry Capabilities",
            "## Operator Can Now Judge",
            "## Next Real Options",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("dry_mvp_loop_closeout_pass", rendered)

    def test_recommended_next_boundary_points_to_pm_status_packet(self):
        closeout = build_dry_mvp_loop_closeout_review_dict()

        self.assertEqual(closeout["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertEqual(closeout["recommended_next_boundary"], "PM_FACING_ORCHESTRATOR_STATUS_PACKET_SOURCE_TEST_DOCS")


if __name__ == "__main__":
    unittest.main()
