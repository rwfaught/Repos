from __future__ import annotations

from typing import Any

import orchestrator.run_manager as run_manager
from orchestrator.task_schema import Task


_FORBIDDEN_REQUEST_TERMS = [
    "runtime",
    "model",
    "ollama",
    "provider",
    "planner",
    "reviewer",
    "verifier",
    "platform",
    "openclaw",
    "discord",
    "bridge",
    "adapter",
    "installer",
    "wsl",
    "a18cf",
    "vendor",
    "cleanup",
    "clean up",
    "delete",
    "archive",
    "oz",
    "codex",
]

_MULTI_TASK_TERMS = [
    "all tasks",
    "multiple tasks",
    "every task",
    "batch execute",
    "execute batch",
    "run all",
    "run everything",
]

_BROAD_FILE_SURFACE_TOKENS = {"*", ".", "./", "all", "repo", "repository", "project", "workspace", "entire repo", "whole repo"}

_PHASE73_REQUIRED_FALSE_FLAGS = {
    "task_created": "phase73_authorization_implies_task_creation",
    "task_mutated": "phase73_authorization_implies_task_mutation",
    "task_executed": "phase73_authorization_implies_prior_task_execution",
    "planner_invoked": "phase73_authorization_implies_planner_invocation",
    "runtime_executed": "phase73_authorization_implies_runtime_execution",
    "model_executed": "phase73_authorization_implies_model_execution",
    "platform_invoked": "phase73_authorization_implies_platform_execution",
    "openclaw_invoked": "phase73_authorization_implies_openclaw_execution",
    "discord_invoked": "phase73_authorization_implies_discord_execution",
    "bridge_invoked": "phase73_authorization_implies_bridge_execution",
    "adapter_invoked": "phase73_authorization_implies_adapter_execution",
    "verifier_invoked": "phase73_authorization_implies_verifier_execution",
    "reviewer_invoked": "phase73_authorization_implies_reviewer_execution",
    "mutation_performed": "phase73_authorization_implies_mutation",
    "execution_performed": "phase73_authorization_implies_prior_execution",
}

