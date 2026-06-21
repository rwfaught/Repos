import json
import re
from pathlib import Path

from orchestrator.paths import DATA_DIR

CASE_PACKETS_DIR = DATA_DIR / "case_packets"
_SAFE_CASE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

_REQUIRED_SCALAR_FIELDS = [
    "case_id",
    "case_type",
    "title",
    "objective",
    "status",
    "next_step",
]

_REQUIRED_LIST_FIELDS = [
    "counterparties",
    "source_materials",
    "extracted_facts",
    "timeline_events",
    "open_issues",
    "missing_evidence",
    "contradictions",
    "drafts",
    "decisions",
]

_APPENDABLE_FIELDS = [
    "counterparties",
    "source_materials",
    "extracted_facts",
    "timeline_events",
    "open_issues",
    "missing_evidence",
    "contradictions",
    "drafts",
    "decisions",
]

_ORIENTATION_FIELDS = [
    "status",
    "next_step",
]


def _normalize_scalar(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return ""
    return str(value).strip()


def _normalize_list(value: object) -> list:
    if isinstance(value, list):
        return value
    return []


def _is_safe_case_id(case_id: str) -> bool:
    if not case_id:
        return False
    return _SAFE_CASE_ID_PATTERN.fullmatch(case_id) is not None


def normalize_case_packet(payload: dict) -> dict:
    packet = {}

    for field in _REQUIRED_SCALAR_FIELDS:
        packet[field] = _normalize_scalar(payload.get(field))

    for field in _REQUIRED_LIST_FIELDS:
        packet[field] = _normalize_list(payload.get(field))

    return packet


def validate_case_packet(packet: dict) -> dict:
    errors: list[str] = []

    case_id = _normalize_scalar(packet.get("case_id"))
    title = _normalize_scalar(packet.get("title"))
    objective = _normalize_scalar(packet.get("objective"))

    if not case_id:
        errors.append("case_id is required")
    elif not _is_safe_case_id(case_id):
        errors.append("case_id contains unsafe characters")

    if not title:
        errors.append("title is required")

    if not objective:
        errors.append("objective is required")

    return {"valid": len(errors) == 0, "errors": errors}


def _case_packet_path(case_id: str) -> Path:
    normalized = _normalize_scalar(case_id)
    if not _is_safe_case_id(normalized):
        raise ValueError("Unsafe case_id")

    return CASE_PACKETS_DIR / f"{normalized}.json"


def save_case_packet(packet: dict) -> Path:
    case_id = _normalize_scalar(packet.get("case_id"))
    path = _case_packet_path(case_id)
    CASE_PACKETS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return path


def load_case_packet(case_id: str) -> dict:
    path = _case_packet_path(case_id)
    return json.loads(path.read_text(encoding="utf-8"))


def assess_case_packet_readiness(packet: dict) -> dict:
    normalized = normalize_case_packet(packet)
    validation = validate_case_packet(normalized)
    if not validation["valid"]:
        return {"readiness": "invalid"}

    category_counts = {field: len(normalized[field]) for field in _REQUIRED_LIST_FIELDS}
    populated = [field for field, count in category_counts.items() if count > 0]

    if not populated:
        return {"readiness": "skeletal"}

    review_ready = (
        category_counts["source_materials"] > 0
        and category_counts["open_issues"] > 0
        and bool(normalized["status"])
        and bool(normalized["next_step"])
    )
    if review_ready:
        return {"readiness": "review_ready"}

    return {"readiness": "partially_populated"}


def summarize_case_packet(packet: dict) -> dict:
    normalized = normalize_case_packet(packet)
    validation = validate_case_packet(normalized)
    category_counts = {field: len(normalized[field]) for field in _REQUIRED_LIST_FIELDS}
    populated_categories = [field for field in _REQUIRED_LIST_FIELDS if category_counts[field] > 0]
    empty_categories = [field for field in _REQUIRED_LIST_FIELDS if category_counts[field] == 0]
    readiness = assess_case_packet_readiness(normalized)

    return {
        "case_id": normalized["case_id"],
        "case_type": normalized["case_type"],
        "title": normalized["title"],
        "objective": normalized["objective"],
        "status": normalized["status"],
        "next_step": normalized["next_step"],
        "validation": validation,
        "category_counts": category_counts,
        "populated_categories": populated_categories,
        "empty_categories": empty_categories,
        "readiness": readiness,
    }


def initialize_case_packet_from_seed(seed: dict) -> dict:
    candidate = {
        "case_id": seed.get("case_id", ""),
        "case_type": seed.get("case_type", ""),
        "title": seed.get("title", ""),
        "objective": seed.get("objective", ""),
        "status": seed.get("status", "active"),
        "next_step": seed.get("next_step", ""),
    }

    for field in _REQUIRED_LIST_FIELDS:
        candidate[field] = seed.get(field, [])

    return normalize_case_packet(candidate)


def get_case_packet_appendable_fields() -> list[str]:
    return list(_APPENDABLE_FIELDS)


def append_case_packet_entry(packet: dict, field: str, entry: object) -> dict:
    normalized_field = _normalize_scalar(field)
    if normalized_field in _REQUIRED_SCALAR_FIELDS:
        raise ValueError(f"field is scalar and not appendable: {normalized_field}")
    if normalized_field not in _APPENDABLE_FIELDS:
        raise ValueError(f"field is not appendable: {normalized_field}")
    if entry is None:
        raise ValueError("entry is required")

    normalized_packet = normalize_case_packet(packet)
    normalized_packet[normalized_field].append(entry)
    return normalized_packet


def get_case_packet_orientation_fields() -> list[str]:
    return list(_ORIENTATION_FIELDS)


def update_case_packet_orientation(packet: dict, updates: dict) -> dict:
    if not isinstance(updates, dict) or not updates:
        raise ValueError("at least one orientation field is required")

    normalized_packet = normalize_case_packet(packet)
    updated_packet = dict(normalized_packet)

    for field, value in updates.items():
        normalized_field = _normalize_scalar(field)
        if normalized_field not in _ORIENTATION_FIELDS:
            raise ValueError(f"field is not orientation-updatable: {normalized_field}")
        if value is None:
            raise ValueError(f"{normalized_field} must not be null")
        if not isinstance(value, str):
            raise ValueError(f"{normalized_field} must be a string")
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError(f"{normalized_field} must not be empty")
        updated_packet[normalized_field] = normalized_value

    return updated_packet
