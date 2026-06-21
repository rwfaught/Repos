from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.case_packet import CASE_PACKETS_DIR, validate_case_packet

_SAFE_CASE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = _normalize_string(item)
        if text:
            normalized.append(text)
    return normalized


def _is_safe_case_id(case_id: str) -> bool:
    return bool(case_id) and _SAFE_CASE_ID_PATTERN.fullmatch(case_id) is not None


def _extract_creation_authorization(persistence_input: dict[str, Any]) -> dict[str, Any] | None:
    for key in (
        "phase67_creation_authorization_result",
        "creation_authorization_result",
        "authorization_result",
    ):
        value = persistence_input.get(key)
        if isinstance(value, dict):
            return value

    if "creation_authorization" in persistence_input and "case_packet_creation_authorized" in persistence_input:
        return persistence_input

    return None


def _extract_operator_persistence_decision(persistence_input: dict[str, Any]) -> str:
    for key in (
        "operator_case_packet_persistence_decision",
        "operator_persistence_decision",
        "persistence_decision",
        "operator_decision",
        "decision",
    ):
        text = _normalize_string(persistence_input.get(key))
        if text:
            return text
    return ""


def _operator_authorizes_persistence(decision: str) -> bool:
    normalized = decision.strip().lower().replace("-", "_").replace(" ", "_")
    approved_decisions = {
        "authorize_case_packet_persistence",
        "approve_case_packet_persistence",
        "case_packet_persistence_authorized",
        "persist_case_packet",
        "authorize_persistence",
        "approved_case_packet_persistence",
    }
    return normalized in approved_decisions


def _operator_decision_is_ambiguous_or_deferral(decision: str) -> bool:
    normalized = decision.strip().lower().replace("-", "_").replace(" ", "_")
    if not normalized:
        return True
    ambiguous_decisions = {
        "maybe",
        "not_yet",
        "hold",
        "pause",
        "review_more",
        "needs_more_review",
        "inspect_more",
        "preview",
        "preview_first",
        "defer",
        "later",
        "change_boundary",
        "different_case_boundary",
        "no",
        "deny",
        "decline",
    }
    return normalized in ambiguous_decisions


def _contains_forbidden_runtime_or_platform_request(value: Any) -> bool:
    if isinstance(value, dict):
        fields = [
            value.get("requested_action"),
            value.get("requested_behavior"),
            value.get("authorized_next_action"),
            value.get("execution_request"),
            value.get("platform_request"),
            value.get("operator_request"),
            value.get("operator_decision"),
            value.get("decision"),
        ]
    else:
        fields = [value]

    forbidden_terms = [
        "task",
        "planner",
        "runtime",
        "model",
        "ollama",
        "platform",
        "discord",
        "openclaw",
        "bridge",
        "adapter",
        "installer",
        "wsl",
        "execute",
        "execution",
        "run",
        "vendor",
        "cleanup",
        "delete",
        "archive",
        "codex",
    ]

    allowed_exact = {
        "authorize_case_packet_persistence",
        "approve_case_packet_persistence",
        "case_packet_persistence_authorized",
        "persist_case_packet",
        "authorize_persistence",
        "approved_case_packet_persistence",
        "operator_may_choose_explicit_case_packet_persistence_boundary",
    }

    for field in fields:
        text = _normalize_string(field).lower()
        if not text:
            continue
        normalized = text.replace("-", "_").replace(" ", "_")
        if normalized in allowed_exact:
            continue
        if any(term in text for term in forbidden_terms):
            return True

    return False