_NON_PLATFORM_FLAGS = {
    "runtime_executed": False,
    "model_executed": False,
    "provider_executed": False,
    "planner_invoked": False,
    "reviewer_invoked": False,
    "verifier_invoked": False,
    "platform_invoked": False,
    "openclaw_invoked": False,
    "discord_invoked": False,
    "bridge_invoked": False,
    "adapter_invoked": False,
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


def _extract_phase73_authorization(execution_input: dict[str, Any]) -> dict[str, Any] | None:
    if execution_input.get("case_packet_task_execution_authorization_gate") is True:
        return execution_input

    for key in (
        "phase73_task_execution_authorization_result",
        "case_packet_task_execution_authorization_result",
        "task_execution_authorization_result",
        "phase73_authorization_result",
        "authorization_result",
    ):
        value = execution_input.get(key)
        if isinstance(value, dict):
            return value

    return None


def _contains_forbidden_request(value: Any) -> bool:
    fields: list[Any] = []

    if isinstance(value, dict):
        for key in (
            "requested_action",
            "requested_behavior",
            "requested_next_move",
            "execution_request",
            "platform_request",
            "operator_request",
            "operator_decision",
            "task_execution_request",
            "provider_name",
            "runtime_name",
            "model_name",
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
        if any(term in text for term in _FORBIDDEN_REQUEST_TERMS):
            return True
        if any(term in text for term in _MULTI_TASK_TERMS):
            return True

    return False


def _phase73_blocked_conditions(authorization: dict[str, Any]) -> list[str]:
    blocked: list[str] = []

    if authorization.get("case_packet_task_execution_authorization_gate") is not True:
        blocked.append("input_not_phase73_case_packet_task_execution_authorization_gate")

    if _normalize_string(authorization.get("task_execution_authorization")) != "task_execution_authorized":
        blocked.append("phase73_task_execution_not_authorized")

    if authorization.get("task_execution_authorized") is not True:
        blocked.append("phase73_authorized_boolean_not_true")

    for field, condition in _PHASE73_REQUIRED_FALSE_FLAGS.items():
        if bool(authorization.get(field)):
            blocked.append(condition)

    if _contains_forbidden_request(authorization):
        blocked.append("phase73_authorization_contains_forbidden_execution_expansion")

    return sorted(set(blocked))


def _candidate_summary(authorization: dict[str, Any]) -> dict[str, Any]:
    summary = authorization.get("selected_candidate_summary")
    return dict(summary) if isinstance(summary, dict) else {}


def _candidate_files(candidate: dict[str, Any]) -> list[str]:
    return _normalize_string_list(candidate.get("files_in_scope"))


def _has_broad_file_surface(files: list[str]) -> bool:
    for file_name in files:
        text = file_name.lower().strip().replace("\\", "/")
        if text in _BROAD_FILE_SURFACE_TOKENS:
            return True
        if text.endswith("/*") or text.endswith("/**"):
            return True
    return False


def _candidate_missing_requirements(candidate: dict[str, Any]) -> list[str]:
    missing: list[str] = []

    if not _normalize_string(candidate.get("task_id")):
        missing.append("selected_candidate_summary.task_id")
    if not _normalize_string(candidate.get("task_path")):
        missing.append("selected_candidate_summary.task_path")
    if not _normalize_string(candidate.get("run_id")):
        missing.append("selected_candidate_summary.run_id")
    if not _normalize_string(candidate.get("title")):
        missing.append("selected_candidate_summary.title")
    if not _normalize_string(candidate.get("role")):
        missing.append("selected_candidate_summary.role")
    if not _normalize_string(candidate.get("status")):
        missing.append("selected_candidate_summary.status")

    files = _candidate_files(candidate)
    if not files:
        missing.append("selected_candidate_summary.files_in_scope")
    if files and _has_broad_file_surface(files):
        missing.append("selected_candidate_summary.bounded_file_scope")

    if not _normalize_string(candidate.get("source_case_packet_identity")) and not _normalize_string(candidate.get("source_artifact_id")):
        missing.append("selected_candidate_summary.case_packet_traceability")

    if not _normalize_string_list(candidate.get("success_criteria")):
        missing.append("selected_candidate_summary.success_criteria")

    if not _normalize_string(candidate.get("expected_output")):
        missing.append("selected_candidate_summary.expected_output")

    return missing


def _task_path_for_id(task_id: str) -> str:
    return f"data/tasks/{task_id}.json"


def _task_summary(task: Task | None) -> dict[str, Any]:
    if task is None:
        return {}
    return {
        "task_id": task.id,
        "run_id": task.run_id,
        "title": task.title,
        "role": task.role,
        "status": task.status,
        "files_in_scope": list(task.files_in_scope),
        "success_criteria": list(task.success_criteria),
        "expected_output": task.expected_output,
        "source_artifact_id": task.source_artifact_id,
        "execution_artifact_id": task.execution_artifact_id,
        "execution_policy": task.execution_policy,
        "requires_causal_change": task.requires_causal_change,
        "execution_delegation_status": task.execution_delegation_status,
        "source_case_packet_identity": task.source_case_packet_identity,
        "execution_authorization_provenance": task.execution_authorization_provenance,
    }


def _authorization_summary(authorization: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(authorization, dict):
        return {}
    return {
        "case_packet_task_execution_authorization_gate": bool(authorization.get("case_packet_task_execution_authorization_gate")),
        "task_execution_authorization": _normalize_string(authorization.get("task_execution_authorization")),
        "task_execution_authorized": bool(authorization.get("task_execution_authorized")),
        "run_id": _normalize_string(authorization.get("run_id")),
        "task_id": _normalize_string(authorization.get("task_id")),
        "task_path": _normalize_string(authorization.get("task_path")),
        "operator_decision": _normalize_string(authorization.get("operator_decision")),
        "reason": _normalize_string(authorization.get("reason")),
        "detail": _normalize_string(authorization.get("detail")),
        "reviewer_decision": _normalize_string(authorization.get("reviewer_decision")),
        "reviewer_recommendation": _normalize_string(
            authorization.get("reviewer_recommendation")
        ),
        "next_action": _normalize_string(authorization.get("next_action")),
    }


def _result(
    status: str,
    authorization: dict[str, Any] | None,
    task: Task | None,
    reason: str,
    detail: str,
    artifact_id: str = "",
    artifact_path: str = "",
    blocked_conditions: list[str] | None = None,
    missing_requirements: list[str] | None = None,
    next_action: str = "",
) -> dict[str, Any]:
    return {
        "authorized_case_packet_task_execution_boundary": True,
        "run_id": _normalize_string((authorization or {}).get("run_id")) or (task.run_id if task else ""),
        "task_id": _normalize_string((authorization or {}).get("task_id")) or (task.id if task else ""),
        "task_path": _normalize_string((authorization or {}).get("task_path")),
        "task_execution_status": status,
        "task_executed": status == "executed",
        "execution_performed": status == "executed",
        "artifact_id": artifact_id,
        "artifact_path": artifact_path,
        "reason": reason,
        "detail": detail,
        "blocked_conditions": sorted(set(blocked_conditions or [])),
        "missing_requirements": list(missing_requirements or []),
        "source_authorization_summary": _authorization_summary(authorization),
        "selected_candidate_summary": _candidate_summary(authorization or {}),
        "task_summary": _task_summary(task),
        "next_action": next_action,
        **_NON_PLATFORM_FLAGS,
    }


def _load_task_or_none(task_id: str) -> Task | None:
    try:
        return run_manager.load_task(task_id)
    except FileNotFoundError:
        return None


def execute_authorized_case_packet_task(execution_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(execution_input, dict):
        return _result(
            status="blocked",
            authorization=None,
            task=None,
            reason="Execution input must be a JSON object.",
            detail="Phase 74 requires a Phase 73 task-execution authorization result.",
            blocked_conditions=["json_object_input_required"],
            next_action="provide_phase73_authorization_before_execution",
        )

    if _contains_forbidden_request(execution_input):
        return _result(
            status="blocked",
            authorization=None,
            task=None,
            reason="Execution request expands beyond Phase 74 local task execution.",
            detail="Phase 74 implementation does not allow runtime, model, provider, planner, reviewer, verifier, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, A18CF, vendoring, cleanup, deletion, archive, oz, Codex, or multi-task behavior.",
            blocked_conditions=["execution_request_expands_beyond_authorized_local_task_execution"],
            next_action="separate_platform_or_runtime_work_into_a_later_explicit_boundary",
        )

    authorization = _extract_phase73_authorization(execution_input)
    if authorization is None:
        return _result(
            status="blocked",
            authorization=None,
            task=None,
            reason="Phase 73 authorization result is missing.",
            detail="Phase 74 can execute only from an explicit Phase 73 task_execution_authorized result.",
            blocked_conditions=["phase73_authorization_result_missing"],
            next_action="provide_phase73_authorization_before_execution",
        )

    phase73_blocked = _phase73_blocked_conditions(authorization)
    if phase73_blocked:
        return _result(
            status="blocked",
            authorization=authorization,
            task=None,
            reason="Phase 73 authorization is not execution-safe.",
            detail="Phase 74 requires a clean Phase 73 task_execution_authorized result that has not already executed or expanded into runtime/model/platform behavior.",
            blocked_conditions=phase73_blocked,
            next_action="repair_or_reissue_phase73_authorization_before_execution",
        )

    candidate = _candidate_summary(authorization)
    missing = _candidate_missing_requirements(candidate)
    if missing:
        return _result(
            status="blocked",
            authorization=authorization,
            task=None,
            reason="Phase 73 authorization is missing candidate execution requirements.",
            detail="Phase 74 requires task id, task path, run id, role, queued status, bounded file scope, case-packet traceability, success criteria, and expected output.",
            missing_requirements=missing,
            blocked_conditions=["phase73_authorization_missing_execution_requirements"],
            next_action="provide_complete_phase73_authorization_before_execution",
        )

    task_id = _normalize_string(candidate.get("task_id"))
    authorization_task_id = _normalize_string(authorization.get("task_id"))
    if authorization_task_id and authorization_task_id != task_id:
        return _result(
            status="blocked",
            authorization=authorization,
            task=None,
            reason="Authorization task id does not match selected candidate task id.",
            detail="Phase 74 cannot execute a task whose identity differs between the authorization result and the selected candidate summary.",
            blocked_conditions=["authorization_task_id_mismatch"],
            next_action="repair_phase73_authorization_task_identity_before_execution",
        )

    task = _load_task_or_none(task_id)
    if task is None:
        return _result(
            status="blocked",
            authorization=authorization,
            task=None,
            reason="Selected task file was not found.",
            detail="Phase 74 requires the selected authorized task to exist in the task store at execution time.",
            blocked_conditions=["selected_task_file_missing"],
            next_action="restore_or_recreate_selected_task_before_execution",
        )

    blocked: list[str] = []
    if task.id != task_id:
        blocked.append("loaded_task_id_mismatch")
    if task.run_id != _normalize_string(candidate.get("run_id")):
        blocked.append("loaded_task_run_id_mismatch")
    if task.status != "queued":
        blocked.append("loaded_task_status_not_queued")
    if _task_path_for_id(task.id) != _normalize_string(candidate.get("task_path")).replace("\\", "/"):
        blocked.append("loaded_task_path_mismatch")
    if list(task.files_in_scope) != _candidate_files(candidate):
        blocked.append("loaded_task_file_scope_mismatch")
    if list(task.success_criteria) != _normalize_string_list(candidate.get("success_criteria")):
        blocked.append("loaded_task_success_criteria_mismatch")
    if _normalize_string(task.expected_output) != _normalize_string(candidate.get("expected_output")):
        blocked.append("loaded_task_expected_output_mismatch")
    if _normalize_string(task.source_artifact_id) != _normalize_string(candidate.get("source_artifact_id")):
        blocked.append("loaded_task_source_artifact_mismatch")
    if _normalize_string(task.execution_artifact_id):
        blocked.append("loaded_task_already_has_execution_artifact")
    if _contains_forbidden_request(candidate):
        blocked.append("selected_candidate_expands_beyond_authorized_scope")

    if blocked:
        return _result(
            status="blocked",
            authorization=authorization,
            task=task,
            reason="Selected task no longer matches Phase 73 authorization requirements.",
            detail="Phase 74 blocks execution when task identity, queue state, file scope, success criteria, expected output, or case-packet traceability has drifted.",
            blocked_conditions=blocked,
            next_action="resurface_and_reauthorize_task_before_execution",
        )

    task.execution_delegation_status = "queued_for_canonical_execution"
    task.source_case_packet_identity = _normalize_string(
        candidate.get("source_case_packet_identity")
    ) or None
    task.execution_authorization_provenance = _authorization_summary(authorization)
    run_manager.save_task(task)

    return _result(
        status="queued_for_canonical_execution",
        authorization=authorization,
        task=task,
        reason="Phase 73 authorization is valid and the task is delegated to the canonical engine queue.",
        detail="Authorization is not execution. No artifact was written, the selected task remains queued with no execution artifact, and normal engine processing requires a separate execution boundary.",
        next_action="use_a_separately_authorized_normal_engine_execution_boundary",
    )
