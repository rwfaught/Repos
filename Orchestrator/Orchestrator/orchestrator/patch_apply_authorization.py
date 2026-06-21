from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from orchestrator import artifact_store
from orchestrator.patch_proposal import (
    PATCH_PROPOSAL_ARTIFACT_TYPE,
    load_patch_proposal,
)
from orchestrator.paths import resolve_declared_project_path, validate_record_id
from orchestrator.task_schema import FILESYSTEM_MUTATION_EXECUTION_POLICY


PATCH_APPLY_AUTHORIZATION_ARTIFACT_TYPE = "patch_apply_authorization"
PATCH_APPLY_AUTHORIZATION_SOURCE = "operator_apply_authorization"
AUTHORIZE_APPLY_DECISION = "authorize_apply"
REJECT_APPLY_DECISION = "reject_apply"
_KNOWN_OPERATOR_DECISIONS = {
    AUTHORIZE_APPLY_DECISION,
    REJECT_APPLY_DECISION,
}


def patch_apply_authorization_path(authorization_id: str):
    return artifact_store.artifact_path(
        validate_record_id(authorization_id, label="authorization id")
    )


def _bounded_declared_path(path: Any) -> str:
    normalized = str(path or "").strip()
    resolve_declared_project_path(normalized)
    return normalized


def _path_identity(path: str) -> str:
    return path.replace("\\", "/")


def _proposal_files(proposal: dict[str, Any]) -> list[str]:
    raw_files = proposal.get("files_in_scope")
    if not isinstance(raw_files, list) or not raw_files:
        raise ValueError("Patch proposal requires bounded files_in_scope.")
    return [_bounded_declared_path(path) for path in raw_files]


def _validate_proposal(proposal: dict[str, Any], proposal_id: str) -> list[str]:
    if proposal.get("artifact_type") != PATCH_PROPOSAL_ARTIFACT_TYPE:
        raise ValueError("Stored artifact is not a patch proposal.")
    if proposal.get("proposal_id") != proposal_id:
        raise ValueError("Stored proposal id does not match the requested proposal id.")
    if proposal.get("execution_policy") != FILESYSTEM_MUTATION_EXECUTION_POLICY:
        raise ValueError(
            "Patch apply authorization requires "
            "execution_policy='filesystem_mutation'; report_only proposals are "
            "policy-incompatible."
        )
    if proposal.get("applied") is not False:
        raise ValueError("Patch apply authorization requires an unapplied proposal.")
    if proposal.get("requires_operator_apply") is not True:
        raise ValueError("Patch proposal does not require operator apply authorization.")

    task_id = str(proposal.get("task_id") or "").strip()
    if not task_id:
        raise ValueError("Patch proposal requires a task_id.")
    return _proposal_files(proposal)


def _normalize_files_authorized(
    files_authorized: list[str] | None,
    *,
    proposal_files: list[str],
) -> list[str]:
    requested = proposal_files if files_authorized is None else files_authorized
    if not isinstance(requested, list) or not requested:
        raise ValueError("files_authorized must be a non-empty list.")

    allowed = {_path_identity(path) for path in proposal_files}
    normalized: list[str] = []
    seen: set[str] = set()
    for path in requested:
        bounded_path = _bounded_declared_path(path)
        identity = _path_identity(bounded_path)
        if identity not in allowed:
            raise ValueError(
                f"Authorized file {bounded_path!r} is outside proposal files_in_scope."
            )
        if identity not in seen:
            normalized.append(bounded_path)
            seen.add(identity)
    return normalized


def create_patch_apply_authorization(
    proposal_id: str,
    *,
    operator_decision: str,
    operator_label: str,
    decision_reason: str,
    files_authorized: list[str] | None = None,
) -> dict[str, Any]:
    safe_proposal_id = validate_record_id(proposal_id, label="proposal id")
    proposal = load_patch_proposal(safe_proposal_id)
    proposal_files = _validate_proposal(proposal, safe_proposal_id)

    decision = str(operator_decision or "").strip()
    if decision not in _KNOWN_OPERATOR_DECISIONS:
        known = ", ".join(sorted(_KNOWN_OPERATOR_DECISIONS))
        raise ValueError(f"Unknown operator_decision {operator_decision!r}; expected: {known}.")

    operator = str(operator_label or "").strip()
    if not operator:
        raise ValueError("operator_label must not be empty.")
    rationale = str(decision_reason or "").strip()
    if not rationale:
        raise ValueError("decision_reason must not be empty.")

    bounded_files = _normalize_files_authorized(
        files_authorized,
        proposal_files=proposal_files,
    )
    authorization_id = f"patch_apply_authorization_{uuid4().hex[:8]}"
    authorization = {
        "artifact_type": PATCH_APPLY_AUTHORIZATION_ARTIFACT_TYPE,
        "authorization_id": authorization_id,
        "proposal_id": safe_proposal_id,
        "task_id": proposal["task_id"],
        "run_id": proposal.get("run_id") or None,
        "execution_policy": FILESYSTEM_MUTATION_EXECUTION_POLICY,
        "files_authorized": bounded_files,
        "operator_decision": decision,
        "operator_label": operator,
        "decision_reason": rationale,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requires_separate_apply_boundary": True,
        "applied": False,
        "source": PATCH_APPLY_AUTHORIZATION_SOURCE,
        "authorization_status": (
            "authorized_for_future_apply_boundary"
            if decision == AUTHORIZE_APPLY_DECISION
            else "apply_rejected"
        ),
        "execution_performed": False,
        "provider_executed": False,
        "model_executed": False,
        "runtime_executed": False,
        "completion_proof": False,
        "verification_satisfied": False,
        "causal_change_satisfied": False,
    }

    path = patch_apply_authorization_path(authorization_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(authorization, indent=2), encoding="utf-8")
    return authorization


def load_patch_apply_authorization(authorization_id: str) -> dict[str, Any]:
    path = patch_apply_authorization_path(authorization_id)
    authorization = json.loads(path.read_text(encoding="utf-8"))
    if authorization.get("artifact_type") != PATCH_APPLY_AUTHORIZATION_ARTIFACT_TYPE:
        raise ValueError("Stored artifact is not a patch apply authorization.")
    if authorization.get("authorization_id") != authorization_id:
        raise ValueError(
            "Stored authorization id does not match the requested authorization id."
        )
    return authorization
