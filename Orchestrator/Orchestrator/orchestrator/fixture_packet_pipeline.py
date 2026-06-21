"""End-to-end fixture/intake to boundary-packet draft pipeline.

This module composes existing deterministic contracts only. Packet text output
is a draft, not dispatch, coordinator acceptance, worker execution, or
production authority.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from orchestrator.boundary_packet import (
    BoundaryPacketDraft,
    BoundaryPacketDraftResult,
    build_boundary_packet_draft,
    render_boundary_packet_text,
)
from orchestrator.intake_admission_pipeline import (
    IntakeAdmissionPipelineResult,
    run_fixture_admission_pipeline,
    run_structured_intake_admission_pipeline,
)
from orchestrator.prompt_to_envelope import PromptInferenceFixture


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

PIPELINE_NON_PROOFS = (
    "fixture_packet_pipeline_is_not_live_prompt_inference",
    "fixture_packet_pipeline_is_not_natural_language_intent_inference",
    "fixture_packet_pipeline_is_not_regex_classifier",
    "fixture_packet_pipeline_is_not_model_provider_inference",
    "fixture_packet_pipeline_is_not_live_router",
    "fixture_packet_pipeline_is_not_route_execution",
    "fixture_packet_pipeline_is_not_worker_execution",
    "fixture_packet_pipeline_does_not_invoke_codex",
    "fixture_packet_pipeline_does_not_select_concrete_substrate",
    "fixture_packet_pipeline_does_not_select_provider_model_runtime_platform",
    "fixture_packet_pipeline_does_not_perform_rag_or_local_lookup",
    "fixture_packet_pipeline_does_not_perform_web_lookup",
    "fixture_packet_pipeline_does_not_execute_scheduler_or_reminder",
    "fixture_packet_pipeline_does_not_execute_connector",
    "fixture_packet_pipeline_does_not_mutate_files",
    "fixture_packet_pipeline_does_not_export_or_package_artifacts",
    "fixture_packet_pipeline_does_not_cleanup_delete_or_archive",
    "fixture_packet_pipeline_does_not_execute_production_work",
    "fixture_packet_pipeline_is_not_production_readiness",
)


@dataclass(frozen=True)
class FixtureBoundaryPacketPipelineResult:
    pipeline_stage: str
    accepted: bool
    request_id: str
    request_type: str
    fixture_or_intake_source: str
    intake_admission_result: IntakeAdmissionPipelineResult
    boundary_packet_result: BoundaryPacketDraftResult
    packet_draft: BoundaryPacketDraft | None
    packet_text: str
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    capability_assessment: dict[str, Any]
    recommended_next_action: str
    non_proofs: tuple[str, ...]
    no_activity_flags: dict[str, bool]
    caveats: tuple[str, ...]


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _caveats_from_result(
    admission_result: IntakeAdmissionPipelineResult,
    packet_result: BoundaryPacketDraftResult,
) -> tuple[str, ...]:
    caveats: tuple[str, ...] = ()
    if admission_result.intake_record is not None:
        caveats += admission_result.intake_record.caveats
    if admission_result.candidate_route is not None:
        route_caveats = admission_result.candidate_route.route_envelope.get("caveats", ())
        if isinstance(route_caveats, list):
            caveats += tuple(str(item) for item in route_caveats)
    if packet_result.packet_draft is not None:
        caveats += packet_result.packet_draft.caveats
    if not packet_result.accepted:
        caveats += ("packet_draft_not_created",)
    return _dedupe(caveats)


def _combine_flags(
    admission_result: IntakeAdmissionPipelineResult,
    packet_result: BoundaryPacketDraftResult,
) -> dict[str, bool]:
    flags = dict(NO_ACTIVITY_FLAGS)
    for source in (admission_result.no_activity_flags, packet_result.no_activity_flags):
        for key in flags:
            flags[key] = flags[key] or bool(source.get(key, False))
    return flags


def _result_from_admission_and_packet(
    admission_result: IntakeAdmissionPipelineResult,
    packet_result: BoundaryPacketDraftResult,
    source_kind: str,
) -> FixtureBoundaryPacketPipelineResult:
    packet_text = (
        render_boundary_packet_text(packet_result.packet_draft)
        if packet_result.packet_draft is not None
        else ""
    )
    accepted = admission_result.accepted and packet_result.accepted
    stage = "boundary_packet_draft_created" if accepted else (
        "boundary_packet_draft_blocked"
        if admission_result.accepted
        else admission_result.pipeline_stage
    )
    blocked_conditions = _dedupe(admission_result.blocked_conditions + packet_result.blocked_conditions)
    missing_requirements = _dedupe(admission_result.missing_requirements + packet_result.missing_requirements)
    non_proofs = _dedupe(PIPELINE_NON_PROOFS + admission_result.non_proofs + packet_result.non_proofs)

    return FixtureBoundaryPacketPipelineResult(
        pipeline_stage=stage,
        accepted=accepted,
        request_id=admission_result.request_id,
        request_type=admission_result.request_type,
        fixture_or_intake_source=source_kind,
        intake_admission_result=admission_result,
        boundary_packet_result=packet_result,
        packet_draft=packet_result.packet_draft,
        packet_text=packet_text,
        blocked_conditions=blocked_conditions,
        missing_requirements=missing_requirements,
        capability_assessment=deepcopy(packet_result.capability_assessment),
        recommended_next_action=packet_result.recommended_next_action,
        non_proofs=non_proofs,
        no_activity_flags=_combine_flags(admission_result, packet_result),
        caveats=_caveats_from_result(admission_result, packet_result),
    )


def run_fixture_to_boundary_packet_pipeline(
    fixture: PromptInferenceFixture | dict[str, Any],
) -> FixtureBoundaryPacketPipelineResult:
    """Run prompt fixture through admission and boundary-packet drafting."""

    admission_result = run_fixture_admission_pipeline(fixture)
    packet_result = build_boundary_packet_draft(admission_result)
    return _result_from_admission_and_packet(admission_result, packet_result, "prompt_fixture")


def run_structured_intake_to_boundary_packet_pipeline(
    intake: Any,
) -> FixtureBoundaryPacketPipelineResult:
    """Run structured intake through admission and boundary-packet drafting."""

    admission_result = run_structured_intake_admission_pipeline(intake)
    packet_result = build_boundary_packet_draft(admission_result)
    return _result_from_admission_and_packet(admission_result, packet_result, "structured_intake")
