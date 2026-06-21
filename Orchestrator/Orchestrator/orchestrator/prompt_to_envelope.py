"""Deterministic prompt-to-envelope fixture contract.

This module handles explicit test fixtures only. Raw prompt text is preserved
for traceability but is never parsed as route authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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

NON_PROOFS = (
    "fixture_classification_is_not_live_prompt_inference",
    "raw_prompt_text_is_not_parsed_as_authority",
    "no_natural_language_intent_inference",
    "no_model_provider_inference",
    "no_live_router",
    "no_route_execution",
    "no_provider_model_runtime_platform_selection",
    "no_rag_or_local_lookup",
    "no_scheduler_or_reminder_execution",
    "no_connector_execution",
    "no_file_mutation",
    "no_production_readiness",
)

SUBSTRATE_SMUGGLING_TERMS = (
    "codex",
    "worker substrate",
    "worker_substrate",
    "provider",
    "model",
    "runtime",
    "platform",
    "openclaw",
    "hermes",
    "ollama",
    "wsl",
    "discord",
    "connector execution",
    "production execution",
)

SUBSTRATE_CONTEXT_FIELDS = (
    "declared_request_type",
    "expected_blocked_reason",
    "expected_next_action",
    "fixture_notes",
)


@dataclass(frozen=True)
class PromptInferenceFixture:
    fixture_id: str
    raw_prompt: str = ""
    declared_request_type: str | None = None
    expected_required_capabilities: tuple[str, ...] | None = None
    expected_risk_level: str | None = None
    expected_missing_inputs: tuple[str, ...] = ()
    expected_requires_confirmation: bool = False
    expected_requires_external_connector: bool = False
    expected_allowed_to_answer_directly: bool = False
    expected_allowed_to_mutate_files: bool = False
    expected_allowed_to_schedule: bool = False
    expected_allowed_to_use_local_documents: bool = False
    expected_allowed_to_use_web: bool = False
    expected_blocked_reason: str = ""
    expected_next_action: str = ""
    fixture_notes: str = ""
    expected_explicit_mutation_permission: bool = False
    expected_explicit_local_document_authority: bool = False
    expected_explicit_web_boundary: bool = False
    expected_explicit_schedule_confirmation: bool = False
    expected_explicit_connector_boundary: bool = False
    expected_explicit_export_package_permission: bool = False
    expected_explicit_cleanup_delete_archive_permission: bool = False
    expected_explicit_production_boundary: bool = False


@dataclass(frozen=True)
class PromptInferenceDecision:
    fixture_id: str
    route_admission: str
    accepted: bool
    request_type: str
    confidence: float
    required_capabilities: tuple[str, ...]
    missing_inputs: tuple[str, ...]
    risk_level: str
    execution_policy: str
    recommended_next_action: str
    requires_operator_confirmation: bool
    requires_external_connector: bool
    allowed_to_answer_directly: bool
    allowed_to_mutate_files: bool
    allowed_to_schedule: bool
    allowed_to_use_local_documents: bool
    allowed_to_use_web: bool
    reasoning_summary_for_operator: str
    caveats: tuple[str, ...]
    blocked_conditions: tuple[str, ...]
    non_proofs: tuple[str, ...]
    intake_source: str
    activity_flags: dict[str, bool]


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _tuple_of_text(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (_normalize_text(value),) if _normalize_text(value) else ()
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(text for text in (_normalize_text(item) for item in value) if text)


def _contains_smuggling(value: Any) -> bool:
    if isinstance(value, (list, tuple)):
        return any(_contains_smuggling(item) for item in value)
    text = _normalize_text(value).lower()
    return bool(text) and any(term in text for term in SUBSTRATE_SMUGGLING_TERMS)


def _blocked_decision(
    fixture: PromptInferenceFixture,
    route_admission: str,
    blocked_conditions: tuple[str, ...],
    *,
    request_type: str = "needs_clarification",
    missing_inputs: tuple[str, ...] = (),
    recommended_next_action: str = "ask_operator_for_explicit_fixture_metadata",
) -> PromptInferenceDecision:
    return PromptInferenceDecision(
        fixture_id=_normalize_text(fixture.fixture_id),
        route_admission=route_admission,
        accepted=False,
        request_type=request_type,
        confidence=0.0,
        required_capabilities=(),
        missing_inputs=missing_inputs,
        risk_level="unknown",
        execution_policy="fixture_classification_only",
        recommended_next_action=recommended_next_action,
        requires_operator_confirmation=False,
        requires_external_connector=False,
        allowed_to_answer_directly=False,
        allowed_to_mutate_files=False,
        allowed_to_schedule=False,
        allowed_to_use_local_documents=False,
        allowed_to_use_web=False,
        reasoning_summary_for_operator=(
            "Fixture metadata was insufficient or blocked; raw prompt text was not inferred."
        ),
        caveats=("fixture_not_converted_to_executing_route",),
        blocked_conditions=blocked_conditions,
        non_proofs=NON_PROOFS,
        intake_source="prompt_fixture_contract",
        activity_flags=dict(NO_ACTIVITY_FLAGS),
    )


def _has_metadata_smuggling(fixture: PromptInferenceFixture) -> bool:
    values = [getattr(fixture, field) for field in SUBSTRATE_CONTEXT_FIELDS]
    return any(_contains_smuggling(value) for value in values)


def classify_prompt_fixture(fixture: PromptInferenceFixture | dict[str, Any]) -> PromptInferenceDecision:
    """Classify an explicit fixture without inferring intent from raw text."""

    if isinstance(fixture, dict):
        fixture = PromptInferenceFixture(**fixture)
    if not isinstance(fixture, PromptInferenceFixture):
        raise TypeError("fixture must be PromptInferenceFixture or fixture dict")

    fixture_id = _normalize_text(fixture.fixture_id)
    request_type = _normalize_text(fixture.declared_request_type)
    required_capabilities = _tuple_of_text(fixture.expected_required_capabilities)
    risk_level = _normalize_text(fixture.expected_risk_level)
    missing_inputs = _tuple_of_text(fixture.expected_missing_inputs)
    next_action = _normalize_text(fixture.expected_next_action) or "prepare_fixture_intake_for_admission_review"
    caveats = ["prompt_fixture_contract_only", "raw_prompt_not_inferred"]
    blocked_conditions: list[str] = []

    if not fixture_id:
        blocked_conditions.append("fixture_id_required")
    if not request_type:
        return _blocked_decision(
            fixture,
            "needs_clarification",
            tuple(blocked_conditions + ["declared_request_type_required"]),
            missing_inputs=tuple(dict.fromkeys(missing_inputs + ("declared_request_type",))),
        )
    if fixture.expected_required_capabilities is None:
        return _blocked_decision(
            fixture,
            "needs_clarification",
            tuple(blocked_conditions + ["expected_required_capabilities_required"]),
            request_type="needs_clarification",
            missing_inputs=tuple(dict.fromkeys(missing_inputs + ("expected_required_capabilities",))),
        )
    if not risk_level:
        return _blocked_decision(
            fixture,
            "needs_clarification",
            tuple(blocked_conditions + ["expected_risk_level_required"]),
            missing_inputs=tuple(dict.fromkeys(missing_inputs + ("expected_risk_level",))),
        )

    if _has_metadata_smuggling(fixture):
        return _blocked_decision(
            fixture,
            "rejected",
            tuple(blocked_conditions + ["substrate_smuggling_blocked"]),
            request_type="unsupported_or_requires_connector",
            recommended_next_action="reject_or_reframe_without_provider_model_runtime_platform_substrate",
        )

    if fixture.expected_allowed_to_mutate_files and (
        not fixture.expected_requires_confirmation or not fixture.expected_explicit_mutation_permission
    ):
        blocked_conditions.append("mutation_requires_explicit_permission_and_confirmation")

    if fixture.expected_allowed_to_schedule and (
        not fixture.expected_requires_confirmation or not fixture.expected_explicit_schedule_confirmation
    ):
        blocked_conditions.append("scheduling_requires_explicit_confirmation")

    if fixture.expected_allowed_to_use_local_documents and not fixture.expected_explicit_local_document_authority:
        blocked_conditions.append("local_document_lookup_requires_source_authority")

    if fixture.expected_allowed_to_use_web and not fixture.expected_explicit_web_boundary:
        blocked_conditions.append("web_research_requires_explicit_boundary")
        caveats.append("web_lookup_not_implemented")
    elif fixture.expected_allowed_to_use_web:
        caveats.append("web_lookup_not_implemented")

    if fixture.expected_requires_external_connector and not fixture.expected_explicit_connector_boundary:
        blocked_conditions.append("connector_requires_explicit_boundary")

    if request_type == "needs_clarification":
        blocked_conditions.append("fixture_declares_needs_clarification")
    if request_type == "unsupported_or_requires_connector":
        blocked_conditions.append("unsupported_or_requires_connector")
    if "unsupported_or_blocked" in required_capabilities:
        blocked_conditions.append("unsupported_or_blocked_capability")
    if "provider_model" in required_capabilities or "platform_runtime" in required_capabilities:
        blocked_conditions.append("provider_model_runtime_platform_requires_separate_boundary")
    if "production_execution" in required_capabilities or fixture.expected_explicit_production_boundary:
        blocked_conditions.append("production_execution_blocked")
    if "artifact_export_package" in required_capabilities and not fixture.expected_explicit_export_package_permission:
        blocked_conditions.append("export_package_requires_explicit_permission")
    if (
        any(item in required_capabilities for item in ("bounded_file_write", "filesystem_mutation_authority"))
        and "cleanup" in _normalize_text(fixture.expected_blocked_reason).lower()
        and not fixture.expected_explicit_cleanup_delete_archive_permission
    ):
        blocked_conditions.append("cleanup_delete_archive_requires_explicit_permission")

    if blocked_conditions:
        return _blocked_decision(
            fixture,
            "needs_clarification" if request_type == "needs_clarification" else "rejected",
            tuple(dict.fromkeys(blocked_conditions)),
            request_type=request_type,
            missing_inputs=missing_inputs,
            recommended_next_action=next_action,
        )

    if request_type in {"local_document_lookup", "research_request", "reminder_request"}:
        caveats.append("capability_requires_downstream_boundary")
    if fixture.expected_requires_external_connector:
        caveats.append("connector_execution_not_implemented")
    if fixture.expected_allowed_to_mutate_files:
        caveats.append("mutation_authority_is_fixture_metadata_only")
    if "artifact_export_package" in required_capabilities:
        caveats.append("artifact_export_package_not_implemented")

    return PromptInferenceDecision(
        fixture_id=fixture_id,
        route_admission="fixture_intake_ready",
        accepted=True,
        request_type=request_type,
        confidence=0.85,
        required_capabilities=required_capabilities,
        missing_inputs=missing_inputs,
        risk_level=risk_level,
        execution_policy="fixture_classification_only_no_execution",
        recommended_next_action=next_action,
        requires_operator_confirmation=fixture.expected_requires_confirmation,
        requires_external_connector=fixture.expected_requires_external_connector,
        allowed_to_answer_directly=fixture.expected_allowed_to_answer_directly,
        allowed_to_mutate_files=fixture.expected_allowed_to_mutate_files,
        allowed_to_schedule=fixture.expected_allowed_to_schedule,
        allowed_to_use_local_documents=fixture.expected_allowed_to_use_local_documents,
        allowed_to_use_web=fixture.expected_allowed_to_use_web,
        reasoning_summary_for_operator=(
            "Explicit fixture metadata was converted to structured intake; raw prompt text was preserved only."
        ),
        caveats=tuple(dict.fromkeys(caveats)),
        blocked_conditions=(),
        non_proofs=NON_PROOFS,
        intake_source="prompt_fixture_contract",
        activity_flags=dict(NO_ACTIVITY_FLAGS),
    )


def fixture_to_request_intake(
    fixture_or_decision: PromptInferenceFixture | PromptInferenceDecision | dict[str, Any],
) -> RequestIntakeRecord:
    """Convert an accepted fixture decision into Phase 111 structured intake."""

    decision = (
        fixture_or_decision
        if isinstance(fixture_or_decision, PromptInferenceDecision)
        else classify_prompt_fixture(fixture_or_decision)
    )
    if not decision.accepted:
        raise ValueError("fixture_decision_not_accepted_for_intake_conversion")

    return RequestIntakeRecord(
        request_id=decision.fixture_id,
        observed_request_summary="Fixture metadata converted to structured intake; raw prompt not inferred.",
        request_type=decision.request_type,
        confidence=decision.confidence,
        required_capabilities=decision.required_capabilities,
        missing_inputs=decision.missing_inputs,
        risk_level=decision.risk_level,
        execution_policy=decision.execution_policy,
        recommended_next_action=decision.recommended_next_action,
        requires_operator_confirmation=decision.requires_operator_confirmation,
        requires_external_connector=decision.requires_external_connector,
        allowed_to_answer_directly=decision.allowed_to_answer_directly,
        allowed_to_mutate_files=decision.allowed_to_mutate_files,
        allowed_to_schedule=decision.allowed_to_schedule,
        allowed_to_use_local_documents=decision.allowed_to_use_local_documents,
        allowed_to_use_web=decision.allowed_to_use_web,
        reasoning_summary_for_operator=decision.reasoning_summary_for_operator,
        caveats=decision.caveats + decision.non_proofs,
        intake_source=decision.intake_source,
    )
