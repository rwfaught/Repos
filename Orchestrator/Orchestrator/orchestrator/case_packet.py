import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from orchestrator.alpha_runtime import atomic_write_json
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

_ENTRY_KIND_TO_CASE_PACKET_FIELD = {
    "source_material": "source_materials",
    "extracted_fact": "extracted_facts",
}


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


def _validate_persisted_case_packet(packet: object, *, expected_case_id: str | None = None) -> dict[str, Any]:
    """Reject malformed durable packets without normalizing or migrating them."""
    if not isinstance(packet, dict):
        raise ValueError("persisted case packet must be a JSON object")

    missing_fields = [
        field for field in (*_REQUIRED_SCALAR_FIELDS, *_REQUIRED_LIST_FIELDS) if field not in packet
    ]
    if missing_fields:
        raise ValueError(f"persisted case packet is missing required fields: {', '.join(missing_fields)}")

    non_string_scalars = [field for field in _REQUIRED_SCALAR_FIELDS if not isinstance(packet[field], str)]
    if non_string_scalars:
        raise ValueError(
            f"persisted case packet scalar fields must be strings: {', '.join(non_string_scalars)}"
        )
    non_list_fields = [field for field in _REQUIRED_LIST_FIELDS if not isinstance(packet[field], list)]
    if non_list_fields:
        raise ValueError(f"persisted case packet list fields must be lists: {', '.join(non_list_fields)}")

    case_id = packet["case_id"]
    if expected_case_id is not None and case_id != expected_case_id:
        raise ValueError("persisted case packet case_id does not match requested case_id")

    validation = validate_case_packet(packet)
    if not validation["valid"]:
        raise ValueError(f"persisted case packet is invalid: {', '.join(validation['errors'])}")

    from orchestrator.case_packet_entry_preservation import validate_case_scoped_entry_collection

    for field in _ENTRY_KIND_TO_CASE_PACKET_FIELD.values():
        try:
            validate_case_scoped_entry_collection(packet[field])
        except ValueError as error:
            raise ValueError(f"persisted {field} are malformed: {error}") from error

    return deepcopy(packet)


def _identified_entry_ids(entries: list[Any]) -> list[str]:
    return [entry["entry_id"] for entry in entries if isinstance(entry, Mapping) and "entry_id" in entry]


def _validate_whole_packet_update_preserves_identities(existing: dict[str, Any], candidate: dict[str, Any]) -> None:
    for field in _ENTRY_KIND_TO_CASE_PACKET_FIELD.values():
        if _identified_entry_ids(existing[field]) != _identified_entry_ids(candidate[field]):
            raise ValueError(
                f"whole-packet update changes explicit {field} identities; "
                "use save_case_packet_entry_preservation_operation"
            )


def save_case_packet(packet: dict, *, entry_operation: Mapping[str, Any] | None = None) -> Path:
    candidate = _validate_persisted_case_packet(packet)
    case_id = candidate["case_id"]
    path = _case_packet_path(case_id)

    if path.exists():
        existing = load_case_packet(case_id)
        if entry_operation is None:
            _validate_whole_packet_update_preserves_identities(existing, candidate)
        else:
            expected = apply_case_packet_entry_preservation_operation(existing, entry_operation)["case_packet"]
            if candidate != expected:
                raise ValueError("case-packet update does not match the explicit entry preservation operation")

    atomic_write_json(path, candidate)
    return path


def load_case_packet(case_id: str) -> dict:
    normalized_case_id = _normalize_scalar(case_id)
    path = _case_packet_path(normalized_case_id)
    try:
        packet = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise ValueError(f"malformed persisted case packet JSON: {error.msg}") from error
    return _validate_persisted_case_packet(packet, expected_case_id=normalized_case_id)


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


def apply_case_packet_entry_preservation_operation(
    packet: Mapping[str, Any], operation: Mapping[str, Any]
) -> dict[str, Any]:
    """Apply one explicit source/fact transition to an in-memory case packet.

    The caller supplies the case-scoped entry identity and transition.  This
    producer delegates all entry semantics to the preservation contract and
    deliberately does not save a packet, infer identity, or associate evidence.
    """
    if not isinstance(packet, Mapping):
        raise ValueError("packet must be a mapping")

    # The local import keeps the pure contract's existing dependency on this
    # module's case-id validation rule acyclic.
    from orchestrator.case_packet_entry_preservation import (
        apply_case_scoped_entry_operation,
        normalize_case_scoped_entry_operation,
    )

    supplied_packet = dict(packet)
    normalized_packet = normalize_case_packet(supplied_packet)
    normalized_operation = normalize_case_scoped_entry_operation(operation)
    if normalized_packet["case_id"] != normalized_operation["case_id"]:
        raise ValueError("operation case_id does not match packet case_id")

    field = _ENTRY_KIND_TO_CASE_PACKET_FIELD[normalized_operation["entry_kind"]]
    preservation_result = apply_case_scoped_entry_operation(
        normalized_packet[field], normalized_operation
    )
    updated_packet = deepcopy(supplied_packet)
    updated_packet.update(normalized_packet)
    updated_packet[field] = preservation_result["entries"]
    return {
        "case_packet": updated_packet,
        "readback": deepcopy(preservation_result["readback"]),
    }


def save_case_packet_entry_preservation_operation(
    case_id: str, operation: Mapping[str, Any]
) -> dict[str, Any]:
    """Load, apply, and atomically save one explicit source/fact transition."""
    packet = load_case_packet(case_id)
    result = apply_case_packet_entry_preservation_operation(packet, operation)
    path = save_case_packet(result["case_packet"], entry_operation=operation)
    return {
        "case_packet": deepcopy(result["case_packet"]),
        "path": path,
        "readback": deepcopy(result["readback"]),
    }


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
