from __future__ import annotations

from typing import Any


_FORBIDDEN_RESPONSE_REQUEST_TERMS = [
    "execute",
    "rerun",
    "run again",
    "mutate",
    "create",
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

_PHASE75_CLASSIFICATIONS = {
    "execution_result_ready_for_operator_review",
    "needs_operator_review",
    "execution_result_missing_artifact",
    "execution_result_failed",
    "blocked",
}

_READ_ONLY_FLAGS = {
    "task_created": False,
    "task_mutated": False,
    "task_executed": False,
    "execution_performed": False,
    "artifact_created": False,
    "artifact_mutated": False,
    "followup_created": False,
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


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _extract_phase75_review_result(response_input: dict[str, Any]) -> dict[str, Any] | None:
    if response_input.get("case_packet_task_execution_result_review_surface") is True:
        return response_input

    for key in (
        "phase75_review_result",
        "phase75_task_execution_result_review",
        "case_packet_task_execution_result_review",
        "source_review_result",
        "review_result",
    ):
        value = response_input.get(key)
        if isinstance(value, dict):
            return value

    return None


def _contains_forbidden_response_request(response_input: dict[str, Any]) -> bool:
    fields: list[Any] = []
    for key in (
        "requested_action",
        "requested_behavior",
        "requested_next_move",
        "operator_request",
        "operator_decision",
        "response_request",
        "provider_name",
        "runtime_name",
        "model_name",
    ):
        fields.append(response_input.get(key))

    for field in fields:
        text = _normalize_string(field).lower()
        if not text:
            continue
        if any(term in text for term in _FORBIDDEN_RESPONSE_REQUEST_TERMS):
            return True
    return False


def _missing_requirements(review_result: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if not _normalize_string(review_result.get("execution_result_review")):
        missing.append("execution_result_review")
    if not _normalize_string(review_result.get("task_id")):
        missing.append("task_id")
    if not _normalize_string(review_result.get("task_path")):
        missing.append("task_path")
    if not _as_dict(review_result.get("source_execution_summary")):
        missing.append("source_execution_summary")
    if not _as_dict(review_result.get("source_authorization_summary")):
        missing.append("source_authorization_summary")
    if not _as_dict(review_result.get("selected_candidate_summary")):
        missing.append("selected_candidate_summary")
    return missing


def _review_summary(review_result: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(review_result, dict):
        return {}
    return {
        "case_packet_task_execution_result_review_surface": bool(review_result.get("case_packet_task_execution_result_review_surface")),
        "execution_result_review": _normalize_string(review_result.get("execution_result_review")),
        "ready_for_operator_review": bool(review_result.get("ready_for_operator_review")),
        "run_id": _normalize_string(review_result.get("run_id")),
        "task_id": _normalize_string(review_result.get("task_id")),
        "task_path": _normalize_string(review_result.get("task_path")),
        "artifact_id": _normalize_string(review_result.get("artifact_id")),
        "artifact_path": _normalize_string(review_result.get("artifact_path")),
        "reason": _normalize_string(review_result.get("reason")),
        "next_action": _normalize_string(review_result.get("next_action")),
    }


def _response_options_for(classification: str) -> tuple[str, list[dict[str, Any]], str, str]:
    if classification == "execution_result_ready_for_operator_review":
        return (
            "ready_result_response_options",
            [
                {
                    "option_id": "inspect_artifact_manually",
                    "label": "Inspect the artifact manually.",
                    "requires_later_boundary": False,
                    "authorized_now": True,
                },
                {
                    "option_id": "accept_current_local_result_for_now",
                    "label": "Accept the current local result as sufficient for now.",
                    "requires_later_boundary": True,
                    "later_boundary": "operator_acceptance_record_boundary",
                    "authorized_now": False,
                },
                {
                    "option_id": "define_later_operator_response_boundary",
                    "label": "Define a later explicit operator-response boundary if follow-up is needed.",
                    "requires_later_boundary": True,
                    "later_boundary": "followup_response_definition_boundary",
                    "authorized_now": False,
                },
                {
                    "option_id": "no_immediate_followup",
                    "label": "Take no immediate follow-up action.",
                    "requires_later_boundary": False,
                    "authorized_now": True,
                },
            ],
            "Phase 75 result is ready for operator review.",
            "operator_may_inspect_artifact_or_choose_later_response_boundary",
        )

    if classification == "needs_operator_review":
        return (
            "needs_review_response_options",
            [
                {
                    "option_id": "inspect_artifact_manually",
                    "label": "Inspect the artifact manually before deciding adequacy.",
                    "requires_later_boundary": False,
                    "authorized_now": True,
                },
                {
                    "option_id": "define_followup_review_task_creation_boundary",
                    "label": "Define a later follow-up review task creation boundary.",
                    "requires_later_boundary": True,
                    "later_boundary": "followup_review_task_creation_boundary",
                    "authorized_now": False,
                },
                {
                    "option_id": "define_repair_or_clarification_boundary",
                    "label": "Define a later repair or clarification boundary if the artifact is inadequate.",
                    "requires_later_boundary": True,
                    "later_boundary": "repair_or_clarification_boundary",
                    "authorized_now": False,
                },
            ],
            "Phase 75 result needs operator review.",
            "operator_should_inspect_artifact_before_any_followup_boundary",
        )

    if classification == "execution_result_missing_artifact":
        return (
            "missing_artifact_response_options",
            [
                {
                    "option_id": "inspect_missing_artifact_reference",
                    "label": "Inspect the missing artifact reference.",
                    "requires_later_boundary": False,
                    "authorized_now": True,
                },
                {
                    "option_id": "define_artifact_record_repair_boundary",
                    "label": "Define a later artifact-record repair boundary.",
                    "requires_later_boundary": True,
                    "later_boundary": "artifact_record_repair_boundary",
                    "authorized_now": False,
                },
                {
                    "option_id": "define_later_reexecution_boundary",
                    "label": "Define a later re-execution boundary only if explicitly authorized.",
                    "requires_later_boundary": True,
                    "later_boundary": "authorized_reexecution_boundary",
                    "authorized_now": False,
                },
            ],
            "Phase 75 result reports missing artifact context.",
            "operator_may_inspect_missing_artifact_reference_before_repair_or_reexecution_boundary",
        )

    if classification == "execution_result_failed":
        return (
            "failed_result_response_options",
            [
                {
                    "option_id": "inspect_failure_detail",
                    "label": "Inspect failure detail.",
                    "requires_later_boundary": False,
                    "authorized_now": True,
                },
                {
                    "option_id": "define_repair_boundary",
                    "label": "Define a later repair boundary.",
                    "requires_later_boundary": True,
                    "later_boundary": "execution_result_repair_boundary",
                    "authorized_now": False,
                },
                {
                    "option_id": "define_later_retry_boundary",
                    "label": "Define a later retry boundary only if explicitly authorized.",
                    "requires_later_boundary": True,
                    "later_boundary": "authorized_retry_boundary",
                    "authorized_now": False,
                },
            ],
            "Phase 75 result reports execution failure.",
            "operator_may_inspect_failure_detail_before_repair_or_retry_boundary",
        )

    return (
        "blocked_result_response_options",
        [
            {
                "option_id": "inspect_blocked_conditions",
                "label": "Inspect blocked conditions.",
                "requires_later_boundary": False,
                "authorized_now": True,
            },
            {
                "option_id": "return_to_relevant_prior_boundary",
                "label": "Return to the relevant prior phase boundary.",
                "requires_later_boundary": True,
                "later_boundary": "prior_phase_repair_boundary",
                "authorized_now": False,
            },
            {
                "option_id": "repair_source_result_or_authorization",
                "label": "Repair the source result or authorization in a later explicit boundary.",
                "requires_later_boundary": True,
                "later_boundary": "source_result_or_authorization_repair_boundary",
                "authorized_now": False,
            },
        ],
        "Phase 75 result is blocked.",
        "operator_should_inspect_blocked_conditions_before_prior_boundary_repair",
    )


def _result(
    surface: str,
    review_result: dict[str, Any] | None,
    reason: str,
    detail: str,
    response_options: list[dict[str, Any]] | None = None,
    blocked_conditions: list[str] | None = None,
    missing_requirements: list[str] | None = None,
    next_action: str = "",
) -> dict[str, Any]:
    review_result = review_result if isinstance(review_result, dict) else {}
    return {
        "case_packet_task_execution_result_operator_response_surface": True,
        "run_id": _normalize_string(review_result.get("run_id")),
        "task_id": _normalize_string(review_result.get("task_id")),
        "task_path": _normalize_string(review_result.get("task_path")),
        "artifact_id": _normalize_string(review_result.get("artifact_id")),
        "artifact_path": _normalize_string(review_result.get("artifact_path")),
        "source_review_classification": _normalize_string(review_result.get("execution_result_review")),
        "operator_response_surface": surface,
        "response_options": list(response_options or []),
        "blocked_conditions": sorted(set(blocked_conditions or [])),
        "missing_requirements": list(missing_requirements or []),
        "source_review_summary": _review_summary(review_result),
        "source_execution_summary": _as_dict(review_result.get("source_execution_summary")),
        "source_authorization_summary": _as_dict(review_result.get("source_authorization_summary")),
        "selected_candidate_summary": _as_dict(review_result.get("selected_candidate_summary")),
        "artifact_summary": _as_dict(review_result.get("artifact_summary")),
        "task_summary": _as_dict(review_result.get("task_summary")),
        "reason": reason,
        "detail": detail,
        "next_action": next_action,
        **_READ_ONLY_FLAGS,
    }


def surface_case_packet_task_execution_result_response_options(response_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(response_input, dict):
        return _result(
            surface="blocked",
            review_result=None,
            reason="Response input must be a JSON object.",
            detail="Phase 76 requires a Phase 75 result review object or a wrapper containing one.",
            blocked_conditions=["json_object_input_required"],
            next_action="provide_phase75_review_result_for_response_options",
        )

    if _contains_forbidden_response_request(response_input):
        return _result(
            surface="blocked",
            review_result=None,
            reason="Response request asks Phase 76 to do more than read-only option surfacing.",
            detail="Phase 76 cannot execute, mutate, create, verify, review, rerun, repair, clean up, delete, archive, export, call a provider, or touch runtime/model/platform/OpenClaw/Discord/bridge/adapter/installer/WSL behavior.",
            blocked_conditions=["response_request_expands_beyond_read_only_option_surface"],
            next_action="separate_action_into_a_later_explicit_boundary",
        )

    review_result = _extract_phase75_review_result(response_input)
    if review_result is None:
        return _result(
            surface="blocked",
            review_result=None,
            reason="Phase 75 review result is missing.",
            detail="Phase 76 can surface response options only from an explicit Phase 75 case-packet task execution result review.",
            blocked_conditions=["phase75_review_result_missing"],
            next_action="provide_phase75_review_result_for_response_options",
        )

    if review_result.get("case_packet_task_execution_result_review_surface") is not True:
        return _result(
            surface="blocked",
            review_result=review_result,
            reason="Input is not a Phase 75 review result.",
            detail="Phase 76 requires case_packet_task_execution_result_review_surface=true.",
            blocked_conditions=["input_not_phase75_case_packet_task_execution_result_review"],
            next_action="provide_phase75_review_result_for_response_options",
        )

    missing = _missing_requirements(review_result)
    classification = _normalize_string(review_result.get("execution_result_review"))
    if classification and classification not in _PHASE75_CLASSIFICATIONS:
        missing.append("known_execution_result_review_classification")

    if missing:
        return _result(
            surface="blocked",
            review_result=review_result,
            reason="Phase 75 review result is missing response-option requirements.",
            detail="Phase 76 requires review classification, task identity, source execution summary, source authorization summary, and selected candidate summary.",
            blocked_conditions=["phase75_review_result_missing_response_requirements"],
            missing_requirements=missing,
            next_action="provide_complete_phase75_review_result_for_response_options",
        )

    surface, options, reason, next_action = _response_options_for(classification)
    return _result(
        surface=surface,
        review_result=review_result,
        reason=reason,
        detail="Phase 76 surfaced bounded operator response options only. It did not execute, mutate, create follow-up tasks, verify, review, rerun, repair, call providers, or touch runtime/model/platform behavior.",
        response_options=options,
        blocked_conditions=list(review_result.get("blocked_conditions") or []),
        missing_requirements=list(review_result.get("missing_requirements") or []),
        next_action=next_action,
    )