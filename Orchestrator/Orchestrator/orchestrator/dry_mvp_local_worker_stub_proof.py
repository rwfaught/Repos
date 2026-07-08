from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BOUNDARY = "DRY_MVP_DETERMINISTIC_LOCAL_WORKER_STUB_PROOF_SOURCE_TEST_DOCS"
PACKET_NAME = "dry_mvp_local_worker_stub_proof"
ARTIFACT_KIND = "dry_mvp_deterministic_local_worker_stub_proof"
WORKER_RESULT_CLASSIFICATION = "deterministic_local_worker_stub_ran_no_external_execution"
RECOMMENDED_NEXT_BOUNDARY = "DRY_MVP_LOCAL_WORKER_STUB_PROOF_REVIEW_READONLY"

EXPLICIT_NON_PROOFS = (
    "no provider/model execution",
    "no local model execution",
    "no runtime/platform execution",
    "no subprocess worker proof",
    "no Codex handoff proof",
    "no file mutation execution proof",
    "no production task execution",
    "no semantic correctness proof",
    "no production readiness proof",
    "no Phase 387 implementation",
    "no product-wedge selection",
)

FALSE_FLAGS = {
    "provider_model_executed": False,
    "local_model_executed": False,
    "runtime_executed": False,
    "platform_executed": False,
    "subprocess_executed": False,
    "codex_dispatched": False,
    "file_mutation_executed": False,
    "production_task_executed": False,
    "semantic_correctness_proven": False,
    "production_readiness_claimed": False,
    "phase_387_implemented": False,
    "product_wedge_selected": False,
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [text for text in (_normalize_text(item) for item in value) if text]


def _task_summary(input_packet: dict[str, Any]) -> dict[str, Any]:
    task = input_packet.get("task")
    if isinstance(task, dict):
        source = task
    else:
        source = input_packet
    return {
        "task_id": _normalize_text(source.get("task_id") or source.get("id")),
        "task_title": _normalize_text(source.get("task_title") or source.get("title")),
        "files_in_scope": _text_list(source.get("files_in_scope")),
    }


def _artifact_id(task: dict[str, Any]) -> str:
    task_id = task["task_id"] or "minimal_input"
    safe = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in task_id)
    return f"local_worker_stub_proof_{safe}"


def _blocked_result(
    *,
    reason: str,
    blocked_conditions: list[str],
    missing_requirements: list[str] | None = None,
    input_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task = _task_summary(input_packet or {}) if isinstance(input_packet, dict) else _task_summary({})
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "proof_status": "blocked",
        "artifact_created": False,
        "artifact_persisted": False,
        "artifact_id": "",
        "artifact_path": "",
        "worker_ran": False,
        "worker_result_classification": "",
        "reason": reason,
        "blocked_conditions": sorted(set(blocked_conditions)),
        "missing_requirements": sorted(set(missing_requirements or [])),
        "input_task_id": task["task_id"],
        "input_task_title": task["task_title"],
        "files_in_scope": task["files_in_scope"],
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }


def _authorization_text(operator_authorization: Any) -> str:
    if isinstance(operator_authorization, dict):
        return _normalize_text(
            operator_authorization.get("authorization_text")
            or operator_authorization.get("authorization_note")
            or operator_authorization.get("note")
        )
    return _normalize_text(operator_authorization)


def _authorization_blocks(operator_authorization: Any) -> tuple[list[str], list[str], str]:
    text = _authorization_text(operator_authorization)
    blocked: list[str] = []
    missing: list[str] = []
    if not text:
        missing.append("operator_local_worker_authorization")
    if isinstance(operator_authorization, dict):
        if operator_authorization.get("authorized") is not True:
            blocked.append("operator_local_worker_authorized_boolean_required")
    elif not text:
        blocked.append("operator_local_worker_authorization_required")
    return blocked, missing, text


def _run_deterministic_local_worker_stub(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "worker_kind": "deterministic_local_worker_stub",
        "worker_ran": True,
        "worker_result_classification": WORKER_RESULT_CLASSIFICATION,
        "worker_output_summary": (
            "Deterministic local-worker stub read the bounded input packet and "
            "produced reviewable proof evidence without external execution."
        ),
        "observed_task_id": task["task_id"],
        "observed_task_title": task["task_title"],
        "observed_files_in_scope": list(task["files_in_scope"]),
    }


