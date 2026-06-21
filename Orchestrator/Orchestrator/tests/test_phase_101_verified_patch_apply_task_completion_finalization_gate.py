import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.paths as project_paths
import orchestrator.run_manager as run_manager
from orchestrator.patch_apply_task_finalization import (
    finalize_verified_patch_apply_task,
    load_patch_apply_task_finalization,
)
from orchestrator.patch_apply_engine import patch_apply_result_path
from orchestrator.patch_apply_result_review import review_patch_apply_result
from orchestrator.task_schema import FILESYSTEM_MUTATION_EXECUTION_POLICY, Task


class Phase101VerifiedPatchApplyTaskFinalizationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.tasks_dir = self.root / "data" / "tasks"
        self.artifacts_dir = self.root / "data" / "artifacts"
        self.project_patch = patch.object(project_paths, "PROJECT_ROOT", self.root)
        self.tasks_patch = patch.object(run_manager, "TASKS_DIR", self.tasks_dir)
        self.artifact_patch = patch.object(
            artifact_store,
            "ARTIFACTS_DIR",
            self.artifacts_dir,
        )
        self.project_patch.start()
        self.tasks_patch.start()
        self.artifact_patch.start()
        self.addCleanup(self.project_patch.stop)
        self.addCleanup(self.tasks_patch.stop)
        self.addCleanup(self.artifact_patch.stop)
        self.addCleanup(self.temporary.cleanup)

    def _task(self, **overrides) -> Task:
        task = Task(
            id="task_phase101",
            run_id="run_phase101",
            title="Finalize verified patch apply work",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Finalize only from eligible bounded evidence."],
            files_in_scope=["src/phase101.txt"],
            retry_count=0,
            execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
            requires_causal_change=True,
        )
        for key, value in overrides.items():
            setattr(task, key, value)
        run_manager.save_task(task)
        return task

    def _apply_result(self) -> dict:
        return {
            "artifact_type": "patch_apply_result",
            "apply_id": "patch_apply_result_phase101",
            "proposal_id": "patch_proposal_phase101",
            "authorization_id": "patch_apply_authorization_phase101",
            "task_id": "task_phase101",
            "files_changed": ["src/phase101.txt"],
            "before_sha256": {"src/phase101.txt": "1" * 64},
            "after_sha256": {"src/phase101.txt": "2" * 64},
            "operations_applied": [
                {
                    "operation_id": "replace_phase101_text",
                    "file_path": "src/phase101.txt",
                }
            ],
            "causal_change_observed": True,
            "requires_verification": True,
        }

    def _review(self, **overrides) -> dict:
        apply_result = self._apply_result()
        path = patch_apply_result_path(apply_result["apply_id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(apply_result, indent=2), encoding="utf-8")
        review = review_patch_apply_result(
            apply_result["apply_id"],
            expected_task_id="task_phase101",
        )
        review.update(overrides)
        return review

    def _finalize(self, review: dict | None = None) -> dict:
        return finalize_verified_patch_apply_task(
            "task_phase101",
            review_result=self._review() if review is None else review,
        )

    def test_valid_eligible_review_finalizes_compatible_task(self):
        for status in ("queued", "in_progress"):
            with self.subTest(status=status):
                self._task(status=status)
                result = self._finalize()
                self.assertTrue(result["completed"])
                self.assertEqual(run_manager.load_task("task_phase101").status, "completed")
                self.artifacts_dir.joinpath(
                    f"{result['finalization_id']}.json"
                ).unlink()

    def test_finalization_result_records_required_evidence(self):
        self._task()
        result = self._finalize()

        self.assertEqual(result["task_id"], "task_phase101")
        self.assertEqual(result["apply_id"], "patch_apply_result_phase101")
        self.assertEqual(result["proposal_id"], "patch_proposal_phase101")
        self.assertEqual(
            result["authorization_id"],
            "patch_apply_authorization_phase101",
        )
        self.assertEqual(result["previous_task_status"], "queued")
        self.assertEqual(result["new_task_status"], "completed")
        self.assertTrue(result["completed"])
        self.assertTrue(result["evidence_summary"])
        self.assertEqual(
            load_patch_apply_task_finalization(result["finalization_id"]),
            result,
        )

    def test_missing_review_result_is_rejected(self):
        self._task()
        with self.assertRaisesRegex(ValueError, "review result is required"):
            finalize_verified_patch_apply_task(
                "task_phase101",
                review_result=None,
            )
        self.assertEqual(run_manager.load_task("task_phase101").status, "queued")

    def test_non_eligible_review_result_is_rejected(self):
        self._task()
        with self.assertRaisesRegex(ValueError, "not eligible_for_completion"):
            self._finalize(self._review(decision="rejected"))

    def test_missing_canonical_apply_evidence_is_rejected(self):
        self._task()
        review = self._review()
        patch_apply_result_path(review["apply_id"]).unlink()
        with self.assertRaisesRegex(ValueError, "lacks Phase 100 eligibility"):
            self._finalize(review)

    def test_mismatched_task_id_is_rejected(self):
        self._task()
        with self.assertRaisesRegex(ValueError, "does not match"):
            self._finalize(self._review(task_id="task_other"))

    def test_missing_task_id_is_rejected(self):
        self._task()
        with self.assertRaises(ValueError):
            self._finalize(self._review(task_id=None))

    def test_missing_apply_id_is_rejected(self):
        self._task()
        with self.assertRaises(ValueError):
            self._finalize(self._review(apply_id=None))

    def test_missing_proposal_id_is_rejected(self):
        self._task()
        with self.assertRaises(ValueError):
            self._finalize(self._review(proposal_id=None))

    def test_missing_authorization_id_is_rejected(self):
        self._task()
        with self.assertRaises(ValueError):
            self._finalize(self._review(authorization_id=None))

    def test_absolute_file_path_evidence_is_rejected(self):
        self._task()
        with self.assertRaisesRegex(ValueError, "must be relative"):
            self._finalize(self._review(files_changed=["/tmp/outside.txt"]))

    def test_parent_traversal_file_path_evidence_is_rejected(self):
        self._task()
        with self.assertRaisesRegex(ValueError, "parent traversal"):
            self._finalize(self._review(files_changed=["../outside.txt"]))

    def test_incompatible_task_status_is_rejected(self):
        self._task(status="verification_failed")
        with self.assertRaisesRegex(ValueError, "incompatible"):
            self._finalize()

    def test_review_without_causal_change_evidence_is_rejected(self):
        self._task()
        with self.assertRaisesRegex(ValueError, "causal change"):
            self._finalize(self._review(causal_change_observed=False))

    def test_review_without_requires_verification_evidence_is_rejected(self):
        self._task()
        with self.assertRaisesRegex(ValueError, "requires_verification"):
            self._finalize(self._review(requires_verification=False))

    def test_already_completed_task_is_rejected_without_duplicate_artifact(self):
        self._task(status="completed")
        with self.assertRaisesRegex(ValueError, "already completed"):
            self._finalize()
        self.assertEqual(
            list(self.artifacts_dir.glob("patch_apply_task_finalization_*.json")),
            [],
        )

    def test_finalization_does_not_apply_patches(self):
        target = self.root / "src" / "phase101.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("unchanged\n", encoding="utf-8")
        self._task()
        result = self._finalize()
        self.assertEqual(target.read_text(encoding="utf-8"), "unchanged\n")
        self.assertFalse(result["patch_applied_by_finalization"])

    def test_finalization_records_no_provider_model_or_runtime_execution(self):
        self._task()
        result = self._finalize()
        self.assertFalse(result["provider_executed"])
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["runtime_executed"])

    def test_finalization_does_not_claim_independent_semantic_correctness(self):
        self._task()
        summary = self._finalize()["evidence_summary"]
        self.assertFalse(summary["semantic_correctness_independently_proven"])
        self.assertIn("not independently proven", summary["semantic_correctness_caveat"])


if __name__ == "__main__":
    unittest.main()
