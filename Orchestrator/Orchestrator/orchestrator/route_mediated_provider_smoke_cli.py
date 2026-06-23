"""CLI-compatible adapter for the Phase 206 route-mediated smoke runner.

The default mode is dry artifact/plan output only. Runtime provider calls are
not authorized by Phase 206; --allow-provider-call is accepted only so it can
be rejected explicitly and reviewably.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence

from orchestrator.route_mediated_provider_smoke_runner import (
    build_route_mediated_provider_smoke_dry_artifact,
    reject_future_runtime_execution_request,
    review_route_mediated_provider_smoke_capture,
    write_route_mediated_provider_smoke_artifact,
)


def _help_text() -> str:
    return "\n".join(
        (
            "Route-mediated provider smoke runner commands:",
            "  --dry-run [--write-artifact --out-dir <path>]",
            "  --review-captured <json-file> [--write-artifact --out-dir <path>]",
            "  --allow-provider-call",
            "  --help",
            "",
            "Default mode is dry artifact shape only.",
            "Phase 206 does not authorize route/provider/model/runtime execution.",
            "--allow-provider-call is rejected during Phase 206.",
        )
    )


def run_route_mediated_provider_smoke_cli(argv: Sequence[str] | None = None) -> dict[str, object]:
    """Run deterministic CLI logic without runtime/provider execution."""

    args = tuple(argv or ())
    if args in ((), ("--help",), ("-h",)):
        return {"exit_code": 0, "output_text": _help_text(), "error_text": "", "payload": {}}

    write_artifact = "--write-artifact" in args
    out_dir = _option_value(args, "--out-dir")
    if write_artifact and not out_dir:
        return {
            "exit_code": 2,
            "output_text": _help_text(),
            "error_text": "--write-artifact requires --out-dir.",
            "payload": {},
        }

    if "--allow-provider-call" in args:
        result = reject_future_runtime_execution_request(allow_provider_call=True)
        return _cli_result(result.payload, 2, result.written_path, "Provider calls are not authorized by Phase 206.")

    if "--review-captured" in args:
        captured_path = _option_value(args, "--review-captured")
        if not captured_path:
            return {
                "exit_code": 2,
                "output_text": _help_text(),
                "error_text": "--review-captured requires a JSON file path.",
                "payload": {},
            }
        captured = json.loads(Path(captured_path).read_text(encoding="utf-8"))
        result = (
            write_route_mediated_provider_smoke_artifact(out_dir, captured_result=captured)
            if write_artifact
            else review_route_mediated_provider_smoke_capture(captured)
        )
        return _cli_result(result.payload, 0 if result.accepted else 1, result.written_path, "")

    if "--dry-run" in args:
        result = (
            write_route_mediated_provider_smoke_artifact(out_dir)
            if write_artifact
            else build_route_mediated_provider_smoke_dry_artifact()
        )
        return _cli_result(result.payload, 0, result.written_path, "")

    return {
        "exit_code": 2,
        "output_text": _help_text(),
        "error_text": "Unsupported route-mediated provider smoke CLI arguments.",
        "payload": {},
    }


def _option_value(args: tuple[str, ...], option: str) -> str:
    if option not in args:
        return ""
    index = args.index(option)
    if index + 1 >= len(args):
        return ""
    return args[index + 1]


def _cli_result(payload: dict[str, object], exit_code: int, written_path: str | None, error_text: str) -> dict[str, object]:
    output_payload = dict(payload)
    if written_path:
        output_payload["written_path"] = written_path
    return {
        "exit_code": exit_code,
        "output_text": json.dumps(output_payload, indent=2, sort_keys=True),
        "error_text": error_text,
        "payload": output_payload,
    }


def main(argv: Sequence[str] | None = None) -> int:
    result = run_route_mediated_provider_smoke_cli(sys.argv[1:] if argv is None else argv)
    if result["output_text"]:
        print(result["output_text"])
    if result["error_text"]:
        print(result["error_text"], file=sys.stderr)
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
