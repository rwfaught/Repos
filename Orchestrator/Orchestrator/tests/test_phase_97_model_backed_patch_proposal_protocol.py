import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.paths as project_paths
from orchestrator.patch_proposal import create_patch_proposal, load_patch_proposal
from orchestrator.task_schema import (
    FILESYSTEM_MUTATION_EXECUTION_POLICY,
    REPORT_ONLY_EXECUTION_POLICY,
    Task,
)


class Phase97ModelBackedPatchProposalProtocolTests(unittest.TestCase):
    def _task(self, **overrides) -> Task:
        task = Task(
            id="task_phase97",
            run_id="run_phase97",
            title="Propose a bounded patch",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Propose, but do not apply, a bounded change."],
            files_in_scope=["src/phase97.txt"],
            retry_count=0,
            execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
            requires_causal_change=True,
        )
        for key, value in overrides.items():
            setattr(task, key, value)
        return task

    def _create(self, task: Task, **overrides):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        artifacts_dir = root / "data" / "artifacts"
        project_patch = patch.object(project_paths, "PROJECT_ROOT", root)
        artifact_patch = patch.object(artifact_store, "ARTIFACTS_DIR", artifacts_dir)
        project_patch.start()
        artifact_patch.start()
        self.addCleanup(project_patch.stop)
        self.addCleanup(artifact_patch.stop)
        self.addCleanup(temporary.cleanup)

        arguments = {
            "proposed_changes": [
                {
                    "path": "src/phase97.txt",
                    "description": "Replace the bounded file content.",
                }
            ],
            "unified_diff": (
                "diff --git a/src/phase97.txt b/src/phase97.txt\n"
                "--- a/src/phase97.txt\n"
                "+++ b/src/phase97.txt\n"
                "@@ -1 +1 @@\n"
                "-before\n"
                "+after\n"
            ),
            "rationale": "The proposed change satisfies the bounded task.",
            "risk_notes": ["Operator must review the replacement."],
            "validation_hints": ["Inspect the diff before applying it."],
        }
        arguments.update(overrides)
        proposal = create_patch_proposal(task, **arguments)
        return root, proposal

    def test_create_store_and_load_valid_filesystem_mutation_proposal(self):
        _, proposal = self._create(self._task())
        loaded = load_patch_proposal(proposal["proposal_id"])

        self.assertEqual(loaded, proposal)
        self.assertEqual(loaded["artifact_type"], "patch_proposal")
        self.assertEqual(loaded["proposal_status"], "awaiting_operator_apply")

    def test_proposal_preserves_task_policy_scope_and_diff(self):
        task = self._task()
        _, proposal = self._create(task)

        self.assertEqual(proposal["task_id"], task.id)
        self.assertEqual(proposal["run_id"], task.run_id)
        self.assertEqual(
            proposal["execution_policy"],
            FILESYSTEM_MUTATION_EXECUTION_POLICY,
        )
        self.assertEqual(proposal["files_in_scope"], task.files_in_scope)
        self.assertIn("+after", proposal["proposed_diff"])
        self.assertEqual(proposal["proposed_diff"], proposal["unified_diff"])

    def test_absolute_proposed_change_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be relative"):
            self._create(
                self._task(files_in_scope=["/tmp/outside.txt"]),
                proposed_changes=[
                    {"path": "/tmp/outside.txt", "description": "Unsafe change."}
                ],
                unified_diff="--- /tmp/outside.txt\n+++ /tmp/outside.txt\n",
            )

    def test_parent_traversal_proposed_change_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "parent traversal"):
            self._create(
                self._task(files_in_scope=["../outside.txt"]),
                proposed_changes=[
                    {"path": "../outside.txt", "description": "Unsafe change."}
                ],
                unified_diff="--- a/../outside.txt\n+++ b/../outside.txt\n",
            )

    def test_diff_cannot_expand_beyond_task_scope(self):
        with self.assertRaisesRegex(ValueError, "outside task files_in_scope"):
            self._create(
                self._task(),
                unified_diff="--- a/src/phase97.txt\n+++ b/src/outside.txt\n",
            )

    def test_proposal_does_not_mutate_referenced_file(self):
        task = self._task()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / task.files_in_scope[0]
            target.parent.mkdir(parents=True)
            target.write_text("before\n", encoding="utf-8")
            artifacts_dir = root / "artifacts"
            with (
                patch.object(project_paths, "PROJECT_ROOT", root),
                patch.object(artifact_store, "ARTIFACTS_DIR", artifacts_dir),
            ):
                create_patch_proposal(
                    task,
                    proposed_changes=[
                        {
                            "path": task.files_in_scope[0],
                            "description": "Replace content.",
                        }
                    ],
                    unified_diff=(
                        "--- a/src/phase97.txt\n"
                        "+++ b/src/phase97.txt\n"
                        "@@ -1 +1 @@\n-before\n+after\n"
                    ),
                    rationale="Bounded proposal only.",
                )

            self.assertEqual(target.read_text(encoding="utf-8"), "before\n")

    def test_proposal_does_not_complete_or_attach_execution_artifact(self):
        task = self._task()
        _, proposal = self._create(task)

        self.assertEqual(task.status, "queued")
        self.assertIsNone(task.execution_artifact_id)
        self.assertFalse(proposal["execution_performed"])
        self.assertFalse(proposal["completion_proof"])

    def test_operator_apply_gate_is_explicit_and_unapplied(self):
        _, proposal = self._create(self._task())

        self.assertTrue(proposal["requires_operator_apply"])
        self.assertFalse(proposal["applied"])
        self.assertEqual(proposal["source"], "manual_or_model_proposal")

    def test_proposal_does_not_satisfy_causal_change_proof(self):
        task = self._task()
        _, proposal = self._create(task)

        self.assertTrue(task.requires_causal_change)
        self.assertFalse(proposal["causal_change_satisfied"])
        self.assertFalse(proposal["provider_executed"])
        self.assertFalse(proposal["model_executed"])
        self.assertFalse(proposal["runtime_executed"])

    def test_report_only_tasks_are_deterministically_rejected(self):
        with self.assertRaisesRegex(ValueError, "report_only tasks are policy-incompatible"):
            self._create(
                self._task(
                    execution_policy=REPORT_ONLY_EXECUTION_POLICY,
                    requires_causal_change=False,
                )
            )


if __name__ == "__main__":
    unittest.main()
