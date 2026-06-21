from __future__ import annotations

from typing import Any

_BROAD_FILE_SURFACE_TOKENS = {"*", ".", "./", "all", "repo", "repository", "project", "workspace", "entire repo", "whole repo"}

_FORBIDDEN_TRUE_FIELDS = {
    "task_created": "phase72_surface_implies_task_creation",
    "task_mutated": "phase72_surface_implies_task_mutation",
    "task_executed": "phase72_surface_implies_task_execution",
    "planner_invoked": "phase72_surface_implies_planner_invocation",
    "runtime_executed": "phase72_surface_implies_runtime_execution",
    "model_executed": "phase72_surface_implies_model_execution",
    "platform_invoked": "phase72_surface_implies_platform_execution",
    "openclaw_invoked": "phase72_surface_implies_openclaw_execution",
    "discord_invoked": "phase72_surface_implies_discord_execution",
    "bridge_invoked": "phase72_surface_implies_bridge_execution",
    "adapter_invoked": "phase72_surface_implies_adapter_execution",
    "installer_invoked": "phase72_surface_implies_installer_execution",
    "wsl_invoked": "phase72_surface_implies_wsl_execution",
    "verifier_invoked": "phase72_surface_implies_verifier_execution",
    "reviewer_invoked": "phase72_surface_implies_reviewer_execution",
    "mutation_performed": "phase72_surface_implies_mutation",
    "execution_performed": "phase72_surface_implies_execution",
    "cleanup_performed": "phase72_surface_implies_cleanup",
    "deletion_performed": "phase72_surface_implies_deletion",
    "archive_performed": "phase72_surface_implies_archive",
    "oz_invoked": "phase72_surface_implies_oz",
    "codex_invoked": "phase72_surface_implies_codex",
}

_NON_EXECUTION_FLAGS = {
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


def _normalize_decision(value: Any) -> str:
    return _normalize_string(value).lower()


def _machine_token(value: Any) -> str:
    return _normalize_decision(value).replace("-", "_").replace(" ", "_")


def _allowed_authorization_tokens() -> set[str]:
    return {
        "authorize_task_execution",
        "approve_task_execution",
        "approved_task_execution",
        "task_execution_authorized",
        "authorized_task_execution",
        "operator_authorizes_task_execution",
        "authorize_execution",
        "approve_execution",
        "execution_authorized",
    }


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
            "operator_task_execution_decision",
            "operator_case_packet_task_execution_decision",
            "task_execution_decision",
            "decision",
        ):
            fields.append(value.get(key))
    else:
        fields.append(value)

    platform_terms = [
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
        "vendor",
        "cleanup",
        "clean up",
        "delete",
        "archive",
        "oz",
        "codex",
    ]
    execution_bundling_terms = [
        "execute now",
        "execute it",
        "execute the task",
        "execute this task",
        "run the task",
        "run this task",
        "also execute",
        "then execute",
        "authorize and execute",
        "approve and execute",
        "start execution",
        "perform execution",
        "create execution artifact",
        "write execution artifact",
        "execute and",
    ]

    for field in fields:
        text = _normalize_decision(field)
        if not text:
            continue
        token = _machine_token(text)
        if token in _allowed_authorization_tokens():
            continue
        if any(term in text for term in platform_terms):
            return True
        if any(term in text for term in execution_bundling_terms):
            return True

    return False


def _extract_phase72_surface(authorization_input: dict[str, Any]) -> dict[str, Any] | None:
    if authorization_input.get("case_packet_task_execution_candidate_surface") is True:
        return authorization_input

    for key in (
        "phase72_task_execution_candidate_surface_result",
        "case_packet_task_execution_candidate_surface_result",
        "task_execution_candidate_surface_result",
        "execution_candidate_surface_result",
        "phase72_surface_result",
        "surface_result",
    ):
        value = authorization_input.get(key)
        if isinstance(value, dict):
            return value

    return None


def _extract_operator_decision(authorization_input: dict[str, Any]) -> str:
    for key in (
        "operator_task_execution_decision",
        "operator_case_packet_task_execution_decision",
        "operator_execution_decision",
        "operator_decision",
        "task_execution_decision",
        "decision",
    ):
        text = _normalize_string(authorization_input.get(key))
        if text:
            return text
    return ""


