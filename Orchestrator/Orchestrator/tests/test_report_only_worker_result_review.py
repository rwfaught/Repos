import tempfile
import unittest

from orchestrator.approved_bounded_task_packet_to_queued_task import (
    create_queued_task_from_approved_bounded_packet,
)
from orchestrator.bounded_task_packet_review_gate import build_bounded_task_packet_review_gate_dict
from orchestrator.goal_intake_to_bounded_task_packet import (
    DOGWALKING_APP_GOAL,
    build_goal_intake_to_bounded_task_packet_dict,
)
from orchestrator.queued_task_execution_authorization_review import (
    build_queued_task_execution_authorization_review_dict,
)
from orchestrator.report_only_worker_execution_dry_run import (
    run_report_only_worker_execution_dry_run,
)
from orchestrator.report_only_worker_result_review import (
    BOUNDARY,
    EXPLICIT_NON_PROOFS,
    RECOMMENDED_NEXT_BOUNDARY,
    build_report_only_worker_result_review_dict,
    render_report_only_worker_result_review_markdown,
)


class ReportOnlyWorkerResultReviewTests(unittest.TestCase):
    def _approval(self) -> dict:
        return {
            "decision": "approve_next_boundary",
            "roger_approved": True,
            "approval_note": "Roger approves creating the queued planning task only.",
            "approved_at": "2026-07-05T00:00:00Z",
        }

    def _authorization(self) -> dict:
        return {
            "decision": "authorize_report_only_execution_boundary",
            "roger_authorized": True,
            "authorization_note": "Roger authorizes a report-only dry run only.",
            "authorized_at": "2026-07-05T00:00:00Z",
        }

    def _dry_run_result(self) -> dict:
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
        gate = build_bounded_task_packet_review_gate_dict(goal_packet)
        with tempfile.TemporaryDirectory() as task_dir:
            task_creation = create_queued_task_from_approved_bounded_packet(
                review_gate=gate,
                operator_approval=self._approval(),
                task_store_dir=task_dir,
            )
        queued_review = build_queued_task_execution_authorization_review_dict(task_creation)
        with tempfile.TemporaryDirectory() as artifact_dir:
            return run_report_only_worker_execution_dry_run(
                review_packet=queued_review,
                operator_authorization=self._authorization(),
                artifact_store_dir=artifact_dir,
            )

    def test_review_builds_as_dict_with_exact_boundary(self):
        review = build_report_only_worker_result_review_dict()

        self.assertIsInstance(review, dict)
        self.assertEqual(review["boundary"], BOUNDARY)
        self.assertEqual(review["boundary"], "REPORT_ONLY_WORKER_RESULT_REVIEW_SOURCE_TEST_DOCS")

    def test_valid_dry_result_is_accepted_as_dry_loop_artifact(self):
        review = build_report_only_worker_result_review_dict(self._dry_run_result())

        self.assertEqual(review["review_decision"], "accepted_as_dry_loop_artifact")
        self.assertEqual(review["blocked_conditions"], [])
        self.assertEqual(review["missing_requirements"], [])
        self.assertIn("dry_run_did_not_dispatch_worker", review["artifact_summary"]["verification_notes"])
        self.assertFalse(review["worker_dispatched"])
        self.assertFalse(review["real_worker_executed"])

    def test_default_missing_dry_result_requires_repair(self):
        review = build_report_only_worker_result_review_dict()

        self.assertEqual(review["review_decision"], "needs_dry_result_repair")
        self.assertIn("dry_result_artifact_missing_required_fields", review["blocked_conditions"])
        self.assertIn("artifact_id", review["missing_requirements"])

    def test_missing_required_artifact_field_requires_repair(self):
        result = self._dry_run_result()
        del result["dry_result_artifact"]["dry_output_summary"]

        review = build_report_only_worker_result_review_dict(result)

        self.assertEqual(review["review_decision"], "needs_dry_result_repair")
        self.assertIn("dry_result_artifact_missing_required_fields", review["blocked_conditions"])
        self.assertIn("dry_output_summary", review["missing_requirements"])

    def test_activity_flag_claiming_worker_dispatch_is_blocked(self):
        result = self._dry_run_result()
        result["dry_result_artifact"]["activity_flags"]["worker_dispatched"] = True

        review = build_report_only_worker_result_review_dict(result)

        self.assertEqual(review["review_decision"], "needs_dry_result_repair")
        self.assertIn("worker_dispatched_must_be_false", review["blocked_conditions"])
        self.assertFalse(review["worker_dispatched"])

    def test_unexpected_artifact_kind_is_blocked(self):
        result = self._dry_run_result()
        result["dry_result_artifact"]["artifact_kind"] = "live_worker_result"

        review = build_report_only_worker_result_review_dict(result)

        self.assertIn("unexpected_artifact_kind", review["blocked_conditions"])

    def test_missing_verification_note_requires_repair(self):
        result = self._dry_run_result()
        notes = result["dry_result_artifact"]["verification_notes"]
        result["dry_result_artifact"]["verification_notes"] = tuple(
            note for note in notes if note != "dry_run_did_not_mutate_files"
        )

        review = build_report_only_worker_result_review_dict(result)

        self.assertIn("dry_result_artifact_missing_required_fields", review["blocked_conditions"])
        self.assertIn(
            "verification_notes.dry_run_did_not_mutate_files",
            review["missing_requirements"],
        )

    def test_operator_response_options_are_visible(self):
        review = build_report_only_worker_result_review_dict(self._dry_run_result())

        for option in (
            "accept_dry_loop_artifact",
            "repair_dry_result_artifact",
            "repeat_dry_run_with_same_inputs",
            "authorize_next_local_worker_proof_boundary_later",
            "stop_or_reframe_goal",
        ):
            self.assertIn(option, review["operator_response_options"])

    def test_false_flags_remain_false(self):
        review = build_report_only_worker_result_review_dict(self._dry_run_result())

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
            self.assertIs(review[flag], False, flag)

    def test_explicit_non_proofs_are_visible(self):
        review = build_report_only_worker_result_review_dict()

        for non_proof in EXPLICIT_NON_PROOFS:
            self.assertIn(non_proof, review["explicit_non_proofs"])
        self.assertIn("no real worker execution proof", review["explicit_non_proofs"])
        self.assertIn("no file mutation execution proof", review["explicit_non_proofs"])

    def test_rendered_markdown_preserves_review_shape(self):
        rendered = render_report_only_worker_result_review_markdown(
            build_report_only_worker_result_review_dict(self._dry_run_result())
        )

        for heading in (
            "## Review Decision",
            "## Artifact Summary",
            "## Files In Scope",
            "## Success Criteria Checked",
            "## Verification Notes",
            "## Operator Response Options",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("Decision: accepted_as_dry_loop_artifact", rendered)
        self.assertIn("accept_dry_loop_artifact", rendered)
        self.assertIn("real_worker_executed=False", rendered)

    def test_recommended_next_boundary_is_dry_loop_closeout_review(self):
        review = build_report_only_worker_result_review_dict()

        self.assertEqual(review["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertEqual(
            review["recommended_next_boundary"],
            "DRY_MVP_LOOP_CLOSEOUT_REVIEW_READONLY",
        )


if __name__ == "__main__":
    unittest.main()
