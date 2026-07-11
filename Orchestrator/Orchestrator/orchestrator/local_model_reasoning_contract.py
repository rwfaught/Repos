"""Strict, non-executing contract for future local-model intake reasoning."""

from __future__ import annotations

import json
import re
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

OUTPUT_CLASSIFICATIONS = (
    "strict_json",
    "extracted_embedded_json",
    "rejected_malformed_json",
    "rejected_multiple_json_candidates",
    "rejected_no_json_candidate",
    "rejected_authority_or_execution_claim",
    "quarantined_ambiguous_output",
)

OUTPUT_NON_PROOFS = REASONING_NON_PROOFS + (
    "not raw model text trust",
    "not raw output normalization proof of model behavior",
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
_AUTHORITY_FIELDS = frozenset({
    "approval", "approved", "coordinator_plan", "dispatch", "dispatched",
    "execution_authorized", "execution_performed", "operator_approval",
    "production_readiness", "product_wedge", "route", "route_name",
    "worker", "worker_type", "worker_dispatch", "provider_execution",
})
_ALLOWED_WRAPPER_PREFIX_REASON = "whitespace_only_empty_think_wrapper"
_ALLOWED_WRAPPER_SUFFIX = "[end of text]"
_EMPTY_THINK_WRAPPER_PATTERN = re.compile(r"<think>\s*</think>")
_CLARIFICATION_REQUEST_WORDS = frozenset({
    "attach", "clarify", "confirm", "define", "determine", "document",
    "establish", "identify", "include", "name", "provide", "record",
    "reconcile", "resolve", "share", "show", "specify", "state", "supply",
    "verify",
})
_CLARIFICATION_SAFETY_MARKERS = (
    "authority-shaped",
    "embedded procedural injection",
    "procedural-injection",
    "prompt injection",
    "system override",
    "unsupported inference",
    "false certainty",
    "unsafe advice",
)


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


@dataclass(frozen=True)
class LocalModelOutputNormalization:
    classification: str
    raw_output: str
    candidate_json: str | None
    parsed_candidate: dict[str, Any] | None
    reasons: tuple[str, ...]
    non_proofs: tuple[str, ...] = OUTPUT_NON_PROOFS


@dataclass(frozen=True)
class LocalModelRawOutputValidation:
    classification: str
    raw_output: str
    candidate_json: str | None
    parsed_candidate: dict[str, Any] | None
    validation: InterpretationValidation | None
    accepted: bool
    reasons: tuple[str, ...]
    non_proofs: tuple[str, ...] = OUTPUT_NON_PROOFS


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


def render_local_model_interpretation_prompt(request: LocalModelInterpretationRequest) -> str:
    """Render the canonical advisory response schema for a runtime transport."""
    example = {
        "contract_version": request.contract_version,
        "request_id": request.request_id,
        "objective": request.objective,
        "normalized_objective": request.objective.lower(),
        "capability_task": {
            "task_id": "task-001",
            "title": "short capability task title",
            "objective": request.objective,
            "complexity": "simple",
            "code_generation_required": False,
            "long_context_required": False,
            "safety_risk": "low",
            "privacy_sensitivity": "internal",
            "external_tool_or_api_need": False,
            "live_runtime_execution_need": False,
            "tolerance_for_mistakes": "medium",
            "deterministic_validation_available": True,
            "local_model_output_reviewable": True,
        },
        "matched_signals": {"deterministic": ["brief supporting signal"]},
        "confidence": 0.91,
        "clarification_needed": [],
        "risk_flags": [],
        "assumptions": [],
    }
    return "\n".join((
        "Return exactly one JSON object and no prose.",
        "This is advisory intake only. Do not include route, plan, approval, worker selection, dispatch, execution, or production authority.",
        "The response fields matched_signals, confidence, clarification_needed, risk_flags, and assumptions are top-level fields, not capability_task fields.",
        "matched_signals may contain only these keys: deterministic, local_model, frontier, external, human.",
        "Do not invent matched_signals keys such as interpretation or hypotheses. Put facts, hypotheses, interpretations, conclusions, and assumptions in their canonical fields; use clarification_needed for missing prerequisites and confidence, risk_flags, and assumptions for uncertainty. Unsupported keys are rejected or quarantined. The result remains advisory evidence only.",
        "Use this exact response schema:",
        json.dumps(example, indent=2),
    ))


def _string_list(value: Any, field: str) -> tuple[tuple[str, ...] | None, str | None]:
    if not isinstance(value, (list, tuple)):
        return None, f"{field}_must_be_a_list"
    if not all(isinstance(item, str) and item.strip() for item in value):
        return None, f"{field}_must_contain_nonempty_strings"
    return tuple(item.strip() for item in value), None


def _has_responsible_clarification(
    clarification_needed: tuple[str, ...] | None,
    matched_signals: Mapping[str, list[str]],
    assumptions: tuple[str, ...] | None,
    risk_flags: tuple[str, ...] | None,
) -> bool:
    """Recognize bounded clarification without admitting vague or unsafe output."""
    if not clarification_needed or not assumptions:
        return False
    if not any(matched_signals.values()):
        return False
    if any(len(item.split()) < 3 for item in clarification_needed):
        return False
    request_pattern = r"\b(?:" + "|".join(_CLARIFICATION_REQUEST_WORDS) + r")\b"
    if not any(re.search(request_pattern, item.casefold()) for item in clarification_needed):
        return False
    risk_text = " ".join(risk_flags or ()).casefold()
    return not any(marker in risk_text for marker in _CLARIFICATION_SAFETY_MARKERS)


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
    if clarification_needed and not _has_responsible_clarification(
        clarification_needed,
        matched_signal_lists,
        assumptions,
        risk_flags,
    ):
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


def _object_start_positions(text: str) -> list[int]:
    """Find object delimiters outside quoted strings without rewriting text."""
    positions: list[int] = []
    in_string = False
    escaped = False
    for index, character in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character == "{":
            positions.append(index)
    return positions


def _parse_object_candidates(text: str) -> list[tuple[int, int, dict[str, Any]]]:
    decoder = json.JSONDecoder()
    candidates: list[tuple[int, int, dict[str, Any]]] = []
    for position in _object_start_positions(text):
        try:
            parsed, end = decoder.raw_decode(text, position)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, Mapping):
            candidates.append((position, end, dict(parsed)))
    return candidates


