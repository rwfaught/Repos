"""CLI/file-input adapter for operator coding task packets.

This module is a standard-library-only adapter over the Phase 274 packet
surface. It reads one local JSON packet file and prints deterministic JSON.
It does not add provider, model, runtime, platform, service, API, UI,
general_answer, scheduler, connector, or production behavior.
"""

from __future__ import annotations

import json
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any, Sequence

from orchestrator.operator_coding_task_packet import run_operator_coding_task_packet
from orchestrator.packet_cli_residue_guard import inspect_packet_cli_generated_residue


_NO_ACTIVITY_FLAGS = {
    "model_executed": False,
    "runtime_executed": False,
    "platform_invoked": False,
    "live_provider_invoked": False,
    "ollama_invoked": False,
    "openclaw_invoked": False,
    "hermes_invoked": False,
    "discord_invoked": False,
    "installer_invoked": False,
    "autonomous_ai_coding_claimed": False,
    "production_readiness_claimed": False,
    "semantic_correctness_claimed": False,
}

_NON_PROOFS = [
    "no_semantic_correctness_proof",
    "no_live_provider_model_proof",
    "no_runtime_platform_proof",
    "no_autonomous_ai_coding_proof",
    "no_production_readiness_proof",
    "no_service_api_ui_proof",
    "no_general_answer_resumption",
    "local_file_is_deterministic_local_behavior_not_model_backed_generation",
]


def _blocked(
    *,
    blocked_conditions: list[str],
    detail: str = "",
    missing_requirements: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "operator_coding_task_packet_cli_surface": True,
        "accepted": False,
        "blocked": True,
        "blocked_conditions": sorted(set(blocked_conditions)),
        "missing_requirements": sorted(set(missing_requirements or [])),
        "detail": detail,
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        "non_proofs": list(_NON_PROOFS),
    }


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _read_packet_json(path_text: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    try:
        raw_text = Path(path_text).read_text(encoding="utf-8-sig")
    except OSError as error:
        return None, _blocked(
            blocked_conditions=["packet_json_file_unreadable"],
            detail=f"Could not read packet JSON file: {error.__class__.__name__}.",
            missing_requirements=["packet_json"],
        )

    try:
        value = json.loads(raw_text)
    except json.JSONDecodeError as error:
        return None, _blocked(
            blocked_conditions=["malformed_packet_json"],
            detail=f"Malformed packet JSON: {error.msg}.",
            missing_requirements=["valid_json_object"],
        )

    if not isinstance(value, dict):
        return None, _blocked(
            blocked_conditions=["packet_json_must_be_object"],
            detail="Operator coding task packet JSON must be an object.",
            missing_requirements=["json_object_packet"],
        )

    return value, None


def _parse_args(argv: Sequence[str]) -> tuple[str, str, dict[str, Any] | None]:
    args = tuple(argv)
    if len(args) == 2 and args[0] == "--packet-json" and args[1]:
        return "packet_json", args[1], None
    if len(args) == 1 and args[0] == "--residue-guard":
        return "residue_guard", "", None
    return "", "", _blocked(
        blocked_conditions=["unsupported_or_missing_cli_arguments"],
        detail="Usage: python -m orchestrator.operator_coding_task_packet_cli --packet-json <path> | --residue-guard",
        missing_requirements=["packet_json_path"],
    )


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    mode, packet_path, argument_error = _parse_args(args)
    if argument_error is not None:
        _print_json(argument_error)
        return 2

    if mode == "residue_guard":
        _print_json(inspect_packet_cli_generated_residue())
        return 0

    packet, read_error = _read_packet_json(packet_path)
    if read_error is not None:
        _print_json(read_error)
        return 1
    assert packet is not None

    engine_stdout = StringIO()
    with redirect_stdout(engine_stdout):
        result = run_operator_coding_task_packet(packet)
    _print_json(result)
    if result.get("accepted") is True and result.get("blocked") is False:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
