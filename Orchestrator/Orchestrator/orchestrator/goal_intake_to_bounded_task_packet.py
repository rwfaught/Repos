from __future__ import annotations

from typing import Any


BOUNDARY = "GOAL_INTAKE_TO_BOUNDED_TASK_PACKET_VERTICAL_SLICE_SOURCE_TEST_DOCS"
PACKET_NAME = "goal_intake_to_bounded_task_packet_vertical_slice"
RECOMMENDED_NEXT_BOUNDARY = "GOAL_INTAKE_TO_BOUNDED_TASK_PACKET_VERTICAL_SLICE_REVIEW_READONLY"

EXPLICIT_NON_PROOFS = (
    "no runtime/provider/model execution",
    "no live coordinator reasoning proof",
    "no autonomous task dispatch proof",
    "no local model capability proof",
    "no frontier model escalation proof",
    "no semantic correctness proof",
    "no production readiness proof",
    "no file mutation proof",
    "no Phase 387 implementation",
    "no first product wedge selection",
)

FALSE_FLAGS = {
    "runtime_required": False,
    "provider_model_required": False,
    "live_coordinator_reasoning_claimed": False,
    "autonomous_decomposition_claimed": False,
    "task_dispatched": False,
    "mutation_authorized": False,
    "local_model_executed": False,
    "frontier_model_executed": False,
    "semantic_correctness_proven": False,
    "production_readiness_claimed": False,
    "phase_387_implemented": False,
    "first_product_wedge_selected": False,
}

DOGWALKING_APP_GOAL: dict[str, Any] = {
    "goal_id": "roger_example_local_dogwalking_app",
    "operator_goal": (
        "Build a simple local dogwalking gig work app that connects someone who "
        "needs a dog walker for one day with an available walker."
    ),
    "goal_kind": "app_build",
    "known_context": (
        "This is a simple example app idea, not a selected product wedge.",
        "Roger wants Orchestrator to decide what information is missing and propose a bounded first step.",
    ),
    "missing_inputs": (
        "target platform",
        "user roles and trust requirements",
        "payment and liability posture",
        "geographic scope",
        "minimum viable workflow",
    ),
    "risk_flags": (
        "market/product uncertainty",
        "trust and safety",
        "payments or identity verification would need later approval",
    ),
    "desired_outcome": "reviewable first planning packet",
    "allowed_next_step": "draft_compact_product_brief_and_first_slice_plan",
}

