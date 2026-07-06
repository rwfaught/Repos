from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.bounded_task_packet_review_gate import (
    build_bounded_task_packet_review_gate_dict,
)
from orchestrator.task_schema import REPORT_ONLY_EXECUTION_POLICY, Task, serialize_task


BOUNDARY = "APPROVED_BOUNDED_TASK_PACKET_TO_QUEUED_TASK_SOURCE_TEST_DOCS"
PACKET_NAME = "approved_bounded_task_packet_to_queued_task"
RECOMMENDED_NEXT_BOUNDARY = "QUEUED_TASK_EXECUTION_AUTHORIZATION_REVIEW_READONLY"

EXPLICIT_NON_PROOFS = (
    "no runtime/provider/model execution",
    "no live coordinator reasoning proof",
    "no autonomous task dispatch proof",
    "no worker execution proof",
    "no local model capability proof",
    "no frontier model escalation proof",
    "no semantic correctness proof",
    "no production readiness proof",
    "no file mutation execution proof",
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


def _machine_token(value: Any) -> str:
    text = _normalize_text(value).lower()
    token = re.sub(r"[^a-z0-9._-]+", "_", text).strip("_")
    return token or "operator_goal"


def _blocked_result(
    *,
    review_gate: dict[str, Any] | None,
    reason: str,
    blocked_conditions: list[str],
    missing_requirements: list[str] | None = None,
) -> dict[str, Any]:
    review = review_gate if isinstance(review_gate, dict) else {}
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "task_creation_status": "blocked",
        "task_created": False,
        "task_persisted": False,
        "task_id": "",
        "task_path": "",
        "source_goal_id": _normalize_text(review.get("source_goal_id")),
        "source_review_decision": _normalize_text(review.get("review_decision")),
        "reason": reason,
        "blocked_conditions": sorted(set(blocked_conditions)),
        "missing_requirements": sorted(set(missing_requirements or [])),
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def _approval_conditions(operator_approval: dict[str, Any] | None) -> tuple[list[str], list[str]]:
    if not isinstance(operator_approval, dict):
        return ["operator_approval_record_required"], ["operator_approval"]

    blocked: list[str] = []
    missing: list[str] = []
    if _normalize_text(operator_approval.get("decision")) != "approve_next_boundary":
        blocked.append("operator_decision_does_not_approve_next_boundary")
    if operator_approval.get("roger_approved") is not True:
        blocked.append("roger_approved_boolean_required")
    if not _normalize_text(operator_approval.get("approval_note")):
        missing.append("approval_note")
    return blocked, missing


def _task_from_review_gate(
    review_gate: dict[str, Any],
    operator_approval: dict[str, Any],
) -> Task:
    summary = review_gate["task_packet_summary"]
    source_goal_id = _machine_token(review_gate.get("source_goal_id"))
    task_id = f"task_{source_goal_id}_first_bounded_packet"
    title = _normalize_text(summary.get("title")) or "Approved bounded task packet"
    expected_output = _normalize_text(summary.get("purpose")) or "Complete the approved bounded task packet."
    return Task(
        id=task_id,
        run_id=f"run_{source_goal_id}",
        title=title,
        role="worker",
        status="queued",
        dependencies=[],
        success_criteria=_text_list(summary.get("success_criteria")),
        files_in_scope=_text_list(summary.get("files_in_scope")),
        retry_count=0,
        expected_output=expected_output,
        source_task_id=None,
        source_artifact_id=_normalize_text(review_gate.get("boundary")),
        execution_artifact_id=None,
        review_reason=(
            "Created from Roger-approved bounded task packet review gate; "
            "task creation only, not execution authorization."
        ),
        recommendation_type="approved_bounded_task_packet",
        recommendation_reason=_normalize_text(operator_approval.get("approval_note")),
        recommendation_identity="roger_approved_next_boundary_task_creation",
        recommendation_confirmed=True,
        recommendation_confirmed_at=_normalize_text(operator_approval.get("approved_at")) or None,
        verification_checks=None,
        requires_causal_change=False,
        execution_policy=REPORT_ONLY_EXECUTION_POLICY,
        execution_delegation_status="queued_waiting_for_explicit_execution_boundary",
        source_case_packet_identity=None,
        execution_authorization_provenance={
            "task_creation_only": True,
            "execution_authorized": False,
            "operator_decision": _normalize_text(operator_approval.get("decision")),
            "review_boundary": _normalize_text(review_gate.get("boundary")),
        },
    )


def create_queued_task_from_approved_bounded_packet(
    review_gate: dict[str, Any] | None = None,
    operator_approval: dict[str, Any] | None = None,
    task_store_dir: str | Path | None = None,
) -> dict[str, Any]:
    review = review_gate or build_bounded_task_packet_review_gate_dict()
    if _normalize_text(review.get("review_decision")) != "ready_for_roger_approval":
        return _blocked_result(
            review_gate=review,
            reason="Review gate is not ready for Roger approval.",
            blocked_conditions=["review_gate_not_ready_for_task_creation"],
            missing_requirements=list(review.get("missing_requirements", ())),
        )

    approval_blocked, approval_missing = _approval_conditions(operator_approval)
    if approval_blocked or approval_missing:
        return _blocked_result(
            review_gate=review,
            reason="Explicit Roger approval is required before task creation.",
            blocked_conditions=approval_blocked,
            missing_requirements=approval_missing,
        )

    if task_store_dir is None:
        return _blocked_result(
            review_gate=review,
            reason="Caller-supplied task_store_dir is required for persistence.",
            blocked_conditions=["task_store_dir_required"],
            missing_requirements=["task_store_dir"],
        )

    task = _task_from_review_gate(review, operator_approval or {})
    task_dir = Path(task_store_dir)
    task_path = task_dir / f"{task.id}.json"
    if task_path.exists():
        return _blocked_result(
            review_gate=review,
            reason="Queued task record already exists.",
            blocked_conditions=["queued_task_record_already_exists"],
            missing_requirements=[str(task_path)],
        )

    task_dir.mkdir(parents=True, exist_ok=True)
    task_payload = serialize_task(task)
    task_path.write_text(json.dumps(task_payload, indent=2), encoding="utf-8")

    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "task_creation_status": "created",
        "task_created": True,
        "task_persisted": True,
        "task_id": task.id,
        "task_path": str(task_path),
        "source_goal_id": _normalize_text(review.get("source_goal_id")),
        "source_review_decision": _normalize_text(review.get("review_decision")),
        "reason": "Created one queued report-only task from explicit Roger approval.",
        "blocked_conditions": [],
        "missing_requirements": [],
        "queued_task_record": task_payload,
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def render_approved_bounded_task_to_queued_task_markdown(
    result: dict[str, Any] | None = None,
) -> str:
    payload = result or create_queued_task_from_approved_bounded_packet()
    lines = [
        "# Approved Bounded Task Packet To Queued Task",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Packet: `{payload['packet_name']}`",
        "",
        "## Task Creation Status",
        f"- Status: {payload['task_creation_status']}",
        f"- Task created: {payload['task_created']}",
        f"- Task persisted: {payload['task_persisted']}",
        f"- Task id: {payload['task_id']}",
        f"- Task path: {payload['task_path']}",
        f"- Reason: {payload['reason']}",
        "",
        "## Blocked Conditions",
        *[f"- {item}" for item in payload["blocked_conditions"]],
        "",
        "## Missing Requirements",
        *[f"- {item}" for item in payload["missing_requirements"]],
        "",
        "## Explicit Non-Proofs",
        *[f"- {item}" for item in payload["explicit_non_proofs"]],
        "",
        "## Posture",
        f"- worker_dispatched={payload['worker_dispatched']}",
        f"- task_execution_authorized={payload['task_execution_authorized']}",
        f"- mutation_authorized={payload['mutation_authorized']}",
        f"- runtime_required={payload['runtime_required']}",
        f"- provider_model_required={payload['provider_model_required']}",
        f"- recommended_next_boundary={payload['recommended_next_boundary']}",
    ]
    return "\n".join(lines)
