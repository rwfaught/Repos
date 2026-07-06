from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.dry_mvp_commit_readiness_review import (
    build_dry_mvp_commit_readiness_review_dict,
)


BOUNDARY = "DRY_MVP_MILESTONE_CLOSEOUT_SOURCE_TEST_DOCS"
PACKET_NAME = "dry_mvp_milestone_closeout"
RECOMMENDED_NEXT_BOUNDARY = "ROGER_DRY_MVP_COMMIT_DECISION_OPERATOR_REVIEW"

MILESTONE_REQUIREMENTS = (
    "goal_intake_preserves_broad_operator_goal",
    "bounded_task_packet_can_be_proposed",
    "bounded_task_packet_has_review_gate",
    "roger_approval_required_before_queued_task_creation",
    "queued_task_has_execution_authorization_review",
    "report_only_dry_run_writes_caller_supplied_artifact",
    "dry_result_has_review_gate",
    "dry_loop_has_closeout_review",
    "pm_facing_status_packet_exists",
    "thin_cli_readback_exists",
    "integrated_acceptance_passes",
    "commit_readiness_review_passes",
)

EXPLICIT_NON_PROOFS = (
    "no runtime/provider/model execution",
    "no real provider path proof for this dry MVP spine",
    "no live coordinator reasoning proof",
    "no autonomous task dispatch proof",
    "no real worker execution proof",
    "no local model capability proof",
    "no frontier model escalation proof",
    "no semantic correctness proof",
    "no production readiness proof",
    "no full current-success-criterion proof",
    "no file mutation execution proof through the Orchestrator spine",
    "no Phase 387 implementation",
    "no first product wedge selection",
    "no commit performed",
    "no push performed",
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
    "full_current_success_criterion_claimed": False,
    "phase_387_implemented": False,
    "first_product_wedge_selected": False,
    "commit_performed": False,
    "push_performed": False,
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _closeout_status(readiness_packet: dict[str, Any]) -> tuple[str, list[str], str]:
    if _normalize_text(readiness_packet.get("readiness_status")) != "dry_mvp_ready_for_roger_commit_decision":
        return (
            "dry_mvp_milestone_not_closed",
            ["commit_readiness_review_not_passed"],
            "Repair dry MVP readiness blockers before milestone closeout.",
        )
    return (
        "dry_mvp_source_test_docs_milestone_complete_pending_roger_commit_decision",
        [],
        "Ask Roger for the commit decision before treating the milestone as committed.",
    )


def build_dry_mvp_milestone_closeout_dict(
    output_dir: str | Path | None = None,
    project_root: str | Path | None = None,
    readiness_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    readiness = readiness_packet or build_dry_mvp_commit_readiness_review_dict(
        output_dir=output_dir,
        project_root=project_root,
    )
    status, blocked_conditions, recommended_action = _closeout_status(readiness)
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": (
            "Close out the source/test/docs dry MVP milestone without overstating it "
            "as product readiness, real worker execution, or full current-success proof."
        ),
        "milestone_status": status,
        "source_readiness_status": _normalize_text(readiness.get("readiness_status")),
        "blocked_conditions": blocked_conditions,
        "missing_requirements": list(readiness.get("missing_requirements", ())),
        "recommended_action": recommended_action,
        "milestone_requirements": list(MILESTONE_REQUIREMENTS),
        "what_is_complete": (
            "deterministic dry loop from broad goal intake to reviewed dry result artifact",
            "operator approval and authorization checkpoints in the dry spine",
            "PM-facing status packet",
            "CLI/readback surface using caller-supplied directories",
            "integrated acceptance check",
            "commit-readiness review for Roger decision",
        ),
        "what_is_not_complete": (
            "real local-worker execution in this spine",
            "provider/model routing in this spine",
            "semantic quality proof",
            "production readiness",
            "full CURRENT_SUCCESS_CRITERION.md proof for a real bounded task run",
            "commit or push",
        ),
        "roger_decision_needed": (
            "commit the dry MVP skeleton",
            "request targeted repair before commit",
            "pause without commit",
            "authorize a later local-worker proof boundary",
        ),
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def render_dry_mvp_milestone_closeout_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = packet or build_dry_mvp_milestone_closeout_dict()
    lines = [
        "# Dry MVP Milestone Closeout",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Status: `{payload['milestone_status']}`",
        "",
        "## Purpose",
        payload["purpose"],
        "",
        "## What Is Complete",
        *[f"- {item}" for item in payload["what_is_complete"]],
        "",
        "## What Is Not Complete",
        *[f"- {item}" for item in payload["what_is_not_complete"]],
        "",
        "## Milestone Requirements",
        *[f"- {item}" for item in payload["milestone_requirements"]],
        "",
        "## Roger Decision Needed",
        *[f"- {item}" for item in payload["roger_decision_needed"]],
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
        f"- runtime_required={payload['runtime_required']}",
        f"- provider_model_required={payload['provider_model_required']}",
        f"- full_current_success_criterion_claimed={payload['full_current_success_criterion_claimed']}",
        f"- commit_performed={payload['commit_performed']}",
        f"- push_performed={payload['push_performed']}",
        f"- recommended_next_boundary={payload['recommended_next_boundary']}",
    ]
    return "\n".join(lines)
