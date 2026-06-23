"""CLI-compatible adapter for the tiny vertical tracer dry report.

This module is a standard-library-only adapter over the Phase 169 dry tracer.
It does not execute providers, models, routes, workers, runtime surfaces,
platforms, services, APIs, UI, exports, packages, cleanup, archive, or
production behavior.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from orchestrator.tiny_vertical_tracer import (
    DEFAULT_FIXTURE_ID,
    NO_TRACER_ACTIVITY_FLAGS,
    TRACER_NON_PROOFS,
    build_tiny_vertical_tracer_dry_report,
    write_tiny_vertical_tracer_dry_report,
)


TINY_VERTICAL_TRACER_CLI_NON_PROOFS = (
    "tiny_vertical_tracer_cli_is_not_provider_execution",
    "tiny_vertical_tracer_cli_is_not_model_execution",
    "tiny_vertical_tracer_cli_is_not_route_execution",
    "tiny_vertical_tracer_cli_is_not_worker_dispatch",
    "tiny_vertical_tracer_cli_is_not_codex_dispatch",
    "tiny_vertical_tracer_cli_is_not_ollama_wsl_openclaw_hermes_discord",
    "tiny_vertical_tracer_cli_is_not_rag_web_scheduler_connector_behavior",
    "tiny_vertical_tracer_cli_is_not_service_api_ui_productization",
    "tiny_vertical_tracer_cli_is_not_export_package_cleanup_delete_archive",
    "tiny_vertical_tracer_cli_is_not_production_execution",
    "tiny_vertical_tracer_cli_is_not_production_readiness",
)

SUPPORTED_FIXTURES = (DEFAULT_FIXTURE_ID,)
SUPPORTED_FORMATS = ("text", "json")


@dataclass(frozen=True)
class TinyVerticalTracerCliResult:
    exit_code: int
    command: str
    fixture_id: str
    output_text: str
    error_text: str
    listed_fixtures: tuple[str, ...]
    accepted: bool
    payload: dict[str, Any]
    written_json_path: str | None
    written_text_path: str | None
    non_proofs: tuple[str, ...]
    activity_flags: dict[str, bool]
    caveats: tuple[str, ...]


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _help_text() -> str:
    return "\n".join(
        (
            "Tiny vertical tracer dry-report adapter commands:",
            "  --list-fixtures [--format text|json]",
            "  --fixture safe_direct_answer [--write-artifact --out-dir <path>] [--format text|json]",
            "  --help",
            "",
            "This adapter renders or writes deterministic Phase 169 dry report output only.",
            "Artifact writing requires a caller-supplied output directory.",
            "No provider/model/runtime/route/worker/platform/service/API/UI execution occurs.",
        )
    )


def _base_flags(*, persisted: bool = False) -> dict[str, bool]:
    flags = dict(NO_TRACER_ACTIVITY_FLAGS)
    flags["dry_artifact_persisted"] = persisted
    return flags


def _result(
    *,
    exit_code: int,
    command: str,
    fixture_id: str = "",
    output_text: str = "",
    error_text: str = "",
    listed_fixtures: tuple[str, ...] = (),
    accepted: bool = False,
    payload: dict[str, Any] | None = None,
    written_json_path: str | None = None,
    written_text_path: str | None = None,
    non_proofs: tuple[str, ...] = TINY_VERTICAL_TRACER_CLI_NON_PROOFS,
    activity_flags: dict[str, bool] | None = None,
    caveats: tuple[str, ...] = (),
) -> TinyVerticalTracerCliResult:
    return TinyVerticalTracerCliResult(
        exit_code=exit_code,
        command=command,
        fixture_id=fixture_id,
        output_text=output_text,
        error_text=error_text,
        listed_fixtures=listed_fixtures,
        accepted=accepted,
        payload=dict(payload or {}),
        written_json_path=written_json_path,
        written_text_path=written_text_path,
        non_proofs=_dedupe(non_proofs),
        activity_flags=dict(activity_flags or _base_flags()),
        caveats=_dedupe(caveats),
    )


def _json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def _parse_args(argv: Sequence[str]) -> tuple[dict[str, object], str]:
    args = tuple(argv)
    parsed: dict[str, object] = {
        "format": "text",
        "fixture_id": "",
        "list_fixtures": False,
        "write_artifact": False,
        "out_dir": "",
    }

    index = 0
    while index < len(args):
        item = args[index]
        if item in {"--help", "-h"}:
            parsed["help"] = True
            index += 1
            continue
        if item == "--list-fixtures":
            parsed["list_fixtures"] = True
            index += 1
            continue
        if item == "--fixture":
            if index + 1 >= len(args) or not args[index + 1]:
                return parsed, "Tiny vertical tracer CLI requires a fixture id after --fixture."
            parsed["fixture_id"] = args[index + 1]
            index += 2
            continue
        if item == "--write-artifact":
            parsed["write_artifact"] = True
            index += 1
            continue
        if item == "--out-dir":
            if index + 1 >= len(args) or not args[index + 1]:
                return parsed, "Tiny vertical tracer CLI requires a path after --out-dir."
            parsed["out_dir"] = args[index + 1]
            index += 2
            continue
        if item == "--format":
            if index + 1 >= len(args) or args[index + 1] not in SUPPORTED_FORMATS:
                return parsed, "Tiny vertical tracer CLI requires --format text or --format json."
            parsed["format"] = args[index + 1]
            index += 2
            continue
        return parsed, f"Tiny vertical tracer CLI received unsupported option: {item}."

    return parsed, ""


def _render_fixture_result(
    *,
    payload: dict[str, Any],
    rendered_text: str,
    output_format: str,
    written_json_path: str | None,
) -> str:
    if output_format == "json":
        return _json_text(payload)

    lines = [
        rendered_text,
        "",
        "CLI No-Execution Authority",
        f"- provider_selection_allowed={str(payload['provider_selection_allowed']).lower()}",
        f"- provider_execution_allowed={str(payload['provider_execution_allowed']).lower()}",
        f"- route_execution_allowed={str(payload['route_execution_allowed']).lower()}",
        f"- generation_allowed={str(payload['generation_allowed']).lower()}",
        f"- production_readiness={str(payload['production_readiness']).lower()}",
    ]
    if written_json_path:
        lines.extend(("", f"written_json_path={written_json_path}"))
    return "\n".join(lines)


def run_tiny_vertical_tracer_cli(argv: Sequence[str] | None = None) -> TinyVerticalTracerCliResult:
    """Build deterministic CLI output without executing runtime/provider work."""

    args = tuple(argv or ())
    if args in ((), ("--help",), ("-h",)):
        return _result(
            exit_code=0,
            command="help",
            output_text=_help_text(),
            caveats=("help_does_not_run_fixture",),
        )

    parsed, parse_error = _parse_args(args)
    output_format = str(parsed["format"])
    if parse_error:
        return _result(
            exit_code=2,
            command="invalid",
            output_text=_help_text(),
            error_text=parse_error,
            caveats=("command_rejected_before_tracer_call",),
        )

    if parsed.get("help") is True:
        return _result(
            exit_code=0,
            command="help",
            output_text=_help_text(),
            caveats=("help_does_not_run_fixture",),
        )

    if parsed["list_fixtures"] is True:
        payload = {
            "fixtures": list(SUPPORTED_FIXTURES),
            "phase": "PHASE_169",
            "adapter_phase": "PHASE_176",
            "non_proofs": list(TINY_VERTICAL_TRACER_CLI_NON_PROOFS),
        }
        output = (
            _json_text(payload)
            if output_format == "json"
            else "\n".join(("Tiny vertical tracer fixtures:",) + tuple(f"- {item}" for item in SUPPORTED_FIXTURES))
        )
        return _result(
            exit_code=0,
            command="list-fixtures",
            output_text=output,
            listed_fixtures=SUPPORTED_FIXTURES,
            payload=payload,
            caveats=("fixture_listing_does_not_run_fixture",),
        )

    fixture_id = str(parsed["fixture_id"])
    if not fixture_id:
        return _result(
            exit_code=2,
            command="invalid",
            output_text=_help_text(),
            error_text="Tiny vertical tracer CLI requires --fixture or --list-fixtures.",
            caveats=("missing_command_rejected_before_tracer_call",),
        )

    if fixture_id not in SUPPORTED_FIXTURES:
        return _result(
            exit_code=2,
            command="fixture",
            fixture_id=fixture_id,
            error_text=f"Unknown tiny vertical tracer fixture: {fixture_id}.",
            caveats=("unknown_fixture_rejected_before_tracer_call",),
        )

    if parsed["write_artifact"] is True and not parsed["out_dir"]:
        return _result(
            exit_code=2,
            command="fixture",
            fixture_id=fixture_id,
            error_text="Tiny vertical tracer CLI requires caller-supplied --out-dir with --write-artifact.",
            caveats=("artifact_write_rejected_without_caller_supplied_out_dir",),
        )

    if parsed["write_artifact"] is True:
        out_dir = Path(str(parsed["out_dir"]))
        tracer_result = write_tiny_vertical_tracer_dry_report(out_dir, fixture_id)
        payload = dict(tracer_result.payload)
        payload["adapter_phase"] = "PHASE_176"
        payload["written_json_path"] = tracer_result.written_path
        output_text = _render_fixture_result(
            payload=payload,
            rendered_text=tracer_result.rendered_text,
            output_format=output_format,
            written_json_path=tracer_result.written_path,
        )
        return _result(
            exit_code=0,
            command="fixture",
            fixture_id=fixture_id,
            output_text=output_text,
            accepted=tracer_result.accepted,
            payload=payload,
            written_json_path=tracer_result.written_path,
            non_proofs=TINY_VERTICAL_TRACER_CLI_NON_PROOFS + TRACER_NON_PROOFS + tuple(payload["non_proofs"]),
            activity_flags=dict(payload["activity_flags"]),
            caveats=tuple(payload["caveats"]),
        )

    tracer_result = build_tiny_vertical_tracer_dry_report(fixture_id)
    payload = dict(tracer_result.payload)
    payload["adapter_phase"] = "PHASE_176"
    output_text = _render_fixture_result(
        payload=payload,
        rendered_text=tracer_result.rendered_text,
        output_format=output_format,
        written_json_path=None,
    )
    return _result(
        exit_code=0,
        command="fixture",
        fixture_id=fixture_id,
        output_text=output_text,
        accepted=tracer_result.accepted,
        payload=payload,
        non_proofs=TINY_VERTICAL_TRACER_CLI_NON_PROOFS + TRACER_NON_PROOFS + tuple(payload["non_proofs"]),
        activity_flags=dict(payload["activity_flags"]),
        caveats=tuple(payload["caveats"]),
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Print deterministic adapter output and return an integer exit code."""

    result = run_tiny_vertical_tracer_cli(sys.argv[1:] if argv is None else argv)
    if result.output_text:
        print(result.output_text)
    if result.error_text:
        print(result.error_text, file=sys.stderr)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