PKMS_REORGANIZATION_GOAL: dict[str, Any] = {
    "goal_id": "roger_example_pkms_frontmatter_reorganization",
    "operator_goal": (
        "Reorganize my PKMS by analyzing front matter in every note and generating "
        "consistently formatted notes across the entire thing."
    ),
    "goal_kind": "local_knowledge_base_reorganization",
    "known_context": (
        "The request may require reading and mutating many local notes.",
        "The exact note directory, schema, backup posture, and mutation authority are not provided.",
    ),
    "missing_inputs": (
        "PKMS root path",
        "current front matter schema",
        "desired schema",
        "backup or dry-run requirement",
        "allowed mutation scope",
    ),
    "risk_flags": (
        "large local document read",
        "bulk file mutation",
        "potential data loss without backup and dry-run review",
    ),
    "desired_outcome": "",
    "allowed_next_step": "",
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _tuple_of_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(text for text in (_normalize_text(item) for item in value) if text)


def _coerce_goal(goal_request: dict[str, Any] | None) -> dict[str, Any]:
    source = goal_request or DOGWALKING_APP_GOAL
    return {
        "goal_id": _normalize_text(source.get("goal_id")) or "operator_goal",
        "operator_goal": _normalize_text(source.get("operator_goal")),
        "goal_kind": _normalize_text(source.get("goal_kind")) or "unspecified",
        "known_context": _tuple_of_text(source.get("known_context")),
        "missing_inputs": _tuple_of_text(source.get("missing_inputs")),
        "risk_flags": _tuple_of_text(source.get("risk_flags")),
        "desired_outcome": _normalize_text(source.get("desired_outcome")),
        "allowed_next_step": _normalize_text(source.get("allowed_next_step")),
    }


def _clarification_questions(goal: dict[str, Any]) -> tuple[str, ...]:
    questions = [
        f"What does success look like for {goal['goal_id']}?",
        "What sources, files, apps, or systems may Orchestrator inspect?",
        "What changes are allowed, and should the first pass be read-only?",
    ]
    for missing in goal["missing_inputs"]:
        questions.append(f"Please specify: {missing}.")
    return tuple(questions)


def _intake_status(goal: dict[str, Any]) -> str:
    if not goal["operator_goal"]:
        return "needs_operator_clarification"
    if not goal["desired_outcome"] or not goal["allowed_next_step"]:
        return "needs_operator_clarification"
    if any("bulk file mutation" in risk for risk in goal["risk_flags"]):
        return "needs_operator_clarification"
    return "candidate_task_packet_ready_for_operator_review"


def _route_posture(goal: dict[str, Any], status: str) -> dict[str, Any]:
    if status == "needs_operator_clarification":
        return {
            "recommended_route": "ask_operator_clarifying_questions",
            "local_first_posture": "do_not_dispatch_until_scope_and_authority_are_clear",
            "frontier_escalation_posture": "available_later_for_big_picture_decomposition_if_authorized",
            "reason": "The request is still missing scope, authority, or safe first-step definition.",
            "execution_allowed": False,
        }
    return {
        "recommended_route": "human_reviewed_bounded_worker_packet",
        "local_first_posture": (
            "prefer a local or low-cost worker for the first deterministic planning packet "
            "after operator approval"
        ),
        "frontier_escalation_posture": (
            "reserve frontier coordinator review for ambiguous product judgment, cross-domain "
            "planning, or failed local-worker output"
        ),
        "reason": f"The goal can be reduced to {goal['allowed_next_step']} without executing production work.",
        "execution_allowed": False,
    }


def _bounded_task_packet(goal: dict[str, Any], status: str) -> dict[str, Any] | None:
    if status != "candidate_task_packet_ready_for_operator_review":
        return None
    return {
        "packet_id": f"{goal['goal_id']}_first_bounded_packet",
        "title": "Draft compact product brief and first vertical slice plan",
        "purpose": (
            "Turn the broad operator goal into a small reviewable planning artifact before "
            "any app implementation, runtime execution, provider call, or file mutation."
        ),
        "operator_goal_preserved": goal["operator_goal"],
        "files_in_scope": (
            "no file mutation",
            "operator-approved planning context only",
        ),
        "allowed_operations": (
            "inspect only operator-approved context",
            "draft problem statement",
            "draft user roles",
            "draft smallest useful workflow",
            "list missing decisions",
            "recommend next implementation boundary for operator review",
        ),
        "excluded_operations": (
            "no code implementation",
            "no production deployment",
            "no payments, identity, or live user workflow",
            "no provider/model/runtime execution",
            "no product wedge selection",
        ),
        "success_criteria": (
            "Roger can tell what went in, what Orchestrator did, and what came out.",
            "The packet names missing decisions instead of hiding them.",
            "The packet produces a next boundary that still requires operator approval.",
        ),
        "operator_approval_required": True,
        "dispatch_authorized": False,
    }


def build_goal_intake_to_bounded_task_packet_dict(
    goal_request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    goal = _coerce_goal(goal_request)
    status = _intake_status(goal)
    route = _route_posture(goal, status)
    task_packet = _bounded_task_packet(goal, status)
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": (
            "Demonstrate the smallest honest Orchestrator loop from broad operator goal "
            "to intake judgment, route posture, clarification needs, and a reviewable "
            "next bounded task packet."
        ),
        "operator_goal": goal["operator_goal"],
        "goal_id": goal["goal_id"],
        "goal_kind": goal["goal_kind"],
        "known_context": list(goal["known_context"]),
        "missing_inputs": list(goal["missing_inputs"]),
        "risk_flags": list(goal["risk_flags"]),
        "intake_status": status,
        "clarification_questions": list(_clarification_questions(goal)),
        "route_posture": route,
        "next_bounded_task_packet": task_packet,
        "review_posture": {
            "roger_can_judge": (
                "whether the goal was preserved",
                "whether the missing inputs are real",
                "whether the proposed first task is small enough",
                "whether local-first routing is appropriate",
                "whether frontier escalation should be authorized later",
            ),
            "operator_approval_required_before_mutation": True,
            "coordinator_review_required_before_dispatch": True,
        },
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def _render_bullets(items: list[Any]) -> list[str]:
    return [f"- {item}" for item in items]


def render_goal_intake_to_bounded_task_packet_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = packet or build_goal_intake_to_bounded_task_packet_dict()
    route = payload["route_posture"]
    task_packet = payload["next_bounded_task_packet"]
    sections = [
        "# Goal Intake To Bounded Task Packet Vertical Slice",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Packet: `{payload['packet_name']}`",
        f"Purpose: {payload['purpose']}",
        "",
        "## What Went In",
        f"- Goal id: {payload['goal_id']}",
        f"- Goal kind: {payload['goal_kind']}",
        f"- Operator goal: {payload['operator_goal']}",
        "",
        "## What Orchestrator Did",
        f"- Intake status: {payload['intake_status']}",
        f"- Recommended route: {route['recommended_route']}",
        f"- Local-first posture: {route['local_first_posture']}",
        f"- Frontier escalation posture: {route['frontier_escalation_posture']}",
        f"- Execution allowed: {route['execution_allowed']}",
        "",
        "## Missing Inputs",
        *_render_bullets(payload["missing_inputs"]),
        "",
        "## Clarification Questions",
        *_render_bullets(payload["clarification_questions"]),
        "",
        "## What Came Out",
    ]
    if task_packet is None:
        sections.extend(("- No bounded task packet was produced because clarification is required.",))
    else:
        sections.extend(
            (
                f"- Packet id: {task_packet['packet_id']}",
                f"- Title: {task_packet['title']}",
                f"- Purpose: {task_packet['purpose']}",
                f"- Dispatch authorized: {task_packet['dispatch_authorized']}",
                "### Success Criteria",
                *_render_bullets(list(task_packet["success_criteria"])),
            )
        )
    review = payload["review_posture"]
    sections.extend(
        (
            "",
            "## What Roger Can Judge",
            *_render_bullets(list(review["roger_can_judge"])),
            "",
            "## Explicit Non-Proofs",
            *_render_bullets(payload["explicit_non_proofs"]),
            "",
            "## Posture",
            f"- runtime_required={payload['runtime_required']}",
            f"- provider_model_required={payload['provider_model_required']}",
            f"- task_dispatched={payload['task_dispatched']}",
            f"- mutation_authorized={payload['mutation_authorized']}",
            f"- local_model_executed={payload['local_model_executed']}",
            f"- frontier_model_executed={payload['frontier_model_executed']}",
            f"- first_product_wedge_selected={payload['first_product_wedge_selected']}",
            f"- phase_387_implemented={payload['phase_387_implemented']}",
            f"- recommended_next_boundary={payload['recommended_next_boundary']}",
        )
    )
    return "\n".join(sections)
