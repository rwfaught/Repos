"""Deterministic, research-local validation for one governed historical record.

The module evaluates caller-supplied packet state.  It deliberately keeps
historical source roles, quotation limits, relationship meaning, endpoint
contexts, and conclusion posture outside the neutral evidence-link contract.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from orchestrator.evidence_link import normalize_evidence_link, validate_evidence_link


SOURCE_IDS = frozenset({f"SRC-HR-00{number}" for number in range(1, 7)})
CLAIM_IDS = frozenset({f"CLM-HR-00{number}" for number in range(1, 10)})
SOURCE_ROLES = frozenset(
    {"CORPUS_SOURCE", "UNDERLYING_SOURCE", "CORROBORATING_NON_CORPUS_SOURCE", "CONTEXTUAL_SOURCE"}
)
RELATIONSHIP_TYPES = frozenset(
    {"SUPPORTS", "CONTRADICTS", "QUALIFIES", "CONTEXTUALIZES", "METHODOLOGICAL_LIMIT"}
)
CLAIM_STATUSES = frozenset(
    {"SUPPORTED", "QUALIFIED", "CONTRADICTED", "CONTEXT_ONLY", "INSUFFICIENT", "UNSUPPORTED", "NOT_YET_DETERMINED"}
)
INFERENCE_POSTURES = frozenset({"SOURCE_CONTENT", "ANALYST_INFERENCE"})
USE_TYPES = frozenset({"PARAPHRASE", "EXACT_QUOTATION_WITH_UNL_TRANSCRIPTION_ATTRIBUTION", "ANALYTICAL_INFERENCE"})
REQUIRED_CATEGORIES = frozenset(
    {"CONTEMPORANEOUS_EVENT", "INDEPENDENT_CONTEMPORANEOUS", "INSTITUTIONAL_INTERPRETATION", "SCHOLARLY_TREATMENT", "OPERATIONAL_CONTINUITY"}
)
EXPECTED_ENDPOINTS = {
    "A": "QUALIFIED_CONCLUSION",
    "B": "MAY_10_COMPLETION_UNSUPPORTED",
    "C": "QUALIFIED_CONCLUSION",
    "D": "MAY_10_PROPOSITION_CONTRADICTED",
}
REQUIRED_NON_PROOFS = frozenset(
    {
        "no_autonomous_source_discovery",
        "no_source_authenticity_proof",
        "no_corpus_completeness_proof",
        "no_scholarly_judgment_proof",
        "no_historical_truth_beyond_supplied_packet",
        "no_provider_model_competence_proof",
        "no_generalized_research_competence_proof",
        "no_complete_provenance_proof",
        "no_phase_5_completion",
        "no_generalized_phase_6_completion",
        "no_neutral_core_admission",
        "no_product_readiness_proof",
    }
)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _records(value: Any) -> list[dict[str, Any]]:
    return [dict(item) for item in value] if isinstance(value, list) and all(isinstance(item, Mapping) for item in value) else []


def _unique_ids(records: list[dict[str, Any]], key: str, label: str, errors: list[str]) -> set[str]:
    values = [_text(record.get(key)) for record in records]
    if any(not value for value in values):
        errors.append(f"{label}_id_required")
    if len(values) != len(set(values)):
        errors.append(f"{label}_ids_must_be_unique")
    return set(values)


def _source_control_errors(source: dict[str, Any]) -> list[str]:
    source_id = _text(source.get("source_id"))
    errors: list[str] = []
    if source_id == "SRC-HR-001":
        if source.get("provenance_posture") != "SCAN_LEVEL_VERIFICATION_UNAVAILABLE":
            errors.append("src_hr_001_scan_posture_required")
        if source.get("quotation_posture") != "EXACT_QUOTATION_REQUIRES_UNL_TRANSCRIPTION_ATTRIBUTION":
            errors.append("src_hr_001_quotation_posture_required")
    elif source_id == "SRC-HR-002":
        if source.get("provenance_posture") != "AUTHORITATIVE_SCAN_NOT_VISUALLY_INSPECTED":
            errors.append("src_hr_002_scan_posture_required")
        if source.get("quotation_posture") != "EXACT_BODY_QUOTATION_NOT_AUTHORIZED":
            errors.append("src_hr_002_body_quotation_posture_required")
    elif source_id == "SRC-HR-004":
        authority = source.get("authority_posture")
        if not isinstance(authority, Mapping) or authority.get("peer_reviewed") is not False:
            errors.append("src_hr_004_peer_reviewed_must_be_false")
        if not isinstance(authority, Mapping) or authority.get("university_press") is not False:
            errors.append("src_hr_004_university_press_must_be_false")
    return errors


def validate_historical_record_packet(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Validate structural and governance constraints without selecting an answer."""
    if not isinstance(payload, Mapping):
        return {"valid": False, "errors": ["packet_must_be_mapping"], "normalized_packet": {}}
    packet = deepcopy(dict(payload))
    errors: list[str] = []
    for field in ("case_id", "question", "primary_terminal_classification", "analytical_recommendation"):
        if not _text(packet.get(field)):
            errors.append(f"case_{field}_required")
    if not isinstance(packet.get("human_disposition"), Mapping):
        errors.append("human_disposition_must_be_mapping")
    if not isinstance(packet.get("non_proofs"), list) or not REQUIRED_NON_PROOFS.issubset(set(packet.get("non_proofs", []))):
        errors.append("required_non_proofs_missing")
    if packet.get("retired_claim") != "CLM-HR-010_RETIRED_AND_RECLASSIFIED_AS_OPERATIONAL_DEFINITION_REQUIREMENT":
        errors.append("retired_claim_marker_invalid")

    sources = _records(packet.get("sources"))
    claims = _records(packet.get("claims"))
    relationships = _records(packet.get("relationships"))
    source_ids = _unique_ids(sources, "source_id", "source", errors)
    claim_ids = _unique_ids(claims, "claim_id", "claim", errors)
    _unique_ids(relationships, "relationship_id", "relationship", errors)
    corpus_source_ids = {
        _text(source.get("source_id")) for source in sources if source.get("source_role") == "CORPUS_SOURCE"
    }
    if corpus_source_ids != SOURCE_IDS:
        errors.append("source_ids_must_match_ratified_corpus")
    if claim_ids != CLAIM_IDS:
        errors.append("claim_ids_must_match_ratified_claim_register")

    for source in sources:
        source_id = _text(source.get("source_id"))
        if source.get("source_role") not in SOURCE_ROLES:
            errors.append(f"source_role_invalid:{source_id}")
        if not isinstance(source.get("source_plan_categories"), list):
            errors.append(f"source_plan_categories_must_be_list:{source_id}")
        if not _text(source.get("institution_or_origin")):
            errors.append(f"source_institution_required:{source_id}")
        if not isinstance(source.get("limitations"), list) or not isinstance(source.get("permitted_uses"), list):
            errors.append(f"source_controls_must_be_lists:{source_id}")
        if not isinstance(source.get("enabled"), bool):
            errors.append(f"source_enabled_must_be_boolean:{source_id}")
        errors.extend(_source_control_errors(source))

    for claim in claims:
        claim_id = _text(claim.get("claim_id"))
        if claim.get("declared_status") not in CLAIM_STATUSES:
            errors.append(f"claim_status_invalid:{claim_id}")
        if claim.get("inference_posture") not in INFERENCE_POSTURES:
            errors.append(f"claim_inference_posture_invalid:{claim_id}")
        if not isinstance(claim.get("required_relationship_ids"), list):
            errors.append(f"claim_required_relationship_ids_must_be_list:{claim_id}")
        if not isinstance(claim.get("enabled"), bool):
            errors.append(f"claim_enabled_must_be_boolean:{claim_id}")
    claim_by_id = {claim.get("claim_id"): claim for claim in claims}
    for claim_id in ("CLM-HR-008", "CLM-HR-009"):
        if claim_by_id.get(claim_id, {}).get("inference_posture") != "ANALYST_INFERENCE":
            errors.append(f"claim_requires_explicit_inference:{claim_id}")

    relationship_ids = {_text(item.get("relationship_id")) for item in relationships}
    source_by_id = {source.get("source_id"): source for source in sources}
    for relationship in relationships:
        relationship_id = _text(relationship.get("relationship_id"))
        if relationship.get("relationship_type") not in RELATIONSHIP_TYPES:
            errors.append(f"relationship_type_invalid:{relationship_id}")
        if relationship.get("source_role") not in SOURCE_ROLES:
            errors.append(f"relationship_source_role_invalid:{relationship_id}")
        if relationship.get("use_type") not in USE_TYPES:
            errors.append(f"relationship_use_type_invalid:{relationship_id}")
        if not isinstance(relationship.get("inference_involved"), bool) or not isinstance(relationship.get("enabled"), bool):
            errors.append(f"relationship_boolean_fields_invalid:{relationship_id}")
        link = relationship.get("neutral_evidence_link")
        link_validation = validate_evidence_link(link)
        if not link_validation["valid"]:
            errors.extend(f"neutral_link_invalid:{relationship_id}:{code}" for code in link_validation["errors"])
            continue
        normalized_link = normalize_evidence_link(link)
        source_id = normalized_link["source_reference"]
        claim_id = normalized_link["subject_reference"]["subject_id"]
        if source_id not in source_ids:
            errors.append(f"relationship_source_reference_missing:{relationship_id}")
        if claim_id not in claim_ids:
            errors.append(f"relationship_claim_reference_missing:{relationship_id}")
        if source_id in source_by_id and relationship.get("source_role") != source_by_id[source_id].get("source_role"):
            errors.append(f"relationship_source_role_mismatch:{relationship_id}")
        if source_id == "SRC-HR-001" and relationship.get("use_type") == "EXACT_QUOTATION_WITH_UNL_TRANSCRIPTION_ATTRIBUTION" and relationship.get("quotation_attribution") != "UNL_TRANSCRIPTION":
            errors.append(f"src_hr_001_exact_quote_requires_unl_attribution:{relationship_id}")
        if source_id == "SRC-HR-002" and relationship.get("use_type") == "EXACT_QUOTATION_WITH_UNL_TRANSCRIPTION_ATTRIBUTION":
            errors.append(f"src_hr_002_exact_body_quotation_not_authorized:{relationship_id}")
    for claim in claims:
        for relationship_id in claim.get("required_relationship_ids", []) if isinstance(claim.get("required_relationship_ids"), list) else []:
            if relationship_id not in relationship_ids:
                errors.append(f"claim_required_relationship_missing:{claim.get('claim_id')}:{relationship_id}")

    contexts = packet.get("endpoint_contexts")
    if not isinstance(contexts, Mapping) or set(contexts) != set(EXPECTED_ENDPOINTS):
        errors.append("endpoint_contexts_must_be_exact_a_through_d")
    elif any(contexts.get(key) != posture for key, posture in EXPECTED_ENDPOINTS.items()):
        errors.append("endpoint_context_posture_invalid")
    return {"valid": not errors, "errors": errors, "normalized_packet": packet}


