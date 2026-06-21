import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
import orchestrator.run_manager as run_manager
from orchestrator.case_packet_task_creation_write_gate import (
    create_task_from_authorized_case_packet_task_creation,
)


class Phase71TaskCreationWriteGateTests(unittest.TestCase):
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

    def _task_files(self, task_dir: Path) -> list[Path]:
        if not task_dir.exists():
            return []
        return sorted(task_dir.glob("*.json"))

    def _phase70_authorized_result(self, case_id: str = "phase71_ready_case") -> dict:
        return {
            "case_packet_task_creation_authorization": True,
            "case_id": case_id,
            "case_packet_path": f"data/case_packets/{case_id}.json",
            "task_creation_authorization": "task_creation_authorized",
            "task_creation_authorized": True,
            "operator_decision": "authorize_task_creation",
            "candidate_summary": {
                "objective_text": "Summarize the provided release notes into a short report.",
                "likely_bounded_task_description": "Summarize the provided release notes into a short report.",
                "declared_or_inferred_file_surface": {
                    "source": "case_packet.source_materials",
                    "inference": "declared_by_persisted_case_packet",
                    "files": ["release_notes.md"],
                },
                "success_criteria": "Produce a short report from release_notes.md.",
            },
            "source_case_packet_summary": {
                "case_id": case_id,
                "title": "Release notes summary",
                "objective": "Summarize the provided release notes into a short report.",
                "status": "created",
                "next_step": "operator_review_case_packet_before_task_creation",
            },
            "task_created": False,
            "planner_invoked": False,
            "runtime_executed": False,
            "model_executed": False,
            "platform_invoked": False,
            "openclaw_invoked": False,
            "discord_invoked": False,
            "bridge_invoked": False,
            "adapter_invoked": False,
            "mutation_performed": False,
            "execution_performed": False,
        }

    def test_a_valid_phase70_authorization_creates_exactly_one_queued_task(self):
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                result = create_task_from_authorized_case_packet_task_creation(
                    self._phase70_authorized_result()
                )
                task_files = self._task_files(task_dir)

                self.assertEqual(result.get("task_creation_write"), "created")
                self.assertTrue(result.get("task_created"))
                self.assertEqual(len(task_files), 1)

                task_payload = json.loads(task_files[0].read_text(encoding="utf-8"))

        self.assertEqual(task_payload.get("id"), result.get("task_id"))
        self.assertEqual(task_payload.get("status"), "queued")
        self.assertEqual(task_payload.get("role"), "worker")
        self.assertEqual(task_payload.get("files_in_scope"), ["release_notes.md"])
        self.assertEqual(task_payload.get("source_artifact_id"), "data/case_packets/phase71_ready_case.json")
        self.assertFalse(result.get("planner_invoked"))
        self.assertFalse(result.get("runtime_executed"))
        self.assertFalse(result.get("model_executed"))
        self.assertFalse(result.get("platform_invoked"))
        self.assertFalse(result.get("execution_performed"))

    def test_b_wrapper_input_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            payload = {
                "phase70_task_creation_authorization_result": self._phase70_authorized_result(
                    "phase71_wrapper_case"
                )
            }
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                result = create_task_from_authorized_case_packet_task_creation(payload)

        self.assertEqual(result.get("task_creation_write"), "created")
        self.assertEqual(result.get("case_id"), "phase71_wrapper_case")
        self.assertTrue(result.get("task_created"))

    def test_c_missing_phase70_result_is_blocked_and_creates_no_task(self):
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                result = create_task_from_authorized_case_packet_task_creation(
                    {"operator_decision": "authorize_task_creation"}
                )
                task_files = self._task_files(task_dir)

        self.assertEqual(result.get("task_creation_write"), "blocked")
        self.assertIn("phase70_task_creation_authorization_result_missing", result.get("blocked_conditions", []))
        self.assertFalse(result.get("task_created"))
        self.assertEqual(task_files, [])

    def test_d_not_authorized_result_is_blocked_and_creates_no_task(self):
        payload = self._phase70_authorized_result("phase71_not_authorized")
        payload["task_creation_authorization"] = "needs_operator_decision"
        payload["task_creation_authorized"] = False

        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                result = create_task_from_authorized_case_packet_task_creation(payload)
                task_files = self._task_files(task_dir)

        self.assertEqual(result.get("task_creation_write"), "blocked")
        self.assertIn("phase70_task_creation_not_authorized", result.get("blocked_conditions", []))
        self.assertFalse(result.get("task_created"))
        self.assertEqual(task_files, [])

    def test_e_prior_or_bundled_execution_flags_are_blocked(self):
        payload = self._phase70_authorized_result("phase71_forbidden")
        payload["planner_invoked"] = True
        payload["runtime_executed"] = True
        payload["requested_behavior"] = "create the task then execute it"

        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                result = create_task_from_authorized_case_packet_task_creation(payload)
                task_files = self._task_files(task_dir)

        self.assertEqual(result.get("task_creation_write"), "blocked")
        self.assertIn("phase70_input_implies_planner_invocation", result.get("blocked_conditions", []))
        self.assertIn("phase70_input_implies_runtime_execution", result.get("blocked_conditions", []))
        self.assertIn("phase70_input_contains_forbidden_bundled_behavior", result.get("blocked_conditions", []))
        self.assertFalse(result.get("task_created"))
        self.assertEqual(task_files, [])

    def test_f_missing_candidate_requirements_are_blocked(self):
        payload = self._phase70_authorized_result("phase71_missing_candidate")
        payload["candidate_summary"] = {
            "objective_text": "",
            "declared_or_inferred_file_surface": {"files": []},
        }

        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                result = create_task_from_authorized_case_packet_task_creation(payload)
                task_files = self._task_files(task_dir)

        self.assertEqual(result.get("task_creation_write"), "blocked")
        self.assertIn("phase70_authorization_missing_task_write_requirements", result.get("blocked_conditions", []))
        self.assertIn("candidate_summary.objective_text", result.get("missing_requirements", []))
        self.assertIn("candidate_summary.declared_or_inferred_file_surface.files", result.get("missing_requirements", []))
        self.assertFalse(result.get("task_created"))
        self.assertEqual(task_files, [])

    def test_g_broad_file_surface_is_blocked(self):
        payload = self._phase70_authorized_result("phase71_broad_surface")
        payload["candidate_summary"]["declared_or_inferred_file_surface"]["files"] = ["entire repo"]

        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                result = create_task_from_authorized_case_packet_task_creation(payload)
                task_files = self._task_files(task_dir)

        self.assertEqual(result.get("task_creation_write"), "blocked")
        self.assertIn("candidate_summary.bounded_file_surface", result.get("missing_requirements", []))
        self.assertFalse(result.get("task_created"))
        self.assertEqual(task_files, [])

    def test_h_cli_creates_one_task_and_returns_json(self):
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            payload = self._phase70_authorized_result("phase71_cli_case")
            input_path = self._write_temp_input(payload)

            with patch.object(run_manager, "TASKS_DIR", task_dir):
                text = self._capture_main(["main.py", "case-packet-task-create-authorized", str(input_path)])
                result = json.loads(text)
                task_files = self._task_files(task_dir)

        self.assertEqual(result.get("task_creation_write"), "created")
        self.assertEqual(result.get("case_id"), "phase71_cli_case")
        self.assertEqual(len(task_files), 1)
        self.assertFalse(result.get("execution_performed"))
        self.assertFalse(result.get("planner_invoked"))


if __name__ == "__main__":
    unittest.main()
