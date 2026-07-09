"""PM-readable dry-run CLI for the coordinator-agent loop."""

from __future__ import annotations

import json
import sys

from orchestrator.coordinator_agent_loop import (
    render_operator_review_markdown,
    run_dry_coordinator_loop,
    render_dry_coordinator_loop_markdown,
)
from orchestrator.local_model_provider_stub import StaticLocalModelProvider


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    objective = None
    output_format = "json"
    model_output_json = None
    index = 0
    while index < len(args):
        if args[index] == "--objective" and index + 1 < len(args) and args[index + 1].strip():
            objective = args[index + 1]
            index += 2
        elif args[index] == "--format" and index + 1 < len(args) and args[index + 1] in {"json", "markdown", "operator"}:
            output_format = args[index + 1]
            index += 2
        elif args[index] == "--model-output-json" and index + 1 < len(args):
            model_output_json = args[index + 1]
            index += 2
        else:
            print(json.dumps({"accepted": False, "blocked": True, "detail": "Usage: python -m orchestrator.coordinator_agent_loop_cli --objective <text> [--format json|markdown|operator] [--model-output-json <json>]"}, indent=2))
            return 2
    if objective is None:
        print(json.dumps({"accepted": False, "blocked": True, "detail": "An operator objective is required."}, indent=2))
        return 2
    reasoning_provider = None
    if model_output_json is not None:
        try:
            reasoning_payload = json.loads(model_output_json)
        except json.JSONDecodeError:
            print(json.dumps({"accepted": False, "blocked": True, "detail": "--model-output-json must be valid JSON."}, indent=2))
            return 2
        reasoning_provider = StaticLocalModelProvider(reasoning_payload)
    loop = run_dry_coordinator_loop(objective, reasoning_provider=reasoning_provider)
    if output_format == "operator":
        print(render_operator_review_markdown(loop))
    elif output_format == "markdown":
        print(render_dry_coordinator_loop_markdown(loop))
    else:
        print(json.dumps(loop, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
