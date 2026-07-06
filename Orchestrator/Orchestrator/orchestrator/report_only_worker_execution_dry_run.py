from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestrator.queued_task_execution_authorization_review import (
    build_queued_task_execution_authorization_review_dict,
)


BOUNDARY = "REPORT_ONLY_WORKER_EXECUTION_DRY_RUN_BOUNDARY_SOURCE_TEST_DOCS"
PACKET_NAME = "report_only_worker_execution_dry_run"
RECOMMENDED_NEXT_BOUNDARY = "REPORT_ONLY_WORKER_RESULT_REVIEW_SOURCE_TEST_DOCS"

EXPLICIT_NON_PROOFS = (
    "no runtime/provider/model execution",
    "no live coordinator reasoning proof",
    "no autonomous task dispatch proof",
    "no real worker execution proof",
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
    "real_worker_executed": False,
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


def _blocked_result(
    *,
    review_packet: dict[str, Any] | None,
    reason: str,
    blocked_conditions: list[str],
    missing_requirements: list[str] | None = None,
) -> dict[str, Any]:
    review = review_packet if isinstance(review_packet, dict) else {}
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "dry_run_status": "blocked",
        "dry_result_created": False,
        "dry_result_persisted": False,
        "artifact_id": "",
        "artifact_path": "",
        "source_task_id": _normalize_text(review.get("task_id")),
        "source_review_decision": _normalize_text(review.get("review_decision")),
        "reason": reason,
        "blocked_conditions": sorted(set(blocked_conditions)),
        "missing_requirements": sorted(set(missing_requirements or [])),
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def _authorization_conditions(operator_authorization: dict[str, Any] | None) -> tuple[list[str], list[str]]:
    if not isinstance(operator_authorization, dict):
        return ["operator_execution_authorization_record_required"], ["operator_execution_authorization"]

    blocked: list[str] = []
    missing: list[str] = []
    if _normalize_text(operator_authorization.get("decision")) != "authorize_report_only_execution_boundary":
        blocked.append("operator_decision_does_not_authorize_report_only_execution_boundary")
    if operator_authorization.get("roger_authorized") is not True:
        blocked.append("roger_authorized_boolean_required")
    if not _normalize_text(operator_authorization.get("authorization_note")):
        missing.append("authorization_note")
    return blocked, missing


def _dry_result_payload(
    review_packet: dict[str, Any],
    operator_authorization: dict[str, Any],
) -> dict[str, Any]:
    task = review_packet["task_summary"]
    task_id = _normalize_text(task.get("id"))
    return {
        "artifact_id": f"dry_result_{task_id}",
        "artifact_kind": "report_only_worker_execution_dry_run_result",
        "source_task_id": task_id,
        "source_run_id": _normalize_text(review_packet.get("run_id")),
        "task_title": _normalize_text(task.get("title")),
        "dry_run_classification": "deterministic_report_only_no_worker_dispatched",
        "what_worker_would_do": (
            "Read the approved queued task, preserve its scope, and produce the "
            "requested report-only planning artifact in a future authorized boundary."
        ),
        "dry_output_summary": (
            "The queued task is ready for a future report-only worker boundary. "
            "This dry run records the intended worker action without performing it."
        ),
        "files_in_scope": _text_list(task.get("files_in_scope")),
        "success_criteria_checked": _text_list(task.get("success_criteria")),
        "expected_output": _normalize_text(task.get("expected_output")),
        "operator_authorization_note": _normalize_text(operator_authorization.get("authorization_note")),
        "verification_notes": (
            "review_decision_ready_for_operator_execution_authorization",
            "task_status_queued",
            "execution_policy_report_only",
            "no_execution_artifact_present_before_dry_run",
            "dry_run_did_not_mutate_files",
            "dry_run_did_not_dispatch_worker",
        ),
        "activity_flags": {
            "dry_result_created": True,
            "worker_dispatched": False,
            "real_worker_executed": False,
            "runtime_executed": False,
            "provider_model_executed": False,
            "file_mutation_performed": False,
            "production_task_executed": False,
        },
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
    }


def run_report_only_worker_execution_dry_run(
    review_packet: dict[str, Any] | None = None,
    operator_authorization: dict[str, Any] | None = None,
    artifact_store_dir: str | Path | None = None,
) -> dict[str, Any]:
    review = review_packet or build_queued_task_execution_authorization_review_dict()
    if _normalize_text(review.get("review_decision")) != "ready_for_operator_execution_authorization_review":
        return _blocked_result(
            review_packet=review,
            reason="Queued task review is not ready for execution authorization.",
            blocked_conditions=["queued_task_review_not_ready_for_dry_run"],
            missing_requirements=list(review.get("missing_requirements", ())),
        )

    authorization_blocked, authorization_missing = _authorization_conditions(operator_authorization)
    if authorization_blocked or authorization_missing:
        return _blocked_result(
            review_packet=review,
            reason="Explicit Roger authorization is required before a report-only dry run.",
            blocked_conditions=authorization_blocked,
            missing_requirements=authorization_missing,
        )

    if artifact_store_dir is None:
        return _blocked_result(
            review_packet=review,
            reason="Caller-supplied artifact_store_dir is required for dry-result persistence.",
            blocked_conditions=["artifact_store_dir_required"],
            missing_requirements=["artifact_store_dir"],
        )

    artifact_payload = _dry_result_payload(review, operator_authorization or {})
    artifact_dir = Path(artifact_store_dir)
    artifact_path = artifact_dir / f"{artifact_payload['artifact_id']}.json"
    if artifact_path.exists():
        return _blocked_result(
            review_packet=review,
            reason="Dry result artifact already exists.",
            blocked_conditions=["dry_result_artifact_already_exists"],
            missing_requirements=[str(artifact_path)],
        )

    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(artifact_payload, indent=2), encoding="utf-8")

    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "dry_run_status": "created",
        "dry_result_created": True,
        "dry_result_persisted": True,
        "artifact_id": artifact_payload["artifact_id"],
        "artifact_path": str(artifact_path),
        "source_task_id": artifact_payload["source_task_id"],
        "source_review_decision": _normalize_text(review.get("review_decision")),
        "reason": "Created one deterministic report-only dry worker result artifact.",
        "blocked_conditions": [],
        "missing_requirements": [],
        "dry_result_artifact": artifact_payload,
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def render_report_only_worker_execution_dry_run_markdown(
    result: dict[str, Any] | None = None,
) -> str:
    payload = result or run_report_only_worker_execution_dry_run()
    artifact = payload.get("dry_result_artifact") if isinstance(payload.get("dry_result_artifact"), dict) else {}
    lines = [
        "# Report-Only Worker Execution Dry Run",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Packet: `{payload['packet_name']}`",
        "",
        "## Dry Run Status",
        f"- Status: {payload['dry_run_status']}",
        f"- Dry result created: {payload['dry_result_created']}",
        f"- Dry result persisted: {payload['dry_result_persisted']}",
        f"- Artifact id: {payload['artifact_id']}",
        f"- Artifact path: {payload['artifact_path']}",
        f"- Reason: {payload['reason']}",
        "",
        "## Dry Result",
    ]
    if artifact:
        lines.extend(
            (
                f"- Source task id: {artifact['source_task_id']}",
                f"- Classification: {artifact['dry_run_classification']}",
                f"- What worker would do: {artifact['what_worker_would_do']}",
                f"- Dry output summary: {artifact['dry_output_summary']}",
                "### Files In Scope",
                *[f"- {item}" for item in artifact["files_in_scope"]],
                "### Success Criteria Checked",
                *[f"- {item}" for item in artifact["success_criteria_checked"]],
                "### Verification Notes",
                *[f"- {item}" for item in artifact["verification_notes"]],
            )
        )
    else:
        lines.append("- No dry result artifact was created.")
    lines.extend(
        (
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
            f"- real_worker_executed={payload['real_worker_executed']}",
            f"- task_execution_authorized={payload['task_execution_authorized']}",
            f"- mutation_authorized={payload['mutation_authorized']}",
            f"- runtime_required={payload['runtime_required']}",
            f"- provider_model_required={payload['provider_model_required']}",
            f"- recommended_next_boundary={payload['recommended_next_boundary']}",
        )
    )
    return "\n".join(lines)
