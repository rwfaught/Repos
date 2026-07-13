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
from orchestrator.alpha_runtime import isolated_data_root, reconcile_lifecycle
from providers.subprocess_worker_provider import SubprocessWorkerProvider
from orchestrator.worker_execution_policy import normalize_worker_execution_policy


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


def _parse_args(argv: Sequence[str]) -> tuple[str, str, str, str, list[str], dict[str, Any] | None, dict[str, Any] | None]:
    args = tuple(argv)
    if len(args) >= 2 and args[0] == "--packet-json" and args[1]:
        if len(args) == 2:
            return "legacy_packet_json", args[1], "", "", [], None, None
        data_root = ""
        trust_posture = ""
        command: list[str] = []
        timeout_value: str | None = None
        index = 2
        while index < len(args):
            if args[index] == "--data-root" and index + 1 < len(args): data_root = args[index + 1]; index += 2; continue
            if args[index] == "--trusted-worker-posture" and index + 1 < len(args): trust_posture = args[index + 1]; index += 2; continue
            if args[index] == "--worker-timeout-seconds":
                if index + 1 >= len(args) or not args[index + 1]:
                    return "", "", "", "", [], _blocked(blocked_conditions=["worker_timeout_seconds_value_required"], detail="--worker-timeout-seconds requires a value."), None
                timeout_value = args[index + 1]; index += 2; continue
            if args[index] == "--worker-command" and index + 1 < len(args):
                command = list(args[index + 1:])
                if "--worker-timeout-seconds" in command:
                    return "", "", "", "", [], _blocked(
                        blocked_conditions=["worker_timeout_seconds_must_precede_worker_command"],
                        detail="--worker-timeout-seconds must occur before --worker-command.",
                    ), None
                break
            return "", "", "", "", [], _blocked(blocked_conditions=["unsupported_cli_arguments"], detail="Use --data-root, --trusted-worker-posture, --worker-timeout-seconds, and --worker-command."), None
        if not data_root or not trust_posture or not command:
            return "", "", "", "", [], _blocked(blocked_conditions=["isolated_data_root_worker_trust_and_command_required"], detail="Alpha execution requires --data-root, --trusted-worker-posture, and --worker-command."), None
        try:
            policy = normalize_worker_execution_policy(timeout_value, selection_source=("cli_explicit" if timeout_value is not None else "cli_default"))
        except ValueError as error:
            return "", "", "", "", [], _blocked(blocked_conditions=["worker_timeout_seconds_invalid"], detail=str(error)), None
        return "packet_json", args[1], data_root, trust_posture, command, None, policy
    if len(args) == 3 and args[0] == "--reconcile" and args[1] == "--data-root":
        return "reconcile", "", args[2], "", [], None, None
    if len(args) == 1 and args[0] == "--residue-guard":
        return "residue_guard", "", "", "", [], None, None
    return "", "", "", "", [], _blocked(
        blocked_conditions=["unsupported_or_missing_cli_arguments"],
        detail="Usage: python -m orchestrator.operator_coding_task_packet_cli --packet-json <path> --data-root <path> --trusted-worker-posture trusted_local_unsandboxed [--worker-timeout-seconds <seconds>] --worker-command <command...> | --reconcile --data-root <path>",
        missing_requirements=["packet_json_path"],
    ), None


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    mode, packet_path, data_root, trust_posture, command, argument_error, worker_execution_policy = _parse_args(args)
    if argument_error is not None:
        _print_json(argument_error)
        return 2

    if mode == "residue_guard":
        _print_json(inspect_packet_cli_generated_residue())
        return 0
    if mode == "reconcile":
        _print_json(reconcile_lifecycle(data_root))
        return 0

    packet, read_error = _read_packet_json(packet_path)
    if read_error is not None:
        _print_json(read_error)
        return 1
    assert packet is not None

    if mode == "legacy_packet_json":
        result = run_operator_coding_task_packet(packet)
        _print_json(result)
        return 1

    packet_posture = str(packet.get("worker_trust_posture", "")).strip()
    if packet_posture and packet_posture != trust_posture:
        _print_json(_blocked(blocked_conditions=["worker_trust_posture_mismatch"], detail="Packet and CLI trust postures must match."))
        return 1
    packet = {**packet, "worker_trust_posture": trust_posture}

    engine_stdout = StringIO()
    provider = SubprocessWorkerProvider(command, worker_execution_policy=worker_execution_policy)
    with isolated_data_root(data_root), redirect_stdout(engine_stdout):
        result = run_operator_coding_task_packet(packet, provider=provider)
    _print_json({**result, "worker_execution_policy": worker_execution_policy})
    if result.get("accepted") is True and result.get("blocked") is False:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
