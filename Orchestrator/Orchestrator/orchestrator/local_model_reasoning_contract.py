"""Strict, non-executing contract for future local-model intake reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


CONTRACT_VERSION = "local_model_reasoning_v1"
MIN_ACCEPTED_CONFIDENCE = 0.70

REASONING_NON_PROOFS = (
    "not local model execution",
    "not provider execution",
    "not model competence",
    "not semantic correctness",
    "not route authorization",
    "not coordinator planning",
    "not worker dispatch",
    "not operator approval",
)

_RESPONSE_FIELDS = frozenset({
    "contract_version",
    "request_id",
    "objective",
    "normalized_objective",
    "capability_task",
    "matched_signals",
    "confidence",
    "clarification_needed",
    "risk_flags",
    "assumptions",
})
_CAPABILITY_FIELDS = frozenset({
    "task_id", "title", "objective", "complexity", "code_generation_required",
    "long_context_required", "safety_risk", "privacy_sensitivity",
    "external_tool_or_api_need", "live_runtime_execution_need",
    "tolerance_for_mistakes", "deterministic_validation_available",
    "local_model_output_reviewable",
})
_SIGNAL_CATEGORIES = frozenset({"deterministic", "local_model", "frontier", "external", "human"})
_ENUM_VALUES = {
    "complexity": {"simple", "moderate", "high"},
    "safety_risk": {"low", "medium", "high", "critical"},
    "privacy_sensitivity": {"public", "internal", "sensitive", "regulated"},
    "tolerance_for_mistakes": {"high", "medium", "low", "zero"},
}
_HIGH_RISK_FLAGS = frozenset({"high_consequence", "regulated", "sensitive_data", "legal", "medical", "financial"})


@dataclass(frozen=True)
class LocalModelInterpretationRequest:
    request_id: str
    objective: str
    requested_outcome: str = ""
    owner_context: str = ""
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class StructuredModelInterpretation:
    request_id: str
    objective: str
    normalized_objective: str
    capability_task: dict[str, Any]
    matched_signals: dict[str, list[str]]
    confidence: float
    clarification_needed: tuple[str, ...]
    risk_flags: tuple[str, ...]
    assumptions: tuple[str, ...]
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class InterpretationValidation:
    status: str
    accepted: bool
    interpretation: StructuredModelInterpretation | None
    reasons: tuple[str, ...]
    non_proofs: tuple[str, ...] = REASONING_NON_PROOFS


def build_local_model_interpretation_request(
    request_id: str,
    objective: str,
    requested_outcome: str = "",
    owner_context: str = "",
) -> LocalModelInterpretationRequest:
    return LocalModelInterpretationRequest(
        request_id=str(request_id).strip(),
        objective=str(objective),
        requested_outcome=str(requested_outcome),
        owner_context=str(owner_context),
    )


def interpretation_request_to_dict(request: LocalModelInterpretationRequest) -> dict[str, Any]:
    return asdict(request)


def _string_list(value: Any, field: str) -> tuple[tuple[str, ...] | None, str | None]:
    if not isinstance(value, (list, tuple)):
        return None, f"{field}_must_be_a_list"
    if not all(isinstance(item, str) and item.strip() for item in value):
        return None, f"{field}_must_contain_nonempty_strings"
    return tuple(item.strip() for item in value), None


def _validate_capability_task(value: Any) -> tuple[dict[str, Any] | None, tuple[str, ...]]:
    if not isinstance(value, Mapping):
        return None, ("capability_task_must_be_an_object",)
    reasons: list[str] = []
    extra = sorted(set(value) - _CAPABILITY_FIELDS)
    if extra:
        reasons.append(f"capability_task_has_unsupported_fields:{','.join(extra)}")
    task = dict(value)
    for field in ("task_id", "title", "objective"):
        if not isinstance(task.get(field), str) or not task[field].strip():
            reasons.append(f"capability_task_{field}_must_be_nonempty_string")
    for field in (
        "code_generation_required", "long_context_required", "external_tool_or_api_need",
        "live_runtime_execution_need", "deterministic_validation_available",
        "local_model_output_reviewable",
    ):
        if type(task.get(field)) is not bool:
            reasons.append(f"capability_task_{field}_must_be_boolean")
    for field, allowed in _ENUM_VALUES.items():
        if task.get(field) not in allowed:
            reasons.append(f"capability_task_{field}_invalid")
    return (task if not reasons else None), tuple(reasons)


def validate_local_model_interpretation(
    request: LocalModelInterpretationRequest,
    payload: Any,
) -> InterpretationValidation:
    """Validate and quarantine model-shaped data before policy consumes it."""
    if not isinstance(payload, Mapping):
        return InterpretationValidation("rejected", False, None, ("response_must_be_an_object",))

    reasons: list[str] = []
    extra = sorted(set(payload) - _RESPONSE_FIELDS)
    missing = sorted(_RESPONSE_FIELDS - set(payload))
    if extra:
        reasons.append(f"unsupported_response_fields:{','.join(extra)}")
    if missing:
        reasons.append(f"missing_response_fields:{','.join(missing)}")
    if reasons:
        return InterpretationValidation("rejected", False, None, tuple(reasons))

    if payload["contract_version"] != CONTRACT_VERSION:
        reasons.append("unsupported_contract_version")
    if str(payload["request_id"]).strip() != request.request_id:
        reasons.append("request_id_mismatch")
    if str(payload["objective"]).strip() != request.objective.strip():
        reasons.append("objective_mismatch")
    if not isinstance(payload["normalized_objective"], str) or not payload["normalized_objective"].strip():
        reasons.append("normalized_objective_must_be_nonempty_string")
    if type(payload["confidence"]) not in (int, float):
        reasons.append("confidence_must_be_numeric")
    elif not 0.0 <= float(payload["confidence"]) <= 1.0:
        reasons.append("confidence_must_be_between_zero_and_one")

    clarification_needed, clarification_error = _string_list(payload["clarification_needed"], "clarification_needed")
    risk_flags, risk_error = _string_list(payload["risk_flags"], "risk_flags")
    assumptions, assumptions_error = _string_list(payload["assumptions"], "assumptions")
    for error in (clarification_error, risk_error, assumptions_error):
        if error:
            reasons.append(error)

    matched_signals = payload["matched_signals"]
    matched_signal_lists: dict[str, list[str]] = {}
    if not isinstance(matched_signals, Mapping):
        reasons.append("matched_signals_must_be_an_object")
    else:
        unknown_categories = sorted(set(matched_signals) - _SIGNAL_CATEGORIES)
        if unknown_categories:
            reasons.append(f"matched_signals_has_unsupported_categories:{','.join(unknown_categories)}")
        for category, signals in matched_signals.items():
            parsed, error = _string_list(signals, f"matched_signals_{category}")
            if error:
                reasons.append(error)
            else:
                matched_signal_lists[category] = list(parsed or ())

    capability_task, capability_reasons = _validate_capability_task(payload["capability_task"])
    reasons.extend(capability_reasons)
    if clarification_needed:
        reasons.append("model_interpretation_is_ambiguous")
    if capability_task is None and not capability_reasons:
        reasons.append("capability_task_is_required_for_accepted_interpretation")

    confidence = float(payload["confidence"]) if type(payload["confidence"]) in (int, float) else 0.0
    if confidence < MIN_ACCEPTED_CONFIDENCE:
        reasons.append("model_confidence_below_acceptance_threshold")

    if capability_task is not None:
        high_risk = capability_task["safety_risk"] in {"high", "critical"} or capability_task["privacy_sensitivity"] == "regulated"
        if high_risk or set(risk_flags or ()).intersection(_HIGH_RISK_FLAGS):
            reasons.append("high_risk_interpretation_requires_owner_review")

    if reasons:
        quarantine_reasons = {
            "model_interpretation_is_ambiguous",
            "model_confidence_below_acceptance_threshold",
            "high_risk_interpretation_requires_owner_review",
        }
        status = "quarantined" if any(reason in quarantine_reasons for reason in reasons) else "rejected"
        return InterpretationValidation(status, False, None, tuple(dict.fromkeys(reasons)))

    interpretation = StructuredModelInterpretation(
        request_id=request.request_id,
        objective=request.objective,
        normalized_objective=payload["normalized_objective"].strip(),
        capability_task=capability_task or {},
        matched_signals=matched_signal_lists,
        confidence=confidence,
        clarification_needed=clarification_needed or (),
        risk_flags=risk_flags or (),
        assumptions=assumptions or (),
        contract_version=payload["contract_version"],
    )
    return InterpretationValidation("accepted", True, interpretation, ())