def _authorization_has_forbidden_activity(authorization: dict[str, Any]) -> list[str]:
    blocked_conditions: list[str] = []
    forbidden_true_fields = {
        "case_packet_created": "authorization_implies_case_packet_creation",
        "case_packet_persisted": "authorization_implies_case_packet_persistence",
        "task_created": "authorization_implies_task_creation",
        "planner_invoked": "authorization_implies_planner_invocation",
        "mutation_performed": "authorization_implies_mutation",
        "execution_performed": "authorization_implies_execution",
        "runtime_executed": "authorization_implies_runtime_execution",
        "model_executed": "authorization_implies_model_execution",
        "platform_invoked": "authorization_implies_platform_execution",
    }
    for field, condition in forbidden_true_fields.items():
        if bool(authorization.get(field)):
            blocked_conditions.append(condition)

    if _contains_forbidden_runtime_or_platform_request(authorization):
        blocked_conditions.append("unsupported_execution_or_platform_request")

    return blocked_conditions


def _persistence_result(
    persistence: str,
    persisted: bool,
    reason: str,
    detail: str,
    next_action: str,
    operator_decision: str = "",
    case_id: str = "",
    path: str = "",
    missing_requirements: list[str] | None = None,
    blocked_conditions: list[str] | None = None,
    phase67_authorization_summary: dict[str, Any] | None = None,
    phase66_seed_review_summary: dict[str, Any] | None = None,
    phase65_admission_summary: dict[str, Any] | None = None,
    seed_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "case_packet_persistence": persistence,
        "case_packet_persisted": persisted,
        "case_packet_created": persisted,
        "case_id": case_id,
        "path": path,
        "reason": reason,
        "detail": detail,
        "operator_decision": operator_decision,
        "next_action": next_action,
        "task_created": False,
        "planner_invoked": False,
        "runtime_executed": False,
        "model_executed": False,
        "platform_invoked": False,
        "mutation_performed": persisted,
        "execution_performed": False,
        "missing_requirements": list(missing_requirements or []),
        "blocked_conditions": list(blocked_conditions or []),
        "phase67_authorization_summary": dict(phase67_authorization_summary or {}),
        "phase66_seed_review_summary": dict(phase66_seed_review_summary or {}),
        "phase65_admission_summary": dict(phase65_admission_summary or {}),
        "seed_summary": dict(seed_summary or {}),
    }


