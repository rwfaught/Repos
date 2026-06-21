from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from orchestrator import artifact_store
from orchestrator.patch_apply_authorization import (
    AUTHORIZE_APPLY_DECISION,
    PATCH_APPLY_AUTHORIZATION_ARTIFACT_TYPE,
    load_patch_apply_authorization,
)
from orchestrator.patch_proposal import (
    PATCH_PROPOSAL_ARTIFACT_TYPE,
    load_patch_proposal,
)
from orchestrator.paths import resolve_declared_project_path, validate_record_id
from orchestrator.task_schema import FILESYSTEM_MUTATION_EXECUTION_POLICY


PATCH_APPLY_RESULT_ARTIFACT_TYPE = "patch_apply_result"
PATCH_APPLY_RESULT_SOURCE = "bounded_operator_authorized_patch_apply"


def patch_apply_result_path(apply_id: str):
    return artifact_store.artifact_path(validate_record_id(apply_id, label="apply id"))


def _path_identity(path: str) -> str:
    return path.replace("\\", "/")


def _bounded_paths(raw_paths: Any, *, label: str) -> list[str]:
    if not isinstance(raw_paths, list) or not raw_paths:
        raise ValueError(f"{label} must be a non-empty list.")

    paths: list[str] = []
    for raw_path in raw_paths:
        path = str(raw_path or "").strip()
        resolve_declared_project_path(path)
        paths.append(path)
    return paths


def _validate_proposal(proposal: dict[str, Any], proposal_id: str) -> list[str]:
    if proposal.get("artifact_type") != PATCH_PROPOSAL_ARTIFACT_TYPE:
        raise ValueError("Stored artifact is not a patch proposal.")
    if proposal.get("proposal_id") != proposal_id:
        raise ValueError("Patch proposal identity does not match the apply request.")
    if proposal.get("execution_policy") != FILESYSTEM_MUTATION_EXECUTION_POLICY:
        raise ValueError(
            "Patch apply requires execution_policy='filesystem_mutation'; "
            "report_only proposals are policy-incompatible."
        )
    if proposal.get("applied") is not False:
        raise ValueError("Patch apply requires an unapplied proposal.")
    if proposal.get("requires_operator_apply") is not True:
        raise ValueError("Patch proposal does not require operator apply.")
    if not str(proposal.get("task_id") or "").strip():
        raise ValueError("Patch proposal requires a task_id.")
    return _bounded_paths(proposal.get("files_in_scope"), label="proposal files_in_scope")


def _validate_authorization(
    authorization: dict[str, Any],
    authorization_id: str,
    proposal: dict[str, Any],
) -> list[str]:
    if authorization.get("artifact_type") != PATCH_APPLY_AUTHORIZATION_ARTIFACT_TYPE:
        raise ValueError("Stored artifact is not a patch apply authorization.")
    if authorization.get("authorization_id") != authorization_id:
        raise ValueError("Authorization identity does not match the apply request.")
    if authorization.get("proposal_id") != proposal["proposal_id"]:
        raise ValueError("Authorization does not reference the requested proposal.")
    if authorization.get("task_id") != proposal["task_id"]:
        raise ValueError("Authorization task_id does not match the proposal.")
    if authorization.get("execution_policy") != FILESYSTEM_MUTATION_EXECUTION_POLICY:
        raise ValueError("Authorization is not for filesystem mutation.")
    if authorization.get("operator_decision") != AUTHORIZE_APPLY_DECISION:
        raise ValueError("Patch apply requires operator_decision='authorize_apply'.")
    if authorization.get("requires_separate_apply_boundary") is not True:
        raise ValueError("Authorization does not require a separate apply boundary.")
    if authorization.get("applied") is not False:
        raise ValueError("Patch apply requires an unapplied authorization.")
    return _bounded_paths(
        authorization.get("files_authorized"),
        label="authorization files_authorized",
    )


