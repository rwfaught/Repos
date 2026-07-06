from __future__ import annotations

from typing import Any

from orchestrator.approved_bounded_task_packet_to_queued_task import (
    create_queued_task_from_approved_bounded_packet,
)
from orchestrator.task_schema import REPORT_ONLY_EXECUTION_POLICY


BOUNDARY = "QUEUED_TASK_EXECUTION_AUTHORIZATION_REVIEW_SOURCE_TEST_DOCS"
PACKET_NAME = "queued_task_execution_authorization_review"
RECOMMENDED_NEXT_BOUNDARY = "REPORT_ONLY_WORKER_EXECUTION_DRY_RUN_BOUNDARY_SOURCE_TEST_DOCS"

EXPECTED_DELEGATION_STATUS = "queued_waiting_for_explicit_execution_boundary"

BROAD_FILE_SCOPE_TOKENS = {
    "",
    ".",
    "*",
    "**/*",
    "repo",
    "repository",
    "entire repo",
    "whole repo",
    "all files",
}

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
    "task_executed": False,
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


def _queued_task_record(source: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(source, dict):
        return {}
    direct = source.get("queued_task_record")
    if isinstance(direct, dict):
        return dict(direct)
    if source.get("status") or source.get("id"):
        return dict(source)
    return {}


def _has_broad_file_scope(files_in_scope: list[str]) -> bool:
    if not files_in_scope:
        return True
    for item in files_in_scope:
        if item.lower().strip() in BROAD_FILE_SCOPE_TOKENS:
            return True
    return False


def _review_task_record(task: dict[str, Any]) -> tuple[str, list[str], list[str], str]:
    blocked: list[str] = []
    missing: list[str] = []

    required_text_fields = (
        "id",
        "run_id",
        "title",
        "role",
        "status",
        "expected_output",
        "execution_policy",
        "execution_delegation_status",
    )
    for field in required_text_fields:
        if not _normalize_text(task.get(field)):
            missing.append(field)

    for field in ("success_criteria", "files_in_scope"):
        if not _text_list(task.get(field)):
            missing.append(field)

    if missing:
        blocked.append("queued_task_record_missing_required_fields")

    if _normalize_text(task.get("status")) != "queued":
        blocked.append("task_status_not_queued")
    if _normalize_text(task.get("role")) != "worker":
        blocked.append("task_role_not_worker")
    if _normalize_text(task.get("execution_policy")) != REPORT_ONLY_EXECUTION_POLICY:
        blocked.append("only_report_only_tasks_are_eligible_for_this_review")
    if _normalize_text(task.get("execution_delegation_status")) != EXPECTED_DELEGATION_STATUS:
        blocked.append("task_not_waiting_for_explicit_execution_boundary")
    if _normalize_text(task.get("execution_artifact_id")):
        blocked.append("task_already_has_execution_artifact")
    if task.get("requires_causal_change") is True:
        blocked.append("task_requires_causal_change")
    if _has_broad_file_scope(_text_list(task.get("files_in_scope"))):
        blocked.append("task_file_scope_broad_or_missing")

    provenance = task.get("execution_authorization_provenance")
    if not isinstance(provenance, dict):
        missing.append("execution_authorization_provenance")
        blocked.append("queued_task_record_missing_required_fields")
    elif provenance.get("execution_authorized") is not False:
        blocked.append("prior_execution_authorization_must_be_false")

    if blocked:
        return (
            "blocked_before_execution_authorization_review",
            sorted(set(blocked)),
            sorted(set(missing)),
            "Repair or reframe the queued task before any execution authorization review.",
        )

    return (
        "ready_for_operator_execution_authorization_review",
        [],
        [],
        "Queued task is structurally ready for a separate operator execution-authorization boundary.",
    )


def build_queued_task_execution_authorization_review_dict(
    task_creation_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = task_creation_result or create_queued_task_from_approved_bounded_packet()
    task = _queued_task_record(source)
    decision, blocked_conditions, missing_requirements, recommended_action = _review_task_record(task)
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": (
            "Review a queued task record to decide whether it is structurally ready "
            "for a future explicit execution-authorization boundary."
        ),
        "source_task_creation_status": _normalize_text(source.get("task_creation_status"))
        if isinstance(source, dict)
        else "",
        "task_id": _normalize_text(task.get("id")),
        "run_id": _normalize_text(task.get("run_id")),
        "review_decision": decision,
        "blocked_conditions": blocked_conditions,
        "missing_requirements": missing_requirements,
        "recommended_action": recommended_action,
        "operator_execution_authorization_surface": {
            "question": "Does Roger authorize a separate report-only worker execution boundary for this queued task?",
            "allowed_answers": (
                "authorize_report_only_execution_boundary",
                "request_task_record_repair",
                "keep_task_queued",
                "stop_or_reframe_goal",
            ),
            "execution_authorization_required_before_dispatch": True,
        },
        "task_summary": {
            "id": _normalize_text(task.get("id")),
            "title": _normalize_text(task.get("title")),
            "role": _normalize_text(task.get("role")),
            "status": _normalize_text(task.get("status")),
            "execution_policy": _normalize_text(task.get("execution_policy")),
            "execution_delegation_status": _normalize_text(task.get("execution_delegation_status")),
            "files_in_scope": _text_list(task.get("files_in_scope")),
            "success_criteria": _text_list(task.get("success_criteria")),
            "expected_output": _normalize_text(task.get("expected_output")),
            "execution_artifact_id": _normalize_text(task.get("execution_artifact_id")),
            "requires_causal_change": task.get("requires_causal_change") is True,
        },
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def _render_bullets(items: list[Any]) -> list[str]:
    return [f"- {item}" for item in items]


def render_queued_task_execution_authorization_review_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = packet or build_queued_task_execution_authorization_review_dict()
    task = payload["task_summary"]
    surface = payload["operator_execution_authorization_surface"]
    lines = [
        "# Queued Task Execution Authorization Review",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Packet: `{payload['packet_name']}`",
        f"Purpose: {payload['purpose']}",
        "",
        "## Review Decision",
        f"- Decision: {payload['review_decision']}",
        f"- Recommended action: {payload['recommended_action']}",
        "",
        "## Task Summary",
        f"- Task id: {task['id']}",
        f"- Run id: {payload['run_id']}",
        f"- Title: {task['title']}",
        f"- Role: {task['role']}",
        f"- Status: {task['status']}",
        f"- Execution policy: {task['execution_policy']}",
        f"- Execution delegation status: {task['execution_delegation_status']}",
        f"- Execution artifact id: {task['execution_artifact_id']}",
        f"- Requires causal change: {task['requires_causal_change']}",
        "",
        "## Files In Scope",
        *_render_bullets(task["files_in_scope"]),
        "",
        "## Success Criteria",
        *_render_bullets(task["success_criteria"]),
        "",
        "## Blocked Conditions",
        *_render_bullets(payload["blocked_conditions"]),
        "",
        "## Missing Requirements",
        *_render_bullets(payload["missing_requirements"]),
        "",
        "## Operator Execution Authorization Surface",
        f"- Question: {surface['question']}",
        (
            "- Execution authorization required before dispatch: "
            f"{surface['execution_authorization_required_before_dispatch']}"
        ),
        *_render_bullets(list(surface["allowed_answers"])),
        "",
        "## Explicit Non-Proofs",
        *_render_bullets(payload["explicit_non_proofs"]),
        "",
        "## Posture",
        f"- worker_dispatched={payload['worker_dispatched']}",
        f"- task_execution_authorized={payload['task_execution_authorized']}",
        f"- task_executed={payload['task_executed']}",
        f"- mutation_authorized={payload['mutation_authorized']}",
        f"- runtime_required={payload['runtime_required']}",
        f"- provider_model_required={payload['provider_model_required']}",
        f"- recommended_next_boundary={payload['recommended_next_boundary']}",
    ]
    return "\n".join(lines)
