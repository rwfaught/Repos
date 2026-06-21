from __future__ import annotations

from typing import Any


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [text for item in value if (text := _normalize_string(item))]


def _normalize_decision(value: Any) -> str:
    return _normalize_string(value).lower()


def _machine_token(value: Any) -> str:
    return _normalize_decision(value).replace("-", "_").replace(" ", "_")


def _extract_phase69_review(authorization_input: dict[str, Any]) -> dict[str, Any] | None:
    if authorization_input.get("case_packet_task_candidate_review") is True:
        return authorization_input

    for key in (
        "phase69_task_candidate_review_result",
        "case_packet_task_candidate_review_result",
        "task_candidate_review_result",
        "phase69_review_result",
        "review_result",
    ):
        value = authorization_input.get(key)
        if isinstance(value, dict):
            return value

    return None


def _extract_operator_decision(authorization_input: dict[str, Any]) -> str:
    for key in (
        "operator_task_creation_decision",
        "operator_case_packet_task_creation_decision",
        "operator_decision",
        "task_creation_decision",
        "decision",
    ):
        text = _normalize_string(authorization_input.get(key))
        if text:
            return text
    return ""


def _is_explicit_authorization_decision(decision: str) -> bool:
    text = _normalize_decision(decision)
    token = _machine_token(decision)

    allowed_tokens = {
        "authorize_task_creation",
        "approve_task_creation",
        "approved_task_creation",
        "task_creation_authorized",
        "authorized_task_creation",
        "operator_authorizes_task_creation",
    }

    if token in allowed_tokens:
        return True

    return (
        ("authorize" in text or "approve" in text or "approved" in text or "authorizes" in text)
        and "task creation" in text
        and not _contains_forbidden_bundled_request({"operator_decision": decision})
    )


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
        ):
            fields.append(value.get(key))
    else:
        fields.append(value)

    allowed_exact_tokens = {
        "authorize_task_creation",
        "approve_task_creation",
        "approved_task_creation",
        "task_creation_authorized",
        "authorized_task_creation",
        "operator_authorizes_task_creation",
    }

    execution_or_platform_terms = [
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

    task_creation_bundling_terms = [
        "create task now",
        "create the task",
        "create a task",
        "also create task",
        "then create task",
        "persist task",
        "task persistence",
        "create and",
    ]

    for field in fields:
        text = _normalize_decision(field)
        if not text:
            continue
        token = _machine_token(text)
        if token in allowed_exact_tokens:
            continue
        if any(term in text for term in execution_or_platform_terms):
            return True
        if any(term in text for term in task_creation_bundling_terms):
            return True

    return False


def _review_implies_forbidden_activity(review: dict[str, Any]) -> list[str]:
    blocked_conditions: list[str] = []

    forbidden_true_fields = {
        "task_created": "phase69_review_implies_task_creation",
        "planner_invoked": "phase69_review_implies_planner_invocation",
        "runtime_executed": "phase69_review_implies_runtime_execution",
        "model_executed": "phase69_review_implies_model_execution",
        "platform_invoked": "phase69_review_implies_platform_execution",
        "openclaw_invoked": "phase69_review_implies_openclaw_execution",
        "discord_invoked": "phase69_review_implies_discord_execution",
        "bridge_invoked": "phase69_review_implies_bridge_execution",
        "adapter_invoked": "phase69_review_implies_adapter_execution",
        "mutation_performed": "phase69_review_implies_mutation",
        "execution_performed": "phase69_review_implies_execution",
    }

    for field, condition in forbidden_true_fields.items():
        if bool(review.get(field)):
            blocked_conditions.append(condition)

    if _contains_forbidden_bundled_request(review):
        blocked_conditions.append("phase69_review_contains_forbidden_bundled_behavior")

    return sorted(set(blocked_conditions))


def _candidate_missing_requirements(review: dict[str, Any]) -> list[str]:
    candidate = review.get("candidate_summary")
    source_summary = review.get("source_case_packet_summary")
    missing: list[str] = []

    if not isinstance(candidate, dict):
        return ["candidate_summary"]

    objective = _normalize_string(candidate.get("objective_text")) or _normalize_string(
        candidate.get("likely_bounded_task_description")
    )
    if not objective:
        missing.append("candidate_summary.objective_text")

    file_surface = candidate.get("declared_or_inferred_file_surface")
    files: list[str] = []
    if isinstance(file_surface, dict):
        files = _normalize_string_list(file_surface.get("files"))

    if not files:
        missing.append("candidate_summary.declared_or_inferred_file_surface.files")
    elif any(item.lower() in {".", "*", "repo", "repository", "entire repo", "whole repo"} for item in files):
        missing.append("candidate_summary.bounded_file_surface")

    if not isinstance(source_summary, dict) or not source_summary:
        missing.append("source_case_packet_summary")

    return missing


def _phase69_review_summary(review: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_packet_task_candidate_review": bool(review.get("case_packet_task_candidate_review")),
        "task_candidate_status": _normalize_string(review.get("task_candidate_status")),
        "reason": _normalize_string(review.get("reason")),
        "detail": _normalize_string(review.get("detail")),
        "next_action": _normalize_string(review.get("next_action")),
    }


def _authorization_result(
    status: str,
    review: dict[str, Any] | None,
    reason: str,
    detail: str,
    operator_decision: str = "",
    missing_requirements: list[str] | None = None,
    blocked_conditions: list[str] | None = None,
    next_action: str = "",
) -> dict[str, Any]:
    review_dict = review if isinstance(review, dict) else {}
    candidate_summary = review_dict.get("candidate_summary")
    source_case_packet_summary = review_dict.get("source_case_packet_summary")

    return {
        "case_packet_task_creation_authorization": True,
        "case_id": _normalize_string(review_dict.get("case_id")),
        "case_packet_path": _normalize_string(review_dict.get("case_packet_path")),
        "task_creation_authorization": status,
        "task_creation_authorized": status == "task_creation_authorized",
        "reason": reason,
        "detail": detail,
        "operator_decision": operator_decision,
        "missing_requirements": list(missing_requirements or []),
        "blocked_conditions": list(blocked_conditions or []),
        "candidate_summary": dict(candidate_summary) if isinstance(candidate_summary, dict) else {},
        "source_case_packet_summary": dict(source_case_packet_summary)
        if isinstance(source_case_packet_summary, dict)
        else {},
        "phase69_review_summary": _phase69_review_summary(review_dict),
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


def authorize_task_creation_from_case_packet_candidate_review(
    authorization_input: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(authorization_input, dict):
        return _authorization_result(
            status="blocked",
            review=None,
            reason="Authorization input must be a JSON object.",
            detail="Phase 70 requires a Phase 69 task-candidate review result plus an explicit operator task-creation decision.",
            blocked_conditions=["json_object_input_required"],
            next_action="provide_phase69_task_candidate_review_before_task_creation_authorization",
        )

    review = _extract_phase69_review(authorization_input)
    operator_decision = _extract_operator_decision(authorization_input)

    if _contains_forbidden_bundled_request(authorization_input):
        return _authorization_result(
            status="blocked",
            review=review,
            reason="Authorization request includes forbidden bundled behavior.",
            detail="Phase 70 may authorize task creation only; it cannot create a task, invoke a planner, execute runtime/model/platform behavior, or touch OpenClaw, Discord, bridge, adapter, installer, WSL, vendoring, cleanup, deletion, archive, oz, or Codex.",
            operator_decision=operator_decision,
            blocked_conditions=["unsupported_bundled_behavior_request"],
            next_action="separate_authorization_from_task_creation_or_execution",
        )

    if review is None:
        return _authorization_result(
            status="blocked",
            review=None,
            reason="Phase 69 task-candidate review result is missing.",
            detail="Phase 70 must derive from an explicit Phase 69 task-candidate review result.",
            operator_decision=operator_decision,
            blocked_conditions=["phase69_task_candidate_review_result_missing"],
            next_action="run_or_provide_phase69_task_candidate_review_before_authorization",
        )

    if review.get("case_packet_task_candidate_review") is not True:
        return _authorization_result(
            status="blocked",
            review=review,
            reason="Input is not a Phase 69 task-candidate review result.",
            detail="Phase 70 only authorizes task creation from an explicit Phase 69 review object.",
            operator_decision=operator_decision,
            blocked_conditions=["input_not_phase69_task_candidate_review_result"],
            next_action="provide_valid_phase69_task_candidate_review_result",
        )

    review_blocked_conditions = _review_implies_forbidden_activity(review)
    if review_blocked_conditions:
        return _authorization_result(
            status="blocked",
            review=review,
            reason="Phase 69 review implies forbidden prior or bundled activity.",
            detail="Phase 70 cannot authorize task creation from a review that already implies task creation, planner invocation, mutation, execution, runtime/model/platform behavior, OpenClaw, Discord, bridge, or adapter behavior.",
            operator_decision=operator_decision,
            blocked_conditions=review_blocked_conditions,
            next_action="resolve_phase69_review_integrity_before_authorization",
        )

    if _normalize_string(review.get("task_candidate_status")) != "task_candidate_ready":
        return _authorization_result(
            status="blocked",
            review=review,
            reason="Phase 69 task-candidate review is not ready.",
            detail="Only a Phase 69 task_candidate_ready result may proceed to task-creation authorization.",
            operator_decision=operator_decision,
            blocked_conditions=["phase69_task_candidate_not_ready"],
            next_action="resolve_phase69_task_candidate_review_before_authorization",
        )

    candidate_missing = _candidate_missing_requirements(review)
    if candidate_missing:
        return _authorization_result(
            status="blocked",
            review=review,
            reason="Phase 69 ready review is missing authorization-critical candidate detail.",
            detail="Phase 70 requires objective text, bounded file surface, and inspectable source case-packet summary before task creation can be authorized.",
            operator_decision=operator_decision,
            missing_requirements=candidate_missing,
            blocked_conditions=["phase69_ready_review_missing_authorization_requirements"],
            next_action="repair_or_repeat_phase69_review_before_authorization",
        )

    if not operator_decision:
        return _authorization_result(
            status="needs_operator_decision",
            review=review,
            reason="Explicit operator task-creation authorization is missing.",
            detail="Phase 70 requires explicit operator authorization before any later task-creation write gate.",
            operator_decision="",
            missing_requirements=["operator_task_creation_decision"],
            next_action="operator_must_choose_whether_to_authorize_task_creation",
        )

    if not _is_explicit_authorization_decision(operator_decision):
        return _authorization_result(
            status="needs_operator_decision",
            review=review,
            reason="Operator decision is ambiguous.",
            detail="The operator decision did not explicitly authorize task creation and does not block the boundary outright.",
            operator_decision=operator_decision,
            missing_requirements=["explicit_operator_task_creation_authorization"],
            next_action="operator_must_provide_explicit_task_creation_authorization_or_decline",
        )

    return _authorization_result(
        status="task_creation_authorized",
        review=review,
        reason="Operator explicitly authorized task creation from a Phase 69 ready candidate.",
        detail="Phase 70 records authorization only; no task was created, no planner was invoked, and no runtime/model/platform behavior occurred.",
        operator_decision=operator_decision,
        next_action="operator_may_choose_explicit_authorized_task_creation_write_gate",
    )
