"""Trusted-local-worker safeguards for the canonical alpha subprocess seam.

This is defense in depth for an operator-selected, trusted local command.  It
does not sandbox the command or claim to observe operating-system effects
outside the per-run workspace.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from orchestrator.paths import validate_record_id


TRUSTED_LOCAL_UNSANDBOXED = "trusted_local_unsandboxed"
SUPPORTED_TRUST_POSTURES = frozenset({TRUSTED_LOCAL_UNSANDBOXED})


class WorkerSecurityError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code


def validate_trust_posture(value: Any) -> str | None:
    posture = str(value or "").strip()
    if not posture:
        return "worker_trust_posture_missing"
    if posture not in SUPPORTED_TRUST_POSTURES:
        return "worker_trust_posture_unsupported"
    return None


def _is_reparse_or_symlink(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
        return bool(attributes & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT
    except OSError as error:
        raise WorkerSecurityError("worker_path_inspection_failed", str(error)) from error


def _declared_parts(declared_path: str) -> tuple[str, ...]:
    raw = str(declared_path or "").strip()
    if not raw:
        raise WorkerSecurityError("worker_declared_path_unsafe", "Declared worker path is required.")
    posix = PurePosixPath(raw)
    windows = PureWindowsPath(raw)
    if posix.is_absolute() or windows.is_absolute() or "\\" in raw:
        raise WorkerSecurityError("worker_declared_path_unsafe", "Declared worker path must be relative POSIX form.")
    if any(part in {"", ".", ".."} for part in posix.parts):
        raise WorkerSecurityError("worker_declared_path_unsafe", "Declared worker path is ambiguous or traverses parents.")
    return tuple(posix.parts)


def _assert_safe_existing_chain(root: Path, parts: tuple[str, ...]) -> Path:
    if _is_reparse_or_symlink(root):
        raise WorkerSecurityError("worker_symlink_reparse_risk", "Worker workspace is a symlink or reparse point.")
    current = root
    for part in parts:
        candidate = current / part
        if candidate.exists() or candidate.is_symlink():
            if _is_reparse_or_symlink(candidate):
                raise WorkerSecurityError(
                    "worker_symlink_reparse_risk",
                    f"Declared worker path crosses a symlink or reparse point: {candidate}.",
                )
            current = candidate
            continue
        current = candidate
    return current


def _expected_parent_paths(declared_paths: list[str]) -> list[str]:
    parents = {
        "/".join(_declared_parts(declared_path)[:-1])
        for declared_path in declared_paths
        if _declared_parts(declared_path)[:-1]
    }
    return sorted(parents, key=lambda value: (len(PurePosixPath(value).parts), value))


def prepare_trusted_worker_workspace(
    data_root: str | Path,
    *,
    task_id: str,
    run_id: str,
    trust_posture: str,
    declared_paths: list[str],
) -> dict[str, Any]:
    """Create a unique non-reparse workspace and safe declared target mappings."""
    posture_error = validate_trust_posture(trust_posture)
    if posture_error:
        raise WorkerSecurityError(posture_error, "Canonical workers require trusted_local_unsandboxed posture.")
    safe_task_id = validate_record_id(task_id, label="task id")
    safe_run_id = validate_record_id(run_id, label="run id")
    root = Path(data_root)
    if root.exists() and _is_reparse_or_symlink(root):
        raise WorkerSecurityError("worker_symlink_reparse_risk", "Canonical data root may not be a symlink or reparse point.")
    workspace = root / "worker_workspaces" / f"{safe_run_id}__{safe_task_id}"
    if workspace.exists() or workspace.is_symlink():
        raise WorkerSecurityError("worker_workspace_creation_failed", "Per-run worker workspace already exists.")
    try:
        workspace.mkdir(parents=True, exist_ok=False)
    except OSError as error:
        raise WorkerSecurityError("worker_workspace_creation_failed", str(error)) from error

    try:
        mappings = []
        for declared_path in declared_paths:
            parts = _declared_parts(declared_path)
            target = _assert_safe_existing_chain(workspace, parts)
            parent = target.parent
            parent.mkdir(parents=True, exist_ok=True)
            _assert_safe_existing_chain(workspace, parts[:-1])
            mappings.append({"declared_path": declared_path, "workspace_path": str(target)})
    except Exception:
        # A partially created disposable workspace is never valid for launch.
        raise
    return {
        "trust_posture": trust_posture,
        "workspace_id": f"workspace_{safe_run_id}_{safe_task_id}",
        "workspace_path": str(workspace),
        "declared_targets": mappings,
        "expected_parent_paths": _expected_parent_paths(declared_paths),
        "launch_attempted": False,
        "cleanup_status": "not_started",
        "containment_claim": "trusted_local_unsandboxed_not_os_sandboxed",
    }


def resolve_workspace_target(worker_security: dict[str, Any], declared_path: str) -> Path:
    workspace_text = str(worker_security.get("workspace_path", "")).strip()
    if not workspace_text:
        raise WorkerSecurityError("worker_workspace_identity_missing", "Worker workspace identity is required.")
    workspace = Path(workspace_text)
    parts = _declared_parts(declared_path)
    target = _assert_safe_existing_chain(workspace, parts)
    if target.parent != workspace and workspace not in target.parents:
        raise WorkerSecurityError("worker_declared_path_unsafe", "Worker target escapes its workspace.")
    return target


def validate_trusted_worker_prelaunch_state(
    worker_security: dict[str, Any],
    declared_paths: list[str],
) -> list[Path]:
    """Fail closed if setup's required directory state changed before launch."""
    workspace_text = str(worker_security.get("workspace_path", "")).strip()
    if not workspace_text:
        raise WorkerSecurityError("worker_prelaunch_path_state_unsafe", "Worker workspace identity is required before launch.")
    workspace = Path(workspace_text)
    expected_parents = _expected_parent_paths(declared_paths)
    persisted_parents = worker_security.get("expected_parent_paths")
    if persisted_parents != expected_parents:
        raise WorkerSecurityError("worker_prelaunch_path_state_unsafe", "Worker parent setup state is missing or inconsistent.")
    try:
        if not workspace.is_dir() or _is_reparse_or_symlink(workspace):
            raise WorkerSecurityError("worker_prelaunch_path_state_unsafe", "Worker workspace is unavailable or unsafe before launch.")
        resolved_workspace = workspace.resolve(strict=True)
        for parent_text in expected_parents:
            parent = workspace.joinpath(*PurePosixPath(parent_text).parts)
            if not parent.exists() or not parent.is_dir() or _is_reparse_or_symlink(parent):
                raise WorkerSecurityError(
                    "worker_prelaunch_path_state_unsafe",
                    f"Expected worker output parent is unavailable or unsafe: {parent}.",
                )
            parent.resolve(strict=True).relative_to(resolved_workspace)
        targets = [resolve_workspace_target(worker_security, declared_path) for declared_path in declared_paths]
        for target in targets:
            target.parent.resolve(strict=True).relative_to(resolved_workspace)
        return targets
    except WorkerSecurityError:
        raise
    except (OSError, RuntimeError, ValueError) as error:
        raise WorkerSecurityError("worker_prelaunch_path_state_unsafe", str(error)) from error


