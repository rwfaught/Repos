"""PM-readable dry-run CLI for the coordinator-agent loop."""

from __future__ import annotations

import json
import sys

from orchestrator.coordinator_agent_loop import (
    run_dry_coordinator_loop,
    render_dry_coordinator_loop_markdown,
)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    objective = None
    output_format = "json"
    index = 0
    while index < len(args):
        if args[index] == "--objective" and index + 1 < len(args) and args[index + 1].strip():
            objective = args[index + 1]
            index += 2
        elif args[index] == "--format" and index + 1 < len(args) and args[index + 1] in {"json", "markdown"}:
            output_format = args[index + 1]
            index += 2
        else:
            print(json.dumps({"accepted": False, "blocked": True, "detail": "Usage: python -m orchestrator.coordinator_agent_loop_cli --objective <text> [--format json|markdown]"}, indent=2))
            return 2
    if objective is None:
        print(json.dumps({"accepted": False, "blocked": True, "detail": "An operator objective is required."}, indent=2))
        return 2
    loop = run_dry_coordinator_loop(objective)
    if output_format == "markdown":
        print(render_dry_coordinator_loop_markdown(loop))
    else:
        print(json.dumps(loop, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
