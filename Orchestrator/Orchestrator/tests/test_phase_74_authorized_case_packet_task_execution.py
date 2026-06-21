import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
import orchestrator.artifact_store as artifact_store
import orchestrator.run_manager as run_manager
from orchestrator.authorized_case_packet_task_execution import (
    execute_authorized_case_packet_task,
)
from orchestrator.task_schema import Task


class Phase74AuthorizedCasePacketTaskExecutionTests(unittest.TestCase):
    def _task(self, **overrides):
        task = Task(
            id="task_phase74_valid",
            run_id="run_phase74",
            title="Case packet task: Summarize release notes",
            role="worker",
            status="queued",
            dependencies=[],
            success_criteria=["Produce a short report from release_notes.md."],
            files_in_scope=["release_notes.md"],
            retry_count=0,
            expected_output="Complete bounded task: Summarize release notes",
            source_task_id=None,
            source_artifact_id="data/case_packets/phase74_case.json",
            execution_artifact_id=None,
            review_reason="Phase 71 task created from Phase 70 authorization for case packet phase74_case.",
            recommendation_type=None,
            recommendation_reason=None,
            recommendation_identity=None,
            recommendation_confirmed=False,
            recommendation_confirmed_at=None,
            verification_checks=None,
        )
        for key, value in overrides.items():
            setattr(task, key, value)
        return task

    def _candidate(self, **overrides):
        candidate = {
            "task_id": "task_phase74_valid",
            "task_path": "data/tasks/task_phase74_valid.json",
            "run_id": "run_phase74",
            "title": "Case packet task: Summarize release notes",
            "status": "queued",
            "role": "worker",
            "files_in_scope": ["release_notes.md"],
            "success_criteria": ["Produce a short report from release_notes.md."],
            "expected_output": "Complete bounded task: Summarize release notes",
            "source_artifact_id": "data/case_packets/phase74_case.json",
            "source_case_packet_identity": "phase74_case",
            "execution_candidate_status": "case_packet_task_execution_candidate",
        }
        candidate.update(overrides)
        return candidate

    def _authorization(self, **overrides):
        authorization = {
            "case_packet_task_execution_authorization_gate": True,
            "run_id": "run_phase74",
            "task_id": "task_phase74_valid",
            "task_path": "data/tasks/task_phase74_valid.json",
            "task_execution_authorization": "task_execution_authorized",
            "task_execution_authorized": True,
            "reason": "Operator explicitly authorized later execution.",
            "detail": "Phase 73 authorization only.",
            "blocked_conditions": [],
            "missing_requirements": [],
            "selected_candidate_summary": self._candidate(),
            "source_candidate_surface_summary": {
                "case_packet_task_execution_candidate_surface": True,
                "run_id": "run_phase74",
                "candidate_count": 1,
            },
            "operator_decision": "authorize_task_execution",
            "next_action": "operator_may_choose_later_explicit_case_packet_task_execution_boundary",
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

    def _execution_input(self, **overrides):
        payload = {"phase73_task_execution_authorization_result": self._authorization()}
        payload.update(overrides)
        return payload

    def _capture_main(self, argv):
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                main.main()
            return output.getvalue()

    def test_a_valid_phase73_authorization_rejects_synthetic_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_dir = root / "tasks"
            artifact_dir = root / "artifacts"
            with patch.object(run_manager, "TASKS_DIR", task_dir), patch.object(artifact_store, "ARTIFACTS_DIR", artifact_dir):
                run_manager.save_task(self._task())
                result = execute_authorized_case_packet_task(self._execution_input())
                persisted = run_manager.load_task("task_phase74_valid")
                artifact_files = sorted(artifact_dir.glob("*.json"))

        self.assertTrue(result.get("authorized_case_packet_task_execution_boundary"))
        self.assertEqual(result.get("task_execution_status"), "queued_for_canonical_execution")
        self.assertFalse(result.get("task_executed"))
        self.assertFalse(result.get("execution_performed"))
        self.assertEqual(result.get("artifact_id"), "")
        self.assertEqual(result.get("artifact_path"), "")
        self.assertEqual(persisted.status, "queued")
        self.assertIsNone(persisted.execution_artifact_id)
        self.assertEqual(
            persisted.execution_delegation_status,
            "queued_for_canonical_execution",
        )
        self.assertEqual(artifact_files, [])
        self.assertIn("Authorization is not execution", result.get("detail", ""))
        self.assertIn("normal_engine_execution_boundary", result.get("next_action", ""))
        self.assertFalse(result.get("runtime_executed"))
        self.assertFalse(result.get("model_executed"))
        self.assertFalse(result.get("provider_executed"))
        self.assertFalse(result.get("platform_invoked"))

    def test_b_missing_phase73_authorization_is_blocked(self):
        result = execute_authorized_case_packet_task({})

        self.assertEqual(result.get("task_execution_status"), "blocked")
        self.assertIn("phase73_authorization_result_missing", result.get("blocked_conditions", []))
        self.assertFalse(result.get("task_executed"))

    def test_c_non_authorized_phase73_result_is_blocked(self):
        authorization = self._authorization(
            task_execution_authorization="needs_operator_decision",
            task_execution_authorized=False,
        )
        result = execute_authorized_case_packet_task(
            {"phase73_task_execution_authorization_result": authorization}
        )

        self.assertEqual(result.get("task_execution_status"), "blocked")
        self.assertIn("phase73_task_execution_not_authorized", result.get("blocked_conditions", []))
        self.assertIn("phase73_authorized_boolean_not_true", result.get("blocked_conditions", []))

    def test_d_phase72_candidate_without_phase73_authorization_is_blocked(self):
        phase72_surface = {
            "case_packet_task_execution_candidate_surface": True,
            "run_id": "run_phase74",
            "candidates": [self._candidate()],
        }
        result = execute_authorized_case_packet_task(phase72_surface)

        self.assertEqual(result.get("task_execution_status"), "blocked")
        self.assertIn("phase73_authorization_result_missing", result.get("blocked_conditions", []))

    def test_e_selected_task_mismatch_is_blocked(self):
        authorization = self._authorization(
            task_id="task_phase74_valid",
            selected_candidate_summary=self._candidate(task_id="task_other"),
        )
        result = execute_authorized_case_packet_task(
            {"phase73_task_execution_authorization_result": authorization}
        )

        self.assertEqual(result.get("task_execution_status"), "blocked")
        self.assertIn("authorization_task_id_mismatch", result.get("blocked_conditions", []))

    def test_f_non_queued_selected_task_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_dir = root / "tasks"
            artifact_dir = root / "artifacts"
            with patch.object(run_manager, "TASKS_DIR", task_dir), patch.object(artifact_store, "ARTIFACTS_DIR", artifact_dir):
                run_manager.save_task(self._task(status="completed"))
                result = execute_authorized_case_packet_task(self._execution_input())

        self.assertEqual(result.get("task_execution_status"), "blocked")
        self.assertIn("loaded_task_status_not_queued", result.get("blocked_conditions", []))

    def test_g_missing_bounded_file_scope_is_blocked(self):
        authorization = self._authorization(
            selected_candidate_summary=self._candidate(files_in_scope=[])
        )
        result = execute_authorized_case_packet_task(
            {"phase73_task_execution_authorization_result": authorization}
        )

        self.assertEqual(result.get("task_execution_status"), "blocked")
        self.assertIn("selected_candidate_summary.files_in_scope", result.get("missing_requirements", []))

    def test_h_missing_case_packet_traceability_is_blocked(self):
        authorization = self._authorization(
            selected_candidate_summary=self._candidate(source_artifact_id="", source_case_packet_identity="")
        )
        result = execute_authorized_case_packet_task(
            {"phase73_task_execution_authorization_result": authorization}
        )

        self.assertEqual(result.get("task_execution_status"), "blocked")
        self.assertIn("selected_candidate_summary.case_packet_traceability", result.get("missing_requirements", []))

    def test_i_scope_expansion_request_is_blocked(self):
        result = execute_authorized_case_packet_task(
            {
                "phase73_task_execution_authorization_result": self._authorization(),
                "requested_behavior": "execute all tasks in the repo",
            }
        )

        self.assertEqual(result.get("task_execution_status"), "blocked")
        self.assertIn("execution_request_expands_beyond_authorized_local_task_execution", result.get("blocked_conditions", []))

    def test_j_platform_or_runtime_request_is_blocked(self):
        result = execute_authorized_case_packet_task(
            {
                "phase73_task_execution_authorization_result": self._authorization(),
                "provider_name": "ollama",
            }
        )

        self.assertEqual(result.get("task_execution_status"), "blocked")
        self.assertIn("execution_request_expands_beyond_authorized_local_task_execution", result.get("blocked_conditions", []))

    def test_k_task_file_missing_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_dir = root / "tasks"
            artifact_dir = root / "artifacts"
            with patch.object(run_manager, "TASKS_DIR", task_dir), patch.object(artifact_store, "ARTIFACTS_DIR", artifact_dir):
                result = execute_authorized_case_packet_task(self._execution_input())

        self.assertEqual(result.get("task_execution_status"), "blocked")
        self.assertIn("selected_task_file_missing", result.get("blocked_conditions", []))

    def test_l_cli_defers_authorized_task_without_synthetic_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_dir = root / "tasks"
            artifact_dir = root / "artifacts"
            payload_path = root / "phase74_input.json"
            payload_path.write_text(json.dumps(self._execution_input()), encoding="utf-8")
            with patch.object(run_manager, "TASKS_DIR", task_dir), patch.object(artifact_store, "ARTIFACTS_DIR", artifact_dir):
                run_manager.save_task(self._task())
                output = self._capture_main(["main.py", "case-packet-task-execute-authorized", str(payload_path)])
                result = json.loads(output)
                persisted = run_manager.load_task("task_phase74_valid")
                artifact_files = sorted(artifact_dir.glob("*.json"))

        self.assertEqual(result.get("task_execution_status"), "queued_for_canonical_execution")
        self.assertFalse(result.get("task_executed"))
        self.assertFalse(result.get("execution_performed"))
        self.assertEqual(result.get("artifact_id"), "")
        self.assertEqual(result.get("artifact_path"), "")
        self.assertEqual(persisted.status, "queued")
        self.assertIsNone(persisted.execution_artifact_id)
        self.assertEqual(
            persisted.execution_delegation_status,
            "queued_for_canonical_execution",
        )
        self.assertEqual(artifact_files, [])
        self.assertFalse(result.get("runtime_executed"))
        self.assertFalse(result.get("model_executed"))
        self.assertFalse(result.get("provider_executed"))

    def test_m_existing_execution_artifact_id_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_dir = root / "tasks"
            artifact_dir = root / "artifacts"
            with patch.object(run_manager, "TASKS_DIR", task_dir), patch.object(artifact_store, "ARTIFACTS_DIR", artifact_dir):
                run_manager.save_task(self._task(execution_artifact_id="artifact_existing"))
                result = execute_authorized_case_packet_task(self._execution_input())
                persisted = run_manager.load_task("task_phase74_valid")

        self.assertEqual(result.get("task_execution_status"), "blocked")
        self.assertIn("loaded_task_already_has_execution_artifact", result.get("blocked_conditions", []))
        self.assertEqual(persisted.status, "queued")
        self.assertEqual(persisted.execution_artifact_id, "artifact_existing")


if __name__ == "__main__":
    unittest.main()
