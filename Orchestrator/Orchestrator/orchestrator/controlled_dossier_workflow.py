"""One deterministic, controlled fictional dossier-workflow proof.

This coordinator joins the existing case-packet persistence, neutral evidence
link, and evidence-linked synthesis seams for one caller-supplied workflow
input.  It does not infer analytical content, discover evidence links, or
authorize work beyond the caller's explicit disposition.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from orchestrator.case_packet import load_case_packet, save_case_packet
from orchestrator.evidence_linked_synthesis import build_evidence_linked_synthesis_package


CONTRACT_NAME = "controlled_dossier_workflow"
BOUNDARY = "ORCHESTRATOR_REPEATABLE_FICTIONAL_CONTROLLED_DOSSIER_WORKFLOW_SOURCE_TEST_PROOF"
COMPLETED_CLASSIFICATION = "controlled_dossier_workflow_completed"
BLOCKED_CLASSIFICATION = "controlled_dossier_workflow_blocked"

WORKFLOW_NON_PROOFS = (
    "workflow_does_not_establish_evidence_truth",
    "workflow_does_not_establish_recommendation_correctness",
    "workflow_does_not_authorize_implementation_or_excluded_actions",
    "workflow_does_not_execute_a_provider_model_or_runtime",
    "workflow_does_not_establish_production_readiness",
)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _blocked(errors: list[str], *, synthesis_result: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "contract_name": CONTRACT_NAME,
        "boundary": BOUNDARY,
        "workflow_status": "blocked",
        "workflow_classification": BLOCKED_CLASSIFICATION,
        "completed": False,
        "validation_errors": list(errors),
        "synthesis_result": deepcopy(synthesis_result),
        "explicit_non_proofs": list(WORKFLOW_NON_PROOFS),
    }


def _identified_values(entries: Any, *, entry_kind: str, target_identity: str) -> tuple[list[dict[str, Any]], list[str]]:
    if not isinstance(entries, list):
        return [], [f"workflow_{entry_kind}_entries_must_be_list"]

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    seen: set[str] = set()
    for position, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            errors.append(f"workflow_{entry_kind}_entry_must_be_mapping:{position}")
            continue
        entry_id = _text(entry.get("entry_id"))
        if not entry_id:
            errors.append(f"workflow_{entry_kind}_entry_id_required:{position}")
            continue
        if entry_id in seen:
            errors.append(f"workflow_{entry_kind}_entry_ids_must_be_unique")
            continue
        if "value" not in entry or not isinstance(entry.get("value"), Mapping):
            errors.append(f"workflow_{entry_kind}_entry_value_must_be_mapping:{entry_id}")
            continue
        seen.add(entry_id)
        record = deepcopy(dict(entry["value"]))
        supplied_identity = _text(record.get(target_identity))
        if supplied_identity and supplied_identity != entry_id:
            errors.append(f"workflow_{entry_kind}_identity_mismatch:{entry_id}")
            continue
        record[target_identity] = entry_id
        records.append(record)
    return records, errors


def build_synthesis_packet_from_reloaded_case(
    case_packet: Mapping[str, Any] | Any, analytical_records: Mapping[str, Any] | Any
) -> dict[str, Any]:
    """Copy explicit reloaded records into the accepted synthesis packet shape.

    This adapter only transfers caller-supplied values and explicit identities.
    It neither classifies records nor supplies analytical judgment.
    """
    packet = _mapping(case_packet)
    analytical = _mapping(analytical_records)
    errors: list[str] = []
    sources, source_errors = _identified_values(
        packet.get("source_materials"), entry_kind="source_material", target_identity="source_id"
    )
    statements, statement_errors = _identified_values(
        packet.get("extracted_facts"), entry_kind="extracted_fact", target_identity="statement_id"
    )
    errors.extend(source_errors)
    errors.extend(statement_errors)

    frame = _mapping(packet.get("workflow_case_frame"))
    case_frame = {
        "case_id": _text(packet.get("case_id")),
        "objective": _text(packet.get("objective")),
        "included_scope": deepcopy(frame.get("included_scope", [])),
        "excluded_scope": deepcopy(frame.get("excluded_scope", [])),
        "decision_owner": _text(frame.get("decision_owner")),
        "review_posture": _text(frame.get("review_posture")),
    }
    if not isinstance(frame.get("included_scope"), list):
        errors.append("workflow_case_frame_included_scope_must_be_list")
    if not isinstance(frame.get("excluded_scope"), list):
        errors.append("workflow_case_frame_excluded_scope_must_be_list")

    packet_fields = (
        "constraint_register",
        "contradiction_register",
        "missing_information_register",
        "problem_frame",
        "candidates",
        "assessments",
        "prioritization_judgment",
        "recommendation_claims",
        "evidence_links",
        "decision_gates",
        "authorizations",
        "non_authorizations",
        "non_proofs",
        "next_bounded_action",
        "disposition",
        "revisions",
    )
    synthesis_packet: dict[str, Any] = {
        "case_frame": case_frame,
        "source_inventory": sources,
        "statement_register": statements,
    }
    for field in packet_fields:
        synthesis_packet[field] = deepcopy(analytical.get(field))
    return {"valid": not errors, "validation_errors": errors, "synthesis_packet": synthesis_packet}


def _validate_disposition(disposition: Any) -> list[str]:
    if not isinstance(disposition, Mapping):
        return ["workflow_disposition_must_be_mapping"]
    errors: list[str] = []
    for field in ("status", "owner", "note"):
        if not _text(disposition.get(field)):
            errors.append(f"workflow_disposition_{field}_required")
    for field in ("accepted_items", "not_authorized_items", "separate_future_decisions"):
        if not isinstance(disposition.get(field), list) or not disposition.get(field):
            errors.append(f"workflow_disposition_{field}_must_be_non_empty_list")
    return errors


def run_controlled_dossier_workflow(workflow_input: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Persist, reload, synthesize, and surface one explicit controlled dossier.

    A blocked output is returned for structural input, adapter, or synthesis
    failures. Persistence errors retain the existing case-packet contract's
    diagnostic and are exposed without attempting a repair.
    """
    if not isinstance(workflow_input, Mapping):
        return _blocked(["workflow_input_must_be_mapping"])

    supplied = deepcopy(dict(workflow_input))
    original_case = supplied.get("case_packet")
    analytical_records = supplied.get("analytical_records")
    if not isinstance(original_case, Mapping):
        return _blocked(["workflow_case_packet_must_be_mapping"])
    if not isinstance(analytical_records, Mapping):
        return _blocked(["workflow_analytical_records_must_be_mapping"])

    case_id = _text(original_case.get("case_id"))
    try:
        reloaded_case = load_case_packet(case_id)
    except FileNotFoundError:
        try:
            save_case_packet(dict(original_case))
            reloaded_case = load_case_packet(case_id)
        except ValueError as error:
            return _blocked([f"workflow_case_packet_persistence_blocked:{error}"])
    except ValueError as error:
        return _blocked([f"workflow_case_packet_persistence_blocked:{error}"])
    else:
        if reloaded_case != dict(original_case):
            return _blocked(["workflow_case_packet_existing_contents_differ"])

    adapter_result = build_synthesis_packet_from_reloaded_case(reloaded_case, analytical_records)
    if not adapter_result["valid"]:
        return _blocked(adapter_result["validation_errors"])

    synthesis_result = build_evidence_linked_synthesis_package(adapter_result["synthesis_packet"])
    if not synthesis_result["successful_synthesis"]:
        return _blocked(
            [f"workflow_synthesis_blocked:{error}" for error in synthesis_result["validation_errors"]],
            synthesis_result=synthesis_result,
        )

    disposition = adapter_result["synthesis_packet"]["disposition"]
    disposition_errors = _validate_disposition(disposition)
    if disposition_errors:
        return _blocked(disposition_errors, synthesis_result=synthesis_result)

    return {
        "contract_name": CONTRACT_NAME,
        "boundary": BOUNDARY,
        "workflow_status": "completed",
        "workflow_classification": COMPLETED_CLASSIFICATION,
        "completed": True,
        "validation_errors": [],
        "original_bounded_case": deepcopy(dict(original_case)),
        "persisted_reloaded_identity_state": {
            "case_id": reloaded_case["case_id"],
            "source_materials": deepcopy(reloaded_case["source_materials"]),
            "extracted_facts": deepcopy(reloaded_case["extracted_facts"]),
        },
        "evidence_links": deepcopy(adapter_result["synthesis_packet"]["evidence_links"]),
        "synthesis_result": synthesis_result,
        "human_disposition": deepcopy(disposition),
        "explicit_non_proofs": list(WORKFLOW_NON_PROOFS),
        "next_bounded_action": deepcopy(adapter_result["synthesis_packet"]["next_bounded_action"]),
    }
