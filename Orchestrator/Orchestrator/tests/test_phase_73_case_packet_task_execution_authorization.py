import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
from orchestrator.case_packet_task_execution_authorization import (
    authorize_case_packet_task_execution_from_candidate_surface,
)


class Phase73CasePacketTaskExecutionAuthorizationTests(unittest.TestCase):
    def _candidate(self, **overrides):
        candidate = {
            "task_id": "task_phase73_valid",
            "task_path": "data/tasks/task_phase73_valid.json",
            "run_id": "run_phase73",
            "title": "Case packet task: Summarize release notes",
            "status": "queued",
            "role": "worker",
            "files_in_scope": ["release_notes.md"],
            "success_criteria": ["Produce a short report from release_notes.md."],
            "expected_output": "Complete bounded task: Summarize release notes",
            "source_artifact_id": "data/case_packets/phase73_case.json",
            "source_case_packet_identity": "phase73_case",
            "execution_candidate_status": "case_packet_task_execution_candidate",
        }
        candidate.update(overrides)
        return candidate

    def _surface(self, candidates=None, **overrides):
        surface = {
            "case_packet_task_execution_candidate_surface": True,
            "run_id": "run_phase73",
            "candidate_count": 1,
            "candidates": [self._candidate()] if candidates is None else candidates,
            "excluded_count": 0,
            "excluded": [],
            "reason": "Case-packet task execution candidates surfaced.",
            "detail": "Phase 72 surfaced queued Phase 71 case-packet-created tasks only.",
            "next_action": "operator_may_select_candidate_for_later_explicit_execution_boundary",
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
        surface.update(overrides)
        return surface

    def _authorization_input(self, **overrides):
        payload = {
            "phase72_task_execution_candidate_surface_result": self._surface(),
            "selected_task_id": "task_phase73_valid",
            "operator_task_execution_decision": "authorize_task_execution",
        }
        payload.update(overrides)
        return payload

    def _capture_main(self, argv):
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                main.main()
            return output.getvalue()

    def test_a_valid_phase72_candidate_plus_operator_approval_is_authorized(self):
        result = authorize_case_packet_task_execution_from_candidate_surface(self._authorization_input())

        self.assertTrue(result.get("case_packet_task_execution_authorization_gate"))
        self.assertEqual(result.get("task_execution_authorization"), "task_execution_authorized")
        self.assertTrue(result.get("task_execution_authorized"))
        self.assertEqual(result.get("task_id"), "task_phase73_valid")
        self.assertEqual(result.get("run_id"), "run_phase73")
        self.assertFalse(result.get("task_created"))
        self.assertFalse(result.get("task_mutated"))
        self.assertFalse(result.get("task_executed"))
        self.assertFalse(result.get("execution_performed"))
        self.assertEqual(
            result.get("next_action"),
            "operator_may_choose_later_explicit_case_packet_task_execution_boundary",
        )

    def test_b_valid_candidate_without_operator_approval_needs_decision(self):
        result = authorize_case_packet_task_execution_from_candidate_surface(
            self._authorization_input(operator_task_execution_decision="")
        )

        self.assertEqual(result.get("task_execution_authorization"), "needs_operator_decision")
        self.assertFalse(result.get("task_execution_authorized"))
        self.assertIn("operator_task_execution_decision", result.get("missing_requirements", []))
        self.assertFalse(result.get("task_executed"))

    def test_c_missing_phase72_surface_is_blocked(self):
        result = authorize_case_packet_task_execution_from_candidate_surface(
            {
                "selected_task_id": "task_phase73_valid",
                "operator_task_execution_decision": "authorize_task_execution",
            }
        )

        self.assertEqual(result.get("task_execution_authorization"), "blocked")
        self.assertIn("phase72_task_execution_candidate_surface_missing", result.get("blocked_conditions", []))
        self.assertFalse(result.get("execution_performed"))

    def test_d_missing_selected_task_needs_operator_decision(self):
        result = authorize_case_packet_task_execution_from_candidate_surface(
            self._authorization_input(selected_task_id="")
        )

        self.assertEqual(result.get("task_execution_authorization"), "needs_operator_decision")
        self.assertIn("selected_task_id", result.get("missing_requirements", []))

    def test_e_absent_selected_candidate_is_blocked(self):
        result = authorize_case_packet_task_execution_from_candidate_surface(
            self._authorization_input(selected_task_id="task_absent")
        )

        self.assertEqual(result.get("task_execution_authorization"), "blocked")
        self.assertIn("selected_task_absent_from_phase72_candidates", result.get("blocked_conditions", []))

    def test_f_duplicate_selected_candidate_is_blocked(self):
        duplicated = self._candidate()
        result = authorize_case_packet_task_execution_from_candidate_surface(
            self._authorization_input(
                phase72_task_execution_candidate_surface_result=self._surface(candidates=[duplicated, dict(duplicated)])
            )
        )

        self.assertEqual(result.get("task_execution_authorization"), "blocked")
        self.assertIn("selected_task_not_unique_in_phase72_candidates", result.get("blocked_conditions", []))

    def test_g_non_queued_selected_candidate_is_blocked(self):
        result = authorize_case_packet_task_execution_from_candidate_surface(
            self._authorization_input(
                phase72_task_execution_candidate_surface_result=self._surface(
                    candidates=[self._candidate(status="completed")]
                )
            )
        )

        self.assertEqual(result.get("task_execution_authorization"), "blocked")
        self.assertIn("selected_candidate_status_not_queued", result.get("blocked_conditions", []))

    def test_h_selected_candidate_without_bounded_file_scope_is_blocked(self):
        result = authorize_case_packet_task_execution_from_candidate_surface(
            self._authorization_input(
                phase72_task_execution_candidate_surface_result=self._surface(
                    candidates=[self._candidate(files_in_scope=["*"])]
                )
            )
        )

        self.assertEqual(result.get("task_execution_authorization"), "blocked")
        self.assertIn("selected_candidate_file_scope_broad_or_ambiguous", result.get("blocked_conditions", []))

    def test_i_selected_candidate_without_case_packet_traceability_is_blocked(self):
        result = authorize_case_packet_task_execution_from_candidate_surface(
            self._authorization_input(
                phase72_task_execution_candidate_surface_result=self._surface(
                    candidates=[self._candidate(source_artifact_id="", source_case_packet_identity="")]
                )
            )
        )

        self.assertEqual(result.get("task_execution_authorization"), "blocked")
        self.assertIn("selected_candidate_missing_case_packet_traceability", result.get("blocked_conditions", []))

    def test_j_surface_implying_execution_is_blocked(self):
        result = authorize_case_packet_task_execution_from_candidate_surface(
            self._authorization_input(
                phase72_task_execution_candidate_surface_result=self._surface(task_executed=True)
            )
        )

        self.assertEqual(result.get("task_execution_authorization"), "blocked")
        self.assertIn("phase72_surface_implies_task_execution", result.get("blocked_conditions", []))

    def test_k_request_bundling_authorization_with_execution_is_blocked(self):
        result = authorize_case_packet_task_execution_from_candidate_surface(
            self._authorization_input(
                operator_task_execution_decision="authorize task execution and execute the task now"
            )
        )

        self.assertEqual(result.get("task_execution_authorization"), "blocked")
        self.assertIn("unsupported_bundled_behavior_request", result.get("blocked_conditions", []))
        self.assertFalse(result.get("task_executed"))

    def test_l_ambiguous_operator_decision_needs_decision(self):
        result = authorize_case_packet_task_execution_from_candidate_surface(
            self._authorization_input(operator_task_execution_decision="looks good")
        )

        self.assertEqual(result.get("task_execution_authorization"), "needs_operator_decision")
        self.assertIn("explicit_operator_task_execution_authorization", result.get("missing_requirements", []))

    def test_m_cli_authorizes_from_json_file_without_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            payload_path = Path(directory) / "phase73_input.json"
            payload_path.write_text(json.dumps(self._authorization_input()), encoding="utf-8")
            output = self._capture_main(
                ["main.py", "case-packet-task-execution-authorize", str(payload_path)]
            )

        result = json.loads(output)
        self.assertEqual(result.get("task_execution_authorization"), "task_execution_authorized")
        self.assertFalse(result.get("task_created"))
        self.assertFalse(result.get("task_mutated"))
        self.assertFalse(result.get("task_executed"))
        self.assertFalse(result.get("execution_performed"))


if __name__ == "__main__":
    unittest.main()