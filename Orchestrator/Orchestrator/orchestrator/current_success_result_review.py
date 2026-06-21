from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import orchestrator.artifact_store as artifact_store
import orchestrator.run_manager as run_manager
from orchestrator.paths import (
    DATA_DIR,
    VERIFIER_RESULTS_DIR,
    record_path,
    validate_record_id,
)


_READ_ONLY_FLAGS = {
    "task_created": False,
    "task_mutated": False,
    "task_executed": False,
    "execution_performed": False,
    "artifact_created": False,
    "artifact_mutated": False,
    "verifier_invoked": False,
    "reviewer_invoked": False,
    "provider_executed": False,
    "runtime_executed": False,
    "model_executed": False,
    "platform_invoked": False,
    "openclaw_invoked": False,
    "discord_invoked": False,
    "bridge_invoked": False,
    "adapter_invoked": False,
}


ACCEPTANCE_RECORDS_DIR = DATA_DIR / "acceptance_records"


_STATUS_CLASSIFICATIONS = {
    "completed": "completed_current_state_success",
    "execution_failed": "execution_failure",
    "verification_failed": "verification_failure",
    "needs_review": "needs_review",
    "queued": "not_executed",
    "in_progress": "in_progress",
}


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _task_path(task_id: str) -> Path:
    return record_path(run_manager.TASKS_DIR, task_id, label="task id")