def _normalization(
    classification: str,
    raw_output: str,
    candidate_json: str | None = None,
    parsed_candidate: dict[str, Any] | None = None,
    reasons: tuple[str, ...] = (),
) -> LocalModelOutputNormalization:
    return LocalModelOutputNormalization(
        classification=classification,
        raw_output=raw_output,
        candidate_json=candidate_json,
        parsed_candidate=parsed_candidate,
        reasons=reasons,
    )


def normalize_local_model_output(raw_output: str) -> LocalModelOutputNormalization:
    """Classify raw text and extract at most one contract candidate.

    Only a whitespace-only ``<think>...</think>`` prefix and ``[end of text]``
    suffix are accepted as wrapper artifacts. All other prose or wrapper text
    is kept in the evidence and causes quarantine rather than silent stripping.
    """
    if not isinstance(raw_output, str) or not raw_output.strip():
        return _normalization(
            "rejected_no_json_candidate",
            raw_output if isinstance(raw_output, str) else str(raw_output),
            reasons=("raw_output_is_empty_or_not_text",),
        )

    decoder = json.JSONDecoder()
    stripped = raw_output.strip()
    try:
        parsed, end = decoder.raw_decode(stripped)
    except json.JSONDecodeError:
        parsed = None
        end = -1
    if end == len(stripped) and isinstance(parsed, Mapping):
        return _normalization("strict_json", raw_output, stripped, dict(parsed))
    if end == len(stripped) and parsed is not None:
        return _normalization(
            "rejected_malformed_json",
            raw_output,
            stripped,
            reasons=("json_object_required",),
        )

    candidates = _parse_object_candidates(raw_output)
    if not candidates:
        if "{" in raw_output or stripped.startswith("["):
            return _normalization(
                "rejected_malformed_json",
                raw_output,
                reasons=("no_parseable_json_object",),
            )
        return _normalization(
            "rejected_no_json_candidate",
            raw_output,
            reasons=("no_json_object_candidate_found",),
        )

    first_start, first_end, first_candidate = candidates[0]
    later_candidates = [candidate for candidate in candidates[1:] if candidate[0] >= first_end]
    candidate_json = raw_output[first_start:first_end]
    if later_candidates:
        return _normalization(
            "rejected_multiple_json_candidates",
            raw_output,
            candidate_json,
            first_candidate,
            reasons=("more_than_one_top_level_json_object",),
        )

    prefix = raw_output[:first_start].strip()
    suffix = raw_output[first_end:].strip()
    prefix_allowed = prefix == "" or _EMPTY_THINK_WRAPPER_PATTERN.fullmatch(prefix) is not None
    suffix_allowed = suffix in {"", _ALLOWED_WRAPPER_SUFFIX}
    if not prefix_allowed or not suffix_allowed:
        reasons = []
        if not prefix_allowed:
            reasons.append("unclassified_prefix_artifact")
        if not suffix_allowed:
            reasons.append("unclassified_suffix_artifact")
        return _normalization(
            "quarantined_ambiguous_output",
            raw_output,
            candidate_json,
            first_candidate,
            reasons=tuple(reasons),
        )

    return _normalization(
        "extracted_embedded_json",
        raw_output,
        candidate_json,
        first_candidate,
        reasons=tuple(
            artifact for artifact in (
                _ALLOWED_WRAPPER_PREFIX_REASON if prefix else "",
                _ALLOWED_WRAPPER_SUFFIX if suffix else "",
            ) if artifact
        ),
    )


