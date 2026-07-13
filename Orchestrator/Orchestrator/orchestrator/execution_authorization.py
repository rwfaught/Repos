"""Persisted, domain-neutral execution authorization for the alpha lifecycle."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.alpha_runtime import SCHEMA_VERSION, atomic_write_json
from orchestrator.paths import DATA_DIR, record_path, validate_record_id
from orchestrator.trusted_worker_security import validate_trust_posture
from orchestrator.worker_execution_policy import validate_normalized_worker_execution_policy


AUTHORIZATION_RECORDS_DIR = DATA_DIR / "execution_authorizations"


def validate_execution_authorization(
    authorization: Any,
    *,
    task_id: str,
    files_in_scope: list[str],
) -> str | None:
    """Return a stable block reason when authorization is absent or mismatched."""
    if not isinstance(authorization, dict):
        return "execution_authorization_missing"
    if authorization.get("execution_authorized") is not True or authorization.get("decision") != "authorized":
        return "execution_authorization_denied"
    if str(authorization.get("task_id", "")) != task_id:
        return "execution_authorization_task_mismatch"
    if list(authorization.get("authorized_scope", [])) != list(files_in_scope):
        return "execution_authorization_scope_mismatch"
    if not str(authorization.get("authorization_id", "")).strip():
        return "execution_authorization_identity_missing"
    return None


def persist_execution_authorization(
    packet: dict[str, Any],
    task_id: str,
    files_in_scope: list[str],
    *,
    worker_execution_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    decision = str(packet.get("authorization_decision", "")).strip().lower()
    provenance = str(packet.get("authorization_provenance", "")).strip()
    approved = decision == "authorize_execution" and bool(provenance)
    reason = str(packet.get("authorization_reason", "")).strip()
    record_id = f"authorization_{uuid4().hex[:8]}"
    constraints = packet.get("authorization_constraints", [])
    if not isinstance(constraints, list):
        constraints = []
    trust_posture = str(packet.get("worker_trust_posture", "")).strip()
    posture_error = validate_trust_posture(trust_posture) if packet.get("provider_name") == "subprocess_worker" else None
    policy_error = None
    if worker_execution_policy is not None:
        try:
            worker_execution_policy = validate_normalized_worker_execution_policy(worker_execution_policy)
        except ValueError as error:
            policy_error = str(error)
    if policy_error:
        approved = False
    record = {
        "schema_version": SCHEMA_VERSION,
        "authorization_id": record_id,
        "task_id": validate_record_id(task_id, label="task id"),
        "authorized_scope": list(files_in_scope),
        "decision": "authorized" if approved else "denied",
        "operator_provenance": provenance,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "constraints": [str(item) for item in constraints],
        "denial_reason": "" if approved else (policy_error or reason or "explicit_authorization_required"),
        "worker_trust_posture": trust_posture,
        "worker_trust_posture_valid": posture_error is None,
        "worker_execution_policy": worker_execution_policy or {},
        "worker_execution_policy_valid": policy_error is None,
        "worker_execution_policy_error": policy_error or "",
    }
    path = record_path(AUTHORIZATION_RECORDS_DIR, record_id, label="authorization id")
    atomic_write_json(path, record)
    return {**record, "path": str(path), "execution_authorized": approved}
