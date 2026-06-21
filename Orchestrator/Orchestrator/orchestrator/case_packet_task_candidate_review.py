from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.case_packet import CASE_PACKETS_DIR, summarize_case_packet, validate_case_packet

_SAFE_CASE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [text for item in value if (text := _normalize_string(item))]


def _is_safe_case_id(case_id: str) -> bool:
    return bool(case_id) and _SAFE_CASE_ID_PATTERN.fullmatch(case_id) is not None


def _case_packet_path(case_id: str) -> Path:
    return CASE_PACKETS_DIR / f"{case_id}.json"


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _extract_case_packet_reference(review_input: dict[str, Any]) -> tuple[dict[str, Any] | None, str, str, list[str]]:
    case_id = _normalize_string(review_input.get("case_id"))
    case_packet_path_text = _normalize_string(review_input.get("case_packet_path"))
    direct_packet = review_input.get("case_packet")

    if case_id:
        if not _is_safe_case_id(case_id):
            return None, case_id, "", ["unsafe_case_id"]
        path = _case_packet_path(case_id)
        if not path.exists() or not path.is_file():
            return None, case_id, str(path), ["case_packet_not_found"]
        packet = _read_json_object(path)
        if packet is None:
            return None, case_id, str(path), ["case_packet_json_invalid_or_unreadable"]
        return packet, case_id, str(path), []

    if case_packet_path_text:
        path = Path(case_packet_path_text)
        if not path.is_absolute():
            path = CASE_PACKETS_DIR / path
        if not path.exists() or not path.is_file():
            return None, "", str(path), ["case_packet_not_found"]
        try:
            store_root = CASE_PACKETS_DIR.resolve()
            candidate_parent = path.resolve().parent
        except OSError:
            return None, "", str(path), ["case_packet_path_unresolvable"]
        if candidate_parent != store_root:
            return None, "", str(path), ["case_packet_path_outside_product_case_packet_store"]
        packet = _read_json_object(path)
        if packet is None:
            return None, "", str(path), ["case_packet_json_invalid_or_unreadable"]
        return packet, _normalize_string(packet.get("case_id")), str(path), []

    if isinstance(direct_packet, dict):
        return direct_packet, _normalize_string(direct_packet.get("case_id")), "", ["case_packet_not_loaded_from_product_case_packet_store"]

    return None, "", "", ["case_packet_reference_missing"]


