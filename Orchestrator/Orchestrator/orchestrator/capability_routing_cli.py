"""Read-only PM-facing CLI for capability routing triage."""

from __future__ import annotations

import json
import sys
from typing import Sequence

from orchestrator.capability_routing_triage import (
    build_capability_routing_review_report,
    build_capability_routing_summary,
    render_capability_routing_markdown,
)


def _usage() -> str:
    return "Usage: python -m orchestrator.capability_routing_cli [--summary | --task <id>] [--format json|markdown]"


def _parse_args(argv: Sequence[str]) -> tuple[str | None, bool, str, str | None]:
    task_id = None
    summary = False
    output_format = "json"
    args = list(argv)
    index = 0
    while index < len(args):
        if args[index] == "--summary":
            summary = True
            index += 1
        elif args[index] == "--task" and index + 1 < len(args) and args[index + 1]:
            task_id = args[index + 1]
            index += 2
        elif args[index] == "--format" and index + 1 < len(args) and args[index + 1] in {"json", "markdown"}:
            output_format = args[index + 1]
            index += 2
        else:
            return None, False, output_format, _usage()
    if summary and task_id is not None:
        return None, False, output_format, "--summary and --task cannot be used together"
    return task_id, summary, output_format, None


def main(argv: list[str] | None = None) -> int:
    task_id, summary, output_format, error = _parse_args(sys.argv[1:] if argv is None else argv)
    if error:
        print(json.dumps({"accepted": False, "blocked": True, "detail": error}, indent=2))
        return 2
    payload = (
        build_capability_routing_summary()
        if summary or task_id is None
        else build_capability_routing_review_report(task_id)
    )
    if output_format == "markdown":
        print(render_capability_routing_markdown(payload))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("found", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