def _artifact_path(artifact_id: str) -> Path | None:
    artifact_id = _normalize_string(artifact_id)
    if not artifact_id:
        return None
    try:
        return artifact_store.artifact_path(artifact_id)
    except ValueError:
        return None


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _latest_verifier_result_path(task_id: str) -> Path | None:
    safe_task_id = validate_record_id(task_id, label="task id")
    if not VERIFIER_RESULTS_DIR.exists():
        return None
    candidates = sorted(
        VERIFIER_RESULTS_DIR.glob(f"{safe_task_id}_*.json"),
        key=lambda path: path.name,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _artifact_summary(artifact_id: str) -> tuple[dict[str, Any], list[str]]:
    missing: list[str] = []
    path = _artifact_path(artifact_id)
    if path is None:
        return {}, ["execution_artifact_id"]

    if not path.exists():
        return {"artifact_path": str(path)}, ["execution_artifact_file"]

    payload = _read_json(path)
    if payload is None:
        return {"artifact_path": str(path)}, ["execution_artifact_json"]

    return {
        "artifact_id": _normalize_string(payload.get("artifact_id")),
        "artifact_path": str(path),
        "task_id": _normalize_string(payload.get("task_id")),
        "run_id": _normalize_string(payload.get("run_id")),
        "role": _normalize_string(payload.get("role")),
        "status": _normalize_string(payload.get("status")),
        "output_present": bool(_normalize_string(payload.get("output"))),
    }, missing


def _verification_summary(task_id: str) -> tuple[dict[str, Any], list[str]]:
    path = _latest_verifier_result_path(task_id)
    if path is None:
        return {}, ["verifier_result_file"]

    payload = _read_json(path)
    if payload is None:
        return {"verifier_result_path": str(path)}, ["verifier_result_json"]

    result = payload.get("verification_result")
    if not isinstance(result, dict):
        return {"verifier_result_path": str(path)}, ["verification_result"]

    checks = result.get("checks")
    checks_list = checks if isinstance(checks, list) else []
    return {
        "verifier_result_path": str(path),
        "overall_passed": bool(result.get("overall_passed")),
        "check_count": len(checks_list),
        "checks": checks_list,
        "messages": result.get("messages") if isinstance(result.get("messages"), list) else [],
        "verification_caveat": "Deterministic verification is a bounded tripwire only; it does not prove semantic correctness, production readiness, or task adequacy in the strong sense.",
    }, []

def _latest_acceptance_record_summary(task_id: str) -> dict[str, Any]:
    if not ACCEPTANCE_RECORDS_DIR.exists():
        return {
            "acceptance_record_present": False,
            "accepted": False,
            "acceptance_record_id": "",
            "acceptance_record_path": "",
        }

    records: list[dict[str, Any]] = []
    for path in sorted(ACCEPTANCE_RECORDS_DIR.glob("acceptance_*.json")):
        payload = _read_json(path)
        if not isinstance(payload, dict):
            continue
        if _normalize_string(payload.get("task_id")) != task_id:
            continue
        records.append({"path": path, "payload": payload})

    if not records:
        return {
            "acceptance_record_present": False,
            "accepted": False,
            "acceptance_record_id": "",
            "acceptance_record_path": "",
        }

    records.sort(key=lambda record: _normalize_string(record["payload"].get("accepted_at")), reverse=True)
    latest = records[0]
    payload = latest["payload"]

    return {
        "acceptance_record_present": True,
        "accepted": bool(payload.get("accepted")),
        "acceptance_record_id": _normalize_string(payload.get("acceptance_record_id")),
        "acceptance_record_path": str(latest["path"]),
        "accepted_at": _normalize_string(payload.get("accepted_at")),
        "operator_note_present": bool(_normalize_string(payload.get("operator_note"))),
        "result_classification_accepted": _normalize_string(payload.get("result_classification_accepted")),
        "verification_caveat_acknowledged": bool(payload.get("verification_caveat_acknowledged")),
        "provider_caveat_acknowledged": bool(payload.get("provider_caveat_acknowledged")),
    }

def _response_options_for(classification: str) -> list[dict[str, Any]]:
    base = [
        {
            "option_id": "inspect_task_state",
            "label": "Inspect persisted task state.",
            "authorized_now": True,
            "requires_later_boundary": False,
        },
        {
            "option_id": "inspect_execution_artifact",
            "label": "Inspect persisted execution artifact.",
            "authorized_now": True,
            "requires_later_boundary": False,
        },
        {
            "option_id": "inspect_verifier_result",
            "label": "Inspect persisted deterministic verifier result.",
            "authorized_now": True,
            "requires_later_boundary": False,
        },
    ]

    if classification == "completed_current_state_success":
        base.append(
            {
                "option_id": "record_operator_acceptance_later",
                "label": "Define a later explicit acceptance-record boundary if the operator accepts the result.",
                "authorized_now": False,
                "requires_later_boundary": True,
                "later_boundary": "operator_acceptance_record_boundary",
            }
        )
    elif classification == "verification_failure":
        base.append(
            {
                "option_id": "define_verification_failure_repair_boundary",
                "label": "Define a later repair boundary for the verification failure.",
                "authorized_now": False,
                "requires_later_boundary": True,
                "later_boundary": "verification_failure_repair_boundary",
            }
        )
    elif classification == "execution_failure":
        base.append(
            {
                "option_id": "define_execution_failure_repair_boundary",
                "label": "Define a later repair or retry boundary for the execution failure.",
                "authorized_now": False,
                "requires_later_boundary": True,
                "later_boundary": "execution_failure_repair_or_retry_boundary",
            }
        )
    elif classification == "needs_review":
        base.append(
            {
                "option_id": "define_followup_review_boundary",
                "label": "Define a later explicit follow-up review boundary.",
                "authorized_now": False,
                "requires_later_boundary": True,
                "later_boundary": "followup_review_boundary",
            }
        )
    else:
        base.append(
            {
                "option_id": "return_to_task_execution_boundary",
                "label": "Return to an explicit task execution boundary before treating this as a result.",
                "authorized_now": False,
                "requires_later_boundary": True,
                "later_boundary": "task_execution_boundary",
            }
        )

    return base


def _blocked(task_id: str, reason: str, detail: str, blocked_conditions: list[str]) -> dict[str, Any]:
    return {
        "current_success_result_review_surface": True,
        "task_id": task_id,
        "run_id": "",
        "task_path": str(_task_path(task_id)) if task_id else "",
        "final_task_status": "",
        "final_outcome_classification": "blocked",
        "ready_for_operator_review": False,
        "reason": reason,
        "detail": detail,
        "blocked_conditions": sorted(set(blocked_conditions)),
        "missing_requirements": [],
        "task_summary": {},
        "artifact_summary": {},
        "verification_summary": {},
        "acceptance_summary": _latest_acceptance_record_summary(task_id) if task_id else {"acceptance_record_present": False, "accepted": False, "acceptance_record_id": "", "acceptance_record_path": ""},
        "operator_response_surface": "blocked_current_success_result_options",
        "response_options": _response_options_for("blocked"),
        "next_action": "repair_or_provide_required_task_result_records_before_current_success_review",
        **_READ_ONLY_FLAGS,
    }


def review_current_success_task_result(review_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(review_input, dict):
        return _blocked(
            task_id="",
            reason="Review input must be a JSON object.",
            detail="Provide a JSON object with task_id for current-success result review.",
            blocked_conditions=["json_object_input_required"],
        )

    task_id = _normalize_string(review_input.get("task_id"))
    if not task_id:
        return _blocked(
            task_id="",
            reason="Task id is required.",
            detail="Current-success result review requires a persisted task id.",
            blocked_conditions=["task_id_required"],
        )

    try:
        task_file = _task_path(task_id)
    except ValueError as error:
        return _blocked(
            task_id="",
            reason="Task id is invalid.",
            detail=str(error),
            blocked_conditions=["task_id_invalid"],
        )
    if not task_file.exists():
        return _blocked(
            task_id=task_id,
            reason="Persisted task state was not found.",
            detail="The task file must exist before current-success result review can inspect it.",
            blocked_conditions=["task_file_missing"],
        )

    try:
        task = run_manager.load_task(task_id)
    except Exception as error:
        return _blocked(
            task_id=task_id,
            reason="Persisted task state could not be loaded.",
            detail=str(error),
            blocked_conditions=["task_state_unreadable"],
        )

    artifact, artifact_missing = _artifact_summary(task.execution_artifact_id or "")
    verification, verification_missing = _verification_summary(task.id)

    missing = []
    missing.extend(artifact_missing)
    missing.extend(verification_missing)

    final_status = _normalize_string(task.status)
    classification = _STATUS_CLASSIFICATIONS.get(final_status, "unknown_task_status")
    blocked_conditions: list[str] = []

    if final_status in {"queued", "in_progress"}:
        blocked_conditions.append("task_not_final")
    if missing:
        blocked_conditions.append("current_success_required_record_missing")
    if classification == "unknown_task_status":
        blocked_conditions.append("unknown_final_task_status")

    ready = not blocked_conditions and classification in {
        "completed_current_state_success",
        "verification_failure",
        "execution_failure",
        "needs_review",
    }

    operator_surface = {
        "completed_current_state_success": "completed_result_response_options",
        "verification_failure": "verification_failure_response_options",
        "execution_failure": "execution_failure_response_options",
        "needs_review": "needs_review_response_options",
    }.get(classification, "blocked_current_success_result_options")

    return {
        "current_success_result_review_surface": True,
        "task_id": task.id,
        "run_id": task.run_id,
        "task_path": str(task_file),
        "final_task_status": final_status,
        "final_outcome_classification": classification if not blocked_conditions else "blocked",
        "ready_for_operator_review": ready,
        "reason": (
            "Engine-executed task result is ready for current-success operator review."
            if ready
            else "Engine-executed task result is not ready for current-success operator review."
        ),
        "detail": "This read-only surface inspects persisted task state, execution artifact, and deterministic verifier result. It does not execute, mutate, verify, review, call a provider, or touch runtime/model/platform behavior.",
        "blocked_conditions": sorted(set(blocked_conditions)),
        "missing_requirements": missing,
        "task_summary": {
            "task_id": task.id,
            "run_id": task.run_id,
            "title": task.title,
            "role": task.role,
            "status": task.status,
            "files_in_scope": list(task.files_in_scope),
            "success_criteria": list(task.success_criteria),
            "expected_output": task.expected_output,
            "execution_artifact_id": task.execution_artifact_id,
            "verification_checks": task.verification_checks,
        },
        "artifact_summary": artifact,
        "verification_summary": verification,
        "acceptance_summary": _latest_acceptance_record_summary(task.id),
        "operator_response_surface": operator_surface,
        "response_options": _response_options_for(classification),
        "next_action": (
            "operator_may_inspect_task_artifact_and_verifier_then_choose_later_boundary"
            if ready
            else "repair_or_complete_required_current_success_records_before_operator_review"
        ),
        **_READ_ONLY_FLAGS,
    }