def inventory_workspace(workspace: str | Path) -> dict[str, dict[str, Any]]:
    root = Path(workspace)
    if not root.is_dir() or _is_reparse_or_symlink(root):
        raise WorkerSecurityError("worker_workspace_creation_failed", "Worker workspace is unavailable or unsafe.")
    inventory: dict[str, dict[str, Any]] = {}
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(directory)
        for name in sorted(dirnames + filenames):
            path = current / name
            relative = path.relative_to(root).as_posix()
            if _is_reparse_or_symlink(path):
                inventory[relative] = {"object_type": "symlink_or_reparse", "size": None, "sha256": None}
            elif path.is_dir():
                inventory[relative] = {"object_type": "directory", "size": None, "sha256": None}
            elif path.is_file():
                digest = hashlib.sha256()
                with path.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(65536), b""):
                        digest.update(chunk)
                inventory[relative] = {"object_type": "file", "size": path.stat().st_size, "sha256": digest.hexdigest()}
            else:
                inventory[relative] = {"object_type": "other", "size": None, "sha256": None}
    return inventory


def audit_workspace_effects(
    before: dict[str, dict[str, Any]],
    after: dict[str, dict[str, Any]],
    declared_paths: list[str],
) -> dict[str, Any]:
    declared = {"/".join(_declared_parts(path)) for path in declared_paths}
    created = sorted(set(after) - set(before))
    deleted = sorted(set(before) - set(after))
    modified = sorted(path for path in set(before) & set(after) if before[path] != after[path])
    changed = sorted(set(created + deleted + modified))
    undeclared = sorted(path for path in changed if path not in declared)
    return {
        "audit_version": 1,
        "declared_paths": sorted(declared),
        "created": created,
        "deleted": deleted,
        "modified_or_type_changed": modified,
        "undeclared_changes": undeclared,
        "passed": not undeclared,
        "scope_note": "Audits only the controlled workspace; it does not detect effects outside it.",
    }
