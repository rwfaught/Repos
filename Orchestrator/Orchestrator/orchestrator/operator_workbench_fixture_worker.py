"""Deterministic worker used only for Workbench tests and the isolated proof fixture."""
from __future__ import annotations
import json
import sys
from pathlib import Path

payload = json.load(sys.stdin)
for target in payload["allowed_paths"]:
    path = Path(target); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(payload["expected_output"], encoding="utf-8")
print(json.dumps({"task_id": payload["task_id"], "run_id": payload["run_id"], "status": "success", "output": payload["expected_output"], "changed_paths": payload["allowed_paths"]}))
