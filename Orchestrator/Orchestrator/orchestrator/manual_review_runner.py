"""Manual coordinator review runner contract.

The runner executes only deterministic in-process contracts over explicit
fixtures or structured intake. It is not a service, CLI, router, dispatch
surface, substrate selector, worker execution, or production behavior.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from orchestrator.coordinator_review_report import (
    CoordinatorReviewReportResult,
    build_coordinator_review_report,
    render_coordinator_review_text,
)
from orchestrator.fixture_packet_pipeline import (
    FixtureBoundaryPacketPipelineResult,
    run_fixture_to_boundary_packet_pipeline,
    run_structured_intake_to_boundary_packet_pipeline,
)
from orchestrator.prompt_to_envelope import PromptInferenceFixture
from orchestrator.route_proposal import RequestIntakeRecord


NO_ACTIVITY_FLAGS = {
    "mutation_performed": False,
    "execution_performed": False,
    "provider_executed": False,
    "model_executed": False,
    "runtime_executed": False,
    "wsl_executed": False,
    "installer_executed": False,
    "discord_executed": False,
    "bridge_executed": False,
    "adapter_executed": False,
    "platform_executed": False,
    "export_performed": False,
    "package_performed": False,
    "cleanup_performed": False,
    "deletion_performed": False,
    "archive_performed": False,
}

RUNNER_NON_PROOFS = (
    "runner_is_not_service_api_ui",
    "runner_is_not_live_prompt_inference",
    "runner_is_not_natural_language_intent_inference",
    "runner_is_not_regex_classifier",
    "runner_is_not_live_router",
    "runner_is_not_route_execution",
    "runner_is_not_worker_execution",
    "runner_does_not_invoke_codex_or_relay",
    "runner_does_not_select_concrete_substrate",
    "runner_does_not_select_provider_model_runtime_platform",
    "runner_does_not_perform_rag_or_local_lookup",
    "runner_does_not_perform_web_lookup",
    "runner_does_not_execute_scheduler_or_reminder",
    "runner_does_not_execute_connector",
    "runner_does_not_mutate_files",
    "runner_does_not_export_or_package_artifacts",
    "runner_does_not_cleanup_delete_or_archive",
    "runner_does_not_execute_production_work",
    "runner_is_not_production_readiness",
)


@dataclass(frozen=True)
class ManualReviewRunResult:
    accepted: bool
    fixture_id: str
    request_id: str
    request_type: str
    pipeline_result: FixtureBoundaryPacketPipelineResult | None
    review_report_result: CoordinatorReviewReportResult | None
    review_text: str
    router_policy_recommendation: dict[str, Any] | None
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    recommended_next_action: str
    non_proofs: tuple[str, ...]
    no_activity_flags: dict[str, bool]
    caveats: tuple[str, ...]


def _fixture(
    fixture_id: str,
    request_type: str,
    required_capabilities: tuple[str, ...],
    **overrides: Any,
) -> PromptInferenceFixture:
    values = {
        "fixture_id": fixture_id,
        "raw_prompt": "Catalog fixture prompt text is trace-only.",
        "declared_request_type": request_type,
        "expected_required_capabilities": required_capabilities,
        "expected_risk_level": "low",
        "expected_next_action": "prepare_fixture_intake_for_admission_review",
    }
    values.update(overrides)
    return PromptInferenceFixture(**values)


def _intake(
    request_id: str,
    caveats: tuple[str, ...],
) -> RequestIntakeRecord:
    return RequestIntakeRecord(
        request_id=request_id,
        observed_request_summary="Catalog structured intake for manual review runner.",
        request_type="coding_task",
        confidence=0.9,
        required_capabilities=("source_inspection", "patch_proposal", "filesystem_mutation_authority"),
        missing_inputs=(),
        risk_level="low",
        execution_policy="manual_review_runner_structured_intake_only",
        recommended_next_action="route_to_future_operator_confirmed_coding_boundary",
        requires_operator_confirmation=True,
        requires_external_connector=False,
        allowed_to_answer_directly=False,
        allowed_to_mutate_files=True,
        allowed_to_schedule=False,
        allowed_to_use_local_documents=False,
        allowed_to_use_web=False,
        reasoning_summary_for_operator="Manual runner structured intake; no execution authority.",
        caveats=caveats,
        intake_source="manual_review_runner_structured_catalog",
    )


_BUILTIN_REVIEW_CASES: dict[str, dict[str, Any]] = {
    "safe_direct_answer": {
        "kind": "fixture",
        "fixture": _fixture(
            "safe_direct_answer",
            "general_answer",
            ("direct_answer",),
            expected_allowed_to_answer_directly=True,
        ),
    },
    "safe_coding_report_only": {
        "kind": "fixture",
        "fixture": _fixture(
            "safe_coding_report_only",
            "planning_request",
            ("planning_report",),
            expected_next_action="prepare_non_executing_coding_report",
        ),
    },
    "safe_coding_docs_only_mutation": {
        "kind": "structured_intake",
        "intake": _intake(
            "safe_coding_docs_only_mutation",
            ("docs_only_mutation", "allowed_files: docs/PHASE_118.md"),
        ),
    },
    "safe_coding_source_test_mutation": {
        "kind": "structured_intake",
        "intake": _intake(
            "safe_coding_source_test_mutation",
            (
                "allowed_files: orchestrator/manual_review_runner.py",
                "allowed_files: tests/test_phase_118_manual_review_runner_contract.py",
            ),
        ),
    },
    "unknown_capability_blocked": {
        "kind": "fixture",
        "fixture": _fixture("unknown_capability_blocked", "planning_request", ("future_unknown_capability",)),
    },
    "substrate_smuggling_blocked": {
        "kind": "fixture",
        "fixture": _fixture(
            "substrate_smuggling_blocked",
            "coding_task",
            ("source_inspection",),
            expected_next_action="run with Codex provider",
        ),
    },
    "platform_provider_external_boundary": {
        "kind": "fixture",
        "fixture": _fixture(
            "platform_provider_external_boundary",
            "unsupported_or_requires_connector",
            ("provider_model", "platform_runtime"),
        ),
    },
    "production_execution_blocked": {
        "kind": "fixture",
        "fixture": _fixture(
            "production_execution_blocked",
            "unsupported_or_requires_connector",
            ("production_execution",),
            expected_explicit_production_boundary=True,
        ),
    },
    "ambiguous_needs_clarification": {
        "kind": "fixture",
        "fixture": PromptInferenceFixture(
            fixture_id="ambiguous_needs_clarification",
            raw_prompt="Trace-only ambiguous prompt text.",
        ),
    },
}


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _result_from_pipeline(
    pipeline_result: FixtureBoundaryPacketPipelineResult,
    fixture_id: str,
) -> ManualReviewRunResult:
    report_result = build_coordinator_review_report(pipeline_result)
    review_text = render_coordinator_review_text(report_result.report)
    return ManualReviewRunResult(
        accepted=report_result.accepted,
        fixture_id=fixture_id,
        request_id=pipeline_result.request_id,
        request_type=pipeline_result.request_type,
        pipeline_result=pipeline_result,
        review_report_result=report_result,
        review_text=review_text,
        router_policy_recommendation=dict(report_result.report.router_policy_recommendation),
        blocked_conditions=report_result.blocked_conditions,
        missing_requirements=report_result.missing_requirements,
        recommended_next_action=report_result.recommended_next_action,
        non_proofs=_dedupe(RUNNER_NON_PROOFS + report_result.non_proofs),
        no_activity_flags=dict(report_result.no_activity_flags),
        caveats=_dedupe(report_result.caveats),
    )


def _unknown_fixture_result(fixture_id: str) -> ManualReviewRunResult:
    return ManualReviewRunResult(
        accepted=False,
        fixture_id=fixture_id,
        request_id=fixture_id,
        request_type="unknown_fixture",
        pipeline_result=None,
        review_report_result=None,
        review_text="Manual review runner stopped: unknown fixture id. No execution occurred.",
        router_policy_recommendation=None,
        blocked_conditions=("unknown_builtin_review_fixture",),
        missing_requirements=("known_fixture_id",),
        recommended_next_action="choose_known_builtin_review_fixture",
        non_proofs=RUNNER_NON_PROOFS,
        no_activity_flags=dict(NO_ACTIVITY_FLAGS),
        caveats=("unknown_fixture_id_was_not_inferred",),
    )


def list_builtin_review_fixtures() -> tuple[str, ...]:
    """Return stable deterministic fixture IDs."""

    return tuple(sorted(_BUILTIN_REVIEW_CASES))


def get_builtin_review_fixture(fixture_id: str) -> dict[str, Any] | None:
    """Return a defensive copy of a built-in review case."""

    case = _BUILTIN_REVIEW_CASES.get(fixture_id)
    return deepcopy(case) if case is not None else None


def run_named_fixture_review(fixture_id: str) -> ManualReviewRunResult:
    """Run a named built-in fixture or structured intake through review output."""

    case = get_builtin_review_fixture(fixture_id)
    if case is None:
        return _unknown_fixture_result(fixture_id)

    if case["kind"] == "structured_intake":
        return run_structured_intake_review(case["intake"], fixture_id=fixture_id)
    return run_fixture_review(case["fixture"], fixture_id=fixture_id)


def run_fixture_review(
    fixture: PromptInferenceFixture | dict[str, Any],
    *,
    fixture_id: str | None = None,
) -> ManualReviewRunResult:
    """Run an explicit prompt fixture through review report rendering."""

    pipeline_result = run_fixture_to_boundary_packet_pipeline(fixture)
    return _result_from_pipeline(
        pipeline_result,
        fixture_id or pipeline_result.request_id,
    )


def run_structured_intake_review(
    intake: RequestIntakeRecord | dict[str, Any],
    *,
    fixture_id: str | None = None,
) -> ManualReviewRunResult:
    """Run explicit structured intake through review report rendering."""

    pipeline_result = run_structured_intake_to_boundary_packet_pipeline(intake)
    return _result_from_pipeline(
        pipeline_result,
        fixture_id or pipeline_result.request_id,
    )
