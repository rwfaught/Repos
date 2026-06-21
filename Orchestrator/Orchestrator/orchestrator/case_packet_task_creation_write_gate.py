from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

import orchestrator.run_manager as run_manager
from orchestrator.task_schema import Task


_BROAD_FILE_SURFACE_TOKENS = {
    ".",
    "*",
    "repo",
    "repository",
    "entire repo",
    "whole repo",
}

_FORBIDDEN_TRUE_FIELDS = {
    "task_created": "phase70_input_implies_prior_task_creation",
    "planner_invoked": "phase70_input_implies_planner_invocation",
    "runtime_executed": "phase70_input_implies_runtime_execution",
    "model_executed": "phase70_input_implies_model_execution",
    "platform_invoked": "phase70_input_implies_platform_execution",
    "openclaw_invoked": "phase70_input_implies_openclaw_execution",
    "discord_invoked": "phase70_input_implies_discord_execution",
    "bridge_invoked": "phase70_input_implies_bridge_execution",
    "adapter_invoked": "phase70_input_implies_adapter_execution",
    "installer_invoked": "phase70_input_implies_installer_execution",
    "wsl_invoked": "phase70_input_implies_wsl_execution",
    "verifier_invoked": "phase70_input_implies_verifier_execution",
    "reviewer_invoked": "phase70_input_implies_reviewer_execution",
    "mutation_performed": "phase70_input_implies_prior_mutation",
    "execution_performed": "phase70_input_implies_execution",
    "cleanup_performed": "phase70_input_implies_cleanup",
    "deletion_performed": "phase70_input_implies_deletion",
    "archive_performed": "phase70_input_implies_archive",
}

_FORBIDDEN_TEXT_TERMS = [
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
    "verifier",
    "reviewer",
    "vendor",
    "cleanup",
    "delete",
    "archive",
    "codex",
]

_ALLOWED_EXACT_TEXT = {
    "authorize_task_creation",
    "approve_task_creation",
    "approved_task_creation",
    "task_creation_authorized",
    "authorized_task_creation",
    "operator_authorizes_task_creation",
    "operator_may_choose_explicit_authorized_task_creation_write_gate",
    "case_packet_task_creation_write_gate",
}


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [text for item in value if (text := _normalize_string(item))]
    if isinstance(value, str):
        text = _normalize_string(value)
        return [text] if text else []
    return []


def _machine_token(value: Any) -> str:
    text = _normalize_string(value)
    token = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")
    return token or "unknown"


def _extract_phase70_authorization(creation_input: dict[str, Any]) -> dict[str, Any] | None:
    if creation_input.get("case_packet_task_creation_authorization") is True:
        return creation_input

    for key in (
        "phase70_task_creation_authorization_result",
        "case_packet_task_creation_authorization_result",
        "task_creation_authorization_result",
        "phase70_authorization_result",
        "authorization_result",
    ):
        value = creation_input.get(key)
        if isinstance(value, dict):
            return value

    return None


def _contains_forbidden_bundled_request(value: Any) -> bool:
    fields: list[Any] = []

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
            "next_action",
            "detail",
        ):
            fields.append(value.get(key))
    else:
        fields.append(value)

    for field in fields:
        text = _normalize_string(field).lower()
        if not text:
            continue

        normalized = text.replace("-", "_").replace(" ", "_")
        if normalized in _ALLOWED_EXACT_TEXT:
            continue

        if any(term in text for term in _FORBIDDEN_TEXT_TERMS):
            return True

    return False


def _forbidden_input_conditions(phase70_result: dict[str, Any]) -> list[str]:
    blocked: list[str] = []

    for field, condition in _FORBIDDEN_TRUE_FIELDS.items():
        if bool(phase70_result.get(field)):
            blocked.append(condition)

    if _contains_forbidden_bundled_request(phase70_result):
        blocked.append("phase70_input_contains_forbidden_bundled_behavior")

    return sorted(set(blocked))


def _candidate_summary(phase70_result: dict[str, Any]) -> dict[str, Any]:
    candidate = phase70_result.get("candidate_summary")
    return dict(candidate) if isinstance(candidate, dict) else {}


def _source_case_packet_summary(phase70_result: dict[str, Any]) -> dict[str, Any]:
    summary = phase70_result.get("source_case_packet_summary")
    return dict(summary) if isinstance(summary, dict) else {}


