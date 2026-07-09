"""PM-facing read-only CLI for objective-to-route-to-packet review."""

from __future__ import annotations

import json
import sys
from typing import Sequence

from orchestrator.objective_route_packet_loop import (
    build_objective_route_packet,
    render_objective_route_packet_markdown,
)


def _parse_args(argv: Sequence[str]) -> tuple[str | None, str, str | None]:
    objective = None
    output_format = "json"
    args = list(argv)
    index = 0
    while index < len(args):
        if args[index] == "--objective" and index + 1 < len(args) and args[index + 1].strip():
            objective = args[index + 1]
            index += 2
        elif args[index] == "--format" and index + 1 < len(args) and args[index + 1] in {"json", "markdown"}:
            output_format = args[index + 1]
            index += 2
        else:
            return None, output_format, "Usage: python -m orchestrator.objective_route_packet_cli --objective <text> [--format json|markdown]"
    if objective is None:
        return None, output_format, "An operator objective is required."
    return objective, output_format, None


def main(argv: list[str] | None = None) -> int:
    objective, output_format, error = _parse_args(sys.argv[1:] if argv is None else argv)
    if error:
        print(json.dumps({"accepted": False, "blocked": True, "detail": error}, indent=2))
        return 2
    loop = build_objective_route_packet(objective)
    if output_format == "markdown":
        print(render_objective_route_packet_markdown(loop))
    else:
        print(json.dumps(loop, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
