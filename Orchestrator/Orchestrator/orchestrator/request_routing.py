from __future__ import annotations

from copy import deepcopy
from typing import Any

from orchestrator.capability_registry import assess_required_capabilities


REQUEST_TYPES = (
    "general_answer",
    "local_document_lookup",
    "reminder_request",
    "coding_task",
    "file_operation",
    "planning_request",
    "research_request",
    "creative_generation",
    "unsupported_or_requires_connector",
    "needs_clarification",
)

ROUTE_ENVELOPE_REQUIRED_FIELDS = (
    "request_id",
    "request_type",
    "confidence",
    "user_intent_summary",
    "required_capabilities",
    "missing_inputs",
    "risk_level",
    "execution_policy",
    "recommended_next_action",
    "requires_operator_confirmation",
    "requires_external_connector",
    "allowed_to_answer_directly",
    "allowed_to_mutate_files",
    "allowed_to_schedule",
    "allowed_to_use_local_documents",
    "allowed_to_use_web",
    "reasoning_summary_for_operator",
    "caveats",
)

BOOLEAN_PERMISSION_FIELDS = (
    "requires_operator_confirmation",
    "requires_external_connector",
    "allowed_to_answer_directly",
    "allowed_to_mutate_files",
    "allowed_to_schedule",
    "allowed_to_use_local_documents",
    "allowed_to_use_web",
)

LIST_FIELDS = (
    "required_capabilities",
    "missing_inputs",
    "caveats",
)

STRING_FIELDS = (
    "request_id",
    "request_type",
    "user_intent_summary",
    "risk_level",
    "execution_policy",
    "recommended_next_action",
    "reasoning_summary_for_operator",
)

HIGH_RISK_VALUES = {"high", "critical"}
MUTATION_REQUEST_TYPES = {"coding_task", "file_operation"}
LOCAL_DOCUMENT_REQUEST_TYPES = {"local_document_lookup"}
WEB_REQUEST_TYPES = {"research_request"}
SUBSTRATE_EXECUTOR_TERMS = (
    "pi",
    "codex",
    "openclaw",
    "ollama",
    "qwen",
    "openai",
    "anthropic",
    "provider",
    "model",
    "worker_substrate",
    "executor",
)

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


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        text = _normalize_text(item)
        if text:
            result.append(text)
    return result


def _append(condition: list[str], name: str) -> None:
    if name not in condition:
        condition.append(name)


def _contains_substrate_executor_reference(value: Any, *, key_hint: str = "") -> bool:
    if isinstance(value, dict):
        return any(
            _contains_substrate_executor_reference(item_value, key_hint=str(item_key))
            for item_key, item_value in value.items()
        )
    if isinstance(value, list):
        return any(_contains_substrate_executor_reference(item, key_hint=key_hint) for item in value)

    text = _normalize_text(value).lower()
    if not text:
        return False

    executor_context = any(
        term in key_hint.lower()
        for term in ("executor", "provider", "model", "substrate", "worker")
    )
    if executor_context:
        return any(term in text for term in SUBSTRATE_EXECUTOR_TERMS)

    if any(phrase in text for phrase in ("execute with", "run with", "handled by", "provider:", "model:")):
        return any(term in text for term in SUBSTRATE_EXECUTOR_TERMS)

    return False


def _base_result(
    admission: str,
    accepted: bool,
    request_type: str,
    missing_requirements: list[str],
    blocked_conditions: list[str],
    normalized_envelope: dict[str, Any] | None = None,
    capability_assessment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "route_admission": admission,
        "accepted": accepted,
        "request_type": request_type,
        "missing_requirements": list(missing_requirements),
        "blocked_conditions": list(blocked_conditions),
        "normalized_envelope": deepcopy(normalized_envelope) if accepted and normalized_envelope is not None else None,
        "capability_assessment": deepcopy(capability_assessment)
        if capability_assessment is not None
        else assess_required_capabilities([]),
        "activity_statement": (
            "Route-envelope validation only; no mutation, execution, provider, model, runtime, WSL, "
            "installer, Discord, bridge, adapter, platform, export, package, cleanup, deletion, "
            "or archive occurred."
        ),
    }
    result.update(NO_ACTIVITY_FLAGS)
    return result