def _candidate_objective(candidate: dict[str, Any]) -> str:
    return _normalize_string(candidate.get("objective_text")) or _normalize_string(
        candidate.get("likely_bounded_task_description")
    )


def _candidate_files(candidate: dict[str, Any]) -> list[str]:
    surface = candidate.get("declared_or_inferred_file_surface")
    if not isinstance(surface, dict):
        return []
    return _normalize_string_list(surface.get("files"))


def _candidate_success_criteria(candidate: dict[str, Any], case_id: str) -> list[str]:
    raw = candidate.get("success_criteria")
    items = _normalize_string_list(raw)
    if items:
        return items
    return [f"Complete the authorized bounded task for case packet {case_id}."]


def _has_broad_file_surface(files: list[str]) -> bool:
    for file_name in files:
        text = file_name.lower().strip()
        if text in _BROAD_FILE_SURFACE_TOKENS:
            return True
    return False


def _run_id_for_phase70_result(phase70_result: dict[str, Any]) -> str:
    direct = _normalize_string(phase70_result.get("run_id"))
    if direct:
        return direct

    source_summary = _source_case_packet_summary(phase70_result)
    summary_run_id = _normalize_string(source_summary.get("run_id"))
    if summary_run_id:
        return summary_run_id

    case_id = _normalize_string(phase70_result.get("case_id")) or _normalize_string(
        source_summary.get("case_id")
    )
    if case_id:
        return f"case_packet_{_machine_token(case_id)}"

    return "case_packet_task_creation"


def _task_title(objective: str, case_id: str) -> str:
    base = objective or f"Authorized task for case packet {case_id}"
    title = f"Case packet task: {base}"
    if len(title) <= 120:
        return title
    return title[:117].rstrip() + "..."


def _task_expected_output(objective: str) -> str:
    if objective:
        return f"Complete bounded task: {objective}"
    return "Complete the authorized bounded case-packet task."


def _blocked_result(
    phase70_result: dict[str, Any] | None,
    reason: str,
    detail: str,
    blocked_conditions: list[str],
    missing_requirements: list[str] | None = None,
) -> dict[str, Any]:
    phase70 = phase70_result if isinstance(phase70_result, dict) else {}
    return {
        "case_packet_task_creation_write_gate": True,
        "task_creation_write": "blocked",
        "task_created": False,
        "task_id": "",
        "task_path": "",
        "case_id": _normalize_string(phase70.get("case_id")),
        "reason": reason,
        "detail": detail,
        "missing_requirements": list(missing_requirements or []),
        "blocked_conditions": sorted(set(blocked_conditions)),
        "planner_invoked": False,
        "runtime_executed": False,
        "model_executed": False,
        "platform_invoked": False,
        "openclaw_invoked": False,
        "discord_invoked": False,
        "bridge_invoked": False,
        "adapter_invoked": False,
        "verifier_invoked": False,
        "reviewer_invoked": False,
        "mutation_performed": False,
        "execution_performed": False,
        "next_action": "resolve_blocked_condition_before_task_creation_write_gate",
    }


