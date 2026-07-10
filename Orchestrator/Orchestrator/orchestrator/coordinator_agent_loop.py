"""Dry-run coordinator-agent loop architecture for Orchestrator.

The loop exposes the future model-intake seam while keeping the current
implementation deterministic, typed, inspectable, and non-executing.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from orchestrator.capability_routing_triage import (
    EXPLICIT_NON_PROOFS as ROUTING_NON_PROOFS,
    ROUTES,
    classify_capability_task,
)
from orchestrator.local_model_provider_stub import (
    LocalModelReasoningProvider,
    ProviderInterpretationResult,
)
from orchestrator.local_model_reasoning_contract import (
    REASONING_NON_PROOFS,
    build_local_model_interpretation_request,
    validate_local_model_raw_output,
    validate_local_model_interpretation,
)
from orchestrator.objective_route_packet_loop import (
    build_objective_route_packet,
    infer_objective_capability_task,
)


LOOP_NON_PROOFS = tuple(dict.fromkeys(ROUTING_NON_PROOFS + (
    "not model-assisted intake execution",
    "not coordinator autonomy",
    "not worker dispatch",
    "not worker task execution",
    "not reviewer semantic evaluation",
    "not retry execution",
    "not operator approval",
    "not packet persistence",
) + REASONING_NON_PROOFS))

REVIEW_ACTIONS = (
    "accept",
    "needs_retry",
    "escalate",
    "blocked",
    "needs_operator_clarification",
)

WORKER_TYPES = {
    "deterministic_code_only": "deterministic_local_worker",
    "local_model_candidate": "local_model_worker",
    "frontier_model_or_codex_required": "frontier_codex_worker",
    "external_api_required": "external_api_worker",
    "human_review_or_blocked": "human_review_worker",
}


@dataclass(frozen=True)
class OperatorPrompt:
    prompt_id: str
    objective: str
    requested_outcome: str = ""
    owner_context: str = ""


@dataclass(frozen=True)
class IntakeInterpretation:
    prompt_id: str
    objective: str
    interpretation_source: str
    capability_task: dict[str, Any] | None
    matched_signals: dict[str, list[str]]
    confidence: float
    clarification_needed: tuple[str, ...]
    model_reasoning_seam: str
    model_execution: bool
    reasoning_mode: str = "deterministic_stub"
    reasoning_provider_status: str = "not_requested"
    reasoning_provider_key: str = "none"
    reasoning_validation_status: str = "not_requested"
    reasoning_validation_reasons: tuple[str, ...] = ()
    reasoning_raw_output: str = ""
    reasoning_output_classification: str = "not_available"
    reasoning_normalization_classification: str = "not_attempted"
    reasoning_candidate_json: str = ""
    provider_attempted: bool = False
    reasoning_fallback_status: str = "not_required"
    model_candidate_admitted: bool = False
    authority_quarantined: bool = False
    reasoning_raw_output_reference: str = ""


@dataclass(frozen=True)
class CapabilityRoute:
    route_name: str
    worker_type: str
    rationale: str
    route_is_recommendation: bool
    local_first_posture: bool
    execution_authorized: bool
    blocked_or_deferred_conditions: tuple[str, ...]


@dataclass(frozen=True)
class CoordinatorPlan:
    plan_id: str
    prompt_id: str
    objective: str
    capability_route: CapabilityRoute
    planning_steps: tuple[str, ...]
    approval_gate: str
    worker_type: str
    handoff_authorized: bool
    execution_authorized: bool


@dataclass(frozen=True)
class WorkerHandoff:
    handoff_id: str
    plan_id: str
    worker_type: str
    scope: tuple[str, ...]
    allowed_operations: tuple[str, ...]
    exclusions: tuple[str, ...]
    handoff_status: str
    dispatched: bool
    authorization_required: bool


@dataclass(frozen=True)
class WorkerResult:
    result_id: str
    handoff_id: str
    status: str
    artifact_summary: str
    validation_passed: bool | None
    execution_performed: bool
    error_class: str = ""


@dataclass(frozen=True)
class ReviewEvaluation:
    action: str
    rationale: str
    retry_count: int
    result_accepted: bool
    operator_decision_required: bool


@dataclass(frozen=True)
class CoordinatorCloseout:
    status: str
    operator_message: str
    next_bounded_action: str
    execution_performed: bool
    coordinator_closeout_authorized: bool


def _as_prompt(value: OperatorPrompt | dict[str, Any] | str) -> OperatorPrompt:
    if isinstance(value, OperatorPrompt):
        return value
    if isinstance(value, str):
        return OperatorPrompt(prompt_id="prompt-001", objective=value)
    if isinstance(value, dict):
        return OperatorPrompt(
            prompt_id=str(value.get("prompt_id", "prompt-001")).strip(),
            objective=str(value.get("objective", "")).strip(),
            requested_outcome=str(value.get("requested_outcome", "")).strip(),
            owner_context=str(value.get("owner_context", "")).strip(),
        )
    raise TypeError("operator prompt must be OperatorPrompt, mapping, or string")


def _build_deterministic_intake(
    prompt: OperatorPrompt,
    inferred: dict[str, Any],
    *,
    interpretation_source: str,
    reasoning_mode: str = "deterministic_stub",
    provider_status: str = "not_requested",
    provider_key: str = "none",
    validation_status: str = "not_requested",
    validation_reasons: tuple[str, ...] = (),
    raw_output: str = "",
    output_classification: str = "not_available",
    normalization_classification: str = "not_attempted",
    candidate_json: str = "",
    provider_attempted: bool = False,
    fallback_status: str = "not_required",
    candidate_admitted: bool = False,
    authority_quarantined: bool = False,
    raw_output_reference: str = "",
    model_reasoning_seam: str = "replace this function with an owner-controlled model-assisted interpreter",
) -> IntakeInterpretation:
    capability_task = inferred["capability_task"]
    return IntakeInterpretation(
        prompt_id=prompt.prompt_id,
        objective=prompt.objective,
        interpretation_source=interpretation_source,
        capability_task=capability_task,
        matched_signals=inferred["matched_signals"],
        confidence=0.75 if capability_task is not None else 0.0,
        clarification_needed=tuple(inferred["clarification_needed"]),
        model_reasoning_seam=model_reasoning_seam,
        model_execution=False,
        reasoning_mode=reasoning_mode,
        reasoning_provider_status=provider_status,
        reasoning_provider_key=provider_key,
        reasoning_validation_status=validation_status,
        reasoning_validation_reasons=validation_reasons,
        reasoning_raw_output=raw_output,
        reasoning_output_classification=output_classification,
        reasoning_normalization_classification=normalization_classification,
        reasoning_candidate_json=candidate_json,
        provider_attempted=provider_attempted,
        reasoning_fallback_status=fallback_status,
        model_candidate_admitted=candidate_admitted,
        authority_quarantined=authority_quarantined,
        reasoning_raw_output_reference=raw_output_reference,
    )


def _deterministic_fallback_after_reasoning(
    prompt: OperatorPrompt,
    inferred: dict[str, Any],
    *,
    provider_status: str,
    provider_key: str,
    validation_status: str,
    validation_reasons: tuple[str, ...],
    raw_output: str = "",
    output_classification: str = "not_available",
    normalization_classification: str = "not_attempted",
    candidate_json: str = "",
    provider_attempted: bool = True,
    fallback_status: str = "deterministic_fallback",
    authority_quarantined: bool = False,
    raw_output_reference: str = "",
) -> IntakeInterpretation:
    return _build_deterministic_intake(
        prompt,
        inferred,
        interpretation_source=f"deterministic_stub_fallback_after_{provider_status}",
        reasoning_mode="deterministic_fallback",
        provider_status=provider_status,
        provider_key=provider_key,
        validation_status=validation_status,
        validation_reasons=validation_reasons,
        raw_output=raw_output,
        output_classification=output_classification,
        normalization_classification=normalization_classification,
        candidate_json=candidate_json,
        provider_attempted=provider_attempted,
        fallback_status=fallback_status,
        authority_quarantined=authority_quarantined,
        raw_output_reference=raw_output_reference,
        model_reasoning_seam=(
            "local-model interpretation was unavailable or quarantined; "
            "deterministic intake fallback remains authoritative"
        ),
    )


def interpret_operator_prompt(
    prompt: OperatorPrompt,
    reasoning_provider: LocalModelReasoningProvider | None = None,
) -> IntakeInterpretation:
    """Use validated candidate reasoning when supplied, otherwise deterministic intake."""
    inferred = infer_objective_capability_task(prompt.objective)
    if reasoning_provider is None:
        return _build_deterministic_intake(
            prompt,
            inferred,
            interpretation_source=(
                "deterministic_stub_intake_future_local_model_seam"
                if inferred["capability_task"] is not None else "deterministic_stub_intake_insufficient_signals"
            ),
        )

    request = build_local_model_interpretation_request(
        request_id=prompt.prompt_id,
        objective=prompt.objective,
        requested_outcome=prompt.requested_outcome,
        owner_context=prompt.owner_context,
    )
    provider_key = str(getattr(reasoning_provider, "provider_key", "unknown_provider"))
    try:
        provider_result = reasoning_provider.interpret(request)
    except Exception:
        return _deterministic_fallback_after_reasoning(
            prompt,
            inferred,
            provider_status="provider_exception",
            provider_key=provider_key,
            validation_status="rejected",
            validation_reasons=("provider_call_failed",),
            provider_attempted=True,
        )

    if not isinstance(provider_result, ProviderInterpretationResult):
        return _deterministic_fallback_after_reasoning(
            prompt,
            inferred,
            provider_status="invalid_provider_result",
            provider_key=provider_key,
            validation_status="rejected",
            validation_reasons=("provider_result_shape_invalid",),
            provider_attempted=True,
        )

    provider_status = provider_result.status or "unknown_status"
    provider_key = provider_result.provider_key or provider_key
    raw_output = provider_result.raw_output
    if provider_result.execution_performed:
        return _deterministic_fallback_after_reasoning(
            prompt,
            inferred,
            provider_status=provider_status,
            provider_key=provider_key,
            validation_status="rejected",
            validation_reasons=("provider_execution_flag_must_be_false",),
            raw_output=raw_output or "",
            output_classification="rejected_authority_or_execution_claim" if raw_output is not None else "not_available",
            normalization_classification=(provider_result.normalization_classification
                                          if provider_result.normalization_classification != "not_attempted"
                                          else "not_available"),
            provider_attempted=True,
            raw_output_reference=provider_result.raw_output_reference,
        )
    if raw_output is not None:
        raw_review = getattr(provider_result, "raw_output_validation", None)
        if raw_review is None:
            raw_review = validate_local_model_raw_output(request, raw_output)
        if raw_review.accepted and raw_review.validation and raw_review.validation.interpretation:
            interpretation = raw_review.validation.interpretation
            return IntakeInterpretation(
                prompt_id=prompt.prompt_id,
                objective=prompt.objective,
                interpretation_source="validated_local_model_raw_output",
                capability_task=interpretation.capability_task,
                matched_signals=interpretation.matched_signals,
                confidence=interpretation.confidence,
                clarification_needed=interpretation.clarification_needed,
                model_reasoning_seam=(
                    "validated raw output is candidate intake only; deterministic capability policy remains authoritative"
                ),
                model_execution=False,
                reasoning_mode="validated_model_raw_output",
                reasoning_provider_status=provider_status,
                reasoning_provider_key=provider_key,
                reasoning_validation_status=raw_review.validation.status,
                reasoning_validation_reasons=raw_review.reasons,
                reasoning_raw_output=raw_review.raw_output,
                reasoning_output_classification=raw_review.classification,
                reasoning_normalization_classification=(provider_result.normalization_classification
                                                        if provider_result.normalization_classification != "not_attempted"
                                                        else raw_review.classification),
                reasoning_candidate_json=raw_review.candidate_json or "",
                provider_attempted=True,
                reasoning_fallback_status=provider_result.fallback_status,
                model_candidate_admitted=True,
                authority_quarantined=provider_result.authority_quarantined,
                reasoning_raw_output_reference=provider_result.raw_output_reference,
            )
        validation_status = raw_review.validation.status if raw_review.validation else raw_review.classification
        return _deterministic_fallback_after_reasoning(
            prompt,
            inferred,
            provider_status=provider_status,
            provider_key=provider_key,
            validation_status=validation_status,
            validation_reasons=raw_review.reasons,
            raw_output=raw_review.raw_output,
            output_classification=raw_review.classification,
            normalization_classification=(provider_result.normalization_classification
                                          if provider_result.normalization_classification != "not_attempted"
                                          else raw_review.classification),
            candidate_json=raw_review.candidate_json or "",
            provider_attempted=True,
            fallback_status=provider_result.fallback_status,
            authority_quarantined=provider_result.authority_quarantined,
            raw_output_reference=provider_result.raw_output_reference,
        )
    if provider_result.response is None:
        return _deterministic_fallback_after_reasoning(
            prompt,
            inferred,
            provider_status=provider_status,
            provider_key=provider_key,
            validation_status="not_attempted",
            validation_reasons=("provider_response_unavailable",),
        )

    validation = validate_local_model_interpretation(request, provider_result.response)
    if validation.accepted and validation.interpretation is not None:
        interpretation = validation.interpretation
        return IntakeInterpretation(
            prompt_id=prompt.prompt_id,
            objective=prompt.objective,
            interpretation_source="validated_local_model_stub_response",
            capability_task=interpretation.capability_task,
            matched_signals=interpretation.matched_signals,
            confidence=interpretation.confidence,
            clarification_needed=interpretation.clarification_needed,
            model_reasoning_seam=(
                "validated structured model interpretation is input only; "
                "deterministic capability policy remains authoritative"
            ),
            model_execution=False,
            reasoning_mode="validated_model_stub",
            reasoning_provider_status=provider_status,
            reasoning_provider_key=provider_key,
            reasoning_validation_status=validation.status,
            reasoning_validation_reasons=validation.reasons,
            reasoning_output_classification="structured_payload",
            provider_attempted=True,
            model_candidate_admitted=True,
        )

    return _deterministic_fallback_after_reasoning(
        prompt,
        inferred,
        provider_status=provider_status,
        provider_key=provider_key,
        validation_status=validation.status,
        validation_reasons=validation.reasons,
        output_classification="structured_payload",
        provider_attempted=True,
        fallback_status=provider_result.fallback_status,
        raw_output_reference=provider_result.raw_output_reference,
    )


def create_capability_route(intake: IntakeInterpretation) -> CapabilityRoute:
    if intake.capability_task is None:
        return CapabilityRoute(
            route_name="human_review_or_blocked",
            worker_type=WORKER_TYPES["human_review_or_blocked"],
            rationale="Intake interpretation is insufficient for safe planning.",
            route_is_recommendation=True,
            local_first_posture=True,
            execution_authorized=False,
            blocked_or_deferred_conditions=("intake_interpretation_requires_clarification",),
        )
    recommendation = classify_capability_task(intake.capability_task)
    route = recommendation["route"]
    return CapabilityRoute(
        route_name=route,
        worker_type=WORKER_TYPES[route],
        rationale=recommendation["rationale"],
        route_is_recommendation=True,
        local_first_posture=True,
        execution_authorized=False,
        blocked_or_deferred_conditions=tuple(recommendation["blocked_or_deferred_conditions"]),
    )


def create_coordinator_plan(prompt: OperatorPrompt, intake: IntakeInterpretation, route: CapabilityRoute) -> CoordinatorPlan:
    plan_id = f"plan-{prompt.prompt_id}"
    steps = {
        "deterministic_code_only": ("confirm deterministic inputs", "run bounded local check", "review validation result"),
        "local_model_candidate": ("confirm redaction and review boundary", "prepare local-model attempt", "review draft before use"),
        "frontier_model_or_codex_required": ("define architecture scope", "request explicit frontier/Codex authority", "review proposed implementation"),
        "external_api_required": ("map integration fields", "request separate API boundary", "review no-credentials integration plan"),
        "human_review_or_blocked": ("clarify objective and risk", "owner reviews stop conditions", "do not dispatch execution"),
    }[route.route_name]
    return CoordinatorPlan(
        plan_id=plan_id,
        prompt_id=prompt.prompt_id,
        objective=prompt.objective,
        capability_route=route,
        planning_steps=steps,
        approval_gate="operator_or_owner_approval_required_before_dispatch",
        worker_type=route.worker_type,
        handoff_authorized=False,
        execution_authorized=False,
    )


def prepare_worker_handoff(plan: CoordinatorPlan) -> WorkerHandoff:
    return WorkerHandoff(
        handoff_id=f"handoff-{plan.plan_id}",
        plan_id=plan.plan_id,
        worker_type=plan.worker_type,
        scope=(plan.objective,),
        allowed_operations=("inspect declared objective", "prepare bounded result or recommendation"),
        exclusions=("no provider/model/runtime execution", "no external service calls", "no unapproved mutation"),
        handoff_status="prepared_not_dispatched",
        dispatched=False,
        authorization_required=True,
    )


def build_dry_worker_result(route: CapabilityRoute, handoff: WorkerHandoff) -> WorkerResult:
    if route.route_name == "deterministic_code_only":
        return WorkerResult(
            result_id=f"result-{handoff.handoff_id}",
            handoff_id=handoff.handoff_id,
            status="success",
            artifact_summary="deterministic stub result prepared; no real task executed",
            validation_passed=True,
            execution_performed=False,
        )
    if route.route_name == "human_review_or_blocked":
        return WorkerResult(
            result_id=f"result-{handoff.handoff_id}",
            handoff_id=handoff.handoff_id,
            status="blocked",
            artifact_summary="human-review boundary prepared; no worker dispatched",
            validation_passed=None,
            execution_performed=False,
            error_class="human_review_required",
        )
    return WorkerResult(
        result_id=f"result-{handoff.handoff_id}",
        handoff_id=handoff.handoff_id,
        status="not_executed",
        artifact_summary="dry-run handoff only; downstream worker execution is not authorized",
        validation_passed=None,
        execution_performed=False,
        error_class="execution_boundary_not_authorized",
    )


def evaluate_worker_result(
    route: CapabilityRoute,
    result: WorkerResult,
    *,
    retry_count: int = 0,
) -> ReviewEvaluation:
    if result.status == "blocked" or route.route_name == "human_review_or_blocked":
        return ReviewEvaluation("blocked", "Human review or a blocked intake condition stops downstream work.", retry_count, False, True)
    if result.status in {"clarification_required", "not_executed"}:
        if route.route_name == "local_model_candidate":
            return ReviewEvaluation("needs_operator_clarification", "Local-model work requires owner review and a separate authorized execution boundary.", retry_count, False, True)
        if route.route_name in {"frontier_model_or_codex_required", "external_api_required"}:
            return ReviewEvaluation("escalate", "The recommended downstream boundary is not executable in this dry run.", retry_count, False, True)
        return ReviewEvaluation("needs_operator_clarification", "The result does not establish enough evidence for closeout.", retry_count, False, True)
    if result.status == "success" and result.validation_passed is True and route.route_name == "deterministic_code_only":
        return ReviewEvaluation("accept", "Deterministic stub result passed its bounded validation tripwire.", retry_count, True, False)
    if result.status == "failed" or result.validation_passed is False:
        if retry_count < 1:
            return ReviewEvaluation("needs_retry", "The bounded result failed validation and may receive one reviewed retry recommendation.", retry_count + 1, False, True)
        return ReviewEvaluation("escalate", "The bounded retry allowance is exhausted; coordinator review is required.", retry_count, False, True)
    return ReviewEvaluation("needs_operator_clarification", "Result shape is not sufficient for coordinator closeout.", retry_count, False, True)


def create_coordinator_closeout(route: CapabilityRoute, evaluation: ReviewEvaluation) -> CoordinatorCloseout:
    next_actions = {
        "accept": "operator reviews the accepted deterministic result and decides whether to close the bounded task",
        "needs_retry": "coordinator prepares a bounded retry recommendation; no retry is executed",
        "escalate": "operator reviews the required frontier/API boundary before any escalation",
        "blocked": "operator resolves the human-review blocker or records a stop decision",
        "needs_operator_clarification": "operator clarifies the objective, approval, or execution boundary",
    }
    return CoordinatorCloseout(
        status=evaluation.action,
        operator_message=evaluation.rationale,
        next_bounded_action=next_actions[evaluation.action],
        execution_performed=False,
        coordinator_closeout_authorized=False,
    )


def build_operator_review_packet(
    prompt: OperatorPrompt,
    intake: IntakeInterpretation,
    route: CapabilityRoute,
    plan: CoordinatorPlan,
    handoff: WorkerHandoff,
    result: WorkerResult,
    evaluation: ReviewEvaluation,
    closeout: CoordinatorCloseout,
) -> dict[str, Any]:
    """Assemble a concise operator view without duplicating packet semantics.

    The objective-route packet remains the owner-review and neutral-case data
    surface. This function adds the coordinator's control-flow evidence around
    that packet so the operator can review one bounded readback.
    """
    route_packet = build_objective_route_packet(prompt.objective)
    owner_packet = route_packet.get("owner_review_packet")
    bridge = route_packet.get("neutral_dossier_case_bridge")

    if owner_packet is None:
        safe_local_exploration = (
            "clarify the objective type, risk/privacy posture, and reviewability",
        )
        blocked_or_deferred = list(dict.fromkeys(
            list(route.blocked_or_deferred_conditions)
            + [f"clarification_required_{item}" for item in intake.clarification_needed]
        ))
        neutral_case_relationship = (
            "No neutral dossier/case bridge is created until the objective is clarified."
        )
        structural_readiness = False
    else:
        safe_local_exploration = tuple(owner_packet["deterministic_first"])
        blocked_or_deferred = list(dict.fromkeys(
            list(route.blocked_or_deferred_conditions)
            + list(owner_packet["blocked_or_deferred_conditions"])
        ))
        neutral_case_relationship = bridge["architecture_posture"]
        structural_readiness = bool(
            bridge["neutral_task_readiness"]["structurally_ready_for_domain_specific_work"]
        )

    if route_packet.get("route_readback", {}).get("route") != route.route_name:
        blocked_or_deferred.append("coordinator_route_packet_alignment_requires_review")

    if result.status not in {"success", "blocked"}:
        blocked_or_deferred.append(f"dry_result_status_{result.status}")

    return {
        "packet_name": "coordinator_operator_review_packet",
        "objective": prompt.objective,
        "decision": evaluation.action,
        "rationale": evaluation.rationale,
        "intake_confidence": intake.confidence,
        "reasoning_provider_key": intake.reasoning_provider_key,
        "reasoning_validation_status": intake.reasoning_validation_status,
        "reasoning_validation_reasons": list(intake.reasoning_validation_reasons),
        "reasoning_output_classification": intake.reasoning_output_classification,
        "normalization_classification": intake.reasoning_normalization_classification,
        "raw_output_preserved": bool(intake.reasoning_raw_output),
        "candidate_json_extracted": bool(intake.reasoning_candidate_json),
        "provider_attempted": intake.provider_attempted,
        "raw_output_reference": intake.reasoning_raw_output_reference,
        "fallback_status": intake.reasoning_fallback_status,
        "model_candidate_admitted": intake.model_candidate_admitted,
        "authority_quarantined": intake.authority_quarantined,
        "recommended_route": route.route_name,
        "handoff_status": handoff.handoff_status,
        "dispatched": handoff.dispatched,
        "safe_local_exploration": list(safe_local_exploration),
        "blocked_or_deferred": blocked_or_deferred,
        "owner_approval_gates": [
            plan.approval_gate,
            "worker handoff must remain prepared_not_dispatched",
            "execution authorization must remain false until a separate boundary approves it",
        ],
        "evidence_produced": [
            "operator prompt and deterministic intake interpretation",
            "capability route recommendation",
            "coordinator plan and bounded worker handoff",
            "dry worker result and review evaluation",
            "coordinator closeout",
        ],
        "neutral_dossier_case": {
            "relationship": neutral_case_relationship,
            "bridge_present": bridge is not None,
            "structurally_ready_for_domain_specific_work": structural_readiness,
        },
        "next_bounded_action": closeout.next_bounded_action,
        "execution_authorized": False,
        "execution_performed": False,
        "explicit_non_proofs": list(LOOP_NON_PROOFS),
    }


def run_dry_coordinator_loop(
    prompt: OperatorPrompt | dict[str, Any] | str,
    reasoning_provider: LocalModelReasoningProvider | None = None,
) -> dict[str, Any]:
    """Run intake, planning, routing, handoff, dry result review, and closeout."""
    operator_prompt = _as_prompt(prompt)
    intake = interpret_operator_prompt(operator_prompt, reasoning_provider)
    route = create_capability_route(intake)
    plan = create_coordinator_plan(operator_prompt, intake, route)
    handoff = prepare_worker_handoff(plan)
    result = build_dry_worker_result(route, handoff)
    evaluation = evaluate_worker_result(route, result)
    closeout = create_coordinator_closeout(route, evaluation)
    operator_review = build_operator_review_packet(
        operator_prompt, intake, route, plan, handoff, result, evaluation, closeout
    )
    return {
        "loop_name": "dry_coordinator_agent_loop",
        "operator_prompt": asdict(operator_prompt),
        "intake_interpretation": asdict(intake),
        "capability_route": asdict(route),
        "coordinator_plan": asdict(plan),
        "worker_handoff": asdict(handoff),
        "worker_result": asdict(result),
        "review_evaluation": asdict(evaluation),
        "coordinator_closeout": asdict(closeout),
        "operator_review_packet": operator_review,
        "execution_posture": {
            "model_execution": False,
            "provider_execution": False,
            "runtime_execution": False,
            "worker_dispatch": False,
            "external_service_execution": False,
        },
        "explicit_non_proofs": list(LOOP_NON_PROOFS),
    }


def render_dry_coordinator_loop_markdown(loop: dict[str, Any]) -> str:
    intake = loop["intake_interpretation"]
    route = loop["capability_route"]
    plan = loop["coordinator_plan"]
    handoff = loop["worker_handoff"]
    result = loop["worker_result"]
    review = loop["review_evaluation"]
    closeout = loop["coordinator_closeout"]
    lines = [
        "# Dry Coordinator-Agent Loop Readback",
        "",
        f"Objective: {loop['operator_prompt']['objective'] or '(missing)'}",
        f"Route: `{route['route_name']}`",
        f"Worker type: `{route['worker_type']}`",
        f"Closeout: `{closeout['status']}`",
        "",
        "## Intake Interpretation",
        f"Source: `{intake['interpretation_source']}`",
        f"Reasoning mode: `{intake['reasoning_mode']}`",
        f"Provider status: `{intake['reasoning_provider_status']}`",
        f"Contract validation: `{intake['reasoning_validation_status']}`",
        f"Raw-output classification: `{intake['reasoning_output_classification']}`",
        f"Raw output preserved: `{bool(intake['reasoning_raw_output'])}`",
        f"Confidence: `{intake['confidence']}`",
        f"Future model seam: {intake['model_reasoning_seam']}",
        f"Model execution: `{intake['model_execution']}`",
        "",
        "## Coordinator Plan",
        f"Rationale: {route['rationale']}",
        f"Approval gate: {plan['approval_gate']}",
        *[f"- {step}" for step in plan["planning_steps"]],
        "",
        "## Worker Handoff",
        f"Status: `{handoff['handoff_status']}`",
        f"Dispatched: `{handoff['dispatched']}`",
        *[f"- Exclusion: {item}" for item in handoff["exclusions"]],
        "",
        "## Dry Worker Result",
        f"Status: `{result['status']}`",
        f"Artifact: {result['artifact_summary']}",
        f"Execution performed: `{result['execution_performed']}`",
        "",
        "## Review/Evaluation",
        f"Action: `{review['action']}`",
        f"Rationale: {review['rationale']}",
        "",
        "## Coordinator Closeout",
        closeout["operator_message"],
        f"Next bounded action: {closeout['next_bounded_action']}",
        "",
        "## Explicit Non-Proofs",
        *[f"- {item}" for item in loop["explicit_non_proofs"]],
    ]
    return "\n".join(lines)


def render_operator_review_markdown(loop: dict[str, Any]) -> str:
    """Render the compact PM/operator readback for the coordinator loop."""
    review = loop["operator_review_packet"]
    neutral_case = review["neutral_dossier_case"]
    lines = [
        "# Coordinator Operator Review",
        "",
        f"Objective: {review['objective'] or '(missing)'}",
        f"Decision: `{review['decision']}`",
        f"Recommended route: `{review['recommended_route']}`",
        f"Execution authorized: `{review['execution_authorized']}`",
        "",
        "## Interpretation Boundary",
        f"Mode: `{loop['intake_interpretation']['reasoning_mode']}`",
        f"Provider status: `{loop['intake_interpretation']['reasoning_provider_status']}`",
        f"Provider key: `{review['reasoning_provider_key']}`",
        f"Contract validation: `{loop['intake_interpretation']['reasoning_validation_status']}`",
        f"Raw-output classification: `{review['reasoning_output_classification']}`",
        f"Raw output preserved: `{review['raw_output_preserved']}`",
        f"Candidate JSON extracted: `{review['candidate_json_extracted']}`",
        f"Provider attempted: `{review['provider_attempted']}`",
        f"Fallback status: `{review['fallback_status']}`",
        f"Model candidate admitted: `{review['model_candidate_admitted']}`",
        f"Authority-shaped candidate quarantined: `{review['authority_quarantined']}`",
        f"Validation reasons: {', '.join(review['reasoning_validation_reasons']) or 'none'}",
        "Model interpretation is candidate intake data only; deterministic policy selects the route and no model output authorizes execution.",
        "",
        "## Why",
        review["rationale"],
        f"Intake confidence: `{review['intake_confidence']}`",
        "",
        "## Safe Local Exploration (Planning Only)",
        *[f"- {item}" for item in review["safe_local_exploration"]],
        "",
        "## Owner Approval Gates",
        *[f"- {item}" for item in review["owner_approval_gates"]],
        "",
        "## Blocked or Deferred",
        *[f"- {item}" for item in review["blocked_or_deferred"] or ["none"]],
        "",
        "## Evidence Produced",
        *[f"- {item}" for item in review["evidence_produced"]],
        "",
        "## Neutral Dossier/Case Relationship",
        f"- {neutral_case['relationship']}",
        f"- Bridge present: `{neutral_case['bridge_present']}`",
        f"- Structural readiness: `{neutral_case['structurally_ready_for_domain_specific_work']}`",
        "",
        "## Next Bounded Action",
        review["next_bounded_action"],
        "",
        "## Explicit Non-Proofs",
        *[f"- {item}" for item in review["explicit_non_proofs"]],
    ]
    return "\n".join(lines)
