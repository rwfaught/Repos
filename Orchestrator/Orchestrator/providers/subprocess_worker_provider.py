"""Trusted-local-unsandboxed subprocess adapter for canonical alpha work.

The operator selects a trusted local command.  This module controls its
workspace and audits that workspace, but it does not sandbox arbitrary process
effects outside that workspace.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
from pathlib import Path
from typing import Any

from orchestrator.execution_authorization import validate_execution_authorization
from orchestrator.task_schema import Task
from orchestrator.trusted_worker_security import (
    WorkerSecurityError,
    audit_workspace_effects,
    inventory_workspace,
    resolve_workspace_target,
    validate_trust_posture,
)
from providers.base import BaseProvider, ProviderResult


class SubprocessWorkerProvider(BaseProvider):
    provider_name = "subprocess_worker"

    def __init__(self, command: list[str], timeout_seconds: float = 30.0) -> None:
        if not command:
            raise ValueError("Subprocess worker command is required.")
        self.command = list(command)
        self.timeout_seconds = timeout_seconds

    def _error(self, error: str, metadata: dict[str, Any]) -> ProviderResult:
        return {"status": "error", "output": None, "provider": self.provider_name, "metadata": metadata, "error": error}

    def _terminate_descendants(self, process: subprocess.Popen[str]) -> tuple[str, str]:
        """Attempt bounded tree cleanup; return status and implementation detail."""
        try:
            if os.name == "nt":
                cleanup = subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    capture_output=True,
                    text=True,
                    timeout=2.0,
                    check=False,
                )
                try:
                    process.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    return "unconfirmed", f"taskkill_exit={cleanup.returncode}; direct_process_wait_timeout"
                return "confirmed", f"taskkill_exit={cleanup.returncode}"
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=1.0)
                return "confirmed", "process_group_sigterm"
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=1.0)
                return "confirmed", "process_group_sigkill"
        except (OSError, subprocess.SubprocessError) as error:
            return "unconfirmed", f"{error.__class__.__name__}: {error}"

    def execute(self, role: str, task: Task, context: dict[str, Any] | None = None) -> ProviderResult:
        dispatch_context = context or {}
        authorization_error = validate_execution_authorization(
            dispatch_context.get("execution_authorization"),
            task_id=task.id,
            files_in_scope=task.files_in_scope,
        )
        base_metadata: dict[str, Any] = {"command": self.command, "task_id": task.id}
        if authorization_error:
            return self._error(authorization_error, base_metadata)

        worker_security = dict(dispatch_context.get("worker_security") or task.worker_security or {})
        posture_error = validate_trust_posture(worker_security.get("trust_posture"))
        if posture_error:
            return self._error(posture_error, {**base_metadata, "worker_security": worker_security})
        authorization = dispatch_context.get("execution_authorization")
        if not isinstance(authorization, dict) or authorization.get("worker_trust_posture") != worker_security["trust_posture"]:
            return self._error("worker_trust_posture_mismatch", {**base_metadata, "worker_security": worker_security})

        try:
            workspace = Path(str(worker_security.get("workspace_path", "")))
            if not workspace.is_dir():
                raise WorkerSecurityError("worker_workspace_creation_failed", "Worker workspace is unavailable.")
            allowed = [resolve_workspace_target(worker_security, declared) for declared in task.files_in_scope]
            if [str(path) for path in allowed] != list(dispatch_context.get("allowed_paths", [])):
                raise WorkerSecurityError("worker_declared_path_unsafe", "Engine targets do not match safe workspace mappings.")
            before = inventory_workspace(workspace)
        except WorkerSecurityError as error:
            worker_security.update({"launch_attempted": False, "cleanup_status": "not_started"})
            return self._error(error.code, {**base_metadata, "worker_security": worker_security})

        payload = {
            "task_id": task.id,
            "run_id": task.run_id,
            "role": role,
            "title": task.title,
            "files_in_scope": task.files_in_scope,
            "success_criteria": task.success_criteria,
            "expected_output": task.expected_output,
            "allowed_paths": [str(path) for path in allowed],
            "worker_workspace": str(workspace),
            "trust_posture": worker_security["trust_posture"],
        }
        popen_args: dict[str, Any] = {
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
            "cwd": str(workspace),
        }
        if os.name == "nt":
            popen_args["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        else:
            popen_args["start_new_session"] = True
        try:
            process: subprocess.Popen[str] = subprocess.Popen(self.command, **popen_args)
        except OSError as error:
            worker_security.update({"launch_attempted": False, "cleanup_status": "not_started"})
            return self._error("worker_launch_failed", {**base_metadata, "worker_security": worker_security, "launch_error": error.__class__.__name__})

        worker_security["launch_attempted"] = True
        worker_security["workspace_path"] = str(workspace)
        try:
            stdout, stderr = process.communicate(json.dumps(payload), timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired:
            cleanup_status, cleanup_detail = self._terminate_descendants(process)
            if cleanup_status == "confirmed":
                try:
                    after = inventory_workspace(workspace)
                    worker_security["workspace_effect_audit"] = audit_workspace_effects(before, after, task.files_in_scope)
                except WorkerSecurityError as error:
                    worker_security["workspace_effect_audit_error"] = error.code
            else:
                worker_security["workspace_effect_audit_status"] = "unavailable_unconfirmed_cleanup"
            worker_security.update({"cleanup_status": cleanup_status, "cleanup_detail": cleanup_detail})
            code = "worker_timeout" if cleanup_status == "confirmed" else "worker_descendant_cleanup_unconfirmed"
            return self._error(code, {**base_metadata, "timeout_seconds": self.timeout_seconds, "worker_security": worker_security})

        worker_security["cleanup_status"] = "not_required"
        metadata = {**base_metadata, "exit_code": process.returncode, "stdout": stdout, "stderr": stderr}
        try:
            after = inventory_workspace(workspace)
            audit = audit_workspace_effects(before, after, task.files_in_scope)
            worker_security["workspace_effect_audit"] = audit
        except WorkerSecurityError as error:
            worker_security["workspace_effect_audit_error"] = error.code
            return self._error(error.code, {**metadata, "worker_security": worker_security})
        metadata["worker_security"] = worker_security
        if process.returncode != 0:
            return {"status": "error", "output": stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_nonzero_exit"}
        if not worker_security["workspace_effect_audit"]["passed"]:
            return self._error("worker_undeclared_workspace_mutation", metadata)
        try:
            result = json.loads(stdout)
        except json.JSONDecodeError:
            return {"status": "error", "output": stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_output_not_json"}
        if (
            not isinstance(result, dict)
            or result.get("task_id") != task.id
            or result.get("run_id") != task.run_id
            or result.get("status") != "success"
            or not isinstance(result.get("output"), str)
            or not isinstance(result.get("target_path"), str)
            or not result.get("target_path", "").strip()
        ):
            return {"status": "error", "output": stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_result_mismatch"}
        try:
            reported = Path(result["target_path"])
            if reported != allowed[0]:
                return {"status": "error", "output": stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_target_outside_declared_scope"}
        except OSError:
            return {"status": "error", "output": stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_result_mismatch"}
        return {"status": "success", "output": result["output"], "provider": self.provider_name, "metadata": {**metadata, "worker_result": result}, "error": None}