def validate_route_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    """Validate a proposed route envelope without inferring intent or executing work."""
    if not isinstance(envelope, dict):
        return _base_result(
            "rejected",
            False,
            "",
            ["route_envelope_object"],
            ["route_envelope_must_be_dict"],
        )

    missing_requirements: list[str] = []
    blocked_conditions: list[str] = []

    for field in ROUTE_ENVELOPE_REQUIRED_FIELDS:
        if field not in envelope:
            missing_requirements.append(field)

    request_type = _normalize_text(envelope.get("request_type"))
    capability_assessment = assess_required_capabilities(_string_list(envelope.get("required_capabilities")))
    if missing_requirements:
        return _base_result(
            "rejected",
            False,
            request_type,
            missing_requirements,
            ["missing_required_envelope_fields"],
            capability_assessment=capability_assessment,
        )

    if request_type not in REQUEST_TYPES:
        _append(blocked_conditions, "unknown_request_type")

    confidence = envelope.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        _append(blocked_conditions, "confidence_must_be_numeric")
    elif not 0.0 <= float(confidence) <= 1.0:
        _append(blocked_conditions, "confidence_out_of_range")

    for field in BOOLEAN_PERMISSION_FIELDS:
        if not isinstance(envelope.get(field), bool):
            _append(blocked_conditions, f"{field}_must_be_boolean")

    for field in LIST_FIELDS:
        if not isinstance(envelope.get(field), list):
            _append(blocked_conditions, f"{field}_must_be_list")

    for field in STRING_FIELDS:
        if not isinstance(envelope.get(field), str) or not envelope.get(field).strip():
            _append(blocked_conditions, f"{field}_must_be_non_empty_string")

    required_capabilities = _string_list(envelope.get("required_capabilities"))
    capability_assessment = assess_required_capabilities(required_capabilities)
    missing_inputs = _string_list(envelope.get("missing_inputs"))
    caveats = _string_list(envelope.get("caveats"))
    risk_level = _normalize_text(envelope.get("risk_level")).lower()

    requires_operator_confirmation = envelope.get("requires_operator_confirmation") is True
    requires_external_connector = envelope.get("requires_external_connector") is True
    allowed_to_answer_directly = envelope.get("allowed_to_answer_directly") is True
    allowed_to_mutate_files = envelope.get("allowed_to_mutate_files") is True
    allowed_to_schedule = envelope.get("allowed_to_schedule") is True
    allowed_to_use_local_documents = envelope.get("allowed_to_use_local_documents") is True
    allowed_to_use_web = envelope.get("allowed_to_use_web") is True

    if capability_assessment["unknown_capabilities"]:
        _append(blocked_conditions, "unknown_required_capabilities")

    if (
        capability_assessment["blocked_or_external_capabilities"]
        and request_type not in {"unsupported_or_requires_connector", "needs_clarification"}
    ):
        _append(blocked_conditions, "blocked_or_external_required_capabilities")

    if request_type == "needs_clarification":
        if not missing_inputs:
            _append(missing_requirements, "missing_inputs")
        if any(
            (
                allowed_to_answer_directly,
                allowed_to_mutate_files,
                allowed_to_schedule,
                allowed_to_use_local_documents,
                allowed_to_use_web,
            )
        ):
            _append(blocked_conditions, "needs_clarification_must_not_enable_capabilities")

    if request_type == "unsupported_or_requires_connector":
        if any(
            (
                allowed_to_answer_directly,
                allowed_to_mutate_files,
                allowed_to_schedule,
                allowed_to_use_local_documents,
                allowed_to_use_web,
            )
        ):
            _append(blocked_conditions, "unsupported_route_must_not_enable_capabilities")

    if allowed_to_mutate_files:
        if request_type not in MUTATION_REQUEST_TYPES:
            _append(blocked_conditions, "mutation_only_allowed_for_coding_task_or_file_operation")
        if not requires_operator_confirmation:
            _append(blocked_conditions, "mutation_requires_operator_confirmation")

    if allowed_to_schedule:
        if request_type != "reminder_request":
            _append(blocked_conditions, "scheduling_only_allowed_for_reminder_request")
        if not requires_operator_confirmation:
            _append(blocked_conditions, "scheduling_requires_operator_confirmation")

    if allowed_to_use_local_documents and request_type not in LOCAL_DOCUMENT_REQUEST_TYPES:
        _append(blocked_conditions, "local_documents_only_allowed_for_local_document_lookup")

    if allowed_to_use_web:
        if request_type not in WEB_REQUEST_TYPES:
            _append(blocked_conditions, "web_only_allowed_for_research_request")
        if "web_lookup_not_implemented" not in caveats:
            _append(missing_requirements, "web_lookup_not_implemented_caveat")

    if allowed_to_answer_directly:
        direct_answer_blockers = []
        if missing_inputs:
            direct_answer_blockers.append("missing_inputs")
        if risk_level in HIGH_RISK_VALUES:
            direct_answer_blockers.append("high_risk")
        if allowed_to_mutate_files:
            direct_answer_blockers.append("mutation_allowed")
        if allowed_to_schedule:
            direct_answer_blockers.append("scheduling_allowed")
        if requires_external_connector:
            direct_answer_blockers.append("external_connector_required")
        if allowed_to_use_local_documents:
            direct_answer_blockers.append("local_documents_required")
        if allowed_to_use_web:
            direct_answer_blockers.append("web_required")
        if direct_answer_blockers:
            _append(blocked_conditions, "direct_answer_not_allowed:" + ",".join(direct_answer_blockers))

    if request_type in {"coding_task", "file_operation"} and _contains_substrate_executor_reference(envelope):
        _append(blocked_conditions, "route_must_be_substrate_agnostic")

    normalized_envelope = {
        field: deepcopy(envelope[field])
        for field in ROUTE_ENVELOPE_REQUIRED_FIELDS
    }
    if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
        normalized_envelope["confidence"] = float(confidence)
    normalized_envelope["required_capabilities"] = required_capabilities
    normalized_envelope["missing_inputs"] = missing_inputs
    normalized_envelope["caveats"] = caveats

    if request_type == "needs_clarification":
        admission = "needs_clarification"
        accepted = False
    elif request_type == "unsupported_or_requires_connector":
        admission = "rejected"
        accepted = False
        _append(blocked_conditions, "unsupported_or_requires_connector")
    else:
        admission = "accepted"
        accepted = True

    if missing_requirements or blocked_conditions:
        admission = "needs_clarification" if request_type == "needs_clarification" and not blocked_conditions else "rejected"
        accepted = False

    return _base_result(
        admission,
        accepted,
        request_type,
        missing_requirements,
        blocked_conditions,
        normalized_envelope,
        capability_assessment,
    )
