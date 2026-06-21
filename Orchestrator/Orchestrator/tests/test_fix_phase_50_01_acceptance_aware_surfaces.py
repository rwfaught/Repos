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
from orchestrator.task_schema import create_task

RECOMMENDATIONS_DIR = Path("data/reviewer_recommendations")


class FixPhase5001AcceptanceAwareSurfacesTests(unittest.TestCase):
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

    def _capture(self, argv: list[str], fn) -> str:
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                fn()
            return output.getvalue()

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

    def test_a_recommendations_listing_shows_acceptance_state(self):
        run = create_run("fix phase 50 01 direct acceptance")
        accepted_task_id = self._task_id("task_fix50_01_accepted")
        non_accepted_task_id = self._task_id("task_fix50_01_non_accepted")

        self._create_reviewer_emitter_task(run["id"], accepted_task_id, "source_a", "artifact_a")
        self._create_reviewer_emitter_task(run["id"], non_accepted_task_id, "source_b", "artifact_b")
        self._persist_recommendation(accepted_task_id, "accept_result", "Accepted recommendation")
        self._persist_recommendation(non_accepted_task_id, "accept_result", "Pending recommendation")

        accept_text = self._capture(
            [
                "main.py",
                "recommendation-accept",
                "--reviewer-task",
                accepted_task_id,
                "--run",
                run["id"],
            ],
            main.accept_recommendation,
        )
        self.assertIn("Recommendation record accepted.", accept_text)

        listing_text = self._capture(
            ["main.py", "recommendations", "--run", run["id"]],
            main.print_recommendations,
        )
        self.assertIn(f"Reviewer Task: {accepted_task_id}", listing_text)
        self.assertIn("Acceptance Status: accepted", listing_text)
        self.assertIn("Accepted At:", listing_text)
        self.assertIn(f"Reviewer Task: {non_accepted_task_id}", listing_text)
        self.assertIn("Acceptance Status: not_accepted", listing_text)

    def test_b_grouped_surfaces_show_acceptance_and_acceptance_plus_archival(self):
        run = create_run("fix phase 50 01 grouped acceptance")
        accepted_and_archived_task_id = self._task_id("task_fix50_01_accepted_archived")
        active_non_accepted_task_id = self._task_id("task_fix50_01_active_non_accepted")

        self._create_reviewer_emitter_task(
            run["id"], accepted_and_archived_task_id, "source_c", "artifact_c"
        )
        self._create_reviewer_emitter_task(run["id"], active_non_accepted_task_id, "source_d", "artifact_d")
        self._persist_recommendation(
            accepted_and_archived_task_id,
            "accept_result",
            "Accepted and archived recommendation",
        )
        self._persist_recommendation(active_non_accepted_task_id, "accept_result", "Still active recommendation")

        self._capture(
            [
                "main.py",
                "recommendation-accept",
                "--reviewer-task",
                accepted_and_archived_task_id,
                "--run",
                run["id"],
            ],
            main.accept_recommendation,
        )
        self._capture(
            [
                "main.py",
                "recommendation-archive",
                "--reviewer-task",
                accepted_and_archived_task_id,
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
        self.assertIn("acceptance_status=accepted", summary_text)
        self.assertIn("acceptance_status=not_accepted", summary_text)
        self.assertIn("archival_status=archived", summary_text)

        actions_text = self._capture(
            ["main.py", "recommendation-actions", "--run", run["id"]],
            main.print_recommendation_actions,
        )
        self.assertIn("acceptance_status=accepted", actions_text)
        self.assertIn("acceptance_status=not_accepted", actions_text)
        self.assertIn("archival_status=archived", actions_text)

        drafts_text = self._capture(
            ["main.py", "recommendation-drafts", "--run", run["id"]],
            main.print_recommendation_drafts,
        )
        self.assertIn("acceptance_status=accepted", drafts_text)
        self.assertIn("acceptance_status=not_accepted", drafts_text)
        self.assertIn("archival_status=archived", drafts_text)

        outcomes_text = self._capture(
            ["main.py", "recommendation-outcomes", "--run", run["id"]],
            main.print_recommendation_outcomes,
        )
        self.assertIn("acceptance_status=accepted", outcomes_text)
        self.assertIn("acceptance_status=not_accepted", outcomes_text)
        self.assertIn("archival_status=archived", outcomes_text)

        resolution_text = self._capture(
            ["main.py", "recommendation-resolution", "--run", run["id"]],
            main.print_recommendation_resolution,
        )
        self.assertIn("acceptance_status=accepted", resolution_text)
        self.assertIn("acceptance_status=not_accepted", resolution_text)
        self.assertIn("archival_status=archived", resolution_text)

        records_after = {
            record["_path"]: Path(record["_path"]).read_text(encoding="utf-8")
            for record in load_recommendation_records_for_run(run["id"])
        }
        self.assertEqual(records_before, records_after)
        self.assertEqual(counts_before, self._snapshot_counts())


if __name__ == "__main__":
    unittest.main()
