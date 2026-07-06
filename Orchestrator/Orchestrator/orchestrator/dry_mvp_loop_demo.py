from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestrator.approved_bounded_task_packet_to_queued_task import create_queued_task_from_approved_bounded_packet
from orchestrator.bounded_task_packet_review_gate import build_bounded_task_packet_review_gate_dict
from orchestrator.dry_mvp_loop_closeout_review import build_dry_mvp_loop_closeout_review_dict
from orchestrator.goal_intake_to_bounded_task_packet import DOGWALKING_APP_GOAL, build_goal_intake_to_bounded_task_packet_dict
from orchestrator.pm_facing_orchestrator_status_packet import build_pm_facing_orchestrator_status_packet_dict
from orchestrator.queued_task_execution_authorization_review import build_queued_task_execution_authorization_review_dict
from orchestrator.report_only_worker_execution_dry_run import run_report_only_worker_execution_dry_run
from orchestrator.report_only_worker_result_review import build_report_only_worker_result_review_dict


BOUNDARY = "DRY_MVP_LOOP_DEMO_CLI_SOURCE_TEST_DOCS"
PACKET_NAME = "dry_mvp_loop_demo"


def _approval() -> dict[str, Any]:
    return {
        "decision": "approve_next_boundary",
        "roger_approved": True,
        "approval_note": "Deterministic demo approval for queued task creation only.",
    }


def _authorization() -> dict[str, Any]:
    return {
        "decision": "authorize_report_only_execution_boundary",
        "roger_authorized": True,
        "authorization_note": "Deterministic demo authorization for report-only dry run only.",
    }


def run_dry_mvp_loop_demo(output_dir: str | Path) -> dict[str, Any]:
    base = Path(output_dir)
    task_dir = base / "tasks"
    artifact_dir = base / "artifacts"
    goal_packet = build_goal_intake_to_bounded_task_packet_dict(DOGWALKING_APP_GOAL)
    task_packet_review = build_bounded_task_packet_review_gate_dict(goal_packet)
    task_creation = create_queued_task_from_approved_bounded_packet(
        review_gate=task_packet_review,
        operator_approval=_approval(),
        task_store_dir=task_dir,
    )
    queued_task_review = build_queued_task_execution_authorization_review_dict(task_creation)
    dry_run = run_report_only_worker_execution_dry_run(
        review_packet=queued_task_review,
        operator_authorization=_authorization(),
        artifact_store_dir=artifact_dir,
    )
    result_review = build_report_only_worker_result_review_dict(dry_run)
    closeout = build_dry_mvp_loop_closeout_review_dict(result_review)
    pm_status = build_pm_facing_orchestrator_status_packet_dict(closeout)
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "output_dir": str(base),
        "task_store_dir": str(task_dir),
        "artifact_store_dir": str(artifact_dir),
        "goal_packet": goal_packet,
        "task_packet_review": task_packet_review,
        "task_creation": task_creation,
        "queued_task_review": queued_task_review,
        "dry_run": dry_run,
        "result_review": result_review,
        "closeout": closeout,
        "pm_status": pm_status,
        "demo_status": (
            "dry_mvp_demo_pass"
            if closeout.get("closeout_decision") == "dry_mvp_loop_closeout_pass"
            else "dry_mvp_demo_not_closed"
        ),
        "non_proofs": list(pm_status["explicit_non_proofs"]),
    }


def render_dry_mvp_loop_demo_text(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "DRY MVP LOOP DEMO",
            f"status={result['demo_status']}",
            f"output_dir={result['output_dir']}",
            f"task_creation={result['task_creation']['task_creation_status']}",
            f"queued_review={result['queued_task_review']['review_decision']}",
            f"dry_run={result['dry_run']['dry_run_status']}",
            f"result_review={result['result_review']['review_decision']}",
            f"closeout={result['closeout']['closeout_decision']}",
            f"pm_status={result['pm_status']['overall_status']}",
            "non_proofs=" + "; ".join(result["non_proofs"]),
        ]
    )


def dry_mvp_loop_demo_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2)
