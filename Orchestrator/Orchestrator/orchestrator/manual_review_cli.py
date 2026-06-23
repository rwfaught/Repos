"""Deterministic manual review CLI-compatible adapter contract.

This module is a thin standard-library adapter over the Phase 118 manual
review runner. It is not a productized CLI framework, service, UI, router,
worker dispatch surface, or production execution path.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from orchestrator.manual_review_runner import (
    NO_ACTIVITY_FLAGS as RUNNER_NO_ACTIVITY_FLAGS,
    list_builtin_review_fixtures,
    run_named_fixture_review,
    run_structured_intake_review,
)
from orchestrator.route_proposal import RequestIntakeRecord


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

GENERAL_ANSWER_BLOCKING_FLAGS = {
    "requires_file_mutation": "requires_file_mutation",
    "allowed_to_mutate_files": "requires_file_mutation",
    "requires_mutation": "requires_file_mutation",
    "requires_scheduling": "requires_scheduling",
    "allowed_to_schedule": "requires_scheduling",
    "requires_reminder": "requires_scheduling",
    "requires_local_documents": "requires_local_documents_or_rag",
    "requires_rag_lookup": "requires_local_documents_or_rag",
    "allowed_to_use_local_documents": "requires_local_documents_or_rag",
    "requires_web_lookup": "requires_web_lookup",
    "allowed_to_use_web": "requires_web_lookup",
    "requires_external_connector": "requires_external_connector",
    "requires_connector": "requires_external_connector",
    "requires_provider_execution": "requires_provider_model_or_runtime_execution",
    "requires_model_execution": "requires_provider_model_or_runtime_execution",
    "requires_runtime_execution": "requires_provider_model_or_runtime_execution",
    "provider_execution_required": "requires_provider_model_or_runtime_execution",
    "model_execution_required": "requires_provider_model_or_runtime_execution",
    "runtime_execution_required": "requires_provider_model_or_runtime_execution",
    "production_readiness": "claims_production_readiness",
    "claims_production_readiness": "claims_production_readiness",
}

LOW_RISK_GENERAL_ANSWER_VALUES = {"low", "routine"}


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
            "  --general-answer-input <json_path> [--write-review-json <artifact_json_path>]",
            "  --fixture <fixture_id> [--draft-provider-probe-packet] [--authorize-probe-boundary]",
            "      [--probe-kind <value>] [--probe-surface <value>]",
            "      [--probe-scope <value>] [--expected-evidence <value>] [--stop-condition <value>]",
            "  --help",
            "",
            "This adapter renders deterministic Phase 118 review output only.",
            "General answer input accepts structured local JSON only.",
            "Review JSON persistence requires a caller-supplied artifact path.",
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


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _string_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(text for text in (_text(item) for item in value) if text)


def _read_json_object(path_text: str) -> tuple[dict[str, Any] | None, str]:
    if not path_text:
        return None, "Manual review adapter requires a JSON path after --general-answer-input."

    try:
        raw_text = Path(path_text).read_text(encoding="utf-8-sig")
    except OSError as exc:
        return None, f"Manual review adapter could not read general-answer input: {exc.__class__.__name__}."

    try:
        value = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        return None, f"Manual review adapter rejected malformed JSON: line {exc.lineno} column {exc.colno}."

    if not isinstance(value, dict):
        return None, "Manual review adapter requires a structured JSON object."
    return value, ""


def _general_answer_input_blockers(value: dict[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    missing: list[str] = []
    blocked: list[str] = []

    request_id = _text(value.get("request_id"))
    request_type = _text(value.get("request_type"))
    intent = _text(value.get("user_intent_summary"))
    risk_level = _text(value.get("risk_level")).lower()

    if not request_id:
        missing.append("request_id")
    if not intent:
        missing.append("user_intent_summary")
    if request_type != "general_answer":
        blocked.append("wrong_request_type")
    if risk_level not in LOW_RISK_GENERAL_ANSWER_VALUES:
        if risk_level in {"high", "critical"}:
            blocked.append("high_or_critical_risk")
        else:
            blocked.append("not_low_risk_general_answer")

    for field, blocker in GENERAL_ANSWER_BLOCKING_FLAGS.items():
        if value.get(field) is True and blocker not in blocked:
            blocked.append(blocker)

    return tuple(missing), tuple(blocked)


def _general_answer_rejection_result(
    *,
    error_text: str,
    caveat: str,
    output_text: str = "",
) -> ManualReviewCliResult:
    return _result(
        exit_code=2,
        command="general-answer-input",
        output_text=output_text,
        error_text=error_text,
        caveats=(caveat, "general_answer_input_rejected_before_runner_call"),
    )


def _structured_general_answer_intake(value: dict[str, Any]) -> RequestIntakeRecord:
    request_id = _text(value.get("request_id"))
    intent = _text(value.get("user_intent_summary"))
    caveats = _dedupe(
        _string_tuple(value.get("caveats"))
        + (
            "real_input_report_only_cli_adapter=true",
            "structured_json_input_only",
            "manual_review_only_non_executing",
        )
    )
    return RequestIntakeRecord(
        request_id=request_id,
        observed_request_summary=intent,
        request_type="general_answer",
        confidence=0.9,
        required_capabilities=("direct_answer",),
        missing_inputs=(),
        risk_level=_text(value.get("risk_level")).lower(),
        execution_policy="report_only_manual_review_only_non_executing",
        recommended_next_action=_text(value.get("recommended_next_action"))
        or "surface_lightweight_general_answer_report_for_manual_review",
        requires_operator_confirmation=False,
        requires_external_connector=False,
        allowed_to_answer_directly=True,
        allowed_to_mutate_files=False,
        allowed_to_schedule=False,
        allowed_to_use_local_documents=False,
        allowed_to_use_web=False,
        reasoning_summary_for_operator=(
            "Operator supplied structured low-risk general_answer JSON; "
            "adapter performs no raw prompt inference and no execution."
        ),
        caveats=caveats,
        intake_source="operator_structured_general_answer_input_file",
    )


def _parse_general_answer_input_options(args: tuple[str, ...]) -> tuple[str, str, str]:
    if len(args) < 2 or not args[1]:
        return "", "", "Manual review adapter requires exactly one JSON path after --general-answer-input."

    input_path = args[1]
    artifact_path = ""
    index = 2
    while index < len(args):
        item = args[index]
        if item == "--write-review-json":
            if artifact_path:
                return "", "", "Manual review adapter received duplicate --write-review-json."
            if index + 1 >= len(args) or not args[index + 1]:
                return "", "", "Manual review adapter requires a JSON path after --write-review-json."
            artifact_path = args[index + 1]
            index += 2
            continue
        return "", "", f"Manual review adapter received unsupported general-answer option: {item}."

    return input_path, artifact_path, ""


def _review_artifact_payload(review, result: ManualReviewCliResult) -> dict[str, Any]:
    lightweight_payload = review.lightweight_answer_report_payload
    return {
        "phase": "PHASE_257",
        "artifact_kind": "general_answer_real_input_review_artifact_persistence",
        "request_id": review.request_id,
        "request_type": review.request_type,
        "accepted": bool(review.accepted),
        "blocked": not bool(review.accepted),
        "cli_result_status": "accepted" if result.exit_code == 0 and result.accepted else "blocked_or_rejected",
        "exit_code_intent": result.exit_code,
        "manual_review_text": review.review_text,
        "lightweight_answer_report_present": lightweight_payload is not None,
        "lightweight_answer_report_payload": lightweight_payload,
        "non_proofs": list(result.non_proofs),
        "caveats": list(result.caveats),
        "no_activity_flags": dict(result.no_activity_flags),
        "production_readiness": False,
        "source_input_kind": "structured_local_general_answer_json",
        "report_only": True,
        "runtime_execution": False,
        "provider_execution": False,
        "model_execution": False,
        "rag_lookup": False,
        "web_lookup": False,
        "scheduler_execution": False,
        "connector_execution": False,
        "worker_dispatch": False,
        "codex_dispatch": False,
        "service_api_ui": False,
    }


def _write_review_artifact(path_text: str, payload: dict[str, Any]) -> str:
    try:
        Path(path_text).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        return f"Manual review adapter could not write review JSON artifact: {exc.__class__.__name__}."
    return ""


def _run_general_answer_input(path_text: str, artifact_path: str = "") -> ManualReviewCliResult:
    value, read_error = _read_json_object(path_text)
    if read_error:
        return _general_answer_rejection_result(
            error_text=read_error,
            caveat="general_answer_input_file_rejected_before_runner_call",
        )

    assert value is not None
    missing, blocked = _general_answer_input_blockers(value)
    if missing or blocked:
        parts = []
        if blocked:
            parts.append("blocked_conditions=" + ",".join(blocked))
        if missing:
            parts.append("missing_requirements=" + ",".join(missing))
        detail = "; ".join(parts)
        return _general_answer_rejection_result(
            error_text=f"Manual review adapter rejected structured general-answer input: {detail}.",
            caveat="unsafe_or_incomplete_general_answer_input_rejected_before_runner_call",
            output_text="\n".join(
                (
                    "Structured General Answer Input Rejected",
                    f"- {detail}",
                    "- runner_review_started=false",
                    "- accepted_lightweight_report=false",
                )
            ),
        )

    review = run_structured_intake_review(
        _structured_general_answer_intake(value),
        fixture_id=_text(value.get("request_id")),
    )
    error_text = ""
    if not review.accepted:
        error_text = "Manual review adapter stopped conservatively for non-accepted structured general-answer input."
    result = _result(
        exit_code=0 if review.accepted else 1,
        command="general-answer-input",
        fixture_id=_text(value.get("request_id")),
        output_text=review.review_text,
        error_text=error_text,
        accepted=review.accepted,
        non_proofs=CLI_NON_PROOFS + review.non_proofs,
        no_activity_flags=review.no_activity_flags,
        caveats=review.caveats + ("general_answer_input_loaded_from_structured_local_json",),
    )
    if artifact_path:
        write_error = _write_review_artifact(artifact_path, _review_artifact_payload(review, result))
        if write_error:
            return _result(
                exit_code=2,
                command="general-answer-input",
                fixture_id=_text(value.get("request_id")),
                error_text=write_error,
                accepted=False,
                non_proofs=result.non_proofs,
                no_activity_flags=result.no_activity_flags,
                caveats=result.caveats + ("review_json_artifact_write_failed",),
            )
    return result


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

    if args and args[0] == "--general-answer-input":
        input_path, artifact_path, parse_error = _parse_general_answer_input_options(args)
        if parse_error:
            return _general_answer_rejection_result(
                error_text=parse_error,
                caveat="general_answer_input_path_count_rejected_before_runner_call",
            )
        return _run_general_answer_input(input_path, artifact_path)

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