def _normalize_operations(
    operations: Any,
    *,
    proposal_files: set[str],
    authorized_files: set[str],
) -> list[dict[str, str]]:
    if not isinstance(operations, list) or not operations:
        raise ValueError("operations must be a non-empty list.")

    normalized: list[dict[str, str]] = []
    operation_ids: set[str] = set()
    for operation in operations:
        if not isinstance(operation, dict):
            raise ValueError("Each patch operation must be an object.")

        operation_id = validate_record_id(
            operation.get("operation_id"),
            label="operation id",
        )
        if operation_id in operation_ids:
            raise ValueError(f"Duplicate operation id: {operation_id!r}.")
        operation_ids.add(operation_id)

        file_path = str(operation.get("file_path") or "").strip()
        resolve_declared_project_path(file_path)
        identity = _path_identity(file_path)
        if identity not in proposal_files:
            raise ValueError(
                f"Operation file {file_path!r} is outside proposal files_in_scope."
            )
        if identity not in authorized_files:
            raise ValueError(
                f"Operation file {file_path!r} is outside authorization "
                "files_authorized."
            )

        expected_before = operation.get("expected_before")
        replacement_after = operation.get("replacement_after")
        if not isinstance(expected_before, str) or not expected_before:
            raise ValueError("expected_before must be a non-empty string.")
        if not isinstance(replacement_after, str):
            raise ValueError("replacement_after must be a string.")

        normalized.append(
            {
                "operation_id": operation_id,
                "file_path": file_path,
                "expected_before": expected_before,
                "replacement_after": replacement_after,
                "description": str(operation.get("description") or "").strip(),
            }
        )
    return normalized


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def apply_authorized_patch(
    authorization_id: str,
    *,
    operations: list[dict[str, str]],
) -> dict[str, Any]:
    safe_authorization_id = validate_record_id(
        authorization_id,
        label="authorization id",
    )
    authorization = load_patch_apply_authorization(safe_authorization_id)

    proposal_id = validate_record_id(
        authorization.get("proposal_id"),
        label="proposal id",
    )
    proposal = load_patch_proposal(proposal_id)
    proposal_paths = _validate_proposal(proposal, proposal_id)
    authorized_paths = _validate_authorization(
        authorization,
        safe_authorization_id,
        proposal,
    )

    normalized_operations = _normalize_operations(
        operations,
        proposal_files={_path_identity(path) for path in proposal_paths},
        authorized_files={_path_identity(path) for path in authorized_paths},
    )

    staged_text: dict[str, str] = {}
    original_text: dict[str, str] = {}
    resolved_paths = {}
    operations_applied: list[dict[str, str]] = []
    for operation in normalized_operations:
        file_path = operation["file_path"]
        identity = _path_identity(file_path)
        resolved = resolve_declared_project_path(file_path)
        if not resolved.is_file():
            raise ValueError(f"Patch target {file_path!r} must be an existing file.")

        if identity not in staged_text:
            text = resolved.read_text(encoding="utf-8")
            original_text[identity] = text
            staged_text[identity] = text
            resolved_paths[identity] = resolved

        match_count = staged_text[identity].count(operation["expected_before"])
        if match_count != 1:
            raise ValueError(
                f"Operation {operation['operation_id']!r} expected_before must "
                f"appear exactly once; found {match_count} matches."
            )
        staged_text[identity] = staged_text[identity].replace(
            operation["expected_before"],
            operation["replacement_after"],
            1,
        )
        operations_applied.append(
            {
                "operation_id": operation["operation_id"],
                "file_path": file_path,
                "description": operation["description"],
            }
        )

    changed_identities = [
        identity
        for identity, after_text in staged_text.items()
        if after_text != original_text[identity]
    ]
    if not changed_identities:
        raise ValueError("Patch operations produced no causal file change.")

    for identity in changed_identities:
        resolved_paths[identity].write_text(staged_text[identity], encoding="utf-8")

    files_changed = [
        operation["file_path"]
        for operation in normalized_operations
        if _path_identity(operation["file_path"]) in changed_identities
    ]
    files_changed = list(dict.fromkeys(files_changed))
    before_sha256 = {
        path: _sha256_text(original_text[_path_identity(path)])
        for path in files_changed
    }
    after_sha256 = {
        path: _sha256_text(staged_text[_path_identity(path)])
        for path in files_changed
    }
    causal_change_observed = any(
        before_sha256[path] != after_sha256[path] for path in files_changed
    )
    if not causal_change_observed:
        raise RuntimeError("Successful patch write did not produce causal hash evidence.")

    apply_id = f"patch_apply_result_{uuid4().hex[:8]}"
    result = {
        "artifact_type": PATCH_APPLY_RESULT_ARTIFACT_TYPE,
        "apply_id": apply_id,
        "proposal_id": proposal_id,
        "authorization_id": safe_authorization_id,
        "task_id": proposal["task_id"],
        "run_id": proposal.get("run_id") or None,
        "execution_policy": FILESYSTEM_MUTATION_EXECUTION_POLICY,
        "files_changed": files_changed,
        "before_sha256": before_sha256,
        "after_sha256": after_sha256,
        "operations_applied": operations_applied,
        "applied": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requires_verification": True,
        "causal_change_observed": causal_change_observed,
        "source": PATCH_APPLY_RESULT_SOURCE,
        "task_completed": False,
        "verification_satisfied": False,
        "provider_executed": False,
        "model_executed": False,
        "runtime_executed": False,
    }

    path = patch_apply_result_path(apply_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def load_patch_apply_result(apply_id: str) -> dict[str, Any]:
    path = patch_apply_result_path(apply_id)
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("artifact_type") != PATCH_APPLY_RESULT_ARTIFACT_TYPE:
        raise ValueError("Stored artifact is not a patch apply result.")
    if result.get("apply_id") != apply_id:
        raise ValueError("Stored apply id does not match the requested apply id.")
    return result
