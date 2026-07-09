"""Read-only CLI for the deterministic local AI consulting campaign surface."""

from __future__ import annotations

import json
import sys
from typing import Sequence

from orchestrator.local_ai_consulting_campaign import (
    build_local_ai_consulting_operator_readback,
    build_local_ai_consulting_operator_review_report,
    build_local_ai_consulting_operator_summary,
    render_local_ai_consulting_operator_readback_markdown,
)


def _usage() -> str:
    return (
        "Usage: python -m orchestrator.local_ai_consulting_campaign_cli "
        "[--summary | --scenario <id>] [--format json|markdown]"
    )


def _parse_args(argv: Sequence[str]) -> tuple[str | None, bool, str | None, str | None]:
    args = list(argv)
    scenario_id = None
    summary = False
    output_format = "json"
    index = 0
    while index < len(args):
        if args[index] == "--scenario" and index + 1 < len(args) and args[index + 1]:
            scenario_id = args[index + 1]
            index += 2
            continue
        if args[index] == "--format" and index + 1 < len(args) and args[index + 1] in {"json", "markdown"}:
            output_format = args[index + 1]
            index += 2
            continue
        if args[index] == "--summary":
            summary = True
            index += 1
            continue
        return None, False, None, _usage()
    if summary and scenario_id is not None:
        return None, False, None, "--summary and --scenario cannot be used together"
    return scenario_id, summary, output_format, None


def main(argv: list[str] | None = None) -> int:
    scenario_id, summary, output_format, error = _parse_args(sys.argv[1:] if argv is None else argv)
    if error:
        print(json.dumps({"accepted": False, "blocked": True, "detail": error}, indent=2))
        return 2

    if summary:
        readback = build_local_ai_consulting_operator_summary()
    elif scenario_id is not None:
        readback = build_local_ai_consulting_operator_review_report(scenario_id)
    else:
        readback = build_local_ai_consulting_operator_readback()
    if output_format == "markdown":
        print(render_local_ai_consulting_operator_readback_markdown(readback))
    else:
        print(json.dumps(readback, indent=2, sort_keys=True))
    return 0 if readback.get("found", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
