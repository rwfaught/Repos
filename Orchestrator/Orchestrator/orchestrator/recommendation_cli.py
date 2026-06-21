from orchestrator.recommendation_store import (
    format_recommendation_summary,
    load_recommendation_records_for_run,
)
from orchestrator.reviewer_output import (
    accept_recommendation_record,
    archive_recommendation_record,
    find_recommendation_records_for_reviewer_task,
)
from orchestrator.run_manager import (
    get_task_recommendation_type,
    load_recommendation_created_tasks_for_run,
    load_task,
)
from orchestrator.state import load_state


NO_ACTIVE_RUN_MESSAGE = "No active run. Use --run <run_id> or create/select an active run."


def _resolve_run_id(run_id: str | None) -> str | None:
    if run_id:
        return str(run_id)

    state = load_state()
    active_run_id = state.get("active_run_id")
    if not active_run_id:
        print(NO_ACTIVE_RUN_MESSAGE)
        return None
    return str(active_run_id)


def _recommendation_archival_status(record: dict) -> str:
    return "archived" if bool(record.get("archived", False)) else "active"


def _recommendation_archival_fields(record: dict) -> str:
    archived_at = str(record.get("archived_at", "")).strip() or "(none)"
    return (
        f"archival_status={_recommendation_archival_status(record)} "
        f"archived_at={archived_at}"
    )


def _recommendation_acceptance_status(record: dict) -> str:
    return "accepted" if bool(record.get("accepted", False)) else "not_accepted"


def _recommendation_acceptance_fields(record: dict) -> str:
    accepted_at = str(record.get("accepted_at", "")).strip() or "(none)"
    return (
        f"acceptance_status={_recommendation_acceptance_status(record)} "
        f"accepted_at={accepted_at}"
    )


def _get_source_task_id_for_recommendation_record(record: dict) -> str:
    recommendation = record.get("recommendation", {})
    source_task_id = str(recommendation.get("source_task_id", "")).strip()
    if source_task_id:
        return source_task_id

    reviewer_task_id = str(record.get("reviewer_task_id", "")).strip()
    if not reviewer_task_id:
        return ""

    try:
        reviewer_task = load_task(reviewer_task_id)
    except FileNotFoundError:
        return ""
    return str(reviewer_task.source_task_id or "").strip()


def _find_materialized_task_id_for_recommendation(record: dict, recommendation_created_tasks: list) -> str:
    recommendation = record.get("recommendation", {})
    recommendation_type = str(recommendation.get("recommendation_type", "")).strip()
    source_task_id = _get_source_task_id_for_recommendation_record(record)
    if not recommendation_type or not source_task_id:
        return ""

    matching_ids = sorted(
        task.id
        for task in recommendation_created_tasks
        if str(task.source_task_id or "").strip() == source_task_id
        and get_task_recommendation_type(task) == recommendation_type
    )
    if not matching_ids:
        return ""
    return matching_ids[0]


def print_recommendations(run_id: str | None) -> None:
    resolved_run_id = _resolve_run_id(run_id)
    if resolved_run_id is None:
        return

    records = sorted(
        load_recommendation_records_for_run(resolved_run_id),
        key=lambda record: (
            str(record.get("timestamp", "")),
            str(record.get("reviewer_task_id", "")),
        ),
    )
    heading = f"Reviewer recommendations for run: {resolved_run_id}"
    if not records:
        print(f"{heading}\nNo recommendation records found for this run.")
        return

    print(f"{heading}\nCount: {len(records)}")
    for record in records:
        print("---")
        print(format_recommendation_summary(record))


