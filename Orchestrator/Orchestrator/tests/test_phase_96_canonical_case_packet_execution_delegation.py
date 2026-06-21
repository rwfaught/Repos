import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.run_manager as run_manager
from orchestrator.authorized_case_packet_task_execution import (
    execute_authorized_case_packet_task,
)
from orchestrator.task_schema import (
    FILESYSTEM_MUTATION_EXECUTION_POLICY,
    REPORT_ONLY_EXECUTION_POLICY,
    Task,
)


class Phase96CanonicalCasePacketExecutionDelegationTests(unittest.TestCase):
    def _task(self, **overrides) -> Task:
        task = Task(
            id="task_phase96",
            run_id="run_phase96",
            title="Delegated case-packet task",
            role="worker",
            status="queued",
            dependencies=[],
            success_criteria=["Produce the bounded result."],
            files_in_scope=["outputs/phase96.txt"],
            retry_count=0,
            expected_output="phase 96 result",
            source_artifact_id="data/case_packets/phase96_case.json",
            review_reason="Reviewer approved this bounded candidate.",
            execution_policy=REPORT_ONLY_EXECUTION_POLICY,
        )
        for key, value in overrides.items():
            setattr(task, key, value)
        return task

    def _candidate(self, **overrides) -> dict:
        candidate = {
            "task_id": "task_phase96",
            "task_path": "data/tasks/task_phase96.json",
            "run_id": "run_phase96",
            "title": "Delegated case-packet task",
            "status": "queued",
            "role": "worker",
            "files_in_scope": ["outputs/phase96.txt"],
            "success_criteria": ["Produce the bounded result."],
            "expected_output": "phase 96 result",
            "source_artifact_id": "data/case_packets/phase96_case.json",
            "source_case_packet_identity": "phase96_case",
            "execution_candidate_status": "case_packet_task_execution_candidate",
        }
        candidate.update(overrides)
        return candidate

    def _authorization(self, **overrides) -> dict:
        authorization = {
            "case_packet_task_execution_authorization_gate": True,
            "run_id": "run_phase96",
            "task_id": "task_phase96",
            "task_path": "data/tasks/task_phase96.json",
            "task_execution_authorization": "task_execution_authorized",
            "task_execution_authorized": True,
            "reason": "Operator authorized canonical delegation.",
            "detail": "Authorization permits queue delegation only.",
            "selected_candidate_summary": self._candidate(),
            "operator_decision": "authorize_task_execution",
            "reviewer_decision": "bounded_candidate_approved",
            "next_action": "delegate_to_normal_engine_queue",
            "task_created": False,
            "task_mutated": False,
            "task_executed": False,
            "planner_invoked": False,
            "runtime_executed": False,
            "model_executed": False,
            "platform_invoked": False,
            "openclaw_invoked": False,
            "discord_invoked": False,
            "bridge_invoked": False,
            "adapter_invoked": False,
            "verifier_invoked": False,
            "reviewer_invoked": False,
            "mutation_performed": False,
            "execution_performed": False,
        }
        authorization.update(overrides)
        return authorization

    def _delegate(self, task: Task, authorization: dict | None = None):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        task_dir = root / "tasks"
        artifact_dir = root / "artifacts"
        task_patch = patch.object(run_manager, "TASKS_DIR", task_dir)
        artifact_patch = patch.object(artifact_store, "ARTIFACTS_DIR", artifact_dir)
        task_patch.start()
        artifact_patch.start()
        self.addCleanup(task_patch.stop)
        self.addCleanup(artifact_patch.stop)
        self.addCleanup(temporary.cleanup)

        run_manager.save_task(task)
        result = execute_authorized_case_packet_task(
            {
                "phase73_task_execution_authorization_result": (
                    authorization or self._authorization()
                )
            }
        )
        return result, run_manager.load_task(task.id), sorted(artifact_dir.glob("*.json"))

    def test_valid_authorization_delegates_without_completion_or_artifact(self):
        result, persisted, artifacts = self._delegate(self._task())

        self.assertEqual(
            result["task_execution_status"],
            "queued_for_canonical_execution",
        )
        self.assertEqual(persisted.status, "queued")
        self.assertIsNone(persisted.execution_artifact_id)
        self.assertEqual(artifacts, [])
        self.assertFalse(result["task_executed"])
        self.assertFalse(result["execution_performed"])

    def test_delegation_preserves_case_packet_and_authorization_provenance(self):
        result, persisted, _ = self._delegate(self._task())

        self.assertEqual(persisted.source_case_packet_identity, "phase96_case")
        self.assertEqual(
            persisted.execution_authorization_provenance["operator_decision"],
            "authorize_task_execution",
        )
        self.assertEqual(
            persisted.execution_authorization_provenance["reviewer_decision"],
            "bounded_candidate_approved",
        )
        self.assertEqual(
            result["task_summary"]["source_case_packet_identity"],
            "phase96_case",
        )

    def test_report_only_delegation_preserves_normal_engine_compatibility(self):
        result, persisted, _ = self._delegate(
            self._task(execution_policy=REPORT_ONLY_EXECUTION_POLICY)
        )

        self.assertEqual(persisted.execution_policy, REPORT_ONLY_EXECUTION_POLICY)
        self.assertFalse(persisted.requires_causal_change)
        self.assertEqual(
            run_manager.get_next_task(persisted.run_id).id,
            persisted.id,
        )
        self.assertEqual(
            result["task_summary"]["execution_policy"],
            REPORT_ONLY_EXECUTION_POLICY,
        )

    def test_filesystem_mutation_delegation_preserves_causal_requirements(self):
        result, persisted, _ = self._delegate(
            self._task(
                execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
                requires_causal_change=False,
            )
        )

        self.assertEqual(
            persisted.execution_policy,
            FILESYSTEM_MUTATION_EXECUTION_POLICY,
        )
        self.assertTrue(persisted.requires_causal_change)
        self.assertEqual(persisted.files_in_scope, ["outputs/phase96.txt"])
        self.assertTrue(result["task_summary"]["requires_causal_change"])
        self.assertEqual(
            result["task_summary"]["files_in_scope"],
            ["outputs/phase96.txt"],
        )

    def test_delegation_does_not_invoke_engine_provider_or_verifier(self):
        with (
            patch("orchestrator.engine.process_task_by_id") as process_task,
            patch("orchestrator.engine.dispatch_task") as dispatch,
            patch("orchestrator.engine._verify_task_outputs") as verify,
        ):
            result, _, _ = self._delegate(self._task())

        process_task.assert_not_called()
        dispatch.assert_not_called()
        verify.assert_not_called()
        self.assertFalse(result["runtime_executed"])
        self.assertFalse(result["provider_executed"])
        self.assertFalse(result["verifier_invoked"])


if __name__ == "__main__":
    unittest.main()