def _blocked_persistence(
    reason: str,
    detail: str,
    operator_decision: str = "",
    case_id: str = "",
    path: str = "",
    blocked_conditions: list[str] | None = None,
    phase67_authorization_summary: dict[str, Any] | None = None,
    phase66_seed_review_summary: dict[str, Any] | None = None,
    phase65_admission_summary: dict[str, Any] | None = None,
    seed_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _persistence_result(
        persistence="blocked",
        persisted=False,
        reason=reason,
        detail=detail,
        operator_decision=operator_decision,
        case_id=case_id,
        path=path,
        blocked_conditions=blocked_conditions,
        phase67_authorization_summary=phase67_authorization_summary,
        phase66_seed_review_summary=phase66_seed_review_summary,
        phase65_admission_summary=phase65_admission_summary,
        seed_summary=seed_summary,
        next_action="resolve_blocked_condition",
    )


def _needs_operator_decision_persistence(
    reason: str,
    detail: str,
    operator_decision: str = "",
    case_id: str = "",
    missing_requirements: list[str] | None = None,
    phase67_authorization_summary: dict[str, Any] | None = None,
    phase66_seed_review_summary: dict[str, Any] | None = None,
    phase65_admission_summary: dict[str, Any] | None = None,
    seed_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _persistence_result(
        persistence="needs_operator_decision",
        persisted=False,
        reason=reason,
        detail=detail,
        operator_decision=operator_decision,
        case_id=case_id,
        missing_requirements=missing_requirements,
        phase67_authorization_summary=phase67_authorization_summary,
        phase66_seed_review_summary=phase66_seed_review_summary,
        phase65_admission_summary=phase65_admission_summary,
        seed_summary=seed_summary,
        next_action="request_explicit_operator_case_packet_persistence_decision",
    )


def _build_case_packet(
    case_id: str,
    authorization: dict[str, Any],
    seed_summary: dict[str, Any],
    operator_decision: str,
) -> dict[str, Any]:
    objective = _normalize_string(seed_summary.get("objective_text"))
    provided_artifacts = _normalize_string_list(seed_summary.get("provided_artifacts"))
    title = _normalize_string(seed_summary.get("title")) or objective[:80] or case_id

    phase67_authorization_summary = {
        "creation_authorization": authorization.get("creation_authorization"),
        "case_packet_creation_authorized": bool(authorization.get("case_packet_creation_authorized", False)),
        "reason": authorization.get("reason", ""),
        "operator_decision": authorization.get("operator_decision", ""),
        "next_action": authorization.get("next_action", ""),
    }

    return {
        "case_id": case_id,
        "case_type": "orchestrator_intake",
        "title": title,
        "objective": objective,
        "status": "created",
        "next_step": "operator_review_case_packet_before_task_creation",
        "counterparties": [],
        "source_materials": provided_artifacts,
        "extracted_facts": [],
        "timeline_events": [],
        "open_issues": [],
        "missing_evidence": [],
        "contradictions": [],
        "drafts": [],
        "decisions": [
            {
                "phase": "Phase 67",
                "decision": "case_packet_creation_authorized",
                "operator_decision": authorization.get("operator_decision", ""),
            },
            {
                "phase": "Phase 68",
                "decision": "case_packet_persisted",
                "operator_decision": operator_decision,
            },
        ],
        "source_intake_linkage": _normalize_string(seed_summary.get("source_intake_linkage")),
        "phase65_admission_summary": authorization.get("admission_summary", {}),
        "phase66_seed_review_summary": authorization.get("seed_review_summary", {}),
        "phase67_authorization_summary": phase67_authorization_summary,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "persistence_status": "persisted",
    }


def persist_case_packet_from_creation_authorization(persistence_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(persistence_input, dict):
        return _needs_operator_decision_persistence(
            reason="Persistence input must be a JSON object.",
            detail="The Phase 68 persistence gate received a non-object input.",
            missing_requirements=["json_object_input"],
        )

    authorization = _extract_creation_authorization(persistence_input)
    operator_decision = _extract_operator_persistence_decision(persistence_input)
    case_id = _normalize_string(persistence_input.get("case_id"))
    persistence_target = _normalize_string(persistence_input.get("persistence_target")) or "product_case_packet_store"

    if not isinstance(authorization, dict):
        return _needs_operator_decision_persistence(
            reason="Persistence input lacks a Phase 67 creation authorization result.",
            detail="Provide phase67_creation_authorization_result or a direct Phase 67 authorization result.",
            operator_decision=operator_decision,
            case_id=case_id,
            missing_requirements=["phase67_creation_authorization_result"],
        )

    seed_summary = authorization.get("seed_summary") if isinstance(authorization.get("seed_summary"), dict) else {}
    phase66_seed_review_summary = (
        authorization.get("seed_review_summary") if isinstance(authorization.get("seed_review_summary"), dict) else {}
    )
    phase65_admission_summary = (
        authorization.get("admission_summary") if isinstance(authorization.get("admission_summary"), dict) else {}
    )
    phase67_authorization_summary = {
        "creation_authorization": authorization.get("creation_authorization"),
        "case_packet_creation_authorized": bool(authorization.get("case_packet_creation_authorized", False)),
        "reason": authorization.get("reason", ""),
        "operator_decision": authorization.get("operator_decision", ""),
        "next_action": authorization.get("next_action", ""),
    }

    forbidden_conditions = _authorization_has_forbidden_activity(authorization)
    if forbidden_conditions:
        return _blocked_persistence(
            reason="Phase 67 authorization result implies forbidden prior activity.",
            detail="Phase 68 cannot persist from an authorization result that already implies creation, persistence, task creation, planner invocation, mutation, execution, or platform behavior.",
            operator_decision=operator_decision,
            case_id=case_id,
            blocked_conditions=forbidden_conditions,
            phase67_authorization_summary=phase67_authorization_summary,
            phase66_seed_review_summary=phase66_seed_review_summary,
            phase65_admission_summary=phase65_admission_summary,
            seed_summary=seed_summary,
        )

    if (
        _normalize_string(authorization.get("creation_authorization")) != "creation_authorized"
        or not bool(authorization.get("case_packet_creation_authorized", False))
    ):
        return _blocked_persistence(
            reason="Only Phase 67 creation_authorized results may reach persistence.",
            detail="Phase 68 requires creation_authorization=creation_authorized and case_packet_creation_authorized=true.",
            operator_decision=operator_decision,
            case_id=case_id,
            blocked_conditions=["phase67_creation_authorization_not_authorized"],
            phase67_authorization_summary=phase67_authorization_summary,
            phase66_seed_review_summary=phase66_seed_review_summary,
            phase65_admission_summary=phase65_admission_summary,
            seed_summary=seed_summary,
        )

    if persistence_target != "product_case_packet_store":
        return _blocked_persistence(
            reason="Persistence target is outside the product case-packet store.",
            detail="Phase 68 permits only persistence_target=product_case_packet_store.",
            operator_decision=operator_decision,
            case_id=case_id,
            blocked_conditions=["persistence_target_outside_product_case_packet_store"],
            phase67_authorization_summary=phase67_authorization_summary,
            phase66_seed_review_summary=phase66_seed_review_summary,
            phase65_admission_summary=phase65_admission_summary,
            seed_summary=seed_summary,
        )

    if _contains_forbidden_runtime_or_platform_request(persistence_input):
        return _blocked_persistence(
            reason="Persistence request includes forbidden bundled behavior.",
            detail="Phase 68 may persist one case packet only; it cannot bundle task, planner, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, vendoring, cleanup, archive, delete, or Codex behavior.",
            operator_decision=operator_decision,
            case_id=case_id,
            blocked_conditions=["unsupported_bundled_behavior_request"],
            phase67_authorization_summary=phase67_authorization_summary,
            phase66_seed_review_summary=phase66_seed_review_summary,
            phase65_admission_summary=phase65_admission_summary,
            seed_summary=seed_summary,
        )

    missing_requirements: list[str] = []
    if not case_id:
        missing_requirements.append("case_id")
    if not _normalize_string(seed_summary.get("objective_text")):
        missing_requirements.append("seed_objective_text")
    if not isinstance(seed_summary.get("provided_artifacts"), list):
        missing_requirements.append("seed_provided_artifacts_list")
    if not _normalize_string(seed_summary.get("source_intake_linkage")):
        missing_requirements.append("source_intake_linkage")
    if _normalize_string(seed_summary.get("seed_status")) != "candidate_only_not_created":
        missing_requirements.append("seed_status_candidate_only_not_created")
    if _normalize_string(seed_summary.get("creation_status")) != "not_created":
        missing_requirements.append("seed_creation_status_not_created")

    if missing_requirements:
        return _needs_operator_decision_persistence(
            reason="Persistence input is not complete enough to write a case packet.",
            detail="Phase 68 requires a case id and a complete Phase 67 seed summary before persistence.",
            operator_decision=operator_decision,
            case_id=case_id,
            missing_requirements=missing_requirements,
            phase67_authorization_summary=phase67_authorization_summary,
            phase66_seed_review_summary=phase66_seed_review_summary,
            phase65_admission_summary=phase65_admission_summary,
            seed_summary=seed_summary,
        )

    if not _is_safe_case_id(case_id):
        return _blocked_persistence(
            reason="Case packet id is unsafe.",
            detail="case_id must contain only letters, numbers, dots, underscores, or hyphens and must start with a letter or number.",
            operator_decision=operator_decision,
            case_id=case_id,
            blocked_conditions=["unsafe_case_id"],
            phase67_authorization_summary=phase67_authorization_summary,
            phase66_seed_review_summary=phase66_seed_review_summary,
            phase65_admission_summary=phase65_admission_summary,
            seed_summary=seed_summary,
        )

    if not operator_decision:
        return _needs_operator_decision_persistence(
            reason="Explicit operator case-packet persistence decision is required.",
            detail="The Phase 67 authorization is valid, but this boundary still needs explicit persistence approval.",
            operator_decision=operator_decision,
            case_id=case_id,
            missing_requirements=["operator_case_packet_persistence_decision"],
            phase67_authorization_summary=phase67_authorization_summary,
            phase66_seed_review_summary=phase66_seed_review_summary,
            phase65_admission_summary=phase65_admission_summary,
            seed_summary=seed_summary,
        )

    if not _operator_authorizes_persistence(operator_decision):
        if _operator_decision_is_ambiguous_or_deferral(operator_decision):
            return _needs_operator_decision_persistence(
                reason="Operator decision does not explicitly authorize case-packet persistence.",
                detail="Phase 68 requires an explicit approval token such as authorize_case_packet_persistence.",
                operator_decision=operator_decision,
                case_id=case_id,
                missing_requirements=["explicit_operator_case_packet_persistence_authorization"],
                phase67_authorization_summary=phase67_authorization_summary,
                phase66_seed_review_summary=phase66_seed_review_summary,
                phase65_admission_summary=phase65_admission_summary,
                seed_summary=seed_summary,
            )
        return _blocked_persistence(
            reason="Operator request is not an allowed case-packet persistence decision.",
            detail="The operator decision must not bypass or expand the Phase 68 persistence gate.",
            operator_decision=operator_decision,
            case_id=case_id,
            blocked_conditions=["unsupported_operator_persistence_decision"],
            phase67_authorization_summary=phase67_authorization_summary,
            phase66_seed_review_summary=phase66_seed_review_summary,
            phase65_admission_summary=phase65_admission_summary,
            seed_summary=seed_summary,
        )

    target_dir = CASE_PACKETS_DIR
    path = target_dir / f"{case_id}.json"

    if path.exists():
        return _blocked_persistence(
            reason="Case packet already exists.",
            detail="Phase 68 will not overwrite an existing case packet.",
            operator_decision=operator_decision,
            case_id=case_id,
            path=str(path),
            blocked_conditions=["case_packet_already_exists"],
            phase67_authorization_summary=phase67_authorization_summary,
            phase66_seed_review_summary=phase66_seed_review_summary,
            phase65_admission_summary=phase65_admission_summary,
            seed_summary=seed_summary,
        )

    packet = _build_case_packet(case_id, authorization, seed_summary, operator_decision)
    validation = validate_case_packet(packet)
    if not validation.get("valid", False):
        return _blocked_persistence(
            reason="Constructed case packet is invalid.",
            detail="Phase 68 refused to persist because the constructed packet failed case-packet validation.",
            operator_decision=operator_decision,
            case_id=case_id,
            blocked_conditions=list(validation.get("errors", [])),
            phase67_authorization_summary=phase67_authorization_summary,
            phase66_seed_review_summary=phase66_seed_review_summary,
            phase65_admission_summary=phase65_admission_summary,
            seed_summary=seed_summary,
        )

    target_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2), encoding="utf-8")

    return _persistence_result(
        persistence="persisted",
        persisted=True,
        reason="Authorized case packet persisted.",
        detail="Phase 68 persisted one case packet only; no task, planner output, runtime execution, model execution, or platform behavior was created.",
        operator_decision=operator_decision,
        case_id=case_id,
        path=str(path),
        phase67_authorization_summary=phase67_authorization_summary,
        phase66_seed_review_summary=phase66_seed_review_summary,
        phase65_admission_summary=phase65_admission_summary,
        seed_summary=seed_summary,
        next_action="operator_may_review_persisted_case_packet_before_any_task_or_planner_boundary",
    )
