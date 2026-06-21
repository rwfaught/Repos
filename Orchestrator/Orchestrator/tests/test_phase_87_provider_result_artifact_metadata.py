import json

from orchestrator.artifact_store import create_artifact
from orchestrator.paths import ARTIFACTS_DIR
from orchestrator.task_schema import Task


def test_phase_87_artifact_persists_provider_metadata_and_error(tmp_path, monkeypatch):
    monkeypatch.setattr("orchestrator.artifact_store.ARTIFACTS_DIR", tmp_path)

    task = Task(
        id="task_phase87_metadata",
        run_id="run_phase87_metadata",
        title="Persist provider metadata in artifact",
        role="coder",
        status="queued",
        dependencies=[],
        success_criteria=["Provider result metadata is durably inspectable."],
        files_in_scope=["providers/ollama_provider.py"],
        retry_count=0,
    )

    result = {
        "status": "success",
        "output": "bounded model-backed output",
        "provider": "ollama",
        "metadata": {
            "provider_contract": "ollama_generate_v1",
            "model_backed_provider": True,
            "provider_request_attempted": True,
            "runtime_executed": True,
            "model_executed": True,
        },
        "error": None,
    }

    artifact = create_artifact(task, result)

    assert artifact["provider"] == "ollama"
    assert artifact["metadata"]["provider_contract"] == "ollama_generate_v1"
    assert artifact["metadata"]["model_backed_provider"] is True
    assert artifact["metadata"]["runtime_executed"] is True
    assert artifact["metadata"]["model_executed"] is True
    assert artifact["error"] is None

    artifact_path = tmp_path / f"{artifact['artifact_id']}.json"
    persisted = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert persisted["provider"] == "ollama"
    assert persisted["metadata"]["provider_request_attempted"] is True
    assert persisted["metadata"]["runtime_executed"] is True
    assert persisted["metadata"]["model_executed"] is True
    assert persisted["error"] is None