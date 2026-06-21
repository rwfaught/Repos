import json
from pathlib import Path

from orchestrator.paths import DATA_DIR

RECOMMENDATIONS_DIR = DATA_DIR / "reviewer_recommendations"


def load_recommendation_records() -> list[dict]:
    if not RECOMMENDATIONS_DIR.exists():
        return []

    records = []
    for path in sorted(RECOMMENDATIONS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["_path"] = str(path)
        records.append(data)
    return records


def load_recommendation_records_for_run(run_id: str) -> list[dict]:
    return [record for record in load_recommendation_records() if str(record.get("run_id")) == run_id]


def format_recommendation_summary(record: dict) -> str:
    recommendation = record.get("recommendation", {})
    archival_status = "archived" if bool(record.get("archived", False)) else "active"
    acceptance_status = "accepted" if bool(record.get("accepted", False)) else "not_accepted"
    archived_at = str(record.get("archived_at", "")).strip() or "(none)"
    accepted_at = str(record.get("accepted_at", "")).strip() or "(none)"
    return (
        f"Reviewer Task: {record.get('reviewer_task_id')}\n"
        f"Run ID: {record.get('run_id')}\n"
        f"Type: {recommendation.get('recommendation_type')}\n"
        f"Reason: {recommendation.get('reason')}\n"
        f"Source Task: {recommendation.get('source_task_id')}\n"
        f"Source Artifact: {recommendation.get('source_artifact_id')}\n"
        f"Timestamp: {record.get('timestamp')}\n"
        f"Provider: {record.get('provider')}\n"
        f"Archival Status: {archival_status}\n"
        f"Archived At: {archived_at}\n"
        f"Acceptance Status: {acceptance_status}\n"
        f"Accepted At: {accepted_at}"
    )
