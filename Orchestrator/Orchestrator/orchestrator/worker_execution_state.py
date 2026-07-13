"""Durable, generic state records for launched subprocess workers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import time

from orchestrator.alpha_runtime import SCHEMA_VERSION, atomic_write_json, load_json_record
from orchestrator.paths import DATA_DIR, record_path


WORKER_EXECUTION_STATES_DIR = DATA_DIR / "worker_execution_states"


def _write(path: Path, record: dict[str, Any]) -> None:
    """Retry short Windows replacement contention without weakening durability."""
    for attempt in range(3):
        try:
            atomic_write_json(path, record)
            return
        except PermissionError:
            if attempt == 2:
                raise
            time.sleep(0.02 * (attempt + 1))


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def worker_execution_state_id(*, task_id: str, run_id: str) -> str:
    return f"{run_id}__{task_id}"


def worker_execution_state_path(*, task_id: str, run_id: str, states_dir: Path | None = None) -> Path:
    return record_path(
        states_dir or WORKER_EXECUTION_STATES_DIR,
        worker_execution_state_id(task_id=task_id, run_id=run_id),
        label="worker execution state id",
    )


def start_worker_execution_state(*, task_id: str, run_id: str, provider: str, pid: int, policy: dict[str, Any], states_dir: Path | None = None) -> dict[str, Any]:
    now = _timestamp()
    record = {
        "schema_version": SCHEMA_VERSION,
        "state_id": worker_execution_state_id(task_id=task_id, run_id=run_id),
        "task_id": task_id,
        "run_id": run_id,
        "provider": provider,
        "pid": int(pid),
        "state": "running",
        "started_at": now,
        "last_observed_alive_at": now,
        "worker_execution_policy": dict(policy),
        "termination_state": "not_requested",
        "terminal_result_classification": "",
    }
    _write(worker_execution_state_path(task_id=task_id, run_id=run_id, states_dir=states_dir), record)
    return record


def update_worker_execution_state(*, task_id: str, run_id: str, states_dir: Path | None = None, **changes: Any) -> dict[str, Any]:
    path = worker_execution_state_path(task_id=task_id, run_id=run_id, states_dir=states_dir)
    record = load_json_record(path, record_type="worker_execution_state")
    record.update(changes)
    _write(path, record)
    return record


def observe_worker_execution_state(*, task_id: str, run_id: str, states_dir: Path | None = None) -> dict[str, Any]:
    return update_worker_execution_state(
        task_id=task_id,
        run_id=run_id,
        states_dir=states_dir,
        last_observed_alive_at=_timestamp(),
    )


def finish_worker_execution_state(*, task_id: str, run_id: str, classification: str, termination_state: str, states_dir: Path | None = None) -> dict[str, Any]:
    return update_worker_execution_state(
        task_id=task_id,
        run_id=run_id,
        states_dir=states_dir,
        state="terminal",
        termination_state=termination_state,
        terminal_result_classification=classification,
    )