def _proof_artifact(
    *,
    input_packet: dict[str, Any],
    operator_authorization_text: str,
) -> dict[str, Any]:
    task = _task_summary(input_packet)
    worker_result = _run_deterministic_local_worker_stub(task)
    return {
        "artifact_id": _artifact_id(task),
        "artifact_kind": ARTIFACT_KIND,
        "boundary": BOUNDARY,
        "packet_name": PACKET_NAME,
        "proof_status": "created",
        "input_task_id": task["task_id"],
        "input_task_title": task["task_title"],
        "files_in_scope": task["files_in_scope"],
        "operator_authorization_text": operator_authorization_text,
        "worker_kind": worker_result["worker_kind"],
        "worker_ran": True,
        "worker_result_classification": WORKER_RESULT_CLASSIFICATION,
        "worker_output_summary": worker_result["worker_output_summary"],
        "worker_result": worker_result,
        "activity_flags": {
            "worker_ran": True,
            **FALSE_FLAGS,
        },
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
    }


def run_dry_mvp_local_worker_stub_proof(
    *,
    input_packet: dict[str, Any] | None = None,
    boundary: str = BOUNDARY,
    operator_authorization: Any = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    if boundary != BOUNDARY:
        return _blocked_result(
            reason="Exact local-worker stub proof boundary is required.",
            blocked_conditions=["boundary_mismatch"],
            missing_requirements=[BOUNDARY],
            input_packet=input_packet,
        )

    if not isinstance(input_packet, dict):
        return _blocked_result(
            reason="Structured input_packet is required for local-worker stub proof.",
            blocked_conditions=["input_packet_required"],
            missing_requirements=["input_packet"],
        )

    task = _task_summary(input_packet)
    if not task["task_id"] or not task["task_title"]:
        missing = []
        if not task["task_id"]:
            missing.append("task_id")
        if not task["task_title"]:
            missing.append("task_title")
        return _blocked_result(
            reason="Input packet must include task id and title.",
            blocked_conditions=["input_packet_missing_required_task_fields"],
            missing_requirements=missing,
            input_packet=input_packet,
        )

    authorization_blocked, authorization_missing, authorization_text = _authorization_blocks(
        operator_authorization
    )
    if authorization_blocked or authorization_missing:
        return _blocked_result(
            reason="Explicit operator/local-worker authorization is required.",
            blocked_conditions=authorization_blocked,
            missing_requirements=authorization_missing,
            input_packet=input_packet,
        )

    if output_dir is None:
        return _blocked_result(
            reason="Caller-supplied output_dir is required for proof artifact persistence.",
            blocked_conditions=["output_dir_required"],
            missing_requirements=["output_dir"],
            input_packet=input_packet,
        )

    artifact = _proof_artifact(
        input_packet=input_packet,
        operator_authorization_text=authorization_text,
    )
    artifact_dir = Path(output_dir)
    artifact_path = artifact_dir / f"{artifact['artifact_id']}.json"
    if artifact_path.exists():
        return _blocked_result(
            reason="Local-worker stub proof artifact already exists.",
            blocked_conditions=["local_worker_stub_proof_artifact_already_exists"],
            missing_requirements=[str(artifact_path)],
            input_packet=input_packet,
        )

    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "proof_status": "created",
        "artifact_created": True,
        "artifact_persisted": True,
        "artifact_id": artifact["artifact_id"],
        "artifact_path": str(artifact_path),
        "artifact": artifact,
        "worker_ran": True,
        "worker_kind": "deterministic_local_worker_stub",
        "worker_result_classification": WORKER_RESULT_CLASSIFICATION,
        "reason": "Created one deterministic local-worker stub proof artifact.",
        "blocked_conditions": [],
        "missing_requirements": [],
        "input_task_id": artifact["input_task_id"],
        "input_task_title": artifact["input_task_title"],
        "files_in_scope": artifact["files_in_scope"],
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        **FALSE_FLAGS,
    }
