"""Neutral asserted-association records between typed subjects and sources."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping


CONTRACT_NAME = "neutral_evidence_link"
BOUNDARY = "NEUTRAL_EVIDENCE_LINK_CONTRACT_SOURCE_TEST_DOCS_IMPLEMENTATION"

_SUBJECT_TYPE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

NON_PROOFS = (
    "evidence_link_records_an_asserted_association_only",
    "evidence_link_does_not_establish_truth",
    "evidence_link_does_not_establish_source_quality",
    "evidence_link_does_not_establish_evidentiary_sufficiency",
    "evidence_link_does_not_establish_recommendation_correctness",
    "evidence_link_does_not_authorize_action",
)


def _normalize_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _normalized_subject_reference(value: Any) -> dict[str, str]:
    if not isinstance(value, Mapping):
        return {"subject_type": "", "subject_id": ""}
    return {
        "subject_type": _normalize_text(value.get("subject_type")),
        "subject_id": _normalize_text(value.get("subject_id")),
    }


@dataclass(frozen=True)
class TypedSubjectReference:
    subject_type: str
    subject_id: str

    def to_dict(self) -> dict[str, str]:
        return {
            "subject_type": self.subject_type,
            "subject_id": self.subject_id,
        }


@dataclass(frozen=True)
class NeutralEvidenceLink:
    evidence_link_id: str
    subject_reference: TypedSubjectReference
    source_reference: str
    source_locator: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_link_id": self.evidence_link_id,
            "subject_reference": self.subject_reference.to_dict(),
            "source_reference": self.source_reference,
            "source_locator": self.source_locator,
        }


def normalize_evidence_link(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Return a copied, serialization-ready evidence-link mapping.

    Normalization never mutates a caller-supplied mapping. Validation remains
    responsible for rejecting malformed values instead of silently accepting
    them.
    """
    if not isinstance(payload, Mapping):
        return {
            "evidence_link_id": "",
            "subject_reference": {"subject_type": "", "subject_id": ""},
            "source_reference": "",
            "source_locator": None,
        }

    locator = payload.get("source_locator")
    return {
        "evidence_link_id": _normalize_text(payload.get("evidence_link_id")),
        "subject_reference": _normalized_subject_reference(payload.get("subject_reference")),
        "source_reference": _normalize_text(payload.get("source_reference")),
        "source_locator": _normalize_text(locator) if isinstance(locator, str) else None,
    }


def validate_evidence_link(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Validate one neutral evidence link with stable, machine-readable errors."""
    errors: list[str] = []
    normalized = normalize_evidence_link(payload)

    if not isinstance(payload, Mapping):
        errors.append("evidence_link_must_be_mapping")
        return {
            "valid": False,
            "errors": errors,
            "normalized_evidence_link": normalized,
        }

    if not normalized["evidence_link_id"]:
        errors.append("evidence_link_id_required")

    subject = payload.get("subject_reference")
    if not isinstance(subject, Mapping):
        errors.append("subject_reference_must_be_mapping")
    else:
        subject_type = normalized["subject_reference"]["subject_type"]
        subject_id = normalized["subject_reference"]["subject_id"]
        if not subject_type:
            errors.append("subject_reference_subject_type_required")
        elif _SUBJECT_TYPE_PATTERN.fullmatch(subject_type) is None:
            errors.append("subject_reference_subject_type_invalid")
        if not subject_id:
            errors.append("subject_reference_subject_id_required")

    if not normalized["source_reference"]:
        errors.append("source_reference_required")

    if "source_locator" in payload and payload.get("source_locator") is not None:
        if not isinstance(payload.get("source_locator"), str):
            errors.append("source_locator_must_be_string_or_null")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "normalized_evidence_link": normalized,
    }


def build_neutral_evidence_link(payload: Mapping[str, Any] | Any) -> NeutralEvidenceLink:
    """Build a typed neutral evidence link or raise a stable validation error."""
    validation = validate_evidence_link(payload)
    if not validation["valid"]:
        raise ValueError("; ".join(validation["errors"]))

    normalized = validation["normalized_evidence_link"]
    subject = normalized["subject_reference"]
    return NeutralEvidenceLink(
        evidence_link_id=normalized["evidence_link_id"],
        subject_reference=TypedSubjectReference(
            subject_type=subject["subject_type"],
            subject_id=subject["subject_id"],
        ),
        source_reference=normalized["source_reference"],
        source_locator=normalized["source_locator"],
    )


def build_neutral_evidence_link_readback(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Produce a concise, non-authorizing readback for one evidence link."""
    validation = validate_evidence_link(payload)
    return {
        "evidence_link_contract": True,
        "contract_name": CONTRACT_NAME,
        "boundary": BOUNDARY,
        "valid": validation["valid"],
        "association_recorded": validation["valid"],
        "evidence_link": (
            validation["normalized_evidence_link"] if validation["valid"] else None
        ),
        "validation_errors": list(validation["errors"]),
        "association_statement": (
            "The record asserts an association between the typed subject and source reference."
        ),
        "non_proofs": list(NON_PROOFS),
    }
