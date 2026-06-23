"""Deterministic lightweight general-answer report-only contract.

This module builds reviewable report-only artifacts for low-risk structured
``general_answer`` requests. It does not call providers, models, runtimes,
routers, RAG, web, schedulers, connectors, workers, Codex, exports, packages,
cleanup, deletion, archive, or production behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


PHASE = "PHASE_235"
ARTIFACT_KIND = "general_answer_lightweight_report_only_contract"
ACCEPTED_CLASSIFICATION = "general_answer_lightweight_report_only_accepted"
BLOCKED_CLASSIFICATION = "general_answer_lightweight_report_only_blocked"

LOW_RISK_VALUES = {"low", "routine"}
BLOCKED_RISK_VALUES = {"high", "critical"}

NO_ACTIVITY_FLAGS = {
    "mutation_performed": False,
    "execution_performed": False,
    "provider_executed": False,
    "model_executed": False,
    "runtime_executed": False,
    "wsl_executed": False,
    "ollama_executed": False,
    "hermes_executed": False,
    "openclaw_executed": False,
    "discord_executed": False,
    "rag_lookup_performed": False,
    "web_lookup_performed": False,
    "scheduler_executed": False,
    "connector_executed": False,
    "worker_dispatched": False,
    "codex_dispatched": False,
    "export_performed": False,
    "package_performed": False,
    "cleanup_performed": False,
    "deletion_performed": False,
    "archive_performed": False,
    "production_executed": False,
}

NON_PROOFS = (
    "not_semantic_correctness_proof",
    "not_model_backed_generation",
    "not_provider_execution",
    "not_runtime_execution",
    "not_live_router_proof",
    "not_rag_or_local_lookup",
    "not_web_lookup",
    "not_scheduler_or_reminder_execution",
    "not_connector_execution",
    "not_worker_dispatch",
    "not_codex_dispatch",
    "not_production_readiness",
)


@dataclass(frozen=True)
class LightweightGeneralAnswerReport:
    phase: str
    artifact_kind: str
    request_id: str
    request_type: str
    user_intent_summary: str
    accepted: bool
    outcome_classification: str
    report_text: str
    accepted_facts: tuple[str, ...]
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    caveats: tuple[str, ...]
    non_proofs: tuple[str, ...]
    recommended_next_action: str
    activity_flags: dict[str, bool]
    production_readiness: bool


@dataclass(frozen=True)
class LightweightGeneralAnswerReportResult:
    accepted: bool
    report: LightweightGeneralAnswerReport
    payload: dict[str, Any]
    rendered_text: str


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _string_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(_text(item) for item in value if _text(item))


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _truthy(request: dict[str, Any], *keys: str) -> bool:
    return any(request.get(key) is True for key in keys)


def _blockers_for_request(request: dict[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    missing: list[str] = []
    blocked: list[str] = []

    request_id = _text(request.get("request_id"))
    request_type = _text(request.get("request_type"))
    intent = _text(request.get("user_intent_summary"))
    risk_level = _text(request.get("risk_level")).lower()

    if not request_id:
        missing.append("request_id")
    if not intent:
        missing.append("user_intent_summary")

    if request_type != "general_answer":
        blocked.append("wrong_request_type")
    if risk_level in BLOCKED_RISK_VALUES:
        blocked.append("high_or_critical_risk")
    if risk_level and risk_level not in LOW_RISK_VALUES:
        blocked.append("not_low_risk_general_answer")
    if _truthy(request, "requires_file_mutation", "allowed_to_mutate_files", "requires_mutation"):
        blocked.append("requires_file_mutation")
    if _truthy(request, "requires_scheduling", "allowed_to_schedule", "requires_reminder"):
        blocked.append("requires_scheduling")
    if _truthy(
        request,
        "requires_local_documents",
        "requires_rag_lookup",
        "allowed_to_use_local_documents",
    ):
        blocked.append("requires_local_documents_or_rag")
    if _truthy(request, "requires_web_lookup", "allowed_to_use_web"):
        blocked.append("requires_web_lookup")
    if _truthy(request, "requires_external_connector", "requires_connector"):
        blocked.append("requires_external_connector")
    if _truthy(
        request,
        "requires_provider_execution",
        "requires_model_execution",
        "requires_runtime_execution",
        "provider_execution_required",
        "model_execution_required",
        "runtime_execution_required",
    ):
        blocked.append("requires_provider_model_or_runtime_execution")
    if _truthy(request, "production_readiness", "claims_production_readiness"):
        blocked.append("claims_production_readiness")

    return tuple(missing), tuple(blocked)


def _report_text(
    *,
    accepted: bool,
    user_intent_summary: str,
    blocked_conditions: tuple[str, ...],
    missing_requirements: tuple[str, ...],
) -> str:
    if accepted:
        return (
            "Report-only answer lane accepted the structured low-risk "
            f"general_answer request for review: {user_intent_summary}"
        )

    parts = []
    if blocked_conditions:
        parts.append("blocked_conditions=" + ",".join(blocked_conditions))
    if missing_requirements:
        parts.append("missing_requirements=" + ",".join(missing_requirements))
    detail = "; ".join(parts) if parts else "request_not_accepted"
    return f"Report-only answer lane blocked the request: {detail}"


def build_lightweight_general_answer_report(request: dict[str, Any]) -> LightweightGeneralAnswerReportResult:
    """Build a deterministic report-only artifact from structured request data."""

    if not isinstance(request, dict):
        request = {}

    missing_requirements, blocked_conditions = _blockers_for_request(request)
    accepted = not missing_requirements and not blocked_conditions
    request_id = _text(request.get("request_id"))
    request_type = _text(request.get("request_type"))
    user_intent_summary = _text(request.get("user_intent_summary"))
    accepted_facts = _dedupe(
        _string_tuple(request.get("accepted_facts"))
        + (
            f"request_id={request_id}" if request_id else "",
            f"request_type={request_type}" if request_type else "",
            "report_only_lane=true",
        )
    )
    caveats = _dedupe(
        _string_tuple(request.get("caveats"))
        + (
            "low_risk_structured_general_answer_only",
            "no_fact_retrieval_or_model_generation_performed",
            "operator_review_required_before_treating_as_answer_quality_proof",
        )
    )
    recommended_next_action = _text(request.get("recommended_next_action"))
    if not recommended_next_action:
        recommended_next_action = (
            "surface_report_only_answer_to_operator"
            if accepted
            else "clarify_or_route_to_separate_authorized_lane"
        )
    report_text = _report_text(
        accepted=accepted,
        user_intent_summary=user_intent_summary,
        blocked_conditions=blocked_conditions,
        missing_requirements=missing_requirements,
    )

    report = LightweightGeneralAnswerReport(
        phase=PHASE,
        artifact_kind=ARTIFACT_KIND,
        request_id=request_id,
        request_type=request_type,
        user_intent_summary=user_intent_summary,
        accepted=accepted,
        outcome_classification=ACCEPTED_CLASSIFICATION if accepted else BLOCKED_CLASSIFICATION,
        report_text=report_text,
        accepted_facts=accepted_facts,
        blocked_conditions=blocked_conditions,
        missing_requirements=missing_requirements,
        caveats=caveats,
        non_proofs=NON_PROOFS,
        recommended_next_action=recommended_next_action,
        activity_flags=dict(NO_ACTIVITY_FLAGS),
        production_readiness=False,
    )
    payload = lightweight_general_answer_report_to_dict(report)
    return LightweightGeneralAnswerReportResult(
        accepted=accepted,
        report=report,
        payload=payload,
        rendered_text=render_lightweight_general_answer_report(report),
    )


def lightweight_general_answer_report_to_dict(report: LightweightGeneralAnswerReport) -> dict[str, Any]:
    """Return a JSON-safe report payload."""

    payload = asdict(report)
    for key in (
        "accepted_facts",
        "blocked_conditions",
        "missing_requirements",
        "caveats",
        "non_proofs",
    ):
        payload[key] = list(payload[key])
    payload["activity_flags"] = dict(report.activity_flags)
    return payload


def render_lightweight_general_answer_report(report: LightweightGeneralAnswerReport) -> str:
    """Render a compact operator-reviewable report-only artifact."""

    blocked_lines = [f"- {item}" for item in report.blocked_conditions] or ["- none"]
    missing_lines = [f"- {item}" for item in report.missing_requirements] or ["- none"]
    lines = [
        "Lightweight General Answer Report",
        f"- phase={report.phase}",
        f"- artifact_kind={report.artifact_kind}",
        f"- request_id={report.request_id}",
        f"- request_type={report.request_type}",
        f"- accepted={report.accepted}",
        f"- outcome_classification={report.outcome_classification}",
        f"- production_readiness={report.production_readiness}",
        "",
        "Report",
        f"- {report.report_text}",
        "",
        "Accepted Facts",
        *[f"- {item}" for item in report.accepted_facts],
        "",
        "Blocked Conditions",
        *blocked_lines,
        "",
        "Missing Requirements",
        *missing_lines,
        "",
        "Recommended Next Action",
        f"- {report.recommended_next_action}",
        "",
        "Non-Proofs",
        *[f"- {item}" for item in report.non_proofs],
        "",
        "Caveats",
        *[f"- {item}" for item in report.caveats],
    ]
    return "\n".join(lines)