def _source_plan_state(packet: dict[str, Any]) -> dict[str, str]:
    enabled_categories = {
        category
        for source in _records(packet.get("sources"))
        if source.get("enabled") and source.get("source_role") == "CORPUS_SOURCE"
        for category in source.get("source_plan_categories", [])
    }
    return {category: "SATISFIED" if category in enabled_categories else "EXPLICIT_GAP" for category in sorted(REQUIRED_CATEGORIES)}


def _claim_states(packet: dict[str, Any]) -> dict[str, str]:
    relationships = _records(packet.get("relationships"))
    source_enabled = {source.get("source_id"): bool(source.get("enabled")) for source in _records(packet.get("sources"))}
    states: dict[str, str] = {}
    for claim in _records(packet.get("claims")):
        claim_id = claim.get("claim_id")
        if not claim.get("enabled"):
            states[claim_id] = "NOT_YET_DETERMINED"
            continue
        required = set(claim.get("required_relationship_ids", []))
        selected = [item for item in relationships if item.get("relationship_id") in required]
        active = [item for item in selected if item.get("enabled") and source_enabled.get(normalize_evidence_link(item.get("neutral_evidence_link"))["source_reference"], False)]
        if len(active) != len(required):
            states[claim_id] = "INSUFFICIENT"
        elif any(item.get("relationship_type") == "CONTRADICTS" for item in active):
            states[claim_id] = "CONTRADICTED"
        elif any(item.get("relationship_type") in {"QUALIFIES", "METHODOLOGICAL_LIMIT"} for item in active):
            states[claim_id] = "QUALIFIED"
        elif any(item.get("relationship_type") == "SUPPORTS" for item in active):
            states[claim_id] = "SUPPORTED"
        else:
            states[claim_id] = "CONTEXT_ONLY"
    return states


