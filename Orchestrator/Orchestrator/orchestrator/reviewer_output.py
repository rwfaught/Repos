import json
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.paths import DATA_DIR
from orchestrator.recommendation_store import load_recommendation_records
from orchestrator.task_schema import Task

ALLOWED_RECOMMENDATION_TYPES = {
    "accept_result",
    "manual_followup",
    "repair_candidate",
}
REVIEWER_RECOMMENDATIONS_DIR = DATA_DIR / "reviewer_recommendations"


def parse_reviewer_recommendation(output_text: object) -> tuple[dict | None, str]:
    if output_text is None:
        return None, "Reviewer output is missing."

    if not isinstance(output_text, str):
        return None, "Reviewer output must be JSON text."

    raw = output_text.strip()
    if not raw:
        return None, "Reviewer output is empty."

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"Reviewer output is not valid JSON: {exc}"

    if not isinstance(parsed, dict):
        return None, "Reviewer output must be a JSON object."

    return parsed, "Reviewer output parsed."


def validate_reviewer_recommendation(data: dict) -> tuple[bool, str]:
    recommendation_type = str(data.get("recommendation_type", "")).strip()
    reason = str(data.get("reason", "")).strip()

    if recommendation_type not in ALLOWED_RECOMMENDATION_TYPES:
        return False, "Invalid recommendation_type."
    if not reason:
        return False, "Missing reason."

    return True, "Reviewer recommendation is valid."


def build_recommendation_record(task: Task, recommendation: dict, provider_name: str | None = None) -> dict:
    return {
        "reviewer_task_id": task.id,
        "run_id": task.run_id,
        "provider": provider_name,
        "recommendation": {
            "recommendation_type": str(recommendation["recommendation_type"]).strip(),
            "reason": str(recommendation["reason"]).strip(),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def persist_recommendation_record(task: Task, record: dict) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    REVIEWER_RECOMMENDATIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = REVIEWER_RECOMMENDATIONS_DIR / f"{task.id}_{timestamp}.json"
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return str(path)


def find_recommendation_records_for_reviewer_task(
    reviewer_task_id: str,
    run_id: str | None = None,
) -> list[dict]:
    matches = []
    for record in load_recommendation_records():
        if str(record.get("reviewer_task_id", "")).strip() != reviewer_task_id:
            continue
        if run_id is not None and str(record.get("run_id", "")).strip() != run_id:
            continue
        matches.append(record)
    return matches


def archive_recommendation_record(record: dict) -> dict:
    path_value = str(record.get("_path", "")).strip()
    if not path_value:
        raise ValueError("Recommendation record is missing _path and cannot be archived.")

    archived_at = datetime.now(timezone.utc).isoformat()
    record["archived"] = True
    record["archived_at"] = archived_at

    serializable_record = {key: value for key, value in record.items() if key != "_path"}
    path = Path(path_value)
    path.write_text(json.dumps(serializable_record, indent=2), encoding="utf-8")
    return record


def accept_recommendation_record(record: dict) -> dict:
    path_value = str(record.get("_path", "")).strip()
    if not path_value:
        raise ValueError("Recommendation record is missing _path and cannot be accepted.")

    accepted_at = datetime.now(timezone.utc).isoformat()
    record["accepted"] = True
    record["accepted_at"] = accepted_at

    serializable_record = {key: value for key, value in record.items() if key != "_path"}
    path = Path(path_value)
    path.write_text(json.dumps(serializable_record, indent=2), encoding="utf-8")
    return record
