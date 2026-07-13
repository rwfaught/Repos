"""Trusted-local subprocess adapter with bounded observation and durable state."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from orchestrator.execution_authorization import validate_execution_authorization
from orchestrator.task_schema import Task
from orchestrator.trusted_worker_security import (
    WorkerSecurityError, audit_workspace_effects, inventory_workspace,
    resolve_workspace_target, validate_trusted_worker_prelaunch_state,
    validate_trust_posture,
)
from orchestrator.worker_execution_policy import (
    normalize_worker_execution_policy, policies_match,
    validate_normalized_worker_execution_policy,
)
from orchestrator.worker_execution_state import (
    finish_worker_execution_state, observe_worker_execution_state,
    start_worker_execution_state, update_worker_execution_state,
)
from providers.base import BaseProvider, ProviderResult


class SubprocessWorkerProvider(BaseProvider):
    provider_name = "subprocess_worker"

    def __init__(
        self,
        command: list[str],
        timeout_seconds: float | None = None,
        *,
        worker_execution_policy: dict[str, Any] | None = None,
    ) -> None:
        if not command:
            raise ValueError("Subprocess worker command is required.")
        if timeout_seconds is not None and worker_execution_policy is not None:
            raise ValueError("Use timeout_seconds or worker_execution_policy, not both.")
        self.command = list(command)
        if worker_execution_policy is not None:
            self.worker_execution_policy = validate_normalized_worker_execution_policy(worker_execution_policy)
        else:
            self.worker_execution_policy = normalize_worker_execution_policy(
                timeout_seconds,
                selection_source=("direct_timeout_seconds" if timeout_seconds is not None else "provider_default"),
            )
        # Compatibility for direct callers that inspect the previous attribute.
        self.timeout_seconds = self.worker_execution_policy["whole_worker_timeout_seconds"]

    def _error(self, error: str, metadata: dict[str, Any]) -> ProviderResult:
        return {"status": "error", "output": None, "provider": self.provider_name, "metadata": metadata, "error": error}

    def _terminate_descendants(
        self, process: subprocess.Popen[str], task: Task, states_dir: Path, *, state_available: bool = True
    ) -> tuple[str, str, str]:
        """Use a cooperative/process-group request first, then bounded tree cleanup."""
        policy = self.worker_execution_policy
        graceful_detail = ""
        try:
            if state_available:
                update_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, termination_state="graceful_requested")
            if os.name == "nt":
                ctrl_break = getattr(signal, "CTRL_BREAK_EVENT", None)
                if ctrl_break is not None:
                    process.send_signal(ctrl_break)
                    graceful_detail = "windows_ctrl_break"
                else:
                    process.terminate()
                    graceful_detail = "windows_direct_terminate"
            else:
                os.killpg(process.pid, signal.SIGTERM)
                graceful_detail = "process_group_sigterm"
            try:
                process.wait(timeout=policy["graceful_termination_seconds"])
                return "confirmed", graceful_detail, "graceful_terminated"
            except subprocess.TimeoutExpired:
                pass
        except (OSError, subprocess.SubprocessError) as error:
            graceful_detail = f"graceful_{error.__class__.__name__}"

        try:
            if state_available:
                update_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, termination_state="forced_cleanup_requested")
            if os.name == "nt":
                cleanup = subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True,
                    text=True, timeout=policy["forced_cleanup_confirmation_seconds"], check=False,
                )
                detail = f"{graceful_detail}; taskkill_exit={cleanup.returncode}"
            else:
                os.killpg(process.pid, signal.SIGKILL)
                detail = f"{graceful_detail}; process_group_sigkill"
            process.wait(timeout=policy["forced_cleanup_confirmation_seconds"])
            return "confirmed", detail, "forced_cleanup_confirmed"
        except (OSError, subprocess.SubprocessError) as error:
            return "unconfirmed", f"{graceful_detail}; {error.__class__.__name__}: {error}", "forced_cleanup_unconfirmed"

    @staticmethod
    def _reader(stream: Any, capture: dict[str, Any], limit: int) -> None:
        try:
            buffered = getattr(stream, "buffer", stream)
            while True:
                read1 = getattr(buffered, "read1", None)
                chunk = read1(4096) if callable(read1) else buffered.read(4096)
                if not chunk:
                    return
                if isinstance(chunk, bytes):
                    chunk = chunk.decode("utf-8", errors="replace")
                encoded_size = len(chunk.encode("utf-8", errors="replace"))
                remaining = max(0, limit - capture["size"])
                if remaining:
                    kept = chunk.encode("utf-8", errors="replace")[:remaining].decode("utf-8", errors="ignore")
                    capture["parts"].append(kept)
                    capture["size"] += len(kept.encode("utf-8", errors="replace"))
                if encoded_size > remaining:
                    capture["exceeded"] = True
        finally:
            try:
                stream.close()
            except (OSError, ValueError):
                pass

    def _wait_with_observation(self, process: subprocess.Popen[str], task: Task, states_dir: Path) -> tuple[str, str, str, str, str, str, bool]:
        """Drain both pipes on reader threads while the main thread observes a deadline."""
        policy = self.worker_execution_policy
        stdout_capture = {"parts": [], "size": 0, "exceeded": False}
        stderr_capture = {"parts": [], "size": 0, "exceeded": False}
        readers = [
            threading.Thread(target=self._reader, args=(process.stdout, stdout_capture, policy["max_output_bytes"])),
            threading.Thread(target=self._reader, args=(process.stderr, stderr_capture, policy["max_output_bytes"])),
        ]
        for reader in readers:
            reader.start()
        deadline = time.monotonic() + policy["whole_worker_timeout_seconds"]
        outcome, cleanup_status, cleanup_detail, termination_state = "completed", "not_required", "", "not_required"
        while process.poll() is None:
            observe_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir)
            if stdout_capture["exceeded"] or stderr_capture["exceeded"]:
                outcome = "output_exceeded"
                cleanup_status, cleanup_detail, termination_state = self._terminate_descendants(process, task, states_dir)
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                outcome = "timeout"
                cleanup_status, cleanup_detail, termination_state = self._terminate_descendants(process, task, states_dir)
                break
            try:
                # wait() returns immediately on completion and sleeps no more than one bounded poll interval.
                process.wait(timeout=min(policy["poll_interval_seconds"], remaining))
            except subprocess.TimeoutExpired:
                continue
        if outcome != "completed":
            for stream in (process.stdout, process.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
        for reader in readers:
            reader.join(timeout=policy["poll_interval_seconds"])
        if outcome == "completed" and (stdout_capture["exceeded"] or stderr_capture["exceeded"]):
            outcome = "output_exceeded"
        if any(reader.is_alive() for reader in readers) and outcome == "completed":
            outcome = "output_incomplete"
        readers_alive = any(reader.is_alive() for reader in readers)
        return (
            outcome,
            "".join(stdout_capture["parts"]),
            "".join(stderr_capture["parts"]),
            cleanup_detail,
            termination_state,
            cleanup_status,
            readers_alive,
        )

    def execute(self, role: str, task: Task, context: dict[str, Any] | None = None) -> ProviderResult:
        dispatch_context = context or {}
        authorization_error = validate_execution_authorization(
            dispatch_context.get("execution_authorization"), task_id=task.id, files_in_scope=task.files_in_scope,
        )
        base_metadata: dict[str, Any] = {"command": self.command, "task_id": task.id, "worker_execution_policy": self.worker_execution_policy}
        if authorization_error:
            return self._error(authorization_error, base_metadata)
        authorization = dispatch_context.get("execution_authorization")
        # Direct legacy callers can supply older authorization records; canonical
        # dispatch always persists and verifies the snapshot before launch.
        if "worker_execution_policy" in (authorization or {}) and not policies_match((authorization or {}).get("worker_execution_policy"), self.worker_execution_policy):
            return self._error("execution_authorization_policy_mismatch", base_metadata)

        worker_security = dict(dispatch_context.get("worker_security") or task.worker_security or {})
        posture_error = validate_trust_posture(worker_security.get("trust_posture"))
        if posture_error:
            return self._error(posture_error, {**base_metadata, "worker_security": worker_security})
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

        payload = {"task_id": task.id, "run_id": task.run_id, "role": role, "title": task.title, "objective": task.title,
                   "files_in_scope": task.files_in_scope, "success_criteria": task.success_criteria, "expected_output": task.expected_output,
                   "allowed_paths": [str(path) for path in allowed], "worker_workspace": str(workspace), "trust_posture": worker_security["trust_posture"]}
        popen_args: dict[str, Any] = {"stdin": subprocess.PIPE, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "text": True, "cwd": str(workspace)}
        if os.name == "nt": popen_args["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        else: popen_args["start_new_session"] = True
        try:
            final_allowed = validate_trusted_worker_prelaunch_state(worker_security, task.files_in_scope)
            if [str(path) for path in final_allowed] != [str(path) for path in allowed]:
                raise WorkerSecurityError("worker_prelaunch_path_state_unsafe", "Worker targets changed before launch.")
            process: subprocess.Popen[str] = subprocess.Popen(self.command, **popen_args)
        except WorkerSecurityError as error:
            worker_security.update({"launch_attempted": False, "cleanup_status": "not_started"})
            return self._error(error.code, {**base_metadata, "worker_security": worker_security})
        except OSError as error:
            worker_security.update({"launch_attempted": False, "cleanup_status": "not_started"})
            return self._error("worker_launch_failed", {**base_metadata, "worker_security": worker_security, "launch_error": error.__class__.__name__})

        worker_security.update({"launch_attempted": True, "workspace_path": str(workspace)})
        states_dir = workspace.parent.parent / "worker_execution_states"
        try:
            start_worker_execution_state(task_id=task.id, run_id=task.run_id, provider=self.provider_name, pid=process.pid, policy=self.worker_execution_policy, states_dir=states_dir)
        except OSError as error:
            cleanup_status, cleanup_detail, termination_state = self._terminate_descendants(
                process, task, states_dir, state_available=False
            )
            for stream in (process.stdin, process.stdout, process.stderr):
                try:
                    stream.close()
                except (OSError, ValueError):
                    pass
            worker_security.update({
                "cleanup_status": cleanup_status,
                "cleanup_detail": cleanup_detail,
                "start_state_error": error.__class__.__name__,
            })
            return self._error(
                "worker_execution_state_persistence_failed",
                {**base_metadata, "worker_security": worker_security, "launch_error": error.__class__.__name__},
            )
        try:
            assert process.stdin is not None
            process.stdin.write(json.dumps(payload)); process.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        outcome, stdout, stderr, cleanup_detail, termination_state, cleanup_status, readers_alive = self._wait_with_observation(process, task, states_dir)
        metadata = {**base_metadata, "exit_code": process.returncode, "stdout": stdout, "stderr": stderr, "reader_threads_alive": readers_alive, "worker_security": worker_security}
        if outcome in {"timeout", "output_exceeded"}:
            worker_security.update({"cleanup_status": cleanup_status, "cleanup_detail": cleanup_detail})
            if cleanup_status == "confirmed":
                try: worker_security["workspace_effect_audit"] = audit_workspace_effects(before, inventory_workspace(workspace), task.files_in_scope)
                except WorkerSecurityError as error: worker_security["workspace_effect_audit_error"] = error.code
            code = "worker_timeout" if outcome == "timeout" else "worker_output_capture_exceeded"
            if cleanup_status == "unconfirmed": code = "worker_descendant_cleanup_unconfirmed"
            finish_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, classification=code, termination_state=termination_state)
            return self._error(code, metadata)
        if outcome == "output_incomplete":
            finish_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, classification="worker_output_capture_incomplete", termination_state="not_required")
            return self._error("worker_output_capture_incomplete", metadata)

        worker_security["cleanup_status"] = "not_required"
        try:
            worker_security["workspace_effect_audit"] = audit_workspace_effects(before, inventory_workspace(workspace), task.files_in_scope)
        except WorkerSecurityError as error:
            worker_security["workspace_effect_audit_error"] = error.code
            finish_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, classification=error.code, termination_state="not_required")
            return self._error(error.code, metadata)
        if process.returncode != 0:
            finish_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, classification="worker_nonzero_exit", termination_state="not_required")
            return {"status": "error", "output": stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_nonzero_exit"}
        if not worker_security["workspace_effect_audit"]["passed"]:
            finish_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, classification="worker_undeclared_workspace_mutation", termination_state="not_required")
            return self._error("worker_undeclared_workspace_mutation", metadata)
        try: result = json.loads(stdout)
        except json.JSONDecodeError:
            finish_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, classification="worker_output_not_json", termination_state="not_required")
            return {"status": "error", "output": stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_output_not_json"}
        valid = isinstance(result, dict) and result.get("task_id") == task.id and result.get("run_id") == task.run_id and result.get("status") == "success" and isinstance(result.get("output"), str) and isinstance(result.get("changed_paths"), list)
        reported_paths = result.get("changed_paths", []) if isinstance(result, dict) else []
        valid = valid and bool(reported_paths) and all(isinstance(path, str) and path.strip() for path in reported_paths) and len(set(reported_paths)) == len(reported_paths)
        if not valid:
            finish_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, classification="worker_result_mismatch", termination_state="not_required")
            return {"status": "error", "output": stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_result_mismatch"}
        allowed_paths = [str(path) for path in allowed]
        if any(path not in allowed_paths for path in reported_paths):
            finish_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, classification="worker_target_outside_declared_scope", termination_state="not_required")
            return {"status": "error", "output": stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_target_outside_declared_scope"}
        audit_changed_paths = worker_security["workspace_effect_audit"].get("changed_paths", [])
        actual_changed_paths = [str(path) for declared_path, path in zip(task.files_in_scope, allowed) if declared_path in audit_changed_paths]
        if reported_paths != actual_changed_paths:
            finish_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, classification="worker_declared_changes_mismatch", termination_state="not_required")
            return {"status": "error", "output": stdout, "provider": self.provider_name, "metadata": metadata, "error": "worker_declared_changes_mismatch"}
        finish_worker_execution_state(task_id=task.id, run_id=task.run_id, states_dir=states_dir, classification="worker_success", termination_state="not_required")
        return {"status": "success", "output": result["output"], "provider": self.provider_name, "metadata": {**metadata, "worker_result": result}, "error": None}
