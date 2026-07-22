"""Deterministic, caller-governed evidence-linked synthesis transformation.

This module validates and presents a single explicitly structured dossier
packet.  It neither extracts records nor makes analytical or authorization
decisions: those remain caller supplied.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from orchestrator.evidence_link import NON_PROOFS as EVIDENCE_LINK_NON_PROOFS
from orchestrator.evidence_link import normalize_evidence_link, validate_evidence_link


CONTRACT_NAME = "narrow_evidence_linked_synthesis_transformation"
BOUNDARY = "ORCHESTRATOR_NARROW_EVIDENCE_LINKED_SYNTHESIS_TRANSFORMATION_SOURCE_TEST_DOCS_IMPLEMENTATION"

STATEMENT_CLASSIFICATIONS = frozenset(
    {
        "observed_record",
        "reported_statement",
        "reported_estimate",
        "derived_observation",
        "analyst_inference",
        "assumption",
        "constraint",
        "client_preference",
    }
)
MISSING_INFORMATION_STATUSES = frozenset(
    {"unknown", "not_collected", "unavailable", "not_applicable", "resolved"}
)
TRANSFORMATION_POSTURES = frozenset(
    {"copied", "selected", "grouped", "derived", "inferred", "judged", "presentation_only"}
)

_CASE_FRAME_FIELDS = (
    "case_id",
    "objective",
    "included_scope",
    "excluded_scope",
    "decision_owner",
    "review_posture",
)
_COLLECTIONS = (
    ("source_inventory", "source_id"),
    ("statement_register", "statement_id"),
    ("constraint_register", "constraint_id"),
    ("contradiction_register", "contradiction_id"),
    ("missing_information_register", "gap_id"),
    ("candidates", "candidate_id"),
    ("assessments", "assessment_id"),
    ("recommendation_claims", "claim_id"),
    ("decision_gates", "gate_id"),
    ("authorizations", "authorization_id"),
    ("revisions", "revision_id"),
)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    return [_mapping(item) for item in value] if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    return [_text(item) for item in value if _text(item)] if isinstance(value, list) else []


def _index(records: list[dict[str, Any]], identity_key: str) -> set[str]:
    return {_text(record.get(identity_key)) for record in records if _text(record.get(identity_key))}


def _require_reference(
    errors: list[str], reference: str, known: set[str], error_code: str
) -> None:
    if reference and reference not in known:
        errors.append(f"{error_code}:{reference}")


def normalize_synthesis_packet(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Copy a packet into its deterministic, serialization-ready shape."""
    supplied = _mapping(payload)
    case_frame = _mapping(supplied.get("case_frame"))
    normalized_frame = {
        "case_id": _text(case_frame.get("case_id")),
        "objective": _text(case_frame.get("objective")),
        "included_scope": _string_list(case_frame.get("included_scope")),
        "excluded_scope": _string_list(case_frame.get("excluded_scope")),
        "decision_owner": _text(case_frame.get("decision_owner")),
        "review_posture": _text(case_frame.get("review_posture")),
    }
    statements = _records(supplied.get("statement_register"))
    for statement in statements:
        if not _text(statement.get("text")) and "value" in statement:
            statement["text"] = _text(statement.get("value"))
    assessments = _records(supplied.get("assessments"))
    for assessment in assessments:
        if not _text(assessment.get("rating")) and "classification" in assessment:
            assessment["rating"] = _text(assessment.get("classification"))
    normalized = {
        "case_frame": normalized_frame,
        "source_inventory": _records(supplied.get("source_inventory")),
        "statement_register": statements,
        "constraint_register": _records(supplied.get("constraint_register")),
        "contradiction_register": _records(supplied.get("contradiction_register")),
        "missing_information_register": _records(supplied.get("missing_information_register")),
        "problem_frame": _mapping(supplied.get("problem_frame")),
        "candidates": _records(supplied.get("candidates")),
        "assessments": assessments,
        "prioritization_judgment": _mapping(supplied.get("prioritization_judgment")),
        "recommendation_claims": _records(supplied.get("recommendation_claims")),
        "evidence_links": [normalize_evidence_link(item) for item in supplied.get("evidence_links", [])]
        if isinstance(supplied.get("evidence_links", []), list)
        else [],
        "decision_gates": _records(supplied.get("decision_gates")),
        "authorizations": _records(supplied.get("authorizations")),
        "non_authorizations": _records(supplied.get("non_authorizations")),
        "non_proofs": _string_list(supplied.get("non_proofs")),
        "next_bounded_action": _mapping(supplied.get("next_bounded_action")),
        "disposition": _mapping(supplied.get("disposition")),
        "revisions": _records(supplied.get("revisions")),
    }
    return deepcopy(normalized)


