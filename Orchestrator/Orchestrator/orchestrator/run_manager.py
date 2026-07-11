import json
from datetime import datetime, timezone
from uuid import uuid4

from orchestrator.paths import RUNS_DIR, TASKS_DIR, record_path, validate_record_id
from orchestrator.alpha_runtime import SCHEMA_VERSION, atomic_write_json, load_json_record
from orchestrator.state import load_state, save_state
from orchestrator.task_schema import Task, deserialize_task, serialize_task


def create_run(request_text: str) -> dict:
    run_id = f"run_{uuid4().hex[:8]}"
    run_data = {
        "schema_version": SCHEMA_VERSION,
        "id": run_id,
        "request_text": request_text,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    run_path = record_path(RUNS_DIR, run_id, label="run id")
    atomic_write_json(run_path, run_data)

    state = load_state()
    state["active_run_id"] = run_id
    save_state(state)
    return run_data


def ensure_run(run_id: str, request_text: str) -> dict:
    """Persist an alpha caller-supplied run identity without changing active state."""
    safe_id = validate_record_id(run_id, label="run id")
    path = record_path(RUNS_DIR, safe_id, label="run id")
    if path.exists():
        return load_json_record(path, record_type="run")
    run_data = {"schema_version": SCHEMA_VERSION, "id": safe_id, "request_text": request_text, "status": "active", "created_at": datetime.now(timezone.utc).isoformat()}
    atomic_write_json(path, run_data)
    return run_data


def save_task(task: Task) -> None:
    task_path = record_path(TASKS_DIR, task.id, label="task id")
    atomic_write_json(task_path, serialize_task(task))


def load_task(task_id: str) -> Task:
    task_path = record_path(TASKS_DIR, task_id, label="task id")
    data = load_json_record(task_path, record_type="task")
    task = deserialize_task(data)
    persisted_id = validate_record_id(task.id, label="persisted task id")
    if persisted_id != validate_record_id(task_id, label="task id"):
        raise ValueError("Persisted task id does not match the requested task id.")
    return task


def load_tasks_for_run(run_id: str) -> list[Task]:
    if not TASKS_DIR.exists():
        return []

    tasks: list[Task] = []
    for path in sorted(TASKS_DIR.glob("*.json")):
        data = load_json_record(path, record_type="task")
        if str(data.get("run_id")) == run_id:
            tasks.append(deserialize_task(data))
    return tasks


def get_next_task(run_id: str) -> Task | None:
    tasks = load_tasks_for_run(run_id)
    task_map = {task.id: task for task in tasks}

    for task in tasks:
        if task.status != "queued":
            continue

        dependencies_satisfied = True
        for dependency_id in task.dependencies:
            dependency = task_map.get(dependency_id)
            if dependency is None or dependency.status != "completed":
                dependencies_satisfied = False
                break

        if dependencies_satisfied:
            return task

    return None


def create_reviewer_task(
    original_task: Task,
    source_artifact_id: str,
    review_reason: str,
    expected_output: str = "concise review",
) -> Task:
    task_id = f"task_{uuid4().hex[:8]}"
    reviewer_task = Task(
        id=task_id,
        run_id=original_task.run_id,
        title=f"Review output of {original_task.id}",
        role="reviewer",
        status="queued",
        dependencies=[],
        success_criteria=["Assess artifact adequacy and recommend next action."],
        files_in_scope=original_task.files_in_scope,
        retry_count=0,
        expected_output=expected_output,
        source_task_id=original_task.id,
        source_artifact_id=source_artifact_id,
        review_reason=review_reason,
    )
    save_task(reviewer_task)
    return reviewer_task


def create_task_from_recommendation(
    run_id: str,
    source_task_id: str,
    source_artifact_id: str,
    recommendation_type: str,
    reason: str,
) -> Task:
    if recommendation_type == "repair_candidate":
        role = "coder"
        title = f"Repair follow-up for {source_task_id}"
        expected_output = "Provide a repair patch and concise explanation."
    elif recommendation_type == "manual_followup":
        role = "reviewer"
        title = f"Manual follow-up for {source_task_id}"
        expected_output = "Provide a concise manual follow-up assessment."
    else:
        raise ValueError(f"Unsupported recommendation type: {recommendation_type}")

    task = Task(
        id=f"task_{uuid4().hex[:8]}",
        run_id=run_id,
        title=title,
        role=role,
        status="queued",
        dependencies=[],
        success_criteria=[f"Address {recommendation_type} recommendation for {source_task_id}."],
        files_in_scope=[],
        retry_count=0,
        expected_output=expected_output,
        source_task_id=source_task_id,
        source_artifact_id=source_artifact_id,
        review_reason=reason,
        recommendation_type=recommendation_type,
        recommendation_reason=reason,
        recommendation_identity="recommendation_created",
    )
    save_task(task)
    return task


def _parse_recommendation_from_review_reason(review_reason: str | None) -> tuple[str, str]:
    text = (review_reason or "").strip()
    if not text:
        return "", ""

    recommendation_type = ""
    recommendation_reason = ""
    for part in text.split(";"):
        segment = part.strip()
        if segment.startswith("recommendation_type="):
            recommendation_type = segment.split("=", 1)[1].strip()
        elif segment.startswith("reason="):
            recommendation_reason = segment.split("=", 1)[1].strip()

    return recommendation_type, recommendation_reason


def get_task_recommendation_type(task: Task) -> str:
    explicit_type = (task.recommendation_type or "").strip()
    if explicit_type:
        return explicit_type

    legacy_type, _ = _parse_recommendation_from_review_reason(task.review_reason)
    return legacy_type


def get_task_recommendation_reason(task: Task) -> str:
    explicit_reason = (task.recommendation_reason or "").strip()
    if explicit_reason:
        return explicit_reason

    _, legacy_reason = _parse_recommendation_from_review_reason(task.review_reason)
    return legacy_reason


def _is_structural_recommendation_created_task(task: Task) -> bool:
    source_task_id = (task.source_task_id or "").strip()
    source_artifact_id = (task.source_artifact_id or "").strip()
    recommendation_type = get_task_recommendation_type(task)
    recommendation_identity = (task.recommendation_identity or "").strip()
    has_structural_provenance = bool(
        source_artifact_id or recommendation_identity == "recommendation_created"
    )
    return bool(source_task_id and recommendation_type and has_structural_provenance)


def _is_compatibility_recommendation_created_task(task: Task) -> bool:
    if _is_structural_recommendation_created_task(task):
        return False

    source_task_id = (task.source_task_id or "").strip()
    recommendation_type = get_task_recommendation_type(task)
    recommendation_reason = get_task_recommendation_reason(task)
    return bool(source_task_id and recommendation_type and recommendation_reason)


def is_recommendation_created_task(task: Task) -> bool:
    return (
        _is_structural_recommendation_created_task(task)
        or _is_compatibility_recommendation_created_task(task)
    )


def is_confirmed_recommendation_created_task(task: Task) -> bool:
    return is_recommendation_created_task(task) and task.recommendation_confirmed


def is_ready_recommendation_created_task(task: Task) -> bool:
    return is_confirmed_recommendation_created_task(task)


def is_ready_execution_candidate_task(task: Task) -> bool:
    return is_ready_recommendation_created_task(task) and task.status == "queued"


def is_post_execution_recommendation_result_task(task: Task) -> bool:
    if not is_recommendation_created_task(task):
        return False
    return task.status not in {"queued", "ready", "in_progress"}


def load_recommendation_created_tasks_for_run(run_id: str) -> list[Task]:
    return [task for task in load_tasks_for_run(run_id) if is_recommendation_created_task(task)]


def load_confirmed_recommendation_created_tasks_for_run(run_id: str) -> list[Task]:
    return [
        task
        for task in load_recommendation_created_tasks_for_run(run_id)
        if is_confirmed_recommendation_created_task(task)
    ]


def load_ready_recommendation_created_tasks_for_run(run_id: str) -> list[Task]:
    return [
        task
        for task in load_recommendation_created_tasks_for_run(run_id)
        if is_ready_recommendation_created_task(task)
    ]


def load_ready_execution_candidate_tasks_for_run(run_id: str) -> list[Task]:
    return [
        task
        for task in load_recommendation_created_tasks_for_run(run_id)
        if is_ready_execution_candidate_task(task)
    ]


def load_post_execution_recommendation_result_tasks_for_run(run_id: str) -> list[Task]:
    return [
        task
        for task in load_recommendation_created_tasks_for_run(run_id)
        if is_post_execution_recommendation_result_task(task)
    ]


def find_live_response_task_duplicate(
    run_id: str,
    source_task_id: str,
    recommendation_type: str,
) -> Task | None:
    live_statuses = {"queued", "in_progress"}
    for task in load_tasks_for_run(run_id):
        if task.source_task_id != source_task_id:
            continue
        if get_task_recommendation_type(task) != recommendation_type:
            continue
        if task.status not in live_statuses:
            continue
        return task
    return None


def create_followup_review_task_from_needs_review_result(source_task: Task) -> Task:
    recommendation_reason = get_task_recommendation_reason(source_task)
    review_reason_parts = [f"Follow-up review created from needs_review result {source_task.id}."]
    if recommendation_reason:
        review_reason_parts.append(f"Prior recommendation context: {recommendation_reason}.")
    needs_review_result_artifact_id = (source_task.execution_artifact_id or "").strip()
    if needs_review_result_artifact_id:
        review_reason_parts.append(
            f"Inspect artifact {needs_review_result_artifact_id} produced by that result."
        )
    else:
        review_reason_parts.append("No result artifact was persisted for that source task.")

    inherited_scope = list(source_task.files_in_scope) if source_task.files_in_scope else []

    followup_task = Task(
        id=f"task_{uuid4().hex[:8]}",
        run_id=source_task.run_id,
        title=f"Follow-up review for {source_task.id}",
        role="reviewer",
        status="queued",
        dependencies=[],
        success_criteria=[f"Perform follow-up review for needs_review result {source_task.id}."],
        files_in_scope=inherited_scope,
        retry_count=0,
        expected_output="concise follow-up review",
        source_task_id=source_task.id,
        source_artifact_id=(needs_review_result_artifact_id or None),
        review_reason=" ".join(review_reason_parts),
        recommendation_type="manual_followup",
        recommendation_reason=(
            f"Follow-up review created from needs_review result {source_task.id}."
        ),
        recommendation_identity="recommendation_created",
    )
    save_task(followup_task)
    return followup_task


def create_repair_task_from_failed_result(source_task: Task) -> Task:
    recommendation_reason = get_task_recommendation_reason(source_task)
    repair_reason_parts = [f"Repair task created from failed result {source_task.id}."]
    if recommendation_reason:
        repair_reason_parts.append(f"Prior recommendation context: {recommendation_reason}.")
    failed_result_artifact_id = (source_task.execution_artifact_id or "").strip()
    if failed_result_artifact_id:
        repair_reason_parts.append(
            f"Repair should address artifact {failed_result_artifact_id} from that failed result."
        )
    else:
        repair_reason_parts.append("No failed-result artifact was persisted for that source task.")

    inherited_scope = list(source_task.files_in_scope) if source_task.files_in_scope else []

    repair_task = Task(
        id=f"task_{uuid4().hex[:8]}",
        run_id=source_task.run_id,
        title=f"Repair for {source_task.id}",
        role="coder",
        status="queued",
        dependencies=[],
        success_criteria=[f"Create repair for failed result {source_task.id}."],
        files_in_scope=inherited_scope,
        retry_count=0,
        expected_output="Provide a repair patch and concise explanation.",
        source_task_id=source_task.id,
        source_artifact_id=(failed_result_artifact_id or None),
        review_reason=" ".join(repair_reason_parts),
        recommendation_type="repair_candidate",
        recommendation_reason=(
            f"Repair task created from failed result {source_task.id}."
        ),
        recommendation_identity="recommendation_created",
    )
    save_task(repair_task)
    return repair_task


def is_recommendation_emitter_reviewer_task(task: Task) -> bool:
    if task.role != "reviewer":
        return False
    source_task_id = (task.source_task_id or "").strip()
    source_artifact_id = (task.source_artifact_id or "").strip()
    if not source_task_id or not source_artifact_id:
        return False
    return not is_recommendation_created_task(task)
