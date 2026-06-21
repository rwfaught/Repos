import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.paths as project_paths
from orchestrator.patch_apply_engine import patch_apply_result_path
from orchestrator.patch_apply_result_review import (
    ELIGIBLE_FOR_COMPLETION,
    INSUFFICIENT_EVIDENCE,
    REJECTED,
    review_patch_apply_result,
)
from orchestrator.task_schema import FILESYSTEM_MUTATION_EXECUTION_POLICY, Task


class Phase100PatchApplyResultVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.artifacts_dir = self.root / "data" / "artifacts"
        self.project_patch = patch.object(project_paths, "PROJECT_ROOT", self.root)
        self.artifact_patch = patch.object(
            artifact_store,
            "ARTIFACTS_DIR",
            self.artifacts_dir,
        )
        self.project_patch.start()
        self.artifact_patch.start()
        self.addCleanup(self.project_patch.stop)
        self.addCleanup(self.artifact_patch.stop)
        self.addCleanup(self.temporary.cleanup)

    def _task(self) -> Task:
        return Task(
            id="task_phase100",
            run_id="run_phase100",
            title="Review bounded patch apply evidence",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Review evidence without completing the task."],
            files_in_scope=["src/phase100.txt"],
            retry_count=0,
            execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
            requires_causal_change=True,
        )

    def _result(self, **overrides) -> dict:
        result = {
            "artifact_type": "patch_apply_result",
            "apply_id": "patch_apply_result_phase100",
            "proposal_id": "patch_proposal_phase100",
            "authorization_id": "patch_apply_authorization_phase100",
            "task_id": "task_phase100",
            "files_changed": ["src/phase100.txt"],
            "before_sha256": {"src/phase100.txt": "1" * 64},
            "after_sha256": {"src/phase100.txt": "2" * 64},
            "operations_applied": [
                {
                    "operation_id": "replace_phase100_text",
                    "file_path": "src/phase100.txt",
                }
            ],
            "requires_verification": True,
            "causal_change_observed": True,
        }
        result.update(overrides)
        return result

    def _store(self, result: dict) -> None:
        path = patch_apply_result_path(result["apply_id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    def _review(self, result: dict | None = None) -> dict:
        if result is not None:
            self._store(result)
        return review_patch_apply_result(
            "patch_apply_result_phase100",
            expected_task_id="task_phase100",
        )

    def test_valid_apply_result_is_eligible_for_completion(self):
        review = self._review(self._result())
        self.assertEqual(review["decision"], ELIGIBLE_FOR_COMPLETION)
        self.assertTrue(review["eligible_for_completion"])
        self.assertEqual(review["reasons"], [])

    def test_valid_review_preserves_linkage_identities(self):
        review = self._review(self._result())
        self.assertEqual(review["task_id"], "task_phase100")
        self.assertEqual(review["proposal_id"], "patch_proposal_phase100")
        self.assertEqual(
            review["authorization_id"],
            "patch_apply_authorization_phase100",
        )

    def test_missing_apply_result_is_insufficient_evidence(self):
        review = self._review()
        self.assertEqual(review["decision"], INSUFFICIENT_EVIDENCE)
        self.assertFalse(review["eligible_for_completion"])

    def test_no_changed_files_is_rejected(self):
        review = self._review(self._result(files_changed=[]))
        self.assertEqual(review["decision"], REJECTED)

    def test_false_causal_change_is_rejected(self):
        review = self._review(self._result(causal_change_observed=False))
        self.assertEqual(review["decision"], REJECTED)

    def test_verification_not_required_is_rejected(self):
        review = self._review(self._result(requires_verification=False))
        self.assertEqual(review["decision"], REJECTED)

    def test_no_operations_applied_is_rejected(self):
        review = self._review(self._result(operations_applied=[]))
        self.assertEqual(review["decision"], REJECTED)

    def test_identical_before_after_hashes_are_rejected(self):
        review = self._review(
            self._result(after_sha256={"src/phase100.txt": "1" * 64})
        )
        self.assertEqual(review["decision"], REJECTED)

    def test_missing_proposal_id_is_rejected(self):
        review = self._review(self._result(proposal_id=None))
        self.assertEqual(review["decision"], REJECTED)

    def test_missing_authorization_id_is_rejected(self):
        review = self._review(self._result(authorization_id=None))
        self.assertEqual(review["decision"], REJECTED)

    def test_absolute_changed_file_path_is_rejected(self):
        review = self._review(
            self._result(
                files_changed=["/tmp/outside.txt"],
                before_sha256={"/tmp/outside.txt": "1" * 64},
                after_sha256={"/tmp/outside.txt": "2" * 64},
            )
        )
        self.assertEqual(review["decision"], REJECTED)

    def test_parent_traversal_changed_file_path_is_rejected(self):
        review = self._review(
            self._result(
                files_changed=["../outside.txt"],
                before_sha256={"../outside.txt": "1" * 64},
                after_sha256={"../outside.txt": "2" * 64},
            )
        )
        self.assertEqual(review["decision"], REJECTED)

    def test_changed_file_resolving_outside_project_root_is_rejected(self):
        outside = self.root.parent / f"{self.root.name}_outside"
        outside.mkdir()
        link = self.root / "linked_outside"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest("Symlinks are unavailable in this test environment.")
        self.addCleanup(outside.rmdir)

        review = self._review(
            self._result(
                files_changed=["linked_outside/phase100.txt"],
                before_sha256={"linked_outside/phase100.txt": "1" * 64},
                after_sha256={"linked_outside/phase100.txt": "2" * 64},
            )
        )
        self.assertEqual(review["decision"], REJECTED)

    def test_mismatched_task_id_is_rejected(self):
        review = self._review(self._result(task_id="task_other"))
        self.assertEqual(review["decision"], REJECTED)

    def test_review_does_not_mutate_task_state(self):
        task = self._task()
        before = dict(vars(task))
        review = self._review(self._result())
        self.assertEqual(vars(task), before)
        self.assertFalse(review["task_completed"])
        self.assertFalse(review["task_state_mutated"])

    def test_review_does_not_apply_patches(self):
        target = self.root / "src" / "phase100.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("before\n", encoding="utf-8")
        review = self._review(self._result())
        self.assertEqual(target.read_text(encoding="utf-8"), "before\n")
        self.assertFalse(review["patch_applied_by_review"])


if __name__ == "__main__":
    unittest.main()
