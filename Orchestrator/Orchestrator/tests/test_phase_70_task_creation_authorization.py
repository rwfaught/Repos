import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
import orchestrator.case_packet_persistence as persistence
import orchestrator.case_packet_task_candidate_review as review
from orchestrator.case_packet_task_creation_authorization import (
    authorize_task_creation_from_case_packet_candidate_review,
)
from orchestrator.intake import (
    authorize_case_packet_creation_from_seed_review,
    judge_intake,
    review_case_packet_seed_candidate,
)
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase70TaskCreationAuthorizationTests(unittest.TestCase):
    def _write_temp_input(self, payload: dict) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        with handle:
            json.dump(payload, handle, indent=2)
        return Path(handle.name)

    def _capture_main(self, argv: list[str]) -> str:
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                main.main()
            return output.getvalue()

    def _count_json_files(self, directory: Path) -> int:
        if not directory.exists():
            return 0
        return len(list(directory.glob("*.json")))

    def _snapshot_repo_mutation_surface(self, case_dir: Path | None = None) -> dict[str, int | str]:
        return {
            "runs": self._count_json_files(RUNS_DIR),
            "tasks": self._count_json_files(TASKS_DIR),
            "artifacts": self._count_json_files(ARTIFACTS_DIR),
            "verifier_results": self._count_json_files(VERIFIER_RESULTS_DIR),
            "case_packets": self._count_json_files(case_dir) if case_dir is not None else 0,
            "recommendations": self._count_json_files(DATA_DIR / "reviewer_recommendations"),
            "state_text": STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else "",
        }

    def _proceed_input(self) -> dict:
        return {
            "objective_text": "Summarize the provided release notes into a short report.",
            "provided_artifacts": ["release_notes.md"],
            "confirmed_context": {
                "required_artifacts": ["release_notes.md"],
                "source_format": "markdown",
                "output_format": "summary",
            },
            "available_capabilities": ["local_files"],
        }

    def _phase67_authorization(self) -> dict:
        intake_result = judge_intake(self._proceed_input())
        seed_review = review_case_packet_seed_candidate(intake_result)
        return authorize_case_packet_creation_from_seed_review(
            {
                "seed_review_result": seed_review,
                "operator_case_packet_creation_decision": "authorize_case_packet_creation",
            }
        )

    def _phase69_ready_review(self, case_id: str, case_dir: Path) -> dict:
        persist_payload = {
            "phase67_creation_authorization_result": self._phase67_authorization(),
            "operator_case_packet_persistence_decision": "authorize_case_packet_persistence",
            "case_id": case_id,
        }
        with patch.object(persistence, "CASE_PACKETS_DIR", case_dir):
            persistence.persist_case_packet_from_creation_authorization(persist_payload)
        with patch.object(review, "CASE_PACKETS_DIR", case_dir):
            return review.review_persisted_case_packet_task_candidate({"case_id": case_id})

    def _authorization_payload(self, phase69_review: dict, decision: str | None = "authorize_task_creation") -> dict:
        payload = {"phase69_task_candidate_review_result": phase69_review}
        if decision is not None:
            payload["operator_task_creation_decision"] = decision
        return payload

    def test_a_ready_phase69_review_plus_explicit_operator_approval_is_authorized_without_task_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            phase69_review = self._phase69_ready_review("phase70_ready_case", Path(directory))
            result = authorize_task_creation_from_case_packet_candidate_review(
                self._authorization_payload(phase69_review)
            )

        self.assertEqual(result.get("task_creation_authorization"), "task_creation_authorized")
        self.assertTrue(result.get("task_creation_authorized"))
        self.assertEqual(result.get("case_id"), "phase70_ready_case")
        self.assertEqual(result.get("next_action"), "operator_may_choose_explicit_authorized_task_creation_write_gate")
        self.assertFalse(result.get("task_created"))
        self.assertFalse(result.get("planner_invoked"))
        self.assertFalse(result.get("runtime_executed"))
        self.assertFalse(result.get("model_executed"))
        self.assertFalse(result.get("platform_invoked"))
        self.assertFalse(result.get("mutation_performed"))
        self.assertFalse(result.get("execution_performed"))
        self.assertNotIn("task_id", result)

    def test_b_ready_phase69_review_without_operator_approval_needs_operator_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            phase69_review = self._phase69_ready_review("phase70_needs_decision", Path(directory))
            result = authorize_task_creation_from_case_packet_candidate_review(
                self._authorization_payload(phase69_review, decision=None)
            )

        self.assertEqual(result.get("task_creation_authorization"), "needs_operator_decision")
        self.assertFalse(result.get("task_creation_authorized"))
        self.assertIn("operator_task_creation_decision", result.get("missing_requirements", []))
        self.assertFalse(result.get("task_created"))

    def test_c_ambiguous_operator_decision_needs_operator_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            phase69_review = self._phase69_ready_review("phase70_ambiguous_decision", Path(directory))
            result = authorize_task_creation_from_case_packet_candidate_review(
                self._authorization_payload(phase69_review, decision="looks good")
            )

        self.assertEqual(result.get("task_creation_authorization"), "needs_operator_decision")
        self.assertIn("explicit_operator_task_creation_authorization", result.get("missing_requirements", []))
        self.assertFalse(result.get("task_created"))

    def test_d_non_ready_phase69_review_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            phase69_review = self._phase69_ready_review("phase70_non_ready", Path(directory))
            phase69_review["task_candidate_status"] = "needs_operator_clarification"
            result = authorize_task_creation_from_case_packet_candidate_review(
                self._authorization_payload(phase69_review)
            )

        self.assertEqual(result.get("task_creation_authorization"), "blocked")
        self.assertIn("phase69_task_candidate_not_ready", result.get("blocked_conditions", []))
        self.assertFalse(result.get("task_creation_authorized"))

    def test_e_missing_or_non_phase69_review_is_blocked(self):
        missing_result = authorize_task_creation_from_case_packet_candidate_review(
            {"operator_task_creation_decision": "authorize_task_creation"}
        )
        self.assertEqual(missing_result.get("task_creation_authorization"), "blocked")
        self.assertIn("phase69_task_candidate_review_result_missing", missing_result.get("blocked_conditions", []))

        non_review_result = authorize_task_creation_from_case_packet_candidate_review(
            {
                "phase69_task_candidate_review_result": {"task_candidate_status": "task_candidate_ready"},
                "operator_task_creation_decision": "authorize_task_creation",
            }
        )
        self.assertEqual(non_review_result.get("task_creation_authorization"), "blocked")
        self.assertIn("input_not_phase69_task_candidate_review_result", non_review_result.get("blocked_conditions", []))

    def test_f_review_implying_task_planner_runtime_or_platform_behavior_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            phase69_review = self._phase69_ready_review("phase70_forbidden_review", Path(directory))
            phase69_review["task_created"] = True
            phase69_review["planner_invoked"] = True
            phase69_review["runtime_executed"] = True
            phase69_review["model_executed"] = True
            phase69_review["platform_invoked"] = True
            result = authorize_task_creation_from_case_packet_candidate_review(
                self._authorization_payload(phase69_review)
            )

        self.assertEqual(result.get("task_creation_authorization"), "blocked")
        self.assertIn("phase69_review_implies_task_creation", result.get("blocked_conditions", []))
        self.assertIn("phase69_review_implies_planner_invocation", result.get("blocked_conditions", []))
        self.assertIn("phase69_review_implies_runtime_execution", result.get("blocked_conditions", []))
        self.assertIn("phase69_review_implies_model_execution", result.get("blocked_conditions", []))
        self.assertIn("phase69_review_implies_platform_execution", result.get("blocked_conditions", []))

    def test_g_request_bundling_authorization_with_creation_or_execution_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            phase69_review = self._phase69_ready_review("phase70_bundled_request", Path(directory))
            result = authorize_task_creation_from_case_packet_candidate_review(
                {
                    "phase69_task_candidate_review_result": phase69_review,
                    "operator_task_creation_decision": "authorize_task_creation",
                    "requested_behavior": "authorize task creation and create the task then execute it",
                }
            )

        self.assertEqual(result.get("task_creation_authorization"), "blocked")
        self.assertIn("unsupported_bundled_behavior_request", result.get("blocked_conditions", []))
        self.assertFalse(result.get("task_created"))
        self.assertFalse(result.get("execution_performed"))

    def test_h_ready_review_missing_candidate_requirements_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            phase69_review = self._phase69_ready_review("phase70_missing_candidate", Path(directory))
            phase69_review["candidate_summary"] = {
                "objective_text": "",
                "declared_or_inferred_file_surface": {"files": []},
            }
            result = authorize_task_creation_from_case_packet_candidate_review(
                self._authorization_payload(phase69_review)
            )

        self.assertEqual(result.get("task_creation_authorization"), "blocked")
        self.assertIn("phase69_ready_review_missing_authorization_requirements", result.get("blocked_conditions", []))
        self.assertIn("candidate_summary.objective_text", result.get("missing_requirements", []))
        self.assertIn("candidate_summary.declared_or_inferred_file_surface.files", result.get("missing_requirements", []))

    def test_i_cli_authorization_is_read_only_and_matches_direct_result(self):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)
            phase69_review = self._phase69_ready_review("phase70_cli_case", case_dir)
            payload = self._authorization_payload(phase69_review)
            input_path = self._write_temp_input(payload)

            before = self._snapshot_repo_mutation_surface(case_dir)
            text = self._capture_main(["main.py", "case-packet-task-creation-authorize", str(input_path)])
            after = self._snapshot_repo_mutation_surface(case_dir)
            cli_payload = json.loads(text)
            direct = authorize_task_creation_from_case_packet_candidate_review(payload)

        self.assertEqual(cli_payload, direct)
        self.assertEqual(cli_payload.get("task_creation_authorization"), "task_creation_authorized")
        self.assertEqual(before, after)
        self.assertFalse(cli_payload.get("task_created"))
        self.assertFalse(cli_payload.get("planner_invoked"))
        self.assertFalse(cli_payload.get("runtime_executed"))
        self.assertFalse(cli_payload.get("model_executed"))
        self.assertFalse(cli_payload.get("platform_invoked"))


if __name__ == "__main__":
    unittest.main()
