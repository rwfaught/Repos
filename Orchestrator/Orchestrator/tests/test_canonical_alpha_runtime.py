import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from orchestrator.alpha_runtime import (
    SCHEMA_VERSION,
    atomic_write_json,
    isolated_data_root,
    reconcile_lifecycle,
)
from orchestrator.operator_coding_task_packet import run_operator_coding_task_packet
from orchestrator.operator_coding_task_packet_cli import main as packet_cli_main
from orchestrator.task_schema import FILESYSTEM_MUTATION_EXECUTION_POLICY, Task
from providers.subprocess_worker_provider import SubprocessWorkerProvider


class CanonicalAlphaRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.data_root = self.root / "data"

    def tearDown(self):
        self.directory.cleanup()

    def _packet(self, suffix="one", **overrides):
        packet = {
            "packet_id": f"packet_{suffix}",
            "run_id": f"run_{suffix}",
            "task_id": f"task_{suffix}",
            "title": "Canonical alpha test",
            "files_in_scope": [f"outputs/{suffix}.txt"],
            "success_criteria": ["Write the declared target."],
            "expected_output": f"canonical-output-{suffix}",
            "provider_name": "subprocess_worker",
            "authorization_decision": "authorize_execution",
            "authorization_provenance": "test_operator",
        }
        packet.update(overrides)
        return packet

    def _task(self, suffix="provider"):
        return Task(
            id=f"task_{suffix}",
            run_id=f"run_{suffix}",
            title="Provider contract test",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Write target."],
            files_in_scope=[f"outputs/{suffix}.txt"],
            retry_count=0,
            expected_output="provider-output",
            execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
            requires_causal_change=True,
        )

    def _authorization(self, task, **overrides):
        authorization = {
            "schema_version": SCHEMA_VERSION,
            "authorization_id": "authorization_test",
            "task_id": task.id,
            "authorized_scope": list(task.files_in_scope),
            "decision": "authorized",
            "execution_authorized": True,
            "operator_provenance": "test_operator",
        }
        authorization.update(overrides)
        return authorization

    def _worker(self, body, name="worker.py"):
        path = self.root / name
        path.write_text(body, encoding="utf-8")
        return [sys.executable, str(path)]

    def _valid_worker(self):
        return self._worker(
            "import json, pathlib, sys\n"
            "payload = json.load(sys.stdin)\n"
            "target = pathlib.Path(payload['allowed_paths'][0])\n"
            "target.parent.mkdir(parents=True, exist_ok=True)\n"
            "output = payload['expected_output']\n"
            "target.write_text(output, encoding='utf-8')\n"
            "print(json.dumps({'task_id': payload['task_id'], 'run_id': payload['run_id'], "
            "'status': 'success', 'output': output, 'target_path': str(target)}))\n"
        )

    def _run_packet(self, packet, command=None, timeout=2.0):
        provider = SubprocessWorkerProvider(command or self._valid_worker(), timeout_seconds=timeout)
        with isolated_data_root(self.data_root):
            return run_operator_coding_task_packet(packet, provider=provider)

    def _run_cli(self, packet, command=None):
        packet_path = self.root / f"{packet['packet_id']}.json"
        packet_path.write_text(json.dumps(packet), encoding="utf-8")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = packet_cli_main(
                [
                    "--packet-json",
                    str(packet_path),
                    "--data-root",
                    str(self.data_root),
                    "--worker-command",
                    *(command or self._valid_worker()),
                ]
            )
        return exit_code, json.loads(stdout.getvalue())

    def test_explicit_authorization_allows_dispatch(self):
        result = self._run_packet(self._packet("authorized"))
        self.assertTrue(result["execution_succeeded"])
        self.assertEqual(result["final_task_status"], "completed")
        self.assertTrue((self.root / "outputs" / "authorized.txt").exists())

    def test_missing_authorization_blocks_before_dispatch(self):
        packet = self._packet("missing_auth", authorization_decision="", authorization_provenance="")
        result = self._run_packet(packet)
        self.assertIn("execution_authorization_denied", result["blocked_conditions"])
        self.assertFalse((self.data_root / "tasks").exists())
        self.assertFalse((self.root / "outputs" / "missing_auth.txt").exists())

    def test_denied_authorization_blocks_before_dispatch(self):
        packet = self._packet("denied", authorization_decision="deny_execution")
        result = self._run_packet(packet)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["authorization"]["decision"], "denied")
        self.assertFalse((self.data_root / "runs").exists())

    def test_authorization_identity_and_scope_mismatch_block_at_worker_membrane(self):
        task = self._task("mismatch")
        provider = SubprocessWorkerProvider(["never-started"])
        for authorization, expected in (
            (self._authorization(task, task_id="task_other"), "execution_authorization_task_mismatch"),
            (self._authorization(task, authorized_scope=["outputs/other.txt"]), "execution_authorization_scope_mismatch"),
        ):
            with self.subTest(expected=expected), patch("providers.subprocess_worker_provider.subprocess.run") as run:
                result = provider.execute("coder", task, {"execution_authorization": authorization})
                self.assertEqual(result["error"], expected)
                run.assert_not_called()

    def test_subprocess_success_requires_valid_structured_output(self):
        task = self._task("success")
        target = self.root / "outputs" / "success.txt"
        provider = SubprocessWorkerProvider(self._valid_worker())
        result = provider.execute(
            "coder",
            task,
            {"execution_authorization": self._authorization(task), "allowed_paths": [str(target)]},
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["metadata"]["worker_result"]["target_path"], str(target))

    def test_subprocess_nonzero_exit(self):
        task = self._task("nonzero")
        command = self._worker("import sys\nsys.exit(7)\n", "nonzero.py")
        result = SubprocessWorkerProvider(command).execute(
            "coder", task, {"execution_authorization": self._authorization(task)}
        )
        self.assertEqual(result["error"], "worker_nonzero_exit")
        self.assertEqual(result["metadata"]["exit_code"], 7)

    def test_subprocess_timeout(self):
        task = self._task("timeout")
        command = self._worker("import time\ntime.sleep(1)\n", "timeout.py")
        result = SubprocessWorkerProvider(command, timeout_seconds=0.01).execute(
            "coder", task, {"execution_authorization": self._authorization(task)}
        )
        self.assertTrue(result["error"].startswith("worker_timeout:"))

    def test_malformed_worker_json(self):
        task = self._task("malformed")
        command = self._worker("print('not-json')\n", "malformed.py")
        result = SubprocessWorkerProvider(command).execute(
            "coder", task, {"execution_authorization": self._authorization(task)}
        )
        self.assertEqual(result["error"], "worker_output_not_json")

    def test_missing_required_worker_result_fields(self):
        task = self._task("missing_fields")
        command = self._worker(
            "import json, sys\np=json.load(sys.stdin)\nprint(json.dumps({'task_id': p['task_id'], 'output': 'x'}))\n",
            "missing_fields.py",
        )
        result = SubprocessWorkerProvider(command).execute(
            "coder", task, {"execution_authorization": self._authorization(task)}
        )
        self.assertEqual(result["error"], "worker_output_contract_invalid")

    def test_returned_target_outside_resolved_declared_scope(self):
        task = self._task("outside")
        outside = self.root / "outside.txt"
        command = self._worker(
            "import json, sys\np=json.load(sys.stdin)\nprint(json.dumps({'task_id': p['task_id'], "
            "'run_id': p['run_id'], 'status': 'success', 'output': 'x', 'target_path': p['outside']}))\n".replace(
                "p['outside']", repr(str(outside))
            ),
            "outside.py",
        )
        allowed = self.root / "outputs" / "outside.txt"
        result = SubprocessWorkerProvider(command).execute(
            "coder",
            task,
            {"execution_authorization": self._authorization(task), "allowed_paths": [str(allowed)]},
        )
        self.assertEqual(result["error"], "worker_target_outside_declared_scope")

    def test_task_run_artifact_verifier_authorization_and_acceptance_linkage(self):
        packet = self._packet(
            "linked",
            human_review={
                "accepted": True,
                "operator_note": "Accepted under canonical test caveats.",
                "verification_caveat_acknowledged": True,
                "provider_caveat_acknowledged": True,
            },
        )
        result = self._run_packet(packet)
        authorization = result["authorization"]
        task = json.loads((self.data_root / "tasks" / "task_linked.json").read_text())
        artifact = json.loads(
            (self.data_root / "artifacts" / f"{result['execution_artifact_id']}.json").read_text()
        )
        verifier_path = next((self.data_root / "verifier_results").glob("task_linked_*.json"))
        verifier = json.loads(verifier_path.read_text())
        acceptance_path = Path(result["human_review_acceptance"]["acceptance_record_path"])
        acceptance = json.loads(acceptance_path.read_text())
        for record in (task, artifact, verifier, acceptance):
            self.assertEqual(record["schema_version"], SCHEMA_VERSION)
        self.assertEqual(task["run_id"], artifact["run_id"])
        self.assertEqual(task["id"], artifact["task_id"])
        self.assertEqual(artifact["artifact_id"], verifier["execution_artifact_id"])
        self.assertEqual(authorization["authorization_id"], artifact["authorization_id"])
        self.assertEqual(authorization["authorization_id"], verifier["authorization_id"])
        self.assertEqual(authorization["authorization_id"], acceptance["authorization_id"])

    def test_human_acceptance_is_persisted(self):
        packet = self._packet(
            "accepted_review",
            human_review={
                "accepted": True,
                "operator_note": "Accept.",
                "verification_caveat_acknowledged": True,
                "provider_caveat_acknowledged": True,
            },
        )
        result = self._run_packet(packet)
        self.assertTrue(result["human_review_acceptance"]["acceptance_record_created"])

    def test_human_rejection_is_persisted_without_reclassifying_execution(self):
        packet = self._packet(
            "rejected_review",
            human_review={"accepted": False, "operator_note": "Reject after inspection."},
        )
        result = self._run_packet(packet)
        self.assertTrue(result["execution_succeeded"])
        self.assertTrue(result["human_review_disposition"]["operator_decision_record_created"])
        self.assertTrue(result["human_review_disposition"]["rejected"])

    def test_invalid_task_json_reconciliation(self):
        tasks = self.data_root / "tasks"
        tasks.mkdir(parents=True)
        (tasks / "bad.json").write_text("{", encoding="utf-8")
        result = reconcile_lifecycle(self.data_root)
        self.assertIn("invalid_task_json", {item["classification"] for item in result["findings"]})

    def _write_task_record(self, suffix, status, artifact_id=""):
        tasks = self.data_root / "tasks"
        tasks.mkdir(parents=True, exist_ok=True)
        record = {
            "schema_version": SCHEMA_VERSION,
            "id": f"task_{suffix}",
            "run_id": f"run_{suffix}",
            "title": "Reconciliation fixture",
            "role": "coder",
            "status": status,
            "dependencies": [],
            "success_criteria": ["fixture"],
            "files_in_scope": [f"outputs/{suffix}.txt"],
            "retry_count": 0,
            "expected_output": "fixture",
            "execution_artifact_id": artifact_id or None,
            "execution_policy": FILESYSTEM_MUTATION_EXECUTION_POLICY,
            "execution_authorization_provenance": None,
        }
        atomic_write_json(tasks / f"task_{suffix}.json", record)

    def test_in_progress_run_reconciliation(self):
        self._write_task_record("in_progress", "in_progress")
        result = reconcile_lifecycle(self.data_root)
        self.assertIn("in_progress_requires_recovery", {item["classification"] for item in result["findings"]})

    def test_missing_artifact_reconciliation(self):
        self._write_task_record("missing_artifact", "execution_failed", "artifact_missing")
        result = reconcile_lifecycle(self.data_root)
        self.assertIn("missing_artifact", {item["classification"] for item in result["findings"]})

    def test_missing_verifier_reconciliation(self):
        self._write_task_record("missing_verifier", "execution_failed", "artifact_present")
        artifacts = self.data_root / "artifacts"
        artifacts.mkdir(parents=True)
        atomic_write_json(
            artifacts / "artifact_present.json",
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_id": "artifact_present",
                "task_id": "task_missing_verifier",
                "run_id": "run_missing_verifier",
            },
        )
        result = reconcile_lifecycle(self.data_root)
        self.assertIn("missing_verifier_result", {item["classification"] for item in result["findings"]})

    def test_missing_human_disposition_reconciliation(self):
        self._write_task_record("missing_disposition", "completed")
        result = reconcile_lifecycle(self.data_root)
        self.assertIn("missing_human_disposition", {item["classification"] for item in result["findings"]})

    def test_unsupported_schema_version_is_rejected(self):
        tasks = self.data_root / "tasks"
        tasks.mkdir(parents=True)
        (tasks / "future.json").write_text(
            json.dumps({"schema_version": SCHEMA_VERSION + 1, "id": "task_future"}),
            encoding="utf-8",
        )
        result = reconcile_lifecycle(self.data_root)
        self.assertIn("unsupported_schema_version", {item["classification"] for item in result["findings"]})

    def test_isolated_data_root_leaves_repository_persistence_unchanged(self):
        import orchestrator.paths as project_paths

        repo_data = project_paths.DATA_DIR
        before = sorted(str(path.relative_to(repo_data)) for path in repo_data.rglob("*") if path.is_file())
        self._run_packet(self._packet("isolated"))
        after = sorted(str(path.relative_to(repo_data)) for path in repo_data.rglob("*") if path.is_file())
        self.assertEqual(before, after)

    def test_cli_end_to_end_success_through_external_temporary_worker(self):
        exit_code, result = self._run_cli(self._packet("cli_success"))
        self.assertEqual(exit_code, 0)
        self.assertTrue(result["execution_succeeded"])
        self.assertEqual(result["execution_provider"], "subprocess_worker")

    def test_cli_denial_and_failure_do_not_create_misleading_completion_records(self):
        denied_code, denied = self._run_cli(
            self._packet("cli_denied", authorization_decision="deny_execution")
        )
        self.assertEqual(denied_code, 1)
        self.assertFalse(denied["accepted"])
        self.assertFalse((self.data_root / "tasks" / "task_cli_denied.json").exists())

        failure_command = self._worker("import sys\nsys.exit(9)\n", "cli_failure.py")
        failed_code, failed = self._run_cli(self._packet("cli_failed"), failure_command)
        self.assertEqual(failed_code, 1)
        self.assertFalse(failed["execution_succeeded"])
        failed_task = json.loads((self.data_root / "tasks" / "task_cli_failed.json").read_text())
        self.assertEqual(failed_task["status"], "execution_failed")
        self.assertFalse((self.data_root / "acceptance_records").exists())

    def test_atomic_write_cleans_temporary_file_after_replace_failure(self):
        target = self.root / "atomic" / "record.json"
        with patch("orchestrator.alpha_runtime.os.replace", side_effect=OSError("replace failed")):
            with self.assertRaises(OSError):
                atomic_write_json(target, {"schema_version": SCHEMA_VERSION})
        self.assertFalse(target.exists())
        self.assertEqual(list(target.parent.glob("*.tmp")), [])

    def test_reconciliation_is_read_only_and_optional_disposition_is_not_required_for_failure(self):
        self._write_task_record("failed_optional", "execution_failed")
        before = (self.data_root / "tasks" / "task_failed_optional.json").read_bytes()
        result = reconcile_lifecycle(self.data_root)
        after = (self.data_root / "tasks" / "task_failed_optional.json").read_bytes()
        self.assertEqual(before, after)
        relevant = [item for item in result["findings"] if item.get("task_id") == "task_failed_optional"]
        self.assertNotIn("missing_human_disposition", {item["classification"] for item in relevant})


if __name__ == "__main__":
    unittest.main()
