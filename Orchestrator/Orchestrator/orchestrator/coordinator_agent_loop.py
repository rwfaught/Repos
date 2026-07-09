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
from orchestrator.objective_route_packet_loop import infer_objective_capability_task


LOOP_NON_PROOFS = tuple(dict.fromkeys(ROUTING_NON_PROOFS + (
    "not model-assisted intake execution",
    "not coordinator autonomy",
    "not worker dispatch",
    "not worker task execution",
    "not reviewer semantic evaluation",
    "not retry execution",
    "not operator approval",
    "not packet persistence",
)))

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


def interpret_operator_prompt(prompt: OperatorPrompt) -> IntakeInterpretation:
    """Stub intake interpreter; future local model reasoning plugs in here."""
    inferred = infer_objective_capability_task(prompt.objective)
    capability_task = inferred["capability_task"]
    return IntakeInterpretation(
        prompt_id=prompt.prompt_id,
        objective=prompt.objective,
        interpretation_source=(
            "deterministic_stub_intake_future_local_model_seam"
            if capability_task is not None else "deterministic_stub_intake_insufficient_signals"
        ),
        capability_task=capability_task,
        matched_signals=inferred["matched_signals"],
        confidence=0.75 if capability_task is not None else 0.0,
        clarification_needed=tuple(inferred["clarification_needed"]),
        model_reasoning_seam="replace this function with an owner-controlled model-assisted interpreter",
        model_execution=False,
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


def run_dry_coordinator_loop(prompt: OperatorPrompt | dict[str, Any] | str) -> dict[str, Any]:
    """Run intake, planning, routing, handoff, dry result review, and closeout."""
    operator_prompt = _as_prompt(prompt)
    intake = interpret_operator_prompt(operator_prompt)
    route = create_capability_route(intake)
    plan = create_coordinator_plan(operator_prompt, intake, route)
    handoff = prepare_worker_handoff(plan)
    result = build_dry_worker_result(route, handoff)
    evaluation = evaluate_worker_result(route, result)
    closeout = create_coordinator_closeout(route, evaluation)
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