def print_recommendation_summary(run_id: str | None) -> None:
    resolved_run_id = _resolve_run_id(run_id)
    if resolved_run_id is None:
        return

    records = sorted(
        load_recommendation_records_for_run(resolved_run_id),
        key=lambda record: (
            str(record.get("timestamp", "")),
            str(record.get("reviewer_task_id", "")),
        ),
    )
    if not records:
        print(f"Recommendation summary for run: {resolved_run_id}")
        print("No recommendation records found for this run.")
        return

    stable_type_order = ["accept_result", "manual_followup", "repair_candidate"]
    grouped_records: dict[str, list[dict]] = {key: [] for key in stable_type_order}
    unknown_types: dict[str, list[dict]] = {}
    for record in records:
        rec = record.get("recommendation", {})
        rec_type = str(rec.get("recommendation_type", "")).strip()
        if rec_type in grouped_records:
            grouped_records[rec_type].append(record)
        else:
            unknown_types.setdefault(rec_type or "(missing)", []).append(record)

    ordered_types = stable_type_order + sorted(unknown_types.keys())
    combined_grouped_records = {**grouped_records, **unknown_types}

    print(f"Recommendation summary for run: {resolved_run_id}")
    print(f"Total recommendation records: {len(records)}")
    print("Counts by recommendation type:")
    for recommendation_type in ordered_types:
        print(f"- {recommendation_type}: {len(combined_grouped_records[recommendation_type])}")

    for recommendation_type in ordered_types:
        type_records = combined_grouped_records[recommendation_type]
        if not type_records:
            continue
        print(f"{recommendation_type} ({len(type_records)}):")
        for record in type_records:
            recommendation = record.get("recommendation", {})
            reviewer_task_id = record.get("reviewer_task_id")
            reason = recommendation.get("reason")
            timestamp = record.get("timestamp")
            print(
                f"- reviewer_task_id={reviewer_task_id} "
                f"reason={reason} "
                f"timestamp={timestamp} "
                f"{_recommendation_archival_fields(record)} "
                f"{_recommendation_acceptance_fields(record)}"
            )


def print_recommendation_actions(run_id: str | None) -> None:
    resolved_run_id = _resolve_run_id(run_id)
    if resolved_run_id is None:
        return

    records = sorted(
        load_recommendation_records_for_run(resolved_run_id),
        key=lambda record: (
            str(record.get("timestamp", "")),
            str(record.get("reviewer_task_id", "")),
        ),
    )

    print(f"Recommendation actions for run: {resolved_run_id}")
    print(f"Total recommendation records: {len(records)}")
    print("This command is read-only and does not create tasks or mutate state.")

    if not records:
        print("No recommendation records found for this run.")
        return

    action_map = {
        "accept_result": "Result may be accepted; no immediate follow-up action required.",
        "manual_followup": "Follow-up review task could be created explicitly.",
        "repair_candidate": "Repair task could be created explicitly.",
    }
    stable_type_order = ["accept_result", "manual_followup", "repair_candidate"]
    grouped: dict[str, list[dict]] = {key: [] for key in stable_type_order}
    unknown_types: dict[str, list[dict]] = {}

    for record in records:
        recommendation = record.get("recommendation", {})
        rec_type = str(recommendation.get("recommendation_type", "")).strip()
        if rec_type in grouped:
            grouped[rec_type].append(record)
        else:
            unknown_types.setdefault(rec_type or "(missing)", []).append(record)

    ordered_types = stable_type_order + sorted(unknown_types.keys())
    combined_grouped = {**grouped, **unknown_types}

    print("Counts by recommendation type:")
    for rec_type in ordered_types:
        print(f"- {rec_type}: {len(combined_grouped[rec_type])}")

    for rec_type in ordered_types:
        entries = combined_grouped[rec_type]
        if not entries:
            continue
        print(f"{rec_type} ({len(entries)}):")
        for entry in entries:
            recommendation = entry.get("recommendation", {})
            candidate_action = action_map.get(
                rec_type,
                "No explicit candidate action mapping is defined for this recommendation type.",
            )
            print(
                f"- reviewer_task_id={entry.get('reviewer_task_id')} "
                f"recommendation_type={rec_type} "
                f"reason={recommendation.get('reason')} "
                f"candidate_action={candidate_action} "
                f"timestamp={entry.get('timestamp')} "
                f"{_recommendation_archival_fields(entry)} "
                f"{_recommendation_acceptance_fields(entry)}"
            )


