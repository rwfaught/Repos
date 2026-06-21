from __future__ import annotations

import json
from typing import Any

import orchestrator.artifact_store as artifact_store


_FORBIDDEN_REVIEW_REQUEST_TERMS = [
    "execute",
    "rerun",
    "run again",
    "mutate",
    "create task",
    "follow-up task",
    "verify",
    "reviewer",
    "verifier",
    "planner",
    "runtime",
    "model",
    "ollama",
    "provider",
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
    "export",
    "oz",
    "codex",
]

_SOURCE_TRUE_FORBIDDEN_FLAGS = {
    "runtime_executed": "phase74_result_implies_runtime_execution",
    "model_executed": "phase74_result_implies_model_execution",
    "provider_executed": "phase74_result_implies_provider_execution",
    "planner_invoked": "phase74_result_implies_planner_invocation",
    "reviewer_invoked": "phase74_result_implies_reviewer_invocation",
    "verifier_invoked": "phase74_result_implies_verifier_invocation",
    "platform_invoked": "phase74_result_implies_platform_invocation",
    "openclaw_invoked": "phase74_result_implies_openclaw_invocation",
    "discord_invoked": "phase74_result_implies_discord_invocation",
    "bridge_invoked": "phase74_result_implies_bridge_invocation",
    "adapter_invoked": "phase74_result_implies_adapter_invocation",
}

