"""Deterministic local-first/fallback policy for general-answer requests.

The policy is report-only metadata. It does not generate answers, execute
providers/models/runtimes, perform lookup, dispatch workers, or expose
service/API/UI behavior.
"""

from __future__ import annotations

from typing import Any


FALSE_EXECUTION_FLAGS = (
    "execution_authorized",
    "answer_generation_authorized",
    "production_readiness",
    "provider_execution",
    "model_execution",
    "runtime_execution",
    "rag_lookup",
    "web_lookup",
    "scheduler_execution",
    "connector_execution",
    "worker_dispatch",
    "codex_dispatch",
    "service_api_ui",
)

LOW_RISK_VALUES = {"low", "routine"}
HIGH_RISK_VALUES = {"high", "critical"}

EXECUTION_REQUEST_FIELDS = {
    "requires_provider_execution": ("provider_execution", "provider_execution_requested"),
    "provider_execution_required": ("provider_execution", "provider_execution_requested"),
    "requires_model_execution": ("model_execution", "model_execution_requested"),
    "model_execution_required": ("model_execution", "model_execution_requested"),
    "requires_runtime_execution": ("runtime_execution", "runtime_execution_requested"),
    "runtime_execution_required": ("runtime_execution", "runtime_execution_requested"),
    "requires_rag_lookup": ("rag_lookup", "rag_lookup_requested"),
    "requires_local_documents": ("rag_lookup", "rag_lookup_requested"),
    "allowed_to_use_local_documents": ("rag_lookup", "rag_lookup_requested"),
    "requires_web_lookup": ("web_lookup", "web_lookup_requested"),
    "allowed_to_use_web": ("web_lookup", "web_lookup_requested"),
    "requires_scheduling": ("scheduler_execution", "scheduler_execution_requested"),
    "allowed_to_schedule": ("scheduler_execution", "scheduler_execution_requested"),
    "requires_reminder": ("scheduler_execution", "scheduler_execution_requested"),
    "requires_external_connector": ("connector_execution", "connector_execution_requested"),
    "requires_connector": ("connector_execution", "connector_execution_requested"),
    "requires_worker_dispatch": ("worker_dispatch", "worker_dispatch_requested"),
    "worker_dispatch": ("worker_dispatch", "worker_dispatch_requested"),
    "requires_codex_dispatch": ("codex_dispatch", "codex_dispatch_requested"),
    "codex_dispatch": ("codex_dispatch", "codex_dispatch_requested"),
    "requires_service_api_ui": ("service_api_ui", "service_api_ui_requested"),
    "requires_service": ("service_api_ui", "service_api_ui_requested"),
    "requires_api": ("service_api_ui", "service_api_ui_requested"),
    "requires_ui": ("service_api_ui", "service_api_ui_requested"),
    "service_api_ui": ("service_api_ui", "service_api_ui_requested"),
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _string_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(text for text in (_text(item) for item in value) if text)


def _dedupe(values: tuple[str, ...]) -> list[str]:
    return list(dict.fromkeys(item for item in values if item))


def _truthy(request: dict[str, Any], key: str) -> bool:
    return request.get(key) is True


def _base_policy(request_type: str, *, enabled: bool = True) -> dict[str, Any]:
    policy: dict[str, Any] = {
        "request_type": request_type,
        "local_first_policy_enabled": enabled,
        "report_only": True,
        "recommended_answer_posture": "",
        "fallback_posture": "manual_review",
        "clarification_required": False,
        "block_required": False,
        "missing_requirements": [],
        "blockers": [],
        "caveats": [
            "policy_only_not_answer_generation",
            "local_first_policy_does_not_execute",
            "manual_review_fallback_remains_report_only",
        ],
    }
    for flag in FALSE_EXECUTION_FLAGS:
        policy[flag] = False
    return policy


def _execution_blockers(request: dict[str, Any]) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    caveats: list[str] = []
    for key, (_flag, blocker) in EXECUTION_REQUEST_FIELDS.items():
        if _truthy(request, key):
            blockers.append(blocker)
            caveats.append(f"{key}_not_authorized")
    return _dedupe(tuple(blockers)), _dedupe(tuple(caveats))


def build_general_answer_local_first_fallback_policy(request: dict[str, Any]) -> dict[str, Any]:
    """Return JSON-safe local-first/fallback policy metadata."""

    if not isinstance(request, dict):
        request = {}

    request_type = _text(request.get("request_type"))
    if request_type != "general_answer":
        policy = _base_policy(request_type, enabled=False)
        policy["recommended_answer_posture"] = "not_applicable"
        policy["fallback_posture"] = "route_by_request_type"
        policy["caveats"] = _dedupe(
            tuple(policy["caveats"]) + ("non_general_answer_request_not_evaluated",)
        )
        return policy

    policy = _base_policy(request_type, enabled=True)
    missing: list[str] = []
    blockers: list[str] = []

    risk_level = _text(request.get("risk_level")).lower()
    intent = _text(request.get("user_intent_summary"))
    accepted_facts = _string_tuple(request.get("accepted_facts"))

    if not intent:
        missing.append("user_intent_summary")
    if not accepted_facts:
        missing.append("accepted_facts")

    execution_blockers, execution_caveats = _execution_blockers(request)
    blockers.extend(execution_blockers)

    if execution_blockers:
        policy["recommended_answer_posture"] = "blocked_execution_request"
        policy["fallback_posture"] = "manual_review"
        policy["block_required"] = True
        policy["blockers"] = _dedupe(tuple(blockers))
        policy["missing_requirements"] = _dedupe(tuple(missing))
        policy["caveats"] = _dedupe(tuple(policy["caveats"]) + tuple(execution_caveats))
        return policy

    if risk_level in HIGH_RISK_VALUES:
        blockers.append("high_or_critical_risk")
        policy["recommended_answer_posture"] = "manual_review_or_block"
        policy["fallback_posture"] = "manual_review"
        policy["block_required"] = True
        policy["blockers"] = _dedupe(tuple(blockers))
        policy["missing_requirements"] = _dedupe(tuple(missing))
        policy["caveats"] = _dedupe(tuple(policy["caveats"]) + ("high_risk_not_local_first_answerable",))
        return policy

    if risk_level not in LOW_RISK_VALUES:
        blockers.append("unknown_or_non_low_risk")
        policy["recommended_answer_posture"] = "manual_review_or_block"
        policy["fallback_posture"] = "manual_review"
        policy["block_required"] = True
        policy["blockers"] = _dedupe(tuple(blockers))
        policy["missing_requirements"] = _dedupe(tuple(missing))
        policy["caveats"] = _dedupe(tuple(policy["caveats"]) + ("unknown_risk_not_local_first_answerable",))
        return policy

    if missing:
        policy["recommended_answer_posture"] = "clarify_before_answer"
        policy["fallback_posture"] = "manual_review"
        policy["clarification_required"] = True
        policy["missing_requirements"] = _dedupe(tuple(missing))
        policy["caveats"] = _dedupe(tuple(policy["caveats"]) + ("accepted_local_facts_required",))
        return policy

    policy["recommended_answer_posture"] = "local_report_only_answer_candidate"
    policy["fallback_posture"] = "manual_review"
    policy["missing_requirements"] = []
    policy["blockers"] = []
    policy["caveats"] = _dedupe(
        tuple(policy["caveats"])
        + (
            "sufficient_local_facts_observed",
            "answer_candidate_requires_manual_review_before_use",
        )
    )
    return policy