def print_recommendation_drafts(run_id: str | None) -> None:
    resolved_run_id = _resolve_run_id(run_id)
    if resolved_run_id is None:
        return

    records = sorted(
        load_recommendation_records_for_run(resolved_run_id),
        key=lambda record: (
            str(record.get("timestamp", "")),
            str(record.get("reviewer_task_id", "")),
        ),
    )

    print(f"Recommendation drafts for run: {resolved_run_id}")
    print(f"Total recommendation records: {len(records)}")
    print("This command is read-only and does not create tasks or mutate state.")

    if not records:
        print("No recommendation records found for this run.")
        return

    stable_type_order = ["accept_result", "manual_followup", "repair_candidate"]
    grouped: dict[str, list[dict]] = {key: [] for key in stable_type_order}
    unknown_types: dict[str, list[dict]] = {}

    for record in records:
        recommendation = record.get("recommendation", {})
        rec_type = str(recommendation.get("recommendation_type", "")).strip()
        if rec_type in grouped:
            grouped[rec_type].append(record)
        else:
            unknown_types.setdefault(rec_type or "(missing)", []).append(record)

    ordered_types = stable_type_order + sorted(unknown_types.keys())
    combined_grouped = {**grouped, **unknown_types}

    print("Counts by recommendation type:")
    for rec_type in ordered_types:
        print(f"- {rec_type}: {len(combined_grouped[rec_type])}")

    for rec_type in ordered_types:
        entries = combined_grouped[rec_type]
        if not entries:
            continue
        print(f"{rec_type} ({len(entries)}):")
        for entry in entries:
            recommendation = entry.get("recommendation", {})
            reviewer_task_id = str(entry.get("reviewer_task_id", "")).strip()
            reason = recommendation.get("reason")
            timestamp = entry.get("timestamp")

            source_task_id = recommendation.get("source_task_id")
            source_artifact_id = recommendation.get("source_artifact_id")
            if not source_task_id or not source_artifact_id:
                try:
                    reviewer_task = load_task(reviewer_task_id)
                except FileNotFoundError:
                    reviewer_task = None
                if reviewer_task is not None:
                    if not source_task_id:
                        source_task_id = reviewer_task.source_task_id
                    if not source_artifact_id:
                        source_artifact_id = reviewer_task.source_artifact_id

            if rec_type == "manual_followup":
                proposed_role = "reviewer"
                if source_task_id:
                    proposed_title = f"Follow-up review for {source_task_id}"
                else:
                    proposed_title = f"Follow-up review from recommendation {reviewer_task_id}"
                print(
                    f"- reviewer_task_id={reviewer_task_id} "
                    f"recommendation_type={rec_type} "
                    f"proposed_role={proposed_role} "
                    f"proposed_title={proposed_title} "
                    f"source_task_id={source_task_id} "
                    f"source_artifact_id={source_artifact_id} "
                    f"draft_rationale={reason} "
                    f"timestamp={timestamp} "
                    f"{_recommendation_archival_fields(entry)} "
                    f"{_recommendation_acceptance_fields(entry)}"
                )
                continue

            if rec_type == "repair_candidate":
                proposed_role = "coder"
                if source_task_id:
                    proposed_title = f"Repair for {source_task_id}"
                else:
                    proposed_title = f"Repair from recommendation {reviewer_task_id}"
                print(
                    f"- reviewer_task_id={reviewer_task_id} "
                    f"recommendation_type={rec_type} "
                    f"proposed_role={proposed_role} "
                    f"proposed_title={proposed_title} "
                    f"source_task_id={source_task_id} "
                    f"source_artifact_id={source_artifact_id} "
                    f"draft_rationale={reason} "
                    f"timestamp={timestamp} "
                    f"{_recommendation_archival_fields(entry)} "
                    f"{_recommendation_acceptance_fields(entry)}"
                )
                continue

            if rec_type == "accept_result":
                print(
                    f"- reviewer_task_id={reviewer_task_id} "
                    f"recommendation_type={rec_type} "
                    f"draft_needed=no "
                    f"info=No draft task needed for accept_result. "
                    f"reason={reason} "
                    f"timestamp={timestamp} "
                    f"{_recommendation_archival_fields(entry)} "
                    f"{_recommendation_acceptance_fields(entry)}"
                )
                continue

            print(
                f"- reviewer_task_id={reviewer_task_id} "
                f"recommendation_type={rec_type} "
                f"draft_needed=no "
                f"info=No draft mapping is defined for this recommendation type. "
                f"reason={reason} "
                f"timestamp={timestamp} "
                f"{_recommendation_archival_fields(entry)} "
                f"{_recommendation_acceptance_fields(entry)}"
            )