def _extract_selected_task_id(authorization_input: dict[str, Any]) -> str:
    for key in (
        "selected_task_id",
        "task_id",
        "selected_candidate_task_id",
        "case_packet_task_execution_candidate_task_id",
    ):
        text = _normalize_string(authorization_input.get(key))
        if text:
            return text

    for key in ("selected_candidate", "selected_task", "candidate"):
        value = authorization_input.get(key)
        if isinstance(value, dict):
            text = _normalize_string(value.get("task_id"))
            if text:
                return text

    return ""


def _is_explicit_authorization_decision(decision: str) -> bool:
    text = _normalize_decision(decision)
    token = _machine_token(decision)

    if token in _allowed_authorization_tokens():
        return True

    authorization_words = ("authorize", "approve", "approved", "authorizes", "authorization")
    execution_words = ("task execution", "execution")
    return (
        any(word in text for word in authorization_words)
        and any(word in text for word in execution_words)
        and not _contains_forbidden_bundled_request({"operator_decision": decision})
    )


def _surface_blocked_conditions(surface: dict[str, Any]) -> list[str]:
    blocked: list[str] = []

    if surface.get("case_packet_task_execution_candidate_surface") is not True:
        blocked.append("input_not_phase72_case_packet_task_execution_candidate_surface")

    for field, condition in _FORBIDDEN_TRUE_FIELDS.items():
        if bool(surface.get(field)):
            blocked.append(condition)

    if _contains_forbidden_bundled_request(surface):
        blocked.append("phase72_surface_contains_forbidden_bundled_behavior")

    return sorted(set(blocked))


def _has_broad_file_surface(files: list[str]) -> bool:
    for file_name in files:
        text = file_name.lower().strip().replace("\\", "/")
        if text in _BROAD_FILE_SURFACE_TOKENS:
            return True
        if text.endswith("/*") or text.endswith("/**"):
            return True
    return False


def _candidate_blocked_conditions(candidate: dict[str, Any]) -> list[str]:
    blocked: list[str] = []

    if _normalize_string(candidate.get("execution_candidate_status")) != "case_packet_task_execution_candidate":
        blocked.append("selected_candidate_not_case_packet_task_execution_candidate")
    if _normalize_string(candidate.get("status")) != "queued":
        blocked.append("selected_candidate_status_not_queued")
    if not _normalize_string(candidate.get("task_path")):
        blocked.append("selected_candidate_missing_task_path")

    files = _normalize_string_list(candidate.get("files_in_scope"))
    if not files:
        blocked.append("selected_candidate_missing_bounded_file_scope")
    elif _has_broad_file_surface(files):
        blocked.append("selected_candidate_file_scope_broad_or_ambiguous")

    if not _normalize_string(candidate.get("source_case_packet_identity")) and not _normalize_string(candidate.get("source_artifact_id")):
        blocked.append("selected_candidate_missing_case_packet_traceability")
    if not _normalize_string_list(candidate.get("success_criteria")):
        blocked.append("selected_candidate_missing_success_criteria")
    if not _normalize_string(candidate.get("expected_output")):
        blocked.append("selected_candidate_missing_expected_output")

    if _candidate_text_implies_forbidden_behavior(candidate):
        blocked.append("selected_candidate_text_implies_forbidden_execution_or_platform_behavior")

    return sorted(set(blocked))


def _candidate_text_implies_forbidden_behavior(candidate: dict[str, Any]) -> bool:
    fields: list[str] = [
        _normalize_string(candidate.get("title")),
        _normalize_string(candidate.get("expected_output")),
    ]
    fields.extend(_normalize_string_list(candidate.get("success_criteria")))

    forbidden_terms = [
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
        "execute now",
        "execute the task",
        "run model",
        "vendor",
        "cleanup",
        "clean up",
        "delete",
        "archive",
        "oz",
        "codex",
    ]

    for field in fields:
        text = field.lower()
        if any(term in text for term in forbidden_terms):
            return True
    return False


