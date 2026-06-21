from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from orchestrator import run_manager
from orchestrator.task_schema import Task

_COMPATIBLE_ROLES = {"worker", "coder", "reviewer"}
_BROAD_FILE_SURFACE_TOKENS = {"*", ".", "./", "all", "repo", "repository", "project", "workspace"}
_FORBIDDEN_TEXT_TERMS = (
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
    "clean up",
    "delete",
    "archive",
    "oz",
    "codex",
)
_PHASE71_TRACE_PATTERN = re.compile(
    r"phase\s*71\s+task\s+created\s+from\s+phase\s*70\s+authorization\s+for\s+case\s+packet\s+([^\.]+)",
    re.IGNORECASE,
)


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


def _has_broad_file_surface(files: list[str]) -> bool:
    for file_name in files:
        text = file_name.lower().strip().replace("\\", "/")
        if text in _BROAD_FILE_SURFACE_TOKENS:
            return True
        if text.endswith("/*") or text.endswith("/**"):
            return True
    return False


def _case_identity_from_review_reason(task: Task) -> str:
    review_reason = _normalize_string(task.review_reason)
    match = _PHASE71_TRACE_PATTERN.search(review_reason)
    if not match:
        return ""
    return match.group(1).strip()


def _source_artifact_points_to_case_packet(task: Task) -> bool:
    source = _normalize_string(task.source_artifact_id)
    if not source:
        return False
    normalized = source.replace("\\", "/").lower()
    if "case_packets/" in normalized and normalized.endswith(".json"):
        return True
    if normalized.startswith("case_packet_"):
        return True
    return bool(_case_identity_from_review_reason(task) and source)


def _is_phase71_traceable_task(task: Task) -> bool:
    reason = _normalize_string(task.review_reason).lower()
    return "phase 71 task created from phase 70 authorization for case packet" in reason


def _source_case_packet_identity(task: Task) -> str:
    source = _normalize_string(task.source_artifact_id)
    identity = _case_identity_from_review_reason(task)
    if identity:
        return identity
    if source:
        normalized = source.replace("\\", "/")
        name = Path(normalized).name
        if name.endswith(".json"):
            return name[:-5]
        return source
    return ""


def _text_implies_forbidden_behavior(task: Task) -> bool:
    fields: list[str] = [
        _normalize_string(task.title),
        _normalize_string(task.expected_output),
    ]
    fields.extend(_normalize_string_list(task.success_criteria))

    for field in fields:
        text = field.lower()
        if not text:
            continue
        if any(term in text for term in _FORBIDDEN_TEXT_TERMS):
            return True
    return False


def _candidate_blocked_conditions(task: Task) -> list[str]:
    blocked: list[str] = []

    if task.status != "queued":
        blocked.append("task_status_not_queued")
    if task.role not in _COMPATIBLE_ROLES:
        blocked.append("task_role_not_execution_candidate_compatible")
    if not _is_phase71_traceable_task(task):
        blocked.append("task_missing_phase71_case_packet_trace")
    if not _source_artifact_points_to_case_packet(task):
        blocked.append("task_source_artifact_not_case_packet_trace")
    if not task.files_in_scope:
        blocked.append("task_missing_bounded_file_scope")
    elif _has_broad_file_surface(task.files_in_scope):
        blocked.append("task_file_scope_broad_or_ambiguous")
    if not task.success_criteria:
        blocked.append("task_missing_success_criteria")
    if not _normalize_string(task.expected_output):
        blocked.append("task_missing_expected_output")
    if _normalize_string(task.execution_artifact_id):
        blocked.append("task_has_execution_artifact")
    if run_manager.is_recommendation_created_task(task):
        blocked.append("recommendation_created_task_excluded")
    if _text_implies_forbidden_behavior(task):
        blocked.append("task_text_implies_forbidden_execution_or_platform_behavior")

    return sorted(set(blocked))


def _candidate_payload(task: Task) -> dict[str, Any]:
    return {
        "task_id": task.id,
        "task_path": str(run_manager.TASKS_DIR / f"{task.id}.json"),
        "run_id": task.run_id,
        "title": task.title,
        "status": task.status,
        "role": task.role,
        "files_in_scope": list(task.files_in_scope),
        "success_criteria": list(task.success_criteria),
        "expected_output": _normalize_string(task.expected_output),
        "source_artifact_id": _normalize_string(task.source_artifact_id),
        "source_case_packet_identity": _source_case_packet_identity(task),
        "execution_candidate_status": "case_packet_task_execution_candidate",
    }


def _exclusion_payload(task: Task, blocked_conditions: list[str]) -> dict[str, Any]:
    return {
        "task_id": task.id,
        "run_id": task.run_id,
        "title": task.title,
        "status": task.status,
        "role": task.role,
        "source_artifact_id": _normalize_string(task.source_artifact_id),
        "blocked_conditions": list(blocked_conditions),
    }


def surface_case_packet_task_execution_candidates(run_id: str | None = None) -> dict[str, Any]:
    normalized_run_id = _normalize_string(run_id)
    if not normalized_run_id:
        return {
            "case_packet_task_execution_candidate_surface": True,
            "run_id": "",
            "candidate_count": 0,
            "candidates": [],
            "excluded_count": 0,
            "excluded": [],
            "reason": "Run id is required.",
            "detail": "Phase 72 surfaces case-packet-created queued tasks for a specific run only.",
            "next_action": "provide_run_id_before_case_packet_task_execution_candidate_surfacing",
            "task_created": False,
            "task_mutated": False,
            "task_executed": False,
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
        }

    tasks = run_manager.load_tasks_for_run(normalized_run_id)
    candidates: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for task in tasks:
        blocked_conditions = _candidate_blocked_conditions(task)
        if blocked_conditions:
            excluded.append(_exclusion_payload(task, blocked_conditions))
            continue
        candidates.append(_candidate_payload(task))

    reason = "Case-packet task execution candidates surfaced."
    detail = "Phase 72 surfaced queued Phase 71 case-packet-created tasks only; no task creation, mutation, execution, planner, reviewer, verifier, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, cleanup, deletion, archive, oz, Codex, or execution behavior occurred."
    next_action = "operator_may_select_candidate_for_later_explicit_execution_boundary"
    if not candidates:
        reason = "No case-packet task execution candidates found for this run."
        detail = "Phase 72 inspected the run task store and found no queued Phase 71 case-packet-created task that met all candidate rules."
        next_action = "create_or_repair_phase71_case_packet_task_before_execution_candidate_surfacing"

    return {
        "case_packet_task_execution_candidate_surface": True,
        "run_id": normalized_run_id,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "excluded_count": len(excluded),
        "excluded": excluded,
        "reason": reason,
        "detail": detail,
        "next_action": next_action,
        "task_created": False,
        "task_mutated": False,
        "task_executed": False,
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
    }