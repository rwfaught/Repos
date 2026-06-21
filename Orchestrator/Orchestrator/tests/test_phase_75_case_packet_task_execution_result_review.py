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
from orchestrator.case_packet_task_execution_result_review import (
    review_case_packet_task_execution_result,
)


class Phase75CasePacketTaskExecutionResultReviewTests(unittest.TestCase):
    def _candidate(self, **overrides):
        candidate = {
            "task_id": "task_phase75_valid",
            "task_path": "data/tasks/task_phase75_valid.json",
            "run_id": "run_phase75",
            "title": "Case packet task: Summarize release notes",
            "status": "queued",
            "role": "worker",
            "files_in_scope": ["release_notes.md"],
            "success_criteria": ["Produce a short report from release_notes.md."],
            "expected_output": "Complete bounded task: Summarize release notes",
            "source_artifact_id": "data/case_packets/phase75_case.json",
            "source_case_packet_identity": "phase75_case",
            "execution_candidate_status": "case_packet_task_execution_candidate",
        }
        candidate.update(overrides)
        return candidate

    def _authorization_summary(self, **overrides):
        authorization = {
            "case_packet_task_execution_authorization_gate": True,
            "task_execution_authorization": "task_execution_authorized",
            "task_execution_authorized": True,
            "run_id": "run_phase75",
            "task_id": "task_phase75_valid",
            "task_path": "data/tasks/task_phase75_valid.json",
            "operator_decision": "authorize_task_execution",
            "next_action": "operator_may_choose_later_explicit_case_packet_task_execution_boundary",
        }
        authorization.update(overrides)
        return authorization

    def _task_summary(self, **overrides):
        task = {
            "task_id": "task_phase75_valid",
            "run_id": "run_phase75",
            "title": "Case packet task: Summarize release notes",
            "role": "worker",
            "status": "completed",
            "files_in_scope": ["release_notes.md"],
            "success_criteria": ["Produce a short report from release_notes.md."],
            "expected_output": "Complete bounded task: Summarize release notes",
            "source_artifact_id": "data/case_packets/phase75_case.json",
            "execution_artifact_id": "artifact_phase75",
        }
        task.update(overrides)
        return task

    def _execution_result(self, **overrides):
        result = {
            "authorized_case_packet_task_execution_boundary": True,
            "run_id": "run_phase75",
            "task_id": "task_phase75_valid",
            "task_path": "data/tasks/task_phase75_valid.json",
            "task_execution_status": "executed",
            "task_executed": True,
            "execution_performed": True,
            "artifact_id": "artifact_phase75",
            "artifact_path": "data/artifacts/artifact_phase75.json",
            "reason": "One Phase 73-authorized case-packet task was executed by the local Phase 74 boundary.",
            "detail": "Execution was local and deterministic; no runtime or model behavior occurred.",
            "blocked_conditions": [],
            "missing_requirements": [],
            "source_authorization_summary": self._authorization_summary(),
            "selected_candidate_summary": self._candidate(),
            "task_summary": self._task_summary(),
            "next_action": "operator_may_review_execution_artifact_and_task_status",
            "runtime_executed": False,
            "model_executed": False,
            "provider_executed": False,
            "planner_invoked": False,
            "reviewer_invoked": False,
            "verifier_invoked": False,
            "platform_invoked": False,
            "openclaw_invoked": False,
            "discord_invoked": False,
            "bridge_invoked": False,
            "adapter_invoked": False,
        }
        result.update(overrides)
        return result

    def _write_artifact(self, artifact_dir: Path, output="Reviewed local execution output."):
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "artifact_phase75.json").write_text(
            json.dumps(
                {
                    "artifact_id": "artifact_phase75",
                    "task_id": "task_phase75_valid",
                    "run_id": "run_phase75",
                    "role": "worker",
                    "created_at": "2026-06-12T00:00:00+00:00",
                    "status": "success",
                    "output": output,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def _capture_main(self, argv):
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                main.main()
            return output.getvalue()

    def test_a_valid_phase74_executed_result_with_artifact_is_ready_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact_dir = Path(directory) / "artifacts"
            self._write_artifact(artifact_dir)
            with patch.object(artifact_store, "ARTIFACTS_DIR", artifact_dir):
                result = review_case_packet_task_execution_result(self._execution_result())

        self.assertTrue(result.get("case_packet_task_execution_result_review_surface"))
        self.assertEqual(result.get("execution_result_review"), "execution_result_ready_for_operator_review")
        self.assertTrue(result.get("ready_for_operator_review"))
        self.assertFalse(result.get("task_created"))
        self.assertFalse(result.get("task_mutated"))
        self.assertFalse(result.get("task_executed"))
        self.assertFalse(result.get("execution_performed"))
        self.assertFalse(result.get("artifact_mutated"))
        self.assertFalse(result.get("runtime_executed"))
        self.assertFalse(result.get("model_executed"))
        self.assertFalse(result.get("provider_executed"))
        self.assertTrue(result.get("artifact_summary", {}).get("output_present"))

    def test_b_empty_artifact_output_needs_operator_review(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact_dir = Path(directory) / "artifacts"
            self._write_artifact(artifact_dir, output="")
            with patch.object(artifact_store, "ARTIFACTS_DIR", artifact_dir):
                result = review_case_packet_task_execution_result(self._execution_result())

        self.assertEqual(result.get("execution_result_review"), "needs_operator_review")
        self.assertFalse(result.get("ready_for_operator_review"))

    def test_c_execution_failed_result_is_classified_failed(self):
        result = review_case_packet_task_execution_result(
            self._execution_result(
                task_execution_status="execution_failed",
                task_executed=False,
                execution_performed=False,
                artifact_id="",
                artifact_path="",
                task_summary=self._task_summary(status="execution_failed"),
            )
        )

        self.assertEqual(result.get("execution_result_review"), "execution_result_failed")
        self.assertFalse(result.get("task_executed"))
        self.assertFalse(result.get("execution_performed"))

    def test_d_executed_result_missing_artifact_id_or_path_is_missing_artifact(self):
        result = review_case_packet_task_execution_result(
            self._execution_result(artifact_id="", artifact_path="")
        )

        self.assertEqual(result.get("execution_result_review"), "execution_result_missing_artifact")
        self.assertIn("artifact_id", result.get("missing_requirements", []))
        self.assertIn("artifact_path", result.get("missing_requirements", []))

    def test_e_non_phase74_input_is_blocked(self):
        result = review_case_packet_task_execution_result({"task_execution_status": "executed"})

        self.assertEqual(result.get("execution_result_review"), "blocked")
        self.assertIn("phase74_execution_result_missing", result.get("blocked_conditions", []))

    def test_f_missing_source_authorization_summary_is_blocked(self):
        result = review_case_packet_task_execution_result(
            self._execution_result(source_authorization_summary={})
        )

        self.assertEqual(result.get("execution_result_review"), "blocked")
        self.assertIn("source_authorization_summary", result.get("missing_requirements", []))

    def test_g_missing_selected_candidate_summary_is_blocked(self):
        result = review_case_packet_task_execution_result(
            self._execution_result(selected_candidate_summary={})
        )

        self.assertEqual(result.get("execution_result_review"), "blocked")
        self.assertIn("selected_candidate_summary", result.get("missing_requirements", []))

    def test_h_missing_bounded_file_scope_is_blocked(self):
        result = review_case_packet_task_execution_result(
            self._execution_result(selected_candidate_summary=self._candidate(files_in_scope=[]))
        )

        self.assertEqual(result.get("execution_result_review"), "blocked")
        self.assertIn("selected_candidate_summary.files_in_scope", result.get("missing_requirements", []))

    def test_i_missing_case_packet_traceability_is_blocked(self):
        result = review_case_packet_task_execution_result(
            self._execution_result(
                selected_candidate_summary=self._candidate(source_artifact_id="", source_case_packet_identity="")
            )
        )

        self.assertEqual(result.get("execution_result_review"), "blocked")
        self.assertIn("selected_candidate_summary.case_packet_traceability", result.get("missing_requirements", []))

    def test_j_runtime_model_provider_review_request_is_blocked(self):
        result = review_case_packet_task_execution_result(
            {
                "phase74_execution_result": self._execution_result(),
                "provider_name": "ollama",
            }
        )

        self.assertEqual(result.get("execution_result_review"), "blocked")
        self.assertIn("review_request_expands_beyond_read_only_result_review", result.get("blocked_conditions", []))

    def test_k_review_does_not_misread_negative_runtime_detail_as_expansion(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact_dir = Path(directory) / "artifacts"
            self._write_artifact(artifact_dir)
            with patch.object(artifact_store, "ARTIFACTS_DIR", artifact_dir):
                result = review_case_packet_task_execution_result(self._execution_result())

        self.assertEqual(result.get("execution_result_review"), "execution_result_ready_for_operator_review")

    def test_l_cli_reviews_phase74_result_from_json_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact_dir = root / "artifacts"
            self._write_artifact(artifact_dir)
            payload_path = root / "phase75_input.json"
            payload_path.write_text(json.dumps(self._execution_result()), encoding="utf-8")
            with patch.object(artifact_store, "ARTIFACTS_DIR", artifact_dir):
                output = self._capture_main(["main.py", "case-packet-task-execution-result-review", str(payload_path)])
                result = json.loads(output)

        self.assertEqual(result.get("execution_result_review"), "execution_result_ready_for_operator_review")
        self.assertFalse(result.get("task_mutated"))
        self.assertFalse(result.get("artifact_mutated"))


if __name__ == "__main__":
    unittest.main()