from __future__ import annotations

from typing import Any


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


def _normalize_context(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return dict(value)


def _build_decomposition_handoff(
    objective_text: str,
    provided_artifacts: list[str],
    confirmed_context: dict[str, Any],
) -> dict[str, Any]:
    case_packet_seed_candidate = {
        "objective_text": objective_text,
        "provided_artifacts": list(provided_artifacts),
        "confirmed_context": dict(confirmed_context),
        "seed_status": "candidate_only_not_created",
        "creation_status": "not_created",
        "authorized_use": "operator_inspection_before_case_packet_creation",
    }

    return {
        "source_intake_outcome": "proceed",
        "source_intake_linkage": "judge_intake.proceed",
        "objective_text": objective_text,
        "provided_artifacts": list(provided_artifacts),
        "confirmed_context": dict(confirmed_context),
        "handoff_status": "ready_for_bounded_decomposition",
        "authorized_next_action": "begin_decomposition",
        "admission_review_status": "not_reviewed",
        "execution_status": "not_executed",
        "operator_decision_required": "approve_bounded_decomposition_before_case_packet_creation",
        "case_packet_seed_candidate": case_packet_seed_candidate,
    }


def _blocked_admission(reason: str, detail: str, source_outcome: str = "") -> dict[str, Any]:
    return {
        "admission": "blocked",
        "admissible": False,
        "reason": reason,
        "detail": detail,
        "source_outcome": source_outcome,
        "next_action": "resolve_blocked_condition",
        "mutation_performed": False,
        "execution_performed": False,
    }


def _clarify_admission(reason: str, detail: str, source_outcome: str = "") -> dict[str, Any]:
    return {
        "admission": "needs_operator_clarification",
        "admissible": False,
        "reason": reason,
        "detail": detail,
        "source_outcome": source_outcome,
        "next_action": "request_operator_clarification",
        "mutation_performed": False,
        "execution_performed": False,
    }


def assess_decomposition_handoff_admission(admission_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(admission_input, dict):
        return _clarify_admission(
            reason="Admission input must be a JSON object.",
            detail="The admission gate received a non-object input.",
        )

    source_outcome = _normalize_string(admission_input.get("outcome"))
    if "outcome" in admission_input:
        if source_outcome != "proceed":
            return _blocked_admission(
                reason="Only proceed intake results may be admitted.",
                detail=f"Source intake outcome is {source_outcome}.",
                source_outcome=source_outcome,
            )
        handoff = admission_input.get("decomposition_handoff")
    else:
        handoff = admission_input
        source_outcome = _normalize_string(handoff.get("source_intake_outcome"))

    if source_outcome and source_outcome != "proceed":
        return _blocked_admission(
            reason="Only proceed intake results may be admitted.",
            detail=f"Source intake outcome is {source_outcome}.",
            source_outcome=source_outcome,
        )

    if not isinstance(handoff, dict):
        return _blocked_admission(
            reason="Proceed intake result lacks a decomposition handoff.",
            detail="No decomposition_handoff object was available for admission.",
            source_outcome=source_outcome,
        )

    handoff_source_outcome = _normalize_string(handoff.get("source_intake_outcome"))
    if not source_outcome:
        source_outcome = handoff_source_outcome

    if source_outcome != "proceed":
        return _clarify_admission(
            reason="Handoff lacks proceed lineage.",
            detail="A decomposition handoff must preserve source_intake_outcome=proceed before admission.",
            source_outcome=source_outcome,
        )

    objective_text = _normalize_string(handoff.get("objective_text"))
    if not objective_text:
        return _clarify_admission(
            reason="Handoff lacks bounded objective text.",
            detail="A bounded objective_text is required before admission.",
            source_outcome=source_outcome,
        )

    if _normalize_string(handoff.get("handoff_status")) != "ready_for_bounded_decomposition":
        return _clarify_admission(
            reason="Handoff status is not admission-ready.",
            detail="Expected handoff_status=ready_for_bounded_decomposition.",
            source_outcome=source_outcome,
        )

    if _normalize_string(handoff.get("authorized_next_action")) != "begin_decomposition":
        return _blocked_admission(
            reason="Handoff requests an unsupported next action.",
            detail="Only begin_decomposition may pass this admission gate.",
            source_outcome=source_outcome,
        )

    if not _normalize_string(handoff.get("operator_decision_required")):
        return _clarify_admission(
            reason="Handoff lacks an operator decision requirement.",
            detail="Admission requires explicit operator_decision_required text.",
            source_outcome=source_outcome,
        )

    seed = handoff.get("case_packet_seed_candidate")
    if not isinstance(seed, dict):
        return _clarify_admission(
            reason="Handoff lacks a case-packet seed candidate.",
            detail="A candidate seed is required for later operator inspection, but it must not be created here.",
            source_outcome=source_outcome,
        )

    if _normalize_string(seed.get("seed_status")) != "candidate_only_not_created":
        return _blocked_admission(
            reason="Seed candidate is not marked candidate-only.",
            detail="Expected seed_status=candidate_only_not_created.",
            source_outcome=source_outcome,
        )

    if _normalize_string(seed.get("creation_status")) != "not_created":
        return _blocked_admission(
            reason="Handoff implies hidden case-packet creation.",
            detail="Expected creation_status=not_created.",
            source_outcome=source_outcome,
        )

    return {
        "admission": "admissible",
        "admissible": True,
        "reason": "Proceed-derived decomposition handoff is ready for operator-controlled admission review.",
        "detail": "No task, case packet, planner output, runtime execution, or model execution was created by this check.",
        "source_outcome": source_outcome,
        "next_action": "operator_may_choose_bounded_case_packet_seed_review",
        "mutation_performed": False,
        "execution_performed": False,
        "handoff_summary": {
            "objective_text": objective_text,
            "provided_artifacts": list(_normalize_string_list(handoff.get("provided_artifacts"))),
            "handoff_status": handoff.get("handoff_status"),
            "case_packet_seed_status": seed.get("seed_status"),
            "case_packet_creation_status": seed.get("creation_status"),
        },
    }



def _seed_review_result(
    seed_review: str,
    ready: bool,
    reason: str,
    detail: str,
    next_action: str,
    source_outcome: str = "",
    objective_text: str = "",
    provided_artifacts: list[str] | None = None,
    seed_status: str = "",
    creation_status: str = "",
    operator_decision_required: str = "",
    source_intake_linkage: str = "",
    missing_requirements: list[str] | None = None,
    blocked_conditions: list[str] | None = None,
    admission_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "seed_review": seed_review,
        "ready_for_operator_creation_review": ready,
        "reason": reason,
        "detail": detail,
        "source_outcome": source_outcome,
        "next_action": next_action,
        "mutation_performed": False,
        "execution_performed": False,
        "case_packet_created": False,
        "task_created": False,
        "planner_invoked": False,
        "missing_requirements": list(missing_requirements or []),
        "blocked_conditions": list(blocked_conditions or []),
        "admission_summary": dict(admission_summary or {}),
        "seed_summary": {
            "objective_text": objective_text,
            "provided_artifacts": list(provided_artifacts or []),
            "seed_status": seed_status,
            "creation_status": creation_status,
            "operator_decision_required": operator_decision_required,
            "source_intake_linkage": source_intake_linkage,
        },
    }


def _blocked_seed_review(
    reason: str,
    detail: str,
    source_outcome: str = "",
    objective_text: str = "",
    provided_artifacts: list[str] | None = None,
    seed_status: str = "",
    creation_status: str = "",
    operator_decision_required: str = "",
    source_intake_linkage: str = "",
    blocked_conditions: list[str] | None = None,
    admission_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _seed_review_result(
        seed_review="blocked",
        ready=False,
        reason=reason,
        detail=detail,
        source_outcome=source_outcome,
        objective_text=objective_text,
        provided_artifacts=provided_artifacts,
        seed_status=seed_status,
        creation_status=creation_status,
        operator_decision_required=operator_decision_required,
        source_intake_linkage=source_intake_linkage,
        blocked_conditions=blocked_conditions,
        admission_summary=admission_summary,
        next_action="resolve_blocked_condition",
    )


def _clarify_seed_review(
    reason: str,
    detail: str,
    source_outcome: str = "",
    objective_text: str = "",
    provided_artifacts: list[str] | None = None,
    seed_status: str = "",
    creation_status: str = "",
    operator_decision_required: str = "",
    source_intake_linkage: str = "",
    missing_requirements: list[str] | None = None,
    admission_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _seed_review_result(
        seed_review="needs_operator_clarification",
        ready=False,
        reason=reason,
        detail=detail,
        source_outcome=source_outcome,
        objective_text=objective_text,
        provided_artifacts=provided_artifacts,
        seed_status=seed_status,
        creation_status=creation_status,
        operator_decision_required=operator_decision_required,
        source_intake_linkage=source_intake_linkage,
        missing_requirements=missing_requirements,
        admission_summary=admission_summary,
        next_action="request_operator_clarification",
    )


def _extract_handoff_from_review_input(review_input: dict[str, Any]) -> dict[str, Any] | None:
    if "outcome" in review_input:
        handoff = review_input.get("decomposition_handoff")
        return handoff if isinstance(handoff, dict) else None

    if "decomposition_handoff" in review_input:
        handoff = review_input.get("decomposition_handoff")
        return handoff if isinstance(handoff, dict) else None

    return review_input


def _contains_unsupported_execution_request(value: Any) -> bool:
    if isinstance(value, dict):
        fields = [
            value.get("requested_action"),
            value.get("requested_behavior"),
            value.get("authorized_next_action"),
            value.get("authorized_use"),
            value.get("execution_request"),
            value.get("platform_request"),
        ]
    else:
        fields = [value]

    unsupported_terms = [
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
    ]

    for field in fields:
        text = _normalize_string(field).lower()
        if not text:
            continue
        if text == "begin_decomposition":
            continue
        if text == "operator_inspection_before_case_packet_creation":
            continue
        if any(term in text for term in unsupported_terms):
            return True

    return False


def review_case_packet_seed_candidate(review_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(review_input, dict):
        return _clarify_seed_review(
            reason="Seed review input must be a JSON object.",
            detail="The seed review surface received a non-object input.",
            missing_requirements=["json_object_input"],
        )

    admission = assess_decomposition_handoff_admission(review_input)
    admission_summary = {
        "admission": admission.get("admission"),
        "admissible": admission.get("admissible", False),
        "reason": admission.get("reason", ""),
        "next_action": admission.get("next_action", ""),
    }

    if admission.get("admission") == "needs_operator_clarification":
        return _clarify_seed_review(
            reason="Seed review cannot proceed until handoff admission is clarified.",
            detail=admission.get("detail", "The Phase 65 admission gate did not admit this handoff."),
            source_outcome=_normalize_string(admission.get("source_outcome")),
            missing_requirements=["phase65_admissible_handoff"],
            admission_summary=admission_summary,
        )

    if admission.get("admission") != "admissible" or not admission.get("admissible", False):
        return _blocked_seed_review(
            reason="Only Phase 65 admissible handoffs may be seed-reviewed.",
            detail=admission.get("detail", "The Phase 65 admission gate did not admit this handoff."),
            source_outcome=_normalize_string(admission.get("source_outcome")),
            blocked_conditions=["phase65_admission_not_admissible"],
            admission_summary=admission_summary,
        )

    handoff = _extract_handoff_from_review_input(review_input)
    if not isinstance(handoff, dict):
        return _clarify_seed_review(
            reason="Seed review lacks the admitted handoff body.",
            detail="The review input must include the original intake result or decomposition_handoff, not only the admission summary.",
            missing_requirements=["decomposition_handoff"],
            admission_summary=admission_summary,
        )

    source_outcome = _normalize_string(handoff.get("source_intake_outcome"))
    source_intake_linkage = _normalize_string(handoff.get("source_intake_linkage"))
    objective_text = _normalize_string(handoff.get("objective_text"))
    provided_artifacts = _normalize_string_list(handoff.get("provided_artifacts"))
    operator_decision_required = _normalize_string(handoff.get("operator_decision_required"))
    seed = handoff.get("case_packet_seed_candidate")

    if not source_intake_linkage:
        return _blocked_seed_review(
            reason="Seed candidate lacks source intake lineage.",
            detail="Phase 66 requires source_intake_linkage to preserve where the candidate seed came from.",
            source_outcome=source_outcome,
            objective_text=objective_text,
            provided_artifacts=provided_artifacts,
            operator_decision_required=operator_decision_required,
            source_intake_linkage=source_intake_linkage,
            blocked_conditions=["missing_source_intake_linkage"],
            admission_summary=admission_summary,
        )

    if source_intake_linkage != "judge_intake.proceed":
        return _blocked_seed_review(
            reason="Seed candidate source lineage is unsupported.",
            detail="Phase 66 currently admits only judge_intake.proceed lineage.",
            source_outcome=source_outcome,
            objective_text=objective_text,
            provided_artifacts=provided_artifacts,
            operator_decision_required=operator_decision_required,
            source_intake_linkage=source_intake_linkage,
            blocked_conditions=["unsupported_source_intake_linkage"],
            admission_summary=admission_summary,
        )

    if not isinstance(seed, dict):
        return _clarify_seed_review(
            reason="Admitted handoff lacks a reviewable seed candidate.",
            detail="The handoff must include case_packet_seed_candidate for Phase 66 review.",
            source_outcome=source_outcome,
            objective_text=objective_text,
            provided_artifacts=provided_artifacts,
            operator_decision_required=operator_decision_required,
            source_intake_linkage=source_intake_linkage,
            missing_requirements=["case_packet_seed_candidate"],
            admission_summary=admission_summary,
        )

    seed_status = _normalize_string(seed.get("seed_status"))
    creation_status = _normalize_string(seed.get("creation_status"))
    seed_objective = _normalize_string(seed.get("objective_text"))
    seed_provided_artifacts_raw = seed.get("provided_artifacts")
    seed_confirmed_context_raw = seed.get("confirmed_context")
    authorized_use = _normalize_string(seed.get("authorized_use"))

    if seed_status != "candidate_only_not_created":
        return _blocked_seed_review(
            reason="Seed candidate is not candidate-only.",
            detail="Phase 66 requires seed_status=candidate_only_not_created.",
            source_outcome=source_outcome,
            objective_text=seed_objective or objective_text,
            provided_artifacts=provided_artifacts,
            seed_status=seed_status,
            creation_status=creation_status,
            operator_decision_required=operator_decision_required,
            source_intake_linkage=source_intake_linkage,
            blocked_conditions=["seed_not_candidate_only"],
            admission_summary=admission_summary,
        )

    if creation_status != "not_created":
        return _blocked_seed_review(
            reason="Seed candidate implies hidden case-packet creation.",
            detail="Phase 66 requires creation_status=not_created.",
            source_outcome=source_outcome,
            objective_text=seed_objective or objective_text,
            provided_artifacts=provided_artifacts,
            seed_status=seed_status,
            creation_status=creation_status,
            operator_decision_required=operator_decision_required,
            source_intake_linkage=source_intake_linkage,
            blocked_conditions=["hidden_case_packet_creation"],
            admission_summary=admission_summary,
        )

    if "case_id" in seed or "path" in seed or bool(seed.get("created")):
        return _blocked_seed_review(
            reason="Seed candidate contains created case-packet markers.",
            detail="A Phase 66 seed candidate must not contain case_id, path, or created=true markers.",
            source_outcome=source_outcome,
            objective_text=seed_objective or objective_text,
            provided_artifacts=provided_artifacts,
            seed_status=seed_status,
            creation_status=creation_status,
            operator_decision_required=operator_decision_required,
            source_intake_linkage=source_intake_linkage,
            blocked_conditions=["created_case_packet_marker_present"],
            admission_summary=admission_summary,
        )

    if _contains_unsupported_execution_request(seed) or _contains_unsupported_execution_request(handoff):
        return _blocked_seed_review(
            reason="Seed candidate requests unsupported execution behavior.",
            detail="Phase 66 is review-only and cannot authorize runtime, model, platform, Discord, OpenClaw, bridge, adapter, installer, or WSL behavior.",
            source_outcome=source_outcome,
            objective_text=seed_objective or objective_text,
            provided_artifacts=provided_artifacts,
            seed_status=seed_status,
            creation_status=creation_status,
            operator_decision_required=operator_decision_required,
            source_intake_linkage=source_intake_linkage,
            blocked_conditions=["unsupported_execution_or_platform_request"],
            admission_summary=admission_summary,
        )

    missing_requirements: list[str] = []

    if not seed_objective:
        missing_requirements.append("seed_objective_text")

    if seed_objective and objective_text and seed_objective != objective_text:
        missing_requirements.append("seed_objective_matches_handoff_objective")

    if not isinstance(seed_provided_artifacts_raw, list):
        missing_requirements.append("seed_provided_artifacts_list")

    if not isinstance(seed_confirmed_context_raw, dict):
        missing_requirements.append("seed_confirmed_context_object")

    if not authorized_use:
        missing_requirements.append("seed_authorized_use")

    if not operator_decision_required:
        missing_requirements.append("operator_decision_required")

    if missing_requirements:
        return _clarify_seed_review(
            reason="Seed candidate is not yet legible enough for operator creation review.",
            detail="The seed remains candidate-only, but it is missing required review fields.",
            source_outcome=source_outcome,
            objective_text=seed_objective or objective_text,
            provided_artifacts=provided_artifacts,
            seed_status=seed_status,
            creation_status=creation_status,
            operator_decision_required=operator_decision_required,
            source_intake_linkage=source_intake_linkage,
            missing_requirements=missing_requirements,
            admission_summary=admission_summary,
        )

    return _seed_review_result(
        seed_review="ready_for_operator_creation_review",
        ready=True,
        reason="Candidate-only seed is ready for explicit operator-controlled case-packet creation review.",
        detail="No case packet, task, planner output, runtime execution, or model execution was created by this check.",
        source_outcome=source_outcome,
        objective_text=seed_objective,
        provided_artifacts=_normalize_string_list(seed_provided_artifacts_raw),
        seed_status=seed_status,
        creation_status=creation_status,
        operator_decision_required=operator_decision_required,
        source_intake_linkage=source_intake_linkage,
        admission_summary=admission_summary,
        next_action="operator_may_choose_explicit_case_packet_creation_boundary",
    )



def _creation_authorization_result(
    authorization: str,
    authorized: bool,
    reason: str,
    detail: str,
    next_action: str,
    operator_decision: str = "",
    missing_requirements: list[str] | None = None,
    blocked_conditions: list[str] | None = None,
    seed_review_summary: dict[str, Any] | None = None,
    admission_summary: dict[str, Any] | None = None,
    seed_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "creation_authorization": authorization,
        "case_packet_creation_authorized": authorized,
        "reason": reason,
        "detail": detail,
        "operator_decision": operator_decision,
        "next_action": next_action,
        "case_packet_created": False,
        "case_packet_persisted": False,
        "task_created": False,
        "planner_invoked": False,
        "mutation_performed": False,
        "execution_performed": False,
        "missing_requirements": list(missing_requirements or []),
        "blocked_conditions": list(blocked_conditions or []),
        "seed_review_summary": dict(seed_review_summary or {}),
        "admission_summary": dict(admission_summary or {}),
        "seed_summary": dict(seed_summary or {}),
    }


def _blocked_creation_authorization(
    reason: str,
    detail: str,
    operator_decision: str = "",
    blocked_conditions: list[str] | None = None,
    seed_review_summary: dict[str, Any] | None = None,
    admission_summary: dict[str, Any] | None = None,
    seed_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _creation_authorization_result(
        authorization="blocked",
        authorized=False,
        reason=reason,
        detail=detail,
        operator_decision=operator_decision,
        blocked_conditions=blocked_conditions,
        seed_review_summary=seed_review_summary,
        admission_summary=admission_summary,
        seed_summary=seed_summary,
        next_action="resolve_blocked_condition",
    )


def _needs_operator_decision_authorization(
    reason: str,
    detail: str,
    operator_decision: str = "",
    missing_requirements: list[str] | None = None,
    seed_review_summary: dict[str, Any] | None = None,
    admission_summary: dict[str, Any] | None = None,
    seed_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _creation_authorization_result(
        authorization="needs_operator_decision",
        authorized=False,
        reason=reason,
        detail=detail,
        operator_decision=operator_decision,
        missing_requirements=missing_requirements,
        seed_review_summary=seed_review_summary,
        admission_summary=admission_summary,
        seed_summary=seed_summary,
        next_action="request_explicit_operator_case_packet_creation_decision",
    )


def _extract_seed_review_from_authorization_input(authorization_input: dict[str, Any]) -> dict[str, Any] | None:
    if "seed_review_result" in authorization_input:
        seed_review = authorization_input.get("seed_review_result")
        return seed_review if isinstance(seed_review, dict) else None
    if "phase66_seed_review_result" in authorization_input:
        seed_review = authorization_input.get("phase66_seed_review_result")
        return seed_review if isinstance(seed_review, dict) else None
    if "seed_review" in authorization_input and "ready_for_operator_creation_review" in authorization_input:
        return authorization_input
    return None


def _extract_operator_creation_decision(authorization_input: dict[str, Any], seed_review: dict[str, Any] | None) -> str:
    decision_fields = [
        authorization_input.get("operator_case_packet_creation_decision"),
        authorization_input.get("operator_decision"),
        authorization_input.get("creation_decision"),
        authorization_input.get("decision"),
    ]
    if isinstance(seed_review, dict):
        decision_fields.extend(
            [
                seed_review.get("operator_case_packet_creation_decision"),
                seed_review.get("operator_decision"),
            ]
        )
    for value in decision_fields:
        text = _normalize_string(value)
        if text:
            return text
    return ""


def _operator_authorizes_case_packet_creation(decision: str) -> bool:
    normalized = decision.strip().lower().replace("-", "_").replace(" ", "_")
    approved_decisions = {
        "authorize_case_packet_creation",
        "case_packet_creation_authorized",
        "approve_case_packet_creation",
        "approved_case_packet_creation",
        "create_case_packet_authorized",
        "authorize_creation",
        "approved",
        "approve",
        "yes",
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
        "defer",
        "later",
        "change_boundary",
        "different_case_boundary",
        "no",
        "deny",
        "decline",
    }
    return normalized in ambiguous_decisions


def _seed_review_has_forbidden_activity(seed_review: dict[str, Any]) -> list[str]:
    blocked_conditions: list[str] = []
    forbidden_true_fields = {
        "case_packet_created": "seed_review_implies_case_packet_creation",
        "case_packet_persisted": "seed_review_implies_case_packet_persistence",
        "task_created": "seed_review_implies_task_creation",
        "planner_invoked": "seed_review_implies_planner_invocation",
        "mutation_performed": "seed_review_implies_mutation",
        "execution_performed": "seed_review_implies_execution",
        "runtime_executed": "seed_review_implies_runtime_execution",
        "model_executed": "seed_review_implies_model_execution",
        "platform_invoked": "seed_review_implies_platform_execution",
    }
    for field, condition in forbidden_true_fields.items():
        if bool(seed_review.get(field)):
            blocked_conditions.append(condition)
    if _contains_unsupported_execution_request(seed_review):
        blocked_conditions.append("unsupported_execution_or_platform_request")
    return blocked_conditions


def authorize_case_packet_creation_from_seed_review(authorization_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(authorization_input, dict):
        return _needs_operator_decision_authorization(
            reason="Authorization input must be a JSON object.",
            detail="The Phase 67 authorization gate received a non-object input.",
            missing_requirements=["json_object_input"],
        )

    seed_review = _extract_seed_review_from_authorization_input(authorization_input)
    operator_decision = _extract_operator_creation_decision(authorization_input, seed_review)

    if not isinstance(seed_review, dict):
        return _needs_operator_decision_authorization(
            reason="Authorization input lacks a Phase 66 seed-review result.",
            detail="Provide seed_review_result or a direct Phase 66 seed-review result before requesting case-packet creation authorization.",
            operator_decision=operator_decision,
            missing_requirements=["phase66_seed_review_result"],
        )

    admission_summary = seed_review.get("admission_summary") if isinstance(seed_review.get("admission_summary"), dict) else {}
    seed_summary = seed_review.get("seed_summary") if isinstance(seed_review.get("seed_summary"), dict) else {}
    seed_review_summary = {
        "seed_review": seed_review.get("seed_review"),
        "ready_for_operator_creation_review": bool(seed_review.get("ready_for_operator_creation_review", False)),
        "reason": seed_review.get("reason", ""),
        "next_action": seed_review.get("next_action", ""),
    }

    forbidden_conditions = _seed_review_has_forbidden_activity(seed_review)
    if forbidden_conditions:
        return _blocked_creation_authorization(
            reason="Seed-review result implies forbidden activity before authorization.",
            detail="Phase 67 only authorizes a later persistence boundary; it cannot accept prior mutation, task creation, planner invocation, runtime/model execution, or platform behavior.",
            operator_decision=operator_decision,
            blocked_conditions=forbidden_conditions,
            seed_review_summary=seed_review_summary,
            admission_summary=admission_summary,
            seed_summary=seed_summary,
        )

    if _normalize_string(seed_review.get("seed_review")) != "ready_for_operator_creation_review" or not bool(seed_review.get("ready_for_operator_creation_review", False)):
        return _blocked_creation_authorization(
            reason="Only ready Phase 66 seed-review results may reach creation authorization.",
            detail="Phase 67 requires seed_review=ready_for_operator_creation_review and ready_for_operator_creation_review=true.",
            operator_decision=operator_decision,
            blocked_conditions=["phase66_seed_review_not_ready"],
            seed_review_summary=seed_review_summary,
            admission_summary=admission_summary,
            seed_summary=seed_summary,
        )

    missing_requirements: list[str] = []
    if _normalize_string(seed_summary.get("seed_status")) != "candidate_only_not_created":
        missing_requirements.append("seed_status_candidate_only_not_created")
    if _normalize_string(seed_summary.get("creation_status")) != "not_created":
        missing_requirements.append("seed_creation_status_not_created")
    if not _normalize_string(seed_summary.get("objective_text")):
        missing_requirements.append("seed_objective_text")
    if not isinstance(seed_summary.get("provided_artifacts"), list):
        missing_requirements.append("seed_provided_artifacts_list")
    if not _normalize_string(seed_summary.get("operator_decision_required")):
        missing_requirements.append("operator_decision_required")
    if not _normalize_string(seed_summary.get("source_intake_linkage")):
        missing_requirements.append("source_intake_linkage")
    if admission_summary and admission_summary.get("admission") != "admissible":
        missing_requirements.append("phase65_admission_admissible")

    if missing_requirements:
        return _needs_operator_decision_authorization(
            reason="Seed-review result is missing authorization requirements.",
            detail="The reviewed seed is not yet legible enough to authorize case-packet creation.",
            operator_decision=operator_decision,
            missing_requirements=missing_requirements,
            seed_review_summary=seed_review_summary,
            admission_summary=admission_summary,
            seed_summary=seed_summary,
        )

    if not operator_decision:
        return _needs_operator_decision_authorization(
            reason="Explicit operator case-packet creation decision is required.",
            detail="The seed is ready for authorization review, but no explicit creation decision was provided.",
            operator_decision=operator_decision,
            missing_requirements=["operator_case_packet_creation_decision"],
            seed_review_summary=seed_review_summary,
            admission_summary=admission_summary,
            seed_summary=seed_summary,
        )

    if not _operator_authorizes_case_packet_creation(operator_decision):
        if _operator_decision_is_ambiguous_or_deferral(operator_decision):
            return _needs_operator_decision_authorization(
                reason="Operator decision does not explicitly authorize case-packet creation.",
                detail="Phase 67 requires an explicit approval token such as authorize_case_packet_creation.",
                operator_decision=operator_decision,
                missing_requirements=["explicit_operator_creation_authorization"],
                seed_review_summary=seed_review_summary,
                admission_summary=admission_summary,
                seed_summary=seed_summary,
            )
        return _blocked_creation_authorization(
            reason="Operator request is not an allowed case-packet creation authorization decision.",
            detail="The operator decision must not bypass or expand the Phase 67 authorization gate.",
            operator_decision=operator_decision,
            blocked_conditions=["unsupported_operator_creation_decision"],
            seed_review_summary=seed_review_summary,
            admission_summary=admission_summary,
            seed_summary=seed_summary,
        )

    return _creation_authorization_result(
        authorization="creation_authorized",
        authorized=True,
        reason="Reviewed seed is authorized for a later explicit case-packet persistence boundary.",
        detail="Phase 67 recorded authorization only; no case packet, task, planner output, mutation, runtime execution, or model execution was created by this check.",
        operator_decision=operator_decision,
        seed_review_summary=seed_review_summary,
        admission_summary=admission_summary,
        seed_summary=seed_summary,
        next_action="operator_may_choose_explicit_case_packet_persistence_boundary",
    )

def judge_intake(intake_input: dict[str, Any]) -> dict[str, Any]:
    objective_text = _normalize_string(intake_input.get("objective_text"))
    provided_artifacts = _normalize_string_list(intake_input.get("provided_artifacts"))
    confirmed_context = _normalize_context(intake_input.get("confirmed_context"))
    available_capabilities = set(_normalize_string_list(intake_input.get("available_capabilities")))

    if not objective_text:
        return {
            "outcome": "clarify",
            "decomposition_permitted": False,
            "human_explanation": "I need a clear objective before decomposition can begin.",
            "next_action": "request_clarification",
            "clarification_request": {
                "question": "What is the exact objective you want completed?",
                "required_input_kind": "objective_text",
            },
        }

    required_artifacts = _normalize_string_list(confirmed_context.get("required_artifacts"))
    missing_artifacts = [artifact for artifact in required_artifacts if artifact not in set(provided_artifacts)]
    if missing_artifacts:
        return {
            "outcome": "blocked",
            "decomposition_permitted": False,
            "human_explanation": "A required artifact is missing, so decomposition would be dishonest right now.",
            "next_action": "resolve_blocked_condition",
            "blocked_reason": {
                "type": "missing_input",
                "detail": f"Required artifacts missing: {', '.join(missing_artifacts)}",
            },
        }

    required_connector = _normalize_string(confirmed_context.get("required_connector"))
    if required_connector and required_connector not in available_capabilities:
        return {
            "outcome": "blocked",
            "decomposition_permitted": False,
            "human_explanation": "A required connector is unavailable, so decomposition cannot proceed honestly.",
            "next_action": "resolve_blocked_condition",
            "blocked_reason": {
                "type": "missing_connector",
                "detail": f"Required connector unavailable: {required_connector}",
            },
        }

    required_permission = _normalize_string(confirmed_context.get("required_permission"))
    if required_permission and required_permission not in available_capabilities:
        return {
            "outcome": "blocked",
            "decomposition_permitted": False,
            "human_explanation": "A required permission is unavailable, so decomposition cannot proceed honestly.",
            "next_action": "resolve_blocked_condition",
            "blocked_reason": {
                "type": "missing_permission",
                "detail": f"Required permission unavailable: {required_permission}",
            },
        }

    if bool(confirmed_context.get("requires_source_format")) and not _normalize_string(
        confirmed_context.get("source_format")
    ):
        return {
            "outcome": "clarify",
            "decomposition_permitted": False,
            "human_explanation": "The request is actionable, but source form is not specified yet.",
            "next_action": "request_clarification",
            "clarification_request": {
                "question": "What source data form should be used?",
                "required_input_kind": "source_format",
            },
        }

    if bool(confirmed_context.get("requires_output_format")) and not _normalize_string(
        confirmed_context.get("output_format")
    ):
        return {
            "outcome": "clarify",
            "decomposition_permitted": False,
            "human_explanation": "The request is actionable, but output form is not specified yet.",
            "next_action": "request_clarification",
            "clarification_request": {
                "question": "What output format should be produced?",
                "required_input_kind": "output_format",
            },
        }

    return {
        "outcome": "proceed",
        "decomposition_permitted": True,
        "human_explanation": "The objective and confirmed evidence are sufficient to begin bounded decomposition.",
        "next_action": "begin_decomposition",
        "decomposition_handoff": _build_decomposition_handoff(
            objective_text=objective_text,
            provided_artifacts=provided_artifacts,
            confirmed_context=confirmed_context,
        ),
    }
