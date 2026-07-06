import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.approved_bounded_task_packet_to_queued_task import (
    BOUNDARY,
    EXPLICIT_NON_PROOFS,
    RECOMMENDED_NEXT_BOUNDARY,
    create_queued_task_from_approved_bounded_packet,
    render_approved_bounded_task_to_queued_task_markdown,
)
from orchestrator.bounded_task_packet_review_gate import build_bounded_task_packet_review_gate_dict
from orchestrator.goal_intake_to_bounded_task_packet import (
    DOGWALKING_APP_GOAL,
    PKMS_REORGANIZATION_GOAL,
    build_goal_intake_to_bounded_task_packet_dict,
)


class ApprovedBoundedTaskPacketToQueuedTaskTests(unittest.TestCase):
    def _approval(self) -> dict:
        return {
            "decision": "approve_next_boundary",
            "roger_approved": True,
            "approval_note": "Roger approves creating the queued planning task only.",
            "approved_at": "2026-07-05T00:00:00Z",
        }

    def _ready_review_gate(self) -> dict:
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
        return build_bounded_task_packet_review_gate_dict(goal_packet)

    def test_creates_one_queued_task_when_roger_approval_and_store_are_present(self):
        review_gate = self._ready_review_gate()
        with tempfile.TemporaryDirectory() as directory:
            result = create_queued_task_from_approved_bounded_packet(
                review_gate=review_gate,
                operator_approval=self._approval(),
                task_store_dir=directory,
            )
            files = sorted(Path(directory).glob("*.json"))

            self.assertEqual(result["boundary"], BOUNDARY)
            self.assertEqual(result["task_creation_status"], "created")
            self.assertTrue(result["task_created"])
            self.assertTrue(result["task_persisted"])
            self.assertEqual(len(files), 1)

            persisted = json.loads(files[0].read_text(encoding="utf-8"))

        self.assertEqual(persisted["id"], result["task_id"])
        self.assertEqual(persisted["status"], "queued")
        self.assertEqual(persisted["role"], "worker")
        self.assertEqual(persisted["execution_policy"], "report_only")
        self.assertEqual(
            persisted["execution_delegation_status"],
            "queued_waiting_for_explicit_execution_boundary",
        )
        self.assertIn("no file mutation", persisted["files_in_scope"])
        self.assertFalse(persisted["requires_causal_change"])
        self.assertIsNone(persisted["execution_artifact_id"])
        self.assertFalse(result["worker_dispatched"])
        self.assertFalse(result["task_execution_authorized"])
        self.assertFalse(result["mutation_authorized"])

    def test_missing_operator_approval_blocks_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            result = create_queued_task_from_approved_bounded_packet(
                review_gate=self._ready_review_gate(),
                operator_approval=None,
                task_store_dir=directory,
            )
            files = sorted(Path(directory).glob("*.json"))

        self.assertEqual(result["task_creation_status"], "blocked")
        self.assertFalse(result["task_created"])
        self.assertIn("operator_approval_record_required", result["blocked_conditions"])
        self.assertEqual(files, [])

    def test_non_approval_decision_blocks_without_writing(self):
        approval = self._approval()
        approval["decision"] = "request_packet_repair"

        with tempfile.TemporaryDirectory() as directory:
            result = create_queued_task_from_approved_bounded_packet(
                review_gate=self._ready_review_gate(),
                operator_approval=approval,
                task_store_dir=directory,
            )
            files = sorted(Path(directory).glob("*.json"))

        self.assertEqual(result["task_creation_status"], "blocked")
        self.assertIn("operator_decision_does_not_approve_next_boundary", result["blocked_conditions"])
        self.assertEqual(files, [])

    def test_missing_task_store_dir_blocks_persistence(self):
        result = create_queued_task_from_approved_bounded_packet(
            review_gate=self._ready_review_gate(),
            operator_approval=self._approval(),
            task_store_dir=None,
        )

        self.assertEqual(result["task_creation_status"], "blocked")
        self.assertIn("task_store_dir_required", result["blocked_conditions"])
        self.assertFalse(result["task_persisted"])

    def test_clarification_review_gate_blocks_without_writing(self):
        goal_packet = build_goal_intake_to_bounded_task_packet_dict(PKMS_REORGANIZATION_GOAL)
        review_gate = build_bounded_task_packet_review_gate_dict(goal_packet)

        with tempfile.TemporaryDirectory() as directory:
            result = create_queued_task_from_approved_bounded_packet(
                review_gate=review_gate,
                operator_approval=self._approval(),
                task_store_dir=directory,
            )
            files = sorted(Path(directory).glob("*.json"))

        self.assertEqual(result["task_creation_status"], "blocked")
        self.assertIn("review_gate_not_ready_for_task_creation", result["blocked_conditions"])
        self.assertIn("PKMS root path", result["missing_requirements"])
        self.assertEqual(files, [])

    def test_duplicate_task_record_blocks_second_write(self):
        with tempfile.TemporaryDirectory() as directory:
            first = create_queued_task_from_approved_bounded_packet(
                review_gate=self._ready_review_gate(),
                operator_approval=self._approval(),
                task_store_dir=directory,
            )
            second = create_queued_task_from_approved_bounded_packet(
                review_gate=self._ready_review_gate(),
                operator_approval=self._approval(),
                task_store_dir=directory,
            )
            files = sorted(Path(directory).glob("*.json"))

        self.assertEqual(first["task_creation_status"], "created")
        self.assertEqual(second["task_creation_status"], "blocked")
        self.assertIn("queued_task_record_already_exists", second["blocked_conditions"])
        self.assertEqual(len(files), 1)

    def test_false_flags_remain_false(self):
        with tempfile.TemporaryDirectory() as directory:
            result = create_queued_task_from_approved_bounded_packet(
                review_gate=self._ready_review_gate(),
                operator_approval=self._approval(),
                task_store_dir=directory,
            )

        for flag in (
            "runtime_required",
            "provider_model_required",
            "worker_dispatched",
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
        result = create_queued_task_from_approved_bounded_packet()

        for non_proof in EXPLICIT_NON_PROOFS:
            self.assertIn(non_proof, result["explicit_non_proofs"])
        self.assertIn("no worker execution proof", result["explicit_non_proofs"])
        self.assertIn("no file mutation execution proof", result["explicit_non_proofs"])

    def test_rendered_markdown_preserves_creation_or_blocked_shape(self):
        rendered = render_approved_bounded_task_to_queued_task_markdown()

        for heading in (
            "## Task Creation Status",
            "## Blocked Conditions",
            "## Missing Requirements",
            "## Explicit Non-Proofs",
            "## Posture",
        ):
            self.assertIn(heading, rendered)
        self.assertIn("Task created: False", rendered)
        self.assertIn("operator_approval_record_required", rendered)
        self.assertIn("worker_dispatched=False", rendered)

        missing_store = create_queued_task_from_approved_bounded_packet(
            review_gate=self._ready_review_gate(),
            operator_approval=self._approval(),
            task_store_dir=None,
        )
        rendered_missing_store = render_approved_bounded_task_to_queued_task_markdown(missing_store)
        self.assertIn("task_store_dir_required", rendered_missing_store)

    def test_recommended_next_boundary_is_execution_authorization_review(self):
        result = create_queued_task_from_approved_bounded_packet()

        self.assertEqual(result["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)
        self.assertTrue(result["recommended_next_boundary"].endswith("_REVIEW_READONLY"))


if __name__ == "__main__":
    unittest.main()
