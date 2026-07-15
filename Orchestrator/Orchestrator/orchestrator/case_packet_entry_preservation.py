"""Pure, case-scoped preservation operations for selected case-packet entries.

This module deliberately has no persistence, producer, or evidence-link
integration.  Entry continuity exists only when an explicit caller declares it
through an operation; it is never inferred from an entry value or collection
layout.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from orchestrator.case_packet import _is_safe_case_id


ENTRY_KINDS = ("source_material", "extracted_fact")
OPERATION_KINDS = ("create", "preserve", "edit", "replace", "retire")

_OPERATION_FIELDS = {
    "case_id",
    "entry_kind",
    "operation",
    "entry_id",
    "payload",
    "replacement_entry_id",
}
_ENTRY_FIELDS = {"entry_id", "value"}

NON_PROOF_STATEMENTS = (
    "Caller-declared continuity is not proof of semantic equivalence.",
    "Entry identity does not establish truth.",
    "Source-material identity does not establish source quality.",
    "Fact identity does not establish fact correctness.",
    "Replacement does not establish that the new entry is better.",
    "No persistence or evidence-link adoption occurred.",
)


def _normalized_required_string(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a non-empty string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field} must be a non-empty string")
    return normalized


def _optional_normalized_entry_id(operation: Mapping[str, Any], field: str) -> str | None:
    if field not in operation:
        return None
    return _normalized_required_string(operation[field], field)


def normalize_case_scoped_entry_operation(operation: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize one caller-declared preservation operation."""
    if not isinstance(operation, Mapping):
        raise ValueError("operation must be a mapping")

    unexpected_fields = sorted(set(operation) - _OPERATION_FIELDS)
    if unexpected_fields:
        raise ValueError(f"operation contains unsupported fields: {', '.join(unexpected_fields)}")

    case_id = _normalized_required_string(operation.get("case_id"), "case_id")
    if not _is_safe_case_id(case_id):
        raise ValueError("case_id contains unsafe characters")

    entry_kind = _normalized_required_string(operation.get("entry_kind"), "entry_kind")
    if entry_kind not in ENTRY_KINDS:
        raise ValueError(f"unsupported entry_kind: {entry_kind}")

    operation_kind = _normalized_required_string(operation.get("operation"), "operation")
    if operation_kind not in OPERATION_KINDS:
        raise ValueError(f"unsupported operation: {operation_kind}")

    entry_id = _optional_normalized_entry_id(operation, "entry_id")
    replacement_entry_id = _optional_normalized_entry_id(operation, "replacement_entry_id")
    payload_is_present = "payload" in operation
    payload = operation.get("payload")

    if entry_id is None:
        raise ValueError("entry_id is required")

    if operation_kind in ("create", "edit", "replace"):
        if not payload_is_present or payload is None:
            raise ValueError(f"payload is required for {operation_kind}")
    elif payload_is_present:
        raise ValueError(f"payload is not allowed for {operation_kind}")

    if operation_kind == "replace":
        if replacement_entry_id is None:
            raise ValueError("replacement_entry_id is required for replace")
        if replacement_entry_id == entry_id:
            raise ValueError("replacement_entry_id must differ from entry_id")
    elif replacement_entry_id is not None:
        raise ValueError(f"replacement_entry_id is not allowed for {operation_kind}")

    normalized: dict[str, Any] = {
        "case_id": case_id,
        "entry_kind": entry_kind,
        "operation": operation_kind,
        "entry_id": entry_id,
    }
    if payload_is_present:
        normalized["payload"] = deepcopy(payload)
    if replacement_entry_id is not None:
        normalized["replacement_entry_id"] = replacement_entry_id
    return normalized


