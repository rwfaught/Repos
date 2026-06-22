"""Deterministic manual review CLI-compatible adapter contract.

This module is a thin standard-library adapter over the Phase 118 manual
review runner. It is not a productized CLI framework, service, UI, router,
worker dispatch surface, or production execution path.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Sequence

from orchestrator.manual_review_runner import (
    NO_ACTIVITY_FLAGS as RUNNER_NO_ACTIVITY_FLAGS,
    list_builtin_review_fixtures,
    run_named_fixture_review,
)


CLI_NON_PROOFS = (
    "cli_adapter_is_not_service_api_ui_productization",
    "cli_adapter_is_not_live_prompt_inference",
    "cli_adapter_is_not_natural_language_intent_inference",
    "cli_adapter_is_not_regex_classifier",
    "cli_adapter_is_not_live_router",
    "cli_adapter_is_not_route_execution",
    "cli_adapter_is_not_worker_execution",
    "cli_adapter_does_not_invoke_codex_or_relay",
    "cli_adapter_does_not_select_concrete_substrate",
    "cli_adapter_does_not_select_provider_model_runtime_platform",
    "cli_adapter_does_not_perform_rag_or_local_lookup",
    "cli_adapter_does_not_perform_web_lookup",
    "cli_adapter_does_not_execute_scheduler_or_reminder",
    "cli_adapter_does_not_execute_connector",
    "cli_adapter_does_not_mutate_files",
    "cli_adapter_does_not_export_or_package_artifacts",
    "cli_adapter_does_not_cleanup_delete_or_archive",
    "cli_adapter_does_not_execute_production_work",
    "cli_adapter_is_not_production_readiness",
)


@dataclass(frozen=True)
class ManualReviewCliResult:
    exit_code: int
    command: str
    fixture_id: str
    output_text: str
    error_text: str
    listed_fixtures: tuple[str, ...]
    accepted: bool
    non_proofs: tuple[str, ...]
    no_activity_flags: dict[str, bool]
    caveats: tuple[str, ...]


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _help_text() -> str:
    return "\n".join(
        (
            "Manual review adapter commands:",
            "  --list-fixtures",
            "  --fixture <fixture_id> [--draft-provider-probe-packet] [--authorize-probe-boundary]",
            "      [--probe-kind <value>] [--probe-surface <value>]",
            "      [--probe-scope <value>] [--expected-evidence <value>] [--stop-condition <value>]",
            "  --help",
            "",
            "This adapter renders deterministic Phase 118 review output only.",
            "Provider probe packet drafting is paperwork only.",
            "No probe, provider, model, runtime, worker, RAG, web, scheduler, connector, route, or production execution occurs.",
        )
    )


def _result(
    *,
    exit_code: int,
    command: str,
    fixture_id: str = "",
    output_text: str = "",
    error_text: str = "",
    listed_fixtures: tuple[str, ...] = (),
    accepted: bool = False,
    non_proofs: tuple[str, ...] = CLI_NON_PROOFS,
    no_activity_flags: dict[str, bool] | None = None,
    caveats: tuple[str, ...] = (),
) -> ManualReviewCliResult:
    return ManualReviewCliResult(
        exit_code=exit_code,
        command=command,
        fixture_id=fixture_id,
        output_text=output_text,
        error_text=error_text,
        listed_fixtures=listed_fixtures,
        accepted=accepted,
        non_proofs=_dedupe(non_proofs),
        no_activity_flags=dict(no_activity_flags or RUNNER_NO_ACTIVITY_FLAGS),
        caveats=_dedupe(caveats),
    )


def _parse_probe_packet_options(args: tuple[str, ...]) -> tuple[dict[str, object] | None, str]:
    draft_requested = False
    authorize = False
    probe_kind = ""
    probe_surface = ""
    probe_scope: list[str] = []
    expected_evidence: list[str] = []
    stop_conditions: list[str] = []

    index = 0
    while index < len(args):
        item = args[index]
        if item == "--draft-provider-probe-packet":
            draft_requested = True
            index += 1
            continue
        if item == "--authorize-probe-boundary":
            authorize = True
            index += 1
            continue
        if item in {"--probe-kind", "--probe-surface", "--probe-scope", "--expected-evidence", "--stop-condition"}:
            if index + 1 >= len(args) or not args[index + 1]:
                return None, f"Manual review adapter requires a value after {item}."
            value = args[index + 1]
            if item == "--probe-kind":
                probe_kind = value
            elif item == "--probe-surface":
                probe_surface = value
            elif item == "--probe-scope":
                probe_scope.append(value)
            elif item == "--expected-evidence":
                expected_evidence.append(value)
            elif item == "--stop-condition":
                stop_conditions.append(value)
            index += 2
            continue
        return None, f"Manual review adapter received unsupported fixture option: {item}."

    if not draft_requested:
        if authorize or probe_kind or probe_surface or probe_scope or expected_evidence or stop_conditions:
            return None, "Probe packet options require --draft-provider-probe-packet."
        return None, ""

    return (
        {
            "requested_probe_kind": probe_kind,
            "requested_surface": probe_surface,
            "operator_authorized_probe_boundary": authorize,
            "allowed_probe_scope": tuple(probe_scope),
            "expected_evidence": tuple(expected_evidence),
            "stop_conditions": tuple(stop_conditions),
            "caveats": ("cli_provider_probe_packet_draft_metadata_only",),
        },
        "",
    )


def build_manual_review_cli_output(argv: Sequence[str] | None = None) -> ManualReviewCliResult:
    """Build deterministic CLI-compatible output without mutating state."""

    args = tuple(argv or ())

    if args in ((), ("--help",), ("-h",)):
        return _result(
            exit_code=0,
            command="help",
            output_text=_help_text(),
            caveats=("help_does_not_run_fixture",),
        )

    if args == ("--list-fixtures",):
        fixtures = list_builtin_review_fixtures()
        output = "\n".join(("Built-in review fixtures:",) + tuple(f"- {fixture}" for fixture in fixtures))
        return _result(
            exit_code=0,
            command="list-fixtures",
            output_text=output,
            listed_fixtures=fixtures,
            caveats=("fixture_listing_does_not_run_fixture",),
        )

    if args and args[0] == "--fixture":
        if len(args) < 2 or not args[1]:
            return _result(
                exit_code=2,
                command="fixture",
                error_text="Manual review adapter requires exactly one fixture id.",
                caveats=("fixture_command_rejected_before_runner_call",),
            )

        fixture_id = args[1]
        provider_probe_packet_request, parse_error = _parse_probe_packet_options(args[2:])
        if parse_error:
            return _result(
                exit_code=2,
                command="fixture",
                fixture_id=fixture_id,
                error_text=parse_error,
                caveats=("fixture_command_rejected_before_runner_call",),
            )

        review = run_named_fixture_review(
            fixture_id,
            provider_probe_packet_request=provider_probe_packet_request,
        )
        error_text = ""
        if not review.accepted:
            error_text = "Manual review adapter stopped conservatively for non-accepted fixture review."
        return _result(
            exit_code=0 if review.accepted else 1,
            command="fixture",
            fixture_id=fixture_id,
            output_text=review.review_text,
            error_text=error_text,
            accepted=review.accepted,
            non_proofs=CLI_NON_PROOFS + review.non_proofs,
            no_activity_flags=review.no_activity_flags,
            caveats=review.caveats,
        )

    return _result(
        exit_code=2,
        command="invalid",
        output_text=_help_text(),
        error_text="Manual review adapter received an unsupported command.",
        caveats=("unsupported_command_rejected_before_runner_call",),
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Print deterministic adapter output and return an integer exit code."""

    result = build_manual_review_cli_output(sys.argv[1:] if argv is None else argv)
    if result.output_text:
        print(result.output_text)
    if result.error_text:
        print(result.error_text, file=sys.stderr)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