def evaluate_historical_record_packet(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Return a deterministic governed result from packet state only."""
    validation = validate_historical_record_packet(payload)
    if not validation["valid"]:
        return {"evaluation_status": "blocked", "primary_terminal_classification": "INSUFFICIENT_EVIDENCE", "validation_errors": list(validation["errors"]), "result": None}
    packet = validation["normalized_packet"]
    source_plan = _source_plan_state(packet)
    claim_states = _claim_states(packet)
    material_insufficient = [
        claim.get("claim_id") for claim in _records(packet.get("claims"))
        if claim.get("materiality") == "MATERIAL" and claim_states.get(claim.get("claim_id")) == "INSUFFICIENT"
    ]
    source_plan_valid = all(state == "SATISFIED" for state in source_plan.values())
    if not source_plan_valid or material_insufficient:
        terminal = "INSUFFICIENT_EVIDENCE"
    elif any(state == "QUALIFIED" for state in claim_states.values()) and any(
        value in {"MAY_10_COMPLETION_UNSUPPORTED", "MAY_10_PROPOSITION_CONTRADICTED"}
        for value in packet["endpoint_contexts"].values()
    ):
        terminal = "QUALIFIED_CONCLUSION"
    else:
        terminal = "INSUFFICIENT_EVIDENCE"
    return {
        "evaluation_status": "ready",
        "primary_terminal_classification": terminal,
        "validation_errors": [],
        "result": {
            "case_id": packet["case_id"],
            "corpus_count": sum(1 for source in _records(packet["sources"]) if source.get("enabled") and source.get("source_role") == "CORPUS_SOURCE"),
            "source_plan": source_plan,
            "source_plan_valid": source_plan_valid,
            "claim_states": claim_states,
            "material_operational_claims": "BLOCKED_OR_DOWNGRADED" if material_insufficient else "SUPPORTED_OR_QUALIFIED",
            "endpoint_contexts": deepcopy(packet["endpoint_contexts"]),
            "provenance_and_quotation_limits_preserved": True,
            "typed_evidence_relationships_preserved": True,
            "inference_remains_explicit": True,
            "recommendation_disposition_separation_preserved": True,
            "analytical_recommendation": packet["analytical_recommendation"],
            "human_disposition": deepcopy(packet["human_disposition"]),
            "non_proofs": list(packet["non_proofs"]),
        },
    }


def derive_operational_evidence_diagnostic(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Disable the one marked operational bundle without mutating the input."""
    packet = deepcopy(dict(payload)) if isinstance(payload, Mapping) else {}
    for source in packet.get("sources", []) if isinstance(packet.get("sources"), list) else []:
        if isinstance(source, dict) and source.get("operational_bundle"):
            source["enabled"] = False
    for relationship in packet.get("relationships", []) if isinstance(packet.get("relationships"), list) else []:
        if isinstance(relationship, dict) and relationship.get("operational_bundle"):
            relationship["enabled"] = False
    return packet
