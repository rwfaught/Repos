import json
from datetime import datetime, timezone
from uuid import uuid4

from orchestrator.paths import ARTIFACTS_DIR, record_path
from orchestrator.task_schema import Task


def artifact_path(artifact_id: str):
    return record_path(ARTIFACTS_DIR, artifact_id, label="artifact id")


def create_artifact(task: Task, result: dict) -> dict:
    artifact_id = f"artifact_{uuid4().hex[:8]}"
    artifact = {
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

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    path = artifact_path(artifact_id)
    path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    return artifact
