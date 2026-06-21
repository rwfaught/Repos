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


class Phase49ArchivalAwareSurfacesTests(unittest.TestCase):
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

    def _capture(self, argv: list[str], fn) -> str:
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                fn()
            return output.getvalue()

    def test_a_recommendations_direct_listing_shows_archival_state(self):
        run = create_run("phase49 direct listing archival")
        archived_task_id = self._task_id("task_phase49_archived")
        active_task_id = self._task_id("task_phase49_active")

        self._create_reviewer_emitter_task(run["id"], archived_task_id, "source_a", "artifact_a")
        self._create_reviewer_emitter_task(run["id"], active_task_id, "source_b", "artifact_b")
        self._persist_recommendation(archived_task_id, "manual_followup", "Archived recommendation")
        self._persist_recommendation(active_task_id, "repair_candidate", "Active recommendation")

        archive_text = self._capture(
            [
                "main.py",
                "recommendation-archive",
                "--reviewer-task",
                archived_task_id,
                "--run",
                run["id"],
            ],
            main.archive_recommendation,
        )
        self.assertIn("Recommendation record archived.", archive_text)

        text = self._capture(
            ["main.py", "recommendations", "--run", run["id"]],
            main.print_recommendations,
        )
        self.assertIn(f"Reviewer Task: {archived_task_id}", text)
        self.assertIn("Archival Status: archived", text)
        self.assertIn("Archived At:", text)
        self.assertIn(f"Reviewer Task: {active_task_id}", text)
        self.assertIn("Archival Status: active", text)

    def test_b_grouped_surfaces_preserve_archival_legibility_and_read_only_behavior(self):
        run = create_run("phase49 grouped archival legibility")
        archived_task_id = self._task_id("task_phase49_grouped_archived")
        active_task_id = self._task_id("task_phase49_grouped_active")

        self._create_reviewer_emitter_task(run["id"], archived_task_id, "source_grouped_a", "artifact_grouped_a")
        self._create_reviewer_emitter_task(run["id"], active_task_id, "source_grouped_b", "artifact_grouped_b")
        self._persist_recommendation(archived_task_id, "manual_followup", "Archived grouped recommendation")
        self._persist_recommendation(active_task_id, "manual_followup", "Active grouped recommendation")

        self._capture(
            [
                "main.py",
                "recommendation-archive",
                "--reviewer-task",
                archived_task_id,
                "--run",
                run["id"],
            ],
            main.archive_recommendation,
        )

        counts_before = self._snapshot_counts()
        records_before = {
            record["_path"]: Path(record["_path"]).read_text(encoding="utf-8")
            for record in load_recommendation_records_for_run(run["id"])
        }

        summary_text = self._capture(
            ["main.py", "recommendation-summary", "--run", run["id"]],
            main.print_recommendation_summary,
        )
        self.assertIn("archival_status=archived", summary_text)
        self.assertIn("archival_status=active", summary_text)

        actions_text = self._capture(
            ["main.py", "recommendation-actions", "--run", run["id"]],
            main.print_recommendation_actions,
        )
        self.assertIn("archival_status=archived", actions_text)
        self.assertIn("archival_status=active", actions_text)

        drafts_text = self._capture(
            ["main.py", "recommendation-drafts", "--run", run["id"]],
            main.print_recommendation_drafts,
        )
        self.assertIn("archival_status=archived", drafts_text)
        self.assertIn("archival_status=active", drafts_text)

        outcomes_text = self._capture(
            ["main.py", "recommendation-outcomes", "--run", run["id"]],
            main.print_recommendation_outcomes,
        )
        self.assertIn("archival_status=archived", outcomes_text)
        self.assertIn("archival_status=active", outcomes_text)

        resolution_text = self._capture(
            ["main.py", "recommendation-resolution", "--run", run["id"]],
            main.print_recommendation_resolution,
        )
        self.assertIn("archival_status=archived", resolution_text)
        self.assertIn("archival_status=active", resolution_text)

        records_after = {
            record["_path"]: Path(record["_path"]).read_text(encoding="utf-8")
            for record in load_recommendation_records_for_run(run["id"])
        }
        self.assertEqual(records_before, records_after)
        self.assertEqual(self._snapshot_counts(), counts_before)

    def test_c_no_active_run_message_for_read_surface_unchanged(self):
        state = load_state()
        state["active_run_id"] = None
        save_state(state)
        state_before = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        counts_before = self._snapshot_counts()

        text = self._capture(["main.py", "recommendation-summary"], main.print_recommendation_summary)
        self.assertIn("No active run. Use --run <run_id> or create/select an active run.", text)

        state_after = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else ""
        self.assertEqual(state_before, state_after)
        self.assertEqual(self._snapshot_counts(), counts_before)


if __name__ == "__main__":
    unittest.main()