def create_task_from_authorized_case_packet_task_creation(
    creation_input: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(creation_input, dict):
        return _blocked_result(
            phase70_result=None,
            reason="Task creation write input must be a JSON object.",
            detail="Phase 71 requires a Phase 70 task_creation_authorized result.",
            blocked_conditions=["json_object_input_required"],
        )

    phase70_result = _extract_phase70_authorization(creation_input)
    if phase70_result is None:
        return _blocked_result(
            phase70_result=None,
            reason="Phase 70 task-creation authorization result is missing.",
            detail="Phase 71 can create a task only from an explicit Phase 70 authorization result.",
            blocked_conditions=["phase70_task_creation_authorization_result_missing"],
        )

    if phase70_result.get("case_packet_task_creation_authorization") is not True:
        return _blocked_result(
            phase70_result=phase70_result,
            reason="Input is not a Phase 70 task-creation authorization result.",
            detail="Phase 71 requires case_packet_task_creation_authorization=true from Phase 70.",
            blocked_conditions=["input_not_phase70_task_creation_authorization_result"],
        )

    if _normalize_string(phase70_result.get("task_creation_authorization")) != "task_creation_authorized":
        return _blocked_result(
            phase70_result=phase70_result,
            reason="Phase 70 authorization status is not task_creation_authorized.",
            detail="Only an explicit Phase 70 task_creation_authorized result can pass the Phase 71 write gate.",
            blocked_conditions=["phase70_task_creation_not_authorized"],
        )

    if phase70_result.get("task_creation_authorized") is not True:
        return _blocked_result(
            phase70_result=phase70_result,
            reason="Phase 70 authorization boolean is not true.",
            detail="Phase 71 requires task_creation_authorized=true.",
            blocked_conditions=["phase70_task_creation_authorized_boolean_not_true"],
        )

    forbidden_conditions = _forbidden_input_conditions(phase70_result)
    if forbidden_conditions:
        return _blocked_result(
            phase70_result=phase70_result,
            reason="Phase 70 input implies forbidden prior or bundled behavior.",
            detail="Phase 71 may create one queued task only; it cannot proceed from input implying task creation, planner, reviewer, verifier, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, cleanup, deletion, archive, oz, Codex, or execution behavior.",
            blocked_conditions=forbidden_conditions,
        )

    candidate = _candidate_summary(phase70_result)
    source_summary = _source_case_packet_summary(phase70_result)
    case_id = _normalize_string(phase70_result.get("case_id")) or _normalize_string(
        source_summary.get("case_id")
    )
    case_packet_path = _normalize_string(phase70_result.get("case_packet_path"))
    objective = _candidate_objective(candidate)
    files = _candidate_files(candidate)

    missing: list[str] = []
    if not case_id:
        missing.append("case_id")
    if not candidate:
        missing.append("candidate_summary")
    if not source_summary:
        missing.append("source_case_packet_summary")
    if not objective:
        missing.append("candidate_summary.objective_text")
    if not files:
        missing.append("candidate_summary.declared_or_inferred_file_surface.files")
    elif _has_broad_file_surface(files):
        missing.append("candidate_summary.bounded_file_surface")

    if missing:
        return _blocked_result(
            phase70_result=phase70_result,
            reason="Phase 70 authorization result is missing task-creation write requirements.",
            detail="Phase 71 requires case identity, candidate objective, bounded file surface, and source case-packet summary before it can write a task.",
            missing_requirements=missing,
            blocked_conditions=["phase70_authorization_missing_task_write_requirements"],
        )

    run_id = _run_id_for_phase70_result(phase70_result)
    task = Task(
        id=f"task_{uuid4().hex[:8]}",
        run_id=run_id,
        title=_task_title(objective, case_id),
        role="worker",
        status="queued",
        dependencies=[],
        success_criteria=_candidate_success_criteria(candidate, case_id),
        files_in_scope=files,
        retry_count=0,
        expected_output=_task_expected_output(objective),
        source_task_id=None,
        source_artifact_id=(case_packet_path or case_id),
        execution_artifact_id=None,
        review_reason=(
            f"Phase 71 task created from Phase 70 authorization for case packet {case_id}."
        ),
        recommendation_type=None,
        recommendation_reason=None,
        recommendation_identity=None,
        recommendation_confirmed=False,
        recommendation_confirmed_at=None,
        verification_checks=None,
    )

    run_manager.save_task(task)
    task_path = run_manager.TASKS_DIR / f"{task.id}.json"

    return {
        "case_packet_task_creation_write_gate": True,
        "task_creation_write": "created",
        "task_created": True,
        "task_id": task.id,
        "task_path": str(task_path),
        "run_id": task.run_id,
        "case_id": case_id,
        "case_packet_path": case_packet_path,
        "created_task_summary": {
            "id": task.id,
            "run_id": task.run_id,
            "title": task.title,
            "role": task.role,
            "status": task.status,
            "dependencies": task.dependencies,
            "success_criteria": task.success_criteria,
            "files_in_scope": task.files_in_scope,
            "expected_output": task.expected_output,
            "source_task_id": task.source_task_id,
            "source_artifact_id": task.source_artifact_id,
        },
        "reason": "Created one queued task from explicit Phase 70 authorization.",
        "detail": "Phase 71 created one task record only; no planner, reviewer, verifier, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, cleanup, deletion, archive, oz, Codex, or execution behavior occurred.",
        "missing_requirements": [],
        "blocked_conditions": [],
        "planner_invoked": False,
        "runtime_executed": False,
        "model_executed": False,
        "platform_invoked": False,
        "openclaw_invoked": False,
        "discord_invoked": False,
        "bridge_invoked": False,
        "adapter_invoked": False,
        "verifier_invoked": False,
        "reviewer_invoked": False,
        "mutation_performed": True,
        "execution_performed": False,
        "next_action": "operator_may_review_queued_task_before_any_execution_boundary",
    }