def _candidate_summary(candidate: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        return {}
    return {
        "task_id": _normalize_string(candidate.get("task_id")),
        "task_path": _normalize_string(candidate.get("task_path")),
        "run_id": _normalize_string(candidate.get("run_id")),
        "title": _normalize_string(candidate.get("title")),
        "status": _normalize_string(candidate.get("status")),
        "role": _normalize_string(candidate.get("role")),
        "files_in_scope": _normalize_string_list(candidate.get("files_in_scope")),
        "success_criteria": _normalize_string_list(candidate.get("success_criteria")),
        "expected_output": _normalize_string(candidate.get("expected_output")),
        "source_artifact_id": _normalize_string(candidate.get("source_artifact_id")),
        "source_case_packet_identity": _normalize_string(candidate.get("source_case_packet_identity")),
        "execution_candidate_status": _normalize_string(candidate.get("execution_candidate_status")),
    }


def _surface_summary(surface: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(surface, dict):
        return {}
    return {
        "case_packet_task_execution_candidate_surface": bool(surface.get("case_packet_task_execution_candidate_surface")),
        "run_id": _normalize_string(surface.get("run_id")),
        "candidate_count": int(surface.get("candidate_count") or 0),
        "excluded_count": int(surface.get("excluded_count") or 0),
        "reason": _normalize_string(surface.get("reason")),
        "detail": _normalize_string(surface.get("detail")),
        "next_action": _normalize_string(surface.get("next_action")),
    }


def _authorization_result(
    status: str,
    surface: dict[str, Any] | None,
    selected_candidate: dict[str, Any] | None,
    selected_task_id: str,
    reason: str,
    detail: str,
    operator_decision: str = "",
    missing_requirements: list[str] | None = None,
    blocked_conditions: list[str] | None = None,
    next_action: str = "",
) -> dict[str, Any]:
    candidate_summary = _candidate_summary(selected_candidate)
    task_id = _normalize_string(candidate_summary.get("task_id")) or selected_task_id
    return {
        "case_packet_task_execution_authorization_gate": True,
        "run_id": _normalize_string(candidate_summary.get("run_id")) or _normalize_string((surface or {}).get("run_id")),
        "task_id": task_id,
        "task_path": _normalize_string(candidate_summary.get("task_path")),
        "task_execution_authorization": status,
        "task_execution_authorized": status == "task_execution_authorized",
        "reason": reason,
        "detail": detail,
        "blocked_conditions": list(blocked_conditions or []),
        "missing_requirements": list(missing_requirements or []),
        "selected_candidate_summary": candidate_summary,
        "source_candidate_surface_summary": _surface_summary(surface),
        "operator_decision": operator_decision,
        "next_action": next_action,
        **_NON_EXECUTION_FLAGS,
    }


def authorize_case_packet_task_execution_from_candidate_surface(
    authorization_input: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(authorization_input, dict):
        return _authorization_result(
            status="blocked",
            surface=None,
            selected_candidate=None,
            selected_task_id="",
            reason="Authorization input must be a JSON object.",
            detail="Phase 73 requires a Phase 72 candidate surface, one selected candidate task id, and an explicit operator task-execution authorization decision.",
            blocked_conditions=["json_object_input_required"],
            next_action="provide_phase72_candidate_surface_before_task_execution_authorization",
        )

    surface = _extract_phase72_surface(authorization_input)
    operator_decision = _extract_operator_decision(authorization_input)
    selected_task_id = _extract_selected_task_id(authorization_input)

    if _contains_forbidden_bundled_request(authorization_input):
        return _authorization_result(
            status="blocked",
            surface=surface,
            selected_candidate=None,
            selected_task_id=selected_task_id,
            reason="Authorization request includes forbidden bundled behavior.",
            detail="Phase 73 may authorize later task execution only; it cannot execute the task, create execution artifacts, invoke planner/reviewer/verifier/runtime/model/platform behavior, or touch OpenClaw, Discord, bridge, adapter, installer, WSL, vendoring, cleanup, deletion, archive, oz, or Codex.",
            operator_decision=operator_decision,
            blocked_conditions=["unsupported_bundled_behavior_request"],
            next_action="separate_execution_authorization_from_actual_execution",
        )

    if surface is None:
        return _authorization_result(
            status="blocked",
            surface=None,
            selected_candidate=None,
            selected_task_id=selected_task_id,
            reason="Phase 72 task execution-candidate surface is missing.",
            detail="Phase 73 can authorize later execution only from an explicit Phase 72 case-packet task execution-candidate surface.",
            operator_decision=operator_decision,
            blocked_conditions=["phase72_task_execution_candidate_surface_missing"],
            next_action="run_or_provide_phase72_candidate_surface_before_authorization",
        )

    surface_blocked = _surface_blocked_conditions(surface)
    if surface_blocked:
        return _authorization_result(
            status="blocked",
            surface=surface,
            selected_candidate=None,
            selected_task_id=selected_task_id,
            reason="Phase 72 candidate surface is not authorization-safe.",
            detail="Phase 73 cannot authorize execution from a surface that is not a Phase 72 candidate surface or that implies mutation, execution, runtime/model/platform behavior, OpenClaw, Discord, bridge, adapter, verifier, reviewer, cleanup, deletion, archive, oz, or Codex behavior.",
            operator_decision=operator_decision,
            blocked_conditions=surface_blocked,
            next_action="resolve_phase72_candidate_surface_integrity_before_authorization",
        )

    if not selected_task_id:
        return _authorization_result(
            status="needs_operator_decision",
            surface=surface,
            selected_candidate=None,
            selected_task_id="",
            reason="Selected case-packet task execution candidate is missing.",
            detail="Phase 73 requires the operator to select exactly one Phase 72 candidate task before execution authorization can be recorded.",
            operator_decision=operator_decision,
            missing_requirements=["selected_task_id"],
            next_action="operator_must_select_one_phase72_candidate_task",
        )

    candidates_value = surface.get("candidates")
    candidates = candidates_value if isinstance(candidates_value, list) else []
    matches = [candidate for candidate in candidates if isinstance(candidate, dict) and _normalize_string(candidate.get("task_id")) == selected_task_id]

    if not matches:
        return _authorization_result(
            status="blocked",
            surface=surface,
            selected_candidate=None,
            selected_task_id=selected_task_id,
            reason="Selected task is not present in the Phase 72 candidate list.",
            detail="Phase 73 can authorize only one task that appears in the Phase 72 candidates list.",
            operator_decision=operator_decision,
            blocked_conditions=["selected_task_absent_from_phase72_candidates"],
            next_action="select_task_from_phase72_candidates_before_authorization",
        )

    if len(matches) > 1:
        return _authorization_result(
            status="blocked",
            surface=surface,
            selected_candidate=None,
            selected_task_id=selected_task_id,
            reason="Selected task appears more than once in the Phase 72 candidate list.",
            detail="Phase 73 requires exactly one matching selected candidate before authorization can be recorded.",
            operator_decision=operator_decision,
            blocked_conditions=["selected_task_not_unique_in_phase72_candidates"],
            next_action="repair_phase72_candidate_surface_before_authorization",
        )

    selected_candidate = matches[0]
    candidate_blocked = _candidate_blocked_conditions(selected_candidate)
    if candidate_blocked:
        return _authorization_result(
            status="blocked",
            surface=surface,
            selected_candidate=selected_candidate,
            selected_task_id=selected_task_id,
            reason="Selected candidate does not satisfy Phase 73 authorization requirements.",
            detail="Phase 73 requires a queued Phase 72 case-packet task execution candidate with bounded file scope, case-packet traceability, success criteria, expected output, and no forbidden execution/platform implications.",
            operator_decision=operator_decision,
            blocked_conditions=candidate_blocked,
            next_action="repair_or_resurface_phase72_candidate_before_authorization",
        )

    if not operator_decision:
        return _authorization_result(
            status="needs_operator_decision",
            surface=surface,
            selected_candidate=selected_candidate,
            selected_task_id=selected_task_id,
            reason="Explicit operator task-execution authorization is missing.",
            detail="Phase 73 requires explicit operator authorization before any later case-packet task execution boundary.",
            operator_decision="",
            missing_requirements=["operator_task_execution_decision"],
            next_action="operator_must_choose_whether_to_authorize_task_execution",
        )

    if not _is_explicit_authorization_decision(operator_decision):
        return _authorization_result(
            status="needs_operator_decision",
            surface=surface,
            selected_candidate=selected_candidate,
            selected_task_id=selected_task_id,
            reason="Operator decision is ambiguous.",
            detail="The operator decision did not explicitly authorize task execution and does not block the boundary outright.",
            operator_decision=operator_decision,
            missing_requirements=["explicit_operator_task_execution_authorization"],
            next_action="operator_must_provide_explicit_task_execution_authorization_or_decline",
        )

    return _authorization_result(
        status="task_execution_authorized",
        surface=surface,
        selected_candidate=selected_candidate,
        selected_task_id=selected_task_id,
        reason="Operator explicitly authorized later execution of one Phase 72 case-packet task execution candidate.",
        detail="Phase 73 records authorization only; no task was created, mutated, or executed, no execution artifact was created, and no planner, reviewer, verifier, runtime, model, provider, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, cleanup, deletion, archive, oz, or Codex behavior occurred.",
        operator_decision=operator_decision,
        next_action="operator_may_choose_later_explicit_case_packet_task_execution_boundary",
    )