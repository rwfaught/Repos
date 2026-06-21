import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from uuid import uuid4
from unittest.mock import patch

import main
from orchestrator import engine
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR
from orchestrator.run_manager import (
    create_run,
    create_task_from_recommendation,
    get_task_recommendation_reason,
    get_task_recommendation_type,
    is_recommendation_created_task,
    is_recommendation_emitter_reviewer_task,
    load_task,
    load_tasks_for_run,
    save_task,
)
from orchestrator.task_schema import create_task


class Phase28RecommendationLifecycleRegressionTests(unittest.TestCase):
    RECOMMENDATIONS_DIR = DATA_DIR / "reviewer_recommendations"

    def _task_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:8]}"

    def _create_task(
        self,
        run_id: str,
        task_id: str,
        role: str,
        *,
        status: str = "queued",
        files_in_scope: list[str] | None = None,
        expected_output: str | None = None,
        source_task_id: str | None = None,
        source_artifact_id: str | None = None,
        review_reason: str | None = None,
        recommendation_type: str | None = None,
        recommendation_reason: str | None = None,
        recommendation_confirmed: bool = False,
    ):
        task = create_task(
            {
                "id": task_id,
                "run_id": run_id,
                "title": f"Test task {task_id}",
                "role": role,
                "status": status,
                "dependencies": [],
                "success_criteria": ["test success"],
                "files_in_scope": files_in_scope or [],
                "retry_count": 0,
                "expected_output": expected_output,
                "source_task_id": source_task_id,
                "source_artifact_id": source_artifact_id,
                "review_reason": review_reason,
                "recommendation_type": recommendation_type,
                "recommendation_reason": recommendation_reason,
                "recommendation_confirmed": recommendation_confirmed,
            }
        )
        save_task(task)
        return task

    def _artifact_count_for_task(self, task_id: str) -> int:
        if not ARTIFACTS_DIR.exists():
            return 0

        count = 0
        for artifact_path in ARTIFACTS_DIR.glob("*.json"):
            try:
                payload = json.loads(artifact_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if str(payload.get("task_id")) == task_id:
                count += 1
        return count

    def _recommendation_file_count(self) -> int:
        if not self.RECOMMENDATIONS_DIR.exists():
            return 0
        return len(list(self.RECOMMENDATIONS_DIR.glob("*.json")))

    def test_a_new_recommendation_task_persists_normalized_provenance(self):
        run = create_run("phase28 provenance normalized")
        task = create_task_from_recommendation(
            run_id=run["id"],
            source_task_id="src_task_norm",
            source_artifact_id="src_art_norm",
            recommendation_type="repair_candidate",
            reason="repair this output",
        )

        loaded = load_task(task.id)
        self.assertEqual(loaded.recommendation_type, "repair_candidate")
        self.assertEqual(loaded.recommendation_reason, "repair this output")
        self.assertEqual(get_task_recommendation_type(loaded), "repair_candidate")
        self.assertEqual(get_task_recommendation_reason(loaded), "repair this output")
        self.assertTrue(is_recommendation_created_task(loaded))

        detected_ids = {item.id for item in main._load_recommendation_created_tasks_for_run(run["id"])}
        self.assertIn(loaded.id, detected_ids)

    def test_b_legacy_recommendation_fallback_still_works(self):
        run = create_run("phase28 provenance legacy")
        task_id = self._task_id("task_phase28_legacy")
        self._create_task(
            run_id=run["id"],
            task_id=task_id,
            role="coder",
            source_task_id="legacy_source_task",
            source_artifact_id="legacy_source_artifact",
            review_reason="recommendation_type=manual_followup; reason=legacy reason",
        )

        loaded = load_task(task_id)
        self.assertIsNone(loaded.recommendation_type)
        self.assertIsNone(loaded.recommendation_reason)
        self.assertEqual(get_task_recommendation_type(loaded), "manual_followup")
        self.assertEqual(get_task_recommendation_reason(loaded), "legacy reason")
        self.assertTrue(is_recommendation_created_task(loaded))

        detected_ids = {item.id for item in main._load_recommendation_created_tasks_for_run(run["id"])}
        self.assertIn(task_id, detected_ids)

    def test_b2_legacy_compatibility_without_structural_provenance_still_works(self):
        run = create_run("phase28 legacy compatibility only")
        task_id = self._task_id("task_phase28_legacy_compat_only")
        self._create_task(
            run_id=run["id"],
            task_id=task_id,
            role="coder",
            source_task_id="legacy_source_task_no_artifact",
            source_artifact_id=None,
            recommendation_type=None,
            recommendation_reason=None,
            review_reason="recommendation_type=manual_followup; reason=legacy compat reason",
        )

        loaded = load_task(task_id)
        self.assertIsNone(loaded.source_artifact_id)
        self.assertIsNone(loaded.recommendation_identity)
        self.assertEqual(get_task_recommendation_type(loaded), "manual_followup")
        self.assertEqual(get_task_recommendation_reason(loaded), "legacy compat reason")
        self.assertTrue(is_recommendation_created_task(loaded))

    def test_c_reviewer_semantic_split_emitter_vs_manual_followup(self):
        run = create_run("phase28 reviewer semantic split")

        emitter_task_id = self._task_id("task_phase28_emitter")
        emitter_task = self._create_task(
            run_id=run["id"],
            task_id=emitter_task_id,
            role="reviewer",
            files_in_scope=[],
            source_task_id="source_for_emitter",
            source_artifact_id="artifact_for_emitter",
            review_reason="adequacy follow-up",
        )
        self.assertTrue(is_recommendation_emitter_reviewer_task(emitter_task))

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "{not-json",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(emitter_task_id), provider_name="mock")

        emitter_updated = load_task(emitter_task_id)
        self.assertEqual(emitter_updated.status, "verification_failed")

        followup_task_id = self._task_id("task_phase28_manual_followup")
        followup_task = self._create_task(
            run_id=run["id"],
            task_id=followup_task_id,
            role="reviewer",
            files_in_scope=[],
            source_task_id="source_for_followup",
            source_artifact_id="artifact_for_followup",
            recommendation_type="manual_followup",
            recommendation_reason="manual investigation",
            review_reason="manual follow-up",
        )
        self.assertFalse(is_recommendation_emitter_reviewer_task(followup_task))
        recommendation_records_before = self._recommendation_file_count()
        task_count_before = len(load_tasks_for_run(run["id"]))

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "{not-json",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(followup_task_id), provider_name="mock")

        followup_updated = load_task(followup_task_id)
        self.assertEqual(followup_updated.status, "needs_review")
        self.assertEqual(self._recommendation_file_count(), recommendation_records_before)
        self.assertEqual(len(load_tasks_for_run(run["id"])), task_count_before)

    def test_d_confirmation_readiness_and_candidate_detection(self):
        run = create_run("phase28 confirmation readiness candidate")

        to_confirm_id = self._task_id("task_phase28_to_confirm")
        self._create_task(
            run_id=run["id"],
            task_id=to_confirm_id,
            role="coder",
            status="queued",
            source_task_id="s1",
            source_artifact_id="a1",
            recommendation_type="repair_candidate",
            recommendation_reason="candidate repair",
            recommendation_confirmed=False,
        )

        with patch.object(sys, "argv", ["main.py", "recommendation-confirm", "--task", to_confirm_id]):
            with redirect_stdout(io.StringIO()):
                main.confirm_recommendation_task()

        confirmed = load_task(to_confirm_id)
        self.assertTrue(confirmed.recommendation_confirmed)
        self.assertIsNotNone(confirmed.recommendation_confirmed_at)

        nonqueued_confirmed_id = self._task_id("task_phase28_nonqueued")
        self._create_task(
            run_id=run["id"],
            task_id=nonqueued_confirmed_id,
            role="coder",
            status="completed",
            source_task_id="s2",
            source_artifact_id="a2",
            recommendation_type="manual_followup",
            recommendation_reason="already done",
            recommendation_confirmed=True,
        )

        ordinary_task_id = self._task_id("task_phase28_ordinary")
        ordinary = self._create_task(
            run_id=run["id"],
            task_id=ordinary_task_id,
            role="coder",
            status="queued",
            recommendation_confirmed=True,
        )

        self.assertFalse(is_recommendation_created_task(ordinary))

        ready_ids = {task.id for task in main._load_ready_recommendation_tasks_for_run(run["id"])}
        self.assertIn(to_confirm_id, ready_ids)
        self.assertIn(nonqueued_confirmed_id, ready_ids)

        candidate_ids = {task.id for task in main._load_ready_execution_candidates_for_run(run["id"])}
        self.assertIn(to_confirm_id, candidate_ids)
        self.assertNotIn(nonqueued_confirmed_id, candidate_ids)
        self.assertNotIn(ordinary_task_id, candidate_ids)

    def test_e_explicit_ready_candidate_execution_and_rejections(self):
        run = create_run("phase28 explicit candidate execution")

        valid_candidate_id = self._task_id("task_phase28_valid_candidate")
        self._create_task(
            run_id=run["id"],
            task_id=valid_candidate_id,
            role="coder",
            status="queued",
            files_in_scope=[],
            source_task_id="source_exec",
            source_artifact_id="artifact_exec",
            recommendation_type="repair_candidate",
            recommendation_reason="execute this",
            recommendation_confirmed=True,
        )

        before_artifacts = self._artifact_count_for_task(valid_candidate_id)

        original_dispatch = engine.dispatch_task
        captured_provider: dict[str, str] = {}

        def recording_dispatch(task, provider_name="mock", context=None):
            captured_provider["provider_name"] = provider_name
            return original_dispatch(task, provider_name=provider_name, context=context)

        with patch("orchestrator.engine.dispatch_task", side_effect=recording_dispatch):
            with patch.object(
                sys,
                "argv",
                ["main.py", "execute-ready-candidate", "--task", valid_candidate_id, "--provider", "mock"],
            ):
                with redirect_stdout(io.StringIO()):
                    main.execute_ready_candidate()

        self.assertEqual(captured_provider.get("provider_name"), "mock")
        after_artifacts = self._artifact_count_for_task(valid_candidate_id)
        self.assertEqual(after_artifacts, before_artifacts + 1)

        executed = load_task(valid_candidate_id)
        self.assertEqual(executed.status, "completed")

        nonready_id = self._task_id("task_phase28_nonready")
        self._create_task(
            run_id=run["id"],
            task_id=nonready_id,
            role="coder",
            status="queued",
            source_task_id="source_nonready",
            source_artifact_id="artifact_nonready",
            recommendation_type="repair_candidate",
            recommendation_reason="not confirmed",
            recommendation_confirmed=False,
        )

        with patch.object(
            sys,
            "argv",
            ["main.py", "execute-ready-candidate", "--task", nonready_id, "--provider", "mock"],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.execute_ready_candidate()
        self.assertIn("Task is not ready", output.getvalue())
        self.assertEqual(load_task(nonready_id).status, "queued")

        ordinary_id = self._task_id("task_phase28_ordinary_queued")
        self._create_task(
            run_id=run["id"],
            task_id=ordinary_id,
            role="coder",
            status="queued",
            recommendation_confirmed=True,
        )

        with patch.object(
            sys,
            "argv",
            ["main.py", "execute-ready-candidate", "--task", ordinary_id, "--provider", "mock"],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                main.execute_ready_candidate()
        self.assertIn("Task is not recommendation-created", output.getvalue())
        self.assertEqual(load_task(ordinary_id).status, "queued")

        next_task_id = self._task_id("task_phase28_next_behavior")
        self._create_task(
            run_id=run["id"],
            task_id=next_task_id,
            role="coder",
            status="queued",
            files_in_scope=[],
        )

        engine.process_next_task(provider_name="mock")
        self.assertEqual(load_task(next_task_id).status, "completed")


if __name__ == "__main__":
    unittest.main()