def _authority_claim_fields(payload: Mapping[str, Any]) -> tuple[str, ...]:
    claims = set(payload).intersection(_AUTHORITY_FIELDS)
    capability_task = payload.get("capability_task")
    if isinstance(capability_task, Mapping):
        claims.update(f"capability_task.{field}" for field in set(capability_task).intersection(_AUTHORITY_FIELDS))
    return tuple(sorted(claims))


def validate_local_model_raw_output(
    request: LocalModelInterpretationRequest,
    raw_output: str,
) -> LocalModelRawOutputValidation:
    """Normalize raw text, preserve it, then apply the existing contract validator."""
    normalization = normalize_local_model_output(raw_output)
    if (
        normalization.classification not in {"strict_json", "extracted_embedded_json"}
        or normalization.parsed_candidate is None
    ):
        return LocalModelRawOutputValidation(
            classification=normalization.classification,
            raw_output=normalization.raw_output,
            candidate_json=normalization.candidate_json,
            parsed_candidate=None,
            validation=None,
            accepted=False,
            reasons=normalization.reasons,
        )

    validation = validate_local_model_interpretation(request, normalization.parsed_candidate)
    authority_claims = _authority_claim_fields(normalization.parsed_candidate)
    if authority_claims:
        return LocalModelRawOutputValidation(
            classification="rejected_authority_or_execution_claim",
            raw_output=normalization.raw_output,
            candidate_json=normalization.candidate_json,
            parsed_candidate=normalization.parsed_candidate,
            validation=validation,
            accepted=False,
            reasons=tuple(dict.fromkeys(
                normalization.reasons
                + validation.reasons
                + (f"authority_or_execution_fields:{','.join(authority_claims)}",)
            )),
        )

    if validation.accepted:
        return LocalModelRawOutputValidation(
            classification=normalization.classification,
            raw_output=normalization.raw_output,
            candidate_json=normalization.candidate_json,
            parsed_candidate=normalization.parsed_candidate,
            validation=validation,
            accepted=True,
            reasons=normalization.reasons,
        )

    classification = (
        "quarantined_ambiguous_output"
        if validation.status == "quarantined"
        else "rejected_malformed_json"
    )
    return LocalModelRawOutputValidation(
        classification=classification,
        raw_output=normalization.raw_output,
        candidate_json=normalization.candidate_json,
        parsed_candidate=normalization.parsed_candidate,
        validation=validation,
        accepted=False,
        reasons=tuple(dict.fromkeys(normalization.reasons + validation.reasons)),
    )
