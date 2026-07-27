"""Fixed native-Codex adapter for the Operator Workbench worker protocol.

The canonical subprocess worker supplies one JSON object on stdin.  This
adapter never accepts a browser command, model, or sandbox setting: it invokes
the approved native CLI at the fixed Windows path, confined to the canonical
worker workspace, then emits the exact worker-result envelope expected by the
canonical provider.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


CODEX_BINARY = Path(
    r"C:\Users\accou\.codex\packages\standalone\releases\0.145.0-x86_64-pc-windows-msvc\bin\codex.exe"
)
MAX_CODEX_OUTPUT_CHARS = 20_000


def _payload() -> dict[str, Any]:
    value = json.load(sys.stdin)
    if not isinstance(value, dict):
        raise ValueError("Canonical worker input must be a JSON object.")
    required = ("task_id", "run_id", "objective", "expected_output", "allowed_paths", "worker_workspace", "trust_posture")
    if any(not value.get(key) for key in required):
        raise ValueError("Canonical worker input is missing required fields.")
    if value["trust_posture"] != "trusted_local_unsandboxed":
        raise ValueError("Unsupported worker trust posture.")
    if not isinstance(value["allowed_paths"], list) or len(value["allowed_paths"]) != 1:
        raise ValueError("Workbench Codex adapter supports exactly one allowed path.")
    return value


def _prompt(payload: dict[str, Any], target: Path) -> str:
    return f"""You are the bounded worker for one local coding task. Complete only this task.

Objective: {payload['objective']}
Success criteria: {json.dumps(payload.get('success_criteria', []))}

Create or replace exactly this file: {target}
Its complete UTF-8 text must be exactly:
--- expected text begins ---
{payload['expected_output']}
--- expected text ends ---

Do not read, create, edit, delete, or rename any other file. Do not run git,
network, package, installer, or shell commands unrelated to writing that one
file. Verify the file contents after writing. Respond concisely when done.
"""


def _remove_known_cli_residue(workspace: Path) -> list[str]:
    """Remove only native-CLI control files created in a fresh workbench workspace."""
    removed: list[str] = []
    for name in (".agents", ".git"):
        candidate = workspace / name
        if not candidate.exists() and not candidate.is_symlink():
            continue
        if candidate.is_symlink() or candidate.is_file():
            candidate.unlink()
        elif candidate.is_dir():
            shutil.rmtree(candidate)
        else:
            raise RuntimeError(f"Unsupported native Codex residue type: {candidate}")
        removed.append(name)
    return removed


def main() -> int:
    try:
        payload = _payload()
        workspace = Path(str(payload["worker_workspace"])).resolve()
        target = Path(str(payload["allowed_paths"][0])).resolve()
        if not CODEX_BINARY.is_file():
            raise ValueError(f"Approved native Codex binary is unavailable: {CODEX_BINARY}")
        if not workspace.is_dir() or target.parent != workspace / "workbench_fixtures":
            raise ValueError("Allowed target is outside the Workbench fixture workspace.")
        command = [
            str(CODEX_BINARY), "--ask-for-approval", "never", "exec", "--cd", str(workspace),
            "--sandbox", "workspace-write", "--skip-git-repo-check", "--ephemeral", "--color", "never", _prompt(payload, target),
        ]
        completed = subprocess.run(command, cwd=workspace, capture_output=True, text=True, timeout=3300)
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout)[-MAX_CODEX_OUTPUT_CHARS:]
            raise RuntimeError(f"Native Codex exited {completed.returncode}: {detail}")
        removed_residue = _remove_known_cli_residue(workspace)
        if not target.is_file() or target.read_text(encoding="utf-8") != payload["expected_output"]:
            raise RuntimeError("Native Codex did not produce the exact declared output.")
        print(json.dumps({
            "task_id": payload["task_id"], "run_id": payload["run_id"], "status": "success",
            "output": payload["expected_output"], "changed_paths": [str(target)],
            "adapter_cleanup": {"known_native_cli_residue_removed": removed_residue},
        }))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        print(f"Workbench Codex adapter failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