_REVIEW_READ_ONLY_FLAGS = {
    "task_created": False,
    "task_mutated": False,
    "task_executed": False,
    "execution_performed": False,
    "artifact_mutated": False,
    "planner_invoked": False,
    "reviewer_invoked": False,
    "verifier_invoked": False,
    "runtime_executed": False,
    "model_executed": False,
    "provider_executed": False,
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


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _extract_phase74_execution_result(review_input: dict[str, Any]) -> dict[str, Any] | None:
    if review_input.get("authorized_case_packet_task_execution_boundary") is True:
        return review_input

    for key in (
        "phase74_execution_result",
        "phase74_task_execution_result",
        "authorized_case_packet_task_execution_result",
        "case_packet_task_execution_result",
        "source_execution_result",
        "execution_result",
    ):
        value = review_input.get(key)
        if isinstance(value, dict):
            return value

    return None


def _contains_forbidden_review_request(review_input: dict[str, Any]) -> bool:
    fields: list[Any] = []
    for key in (
        "requested_action",
        "requested_behavior",
        "requested_next_move",
        "operator_request",
        "operator_decision",
        "review_request",
        "provider_name",
        "runtime_name",
        "model_name",
    ):
        fields.append(review_input.get(key))

    for field in fields:
        text = _normalize_string(field).lower()
        if not text:
            continue
        if any(term in text for term in _FORBIDDEN_REVIEW_REQUEST_TERMS):
            return True
    return False


def _source_authorization_summary(execution_result: dict[str, Any]) -> dict[str, Any]:
    return _as_dict(execution_result.get("source_authorization_summary"))


def _selected_candidate_summary(execution_result: dict[str, Any]) -> dict[str, Any]:
    return _as_dict(execution_result.get("selected_candidate_summary"))


def _task_summary(execution_result: dict[str, Any]) -> dict[str, Any]:
    return _as_dict(execution_result.get("task_summary"))


def _artifact_file_path(artifact_id: str, artifact_path: str) -> Any:
    artifact_id = _normalize_string(artifact_id)
    artifact_path = _normalize_string(artifact_path).replace("\\", "/")
    if artifact_id:
        try:
            return artifact_store.artifact_path(artifact_id)
        except ValueError:
            return None
    if artifact_path.startswith("data/artifacts/") and artifact_path.endswith(".json"):
        filename = artifact_path.split("/")[-1]
        artifact_id_from_path = filename.removesuffix(".json")
        try:
            return artifact_store.artifact_path(artifact_id_from_path)
        except ValueError:
            return None
    return None


def _read_artifact_summary(artifact_id: str, artifact_path: str) -> tuple[dict[str, Any], list[str]]:
    missing: list[str] = []
    artifact_id = _normalize_string(artifact_id)
    artifact_path = _normalize_string(artifact_path)
    if not artifact_id:
        missing.append("artifact_id")
    if not artifact_path:
        missing.append("artifact_path")

    file_path = _artifact_file_path(artifact_id, artifact_path)
    if file_path is None:
        if not missing:
            missing.append("artifact_path_inspectable")
        return {}, missing

    if not file_path.exists():
        missing.append("artifact_file")
        return {}, missing

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        missing.append("artifact_json")
        return {}, missing

    summary = {
        "artifact_id": _normalize_string(data.get("artifact_id")),
        "task_id": _normalize_string(data.get("task_id")),
        "run_id": _normalize_string(data.get("run_id")),
        "role": _normalize_string(data.get("role")),
        "status": _normalize_string(data.get("status")),
        "output_present": bool(_normalize_string(data.get("output"))),
    }
    return summary, missing


def _missing_review_requirements(execution_result: dict[str, Any]) -> list[str]:
    missing: list[str] = []

    if not _normalize_string(execution_result.get("run_id")):
        missing.append("run_id")
    if not _normalize_string(execution_result.get("task_id")):
        missing.append("task_id")
    if not _normalize_string(execution_result.get("task_path")):
        missing.append("task_path")

    authorization = _source_authorization_summary(execution_result)
    candidate = _selected_candidate_summary(execution_result)
    if not authorization:
        missing.append("source_authorization_summary")
    if not candidate:
        missing.append("selected_candidate_summary")

    files = _normalize_string_list(candidate.get("files_in_scope"))
    if not files:
        missing.append("selected_candidate_summary.files_in_scope")
    if not _normalize_string(candidate.get("source_case_packet_identity")) and not _normalize_string(candidate.get("source_artifact_id")):
        missing.append("selected_candidate_summary.case_packet_traceability")
    if not _normalize_string_list(candidate.get("success_criteria")):
        missing.append("selected_candidate_summary.success_criteria")
    if not _normalize_string(candidate.get("expected_output")):
        missing.append("selected_candidate_summary.expected_output")

    return missing


def _source_blocked_conditions(execution_result: dict[str, Any]) -> list[str]:
    blocked: list[str] = []
    if execution_result.get("authorized_case_packet_task_execution_boundary") is not True:
        blocked.append("input_not_phase74_authorized_case_packet_task_execution_result")

    for field, condition in _SOURCE_TRUE_FORBIDDEN_FLAGS.items():
        if bool(execution_result.get(field)):
            blocked.append(condition)

    return sorted(set(blocked))


def _source_execution_summary(execution_result: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(execution_result, dict):
        return {}
    return {
        "authorized_case_packet_task_execution_boundary": bool(execution_result.get("authorized_case_packet_task_execution_boundary")),
        "task_execution_status": _normalize_string(execution_result.get("task_execution_status")),
        "task_executed": bool(execution_result.get("task_executed")),
        "execution_performed": bool(execution_result.get("execution_performed")),
        "run_id": _normalize_string(execution_result.get("run_id")),
        "task_id": _normalize_string(execution_result.get("task_id")),
        "task_path": _normalize_string(execution_result.get("task_path")),
        "artifact_id": _normalize_string(execution_result.get("artifact_id")),
        "artifact_path": _normalize_string(execution_result.get("artifact_path")),
        "reason": _normalize_string(execution_result.get("reason")),
        "next_action": _normalize_string(execution_result.get("next_action")),
    }


def _review_result(
    status: str,
    execution_result: dict[str, Any] | None,
    reason: str,
    detail: str,
    artifact_summary: dict[str, Any] | None = None,
    blocked_conditions: list[str] | None = None,
    missing_requirements: list[str] | None = None,
    next_action: str = "",
) -> dict[str, Any]:
    execution_result = execution_result if isinstance(execution_result, dict) else {}
    return {
        "case_packet_task_execution_result_review_surface": True,
        "run_id": _normalize_string(execution_result.get("run_id")),
        "task_id": _normalize_string(execution_result.get("task_id")),
        "task_path": _normalize_string(execution_result.get("task_path")),
        "artifact_id": _normalize_string(execution_result.get("artifact_id")),
        "artifact_path": _normalize_string(execution_result.get("artifact_path")),
        "execution_result_review": status,
        "ready_for_operator_review": status == "execution_result_ready_for_operator_review",
        "reason": reason,
        "detail": detail,
        "blocked_conditions": sorted(set(blocked_conditions or [])),
        "missing_requirements": list(missing_requirements or []),
        "source_execution_summary": _source_execution_summary(execution_result),
        "source_authorization_summary": _source_authorization_summary(execution_result),
        "selected_candidate_summary": _selected_candidate_summary(execution_result),
        "artifact_summary": dict(artifact_summary or {}),
        "task_summary": _task_summary(execution_result),
        "next_action": next_action,
        **_REVIEW_READ_ONLY_FLAGS,
    }


def review_case_packet_task_execution_result(review_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(review_input, dict):
        return _review_result(
            status="blocked",
            execution_result=None,
            reason="Review input must be a JSON object.",
            detail="Phase 75 requires a Phase 74 execution result or a wrapper containing one.",
            blocked_conditions=["json_object_input_required"],
            next_action="provide_phase74_execution_result_for_review",
        )

    if _contains_forbidden_review_request(review_input):
        return _review_result(
            status="blocked",
            execution_result=None,
            reason="Review request asks Phase 75 to do more than read-only result review.",
            detail="Phase 75 cannot create, mutate, execute, rerun, verify, call a provider, or invoke runtime/model/platform/OpenClaw/Discord/bridge/adapter/installer/WSL behavior.",
            blocked_conditions=["review_request_expands_beyond_read_only_result_review"],
            next_action="separate_followup_or_runtime_work_into_a_later_explicit_boundary",
        )

    execution_result = _extract_phase74_execution_result(review_input)
    if execution_result is None:
        return _review_result(
            status="blocked",
            execution_result=None,
            reason="Phase 74 execution result is missing.",
            detail="Phase 75 can review only an explicit Phase 74 authorized case-packet task execution result.",
            blocked_conditions=["phase74_execution_result_missing"],
            next_action="provide_phase74_execution_result_for_review",
        )

    blocked = _source_blocked_conditions(execution_result)
    if blocked:
        return _review_result(
            status="blocked",
            execution_result=execution_result,
            reason="Phase 74 execution result is not review-safe.",
            detail="Phase 75 requires a Phase 74 local execution result that does not imply runtime/model/provider/planner/reviewer/verifier/platform behavior.",
            blocked_conditions=blocked,
            next_action="repair_or_reissue_phase74_execution_result_before_review",
        )

    task_execution_status = _normalize_string(execution_result.get("task_execution_status"))
    task_summary = _task_summary(execution_result)
    if task_execution_status == "execution_failed" or _normalize_string(task_summary.get("status")) == "execution_failed":
        return _review_result(
            status="execution_result_failed",
            execution_result=execution_result,
            reason="Phase 74 execution failed.",
            detail=_normalize_string(execution_result.get("detail")) or "Execution result indicates failure.",
            next_action="operator_may_inspect_failure_detail_before_any_repair_boundary",
        )

    if task_execution_status != "executed" or execution_result.get("task_executed") is not True or execution_result.get("execution_performed") is not True:
        return _review_result(
            status="blocked",
            execution_result=execution_result,
            reason="Phase 74 result is not an executed result.",
            detail="Phase 75 post-execution result review requires an executed Phase 74 result, unless the result is explicitly execution_failed.",
            blocked_conditions=["phase74_result_not_executed"],
            next_action="provide_executed_or_failed_phase74_result_for_review",
        )

    missing = _missing_review_requirements(execution_result)
    if missing:
        return _review_result(
            status="blocked",
            execution_result=execution_result,
            reason="Phase 74 execution result is missing review requirements.",
            detail="Phase 75 requires task identity, source authorization, selected candidate summary, bounded file scope, case-packet traceability, success criteria, and expected output.",
            missing_requirements=missing,
            blocked_conditions=["phase74_result_missing_review_requirements"],
            next_action="provide_complete_phase74_execution_result_before_review",
        )

    artifact_summary, artifact_missing = _read_artifact_summary(
        execution_result.get("artifact_id"), execution_result.get("artifact_path")
    )
    if artifact_missing:
        return _review_result(
            status="execution_result_missing_artifact",
            execution_result=execution_result,
            reason="Phase 74 execution result is missing an inspectable artifact.",
            detail="Execution was marked as performed, but artifact id/path/file/json could not be fully inspected read-only.",
            artifact_summary=artifact_summary,
            missing_requirements=artifact_missing,
            next_action="operator_may_restore_artifact_or_repair_execution_record_in_later_boundary",
        )

    if not artifact_summary.get("output_present"):
        return _review_result(
            status="needs_operator_review",
            execution_result=execution_result,
            reason="Phase 74 artifact exists but output is empty or not semantically inspectable.",
            detail="The review stayed read-only and found an artifact record, but the artifact output is absent.",
            artifact_summary=artifact_summary,
            next_action="operator_should_inspect_artifact_before_followup_boundary",
        )

    return _review_result(
        status="execution_result_ready_for_operator_review",
        execution_result=execution_result,
        reason="Phase 74 execution result is ready for operator review.",
        detail="The review confirmed an executed Phase 74 result, one selected task, source authorization, bounded case-packet traceability, artifact id/path, and an inspectable local artifact without performing mutation or runtime/model/provider/platform behavior.",
        artifact_summary=artifact_summary,
        next_action="operator_may_review_artifact_and_choose_later_response_boundary",
    )
