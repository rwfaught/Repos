import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.paths as project_paths
from orchestrator.patch_apply_authorization import (
    create_patch_apply_authorization,
    patch_apply_authorization_path,
)
from orchestrator.patch_apply_engine import (
    apply_authorized_patch,
    load_patch_apply_result,
)
from orchestrator.patch_proposal import create_patch_proposal, patch_proposal_path
from orchestrator.task_schema import (
    FILESYSTEM_MUTATION_EXECUTION_POLICY,
    REPORT_ONLY_EXECUTION_POLICY,
    Task,
)


class Phase99BoundedPatchApplyEngineTests(unittest.TestCase):
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

    def _task(self, **overrides) -> Task:
        task = Task(
            id="task_phase99",
            run_id="run_phase99",
            title="Apply an operator-authorized bounded patch",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Apply the exact authorized replacement."],
            files_in_scope=["src/phase99.txt"],
            retry_count=0,
            execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
            requires_causal_change=True,
        )
        for key, value in overrides.items():
            setattr(task, key, value)
        return task

    def _proposal(self, task: Task | None = None) -> dict:
        task = task or self._task()
        return create_patch_proposal(
            task,
            proposed_changes=[
                {
                    "path": task.files_in_scope[0],
                    "description": "Replace the exact bounded text.",
                }
            ],
            unified_diff=(
                f"--- a/{task.files_in_scope[0]}\n"
                f"+++ b/{task.files_in_scope[0]}\n"
                "@@ -1 +1 @@\n-before\n+after\n"
            ),
            rationale="The exact replacement is ready for operator review.",
        )

    def _authorization(self, proposal: dict, **overrides) -> dict:
        arguments = {
            "operator_decision": "authorize_apply",
            "operator_label": "operator_roger",
            "decision_reason": "Approved for the bounded apply boundary.",
        }
        arguments.update(overrides)
        return create_patch_apply_authorization(proposal["proposal_id"], **arguments)

    def _operation(self, **overrides) -> dict:
        operation = {
            "operation_id": "replace_phase99_text",
            "file_path": "src/phase99.txt",
            "expected_before": "before",
            "replacement_after": "after",
            "description": "Apply the reviewed exact replacement.",
        }
        operation.update(overrides)
        return operation

    def _target(self, content: str = "before\n") -> Path:
        target = self.root / "src" / "phase99.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def _rewrite(self, path: Path, payload: dict, **changes) -> dict:
        updated = dict(payload)
        updated.update(changes)
        path.write_text(json.dumps(updated, indent=2), encoding="utf-8")
        return updated

    def test_valid_authorized_proposal_applies_exact_replacement(self):
        target = self._target()
        proposal = self._proposal()
        authorization = self._authorization(proposal)

        result = apply_authorized_patch(
            authorization["authorization_id"],
            operations=[self._operation()],
        )

        self.assertEqual(target.read_text(encoding="utf-8"), "after\n")
        self.assertEqual(load_patch_apply_result(result["apply_id"]), result)
        self.assertTrue(result["applied"])

    def test_apply_result_records_required_causal_evidence(self):
        self._target()
        proposal = self._proposal()
        authorization = self._authorization(proposal)
        result = apply_authorized_patch(
            authorization["authorization_id"],
            operations=[self._operation()],
        )

        self.assertEqual(result["proposal_id"], proposal["proposal_id"])
        self.assertEqual(
            result["authorization_id"],
            authorization["authorization_id"],
        )
        self.assertEqual(result["task_id"], proposal["task_id"])
        self.assertEqual(result["files_changed"], ["src/phase99.txt"])
        self.assertIn("src/phase99.txt", result["before_sha256"])
        self.assertIn("src/phase99.txt", result["after_sha256"])
        self.assertNotEqual(
            result["before_sha256"]["src/phase99.txt"],
            result["after_sha256"]["src/phase99.txt"],
        )
        self.assertEqual(
            result["operations_applied"][0]["operation_id"],
            "replace_phase99_text",
        )
        self.assertTrue(result["requires_verification"])
        self.assertTrue(result["causal_change_observed"])

    def test_missing_authorization_is_rejected(self):
        with self.assertRaises(FileNotFoundError):
            apply_authorized_patch(
                "patch_apply_authorization_unknown",
                operations=[self._operation()],
            )

    def test_rejected_authorization_is_rejected_without_write(self):
        target = self._target()
        proposal = self._proposal()
        authorization = self._authorization(
            proposal,
            operator_decision="reject_apply",
        )

        with self.assertRaisesRegex(ValueError, "authorize_apply"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[self._operation()],
            )
        self.assertEqual(target.read_text(encoding="utf-8"), "before\n")

    def test_report_only_proposal_is_rejected(self):
        target = self._target()
        proposal = self._proposal()
        authorization = self._authorization(proposal)
        self._rewrite(
            patch_proposal_path(proposal["proposal_id"]),
            proposal,
            execution_policy=REPORT_ONLY_EXECUTION_POLICY,
        )

        with self.assertRaisesRegex(ValueError, "report_only proposals"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[self._operation()],
            )
        self.assertEqual(target.read_text(encoding="utf-8"), "before\n")

    def test_already_applied_proposal_is_rejected(self):
        target = self._target()
        proposal = self._proposal()
        authorization = self._authorization(proposal)
        self._rewrite(
            patch_proposal_path(proposal["proposal_id"]),
            proposal,
            applied=True,
        )

        with self.assertRaisesRegex(ValueError, "unapplied proposal"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[self._operation()],
            )
        self.assertEqual(target.read_text(encoding="utf-8"), "before\n")

    def test_already_applied_authorization_is_rejected(self):
        target = self._target()
        proposal = self._proposal()
        authorization = self._authorization(proposal)
        self._rewrite(
            patch_apply_authorization_path(authorization["authorization_id"]),
            authorization,
            applied=True,
        )

        with self.assertRaisesRegex(ValueError, "unapplied authorization"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[self._operation()],
            )
        self.assertEqual(target.read_text(encoding="utf-8"), "before\n")

    def test_authorization_without_separate_boundary_is_rejected(self):
        target = self._target()
        proposal = self._proposal()
        authorization = self._authorization(proposal)
        self._rewrite(
            patch_apply_authorization_path(authorization["authorization_id"]),
            authorization,
            requires_separate_apply_boundary=False,
        )

        with self.assertRaisesRegex(ValueError, "separate apply boundary"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[self._operation()],
            )
        self.assertEqual(target.read_text(encoding="utf-8"), "before\n")

    def test_absolute_operation_path_is_rejected(self):
        proposal = self._proposal()
        authorization = self._authorization(proposal)

        with self.assertRaisesRegex(ValueError, "must be relative"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[self._operation(file_path="/tmp/outside.txt")],
            )

    def test_parent_traversal_operation_path_is_rejected(self):
        proposal = self._proposal()
        authorization = self._authorization(proposal)

        with self.assertRaisesRegex(ValueError, "parent traversal"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[self._operation(file_path="../outside.txt")],
            )

    def test_file_outside_proposal_scope_is_rejected(self):
        proposal = self._proposal()
        authorization = self._authorization(proposal)

        with self.assertRaisesRegex(ValueError, "outside proposal files_in_scope"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[self._operation(file_path="src/outside.txt")],
            )

    def test_file_outside_authorization_scope_is_rejected(self):
        task = self._task(files_in_scope=["src/phase99.txt", "src/other.txt"])
        proposal = self._proposal(task)
        authorization = self._authorization(
            proposal,
            files_authorized=["src/other.txt"],
        )

        with self.assertRaisesRegex(ValueError, "outside authorization"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[self._operation()],
            )

    def test_zero_expected_matches_fails_without_write(self):
        target = self._target("different\n")
        proposal = self._proposal()
        authorization = self._authorization(proposal)

        with self.assertRaisesRegex(ValueError, "found 0 matches"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[self._operation()],
            )
        self.assertEqual(target.read_text(encoding="utf-8"), "different\n")

    def test_multiple_expected_matches_fail_without_write(self):
        target = self._target("before and before\n")
        proposal = self._proposal()
        authorization = self._authorization(proposal)

        with self.assertRaisesRegex(ValueError, "found 2 matches"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[self._operation()],
            )
        self.assertEqual(target.read_text(encoding="utf-8"), "before and before\n")

    def test_all_operations_are_validated_before_any_file_is_written(self):
        first = self._target()
        second = self.root / "src" / "second.txt"
        second.write_text("no match\n", encoding="utf-8")
        task = self._task(files_in_scope=["src/phase99.txt", "src/second.txt"])
        proposal = self._proposal(task)
        authorization = self._authorization(proposal)

        with self.assertRaisesRegex(ValueError, "found 0 matches"):
            apply_authorized_patch(
                authorization["authorization_id"],
                operations=[
                    self._operation(),
                    self._operation(
                        operation_id="replace_second",
                        file_path="src/second.txt",
                    ),
                ],
            )
        self.assertEqual(first.read_text(encoding="utf-8"), "before\n")
        self.assertEqual(second.read_text(encoding="utf-8"), "no match\n")

    def test_apply_does_not_complete_task_or_satisfy_verification(self):
        target = self._target()
        task = self._task()
        proposal = self._proposal(task)
        authorization = self._authorization(proposal)
        result = apply_authorized_patch(
            authorization["authorization_id"],
            operations=[self._operation()],
        )

        self.assertEqual(target.read_text(encoding="utf-8"), "after\n")
        self.assertEqual(task.status, "queued")
        self.assertIsNone(task.execution_artifact_id)
        self.assertFalse(result["task_completed"])
        self.assertFalse(result["verification_satisfied"])

    def test_apply_does_not_mutate_proposal_or_authorization_artifacts(self):
        self._target()
        proposal = self._proposal()
        authorization = self._authorization(proposal)
        proposal_before = patch_proposal_path(proposal["proposal_id"]).read_bytes()
        authorization_before = patch_apply_authorization_path(
            authorization["authorization_id"]
        ).read_bytes()

        apply_authorized_patch(
            authorization["authorization_id"],
            operations=[self._operation()],
        )

        self.assertEqual(
            patch_proposal_path(proposal["proposal_id"]).read_bytes(),
            proposal_before,
        )
        self.assertEqual(
            patch_apply_authorization_path(
                authorization["authorization_id"]
            ).read_bytes(),
            authorization_before,
        )


if __name__ == "__main__":
    unittest.main()