def _identified_entries(current_entries: list[Any]) -> dict[str, int]:
    identified: dict[str, int] = {}
    for index, entry in enumerate(current_entries):
        if not isinstance(entry, Mapping) or "entry_id" not in entry:
            continue
        if set(entry) != _ENTRY_FIELDS:
            raise ValueError("structured entry must contain exactly entry_id and value")
        stored_entry_id = entry["entry_id"]
        entry_id = _normalized_required_string(stored_entry_id, "existing entry_id")
        if stored_entry_id != entry_id:
            raise ValueError("existing structured entry_id is noncanonical")
        if entry["value"] is None:
            raise ValueError("structured entry value must not be null")
        if entry_id in identified:
            raise ValueError(f"duplicate existing entry_id: {entry_id}")
        identified[entry_id] = index
    return identified


def _readback(operation: Mapping[str, Any]) -> dict[str, Any]:
    operation_kind = operation["operation"]
    entry_id = operation["entry_id"]
    replacement_entry_id = operation.get("replacement_entry_id")
    transition_names = {
        "create": "created",
        "preserve": "preserved",
        "edit": "edited",
        "replace": "replaced",
        "retire": "retired",
    }
    prior_entry_id = entry_id if operation_kind != "create" else None
    if operation_kind == "retire":
        resulting_entry_id = None
    elif operation_kind == "replace":
        resulting_entry_id = replacement_entry_id
    else:
        resulting_entry_id = entry_id

    return {
        "case_id": operation["case_id"],
        "entry_kind": operation["entry_kind"],
        "operation": operation_kind,
        "transition": transition_names[operation_kind],
        "prior_entry_id": prior_entry_id,
        "resulting_entry_id": resulting_entry_id,
        "caller_declared_continuity": operation_kind in ("preserve", "edit"),
        "non_proofs": list(NON_PROOF_STATEMENTS),
    }


def apply_case_scoped_entry_operation(
    current_entries: list[Any], operation: Mapping[str, Any]
) -> dict[str, Any]:
    """Apply one explicit operation without inferring or persisting identity.

    Anonymous legacy entries are copied through unchanged but are never targets
    for preservation operations.  Only an explicit ``entry_id`` is addressable.
    """
    if not isinstance(current_entries, list):
        raise ValueError("current_entries must be a list")

    normalized = normalize_case_scoped_entry_operation(operation)
    identified = _identified_entries(current_entries)
    operation_kind = normalized["operation"]
    entry_id = normalized["entry_id"]
    replacement_entry_id = normalized.get("replacement_entry_id")

    if operation_kind == "create":
        if entry_id in identified:
            raise ValueError(f"entry_id already exists: {entry_id}")
        updated_entries = deepcopy(current_entries)
        updated_entries.append({"entry_id": entry_id, "value": deepcopy(normalized["payload"])})
    else:
        if entry_id not in identified:
            raise ValueError(f"existing entry_id not found: {entry_id}")
        target_index = identified[entry_id]
        updated_entries = deepcopy(current_entries)

        if operation_kind == "preserve":
            pass
        elif operation_kind == "edit":
            updated_entries[target_index] = {
                "entry_id": entry_id,
                "value": deepcopy(normalized["payload"]),
            }
        elif operation_kind == "replace":
            if replacement_entry_id in identified:
                raise ValueError(f"replacement_entry_id already exists: {replacement_entry_id}")
            updated_entries[target_index] = {
                "entry_id": replacement_entry_id,
                "value": deepcopy(normalized["payload"]),
            }
        else:  # retire
            del updated_entries[target_index]

    return {
        "entries": updated_entries,
        "readback": _readback(normalized),
    }


def serialize_case_scoped_entry_preservation_result(result: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deterministic, copy-safe serialization of a pure result."""
    if not isinstance(result, Mapping):
        raise ValueError("result must be a mapping")
    if set(result) != {"entries", "readback"}:
        raise ValueError("result must contain exactly entries and readback")
    if not isinstance(result["entries"], list) or not isinstance(result["readback"], Mapping):
        raise ValueError("result entries and readback have invalid types")
    return {"entries": deepcopy(result["entries"]), "readback": deepcopy(dict(result["readback"]))}