def print_recommendation_outcomes(run_id: str | None) -> None:
    resolved_run_id = _resolve_run_id(run_id)
    if resolved_run_id is None:
        return

    records = sorted(
        load_recommendation_records_for_run(resolved_run_id),
        key=lambda record: (
            str(record.get("timestamp", "")),
            str(record.get("reviewer_task_id", "")),
        ),
    )

    print(f"Recommendation outcomes for run: {resolved_run_id}")
    print(f"Total recommendation records: {len(records)}")
    print("This command is read-only and does not create tasks or mutate state.")

    if not records:
        print("No recommendation records found for this run.")
        return

    stable_type_order = ["accept_result", "manual_followup", "repair_candidate"]
    grouped: dict[str, list[dict]] = {key: [] for key in stable_type_order}
    unknown_types: dict[str, list[dict]] = {}

    for record in records:
        recommendation = record.get("recommendation", {})
        rec_type = str(recommendation.get("recommendation_type", "")).strip()
        if rec_type in grouped:
            grouped[rec_type].append(record)
        else:
            unknown_types.setdefault(rec_type or "(missing)", []).append(record)

    ordered_types = stable_type_order + sorted(unknown_types.keys())
    combined_grouped = {**grouped, **unknown_types}

    recommendation_created_tasks = load_recommendation_created_tasks_for_run(resolved_run_id)

    print("Counts by recommendation type:")
    for rec_type in ordered_types:
        print(f"- {rec_type}: {len(combined_grouped[rec_type])}")

    for rec_type in ordered_types:
        entries = combined_grouped[rec_type]
        if not entries:
            continue
        print(f"{rec_type} ({len(entries)}):")
        for entry in entries:
            recommendation = entry.get("recommendation", {})
            reviewer_task_id = str(entry.get("reviewer_task_id", "")).strip()
            reason = recommendation.get("reason")
            timestamp = entry.get("timestamp")
            source_task_id = _get_source_task_id_for_recommendation_record(entry)
            materialized_task_id = _find_materialized_task_id_for_recommendation(
                entry, recommendation_created_tasks
            )

            if rec_type == "accept_result":
                materialization_status = (
                    "not materialized (accept_result has no task-creation path)"
                )
            elif not source_task_id:
                materialization_status = "unknown (source task linkage unavailable)"
            elif materialized_task_id:
                materialization_status = "materialized"
            else:
                materialization_status = "not yet materialized"

            print(
                f"- reviewer_task_id={reviewer_task_id} "
                f"recommendation_type={rec_type} "
                f"reason={reason} "
                f"timestamp={timestamp} "
                f"materialization_status={materialization_status} "
                f"created_task_id={materialized_task_id or '(none)'} "
                f"source_task_id={source_task_id or '(unknown)'} "
                f"{_recommendation_archival_fields(entry)} "
                f"{_recommendation_acceptance_fields(entry)}"
            )


def print_recommendation_resolution(run_id: str | None) -> None:
    resolved_run_id = _resolve_run_id(run_id)
    if resolved_run_id is None:
        return

    records = sorted(
        load_recommendation_records_for_run(resolved_run_id),
        key=lambda record: (
            str(record.get("timestamp", "")),
            str(record.get("reviewer_task_id", "")),
        ),
    )

    print(f"Recommendation resolution for run: {resolved_run_id}")
    print(f"Total recommendation records: {len(records)}")
    print("This command is read-only and does not create tasks or mutate state.")

    if not records:
        print("No recommendation records found for this run.")
        return

    stable_type_order = ["accept_result", "manual_followup", "repair_candidate"]
    grouped: dict[str, list[dict]] = {key: [] for key in stable_type_order}
    unknown_types: dict[str, list[dict]] = {}

    for record in records:
        recommendation = record.get("recommendation", {})
        rec_type = str(recommendation.get("recommendation_type", "")).strip()
        if rec_type in grouped:
            grouped[rec_type].append(record)
        else:
            unknown_types.setdefault(rec_type or "(missing)", []).append(record)

    ordered_types = stable_type_order + sorted(unknown_types.keys())
    combined_grouped = {**grouped, **unknown_types}
    recommendation_created_tasks = load_recommendation_created_tasks_for_run(resolved_run_id)

    print("Counts by recommendation type:")
    for rec_type in ordered_types:
        print(f"- {rec_type}: {len(combined_grouped[rec_type])}")

    for rec_type in ordered_types:
        entries = combined_grouped[rec_type]
        if not entries:
            continue
        print(f"{rec_type} ({len(entries)}):")
        for entry in entries:
            recommendation = entry.get("recommendation", {})
            reviewer_task_id = str(entry.get("reviewer_task_id", "")).strip()
            reason = recommendation.get("reason")
            timestamp = entry.get("timestamp")
            source_task_id = _get_source_task_id_for_recommendation_record(entry)
            created_task_id = _find_materialized_task_id_for_recommendation(
                entry, recommendation_created_tasks
            )

            if rec_type == "accept_result":
                resolution_status = "informational (resolved in place; no creation path)"
            elif rec_type in {"manual_followup", "repair_candidate"}:
                if not source_task_id:
                    resolution_status = "unknown (source task linkage unavailable)"
                elif created_task_id:
                    resolution_status = "materialized"
                else:
                    resolution_status = "open"
            else:
                resolution_status = "unsupported_or_unknown"

            print(
                f"- reviewer_task_id={reviewer_task_id} "
                f"recommendation_type={rec_type} "
                f"reason={reason} "
                f"timestamp={timestamp} "
                f"resolution_status={resolution_status} "
                f"source_task_id={source_task_id or '(unknown)'} "
                f"created_task_id={created_task_id or '(none)'} "
                f"{_recommendation_archival_fields(entry)} "
                f"{_recommendation_acceptance_fields(entry)}"
            )


