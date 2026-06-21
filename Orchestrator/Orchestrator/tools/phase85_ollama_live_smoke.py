from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOW_ENV = "ORCH_PHASE85_ALLOW_LIVE_OLLAMA"
DEFAULT_MODEL = "llama3.2"
DEFAULT_API_URL = "http://127.0.0.1:11434/api/generate"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_repo_root_on_path() -> None:
    root = str(_repo_root())
    if root not in sys.path:
        sys.path.insert(0, root)


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _live_allowed(env: dict[str, str] | None = None) -> bool:
    env_data = env if env is not None else os.environ
    return env_data.get(ALLOW_ENV, "").strip() == "YES"


def _blocked_payload() -> dict[str, Any]:
    return {
        "phase": 85,
        "status": "blocked",
        "reason": f"Live Ollama smoke is blocked unless {ALLOW_ENV}=YES is set.",
        "live_provider_execution": False,
        "model_execution": False,
        "runtime_execution": False,
        "task_persistence": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def _build_task(prompt: str):
    _ensure_repo_root_on_path()
    from orchestrator.task_schema import Task

    return Task(
        id="task_phase85_ollama_live_smoke_nonpersistent",
        run_id="run_phase85_ollama_live_smoke_nonpersistent",
        title="Phase 85 guarded live Ollama smoke",
        role="reviewer",
        status="queued",
        dependencies=[],
        success_criteria=[
            "Return a short bounded response.",
            "Do not mutate repository files.",
            "Do not claim broad semantic correctness.",
        ],
        files_in_scope=[],
        retry_count=0,
        expected_output=None,
    )


def run_live_smoke(model: str, api_url: str, prompt: str) -> dict[str, Any]:
    _ensure_repo_root_on_path()
    from providers.ollama_provider import OllamaProvider

    task = _build_task(prompt=prompt)

    result = OllamaProvider().execute(
        role="reviewer",
        task=task,
        context={
            "role_prompt": (
                "You are performing a bounded Orchestrator Phase 85 live provider smoke. "
                "Return one short sentence only. Do not mutate files."
            ),
            "ollama_model": model,
            "ollama_api_url": api_url,
        },
    )

    metadata = result.get("metadata", {}) if isinstance(result, dict) else {}

    return {
        "phase": 85,
        "status": result.get("status") if isinstance(result, dict) else "error",
        "provider": result.get("provider") if isinstance(result, dict) else "ollama",
        "output": result.get("output") if isinstance(result, dict) else None,
        "error": result.get("error") if isinstance(result, dict) else "Provider returned non-dict result.",
        "metadata": metadata,
        "live_provider_execution": True,
        "model_execution": bool(metadata.get("model_executed")),
        "runtime_execution": bool(metadata.get("runtime_executed")),
        "task_persistence": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 85 guarded live Ollama smoke harness.")
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", DEFAULT_MODEL))
    parser.add_argument("--api-url", default=os.getenv("OLLAMA_API_URL", DEFAULT_API_URL))
    parser.add_argument(
        "--prompt",
        default="Return exactly this sentence: PHASE85_LIVE_OLLAMA_SMOKE_RESPONSE",
    )

    args = parser.parse_args(argv)

    if not _live_allowed():
        _emit(_blocked_payload())
        return 2

    payload = run_live_smoke(model=args.model, api_url=args.api_url, prompt=args.prompt)
    _emit(payload)

    return 0 if payload.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())