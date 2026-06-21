import json
from typing import Any, Dict

from orchestrator.paths import STATE_DIR

STATE_PATH = STATE_DIR / "workspace_state.json"


def _default_state() -> Dict[str, Any]:
    return {
        "workspace_initialized": False,
        "active_run_id": None,
    }


def load_state() -> Dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return _default_state()


def save_state(state: Dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
