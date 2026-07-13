import math
import tempfile
import unittest
from pathlib import Path

from orchestrator.alpha_runtime import atomic_write_json, isolated_data_root, reconcile_lifecycle
from orchestrator.execution_authorization import persist_execution_authorization
from orchestrator.operator_coding_task_packet_cli import _parse_args
from orchestrator.worker_execution_policy import (
    DEFAULT_WHOLE_WORKER_TIMEOUT_SECONDS,
    normalize_worker_execution_policy,
)
from orchestrator.worker_execution_state import (
    finish_worker_execution_state,
    start_worker_execution_state,
    worker_execution_state_path,
)


class WorkerExecutionPolicyStateTests(unittest.TestCase):
    def test_default_policy_is_bounded_and_marks_its_source(self):
        policy = normalize_worker_execution_policy(selection_source="cli_default")
        self.assertEqual(policy["whole_worker_timeout_seconds"], DEFAULT_WHOLE_WORKER_TIMEOUT_SECONDS)
        self.assertEqual(policy["poll_interval_seconds"], 1.0)
        self.assertEqual(policy["selection_source"], "cli_default")

    def test_invalid_whole_worker_timeout_values_are_rejected(self):
        for value in ("", "not-a-number", 0, -1, 9.99, 3600.01, math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_worker_execution_policy(value, selection_source="test")

    def test_cli_timeout_is_before_worker_command_and_is_normalized(self):
        parsed = _parse_args([
            "--packet-json", "packet.json", "--data-root", "data", "--trusted-worker-posture",
            "trusted_local_unsandboxed", "--worker-timeout-seconds", "15", "--worker-command", "worker",
        ])
        self.assertIsNone(parsed[5])
        self.assertEqual(parsed[6]["whole_worker_timeout_seconds"], 15.0)
        after_command = _parse_args([
            "--packet-json", "packet.json", "--data-root", "data", "--trusted-worker-posture",
            "trusted_local_unsandboxed", "--worker-command", "worker", "--worker-timeout-seconds", "15",
        ])
        self.assertIsNotNone(after_command[5])
        self.assertIn("worker_timeout_seconds_must_precede_worker_command", after_command[5]["blocked_conditions"])

    def test_state_has_no_raw_execution_input_and_becomes_terminal(self):
        with tempfile.TemporaryDirectory() as temporary:
            with isolated_data_root(Path(temporary)):
                policy = normalize_worker_execution_policy(10, selection_source="test")
                start_worker_execution_state(task_id="task_state", run_id="run_state", provider="subprocess_worker", pid=123, policy=policy)
                finish_worker_execution_state(task_id="task_state", run_id="run_state", classification="worker_success", termination_state="not_required")
                record = __import__("json").loads(worker_execution_state_path(task_id="task_state", run_id="run_state").read_text())
        self.assertEqual(record["state"], "terminal")
        self.assertEqual(record["terminal_result_classification"], "worker_success")
        self.assertNotIn("payload", record)
        self.assertNotIn("environment", record)

    def test_invalid_policy_cannot_create_authorized_record(self):
        with tempfile.TemporaryDirectory() as temporary:
            with isolated_data_root(Path(temporary)):
                record = persist_execution_authorization(
                    {"authorization_decision": "authorize_execution", "authorization_provenance": "test"},
                    "task_authorization_policy",
                    ["output.txt"],
                    worker_execution_policy={"policy_id": "worker_execution_policy_v1", "whole_worker_timeout_seconds": 0},
                )
        self.assertFalse(record["execution_authorized"])
        self.assertFalse(record["worker_execution_policy_valid"])
        self.assertEqual(record["decision"], "denied")

    def test_reconciliation_reports_state_and_policy_repairs_but_allows_legacy_policy_absence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = normalize_worker_execution_policy(10, selection_source="test")
            alternate = {**policy, "whole_worker_timeout_seconds": 11.0}
            task_id, run_id, authorization_id, artifact_id = "task_reconcile_policy", "run_reconcile_policy", "authorization_reconcile_policy", "artifact_reconcile_policy"
            atomic_write_json(root / "tasks" / f"{task_id}.json", {
                "id": task_id, "run_id": run_id, "status": "execution_failed", "execution_policy": "filesystem_mutation",
                "files_in_scope": ["output.txt"], "execution_artifact_id": artifact_id,
                "worker_execution_policy": policy,
                "execution_authorization_provenance": {"authorization_id": authorization_id, "worker_trust_posture": "trusted_local_unsandboxed"},
                "worker_security": {"trust_posture": "trusted_local_unsandboxed", "workspace_id": "workspace", "workspace_path": "C:/safe", "launch_attempted": True, "workspace_effect_audit": {"passed": True}, "cleanup_status": "confirmed"},
            })
            atomic_write_json(root / "runs" / f"{run_id}.json", {"id": run_id, "worker_security": {"trust_posture": "trusted_local_unsandboxed", "workspace_id": "workspace", "workspace_path": "C:/safe"}})
            atomic_write_json(root / "execution_authorizations" / f"{authorization_id}.json", {"authorization_id": authorization_id, "task_id": task_id, "authorized_scope": ["output.txt"], "decision": "authorized", "worker_trust_posture": "trusted_local_unsandboxed", "worker_execution_policy": policy})
            atomic_write_json(root / "artifacts" / f"{artifact_id}.json", {"artifact_id": artifact_id, "task_id": task_id, "run_id": run_id, "authorization_id": authorization_id, "error": "worker_timeout", "worker_execution_policy": alternate, "metadata": {"worker_execution_policy": alternate}, "worker_security": {"trust_posture": "trusted_local_unsandboxed", "workspace_id": "workspace", "workspace_path": "C:/safe"}})
            atomic_write_json(root / "worker_execution_states" / f"{run_id}__{task_id}.json", {"task_id": task_id, "run_id": run_id, "state": "running", "termination_state": "forced_cleanup_unconfirmed", "worker_execution_policy": policy})
            findings = {item["classification"] for item in reconcile_lifecycle(root)["findings"]}
            self.assertIn("authorization_artifact_policy_mismatch", findings)
            self.assertIn("nonterminal_worker_execution_state_for_terminal_task", findings)
            self.assertIn("timeout_artifact_policy_mismatch", findings)
            self.assertIn("unconfirmed_worker_cleanup", findings)
            (root / "worker_execution_states" / f"{run_id}__{task_id}.json").unlink()
            findings = {item["classification"] for item in reconcile_lifecycle(root)["findings"]}
            self.assertIn("missing_worker_execution_state", findings)
            (root / "tasks" / f"{task_id}.json").write_text('{"id":"legacy","run_id":"legacy_run","status":"queued","execution_policy":"filesystem_mutation","worker_security":{"launch_attempted":false}}', encoding="utf-8")
            findings = {item["classification"] for item in reconcile_lifecycle(root)["findings"]}
        self.assertNotIn("invalid_worker_execution_policy", findings)


if __name__ == "__main__":
    unittest.main()
