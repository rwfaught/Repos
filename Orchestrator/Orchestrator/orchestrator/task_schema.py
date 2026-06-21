from dataclasses import dataclass
from typing import Any, Dict, List


REPORT_ONLY_EXECUTION_POLICY = "report_only"
FILESYSTEM_MUTATION_EXECUTION_POLICY = "filesystem_mutation"
KNOWN_EXECUTION_POLICIES = frozenset(
    {
        REPORT_ONLY_EXECUTION_POLICY,
        FILESYSTEM_MUTATION_EXECUTION_POLICY,
    }
)


@dataclass
class Task:
    id: str
    run_id: str
    title: str
    role: str
    status: str
    dependencies: List[str]
    success_criteria: List[str]
    files_in_scope: List[str]
    retry_count: int
    expected_output: str | None = None
    source_task_id: str | None = None
    source_artifact_id: str | None = None
    execution_artifact_id: str | None = None
    review_reason: str | None = None
    recommendation_type: str | None = None
    recommendation_reason: str | None = None
    recommendation_identity: str | None = None
    recommendation_confirmed: bool = False
    recommendation_confirmed_at: str | None = None
    verification_checks: List[Dict[str, str]] | None = None
    requires_causal_change: bool = False
    execution_policy: str = REPORT_ONLY_EXECUTION_POLICY
    execution_delegation_status: str | None = None
    source_case_packet_identity: str | None = None
    execution_authorization_provenance: Dict[str, Any] | None = None


def normalize_execution_policy(task: Task) -> str:
    policy = str(task.execution_policy or "").strip()
    if policy not in KNOWN_EXECUTION_POLICIES:
        known = ", ".join(sorted(KNOWN_EXECUTION_POLICIES))
        raise ValueError(
            f"Unknown execution_policy {task.execution_policy!r}; expected one of: {known}."
        )

    task.execution_policy = policy
    if policy == FILESYSTEM_MUTATION_EXECUTION_POLICY:
        task.requires_causal_change = True
    return policy


def _normalize_verification_checks(raw_checks: Any) -> List[Dict[str, str]] | None:
    if not isinstance(raw_checks, list):
        return None

    normalized: List[Dict[str, str]] = []
    for entry in raw_checks:
        if not isinstance(entry, dict):
            continue

        check_name = str(entry.get("check", "")).strip()
        target = str(entry.get("target", "")).strip()
        if not check_name or not target:
            continue

        normalized_entry: Dict[str, str] = {"check": check_name, "target": target}
        if check_name == "file_contains_text" and entry.get("text") is not None:
            normalized_entry["text"] = str(entry.get("text"))

        normalized.append(normalized_entry)

    return normalized or None


def create_task(data: Dict[str, Any]) -> Task:
    recommendation_confirmed_raw = data.get("recommendation_confirmed", False)
    recommendation_confirmed = (
        recommendation_confirmed_raw
        if isinstance(recommendation_confirmed_raw, bool)
        else str(recommendation_confirmed_raw).strip().lower() in {"1", "true", "yes"}
    )
    requires_causal_change_raw = data.get("requires_causal_change", False)
    requires_causal_change = (
        requires_causal_change_raw
        if isinstance(requires_causal_change_raw, bool)
        else str(requires_causal_change_raw).strip().lower() in {"1", "true", "yes"}
    )
    task = Task(
        id=str(data["id"]),
        run_id=str(data["run_id"]),
        title=str(data["title"]),
        role=str(data["role"]),
        status=str(data.get("status", "queued")),
        dependencies=[str(dep) for dep in data.get("dependencies", [])],
        success_criteria=[str(item) for item in data.get("success_criteria", [])],
        files_in_scope=[str(item) for item in data.get("files_in_scope", [])],
        retry_count=int(data.get("retry_count", 0)),
        expected_output=(str(data["expected_output"]) if data.get("expected_output") is not None else None),
        source_task_id=(str(data["source_task_id"]) if data.get("source_task_id") is not None else None),
        source_artifact_id=(
            str(data["source_artifact_id"]) if data.get("source_artifact_id") is not None else None
        ),
        execution_artifact_id=(
            str(data["execution_artifact_id"]) if data.get("execution_artifact_id") is not None else None
        ),
        review_reason=(str(data["review_reason"]) if data.get("review_reason") is not None else None),
        recommendation_type=(
            str(data["recommendation_type"]) if data.get("recommendation_type") is not None else None
        ),
        recommendation_reason=(
            str(data["recommendation_reason"]) if data.get("recommendation_reason") is not None else None
        ),
        recommendation_identity=(
            str(data["recommendation_identity"]) if data.get("recommendation_identity") is not None else None
        ),
        recommendation_confirmed=recommendation_confirmed,
        recommendation_confirmed_at=(
            str(data["recommendation_confirmed_at"])
            if data.get("recommendation_confirmed_at") is not None
            else None
        ),
        verification_checks=_normalize_verification_checks(data.get("verification_checks")),
        requires_causal_change=requires_causal_change,
        execution_policy=str(
            data.get("execution_policy", REPORT_ONLY_EXECUTION_POLICY)
        ).strip(),
        execution_delegation_status=(
            str(data["execution_delegation_status"])
            if data.get("execution_delegation_status") is not None
            else None
        ),
        source_case_packet_identity=(
            str(data["source_case_packet_identity"])
            if data.get("source_case_packet_identity") is not None
            else None
        ),
        execution_authorization_provenance=(
            dict(data["execution_authorization_provenance"])
            if isinstance(data.get("execution_authorization_provenance"), dict)
            else None
        ),
    )
    normalize_execution_policy(task)
    return task


def serialize_task(task: Task) -> Dict[str, Any]:
    normalize_execution_policy(task)
    return {
        "id": task.id,
        "run_id": task.run_id,
        "title": task.title,
        "role": task.role,
        "status": task.status,
        "dependencies": task.dependencies,
        "success_criteria": task.success_criteria,
        "files_in_scope": task.files_in_scope,
        "retry_count": task.retry_count,
        "expected_output": task.expected_output,
        "source_task_id": task.source_task_id,
        "source_artifact_id": task.source_artifact_id,
        "execution_artifact_id": task.execution_artifact_id,
        "review_reason": task.review_reason,
        "recommendation_type": task.recommendation_type,
        "recommendation_reason": task.recommendation_reason,
        "recommendation_identity": task.recommendation_identity,
        "recommendation_confirmed": task.recommendation_confirmed,
        "recommendation_confirmed_at": task.recommendation_confirmed_at,
        "verification_checks": task.verification_checks,
        "requires_causal_change": task.requires_causal_change,
        "execution_policy": task.execution_policy,
        "execution_delegation_status": task.execution_delegation_status,
        "source_case_packet_identity": task.source_case_packet_identity,
        "execution_authorization_provenance": task.execution_authorization_provenance,
    }


def deserialize_task(data: Dict[str, Any]) -> Task:
    return create_task(data)
