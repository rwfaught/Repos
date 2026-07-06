from __future__ import annotations

import argparse
import sys

from orchestrator.dry_mvp_loop_demo import (
    dry_mvp_loop_demo_to_json,
    render_dry_mvp_loop_demo_text,
    run_dry_mvp_loop_demo,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the deterministic dry MVP loop demo.")
    parser.add_argument("--out-dir", required=True, help="Caller-supplied directory for demo task/artifact writes.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = run_dry_mvp_loop_demo(args.out_dir)
    if args.format == "json":
        print(dry_mvp_loop_demo_to_json(result))
    else:
        print(render_dry_mvp_loop_demo_text(result))
    return 0 if result["demo_status"] == "dry_mvp_demo_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
