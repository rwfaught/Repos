from __future__ import annotations

import json
import shlex
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from orchestrator import artifact_store
from orchestrator.paths import resolve_declared_project_path, validate_record_id
from orchestrator.task_schema import (
    FILESYSTEM_MUTATION_EXECUTION_POLICY,
    Task,
    normalize_execution_policy,
)


PATCH_PROPOSAL_ARTIFACT_TYPE = "patch_proposal"
PATCH_PROPOSAL_SOURCE = "manual_or_model_proposal"
_KNOWN_PROPOSAL_SOURCES = {
    PATCH_PROPOSAL_SOURCE,
    "manual_proposal",
    "model_proposal",
}


def patch_proposal_path(proposal_id: str):
    return artifact_store.artifact_path(
        validate_record_id(proposal_id, label="proposal id")
    )


def _bounded_declared_path(path: Any) -> str:
    normalized = str(path or "").strip()
    resolve_declared_project_path(normalized)
    return normalized


def _path_identity(path: str) -> str:
    return path.replace("\\", "/")


def _normalize_text_list(value: Any, *, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list of strings.")

    normalized = []
    for item in value:
        text = str(item).strip()
        if not text:
            raise ValueError(f"{label} entries must not be empty.")
        normalized.append(text)
    return normalized


def _normalize_proposed_changes(
    proposed_changes: Any,
    *,
    allowed_paths: set[str],
) -> list[dict[str, str]]:
    if not isinstance(proposed_changes, list) or not proposed_changes:
        raise ValueError("proposed_changes must be a non-empty list.")

    normalized = []
    for change in proposed_changes:
        if not isinstance(change, dict):
            raise ValueError("Each proposed change must be an object.")

        path = _bounded_declared_path(change.get("path"))
        if _path_identity(path) not in allowed_paths:
            raise ValueError(
                f"Proposed change path {path!r} is outside task files_in_scope."
            )

        description = str(change.get("description", "")).strip()
        if not description:
            raise ValueError("Each proposed change requires a description.")
        normalized.append({"path": path, "description": description})
    return normalized


def _diff_paths(unified_diff: str) -> set[str]:
    paths: set[str] = set()
    for line in unified_diff.splitlines():
        candidates: list[str] = []
        if line.startswith("diff --git "):
            try:
                parts = shlex.split(line)
            except ValueError as exc:
                raise ValueError("unified_diff contains an invalid diff header.") from exc
            if len(parts) != 4:
                raise ValueError("unified_diff contains an invalid diff --git header.")
            candidates.extend(parts[2:4])
        elif line.startswith("--- ") or line.startswith("+++ "):
            candidate = line[4:].split("\t", 1)[0].strip()
            candidates.append(candidate)

        for candidate in candidates:
            if candidate == "/dev/null":
                continue
            if candidate.startswith(("a/", "b/")):
                candidate = candidate[2:]
            paths.add(_bounded_declared_path(candidate))
    return paths


def create_patch_proposal(
    task: Task,
    *,
    proposed_changes: list[dict[str, str]],
    unified_diff: str | None = None,
    proposed_diff: str | None = None,
    rationale: str,
    risk_notes: list[str] | None = None,
    validation_hints: list[str] | None = None,
    source: str = PATCH_PROPOSAL_SOURCE,
) -> dict[str, Any]:
    policy = normalize_execution_policy(task)
    if policy != FILESYSTEM_MUTATION_EXECUTION_POLICY:
        raise ValueError(
            "Patch proposals require execution_policy='filesystem_mutation'; "
            "report_only tasks are policy-incompatible."
        )
    if task.status == "completed":
        raise ValueError("Patch proposals cannot be created for completed tasks.")
    if not task.files_in_scope:
        raise ValueError(
            "Patch proposals require at least one bounded task file in scope."
        )

    files_in_scope = [_bounded_declared_path(path) for path in task.files_in_scope]
    allowed_paths = {_path_identity(path) for path in files_in_scope}
    changes = _normalize_proposed_changes(
        proposed_changes,
        allowed_paths=allowed_paths,
    )

    diff_text = unified_diff if unified_diff is not None else proposed_diff
    diff_text = str(diff_text or "")
    if not diff_text.strip():
        raise ValueError("A non-empty unified_diff or proposed_diff is required.")
    for diff_path in _diff_paths(diff_text):
        if _path_identity(diff_path) not in allowed_paths:
            raise ValueError(
                f"Diff path {diff_path!r} is outside task files_in_scope."
            )

    rationale_text = str(rationale or "").strip()
    if not rationale_text:
        raise ValueError("rationale must not be empty.")

    source_name = str(source or "").strip()
    if source_name not in _KNOWN_PROPOSAL_SOURCES:
        raise ValueError(f"Unsupported patch proposal source: {source!r}.")

    proposal_id = f"patch_proposal_{uuid4().hex[:8]}"
    proposal = {
        "artifact_type": PATCH_PROPOSAL_ARTIFACT_TYPE,
        "proposal_id": proposal_id,
        "task_id": task.id,
        "run_id": task.run_id or None,
        "execution_policy": policy,
        "files_in_scope": files_in_scope,
        "proposed_changes": changes,
        "proposed_diff": diff_text,
        "unified_diff": diff_text,
        "rationale": rationale_text,
        "risk_notes": _normalize_text_list(risk_notes, label="risk_notes"),
        "validation_hints": _normalize_text_list(
            validation_hints,
            label="validation_hints",
        ),
        "requires_operator_apply": True,
        "applied": False,
        "source": source_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "proposal_status": "awaiting_operator_apply",
        "task_status_at_proposal": task.status,
        "execution_performed": False,
        "provider_executed": False,
        "model_executed": False,
        "runtime_executed": False,
        "completion_proof": False,
        "causal_change_satisfied": False,
    }

    path = patch_proposal_path(proposal_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(proposal, indent=2), encoding="utf-8")
    return proposal


def load_patch_proposal(proposal_id: str) -> dict[str, Any]:
    path = patch_proposal_path(proposal_id)
    proposal = json.loads(path.read_text(encoding="utf-8"))
    if proposal.get("artifact_type") != PATCH_PROPOSAL_ARTIFACT_TYPE:
        raise ValueError("Stored artifact is not a patch proposal.")
    if proposal.get("proposal_id") != proposal_id:
        raise ValueError("Stored proposal id does not match the requested proposal id.")
    return proposal
