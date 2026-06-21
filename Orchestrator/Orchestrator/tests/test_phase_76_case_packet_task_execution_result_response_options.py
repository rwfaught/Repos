import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import main
from orchestrator.case_packet_task_execution_result_response_options import (
    surface_case_packet_task_execution_result_response_options,
)


class Phase76CasePacketTaskExecutionResultResponseOptionsTests(unittest.TestCase):
    def _review_result(self, classification="execution_result_ready_for_operator_review", **overrides):
        result = {
            "case_packet_task_execution_result_review_surface": True,
            "run_id": "run_phase76",
            "task_id": "task_phase76_valid",
            "task_path": "data/tasks/task_phase76_valid.json",
            "artifact_id": "artifact_phase76",
            "artifact_path": "data/artifacts/artifact_phase76.json",
            "execution_result_review": classification,
            "ready_for_operator_review": classification == "execution_result_ready_for_operator_review",
            "reason": "Phase 75 review result.",
            "detail": "Read-only review result.",
            "blocked_conditions": [],
            "missing_requirements": [],
            "source_execution_summary": {
                "authorized_case_packet_task_execution_boundary": True,
                "task_execution_status": "executed",
                "task_executed": True,
                "execution_performed": True,
                "run_id": "run_phase76",
                "task_id": "task_phase76_valid",
                "task_path": "data/tasks/task_phase76_valid.json",
                "artifact_id": "artifact_phase76",
                "artifact_path": "data/artifacts/artifact_phase76.json",
            },
            "source_authorization_summary": {
                "case_packet_task_execution_authorization_gate": True,
                "task_execution_authorization": "task_execution_authorized",
                "task_execution_authorized": True,
                "run_id": "run_phase76",
                "task_id": "task_phase76_valid",
                "task_path": "data/tasks/task_phase76_valid.json",
            },
            "selected_candidate_summary": {
                "task_id": "task_phase76_valid",
                "task_path": "data/tasks/task_phase76_valid.json",
                "run_id": "run_phase76",
                "title": "Case packet task",
                "status": "queued",
                "role": "worker",
                "files_in_scope": ["release_notes.md"],
                "success_criteria": ["Produce a short report."],
                "expected_output": "Complete bounded task.",
                "source_artifact_id": "data/case_packets/phase76_case.json",
                "source_case_packet_identity": "phase76_case",
            },
            "artifact_summary": {
                "artifact_id": "artifact_phase76",
                "task_id": "task_phase76_valid",
                "output_present": True,
            },
            "task_summary": {
                "task_id": "task_phase76_valid",
                "run_id": "run_phase76",
                "status": "completed",
            },
            "next_action": "operator_may_review_artifact_and_choose_later_response_boundary",
            "task_created": False,
            "task_mutated": False,
            "task_executed": False,
            "execution_performed": False,
            "artifact_mutated": False,
            "planner_invoked": False,
            "reviewer_invoked": False,
            "verifier_invoked": False,
            "runtime_executed": False,
            "model_executed": False,
            "provider_executed": False,
            "platform_invoked": False,
            "openclaw_invoked": False,
            "discord_invoked": False,
            "bridge_invoked": False,
            "adapter_invoked": False,
        }
        result.update(overrides)
        return result

    def _capture_main(self, argv):
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                main.main()
            return output.getvalue()

    def _assert_read_only_flags(self, result):
        self.assertFalse(result.get("task_created"))
        self.assertFalse(result.get("task_mutated"))
        self.assertFalse(result.get("task_executed"))
        self.assertFalse(result.get("execution_performed"))
        self.assertFalse(result.get("artifact_created"))
        self.assertFalse(result.get("artifact_mutated"))
        self.assertFalse(result.get("followup_created"))
        self.assertFalse(result.get("planner_invoked"))
        self.assertFalse(result.get("reviewer_invoked"))
        self.assertFalse(result.get("verifier_invoked"))
        self.assertFalse(result.get("runtime_executed"))
        self.assertFalse(result.get("model_executed"))
        self.assertFalse(result.get("provider_executed"))
        self.assertFalse(result.get("platform_invoked"))

    def test_a_ready_result_surfaces_bounded_operator_response_options(self):
        result = surface_case_packet_task_execution_result_response_options(self._review_result())

        self.assertTrue(result.get("case_packet_task_execution_result_operator_response_surface"))
        self.assertEqual(result.get("operator_response_surface"), "ready_result_response_options")
        self.assertEqual(result.get("source_review_classification"), "execution_result_ready_for_operator_review")
        self.assertGreaterEqual(len(result.get("response_options", [])), 3)
        self.assertIn("operator_may_inspect_artifact_or_choose_later_response_boundary", result.get("next_action"))
        self._assert_read_only_flags(result)

    def test_b_needs_review_result_surfaces_followup_options_without_creating_anything(self):
        result = surface_case_packet_task_execution_result_response_options(
            self._review_result("needs_operator_review", ready_for_operator_review=False)
        )

        self.assertEqual(result.get("operator_response_surface"), "needs_review_response_options")
        option_ids = {option.get("option_id") for option in result.get("response_options", [])}
        self.assertIn("define_followup_review_task_creation_boundary", option_ids)
        self.assertFalse(result.get("followup_created"))
        self._assert_read_only_flags(result)

    def test_c_missing_artifact_result_surfaces_repair_or_reexecution_options_without_performing_them(self):
        result = surface_case_packet_task_execution_result_response_options(
            self._review_result(
                "execution_result_missing_artifact",
                ready_for_operator_review=False,
                artifact_id="",
                artifact_path="",
                missing_requirements=["artifact_id", "artifact_path"],
            )
        )

        self.assertEqual(result.get("operator_response_surface"), "missing_artifact_response_options")
        option_ids = {option.get("option_id") for option in result.get("response_options", [])}
        self.assertIn("define_artifact_record_repair_boundary", option_ids)
        self.assertIn("define_later_reexecution_boundary", option_ids)
        self.assertFalse(result.get("artifact_mutated"))
        self._assert_read_only_flags(result)

    def test_d_failed_result_surfaces_failure_options_without_retry(self):
        result = surface_case_packet_task_execution_result_response_options(
            self._review_result("execution_result_failed", ready_for_operator_review=False)
        )

        self.assertEqual(result.get("operator_response_surface"), "failed_result_response_options")
        option_ids = {option.get("option_id") for option in result.get("response_options", [])}
        self.assertIn("inspect_failure_detail", option_ids)
        self.assertIn("define_later_retry_boundary", option_ids)
        self.assertFalse(result.get("execution_performed"))
        self._assert_read_only_flags(result)

    def test_e_blocked_result_surfaces_blocked_condition_options_without_bypass(self):
        result = surface_case_packet_task_execution_result_response_options(
            self._review_result("blocked", ready_for_operator_review=False, blocked_conditions=["source_missing"])
        )

        self.assertEqual(result.get("operator_response_surface"), "blocked_result_response_options")
        self.assertIn("source_missing", result.get("blocked_conditions", []))
        option_ids = {option.get("option_id") for option in result.get("response_options", [])}
        self.assertIn("inspect_blocked_conditions", option_ids)
        self.assertIn("return_to_relevant_prior_boundary", option_ids)
        self._assert_read_only_flags(result)

    def test_f_non_phase75_input_is_blocked(self):
        result = surface_case_packet_task_execution_result_response_options({"execution_result_review": "needs_operator_review"})

        self.assertEqual(result.get("operator_response_surface"), "blocked")
        self.assertIn("phase75_review_result_missing", result.get("blocked_conditions", []))
        self._assert_read_only_flags(result)

    def test_g_missing_review_classification_is_blocked(self):
        result = surface_case_packet_task_execution_result_response_options(
            self._review_result(execution_result_review="")
        )

        self.assertEqual(result.get("operator_response_surface"), "blocked")
        self.assertIn("execution_result_review", result.get("missing_requirements", []))

    def test_h_missing_source_execution_summary_is_blocked(self):
        result = surface_case_packet_task_execution_result_response_options(
            self._review_result(source_execution_summary={})
        )

        self.assertEqual(result.get("operator_response_surface"), "blocked")
        self.assertIn("source_execution_summary", result.get("missing_requirements", []))

    def test_i_missing_source_authorization_summary_is_blocked(self):
        result = surface_case_packet_task_execution_result_response_options(
            self._review_result(source_authorization_summary={})
        )

        self.assertEqual(result.get("operator_response_surface"), "blocked")
        self.assertIn("source_authorization_summary", result.get("missing_requirements", []))

    def test_j_missing_selected_candidate_summary_is_blocked(self):
        result = surface_case_packet_task_execution_result_response_options(
            self._review_result(selected_candidate_summary={})
        )

        self.assertEqual(result.get("operator_response_surface"), "blocked")
        self.assertIn("selected_candidate_summary", result.get("missing_requirements", []))

    def test_k_execute_or_platform_request_is_blocked(self):
        result = surface_case_packet_task_execution_result_response_options(
            {
                "phase75_review_result": self._review_result(),
                "requested_action": "execute a follow-up task with ollama",
            }
        )

        self.assertEqual(result.get("operator_response_surface"), "blocked")
        self.assertIn("response_request_expands_beyond_read_only_option_surface", result.get("blocked_conditions", []))
        self._assert_read_only_flags(result)

    def test_l_cli_surfaces_response_options_from_json_file(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as directory:
            payload_path = Path(directory) / "phase76_input.json"
            payload_path.write_text(json.dumps(self._review_result()), encoding="utf-8")
            output = self._capture_main(["main.py", "case-packet-task-execution-result-options", str(payload_path)])
            result = json.loads(output)

        self.assertEqual(result.get("operator_response_surface"), "ready_result_response_options")
        self.assertFalse(result.get("task_mutated"))
        self.assertFalse(result.get("followup_created"))


if __name__ == "__main__":
    unittest.main()