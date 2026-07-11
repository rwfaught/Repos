"""Explicit, bounded external-worker adapter; no model/provider policy lives here."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from orchestrator.task_schema import Task
from orchestrator.execution_authorization import validate_execution_authorization
from providers.base import BaseProvider, ProviderResult


class SubprocessWorkerProvider(BaseProvider):
    provider_name = "subprocess_worker"

    def __init__(self, command: list[str], timeout_seconds: float = 30.0) -> None:
        if not command:
            raise ValueError("Subprocess worker command is required.")
        self.command = list(command)
        self.timeout_seconds = timeout_seconds

    def execute(self, role: str, task: Task, context: dict[str, Any] | None = None) -> ProviderResult:
        dispatch_context = context or {}
        authorization_error = validate_execution_authorization(
            dispatch_context.get("execution_authorization"),
            task_id=task.id,
            files_in_scope=task.files_in_scope,
        )
        if authorization_error:
            return {
                "status": "error",
                "output": None,
                "provider": self.provider_name,
                "metadata": {"command": self.command, "task_id": task.id},
                "error": authorization_error,
            }
        payload = {
            "task_id": task.id,
            "run_id": task.run_id,
            "role": role,
            "title": task.title,
            "files_in_scope": task.files_in_scope,
            "success_criteria": task.success_criteria,
            "expected_output": task.expected_output,
            "allowed_paths": list(dispatch_context.get("allowed_paths", [])),
        }
        try:
            completed = subprocess.run(self.command, input=json.dumps(payload), text=True, capture_output=True, timeout=self.timeout_seconds, check=False)
        except subprocess.TimeoutExpired as error:
            return {"status": "error", "output": None, "provider": self.provider_name, "metadata": {"command": self.command, "timeout_seconds": self.timeout_seconds}, "error": f"worker_timeout: {error}"}
        metadata = {"command": self.command, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
        if completed.returncode != 0:
            return {"status": "error", "output": completed.stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_nonzero_exit"}
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError:
            return {"status": "error", "output": completed.stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_output_not_json"}
        if (
            not isinstance(result, dict)
            or result.get("task_id") != task.id
            or result.get("run_id") != task.run_id
            or result.get("status") != "success"
            or not isinstance(result.get("output"), str)
            or not isinstance(result.get("target_path"), str)
            or not result.get("target_path", "").strip()
        ):
            return {"status": "error", "output": completed.stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_output_contract_invalid"}
        resolved = Path(result["target_path"]).resolve()
        allowed = [Path(item).resolve() for item in dispatch_context.get("allowed_paths", [])]
        if resolved not in allowed:
            return {"status": "error", "output": completed.stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_target_outside_declared_scope"}
        return {"status": "success", "output": result["output"], "provider": self.provider_name, "metadata": {**metadata, "worker_result": result}, "error": None}
