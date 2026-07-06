from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.dry_mvp_integrated_acceptance import (
    build_dry_mvp_integrated_acceptance_dict,
)


BOUNDARY = "DRY_MVP_COMMIT_READINESS_REVIEW_SOURCE_TEST_DOCS"
PACKET_NAME = "dry_mvp_commit_readiness_review"
RECOMMENDED_NEXT_BOUNDARY = "ROGER_DRY_MVP_COMMIT_DECISION_OPERATOR_REVIEW"

EXPECTED_MVP_FILES = (
    "orchestrator/goal_intake_to_bounded_task_packet.py",
    "orchestrator/bounded_task_packet_review_gate.py",
    "orchestrator/approved_bounded_task_packet_to_queued_task.py",
    "orchestrator/queued_task_execution_authorization_review.py",
    "orchestrator/report_only_worker_execution_dry_run.py",
    "orchestrator/report_only_worker_result_review.py",
    "orchestrator/dry_mvp_loop_closeout_review.py",
    "orchestrator/pm_facing_orchestrator_status_packet.py",
    "orchestrator/dry_mvp_loop_demo.py",
    "orchestrator/dry_mvp_loop_cli.py",
    "orchestrator/dry_mvp_integrated_acceptance.py",
    "orchestrator/dry_mvp_commit_readiness_review.py",
    "orchestrator/dry_mvp_milestone_closeout.py",
    "tests/test_goal_intake_to_bounded_task_packet.py",
    "tests/test_bounded_task_packet_review_gate.py",
    "tests/test_approved_bounded_task_packet_to_queued_task.py",
    "tests/test_queued_task_execution_authorization_review.py",
    "tests/test_report_only_worker_execution_dry_run.py",
    "tests/test_report_only_worker_result_review.py",
    "tests/test_dry_mvp_loop_closeout_review.py",
    "tests/test_pm_facing_orchestrator_status_packet.py",
    "tests/test_dry_mvp_loop_demo_cli.py",
    "tests/test_dry_mvp_integrated_acceptance.py",
    "tests/test_dry_mvp_commit_readiness_review.py",
    "tests/test_dry_mvp_milestone_closeout.py",
    "docs/GOAL_INTAKE_TO_BOUNDED_TASK_PACKET_VERTICAL_SLICE.md",
    "docs/BOUNDED_TASK_PACKET_REVIEW_GATE.md",
    "docs/APPROVED_BOUNDED_TASK_PACKET_TO_QUEUED_TASK.md",
    "docs/QUEUED_TASK_EXECUTION_AUTHORIZATION_REVIEW.md",
    "docs/REPORT_ONLY_WORKER_EXECUTION_DRY_RUN.md",
    "docs/REPORT_ONLY_WORKER_RESULT_REVIEW.md",
    "docs/DRY_MVP_LOOP_CLOSEOUT_REVIEW.md",
    "docs/PM_FACING_ORCHESTRATOR_STATUS_PACKET.md",
    "docs/DRY_MVP_LOOP_DEMO_CLI.md",
    "docs/DRY_MVP_INTEGRATED_ACCEPTANCE.md",
    "docs/DRY_MVP_COMMIT_READINESS_REVIEW.md",
    "docs/DRY_MVP_MILESTONE_CLOSEOUT.md",
)