def _contains_forbidden_bundled_request(value: Any) -> bool:
    fields = []
    if isinstance(value, dict):
        for key in (
            "requested_action",
            "requested_behavior",
            "authorized_next_action",
            "requested_next_move",
            "execution_request",
            "platform_request",
            "operator_request",
            "operator_decision",
            "decision",
        ):
            fields.append(value.get(key))
    else:
        fields.append(value)

    forbidden_terms = [
        "create task",
        "task creation",
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
        "run model",
        "vendor",
        "cleanup",
        "delete",
        "archive",
        "codex",
    ]

    allowed_exact = {
        "review_persisted_case_packet",
        "case_packet_task_candidate_review",
        "review_case_packet_task_candidate",
        "operator_may_choose_explicit_task_creation_authorization_boundary",
        "operator_review_case_packet_before_task_creation",
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


def _packet_implies_forbidden_activity(packet: dict[str, Any]) -> list[str]:
    blocked_conditions: list[str] = []
    forbidden_true_fields = {
        "task_created": "case_packet_implies_task_creation",
        "planner_invoked": "case_packet_implies_planner_invocation",
        "runtime_executed": "case_packet_implies_runtime_execution",
        "model_executed": "case_packet_implies_model_execution",
        "platform_invoked": "case_packet_implies_platform_execution",
        "openclaw_invoked": "case_packet_implies_openclaw_execution",
        "discord_invoked": "case_packet_implies_discord_execution",
        "bridge_invoked": "case_packet_implies_bridge_execution",
        "adapter_invoked": "case_packet_implies_adapter_execution",
    }

    for field, condition in forbidden_true_fields.items():
        if bool(packet.get(field)):
            blocked_conditions.append(condition)

    for entry in packet.get("decisions", []):
        if not isinstance(entry, dict):
            continue
        decision = _normalize_string(entry.get("decision")).lower()
        if "task_created" in decision or "task creation" in decision:
            blocked_conditions.append("case_packet_decision_implies_task_creation")
        if "planner" in decision:
            blocked_conditions.append("case_packet_decision_implies_planner_invocation")
        if "runtime" in decision or "model" in decision or "platform" in decision:
            blocked_conditions.append("case_packet_decision_implies_runtime_or_platform_execution")

    return sorted(set(blocked_conditions))


def _summarize_source_packet(packet: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    summary = summarize_case_packet(packet)
    return {
        "case_id": summary.get("case_id", ""),
        "title": summary.get("title", ""),
        "objective": summary.get("objective", ""),
        "status": summary.get("status", ""),
        "next_step": summary.get("next_step", ""),
        "source_materials": list(packet.get("source_materials", [])) if isinstance(packet.get("source_materials"), list) else [],
        "source_intake_linkage": _normalize_string(packet.get("source_intake_linkage")),
        "persistence_status": _normalize_string(packet.get("persistence_status")),
        "validation": validation,
        "readiness": summary.get("readiness", {}),
    }


def _candidate_summary(packet: dict[str, Any]) -> dict[str, Any]:
    source_materials = _normalize_string_list(packet.get("source_materials"))
    objective = _normalize_string(packet.get("objective"))
    return {
        "objective_text": objective,
        "likely_bounded_task_description": objective,
        "declared_or_inferred_file_surface": {
            "source": "case_packet.source_materials",
            "inference": "declared_by_persisted_case_packet" if source_materials else "missing_or_ambiguous",
            "files": source_materials,
        },
        "success_criteria": _normalize_string(packet.get("success_criteria")),
        "explicit_non_authorizations": [
            "task_created=false",
            "planner_invoked=false",
            "runtime_executed=false",
            "model_executed=false",
            "platform_invoked=false",
            "openclaw_invoked=false",
            "discord_invoked=false",
            "bridge_invoked=false",
            "adapter_invoked=false",
        ],
    }


def _review_result(
    status: str,
    case_id: str,
    case_packet_path: str,
    reason: str,
    detail: str,
    missing_requirements: list[str] | None = None,
    blocked_conditions: list[str] | None = None,
    candidate_summary: dict[str, Any] | None = None,
    source_case_packet_summary: dict[str, Any] | None = None,
    next_action: str = "",
) -> dict[str, Any]:
    return {
        "case_packet_task_candidate_review": True,
        "case_id": case_id,
        "case_packet_path": case_packet_path,
        "task_candidate_status": status,
        "reason": reason,
        "detail": detail,
        "missing_requirements": list(missing_requirements or []),
        "blocked_conditions": list(blocked_conditions or []),
        "candidate_summary": dict(candidate_summary or {}),
        "source_case_packet_summary": dict(source_case_packet_summary or {}),
        "next_action": next_action,
        "task_created": False,
        "planner_invoked": False,
        "runtime_executed": False,
        "model_executed": False,
        "platform_invoked": False,
        "openclaw_invoked": False,
        "discord_invoked": False,
        "bridge_invoked": False,
        "adapter_invoked": False,
        "mutation_performed": False,
        "execution_performed": False,
    }


def _blocked_review(
    case_id: str,
    case_packet_path: str,
    reason: str,
    detail: str,
    blocked_conditions: list[str],
    source_case_packet_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _review_result(
        status="blocked",
        case_id=case_id,
        case_packet_path=case_packet_path,
        reason=reason,
        detail=detail,
        blocked_conditions=blocked_conditions,
        source_case_packet_summary=source_case_packet_summary,
        next_action="resolve_blocked_condition_before_any_task_boundary",
    )


def review_persisted_case_packet_task_candidate(review_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(review_input, dict):
        return _blocked_review(
            case_id="",
            case_packet_path="",
            reason="Review input must be a JSON object.",
            detail="Phase 69 requires a case_id, case_packet_path, or persisted case-packet reference.",
            blocked_conditions=["json_object_input_required"],
        )

    packet, case_id, case_packet_path, reference_conditions = _extract_case_packet_reference(review_input)

    if _contains_forbidden_bundled_request(review_input):
        return _blocked_review(
            case_id=case_id,
            case_packet_path=case_packet_path,
            reason="Review request includes forbidden bundled behavior.",
            detail="Phase 69 may review a persisted case packet only; it cannot bundle task creation, planner, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, vendoring, cleanup, delete, archive, oz, or Codex behavior.",
            blocked_conditions=["unsupported_bundled_behavior_request"],
        )

    if packet is None:
        return _blocked_review(
            case_id=case_id,
            case_packet_path=case_packet_path,
            reason="Persisted case packet could not be loaded.",
            detail="Phase 69 requires an existing product case-packet record before task-candidate review.",
            blocked_conditions=reference_conditions or ["case_packet_reference_invalid"],
        )

    validation = validate_case_packet(packet)
    source_summary = _summarize_source_packet(packet, validation)
    candidate = _candidate_summary(packet)

    if reference_conditions:
        return _blocked_review(
            case_id=case_id,
            case_packet_path=case_packet_path,
            reason="Case packet reference is not an inspectable persisted product-store record.",
            detail="Phase 69 readiness requires the case packet to exist in the product case-packet store.",
            blocked_conditions=reference_conditions,
            source_case_packet_summary=source_summary,
        )

    if not validation.get("valid", False):
        return _blocked_review(
            case_id=case_id,
            case_packet_path=case_packet_path,
            reason="Case packet is invalid under current case-packet rules.",
            detail="Phase 69 cannot promote an invalid case packet into a task candidate.",
            blocked_conditions=list(validation.get("errors", [])) or ["case_packet_invalid"],
            source_case_packet_summary=source_summary,
        )

    forbidden_conditions = _packet_implies_forbidden_activity(packet)
    if forbidden_conditions:
        return _blocked_review(
            case_id=case_id,
            case_packet_path=case_packet_path,
            reason="Case packet implies forbidden prior or bundled activity.",
            detail="Phase 69 cannot proceed from a packet that implies task creation, planner invocation, runtime/model/platform behavior, OpenClaw, Discord, bridge, adapter, or related execution.",
            blocked_conditions=forbidden_conditions,
            source_case_packet_summary=source_summary,
        )

    missing_requirements: list[str] = []

    if not _normalize_string(packet.get("objective")):
        missing_requirements.append("objective")
    if not _normalize_string(packet.get("source_intake_linkage")):
        missing_requirements.append("source_intake_linkage")
    if _normalize_string(packet.get("persistence_status")) != "persisted":
        missing_requirements.append("persistence_status_persisted")
    if not isinstance(packet.get("phase65_admission_summary"), dict):
        missing_requirements.append("phase65_admission_summary")
    if not isinstance(packet.get("phase66_seed_review_summary"), dict):
        missing_requirements.append("phase66_seed_review_summary")
    if not isinstance(packet.get("phase67_authorization_summary"), dict):
        missing_requirements.append("phase67_authorization_summary")

    decisions = packet.get("decisions")
    if not isinstance(decisions, list):
        missing_requirements.append("phase67_phase68_decision_trace")
    else:
        decision_phases = {_normalize_string(entry.get("phase")).lower() for entry in decisions if isinstance(entry, dict)}
        if "phase 67" not in decision_phases:
            missing_requirements.append("phase67_decision_trace")
        if "phase 68" not in decision_phases:
            missing_requirements.append("phase68_decision_trace")

    source_materials = _normalize_string_list(packet.get("source_materials"))
    if not source_materials:
        missing_requirements.append("source_materials_or_file_surface")
    if any(item in {".", "*", "repo", "repository", "entire repo", "whole repo"} for item in (text.lower() for text in source_materials)):
        missing_requirements.append("bounded_file_surface")

    if missing_requirements:
        return _review_result(
            status="needs_operator_clarification",
            case_id=case_id,
            case_packet_path=case_packet_path,
            reason="Case packet is valid but not bounded enough for task-candidate readiness.",
            detail="Phase 69 needs enough persisted objective, lineage, provenance, and bounded file-surface information to avoid inventing operator intent.",
            missing_requirements=missing_requirements,
            source_case_packet_summary=source_summary,
            candidate_summary=candidate,
            next_action="request_operator_clarification_before_task_creation_authorization",
        )

    return _review_result(
        status="task_candidate_ready",
        case_id=case_id,
        case_packet_path=case_packet_path,
        reason="Persisted case packet is ready for operator task-candidate authorization review.",
        detail="Phase 69 produced a read-only candidate judgment only; no task, planner output, runtime/model execution, or platform behavior was created.",
        source_case_packet_summary=source_summary,
        candidate_summary=candidate,
        next_action="operator_may_choose_explicit_task_creation_authorization_boundary",
    )
