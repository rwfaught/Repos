import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.approved_bounded_task_packet_to_queued_task import (
    create_queued_task_from_approved_bounded_packet,
)
from orchestrator.bounded_task_packet_review_gate import build_bounded_task_packet_review_gate_dict
from orchestrator.goal_intake_to_bounded_task_packet import (
    DOGWALKING_APP_GOAL,
    PKMS_REORGANIZATION_GOAL,
    build_goal_intake_to_bounded_task_packet_dict,
)
from orchestrator.queued_task_execution_authorization_review import (
    build_queued_task_execution_authorization_review_dict,
)
from orchestrator.report_only_worker_execution_dry_run import (
    BOUNDARY,
    EXPLICIT_NON_PROOFS,
    RECOMMENDED_NEXT_BOUNDARY,
    render_report_only_worker_execution_dry_run_markdown,
    run_report_only_worker_execution_dry_run,
)


class ReportOnlyWorkerExecutionDryRunTests(unittest.TestCase):
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

    def _ready_review(self) -> dict:
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
        gate = build_bounded_task_packet_review_gate_dict(goal_packet)
        with tempfile.TemporaryDirectory() as task_dir:
            task_creation = create_queued_task_from_approved_bounded_packet(
                review_gate=gate,
                operator_approval=self._approval(),
                task_store_dir=task_dir,
            )
        return build_queued_task_execution_authorization_review_dict(task_creation)

    def test_dry_run_builds_result_with_exact_boundary(self):
        result = run_report_only_worker_execution_dry_run()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["boundary"], BOUNDARY)
        self.assertEqual(
            result["boundary"],
            "REPORT_ONLY_WORKER_EXECUTION_DRY_RUN_BOUNDARY_SOURCE_TEST_DOCS",
        )

    def test_authorized_ready_review_creates_one_dry_result_artifact(self):
        with tempfile.TemporaryDirectory() as artifact_dir:
            result = run_report_only_worker_execution_dry_run(
                review_packet=self._ready_review(),
                operator_authorization=self._authorization(),
                artifact_store_dir=artifact_dir,
            )
            files = sorted(Path(artifact_dir).glob("*.json"))

            self.assertEqual(result["dry_run_status"], "created")
            self.assertTrue(result["dry_result_created"])
            self.assertTrue(result["dry_result_persisted"])
            self.assertEqual(len(files), 1)

            persisted = json.loads(files[0].read_text(encoding="utf-8"))

        self.assertEqual(persisted["artifact_id"], result["artifact_id"])
        self.assertEqual(
            persisted["artifact_kind"],
            "report_only_worker_execution_dry_run_result",
        )
        self.assertEqual(
            persisted["dry_run_classification"],
            "deterministic_report_only_no_worker_dispatched",
        )
        self.assertIn("no file mutation", persisted["files_in_scope"])
        self.assertIn("dry_run_did_not_dispatch_worker", persisted["verification_notes"])
        self.assertFalse(persisted["activity_flags"]["worker_dispatched"])
        self.assertFalse(persisted["activity_flags"]["real_worker_executed"])
        self.assertFalse(persisted["activity_flags"]["file_mutation_performed"])
        self.assertFalse(result["worker_dispatched"])
        self.assertFalse(result["real_worker_executed"])
        self.assertFalse(result["mutation_authorized"])

    def test_missing_operator_authorization_blocks_without_writing(self):
        with tempfile.TemporaryDirectory() as artifact_dir:
            result = run_report_only_worker_execution_dry_run(
                review_packet=self._ready_review(),
                operator_authorization=None,
                artifact_store_dir=artifact_dir,
            )
            files = sorted(Path(artifact_dir).glob("*.json"))

        self.assertEqual(result["dry_run_status"], "blocked")
        self.assertIn(
            "operator_execution_authorization_record_required",
            result["blocked_conditions"],
        )
        self.assertEqual(files, [])

    def test_non_authorization_decision_blocks_without_writing(self):
        authorization = self._authorization()
        authorization["decision"] = "keep_task_queued"
        with tempfile.TemporaryDirectory() as artifact_dir:
            result = run_report_only_worker_execution_dry_run(
                review_packet=self._ready_review(),
                operator_authorization=authorization,
                artifact_store_dir=artifact_dir,
            )
            files = sorted(Path(artifact_dir).glob("*.json"))

        self.assertEqual(result["dry_run_status"], "blocked")
        self.assertIn(
            "operator_decision_does_not_authorize_report_only_execution_boundary",
            result["blocked_conditions"],
        )
        self.assertEqual(files, [])

    def test_missing_artifact_store_blocks_persistence(self):
        result = run_report_only_worker_execution_dry_run(
            review_packet=self._ready_review(),
            operator_authorization=self._authorization(),
            artifact_store_dir=None,
        )

        self.assertEqual(result["dry_run_status"], "blocked")
        self.assertIn("artifact_store_dir_required", result["blocked_conditions"])
        self.assertFalse(result["dry_result_persisted"])

    def test_non_ready_review_blocks_without_writing(self):
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(PKMS_REORGANIZATION_GOAL)
        gate = build_bounded_task_packet_review_gate_dict(goal_packet)
        blocked_review = build_queued_task_execution_authorization_review_dict(gate)

        with tempfile.TemporaryDirectory() as artifact_dir:
            result = run_report_only_worker_execution_dry_run(
                review_packet=blocked_review,
                operator_authorization=self._authorization(),
                artifact_store_dir=artifact_dir,
            )
            files = sorted(Path(artifact_dir).glob("*.json"))

        self.assertEqual(result["dry_run_status"], "blocked")
        self.assertIn("queued_task_review_not_ready_for_dry_run", result["blocked_conditions"])
        self.assertEqual(files, [])

    def test_duplicate_artifact_blocks_second_write(self):
        review = self._ready_review()
        with tempfile.TemporaryDirectory() as artifact_dir:
            first = run_report_only_worker_execution_dry_run(
                review_packet=review,
                operator_authorization=self._authorization(),
                artifact_store_dir=artifact_dir,
            )
            second = run_report_only_worker_execution_dry_run(
                review_packet=review,
                operator_authorization=self._authorization(),
                artifact_store_dir=artifact_dir,
            )
            files = sorted(Path(artifact_dir).glob("*.json"))

        self.assertEqual(first["dry_run_status"], "created")
        self.assertEqual(second["dry_run_status"], "blocked")
        self.assertIn("dry_result_artifact_already_exists", second["blocked_conditions"])
        self.assertEqual(len(files), 1)

    def test_false_flags_remain_false(self):
        with tempfile.TemporaryDirectory() as artifact_dir:
            result = run_report_only_worker_execution_dry_run(
                review_packet=self._ready_review(),
                operator_authorization=self._authorization(),
                artifact_store_dir=artifact_dir,
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
        ):
            self.assertIs(result[flag], False, flag)

    def test_explicit_non_proofs_are_visible(self):
        result = run_report_only_worker_execution_dry_run()

        for non_proof in EXPLICIT_NON_PROOFS:
            self.assertIn(non_proof, result["explicit_non_proofs"])
        self.assertIn("no real worker execution proof", result["explicit_non_proofs"])
        self.assertIn("no file mutation execution proof", result["explicit_non_proofs"])

    def test_rendered_markdown_preserves_dry_run_shape(self):
        with tempfile.TemporaryDirectory() as artifact_dir:
            result = run_report_only_worker_execution_dry_run(
                review_packet=self._ready_review(),
                operator_authorization=self._authorization(),
                artifact_store_dir=artifact_dir,
            )
        rendered = render_report_only_worker_execution_dry_run_markdown(result)

        for heading in (
            "## Dry Run Status",
            "## Dry Result",
            "### Files In Scope",
            "### Success Criteria Checked",
            "### Verification Notes",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("deterministic_report_only_no_worker_dispatched", rendered)
        self.assertIn("worker_dispatched=False", rendered)
        self.assertIn("real_worker_executed=False", rendered)

    def test_recommended_next_boundary_is_worker_result_review(self):
        result = run_report_only_worker_execution_dry_run()

        self.assertEqual(result["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertEqual(
            result["recommended_next_boundary"],
            "REPORT_ONLY_WORKER_RESULT_REVIEW_SOURCE_TEST_DOCS",
        )


if __name__ == "__main__":
    unittest.main()