VALIDATION_COMMANDS = (
    "python -B -m unittest tests.test_roger_provided_human_override_seed_calibration_packet "
    "tests.test_goal_intake_to_bounded_task_packet tests.test_bounded_task_packet_review_gate "
    "tests.test_approved_bounded_task_packet_to_queued_task "
    "tests.test_queued_task_execution_authorization_review "
    "tests.test_report_only_worker_execution_dry_run tests.test_report_only_worker_result_review "
    "tests.test_dry_mvp_loop_closeout_review tests.test_pm_facing_orchestrator_status_packet "
    "tests.test_dry_mvp_loop_demo_cli tests.test_dry_mvp_integrated_acceptance "
    "tests.test_dry_mvp_commit_readiness_review tests.test_dry_mvp_milestone_closeout",
    "python -B -m compileall orchestrator",
    "git diff --check",
    "run integrated acceptance with a caller-supplied temporary output directory",
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
    "phase_387_implemented": False,
    "first_product_wedge_selected": False,
    "commit_performed": False,
    "push_performed": False,
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _expected_file_inventory(project_root: str | Path | None) -> dict[str, Any]:
    if project_root is None:
        return {
            "project_root": "",
            "checked": False,
            "expected_file_count": len(EXPECTED_MVP_FILES),
            "present_files": [],
            "missing_files": [],
        }
    root = Path(project_root)
    present: list[str] = []
    missing: list[str] = []
    for relative_path in EXPECTED_MVP_FILES:
        if (root / relative_path).is_file():
            present.append(relative_path)
        else:
            missing.append(relative_path)
    return {
        "project_root": str(root),
        "checked": True,
        "expected_file_count": len(EXPECTED_MVP_FILES),
        "present_files": present,
        "missing_files": missing,
    }


def _readiness_findings(
    acceptance_packet: dict[str, Any],
    expected_file_inventory: dict[str, Any],
) -> tuple[str, list[str], list[str], str]:
    blocked: list[str] = []
    missing: list[str] = []

    if _normalize_text(acceptance_packet.get("acceptance_status")) != "dry_mvp_integrated_acceptance_pass":
        blocked.append("integrated_acceptance_not_passed")
    if _normalize_text(acceptance_packet.get("commit_readiness_assessment")) != "ready_for_human_commit_review_not_committed":
        blocked.append("acceptance_packet_not_ready_for_human_commit_review")

    if expected_file_inventory["checked"]:
        missing.extend(expected_file_inventory["missing_files"])
        if expected_file_inventory["missing_files"]:
            blocked.append("expected_mvp_files_missing")

    if blocked or missing:
        return (
            "dry_mvp_not_ready_for_roger_commit_decision",
            sorted(set(blocked)),
            sorted(set(missing)),
            "Repair missing files or acceptance blockers before asking Roger for a commit decision.",
        )

    return (
        "dry_mvp_ready_for_roger_commit_decision",
        [],
        [],
        "Ask Roger whether to commit the deterministic dry MVP skeleton or request targeted repair.",
    )


def build_dry_mvp_commit_readiness_review_dict(
    output_dir: str | Path | None = None,
    project_root: str | Path | None = None,
    acceptance_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    acceptance = acceptance_packet or build_dry_mvp_integrated_acceptance_dict(output_dir=output_dir)
    inventory = _expected_file_inventory(project_root)
    readiness_status, blocked_conditions, missing_requirements, recommended_action = _readiness_findings(
        acceptance,
        inventory,
    )
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": (
            "Record whether the deterministic dry MVP skeleton is ready for Roger's "
            "commit decision after integrated acceptance and file-inventory checks."
        ),
        "source_acceptance_status": _normalize_text(acceptance.get("acceptance_status")),
        "source_commit_readiness_assessment": _normalize_text(
            acceptance.get("commit_readiness_assessment")
        ),
        "readiness_status": readiness_status,
        "blocked_conditions": blocked_conditions,
        "missing_requirements": missing_requirements,
        "recommended_action": recommended_action,
        "expected_file_inventory": inventory,
        "validation_commands": list(VALIDATION_COMMANDS),
        "roger_commit_decision_options": (
            "commit_dry_mvp_skeleton",
            "request_targeted_repair_before_commit",
            "pause_without_commit",
            "authorize_later_local_worker_proof_boundary",
        ),
        "mvp_milestone_assessment": (
            "The source/test/docs dry MVP milestone is structurally present and ready for "
            "Roger's commit decision."
            if readiness_status == "dry_mvp_ready_for_roger_commit_decision"
            else "The dry MVP milestone still has blockers before Roger's commit decision."
        ),
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def render_dry_mvp_commit_readiness_review_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = packet or build_dry_mvp_commit_readiness_review_dict()
    inventory = payload["expected_file_inventory"]
    lines = [
        "# Dry MVP Commit Readiness Review",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Status: `{payload['readiness_status']}`",
        "",
        "## Purpose",
        payload["purpose"],
        "",
        "## MVP Milestone Assessment",
        payload["mvp_milestone_assessment"],
        "",
        "## Source Acceptance",
        f"- Acceptance status: {payload['source_acceptance_status']}",
        f"- Commit readiness assessment: {payload['source_commit_readiness_assessment']}",
        "",
        "## Expected File Inventory",
        f"- Checked: {inventory['checked']}",
        f"- Expected file count: {inventory['expected_file_count']}",
        f"- Present file count: {len(inventory['present_files'])}",
        f"- Missing file count: {len(inventory['missing_files'])}",
        "",
        "## Validation Commands",
        *[f"- `{item}`" for item in payload["validation_commands"]],
        "",
        "## Roger Commit Decision Options",
        *[f"- {item}" for item in payload["roger_commit_decision_options"]],
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
        f"- commit_performed={payload['commit_performed']}",
        f"- push_performed={payload['push_performed']}",
        f"- recommended_next_boundary={payload['recommended_next_boundary']}",
    ]
    return "\n".join(lines)
