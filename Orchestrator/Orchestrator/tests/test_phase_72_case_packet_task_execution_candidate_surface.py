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
from orchestrator.case_packet_task_execution_candidate_surface import (
    surface_case_packet_task_execution_candidates,
)
from orchestrator.task_schema import Task


class Phase72CasePacketTaskExecutionCandidateSurfaceTests(unittest.TestCase):
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

    def _phase71_task(
        self,
        task_id: str = "task_phase72_valid",
        run_id: str = "run_phase72",
        status: str = "queued",
        files_in_scope: list[str] | None = None,
        source_artifact_id: str = "data/case_packets/phase72_case.json",
        review_reason: str = "Phase 71 task created from Phase 70 authorization for case packet phase72_case.",
        execution_artifact_id: str | None = None,
    ) -> Task:
        return Task(
            id=task_id,
            run_id=run_id,
            title="Case packet task: Summarize release notes",
            role="worker",
            status=status,
            dependencies=[],
            success_criteria=["Produce a short report from release_notes.md."],
            files_in_scope=files_in_scope if files_in_scope is not None else ["release_notes.md"],
            retry_count=0,
            expected_output="Complete bounded task: Summarize release notes",
            source_task_id=None,
            source_artifact_id=source_artifact_id,
            execution_artifact_id=execution_artifact_id,
            review_reason=review_reason,
            recommendation_type=None,
            recommendation_reason=None,
            recommendation_identity=None,
            recommendation_confirmed=False,
            recommendation_confirmed_at=None,
            verification_checks=None,
        )

    def _recommendation_task(self, task_id: str = "task_recommendation") -> Task:
        return Task(
            id=task_id,
            run_id="run_phase72",
            title="Repair follow-up for source task",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Address repair_candidate recommendation for source task."],
            files_in_scope=["release_notes.md"],
            retry_count=0,
            expected_output="Provide a repair patch and concise explanation.",
            source_task_id="task_source",
            source_artifact_id="artifact_123",
            execution_artifact_id=None,
            review_reason="reason=repair",
            recommendation_type="repair_candidate",
            recommendation_reason="repair needed",
            recommendation_identity="recommendation_created",
            recommendation_confirmed=True,
            recommendation_confirmed_at="2026-06-11T00:00:00+00:00",
            verification_checks=None,
        )

    def test_a_valid_phase71_queued_task_is_surfaced_as_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                run_manager.save_task(self._phase71_task())
                result = surface_case_packet_task_execution_candidates("run_phase72")

        self.assertTrue(result.get("case_packet_task_execution_candidate_surface"))
        self.assertEqual(result.get("candidate_count"), 1)
        candidate = result.get("candidates", [])[0]
        self.assertEqual(candidate.get("task_id"), "task_phase72_valid")
        self.assertEqual(candidate.get("source_case_packet_identity"), "phase72_case")
        self.assertEqual(candidate.get("execution_candidate_status"), "case_packet_task_execution_candidate")
        self.assertFalse(result.get("task_created"))
        self.assertFalse(result.get("task_mutated"))
        self.assertFalse(result.get("task_executed"))
        self.assertFalse(result.get("execution_performed"))

    def test_b_non_queued_phase71_task_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                run_manager.save_task(self._phase71_task(status="completed"))
                result = surface_case_packet_task_execution_candidates("run_phase72")

        self.assertEqual(result.get("candidate_count"), 0)
        self.assertEqual(result.get("excluded_count"), 1)
        self.assertIn("task_status_not_queued", result.get("excluded", [])[0].get("blocked_conditions", []))

    def test_c_recommendation_created_task_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                run_manager.save_task(self._recommendation_task())
                result = surface_case_packet_task_execution_candidates("run_phase72")

        self.assertEqual(result.get("candidate_count"), 0)
        blocked = result.get("excluded", [])[0].get("blocked_conditions", [])
        self.assertIn("recommendation_created_task_excluded", blocked)
        self.assertIn("task_missing_phase71_case_packet_trace", blocked)

    def test_d_generic_queued_task_without_case_packet_trace_is_excluded(self):
        generic = self._phase71_task(
            task_id="task_generic",
            source_artifact_id="",
            review_reason="Generic queued task.",
        )
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                run_manager.save_task(generic)
                result = surface_case_packet_task_execution_candidates("run_phase72")

        self.assertEqual(result.get("candidate_count"), 0)
        blocked = result.get("excluded", [])[0].get("blocked_conditions", [])
        self.assertIn("task_missing_phase71_case_packet_trace", blocked)
        self.assertIn("task_source_artifact_not_case_packet_trace", blocked)

    def test_e_broad_file_scope_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                run_manager.save_task(self._phase71_task(files_in_scope=["*"]))
                result = surface_case_packet_task_execution_candidates("run_phase72")

        self.assertEqual(result.get("candidate_count"), 0)
        self.assertIn("task_file_scope_broad_or_ambiguous", result.get("excluded", [])[0].get("blocked_conditions", []))

    def test_f_task_with_execution_artifact_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                run_manager.save_task(self._phase71_task(execution_artifact_id="artifact_done"))
                result = surface_case_packet_task_execution_candidates("run_phase72")

        self.assertEqual(result.get("candidate_count"), 0)
        self.assertIn("task_has_execution_artifact", result.get("excluded", [])[0].get("blocked_conditions", []))

    def test_g_surface_is_read_only_and_does_not_mutate_task_files(self):
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                run_manager.save_task(self._phase71_task())
                before_files = self._task_files(task_dir)
                before_payloads = {path.name: path.read_text(encoding="utf-8") for path in before_files}
                result = surface_case_packet_task_execution_candidates("run_phase72")
                after_files = self._task_files(task_dir)
                after_payloads = {path.name: path.read_text(encoding="utf-8") for path in after_files}

        self.assertEqual(result.get("candidate_count"), 1)
        self.assertEqual([path.name for path in before_files], [path.name for path in after_files])
        self.assertEqual(before_payloads, after_payloads)

    def test_h_cli_prints_json_candidate_surface_for_run(self):
        with tempfile.TemporaryDirectory() as directory:
            task_dir = Path(directory)
            with patch.object(run_manager, "TASKS_DIR", task_dir):
                run_manager.save_task(self._phase71_task())
                output = self._capture_main(["main.py", "case-packet-task-execution-candidates", "--run", "run_phase72"])

        result = json.loads(output)
        self.assertTrue(result.get("case_packet_task_execution_candidate_surface"))
        self.assertEqual(result.get("run_id"), "run_phase72")
        self.assertEqual(result.get("candidate_count"), 1)
        self.assertFalse(result.get("runtime_executed"))
        self.assertFalse(result.get("model_executed"))
        self.assertFalse(result.get("execution_performed"))


if __name__ == "__main__":
    unittest.main()