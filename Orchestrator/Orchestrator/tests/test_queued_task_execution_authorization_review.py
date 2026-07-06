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
    BOUNDARY,
    EXPLICIT_NON_PROOFS,
    RECOMMENDED_NEXT_BOUNDARY,
    build_queued_task_execution_authorization_review_dict,
    render_queued_task_execution_authorization_review_markdown,
)


class QueuedTaskExecutionAuthorizationReviewTests(unittest.TestCase):
    def _approval(self) -> dict:
        return {
            "decision": "approve_next_boundary",
            "roger_approved": True,
            "approval_note": "Roger approves creating the queued planning task only.",
            "approved_at": "2026-07-05T00:00:00Z",
        }

    def _task_creation_result(self) -> dict:
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
        review_gate = build_bounded_task_packet_review_gate_dict(goal_packet)
        with tempfile.TemporaryDirectory() as directory:
            return create_queued_task_from_approved_bounded_packet(
                review_gate=review_gate,
                operator_approval=self._approval(),
                task_store_dir=directory,
            )

    def test_review_builds_as_dict_with_exact_boundary(self):
        review = build_queued_task_execution_authorization_review_dict()

        self.assertIsInstance(review, dict)
        self.assertEqual(review["boundary"], BOUNDARY)
        self.assertEqual(
            review["boundary"],
            "QUEUED_TASK_EXECUTION_AUTHORIZATION_REVIEW_SOURCE_TEST_DOCS",
        )

    def test_ready_queued_task_is_ready_for_operator_execution_authorization_review(self):
        review = build_queued_task_execution_authorization_review_dict(
            self._task_creation_result()
        )

        self.assertEqual(
            review["review_decision"],
            "ready_for_operator_execution_authorization_review",
        )
        self.assertEqual(review["blocked_conditions"], [])
        self.assertEqual(review["missing_requirements"], [])
        self.assertEqual(review["task_summary"]["status"], "queued")
        self.assertEqual(review["task_summary"]["execution_policy"], "report_only")
        self.assertFalse(review["task_execution_authorized"])
        self.assertFalse(review["task_executed"])
        self.assertFalse(review["worker_dispatched"])

    def test_default_missing_task_creation_blocks(self):
        review = build_queued_task_execution_authorization_review_dict()

        self.assertEqual(
            review["review_decision"],
            "blocked_before_execution_authorization_review",
        )
        self.assertIn(
            "queued_task_record_missing_required_fields",
            review["blocked_conditions"],
        )
        self.assertIn("id", review["missing_requirements"])

    def test_completed_task_is_blocked(self):
        result = self._task_creation_result()
        result["queued_task_record"]["status"] = "completed"

        review = build_queued_task_execution_authorization_review_dict(result)

        self.assertEqual(
            review["review_decision"],
            "blocked_before_execution_authorization_review",
        )
        self.assertIn("task_status_not_queued", review["blocked_conditions"])

    def test_task_with_execution_artifact_is_blocked(self):
        result = self._task_creation_result()
        result["queued_task_record"]["execution_artifact_id"] = "artifact_123"

        review = build_queued_task_execution_authorization_review_dict(result)

        self.assertIn("task_already_has_execution_artifact", review["blocked_conditions"])
        self.assertFalse(review["task_execution_authorized"])

    def test_filesystem_mutation_task_is_blocked_for_this_report_only_review(self):
        result = self._task_creation_result()
        result["queued_task_record"]["execution_policy"] = "filesystem_mutation"
        result["queued_task_record"]["requires_causal_change"] = True

        review = build_queued_task_execution_authorization_review_dict(result)

        self.assertIn(
            "only_report_only_tasks_are_eligible_for_this_review",
            review["blocked_conditions"],
        )
        self.assertIn("task_requires_causal_change", review["blocked_conditions"])
        self.assertFalse(review["mutation_authorized"])

    def test_broad_file_scope_is_blocked(self):
        result = self._task_creation_result()
        result["queued_task_record"]["files_in_scope"] = ["entire repo"]

        review = build_queued_task_execution_authorization_review_dict(result)

        self.assertIn("task_file_scope_broad_or_missing", review["blocked_conditions"])

    def test_prior_execution_authorization_is_blocked(self):
        result = self._task_creation_result()
        result["queued_task_record"]["execution_authorization_provenance"][
            "execution_authorized"
        ] = True

        review = build_queued_task_execution_authorization_review_dict(result)

        self.assertIn("prior_execution_authorization_must_be_false", review["blocked_conditions"])

    def test_operator_execution_authorization_surface_has_actionable_answers(self):
        review = build_queued_task_execution_authorization_review_dict(
            self._task_creation_result()
        )
        answers = review["operator_execution_authorization_surface"]["allowed_answers"]

        for answer in (
            "authorize_report_only_execution_boundary",
            "request_task_record_repair",
            "keep_task_queued",
            "stop_or_reframe_goal",
        ):
            self.assertIn(answer, answers)

    def test_false_flags_remain_false(self):
        review = build_queued_task_execution_authorization_review_dict(
            self._task_creation_result()
        )

        for flag in (
            "runtime_required",
            "provider_model_required",
            "worker_dispatched",
            "task_execution_authorized",
            "task_executed",
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
        review = build_queued_task_execution_authorization_review_dict()

        for non_proof in EXPLICIT_NON_PROOFS:
            self.assertIn(non_proof, review["explicit_non_proofs"])
        self.assertIn("no worker execution proof", review["explicit_non_proofs"])
        self.assertIn("no file mutation execution proof", review["explicit_non_proofs"])

    def test_rendered_markdown_preserves_review_shape(self):
        review = build_queued_task_execution_authorization_review_dict(
            self._task_creation_result()
        )
        rendered = render_queued_task_execution_authorization_review_markdown(review)

        for heading in (
            "## Review Decision",
            "## Task Summary",
            "## Files In Scope",
            "## Success Criteria",
            "## Operator Execution Authorization Surface",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("Decision: ready_for_operator_execution_authorization_review", rendered)
        self.assertIn("Execution authorization required before dispatch: True", rendered)
        self.assertIn("worker_dispatched=False", rendered)
        self.assertIn("task_execution_authorized=False", rendered)

    def test_recommended_next_boundary_is_report_only_execution_dry_run(self):
        review = build_queued_task_execution_authorization_review_dict()

        self.assertEqual(review["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertEqual(
            review["recommended_next_boundary"],
            "REPORT_ONLY_WORKER_EXECUTION_DRY_RUN_BOUNDARY_SOURCE_TEST_DOCS",
        )


if __name__ == "__main__":
    unittest.main()
