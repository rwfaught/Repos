"""Small runtime configuration and durable JSON helpers for the alpha spine."""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = 1


def validate_record_schema(value: dict[str, Any], *, record_type: str) -> None:
    """Reject explicitly versioned records from unsupported schemas.

    Unversioned records remain readable as legacy inputs; every record written
    by the canonical alpha path is versioned.
    """
    if "schema_version" not in value:
        return
    version = value.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ValueError(f"Unsupported {record_type} schema_version: {version}.")


def load_json_record(path: Path, *, record_type: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{record_type} record must be a JSON object.")
    validate_record_schema(value, record_type=record_type)
    return value


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    """Write one JSON record atomically in the record's own directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def isolated_data_root(data_root: str | Path | None) -> Iterator[Path | None]:
    """Temporarily redirect the canonical spine's JSON stores to ``data_root``."""
    if data_root is None:
        yield None
        return

    root = Path(data_root).resolve()
    import orchestrator.artifact_store as artifact_store
    import orchestrator.current_success_acceptance as acceptance
    import orchestrator.current_success_result_review as review
    import orchestrator.engine as engine
    import orchestrator.execution_authorization as authorization
    import orchestrator.operator_packet_result_decision as operator_decision
    import orchestrator.paths as paths
    import orchestrator.run_manager as run_manager
    import orchestrator.state as state

    replacements = {
        (paths, "PROJECT_ROOT"): root.parent,
        (paths, "DATA_DIR"): root,
        (paths, "STATE_DIR"): root / "state",
        (paths, "RUNS_DIR"): root / "runs",
        (paths, "TASKS_DIR"): root / "tasks",
        (paths, "ARTIFACTS_DIR"): root / "artifacts",
        (paths, "VERIFIER_RESULTS_DIR"): root / "verifier_results",
        (state, "STATE_PATH"): root / "state" / "workspace_state.json",
        (run_manager, "RUNS_DIR"): root / "runs",
        (run_manager, "TASKS_DIR"): root / "tasks",
        (artifact_store, "ARTIFACTS_DIR"): root / "artifacts",
        (engine, "VERIFIER_RESULTS_DIR"): root / "verifier_results",
        (authorization, "AUTHORIZATION_RECORDS_DIR"): root / "execution_authorizations",
        (operator_decision, "PACKET_OPERATOR_DECISION_RECORDS_DIR"): root / "packet_operator_decision_records",
        (review, "DATA_DIR"): root,
        (review, "ARTIFACTS_DIR"): root / "artifacts",
        (review, "VERIFIER_RESULTS_DIR"): root / "verifier_results",
        (review, "ACCEPTANCE_RECORDS_DIR"): root / "acceptance_records",
        (review, "PACKET_OPERATOR_DECISION_RECORDS_DIR"): root / "packet_operator_decision_records",
        (acceptance, "DATA_DIR"): root,
        (acceptance, "ACCEPTANCE_RECORDS_DIR"): root / "acceptance_records",
    }
    originals = {(module, name): getattr(module, name) for module, name in replacements}
    try:
        for (module, name), value in replacements.items():
            setattr(module, name, value)
        yield root
    finally:
        for (module, name), value in originals.items():
            setattr(module, name, value)


def reconcile_lifecycle(data_root: str | Path) -> dict[str, Any]:
    """Read-only partial-lifecycle and identity-link detector for alpha records."""
    root = Path(data_root).resolve()
    runs = root / "runs"
    tasks = root / "tasks"
    artifacts = root / "artifacts"
    verifiers = root / "verifier_results"
    authorizations = root / "execution_authorizations"
    acceptances = root / "acceptance_records"
    decisions = root / "packet_operator_decision_records"
    findings: list[dict[str, str]] = []

    def add(task_id: str, classification: str, path: Path | None = None) -> None:
        finding = {"task_id": task_id, "classification": classification}
        if path is not None:
            finding["path"] = str(path)
        findings.append(finding)

    def read(path: Path, record_type: str, task_id: str) -> dict[str, Any] | None:
        try:
            return load_json_record(path, record_type=record_type)
        except json.JSONDecodeError:
            add(task_id, f"invalid_{record_type}_json", path)
        except (OSError, ValueError) as error:
            classification = (
                "unsupported_schema_version"
                if "Unsupported" in str(error) and "schema_version" in str(error)
                else f"invalid_{record_type}_record"
            )
            add(task_id, classification, path)
        return None

    for task_path in sorted(tasks.glob("*.json")) if tasks.exists() else []:
        try:
            task = load_json_record(task_path, record_type="task")
        except json.JSONDecodeError:
            findings.append({"task_path": str(task_path), "classification": "invalid_task_json"})
            continue
        except (OSError, ValueError) as error:
            classification = (
                "unsupported_schema_version"
                if "Unsupported" in str(error) and "schema_version" in str(error)
                else "invalid_task_record"
            )
            findings.append({"task_path": str(task_path), "classification": classification})
            continue
        task_id = str(task.get("id", ""))
        run_id = str(task.get("run_id", ""))
        artifact_id = str(task.get("execution_artifact_id", ""))
        if task.get("status") == "in_progress":
            add(task_id, "in_progress_requires_recovery")

        authorization_link = task.get("execution_authorization_provenance")
        authorization_id = str(authorization_link.get("authorization_id", "")) if isinstance(authorization_link, dict) else ""
        authorization: dict[str, Any] | None = None
        if not authorization_id:
            add(task_id, "missing_authorization_link")
        else:
            authorization_path = authorizations / f"{authorization_id}.json"
            if not authorization_path.exists():
                add(task_id, "missing_authorization_record", authorization_path)
            else:
                authorization = read(authorization_path, "authorization", task_id)
                if authorization is not None and (
                    str(authorization.get("task_id", "")) != task_id
                    or list(authorization.get("authorized_scope", [])) != list(task.get("files_in_scope", []))
                    or authorization.get("decision") != "authorized"
                ):
                    add(task_id, "authorization_identity_or_scope_mismatch", authorization_path)
                if (
                    task.get("execution_policy") == "filesystem_mutation"
                    and authorization is not None
                    and str(authorization.get("task_id", "")) != task_id
                ):
                    add(task_id, "worker_task_id_mismatch", authorization_path)

        run: dict[str, Any] | None = None
        run_path = runs / f"{run_id}.json" if run_id else None
        if task.get("execution_policy") == "filesystem_mutation":
            if run_path is None:
                add(task_id, "missing_run_record")
            elif not run_path.exists():
                add(task_id, "missing_run_record", run_path)
            else:
                run = read(run_path, "run", task_id)
                if run is not None and str(run.get("id", "")) != run_id:
                    add(task_id, "worker_run_id_mismatch", run_path)

        worker_security = task.get("worker_security") if isinstance(task.get("worker_security"), dict) else {}
        if task.get("execution_policy") == "filesystem_mutation":
            if worker_security.get("trust_posture") != "trusted_local_unsandboxed":
                add(task_id, "missing_or_inconsistent_worker_trust_posture")
            if not str(worker_security.get("workspace_id", "")).strip() or not str(worker_security.get("workspace_path", "")).strip():
                add(task_id, "missing_worker_workspace_identity")
            if worker_security.get("launch_attempted") is True:
                if not isinstance(worker_security.get("workspace_effect_audit"), dict):
                    add(task_id, "missing_workspace_effect_audit")
                if worker_security.get("cleanup_status") not in {"not_required", "confirmed"}:
                    add(task_id, "incomplete_worker_cleanup_status")

        artifact: dict[str, Any] | None = None
        artifact_path = artifacts / f"{artifact_id}.json" if artifact_id else None
        if artifact_id and artifact_path is not None and not artifact_path.exists():
            add(task_id, "missing_artifact", artifact_path)
        elif artifact_path is not None:
            artifact = read(artifact_path, "artifact", task_id)
            if artifact is not None and (
                str(artifact.get("artifact_id", "")) != artifact_id
                or str(artifact.get("task_id", "")) != task_id
                or str(artifact.get("run_id", "")) != run_id
            ):
                add(task_id, "artifact_identity_mismatch", artifact_path)
            if artifact is not None and task.get("execution_policy") == "filesystem_mutation":
                if str(artifact.get("artifact_id", "")) != artifact_id:
                    add(task_id, "worker_artifact_linkage_mismatch", artifact_path)
                if str(artifact.get("task_id", "")) != task_id:
                    add(task_id, "worker_task_id_mismatch", artifact_path)
                if str(artifact.get("run_id", "")) != run_id:
                    add(task_id, "worker_run_id_mismatch", artifact_path)

        if task.get("execution_policy") == "filesystem_mutation":
            records: list[tuple[str, dict[str, Any] | None, Path | None]] = [
                ("task", worker_security, task_path),
                ("run", run.get("worker_security") if isinstance(run, dict) else None, run_path),
            ]
            if artifact is not None:
                records.append(("artifact", artifact.get("worker_security") if isinstance(artifact.get("worker_security"), dict) else None, artifact_path))

            security_values: dict[str, dict[str, str]] = {}
            for label, security, path in records:
                if not isinstance(security, dict):
                    add(task_id, "missing_worker_security_metadata", path)
                    continue
                posture = str(security.get("trust_posture", "")).strip()
                workspace_id = str(security.get("workspace_id", "")).strip()
                workspace_path = str(security.get("workspace_path", "")).strip()
                if not posture or not workspace_id or not workspace_path:
                    add(task_id, "missing_worker_security_metadata", path)
                    continue
                security_values[label] = {
                    "trust_posture": posture,
                    "workspace_id": workspace_id,
                    "workspace_path": workspace_path,
                }

            task_authorization = authorization_link if isinstance(authorization_link, dict) else {}
            posture_values = [
                str((authorization or {}).get("worker_trust_posture", "")).strip(),
                str(task_authorization.get("worker_trust_posture", "")).strip(),
                *(value["trust_posture"] for value in security_values.values()),
            ]
            if not all(posture_values):
                add(task_id, "missing_worker_security_metadata")
            elif len(set(posture_values)) != 1:
                add(task_id, "worker_trust_posture_mismatch")

            workspace_ids = [value["workspace_id"] for value in security_values.values()]
            workspace_paths = [value["workspace_path"] for value in security_values.values()]
            if len(workspace_ids) > 1 and len(set(workspace_ids)) != 1:
                add(task_id, "worker_workspace_id_mismatch")
            if len(workspace_paths) > 1 and len(set(workspace_paths)) != 1:
                add(task_id, "worker_workspace_path_mismatch")

            linked_authorization_ids = [authorization_id]
            if authorization is not None:
                linked_authorization_ids.append(str(authorization.get("authorization_id", "")).strip())
            if artifact is not None:
                linked_authorization_ids.append(str(artifact.get("authorization_id", "")).strip())
            if not all(linked_authorization_ids):
                add(task_id, "missing_authorization_link")
            elif len(set(linked_authorization_ids)) != 1:
                add(task_id, "worker_authorization_id_mismatch")

        verifier_paths = sorted(verifiers.glob(f"{task_id}_*.json")) if verifiers.exists() else []
        if artifact_id and not verifier_paths:
            add(task_id, "missing_verifier_result")
        elif verifier_paths:
            verifier_path = verifier_paths[-1]
            verifier = read(verifier_path, "verifier", task_id)
            if verifier is not None and (
                str(verifier.get("task_id", "")) != task_id
                or str(verifier.get("run_id", "")) != run_id
                or str(verifier.get("execution_artifact_id", "")) != artifact_id
            ):
                add(task_id, "verifier_identity_mismatch", verifier_path)
            if verifier is not None and task.get("execution_policy") == "filesystem_mutation":
                if str(verifier.get("task_id", "")) != task_id:
                    add(task_id, "worker_task_id_mismatch", verifier_path)
                if str(verifier.get("run_id", "")) != run_id:
                    add(task_id, "worker_run_id_mismatch", verifier_path)
                if str(verifier.get("execution_artifact_id", "")) != artifact_id:
                    add(task_id, "worker_artifact_linkage_mismatch", verifier_path)
            if (
                task.get("execution_policy") == "filesystem_mutation"
                and verifier is not None
                and str(verifier.get("authorization_id", "")).strip()
                and str(verifier.get("authorization_id", "")).strip() != authorization_id
            ):
                add(task_id, "worker_authorization_id_mismatch", verifier_path)

        disposition_records: list[tuple[Path, str]] = []
        disposition_records.extend((path, "acceptance") for path in acceptances.glob("*.json") if acceptances.exists())
        disposition_records.extend((path, "operator_decision") for path in decisions.glob("*.json") if decisions.exists())
        dispositions = []
        for disposition_path, record_type in disposition_records:
            disposition = read(disposition_path, record_type, task_id)
            if disposition is not None and str(disposition.get("task_id", "")) == task_id:
                dispositions.append(disposition)
                if (
                    str(disposition.get("run_id", "")) != run_id
                    or str(disposition.get("execution_artifact_id", "")) != artifact_id
                ):
                    add(task_id, "human_disposition_identity_mismatch", disposition_path)
                if task.get("execution_policy") == "filesystem_mutation":
                    if str(disposition.get("run_id", "")) != run_id:
                        add(task_id, "worker_run_id_mismatch", disposition_path)
                    if str(disposition.get("execution_artifact_id", "")) != artifact_id:
                        add(task_id, "worker_artifact_linkage_mismatch", disposition_path)
                if (
                    task.get("execution_policy") == "filesystem_mutation"
                    and str(disposition.get("authorization_id", "")).strip()
                    and str(disposition.get("authorization_id", "")).strip() != authorization_id
                ):
                    add(task_id, "worker_authorization_id_mismatch", disposition_path)
        if task.get("status") == "completed" and not dispositions:
            add(task_id, "missing_human_disposition")

    return {
        "schema_version": SCHEMA_VERSION,
        "alpha_reconciliation": True,
        "data_root": str(root),
        "findings": findings,
        "healthy": not findings,
    }
