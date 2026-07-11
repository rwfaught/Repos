from datetime import datetime, timezone
from uuid import uuid4

from orchestrator.paths import ARTIFACTS_DIR, record_path
from orchestrator.alpha_runtime import SCHEMA_VERSION, atomic_write_json
from orchestrator.task_schema import Task


def artifact_path(artifact_id: str):
    return record_path(ARTIFACTS_DIR, artifact_id, label="artifact id")


def create_artifact(task: Task, result: dict) -> dict:
    artifact_id = f"artifact_{uuid4().hex[:8]}"
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "task_id": task.id,
        "run_id": task.run_id,
        "role": task.role,
        "execution_policy": task.execution_policy,
        "requires_causal_change": task.requires_causal_change,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": result.get("status", "unknown"),
        "output": result.get("output"),
        "provider": result.get("provider"),
        "metadata": result.get("metadata") if isinstance(result.get("metadata"), dict) else {},
        "error": result.get("error"),
    }

    path = artifact_path(artifact_id)
    atomic_write_json(path, artifact)
    return artifact
