import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from orchestrator.alpha_runtime import SCHEMA_VERSION, atomic_write_json, isolated_data_root, reconcile_lifecycle
from orchestrator.operator_coding_task_packet import run_operator_coding_task_packet
from orchestrator.task_schema import FILESYSTEM_MUTATION_EXECUTION_POLICY, Task
from orchestrator.trusted_worker_security import (
    TRUSTED_LOCAL_UNSANDBOXED,
    prepare_trusted_worker_workspace,
    resolve_workspace_target,
)
from providers.subprocess_worker_provider import SubprocessWorkerProvider


class TrustedWorkerSecurityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.data_root = self.root / "data"

    def tearDown(self):
        self.directory.cleanup()

    def _task(self, suffix="one", files=None):
        return Task(
            id=f"task_security_{suffix}", run_id=f"run_security_{suffix}", title="Trusted worker fixture",
            role="coder", status="queued", dependencies=[], success_criteria=["Write target."],
            files_in_scope=files or [f"outputs/{suffix}.txt"], retry_count=0, expected_output=f"output-{suffix}",
            execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY, requires_causal_change=True,
        )

    def _authorization(self, task):
        return {
            "schema_version": SCHEMA_VERSION, "authorization_id": f"authorization_{task.id}", "task_id": task.id,
            "authorized_scope": list(task.files_in_scope), "decision": "authorized", "execution_authorized": True,
            "operator_provenance": "test_operator", "worker_trust_posture": TRUSTED_LOCAL_UNSANDBOXED,
        }

    def _context(self, task):
        security = prepare_trusted_worker_workspace(
            self.data_root, task_id=task.id, run_id=task.run_id,
            trust_posture=TRUSTED_LOCAL_UNSANDBOXED, declared_paths=task.files_in_scope,
        )
        task.worker_security = security
        return {
            "execution_authorization": self._authorization(task), "worker_security": security,
            "allowed_paths": [str(resolve_workspace_target(security, path)) for path in task.files_in_scope],
        }

    def _worker(self, body, name="worker.py"):
        path = self.root / name
        path.write_text(body, encoding="utf-8")
        return [sys.executable, str(path)]

    def _success_worker(self, extra=""):
        return self._worker(
            "import json, os, pathlib, sys\n"
            "p=json.load(sys.stdin)\n"
            "target=pathlib.Path(p['allowed_paths'][0])\n"
            "target.write_text(p['expected_output'], encoding='utf-8')\n"
            + extra + "\n"
            "print(json.dumps({'task_id':p['task_id'],'run_id':p['run_id'],'status':'success','output':p['expected_output'],'changed_paths':[str(target)],'cwd':os.getcwd()}))\n"
        )

    def _packet(self, suffix="packet", **overrides):
        packet = {
            "packet_id": f"packet_{suffix}", "run_id": f"run_{suffix}", "task_id": f"task_{suffix}",
            "title": "Trusted worker packet", "files_in_scope": [f"outputs/{suffix}.txt"],
            "success_criteria": ["Write target."], "expected_output": f"trusted-worker-output-{suffix}",
            "provider_name": "subprocess_worker", "authorization_decision": "authorize_execution",
            "authorization_provenance": "test_operator", "worker_trust_posture": TRUSTED_LOCAL_UNSANDBOXED,
        }
        packet.update(overrides)
        return packet

    def _run_packet(self, packet, command=None, timeout=1.0):
        provider = SubprocessWorkerProvider(command or self._success_worker(), timeout_seconds=timeout)
        with isolated_data_root(self.data_root), contextlib.redirect_stdout(io.StringIO()):
            return run_operator_coding_task_packet(packet, provider=provider)

    def test_worker_cwd_is_per_run_workspace_and_not_test_root(self):
        task = self._task("cwd")
        context = self._context(task)
        result = SubprocessWorkerProvider(self._success_worker()).execute("coder", task, context)
        workspace = Path(context["worker_security"]["workspace_path"])
        self.assertEqual(result["status"], "success")
        self.assertEqual(Path(result["metadata"]["worker_result"]["cwd"]), workspace)
        self.assertNotEqual(workspace, self.root)

    def test_distinct_runs_receive_distinct_workspaces(self):
        first, second = self._task("first"), self._task("second")
        first_context, second_context = self._context(first), self._context(second)
        self.assertNotEqual(first_context["worker_security"]["workspace_path"], second_context["worker_security"]["workspace_path"])

    def test_missing_and_unsupported_trust_posture_block_before_persistence(self):
        for posture, expected in (("", "worker_trust_posture_missing"), ("sandboxed", "worker_trust_posture_unsupported")):
            with self.subTest(posture=posture):
                result = self._run_packet(self._packet(f"posture_{expected}", worker_trust_posture=posture))
                self.assertIn(expected, result["blocked_conditions"])
                self.assertFalse((self.data_root / "tasks").exists())

    def test_provider_missing_or_unsupported_trust_posture_blocks_launch(self):
        for posture, expected in (("", "worker_trust_posture_missing"), ("untrusted", "worker_trust_posture_unsupported")):
            with self.subTest(posture=posture):
                task = self._task(f"direct_{expected}")
                context = self._context(task)
                context["worker_security"]["trust_posture"] = posture
                with patch("providers.subprocess_worker_provider.subprocess.Popen") as launched:
                    result = SubprocessWorkerProvider(["never-started"]).execute("coder", task, context)
                self.assertEqual(result["error"], expected)
                launched.assert_not_called()

    def test_missing_workspace_blocks_launch(self):
        task = self._task("workspace_missing")
        context = self._context(task)
        context["worker_security"]["workspace_path"] = str(self.root / "does-not-exist")
        with patch("providers.subprocess_worker_provider.subprocess.Popen") as launched:
            result = SubprocessWorkerProvider(["never-started"]).execute("coder", task, context)
        self.assertEqual(result["error"], "worker_workspace_creation_failed")
        launched.assert_not_called()

    def test_symlink_target_and_parent_chain_are_rejected_before_launch(self):
        for suffix, prepare in (("link_target", "target"), ("link_parent", "parent")):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as outside_directory:
                declared = ["linked_target"] if prepare == "target" else ["nested/output.txt"]
                task = self._task(suffix, declared)
                context = self._context(task)
                workspace = Path(context["worker_security"]["workspace_path"])
                outside = Path(outside_directory)
                link = workspace / ("linked_target" if prepare == "target" else "nested")
                if link.exists():
                    link.rmdir()
                created = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], capture_output=True, text=True)
                self.assertEqual(created.returncode, 0, created.stderr)
                with patch("providers.subprocess_worker_provider.subprocess.Popen") as launched:
                    result = SubprocessWorkerProvider(["never-started"]).execute("coder", task, context)
                self.assertEqual(result["error"], "worker_symlink_reparse_risk")
                launched.assert_not_called()

    def test_changed_declared_parent_blocks_real_helper_before_launch(self):
        command = self._worker(
            "import pathlib\n"
            "(pathlib.Path.cwd() / 'launch_marker.txt').write_text('launched', encoding='utf-8')\n",
            "launch_marker_worker.py",
        )
        for suffix, files, replace in (
            ("removed", ["outputs/removed.txt"], "removed"),
            ("replaced_file", ["outputs/replaced.txt"], "file"),
            ("nested_removed", ["nested/parent/removed.txt"], "nested_removed"),
        ):
            with self.subTest(suffix=suffix):
                task = self._task(suffix, files)
                context = self._context(task)
                workspace = Path(context["worker_security"]["workspace_path"])
                self.assertTrue((workspace / files[0]).parent.is_dir())
                if replace == "nested_removed":
                    (workspace / "nested" / "parent").rmdir()
                    (workspace / "nested").rmdir()
                else:
                    parent = workspace / "outputs"
                    parent.rmdir()
                    if replace == "file":
                        parent.write_text("replacement", encoding="utf-8")
                result = SubprocessWorkerProvider(command).execute("coder", task, context)
                self.assertEqual(result["error"], "worker_prelaunch_path_state_unsafe")
                self.assertFalse((workspace / "launch_marker.txt").exists())

    def test_reparse_parent_blocks_real_helper_before_launch(self):
        command = self._worker(
            "import pathlib\n"
            "(pathlib.Path.cwd() / 'launch_marker.txt').write_text('launched', encoding='utf-8')\n",
            "reparse_launch_marker_worker.py",
        )
        with tempfile.TemporaryDirectory() as outside_directory:
            task = self._task("reparse_real", ["nested/output.txt"])
            context = self._context(task)
            workspace = Path(context["worker_security"]["workspace_path"])
            parent = workspace / "nested"
            parent.rmdir()
            created = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(parent), outside_directory],
                capture_output=True,
                text=True,
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            result = SubprocessWorkerProvider(command).execute("coder", task, context)
            self.assertEqual(result["error"], "worker_symlink_reparse_risk")
            self.assertFalse((workspace / "launch_marker.txt").exists())

    def test_reparse_policy_fails_closed_in_portable_abstraction(self):
        task = self._task("reparse_abstraction")
        context = self._context(task)
        with patch("orchestrator.trusted_worker_security._is_reparse_or_symlink", return_value=True), patch(
            "providers.subprocess_worker_provider.subprocess.Popen"
        ) as launched:
            result = SubprocessWorkerProvider(["never-started"]).execute("coder", task, context)
        self.assertEqual(result["error"], "worker_symlink_reparse_risk")
        launched.assert_not_called()

    def test_ordinary_declared_output_succeeds_and_audit_is_persisted(self):
        result = self._run_packet(self._packet("audit_ok"))
        self.assertTrue(result["execution_succeeded"])
        task = json.loads((self.data_root / "tasks" / "task_audit_ok.json").read_text())
        artifact = json.loads((self.data_root / "artifacts" / f"{result['execution_artifact_id']}.json").read_text())
        audit = task["worker_security"]["workspace_effect_audit"]
        self.assertTrue(audit["passed"])
        self.assertEqual(task["worker_security"]["trust_posture"], TRUSTED_LOCAL_UNSANDBOXED)
        self.assertEqual(artifact["worker_security"]["workspace_id"], task["worker_security"]["workspace_id"])

    def test_undeclared_workspace_mutation_blocks_success(self):
        command = self._success_worker("(pathlib.Path(os.getcwd()) / 'rogue.txt').write_text('rogue', encoding='utf-8')")
        result = self._run_packet(self._packet("rogue"), command)
        self.assertFalse(result["execution_succeeded"])
        self.assertEqual(result["final_task_status"], "execution_failed")
        task = json.loads((self.data_root / "tasks" / "task_rogue.json").read_text())
        self.assertIn("rogue.txt", task["worker_security"]["workspace_effect_audit"]["undeclared_changes"])

    def test_workspace_deletion_is_detected(self):
        task = self._task("delete")
        context = self._context(task)
        workspace = Path(context["worker_security"]["workspace_path"])
        tracked = workspace / "tracked.txt"
        tracked.write_text("before", encoding="utf-8")
        command = self._success_worker("(pathlib.Path(os.getcwd()) / 'tracked.txt').unlink()")
        result = SubprocessWorkerProvider(command).execute("coder", task, context)
        self.assertEqual(result["error"], "worker_undeclared_workspace_mutation")
        self.assertIn("tracked.txt", result["metadata"]["worker_security"]["workspace_effect_audit"]["deleted"])

    def test_workspace_type_change_is_detected(self):
        task = self._task("type_change")
        context = self._context(task)
        workspace = Path(context["worker_security"]["workspace_path"])
        tracked = workspace / "tracked.txt"
        tracked.write_text("before", encoding="utf-8")
        command = self._success_worker("(pathlib.Path(os.getcwd()) / 'tracked.txt').unlink(); (pathlib.Path(os.getcwd()) / 'tracked.txt').mkdir()")
        result = SubprocessWorkerProvider(command).execute("coder", task, context)
        self.assertEqual(result["error"], "worker_undeclared_workspace_mutation")
        self.assertIn("tracked.txt", result["metadata"]["worker_security"]["workspace_effect_audit"]["modified_or_type_changed"])

    def test_timeout_uses_real_tree_cleanup_and_records_status(self):
        command = self._worker(
            "import json, pathlib, subprocess, sys, time\n"
            "p=json.load(sys.stdin); workspace=pathlib.Path.cwd()\n"
            "subprocess.Popen([sys.executable,'-c',\"import pathlib,time; time.sleep(0.4); pathlib.Path('descendant_marker.txt').write_text('alive')\"], cwd=workspace)\n"
            "time.sleep(2)\n",
            "timeout_tree.py",
        )
        task = self._task("timeout_tree")
        context = self._context(task)
        result = SubprocessWorkerProvider(command, timeout_seconds=0.05).execute("coder", task, context)
        workspace = Path(context["worker_security"]["workspace_path"])
        time.sleep(0.6)
        self.assertEqual(result["error"], "worker_timeout")
        self.assertEqual(result["metadata"]["worker_security"]["cleanup_status"], "confirmed")
        self.assertFalse((workspace / "descendant_marker.txt").exists())

    def test_unconfirmed_timeout_cleanup_cannot_complete_or_accept(self):
        command = self._worker("import time; time.sleep(2)\n", "unconfirmed.py")
        provider = SubprocessWorkerProvider(command, timeout_seconds=0.01)
        def cleanup_but_report_unconfirmed(process):
            process.kill()
            process.wait(timeout=1.0)
            return "unconfirmed", "simulated confirmation failure after direct cleanup"
        with patch.object(provider, "_terminate_descendants", side_effect=cleanup_but_report_unconfirmed):
            with isolated_data_root(self.data_root), contextlib.redirect_stdout(io.StringIO()):
                result = run_operator_coding_task_packet(self._packet("unconfirmed"), provider=provider)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["final_task_status"], "execution_failed")
        task = json.loads((self.data_root / "tasks" / "task_unconfirmed.json").read_text())
        self.assertEqual(task["worker_security"]["cleanup_status"], "unconfirmed")

    def test_reconciliation_reports_missing_worker_security_linkage_read_only(self):
        task_path = self.data_root / "tasks" / "task_reconcile_security.json"
        atomic_write_json(task_path, {
            "schema_version": SCHEMA_VERSION, "id": "task_reconcile_security", "run_id": "run_reconcile_security",
            "title": "fixture", "role": "coder", "status": "execution_failed", "dependencies": [],
            "success_criteria": ["fixture"], "files_in_scope": ["outputs/fixture.txt"], "retry_count": 0,
            "execution_policy": FILESYSTEM_MUTATION_EXECUTION_POLICY,
            "execution_authorization_provenance": {},
            "worker_security": {"launch_attempted": True, "cleanup_status": "unconfirmed"},
        })
        before = task_path.read_bytes()
        result = reconcile_lifecycle(self.data_root)
        after = task_path.read_bytes()
        classifications = {item["classification"] for item in result["findings"]}
        self.assertEqual(before, after)
        self.assertTrue({"missing_or_inconsistent_worker_trust_posture", "missing_worker_workspace_identity", "missing_workspace_effect_audit", "incomplete_worker_cleanup_status"}.issubset(classifications))

    def test_reconciliation_detects_cross_record_security_mismatch_read_only(self):
        task_id, run_id = "task_reconcile_cross", "run_reconcile_cross"
        artifact_id, authorization_id = "artifact_reconcile_cross", "authorization_reconcile_cross"
        task_path = self.data_root / "tasks" / f"{task_id}.json"
        records = {
            task_path: {
                "schema_version": SCHEMA_VERSION, "id": task_id, "run_id": run_id, "status": "execution_failed",
                "execution_policy": FILESYSTEM_MUTATION_EXECUTION_POLICY, "files_in_scope": ["output.txt"],
                "execution_artifact_id": artifact_id,
                "execution_authorization_provenance": {"authorization_id": authorization_id, "worker_trust_posture": TRUSTED_LOCAL_UNSANDBOXED},
                "worker_security": {"trust_posture": TRUSTED_LOCAL_UNSANDBOXED, "workspace_id": "workspace_cross", "workspace_path": "C:/safe/cross", "launch_attempted": True, "workspace_effect_audit": {"passed": True}, "cleanup_status": "confirmed"},
            },
            self.data_root / "runs" / f"{run_id}.json": {
                "schema_version": SCHEMA_VERSION, "id": run_id,
                "worker_security": {"trust_posture": "mismatched_run_posture", "workspace_id": "workspace_cross", "workspace_path": "C:/safe/cross"},
            },
            self.data_root / "execution_authorizations" / f"{authorization_id}.json": {
                "schema_version": SCHEMA_VERSION, "authorization_id": authorization_id, "task_id": task_id,
                "authorized_scope": ["output.txt"], "decision": "authorized", "worker_trust_posture": "mismatched_authorization_posture",
            },
            self.data_root / "artifacts" / f"{artifact_id}.json": {
                "schema_version": SCHEMA_VERSION, "artifact_id": artifact_id, "task_id": task_id, "run_id": run_id,
                "authorization_id": authorization_id,
                "worker_security": {"trust_posture": "mismatched_artifact_posture", "workspace_id": "workspace_cross", "workspace_path": "C:/safe/cross"},
            },
            self.data_root / "verifier_results" / f"{task_id}_20260711T000000Z.json": {
                "schema_version": SCHEMA_VERSION, "task_id": task_id, "run_id": run_id,
                "execution_artifact_id": artifact_id, "authorization_id": authorization_id,
            },
        }
        for path, payload in records.items():
            atomic_write_json(path, payload)
        before = {path: path.read_bytes() for path in records}
        result = reconcile_lifecycle(self.data_root)
        classifications = {item["classification"] for item in result["findings"]}
        self.assertFalse(result["healthy"])
        self.assertIn("worker_trust_posture_mismatch", classifications)
        self.assertEqual(before, {path: path.read_bytes() for path in records})

    def test_repository_data_root_is_unchanged_by_disposable_worker_contract_run(self):
        import orchestrator.paths as paths

        before = sorted(str(path.relative_to(paths.DATA_DIR)) for path in paths.DATA_DIR.rglob("*") if path.is_file())
        self._run_packet(self._packet("repo_clean"))
        after = sorted(str(path.relative_to(paths.DATA_DIR)) for path in paths.DATA_DIR.rglob("*") if path.is_file())
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
