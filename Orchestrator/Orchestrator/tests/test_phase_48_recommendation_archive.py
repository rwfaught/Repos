import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import main
from orchestrator import engine
from orchestrator.paths import ARTIFACTS_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.recommendation_store import load_recommendation_records_for_run
from orchestrator.run_manager import create_run, load_task, save_task
from orchestrator.state import STATE_PATH, load_state, save_state
from orchestrator.task_schema import create_task

RECOMMENDATIONS_DIR = Path("data/reviewer_recommendations")


class Phase48RecommendationArchiveTests(unittest.TestCase):
    def _task_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:8]}"

    def _create_reviewer_emitter_task(self, run_id: str, task_id: str, source_task_id: str, source_artifact_id: str):
        task = create_task(
            {
                "id": task_id,
                "run_id": run_id,
                "title": f"Reviewer task {task_id}",
                "role": "reviewer",
                "status": "queued",
                "dependencies": [],
                "success_criteria": ["return recommendation json"],
                "files_in_scope": [],
                "retry_count": 0,
                "source_task_id": source_task_id,
                "source_artifact_id": source_artifact_id,
            }
        )
        save_task(task)
        return task

    def _persist_recommendation(self, task_id: str, recommendation_type: str, reason: str) -> None:
        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": json.dumps(
                    {
                        "recommendation_type": recommendation_type,
                        "reason": reason,
                    }
                ),
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(task_id), provider_name="mock")

    def _count_json_files(self, directory: Path) -> int:
        if not directory.exists():
            return 0
        return len(list(directory.glob("*.json")))

    def _snapshot_counts(self) -> dict[str, int]:
        return {
            "runs": self._count_json_files(RUNS_DIR),
            "tasks": self._count_json_files(TASKS_DIR),
            "artifacts": self._count_json_files(ARTIFACTS_DIR),
            "verifier_results": self._count_json_files(VERIFIER_RESULTS_DIR),
            "recommendations": self._count_json_files(RECOMMENDATIONS_DIR),
        }

    def test_a_archive_existing_recommendation_updates_only_target_record(self):
        run = create_run("phase48 archive existing")
        reviewer_target = self._task_id("task_phase48_reviewer_target")
        reviewer_other = self._task_id("task_phase48_reviewer_other")

        self._create_reviewer_emitter_task(run["id"], reviewer_target, "source_target", "artifact_target")
        self._create_reviewer_emitter_task(run["id"], reviewer_other, "source_other", "artifact_other")
        self._persist_recommendation(reviewer_target, "manual_followup", "Target recommendation")
        self._persist_recommendation(reviewer_other, "repair_candidate", "Other recommendation")

        records_before = load_recommendation_records_for_run(run["id"])
        record_text_by_path_before = {
            record["_path"]: Path(record["_path"]).read_text(encoding="utf-8")
            for record in records_before
        }
        target_record_before = next(
            record for record in records_before if str(record.get("reviewer_task_id")) == reviewer_target
        )
        target_path = target_record_before["_path"]

        counts_before = self._snapshot_counts()
        with patch.object(
            sys,
            "argv",
            [
                "main.py",
                "recommendation-archive",
                "--reviewer-task",
                reviewer_target,
                "--run",
                run["id"],
            ],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.archive_recommendation()

        text = output.getvalue()
        self.assertIn("Recommendation record archived.", text)
        self.assertIn(f"Reviewer Task ID: {reviewer_target}", text)

        records_after = load_recommendation_records_for_run(run["id"])
        target_record_after = next(
            record for record in records_after if str(record.get("reviewer_task_id")) == reviewer_target
        )
        self.assertTrue(target_record_after.get("archived"))
        self.assertTrue(str(target_record_after.get("archived_at", "")).strip())

        record_text_by_path_after = {
            record["_path"]: Path(record["_path"]).read_text(encoding="utf-8")
            for record in records_after
        }
        changed_paths = [
            path
            for path in record_text_by_path_before
            if record_text_by_path_before[path] != record_text_by_path_after[path]
        ]
        self.assertEqual(changed_paths, [target_path])

        counts_after = self._snapshot_counts()
        self.assertEqual(counts_before["runs"], counts_after["runs"])
        self.assertEqual(counts_before["tasks"], counts_after["tasks"])
        self.assertEqual(counts_before["artifacts"], counts_after["artifacts"])
        self.assertEqual(counts_before["verifier_results"], counts_after["verifier_results"])
        self.assertEqual(counts_before["recommendations"], counts_after["recommendations"])

    def test_b_missing_recommendation_record_prints_not_found_and_no_mutation(self):
        run = create_run("phase48 missing recommendation")
        missing_reviewer_task_id = self._task_id("task_phase48_missing")

        counts_before = self._snapshot_counts()
        records_before = load_recommendation_records_for_run(run["id"])

        with patch.object(
            sys,
            "argv",
            [
                "main.py",
                "recommendation-archive",
                "--reviewer-task",
                missing_reviewer_task_id,
                "--run",
                run["id"],
            ],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.archive_recommendation()

        self.assertIn("No matching recommendation record found", output.getvalue())
        self.assertEqual(self._snapshot_counts(), counts_before)
        self.assertEqual(load_recommendation_records_for_run(run["id"]), records_before)

    def test_c_wrong_run_scope_stops_cleanly_without_mutation(self):
        run_a = create_run("phase48 run A")
        reviewer_task_id = self._task_id("task_phase48_wrong_scope")
        self._create_reviewer_emitter_task(run_a["id"], reviewer_task_id, "source_a", "artifact_a")
        self._persist_recommendation(reviewer_task_id, "manual_followup", "Only in run A")

        run_b = create_run("phase48 run B")

        counts_before = self._snapshot_counts()
        records_run_a_before = [
            Path(record["_path"]).read_text(encoding="utf-8")
            for record in load_recommendation_records_for_run(run_a["id"])
        ]

        with patch.object(
            sys,
            "argv",
            [
                "main.py",
                "recommendation-archive",
                "--reviewer-task",
                reviewer_task_id,
                "--run",
                run_b["id"],
            ],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.archive_recommendation()

        self.assertIn(
            f"reviewer_task_id={reviewer_task_id} in run={run_b['id']}",
            output.getvalue(),
        )
        self.assertEqual(self._snapshot_counts(), counts_before)

        records_run_a_after = [
            Path(record["_path"]).read_text(encoding="utf-8")
            for record in load_recommendation_records_for_run(run_a["id"])
        ]
        self.assertEqual(records_run_a_before, records_run_a_after)

    def test_d_no_hidden_behavior_change_and_no_task_or_queue_mutation(self):
        run = create_run("phase48 no hidden behavior change")
        reviewer_task_id = self._task_id("task_phase48_no_hidden")
        self._create_reviewer_emitter_task(run["id"], reviewer_task_id, "source_hidden", "artifact_hidden")
        self._persist_recommendation(reviewer_task_id, "repair_candidate", "Archive target")

        tasks_before = {
            path.name: Path(path).read_text(encoding="utf-8")
            for path in TASKS_DIR.glob("*.json")
        }
        counts_before = self._snapshot_counts()

        with patch.object(sys, "argv", ["main.py", "recommendation-archive", "--reviewer-task", reviewer_task_id]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.archive_recommendation()

        self.assertIn("Recommendation record archived.", output.getvalue())

        tasks_after = {
            path.name: Path(path).read_text(encoding="utf-8")
            for path in TASKS_DIR.glob("*.json")
        }
        counts_after = self._snapshot_counts()

        self.assertEqual(tasks_before, tasks_after)
        self.assertEqual(counts_before["runs"], counts_after["runs"])
        self.assertEqual(counts_before["tasks"], counts_after["tasks"])
        self.assertEqual(counts_before["artifacts"], counts_after["artifacts"])
        self.assertEqual(counts_before["verifier_results"], counts_after["verifier_results"])
        self.assertEqual(counts_before["recommendations"], counts_after["recommendations"])

    def test_e_archived_record_is_inspectable(self):
        run = create_run("phase48 archived inspectable")
        reviewer_task_id = self._task_id("task_phase48_inspectable")
        self._create_reviewer_emitter_task(run["id"], reviewer_task_id, "source_inspect", "artifact_inspect")
        self._persist_recommendation(reviewer_task_id, "accept_result", "Inspectable archive")

        with patch.object(
            sys,
            "argv",
            [
                "main.py",
                "recommendation-archive",
                "--reviewer-task",
                reviewer_task_id,
                "--run",
                run["id"],
            ],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.archive_recommendation()

        self.assertIn("Recommendation record archived.", output.getvalue())

        updated_records = load_recommendation_records_for_run(run["id"])
        updated = next(record for record in updated_records if str(record.get("reviewer_task_id")) == reviewer_task_id)
        self.assertEqual(updated.get("reviewer_task_id"), reviewer_task_id)
        self.assertEqual(updated.get("run_id"), run["id"])
        self.assertTrue(updated.get("archived"))
        self.assertTrue(str(updated.get("archived_at", "")).strip())

    def test_f_no_active_run_message_and_no_mutation(self):
        state = load_state()
        state["active_run_id"] = None
        save_state(state)
        state_before = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        counts_before = self._snapshot_counts()

        with patch.object(
            sys,
            "argv",
            ["main.py", "recommendation-archive", "--reviewer-task", self._task_id("task_phase48_no_active")],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.archive_recommendation()

        self.assertIn("No active run. Use --run <run_id> or create/select an active run.", output.getvalue())
        state_after = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        self.assertEqual(state_after, state_before)
        self.assertEqual(self._snapshot_counts(), counts_before)


if __name__ == "__main__":
    unittest.main()
