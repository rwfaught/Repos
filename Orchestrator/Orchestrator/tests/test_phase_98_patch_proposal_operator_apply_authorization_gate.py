import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.paths as project_paths
from orchestrator.patch_apply_authorization import (
    create_patch_apply_authorization,
    load_patch_apply_authorization,
)
from orchestrator.patch_proposal import create_patch_proposal, patch_proposal_path
from orchestrator.task_schema import (
    FILESYSTEM_MUTATION_EXECUTION_POLICY,
    REPORT_ONLY_EXECUTION_POLICY,
    Task,
)


class Phase98PatchProposalOperatorApplyAuthorizationGateTests(unittest.TestCase):
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
            id="task_phase98",
            run_id="run_phase98",
            title="Authorize a bounded patch for later apply",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Authorize, but do not apply, the proposal."],
            files_in_scope=["src/phase98.txt"],
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
                    "description": "Replace the bounded file content.",
                }
            ],
            unified_diff=(
                f"--- a/{task.files_in_scope[0]}\n"
                f"+++ b/{task.files_in_scope[0]}\n"
                "@@ -1 +1 @@\n-before\n+after\n"
            ),
            rationale="The proposal is ready for operator judgment.",
        )

    def _authorize(self, proposal: dict, **overrides) -> dict:
        arguments = {
            "operator_decision": "authorize_apply",
            "operator_label": "operator_roger",
            "decision_reason": "Reviewed and bounded for a later apply boundary.",
        }
        arguments.update(overrides)
        return create_patch_apply_authorization(proposal["proposal_id"], **arguments)

    def _rewrite_proposal(self, proposal: dict, **changes) -> None:
        updated = dict(proposal)
        updated.update(changes)
        patch_proposal_path(proposal["proposal_id"]).write_text(
            json.dumps(updated, indent=2),
            encoding="utf-8",
        )

    def test_create_store_and_load_valid_apply_authorization(self):
        authorization = self._authorize(self._proposal())
        loaded = load_patch_apply_authorization(authorization["authorization_id"])

        self.assertEqual(loaded, authorization)
        self.assertEqual(loaded["artifact_type"], "patch_apply_authorization")
        self.assertEqual(
            loaded["authorization_status"],
            "authorized_for_future_apply_boundary",
        )

    def test_authorization_preserves_proposal_task_policy_and_files(self):
        proposal = self._proposal()
        authorization = self._authorize(proposal)

        self.assertEqual(authorization["proposal_id"], proposal["proposal_id"])
        self.assertEqual(authorization["task_id"], proposal["task_id"])
        self.assertEqual(authorization["run_id"], proposal["run_id"])
        self.assertEqual(
            authorization["execution_policy"],
            FILESYSTEM_MUTATION_EXECUTION_POLICY,
        )
        self.assertEqual(authorization["files_authorized"], proposal["files_in_scope"])

    def test_authorization_requires_separate_boundary_and_remains_unapplied(self):
        authorization = self._authorize(self._proposal())

        self.assertTrue(authorization["requires_separate_apply_boundary"])
        self.assertFalse(authorization["applied"])
        self.assertEqual(authorization["source"], "operator_apply_authorization")

    def test_absolute_authorized_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be relative"):
            self._authorize(
                self._proposal(),
                files_authorized=["/tmp/outside.txt"],
            )

    def test_parent_traversal_authorized_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "parent traversal"):
            self._authorize(
                self._proposal(),
                files_authorized=["../outside.txt"],
            )

    def test_authorized_path_outside_proposal_scope_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside proposal files_in_scope"):
            self._authorize(
                self._proposal(),
                files_authorized=["src/outside.txt"],
            )

    def test_report_only_proposal_is_rejected(self):
        proposal = self._proposal()
        self._rewrite_proposal(
            proposal,
            execution_policy=REPORT_ONLY_EXECUTION_POLICY,
        )

        with self.assertRaisesRegex(ValueError, "report_only proposals"):
            self._authorize(proposal)

    def test_already_applied_proposal_is_rejected(self):
        proposal = self._proposal()
        self._rewrite_proposal(proposal, applied=True)

        with self.assertRaisesRegex(ValueError, "unapplied proposal"):
            self._authorize(proposal)

    def test_proposal_without_operator_apply_requirement_is_rejected(self):
        proposal = self._proposal()
        self._rewrite_proposal(proposal, requires_operator_apply=False)

        with self.assertRaisesRegex(ValueError, "does not require operator apply"):
            self._authorize(proposal)

    def test_unknown_proposal_id_is_rejected(self):
        with self.assertRaises(FileNotFoundError):
            create_patch_apply_authorization(
                "patch_proposal_unknown",
                operator_decision="authorize_apply",
                operator_label="operator_roger",
                decision_reason="No stored proposal exists.",
            )

    def test_authorization_does_not_mutate_referenced_file_or_proposal(self):
        target = self.root / "src" / "phase98.txt"
        target.parent.mkdir(parents=True)
        target.write_text("before\n", encoding="utf-8")
        proposal = self._proposal()

        self._authorize(proposal)
        stored_proposal = json.loads(
            patch_proposal_path(proposal["proposal_id"]).read_text(encoding="utf-8")
        )

        self.assertEqual(target.read_text(encoding="utf-8"), "before\n")
        self.assertEqual(stored_proposal, proposal)
        self.assertFalse(stored_proposal["applied"])

    def test_authorization_does_not_complete_task_or_satisfy_proof(self):
        task = self._task()
        authorization = self._authorize(self._proposal(task))

        self.assertEqual(task.status, "queued")
        self.assertIsNone(task.execution_artifact_id)
        self.assertFalse(authorization["execution_performed"])
        self.assertFalse(authorization["completion_proof"])
        self.assertFalse(authorization["verification_satisfied"])
        self.assertFalse(authorization["causal_change_satisfied"])
        self.assertFalse(authorization["provider_executed"])
        self.assertFalse(authorization["model_executed"])
        self.assertFalse(authorization["runtime_executed"])

    def test_reject_apply_decision_is_stored_without_application(self):
        authorization = self._authorize(
            self._proposal(),
            operator_decision="reject_apply",
            decision_reason="The proposed change needs revision.",
        )

        self.assertEqual(authorization["operator_decision"], "reject_apply")
        self.assertEqual(authorization["authorization_status"], "apply_rejected")
        self.assertFalse(authorization["applied"])


if __name__ == "__main__":
    unittest.main()
