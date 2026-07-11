"""Small runtime configuration and durable JSON helpers for the alpha spine."""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = 1


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    """Write one JSON record atomically in the record's own directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def isolated_data_root(data_root: str | Path | None) -> Iterator[Path | None]:
    """Temporarily redirect the canonical spine's JSON stores to ``data_root``."""
    if data_root is None:
        yield None
        return

    root = Path(data_root).resolve()
    import orchestrator.artifact_store as artifact_store
    import orchestrator.current_success_acceptance as acceptance
    import orchestrator.current_success_result_review as review
    import orchestrator.engine as engine
    import orchestrator.execution_authorization as authorization
    import orchestrator.paths as paths
    import orchestrator.run_manager as run_manager
    import orchestrator.state as state

    replacements = {
        (paths, "PROJECT_ROOT"): root.parent,
        (paths, "DATA_DIR"): root,
        (paths, "STATE_DIR"): root / "state",
        (paths, "RUNS_DIR"): root / "runs",
        (paths, "TASKS_DIR"): root / "tasks",
        (paths, "ARTIFACTS_DIR"): root / "artifacts",
        (paths, "VERIFIER_RESULTS_DIR"): root / "verifier_results",
        (state, "STATE_PATH"): root / "state" / "workspace_state.json",
        (run_manager, "RUNS_DIR"): root / "runs",
        (run_manager, "TASKS_DIR"): root / "tasks",
        (artifact_store, "ARTIFACTS_DIR"): root / "artifacts",
        (engine, "VERIFIER_RESULTS_DIR"): root / "verifier_results",
        (authorization, "AUTHORIZATION_RECORDS_DIR"): root / "execution_authorizations",
        (review, "DATA_DIR"): root,
        (review, "ARTIFACTS_DIR"): root / "artifacts",
        (review, "VERIFIER_RESULTS_DIR"): root / "verifier_results",
        (review, "ACCEPTANCE_RECORDS_DIR"): root / "acceptance_records",
        (review, "PACKET_OPERATOR_DECISION_RECORDS_DIR"): root / "packet_operator_decision_records",
        (acceptance, "DATA_DIR"): root,
        (acceptance, "ACCEPTANCE_RECORDS_DIR"): root / "acceptance_records",
    }
    originals = {(module, name): getattr(module, name) for module, name in replacements}
    try:
        for (module, name), value in replacements.items():
            setattr(module, name, value)
        yield root
    finally:
        for (module, name), value in originals.items():
            setattr(module, name, value)


def reconcile_lifecycle(data_root: str | Path) -> dict[str, Any]:
    """Read-only partial-lifecycle detector for alpha JSON records."""
    root = Path(data_root).resolve()
    tasks = root / "tasks"
    artifacts = root / "artifacts"
    verifiers = root / "verifier_results"
    reviews = root / "acceptance_records"
    findings: list[dict[str, str]] = []
    for task_path in sorted(tasks.glob("*.json")) if tasks.exists() else []:
        try:
            task = json.loads(task_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            findings.append({"task_path": str(task_path), "classification": "invalid_task_json"})
            continue
        task_id = str(task.get("id", ""))
        artifact_id = str(task.get("execution_artifact_id", ""))
        if task.get("status") == "in_progress":
            findings.append({"task_id": task_id, "classification": "in_progress_requires_recovery"})
        if artifact_id and not (artifacts / f"{artifact_id}.json").exists():
            findings.append({"task_id": task_id, "classification": "missing_artifact"})
        if artifact_id and not any(verifiers.glob(f"{task_id}_*.json")):
            findings.append({"task_id": task_id, "classification": "missing_verifier_result"})
        dispositions = []
        for review_path in reviews.glob("*.json") if reviews.exists() else []:
            try:
                dispositions.append(json.loads(review_path.read_text(encoding="utf-8")).get("task_id"))
            except json.JSONDecodeError:
                continue
        if task.get("status") == "completed" and task_id not in dispositions:
            findings.append({"task_id": task_id, "classification": "missing_human_disposition"})
    return {"alpha_reconciliation": True, "data_root": str(root), "findings": findings, "healthy": not findings}