def archive_recommendation(reviewer_task_id: str, run_id: str | None) -> None:
    resolved_run_id = _resolve_run_id(run_id)
    if resolved_run_id is None:
        return

    matches = find_recommendation_records_for_reviewer_task(
        reviewer_task_id=reviewer_task_id,
        run_id=resolved_run_id,
    )

    if not matches:
        print(
            "No matching recommendation record found for "
            f"reviewer_task_id={reviewer_task_id} in run={resolved_run_id}. No archive applied."
        )
        return

    if len(matches) > 1:
        print(
            "Multiple recommendation records matched this reviewer task in the selected run. "
            "No archive applied."
        )
        return

    record = matches[0]
    if bool(record.get("archived", False)):
        print("Recommendation record is already archived.")
        print(f"Reviewer Task ID: {record.get('reviewer_task_id')}")
        print(f"Run ID: {record.get('run_id')}")
        print(f"Archived: {record.get('archived')}")
        print(f"Archived At: {record.get('archived_at')}")
        return

    updated_record = archive_recommendation_record(record)
    recommendation = updated_record.get("recommendation", {})
    print("Recommendation record archived.")
    print(f"Reviewer Task ID: {updated_record.get('reviewer_task_id')}")
    print(f"Run ID: {updated_record.get('run_id')}")
    print(f"Recommendation Type: {recommendation.get('recommendation_type')}")
    print(f"Reason: {recommendation.get('reason')}")
    print(f"Timestamp: {updated_record.get('timestamp')}")
    print(f"Archived: {updated_record.get('archived')}")
    print(f"Archived At: {updated_record.get('archived_at')}")


def accept_recommendation(reviewer_task_id: str, run_id: str | None) -> None:
    resolved_run_id = _resolve_run_id(run_id)
    if resolved_run_id is None:
        return

    matches = find_recommendation_records_for_reviewer_task(
        reviewer_task_id=reviewer_task_id,
        run_id=resolved_run_id,
    )

    if not matches:
        print(
            "No matching recommendation record found for "
            f"reviewer_task_id={reviewer_task_id} in run={resolved_run_id}. No acceptance applied."
        )
        return

    if len(matches) > 1:
        print(
            "Multiple recommendation records matched this reviewer task in the selected run. "
            "No acceptance applied."
        )
        return

    record = matches[0]
    recommendation = record.get("recommendation", {})
    recommendation_type = str(recommendation.get("recommendation_type", "")).strip()
    if recommendation_type != "accept_result":
        print(
            "Only accept_result recommendations can be accepted. "
            f"Found type={recommendation_type or '(missing)'}. No acceptance applied."
        )
        return

    if bool(record.get("accepted", False)):
        print("Recommendation record is already accepted.")
        print(f"Reviewer Task ID: {record.get('reviewer_task_id')}")
        print(f"Run ID: {record.get('run_id')}")
        print(f"Accepted: {record.get('accepted')}")
        print(f"Accepted At: {record.get('accepted_at')}")
        return

    updated_record = accept_recommendation_record(record)
    print("Recommendation record accepted.")
    print(f"Reviewer Task ID: {updated_record.get('reviewer_task_id')}")
    print(f"Run ID: {updated_record.get('run_id')}")
    print(f"Recommendation Type: {recommendation_type}")
    print(f"Reason: {recommendation.get('reason')}")
    print(f"Timestamp: {updated_record.get('timestamp')}")
    print(f"Accepted: {updated_record.get('accepted')}")
    print(f"Accepted At: {updated_record.get('accepted_at')}")
