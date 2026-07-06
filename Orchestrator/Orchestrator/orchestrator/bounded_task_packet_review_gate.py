from __future__ import annotations

from typing import Any

from orchestrator.goal_intake_to_bounded_task_packet import (
    build_goal_intake_to_bounded_task_packet_dict,
)


BOUNDARY = "BOUNDED_TASK_PACKET_REVIEW_GATE_SOURCE_TEST_DOCS"
PACKET_NAME = "bounded_task_packet_review_gate"
RECOMMENDED_NEXT_BOUNDARY = "BOUNDED_TASK_PACKET_REVIEW_GATE_REVIEW_READONLY"

REQUIRED_TASK_PACKET_FIELDS = (
    "packet_id",
    "title",
    "purpose",
    "operator_goal_preserved",
    "files_in_scope",
    "allowed_operations",
    "excluded_operations",
    "success_criteria",
    "operator_approval_required",
    "dispatch_authorized",
)

EXPLICIT_NON_PROOFS = (
    "no runtime/provider/model execution",
    "no live coordinator reasoning proof",
    "no autonomous task dispatch proof",
    "no worker execution proof",
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
    "worker_dispatched": False,
    "task_execution_authorized": False,
    "mutation_authorized": False,
    "local_model_executed": False,
    "frontier_model_executed": False,
    "semantic_correctness_proven": False,
    "production_readiness_claimed": False,
    "phase_387_implemented": False,
    "first_product_wedge_selected": False,
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [text for text in (_normalize_text(item) for item in value) if text]


def _missing_task_packet_fields(task_packet: Any) -> list[str]:
    if not isinstance(task_packet, dict):
        return list(REQUIRED_TASK_PACKET_FIELDS)
    missing: list[str] = []
    for field in REQUIRED_TASK_PACKET_FIELDS:
        value = task_packet.get(field)
        if isinstance(value, bool):
            continue
        if isinstance(value, (list, tuple)):
            if not _text_list(value):
                missing.append(field)
            continue
        if not _normalize_text(value):
            missing.append(field)
    return missing


def _review_decision(goal_packet: dict[str, Any]) -> tuple[str, list[str], list[str], str]:
    status = _normalize_text(goal_packet.get("intake_status"))
    task_packet = goal_packet.get("next_bounded_task_packet")

    if status == "needs_operator_clarification":
        return (
            "blocked_for_operator_clarification",
            ["intake_requires_operator_clarification"],
            list(goal_packet.get("missing_inputs", ())),
            "Ask Roger the visible clarification questions before drafting or dispatching work.",
        )

    missing = _missing_task_packet_fields(task_packet)
    if missing:
        return (
            "needs_packet_repair",
            ["bounded_task_packet_missing_required_fields"],
            missing,
            "Repair the bounded task packet before asking Roger to approve it.",
        )

    if task_packet.get("dispatch_authorized") is not False:
        return (
            "needs_packet_repair",
            ["dispatch_authorization_must_remain_false_before_operator_approval"],
            ["dispatch_authorized_false"],
            "Remove implied dispatch authority before review.",
        )

    if task_packet.get("operator_approval_required") is not True:
        return (
            "needs_packet_repair",
            ["operator_approval_required_flag_missing"],
            ["operator_approval_required_true"],
            "Require Roger approval before any mutation or worker execution.",
        )

    if not _text_list(task_packet.get("excluded_operations")):
        return (
            "needs_packet_repair",
            ["excluded_operations_required"],
            ["excluded_operations"],
            "Name excluded operations so the worker packet cannot silently broaden.",
        )

    return (
        "ready_for_roger_approval",
        [],
        [],
        "Packet is structurally ready for Roger review, but no execution is authorized.",
    )


def build_bounded_task_packet_review_gate_dict(
    goal_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_packet = goal_packet or build_goal_intake_to_bounded_task_packet_dict()
    decision, blocked_conditions, missing_requirements, recommended_action = _review_decision(source_packet)
    task_packet = source_packet.get("next_bounded_task_packet")
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": (
            "Review the next bounded task packet produced by goal intake and decide "
            "whether it is ready for Roger approval, needs repair, or must stay "
            "blocked for clarification."
        ),
        "source_goal_id": _normalize_text(source_packet.get("goal_id")),
        "source_intake_status": _normalize_text(source_packet.get("intake_status")),
        "review_decision": decision,
        "blocked_conditions": blocked_conditions,
        "missing_requirements": missing_requirements,
        "recommended_action": recommended_action,
        "roger_approval_surface": {
            "question": "Does Roger approve this bounded task packet for the next explicit boundary?",
            "allowed_answers": (
                "approve_next_boundary",
                "request_packet_repair",
                "answer_clarification_questions",
                "stop_or_reframe_goal",
            ),
            "approval_required_before_dispatch": True,
        },
        "task_packet_summary": (
            {
                "packet_id": _normalize_text(task_packet.get("packet_id")),
                "title": _normalize_text(task_packet.get("title")),
                "purpose": _normalize_text(task_packet.get("purpose")),
                "files_in_scope": _text_list(task_packet.get("files_in_scope")),
                "allowed_operations": _text_list(task_packet.get("allowed_operations")),
                "excluded_operations": _text_list(task_packet.get("excluded_operations")),
                "success_criteria": _text_list(task_packet.get("success_criteria")),
                "operator_approval_required": task_packet.get("operator_approval_required") is True,
                "dispatch_authorized": task_packet.get("dispatch_authorized") is True,
            }
            if isinstance(task_packet, dict)
            else {}
        ),
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def _render_bullets(items: list[Any]) -> list[str]:
    return [f"- {item}" for item in items]


def render_bounded_task_packet_review_gate_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = packet or build_bounded_task_packet_review_gate_dict()
    summary = payload["task_packet_summary"]
    approval = payload["roger_approval_surface"]
    sections = [
        "# Bounded Task Packet Review Gate",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Packet: `{payload['packet_name']}`",
        f"Purpose: {payload['purpose']}",
        "",
        "## Source Intake",
        f"- Source goal id: {payload['source_goal_id']}",
        f"- Source intake status: {payload['source_intake_status']}",
        "",
        "## Review Decision",
        f"- Decision: {payload['review_decision']}",
        f"- Recommended action: {payload['recommended_action']}",
        "",
        "## Blocked Conditions",
        *_render_bullets(payload["blocked_conditions"]),
        "",
        "## Missing Requirements",
        *_render_bullets(payload["missing_requirements"]),
        "",
        "## Roger Approval Surface",
        f"- Question: {approval['question']}",
        f"- Approval required before dispatch: {approval['approval_required_before_dispatch']}",
        *_render_bullets(list(approval["allowed_answers"])),
        "",
        "## Task Packet Summary",
    ]
    if not summary:
        sections.append("- No task packet is present.")
    else:
        sections.extend(
            (
                f"- Packet id: {summary['packet_id']}",
                f"- Title: {summary['title']}",
                f"- Purpose: {summary['purpose']}",
                f"- Operator approval required: {summary['operator_approval_required']}",
                f"- Dispatch authorized: {summary['dispatch_authorized']}",
                "### Files In Scope",
                *_render_bullets(summary["files_in_scope"]),
                "### Allowed Operations",
                *_render_bullets(summary["allowed_operations"]),
                "### Excluded Operations",
                *_render_bullets(summary["excluded_operations"]),
                "### Success Criteria",
                *_render_bullets(summary["success_criteria"]),
            )
        )
    sections.extend(
        (
            "",
            "## Explicit Non-Proofs",
            *_render_bullets(payload["explicit_non_proofs"]),
            "",
            "## Posture",
            f"- runtime_required={payload['runtime_required']}",
            f"- provider_model_required={payload['provider_model_required']}",
            f"- worker_dispatched={payload['worker_dispatched']}",
            f"- task_execution_authorized={payload['task_execution_authorized']}",
            f"- mutation_authorized={payload['mutation_authorized']}",
            f"- first_product_wedge_selected={payload['first_product_wedge_selected']}",
            f"- phase_387_implemented={payload['phase_387_implemented']}",
            f"- recommended_next_boundary={payload['recommended_next_boundary']}",
        )
    )
    return "\n".join(sections)
