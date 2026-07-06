from __future__ import annotations

from typing import Any

from orchestrator.report_only_worker_result_review import (
    build_report_only_worker_result_review_dict,
)


BOUNDARY = "DRY_MVP_LOOP_CLOSEOUT_REVIEW_SOURCE_TEST_DOCS"
PACKET_NAME = "dry_mvp_loop_closeout_review"
RECOMMENDED_NEXT_BOUNDARY = "PM_FACING_ORCHESTRATOR_STATUS_PACKET_SOURCE_TEST_DOCS"

DRY_LOOP_STAGES = (
    "goal_intake_to_bounded_task_packet",
    "bounded_task_packet_review_gate",
    "approved_bounded_task_packet_to_queued_task",
    "queued_task_execution_authorization_review",
    "report_only_worker_execution_dry_run",
    "report_only_worker_result_review",
)

PROVEN_DRY_CAPABILITIES = (
    "broad goal can be preserved as structured intake",
    "missing inputs and risk flags can be surfaced",
    "a bounded task packet can be proposed",
    "a bounded task packet can be reviewed before approval",
    "explicit Roger approval can create a queued report-only task record",
    "a queued task can be reviewed before execution authorization",
    "explicit Roger authorization can create a deterministic dry result artifact",
    "a dry result artifact can be reviewed and surfaced with response options",
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


def _closeout_decision(result_review: dict[str, Any]) -> tuple[str, list[str], list[str], str]:
    if _normalize_text(result_review.get("review_decision")) != "accepted_as_dry_loop_artifact":
        return (
            "dry_mvp_loop_not_ready_for_closeout",
            ["dry_worker_result_review_not_accepted"],
            list(result_review.get("missing_requirements", ())),
            "Repair or rerun the dry worker result before closeout.",
        )
    return (
        "dry_mvp_loop_closeout_pass",
        [],
        [],
        "Dry MVP loop is structurally complete at deterministic source/test/docs level.",
    )


def build_dry_mvp_loop_closeout_review_dict(
    result_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = result_review or build_report_only_worker_result_review_dict()
    decision, blocked_conditions, missing_requirements, recommended_action = _closeout_decision(source)
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": (
            "Close out the deterministic dry MVP loop by recording what is structurally "
            "proven, what remains unproven, and what Roger can judge next."
        ),
        "source_result_review_decision": _normalize_text(source.get("review_decision")),
        "closeout_decision": decision,
        "blocked_conditions": blocked_conditions,
        "missing_requirements": missing_requirements,
        "recommended_action": recommended_action,
        "dry_loop_stages": list(DRY_LOOP_STAGES),
        "proven_dry_capabilities": list(PROVEN_DRY_CAPABILITIES),
        "operator_can_now_judge": (
            "whether the dry loop is understandable",
            "whether the approval gates are in the right places",
            "whether the artifact chain is inspectable enough",
            "whether a later local-worker proof is worth authorizing",
            "whether to pause and commit the deterministic dry MVP skeleton",
        ),
        "next_real_options": (
            "commit the dry MVP skeleton after verification",
            "add a local deterministic CLI/readback surface",
            "authorize a later local-worker proof boundary",
            "stop and review manually before any real execution",
        ),
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def render_dry_mvp_loop_closeout_review_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = packet or build_dry_mvp_loop_closeout_review_dict()
    lines = [
        "# Dry MVP Loop Closeout Review",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Packet: `{payload['packet_name']}`",
        f"Purpose: {payload['purpose']}",
        "",
        "## Closeout Decision",
        f"- Decision: {payload['closeout_decision']}",
        f"- Recommended action: {payload['recommended_action']}",
        "",
        "## Dry Loop Stages",
        *[f"- {item}" for item in payload["dry_loop_stages"]],
        "",
        "## Proven Dry Capabilities",
        *[f"- {item}" for item in payload["proven_dry_capabilities"]],
        "",
        "## Operator Can Now Judge",
        *[f"- {item}" for item in payload["operator_can_now_judge"]],
        "",
        "## Next Real Options",
        *[f"- {item}" for item in payload["next_real_options"]],
        "",
        "## Blocked Conditions",
        *[f"- {item}" for item in payload["blocked_conditions"]],
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
