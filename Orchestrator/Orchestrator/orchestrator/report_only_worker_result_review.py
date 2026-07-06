from __future__ import annotations

from typing import Any

from orchestrator.report_only_worker_execution_dry_run import (
    run_report_only_worker_execution_dry_run,
)


BOUNDARY = "REPORT_ONLY_WORKER_RESULT_REVIEW_SOURCE_TEST_DOCS"
PACKET_NAME = "report_only_worker_result_review"
RECOMMENDED_NEXT_BOUNDARY = "DRY_MVP_LOOP_CLOSEOUT_REVIEW_READONLY"

REQUIRED_ARTIFACT_FIELDS = (
    "artifact_id",
    "artifact_kind",
    "source_task_id",
    "dry_run_classification",
    "what_worker_would_do",
    "dry_output_summary",
    "files_in_scope",
    "success_criteria_checked",
    "verification_notes",
    "activity_flags",
    "explicit_non_proofs",
)

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


def _artifact_from_result(result: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(result, dict):
        return {}
    artifact = result.get("dry_result_artifact")
    if isinstance(artifact, dict):
        return dict(artifact)
    if result.get("artifact_id") and result.get("artifact_kind"):
        return dict(result)
    return {}


def _review_artifact(artifact: dict[str, Any]) -> tuple[str, list[str], list[str], str]:
    blocked: list[str] = []
    missing: list[str] = []

    for field in REQUIRED_ARTIFACT_FIELDS:
        value = artifact.get(field)
        if isinstance(value, dict):
            if not value:
                missing.append(field)
        elif isinstance(value, (list, tuple)):
            if not _text_list(value):
                missing.append(field)
        elif not _normalize_text(value):
            missing.append(field)

    if missing:
        blocked.append("dry_result_artifact_missing_required_fields")

    if _normalize_text(artifact.get("artifact_kind")) != "report_only_worker_execution_dry_run_result":
        blocked.append("unexpected_artifact_kind")
    if _normalize_text(artifact.get("dry_run_classification")) != "deterministic_report_only_no_worker_dispatched":
        blocked.append("unexpected_dry_run_classification")

    flags = artifact.get("activity_flags")
    if not isinstance(flags, dict):
        blocked.append("activity_flags_missing")
    else:
        for field in (
            "worker_dispatched",
            "real_worker_executed",
            "runtime_executed",
            "provider_model_executed",
            "file_mutation_performed",
            "production_task_executed",
        ):
            if flags.get(field) is not False:
                blocked.append(f"{field}_must_be_false")

    notes = set(_text_list(artifact.get("verification_notes")))
    for note in (
        "dry_run_did_not_mutate_files",
        "dry_run_did_not_dispatch_worker",
    ):
        if note not in notes:
            missing.append(f"verification_notes.{note}")
            blocked.append("dry_result_artifact_missing_required_fields")

    if blocked:
        return (
            "needs_dry_result_repair",
            sorted(set(blocked)),
            sorted(set(missing)),
            "Repair the dry result artifact before treating the dry loop as reviewable.",
        )

    return (
        "accepted_as_dry_loop_artifact",
        [],
        [],
        "Dry result artifact is structurally reviewable and can be used for dry MVP closeout review.",
    )


def build_report_only_worker_result_review_dict(
    dry_run_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = dry_run_result or run_report_only_worker_execution_dry_run()
    artifact = _artifact_from_result(source)
    decision, blocked_conditions, missing_requirements, recommended_action = _review_artifact(artifact)
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": (
            "Review the report-only dry worker result artifact and expose clear "
            "acceptance, repair, or next-step options without claiming real execution."
        ),
        "source_dry_run_status": _normalize_text(source.get("dry_run_status"))
        if isinstance(source, dict)
        else "",
        "artifact_id": _normalize_text(artifact.get("artifact_id")),
        "source_task_id": _normalize_text(artifact.get("source_task_id")),
        "review_decision": decision,
        "blocked_conditions": blocked_conditions,
        "missing_requirements": missing_requirements,
        "recommended_action": recommended_action,
        "operator_response_options": (
            "accept_dry_loop_artifact",
            "repair_dry_result_artifact",
            "repeat_dry_run_with_same_inputs",
            "authorize_next_local_worker_proof_boundary_later",
            "stop_or_reframe_goal",
        ),
        "artifact_summary": {
            "artifact_id": _normalize_text(artifact.get("artifact_id")),
            "artifact_kind": _normalize_text(artifact.get("artifact_kind")),
            "source_task_id": _normalize_text(artifact.get("source_task_id")),
            "dry_run_classification": _normalize_text(artifact.get("dry_run_classification")),
            "dry_output_summary": _normalize_text(artifact.get("dry_output_summary")),
            "files_in_scope": _text_list(artifact.get("files_in_scope")),
            "success_criteria_checked": _text_list(artifact.get("success_criteria_checked")),
            "verification_notes": _text_list(artifact.get("verification_notes")),
        },
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def render_report_only_worker_result_review_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = packet or build_report_only_worker_result_review_dict()
    summary = payload["artifact_summary"]
    lines = [
        "# Report-Only Worker Result Review",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Packet: `{payload['packet_name']}`",
        f"Purpose: {payload['purpose']}",
        "",
        "## Review Decision",
        f"- Decision: {payload['review_decision']}",
        f"- Recommended action: {payload['recommended_action']}",
        "",
        "## Artifact Summary",
        f"- Artifact id: {summary['artifact_id']}",
        f"- Artifact kind: {summary['artifact_kind']}",
        f"- Source task id: {summary['source_task_id']}",
        f"- Classification: {summary['dry_run_classification']}",
        f"- Dry output summary: {summary['dry_output_summary']}",
        "",
        "## Files In Scope",
        *[f"- {item}" for item in summary["files_in_scope"]],
        "",
        "## Success Criteria Checked",
        *[f"- {item}" for item in summary["success_criteria_checked"]],
        "",
        "## Verification Notes",
        *[f"- {item}" for item in summary["verification_notes"]],
        "",
        "## Operator Response Options",
        *[f"- {item}" for item in payload["operator_response_options"]],
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
    ]
    return "\n".join(lines)