def validate_synthesis_packet(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Validate explicit references and blocking conditions without inference."""
    errors: list[str] = []
    if not isinstance(payload, Mapping):
        return {"valid": False, "errors": ["synthesis_packet_must_be_mapping"], "normalized_packet": normalize_synthesis_packet(payload)}

    packet = normalize_synthesis_packet(payload)
    case_frame = packet["case_frame"]
    for field in _CASE_FRAME_FIELDS:
        value = case_frame[field]
        if not value:
            errors.append(f"case_frame_{field}_required")

    indexes: dict[str, set[str]] = {}
    for collection_name, identity_key in _COLLECTIONS:
        supplied_value = payload.get(collection_name)
        if not isinstance(supplied_value, list):
            errors.append(f"{collection_name}_must_be_list")
        records = packet[collection_name]
        for position, record in enumerate(records):
            identity = _text(record.get(identity_key))
            if not identity:
                errors.append(f"{collection_name}_{identity_key}_required:{position}")
        identities = _index(records, identity_key)
        if len(identities) != len(records):
            errors.append(f"{collection_name}_identities_must_be_unique")
        indexes[collection_name] = identities

    if not packet["source_inventory"]:
        errors.append("source_inventory_required")
    for source in packet["source_inventory"]:
        source_id = _text(source.get("source_id"))
        for field in ("source_type", "label", "status"):
            if not _text(source.get(field)):
                errors.append(f"source_{field}_required:{source_id or 'unknown'}")
        if not isinstance(source.get("limitations"), list):
            errors.append(f"source_limitations_must_be_list:{source_id or 'unknown'}")
        if not isinstance(source.get("permitted_use"), list):
            errors.append(f"source_permitted_use_must_be_list:{source_id or 'unknown'}")

    source_ids = indexes["source_inventory"]
    statement_ids = indexes["statement_register"]
    constraint_ids = indexes["constraint_register"]
    contradiction_ids = indexes["contradiction_register"]
    gap_ids = indexes["missing_information_register"]
    candidate_ids = indexes["candidates"]
    authorization_ids = indexes["authorizations"]
    claim_ids = indexes["recommendation_claims"]

    for statement in packet["statement_register"]:
        statement_id = _text(statement.get("statement_id"))
        if not _text(statement.get("text")):
            errors.append(f"statement_text_required:{statement_id or 'unknown'}")
        classification = _text(statement.get("classification"))
        if classification not in STATEMENT_CLASSIFICATIONS:
            errors.append(f"statement_classification_invalid:{statement_id or 'unknown'}")
        for field in ("confidence_or_qualification", "confirmation_posture", "materiality"):
            if not _text(statement.get(field)):
                errors.append(f"statement_{field}_required:{statement_id or 'unknown'}")
        if "source_references" in statement and not isinstance(statement.get("source_references"), list):
            errors.append(f"statement_source_references_must_be_list:{statement_id or 'unknown'}")
        for source_id in _string_list(statement.get("source_references")):
            _require_reference(errors, source_id, source_ids, "statement_source_reference_missing")

    for constraint in packet["constraint_register"]:
        constraint_id = _text(constraint.get("constraint_id"))
        for field in ("text", "type", "source_or_owner_reference", "hardness", "status"):
            if not _text(constraint.get(field)):
                errors.append(f"constraint_{field}_required:{constraint_id or 'unknown'}")

    for contradiction in packet["contradiction_register"]:
        contradiction_id = _text(contradiction.get("contradiction_id"))
        references = _string_list(contradiction.get("statement_references"))
        if not references:
            errors.append(f"contradiction_statement_references_required:{contradiction_id or 'unknown'}")
        for statement_id in references:
            _require_reference(errors, statement_id, statement_ids, "contradiction_statement_reference_missing")
        for field in ("description", "materiality", "resolution_status", "effect_on_assessment"):
            if not _text(contradiction.get(field)):
                errors.append(f"contradiction_{field}_required:{contradiction_id or 'unknown'}")

    for gap in packet["missing_information_register"]:
        gap_id = _text(gap.get("gap_id"))
        for field in ("question", "why_it_matters", "status", "effect_if_unresolved", "blocking_level"):
            if not _text(gap.get(field)):
                errors.append(f"gap_{field}_required:{gap_id or 'unknown'}")
        if _text(gap.get("status")) not in MISSING_INFORMATION_STATUSES:
            errors.append(f"gap_status_invalid:{gap_id or 'unknown'}")
        if _text(gap.get("blocking_level")) == "critical" and _text(gap.get("status")) not in {"resolved", "not_applicable"}:
            errors.append(f"critical_gap_blocks_synthesis:{gap_id or 'unknown'}")

    problem = packet["problem_frame"]
    for field in ("problem_id", "problem_statement", "affected_context", "judgment_note"):
        if not _text(problem.get(field)):
            errors.append(f"problem_frame_{field}_required")
    for statement_id in _string_list(problem.get("supporting_statement_references")):
        _require_reference(errors, statement_id, statement_ids, "problem_supporting_statement_missing")
    for statement_id in _string_list(problem.get("qualifying_statement_references")):
        _require_reference(errors, statement_id, statement_ids, "problem_qualifying_statement_missing")

    for candidate in packet["candidates"]:
        candidate_id = _text(candidate.get("candidate_id"))
        for field in ("description", "mechanism", "scope"):
            if not _text(candidate.get(field)):
                errors.append(f"candidate_{field}_required:{candidate_id or 'unknown'}")
        for list_field in ("dependencies", "assessment_dimensions", "supporting_references", "weakening_references", "unresolved_gap_references", "constraint_compatibility"):
            if not isinstance(candidate.get(list_field), list):
                errors.append(f"candidate_{list_field}_must_be_list:{candidate_id or 'unknown'}")
        for statement_id in _string_list(candidate.get("supporting_references")) + _string_list(candidate.get("weakening_references")):
            _require_reference(errors, statement_id, statement_ids, "candidate_statement_reference_missing")
        for gap_id in _string_list(candidate.get("unresolved_gap_references")):
            _require_reference(errors, gap_id, gap_ids, "candidate_gap_reference_missing")
        for compatibility in _records(candidate.get("constraint_compatibility")):
            constraint_id = _text(compatibility.get("constraint_id"))
            _require_reference(errors, constraint_id, constraint_ids, "candidate_constraint_reference_missing")
            if _text(compatibility.get("status")) == "violated":
                matching = [item for item in packet["constraint_register"] if _text(item.get("constraint_id")) == constraint_id]
                if matching and _text(matching[0].get("hardness")) == "hard":
                    errors.append(f"hard_constraint_violated:{candidate_id or 'unknown'}:{constraint_id}")

    for assessment in packet["assessments"]:
        assessment_id = _text(assessment.get("assessment_id"))
        _require_reference(errors, _text(assessment.get("candidate_reference")), candidate_ids, "assessment_candidate_reference_missing")
        for field in ("dimension", "rating", "rationale", "judgment_note"):
            if not _text(assessment.get(field)):
                errors.append(f"assessment_{field}_required:{assessment_id or 'unknown'}")
        for statement_id in _string_list(assessment.get("evidence_references")):
            _require_reference(errors, statement_id, statement_ids, "assessment_evidence_reference_missing")
        for gap_id in _string_list(assessment.get("gap_references")):
            _require_reference(errors, gap_id, gap_ids, "assessment_gap_reference_missing")

    prioritization = packet["prioritization_judgment"]
    for field in ("prioritization_id", "rationale", "judgment_owner"):
        if not _text(prioritization.get(field)):
            errors.append(f"prioritization_{field}_required")
    selected_candidate_id = _text(prioritization.get("selected_candidate_id"))
    no_recommendation = bool(prioritization.get("no_recommendation"))
    if not selected_candidate_id and not no_recommendation:
        errors.append("prioritization_selection_or_no_recommendation_required")
    if selected_candidate_id:
        _require_reference(errors, selected_candidate_id, candidate_ids, "prioritization_candidate_reference_missing")
        selected = next((item for item in packet["candidates"] if _text(item.get("candidate_id")) == selected_candidate_id), {})
        if _text(selected.get("identity_status")) in {"retired", "replaced"}:
            errors.append(f"selected_candidate_identity_not_active:{selected_candidate_id}")
        granted = {
            _text(item.get("authorization_id"))
            for item in packet["authorizations"]
            if _text(item.get("status")) == "authorized"
        }
        for authorization_id in _string_list(selected.get("required_authorization_ids")):
            _require_reference(errors, authorization_id, authorization_ids, "required_authorization_reference_missing")
            if authorization_id not in granted:
                errors.append(f"required_authorization_absent:{authorization_id}")

    valid_link_subjects = set(statement_ids) | set(claim_ids)
    claim_link_ids: set[str] = set()
    for link_position, raw_link in enumerate(payload.get("evidence_links", []) if isinstance(payload.get("evidence_links", []), list) else []):
        link_validation = validate_evidence_link(raw_link)
        if not link_validation["valid"]:
            errors.extend(f"evidence_link_invalid:{error}:{link_position}" for error in link_validation["errors"])
            continue
        link = link_validation["normalized_evidence_link"]
        source_id = link["source_reference"]
        if source_id not in source_ids:
            errors.append(f"evidence_link_source_reference_missing:{source_id}")
        subject_id = link["subject_reference"]["subject_id"]
        if subject_id not in valid_link_subjects:
            errors.append(f"evidence_link_subject_reference_missing:{subject_id}")
        if link["subject_reference"]["subject_type"] == "recommendation_claim":
            claim_link_ids.add(subject_id)

    for claim in packet["recommendation_claims"]:
        claim_id = _text(claim.get("claim_id"))
        for field in ("text", "materiality", "judgment_posture"):
            if not _text(claim.get(field)):
                errors.append(f"recommendation_claim_{field}_required:{claim_id or 'unknown'}")
        if _text(claim.get("judgment_posture")) not in TRANSFORMATION_POSTURES:
            errors.append(f"recommendation_claim_judgment_posture_invalid:{claim_id or 'unknown'}")
        if not isinstance(claim.get("statement_references"), list):
            errors.append(f"recommendation_claim_statement_references_must_be_list:{claim_id or 'unknown'}")
        for statement_id in _string_list(claim.get("statement_references")):
            _require_reference(errors, statement_id, statement_ids, "recommendation_claim_statement_reference_missing")
        for contradiction_id in _string_list(claim.get("contradiction_references")):
            _require_reference(errors, contradiction_id, contradiction_ids, "recommendation_claim_contradiction_reference_missing")
        for gap_id in _string_list(claim.get("gap_references")):
            _require_reference(errors, gap_id, gap_ids, "recommendation_claim_gap_reference_missing")
        if _text(claim.get("materiality")) == "material":
            if not _string_list(claim.get("statement_references")) or claim_id not in claim_link_ids:
                errors.append(f"material_recommendation_claim_requires_registered_basis:{claim_id or 'unknown'}")

    for gate in packet["decision_gates"]:
        gate_id = _text(gate.get("gate_id"))
        for field in ("description", "status"):
            if not _text(gate.get(field)):
                errors.append(f"decision_gate_{field}_required:{gate_id or 'unknown'}")
        for gap_id in _string_list(gate.get("gap_references")):
            _require_reference(errors, gap_id, gap_ids, "decision_gate_gap_reference_missing")

    for revision in packet["revisions"]:
        revision_id = _text(revision.get("revision_id"))
        original = _text(revision.get("original_recommendation_id"))
        revised = _text(revision.get("revised_recommendation_id"))
        if not original or not revised or original == revised:
            errors.append(f"revision_must_reference_distinct_original_and_revised_recommendations:{revision_id or 'unknown'}")
        for claim_id in (original, revised):
            _require_reference(errors, claim_id, claim_ids, "revision_recommendation_reference_missing")

    return {"valid": not errors, "errors": errors, "normalized_packet": packet}


def _surface(records: list[dict[str, Any]], posture: str) -> list[dict[str, Any]]:
    return [{"transform_posture": posture, **deepcopy(record)} for record in records]


def build_evidence_linked_synthesis_package(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Build a deterministic review package or a clearly blocked result."""
    validation = validate_synthesis_packet(payload)
    if not validation["valid"]:
        return {
            "contract_name": CONTRACT_NAME,
            "boundary": BOUNDARY,
            "synthesis_status": "blocked",
            "successful_synthesis": False,
            "validation_errors": list(validation["errors"]),
            "recommendation_package": None,
        }

    packet = validation["normalized_packet"]
    selected_candidate_id = _text(packet["prioritization_judgment"].get("selected_candidate_id"))
    selected_candidate = next(
        (candidate for candidate in packet["candidates"] if _text(candidate.get("candidate_id")) == selected_candidate_id),
        None,
    )
    claims = []
    for claim in packet["recommendation_claims"]:
        claims.append(
            {
                "transform_posture": "selected",
                **deepcopy(claim),
                "evidence_basis": list(_string_list(claim.get("statement_references"))),
                "qualifications": list(_string_list(claim.get("qualification_references"))),
                "contradicting_basis": list(_string_list(claim.get("contradiction_references"))),
                "unresolved_gaps": list(_string_list(claim.get("gap_references"))),
            }
        )

    recommendation_package = {
        "case_frame": {"transform_posture": "copied", **deepcopy(packet["case_frame"])},
        "problem_statement": {"transform_posture": "copied", **deepcopy(packet["problem_frame"])},
        "evidence_summary": {"transform_posture": "grouped", "sources": _surface(packet["source_inventory"], "copied"), "statements": _surface(packet["statement_register"], "copied")},
        "evidence_classifications": {"transform_posture": "grouped", "classifications": [statement.get("classification") for statement in packet["statement_register"]]},
        "qualifications": {"transform_posture": "grouped", "statement_references": [statement.get("statement_id") for statement in packet["statement_register"] if _text(statement.get("confidence_or_qualification"))]},
        "contradictions": _surface(packet["contradiction_register"], "copied"),
        "missing_information": _surface(packet["missing_information_register"], "copied"),
        "constraints": _surface(packet["constraint_register"], "copied"),
        "candidate_comparison": _surface(packet["candidates"], "selected"),
        "selected_recommendation": {"transform_posture": "judged", "prioritization": deepcopy(packet["prioritization_judgment"]), "candidate": deepcopy(selected_candidate) if selected_candidate else None},
        "recommendation_claims": claims,
        "evidence_associations": {"transform_posture": "copied", "links": deepcopy(packet["evidence_links"]), "non_proofs": list(EVIDENCE_LINK_NON_PROOFS)},
        "risks_and_failure_modes": {"transform_posture": "grouped", "assessments": _surface(packet["assessments"], "copied")},
        "decision_gates": _surface(packet["decision_gates"], "copied"),
        "explicit_authorizations": _surface(packet["authorizations"], "copied"),
        "explicit_non_authorizations": _surface(packet["non_authorizations"], "copied"),
        "explicit_non_proofs": {"transform_posture": "presentation_only", "items": list(packet["non_proofs"])},
        "next_bounded_action": {"transform_posture": "selected", **deepcopy(packet["next_bounded_action"])},
        "disposition_surface": {"transform_posture": "copied", **deepcopy(packet["disposition"])},
        "revision_relationships": _surface(packet["revisions"], "copied"),
    }
    return {
        "contract_name": CONTRACT_NAME,
        "boundary": BOUNDARY,
        "synthesis_status": "ready",
        "successful_synthesis": True,
        "validation_errors": [],
        "recommendation_package": recommendation_package,
    }
