from __future__ import annotations

from typing import Any

from orchestrator import engine
import orchestrator.run_manager as run_manager
from orchestrator.current_success_result_review import review_current_success_task_result
from orchestrator.paths import resolve_declared_project_path, validate_record_id
from orchestrator.task_schema import FILESYSTEM_MUTATION_EXECUTION_POLICY, Task


_REQUIRED_FIELDS = (
    "packet_id",
    "run_id",
    "task_id",
    "title",
    "files_in_scope",
    "success_criteria",
    "expected_output",
)

_PROVIDER_RUNTIME_REQUEST_FIELDS = (
    "model",
    "model_name",
    "runtime",
    "runtime_name",
    "platform",
    "platform_name",
    "ollama_model",
    "openclaw_runtime",
    "hermes_runtime",
    "allow_live_provider",
)

_NON_PROOFS = [
    "no_semantic_correctness_proof",
    "no_live_provider_model_proof",
    "no_runtime_platform_proof",
    "no_autonomous_ai_coding_proof",
    "no_production_readiness_proof",
    "local_file_is_deterministic_local_behavior_not_model_backed_generation",
    "deterministic_verification_is_a_bounded_tripwire",
]

_NO_ACTIVITY_FLAGS = {
    "model_executed": False,
    "runtime_executed": False,
    "platform_invoked": False,
    "live_provider_invoked": False,
    "ollama_invoked": False,
    "openclaw_invoked": False,
    "hermes_invoked": False,
    "discord_invoked": False,
    "installer_invoked": False,
    "autonomous_ai_coding_claimed": False,
    "production_readiness_claimed": False,
    "semantic_correctness_claimed": False,
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _blocked(
    *,
    packet: dict[str, Any] | None,
    blocked_conditions: list[str],
    missing_requirements: list[str] | None = None,
    detail: str = "",
) -> dict[str, Any]:
    packet = packet if isinstance(packet, dict) else {}
    return {
        "operator_coding_task_packet_surface": True,
        "packet_id": _normalize_text(packet.get("packet_id")),
        "run_id": _normalize_text(packet.get("run_id")),
        "task_id": _normalize_text(packet.get("task_id")),
        "accepted": False,
        "blocked": True,
        "blocked_conditions": sorted(set(blocked_conditions)),
        "missing_requirements": sorted(set(missing_requirements or [])),
        "detail": detail,
        "execution_provider": "",
        "final_task_status": "",
        "execution_artifact_id": "",
        "current_success_review": {},
        "operator_response_surface": "blocked_operator_coding_task_packet_options",
        "operator_next_action": "repair_packet_before_execution_boundary",
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        "non_proofs": list(_NON_PROOFS),
    }


def _require_nonempty_sequence(
    packet: dict[str, Any],
    field_name: str,
) -> tuple[list[str], str | None]:
    raw = packet.get(field_name)
    if not isinstance(raw, list):
        return [], field_name
    values = [_normalize_text(item) for item in raw]
    values = [item for item in values if item]
    if not values:
        return [], field_name
    return values, None


def _validate_packet(packet: Any) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(packet, dict):
        return None, _blocked(
            packet=None,
            blocked_conditions=["packet_must_be_json_object"],
            detail="Operator coding task packet must be a JSON object.",
        )

    missing = [
        field_name
        for field_name in _REQUIRED_FIELDS
        if not _normalize_text(packet.get(field_name))
    ]

    packet_id = _normalize_text(packet.get("packet_id"))
    run_id = _normalize_text(packet.get("run_id"))
    task_id = _normalize_text(packet.get("task_id"))
    title = _normalize_text(packet.get("title"))
    expected_output = (
        str(packet.get("expected_output"))
        if packet.get("expected_output") is not None
        else ""
    )

    files_in_scope, files_missing = _require_nonempty_sequence(packet, "files_in_scope")
    success_criteria, criteria_missing = _require_nonempty_sequence(
        packet,
        "success_criteria",
    )
    if files_missing:
        missing.append(files_missing)
    if criteria_missing:
        missing.append(criteria_missing)

    blocked_conditions: list[str] = []
    details: list[str] = []

    if missing:
        blocked_conditions.append("missing_required_packet_fields")

    provider_name = _normalize_text(packet.get("provider_name")) or "local_file"
    if provider_name != "local_file":
        blocked_conditions.append("unsupported_provider_name")
        details.append("Phase 274 only allows provider_name='local_file'.")

    requested_runtime_fields = [
        field_name
        for field_name in _PROVIDER_RUNTIME_REQUEST_FIELDS
        if field_name in packet and _normalize_text(packet.get(field_name))
    ]
    if requested_runtime_fields:
        blocked_conditions.append("provider_model_runtime_platform_request_rejected")
        missing.extend(requested_runtime_fields)

    execution_policy = (
        _normalize_text(packet.get("execution_policy"))
        or FILESYSTEM_MUTATION_EXECUTION_POLICY
    )
    if execution_policy != FILESYSTEM_MUTATION_EXECUTION_POLICY:
        blocked_conditions.append("unsupported_execution_policy")
        details.append("Phase 274 requires filesystem_mutation execution_policy.")

    for label, value in (
        ("packet id", packet_id),
        ("run id", run_id),
        ("task id", task_id),
    ):
        if not value:
            continue
        try:
            validate_record_id(value, label=label)
        except ValueError as error:
            blocked_conditions.append(f"{label.replace(' ', '_')}_invalid")
            details.append(str(error))

    for declared_path in files_in_scope:
        try:
            resolve_declared_project_path(declared_path)
        except ValueError as error:
            blocked_conditions.append("declared_file_path_invalid")
            details.append(str(error))

    if blocked_conditions:
        return None, _blocked(
            packet=packet,
            blocked_conditions=blocked_conditions,
            missing_requirements=missing,
            detail=" ".join(details),
        )

    validated = {
        "packet_id": packet_id,
        "run_id": run_id,
        "task_id": task_id,
        "title": title,
        "files_in_scope": files_in_scope,
        "success_criteria": success_criteria,
        "expected_output": expected_output,
        "provider_name": provider_name,
        "execution_policy": execution_policy,
    }
    return validated, None


def _operator_next_action_from_review(review: dict[str, Any]) -> str:
    option_ids = [
        _normalize_text(option.get("option_id"))
        for option in review.get("response_options", [])
        if isinstance(option, dict)
    ]
    preferred = [
        "inspect_task_state",
        "inspect_execution_artifact",
        "inspect_verifier_result",
        "record_operator_acceptance_later",
    ]
    available = [option_id for option_id in preferred if option_id in option_ids]
    return "; ".join(available) or _normalize_text(review.get("next_action"))


def run_operator_coding_task_packet(packet: dict[str, Any]) -> dict[str, Any]:
    validated, blocked = _validate_packet(packet)
    if blocked is not None:
        return blocked
    assert validated is not None

    task = Task(
        id=validated["task_id"],
        run_id=validated["run_id"],
        title=validated["title"],
        role="coder",
        status="queued",
        dependencies=[],
        success_criteria=validated["success_criteria"],
        files_in_scope=validated["files_in_scope"],
        retry_count=0,
        expected_output=validated["expected_output"],
        execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
        requires_causal_change=False,
    )

    run_manager.save_task(task)
    engine.process_task_by_id(
        run_manager.load_task(task.id),
        provider_name="local_file",
    )
    completed = run_manager.load_task(task.id)
    review = review_current_success_task_result({"task_id": task.id})

    return {
        "operator_coding_task_packet_surface": True,
        "packet_id": validated["packet_id"],
        "run_id": completed.run_id,
        "task_id": completed.id,
        "accepted": True,
        "blocked": False,
        "blocked_conditions": [],
        "missing_requirements": [],
        "execution_provider": "local_file",
        "final_task_status": completed.status,
        "execution_artifact_id": completed.execution_artifact_id or "",
        "current_success_review": review,
        "operator_response_surface": review.get("operator_response_surface"),
        "operator_next_action": _operator_next_action_from_review(review),
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        "non_proofs": list(_NON_PROOFS),
    }
