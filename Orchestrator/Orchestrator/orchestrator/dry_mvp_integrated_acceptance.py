from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.dry_mvp_loop_demo import run_dry_mvp_loop_demo


BOUNDARY = "DRY_MVP_INTEGRATED_ACCEPTANCE_SOURCE_TEST_DOCS"
PACKET_NAME = "dry_mvp_integrated_acceptance"
RECOMMENDED_NEXT_BOUNDARY = "DRY_MVP_COMMIT_READINESS_REVIEW_SOURCE_TEST_DOCS"

EXPECTED_STAGE_STATUSES = {
    "demo_status": "dry_mvp_demo_pass",
    "task_creation": "created",
    "queued_task_review": "ready_for_operator_execution_authorization_review",
    "dry_run": "created",
    "result_review": "accepted_as_dry_loop_artifact",
    "closeout": "dry_mvp_loop_closeout_pass",
    "pm_status": "dry_mvp_loop_structurally_present",
}

REQUIRED_NON_PROOFS = (
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


def _path_is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _stage_statuses(demo_result: dict[str, Any]) -> dict[str, str]:
    return {
        "demo_status": _normalize_text(demo_result.get("demo_status")),
        "task_creation": _normalize_text(
            demo_result.get("task_creation", {}).get("task_creation_status")
            if isinstance(demo_result.get("task_creation"), dict)
            else ""
        ),
        "queued_task_review": _normalize_text(
            demo_result.get("queued_task_review", {}).get("review_decision")
            if isinstance(demo_result.get("queued_task_review"), dict)
            else ""
        ),
        "dry_run": _normalize_text(
            demo_result.get("dry_run", {}).get("dry_run_status")
            if isinstance(demo_result.get("dry_run"), dict)
            else ""
        ),
        "result_review": _normalize_text(
            demo_result.get("result_review", {}).get("review_decision")
            if isinstance(demo_result.get("result_review"), dict)
            else ""
        ),
        "closeout": _normalize_text(
            demo_result.get("closeout", {}).get("closeout_decision")
            if isinstance(demo_result.get("closeout"), dict)
            else ""
        ),
        "pm_status": _normalize_text(
            demo_result.get("pm_status", {}).get("overall_status")
            if isinstance(demo_result.get("pm_status"), dict)
            else ""
        ),
    }


def _artifact_inventory(demo_result: dict[str, Any]) -> dict[str, Any]:
    output_dir_text = _normalize_text(demo_result.get("output_dir"))
    task_store_text = _normalize_text(demo_result.get("task_store_dir"))
    artifact_store_text = _normalize_text(demo_result.get("artifact_store_dir"))
    if not output_dir_text:
        return {
            "output_dir": "",
            "task_store_dir": task_store_text,
            "artifact_store_dir": artifact_store_text,
            "json_files": [],
            "json_file_count": 0,
            "paths_under_output_dir": False,
            "has_task_json": False,
            "has_artifact_json": False,
        }

    output_dir = Path(output_dir_text)
    files = sorted(str(path) for path in output_dir.rglob("*.json")) if output_dir.exists() else []
    file_paths = [Path(path) for path in files]
    return {
        "output_dir": str(output_dir),
        "task_store_dir": task_store_text,
        "artifact_store_dir": artifact_store_text,
        "json_files": files,
        "json_file_count": len(files),
        "paths_under_output_dir": all(_path_is_under(path, output_dir) for path in file_paths),
        "has_task_json": any(path.parent.name == "tasks" for path in file_paths),
        "has_artifact_json": any(path.parent.name == "artifacts" for path in file_paths),
    }


def _false_flag_failures(demo_result: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    packets = (
        demo_result,
        demo_result.get("closeout") if isinstance(demo_result.get("closeout"), dict) else {},
        demo_result.get("pm_status") if isinstance(demo_result.get("pm_status"), dict) else {},
        demo_result.get("dry_run") if isinstance(demo_result.get("dry_run"), dict) else {},
    )
    for packet in packets:
        for key, expected in FALSE_FLAGS.items():
            if key in packet and packet[key] is not expected:
                failures.append(f"{key}_not_false")
    return sorted(set(failures))


def _missing_non_proofs(demo_result: dict[str, Any]) -> list[str]:
    visible = set()
    for packet in (
        demo_result,
        demo_result.get("closeout") if isinstance(demo_result.get("closeout"), dict) else {},
        demo_result.get("pm_status") if isinstance(demo_result.get("pm_status"), dict) else {},
        demo_result.get("dry_run") if isinstance(demo_result.get("dry_run"), dict) else {},
    ):
        values = packet.get("non_proofs", packet.get("explicit_non_proofs", ()))
        if isinstance(values, (list, tuple)):
            visible.update(_normalize_text(value) for value in values)
    return [item for item in REQUIRED_NON_PROOFS if item not in visible]


def _acceptance_findings(demo_result: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    blocked_conditions: list[str] = []
    missing_requirements: list[str] = []
    invariants_checked: list[str] = []

    statuses = _stage_statuses(demo_result)
    for key, expected in EXPECTED_STAGE_STATUSES.items():
        invariants_checked.append(f"{key}_equals_{expected}")
        if statuses.get(key) != expected:
            blocked_conditions.append(f"{key}_not_{expected}")

    inventory = _artifact_inventory(demo_result)
    invariants_checked.extend(
        (
            "exactly_two_json_artifacts_present",
            "json_artifacts_under_caller_supplied_output_dir",
            "task_json_present",
            "dry_result_artifact_json_present",
        )
    )
    if inventory["json_file_count"] != 2:
        blocked_conditions.append("expected_exactly_two_json_artifacts")
    if not inventory["paths_under_output_dir"]:
        blocked_conditions.append("json_artifact_path_outside_output_dir")
    if not inventory["has_task_json"]:
        missing_requirements.append("task_json_artifact")
    if not inventory["has_artifact_json"]:
        missing_requirements.append("dry_result_artifact_json")

    invariants_checked.append("required_non_proofs_visible")
    missing_requirements.extend(_missing_non_proofs(demo_result))

    invariants_checked.append("false_posture_flags_remain_false")
    blocked_conditions.extend(_false_flag_failures(demo_result))

    return sorted(set(blocked_conditions)), sorted(set(missing_requirements)), invariants_checked


def build_dry_mvp_integrated_acceptance_dict(
    output_dir: str | Path | None = None,
    demo_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if demo_result is None and output_dir is None:
        blocked_conditions = ["output_dir_or_demo_result_required"]
        missing_requirements = ["caller_supplied_output_dir_or_demo_result"]
        demo = {}
        invariants_checked: list[str] = []
    else:
        demo = demo_result if demo_result is not None else run_dry_mvp_loop_demo(output_dir or "")
        blocked_conditions, missing_requirements, invariants_checked = _acceptance_findings(demo)

    acceptance_status = (
        "dry_mvp_integrated_acceptance_pass"
        if not blocked_conditions and not missing_requirements
        else "dry_mvp_integrated_acceptance_blocked"
    )
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": (
            "Give Roger one deterministic acceptance surface for the dry MVP loop: "
            "what ran, what artifacts were produced, what was verified, and what remains unproven."
        ),
        "acceptance_status": acceptance_status,
        "stage_statuses": _stage_statuses(demo),
        "artifact_inventory": _artifact_inventory(demo),
        "invariants_checked": invariants_checked,
        "blocked_conditions": blocked_conditions,
        "missing_requirements": missing_requirements,
        "commit_readiness_assessment": (
            "ready_for_human_commit_review_not_committed"
            if acceptance_status == "dry_mvp_integrated_acceptance_pass"
            else "not_ready_for_commit_review_until_blockers_are_repaired"
        ),
        "explicit_non_proofs": list(REQUIRED_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def render_dry_mvp_integrated_acceptance_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = packet or build_dry_mvp_integrated_acceptance_dict()
    inventory = payload["artifact_inventory"]
    lines = [
        "# Dry MVP Integrated Acceptance",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Status: `{payload['acceptance_status']}`",
        f"Commit readiness: `{payload['commit_readiness_assessment']}`",
        "",
        "## Purpose",
        payload["purpose"],
        "",
        "## Stage Statuses",
        *[f"- {key}: {value}" for key, value in payload["stage_statuses"].items()],
        "",
        "## Artifact Inventory",
        f"- Output dir: {inventory['output_dir']}",
        f"- JSON file count: {inventory['json_file_count']}",
        f"- Paths under output dir: {inventory['paths_under_output_dir']}",
        f"- Has task JSON: {inventory['has_task_json']}",
        f"- Has dry-result artifact JSON: {inventory['has_artifact_json']}",
        "",
        "## Invariants Checked",
        *[f"- {item}" for item in payload["invariants_checked"]],
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
