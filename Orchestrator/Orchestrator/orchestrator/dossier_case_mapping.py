from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.case_packet import normalize_case_packet


NO_FIRST_PRODUCT_WEDGE_SELECTED = "no_first_product_wedge_selected"
NON_PROOF_POSTURE = {
    "runtime_proof": False,
    "provider_model_proof": False,
    "semantic_correctness_proof": False,
    "production_readiness_proof": False,
    "phase_387_implementation": False,
    "first_product_wedge_selection": False,
}


@dataclass(frozen=True)
class DossierCaseFieldMapping:
    neutral_field: str
    case_packet_fields: tuple[str, ...]
    adapter_note: str


_CANONICAL_FIELD_MAPPINGS: tuple[DossierCaseFieldMapping, ...] = (
    DossierCaseFieldMapping("objective", ("objective",), "direct shared field"),
    DossierCaseFieldMapping("source_materials", ("source_materials",), "direct shared field"),
    DossierCaseFieldMapping("extracted_facts", ("extracted_facts",), "direct shared field"),
    DossierCaseFieldMapping("chronology", ("timeline_events",), "neutral alias for timeline/history"),
    DossierCaseFieldMapping("open_questions", ("open_issues",), "neutral alias for unresolved issues"),
    DossierCaseFieldMapping("missing_evidence", ("missing_evidence",), "direct shared gap field"),
    DossierCaseFieldMapping("missing_canon", ("missing_evidence",), "neutral creative-domain gap alias"),
    DossierCaseFieldMapping("contradictions", ("contradictions",), "direct shared conflict field"),
    DossierCaseFieldMapping("drafts", ("drafts",), "direct shared prepared-output field"),
    DossierCaseFieldMapping("decisions", ("decisions",), "direct shared human-judgment field"),
    DossierCaseFieldMapping("next_work_items", ("next_step",), "single current next-step signal"),
    DossierCaseFieldMapping("review_posture", ("status", "next_step"), "partial posture from orientation fields"),
    DossierCaseFieldMapping("operator_approvals", ("decisions",), "approval signals remain decision records"),
    DossierCaseFieldMapping("status", ("status",), "direct current status field"),
)


def get_dossier_case_field_mappings() -> tuple[DossierCaseFieldMapping, ...]:
    return _CANONICAL_FIELD_MAPPINGS


def get_dossier_case_field_map() -> dict[str, tuple[str, ...]]:
    return {mapping.neutral_field: mapping.case_packet_fields for mapping in _CANONICAL_FIELD_MAPPINGS}


def adapt_case_packet_to_dossier_case(case_packet: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_case_packet(case_packet)
    return {
        "objective": normalized["objective"],
        "source_materials": list(normalized["source_materials"]),
        "extracted_facts": list(normalized["extracted_facts"]),
        "chronology": list(normalized["timeline_events"]),
        "open_questions": list(normalized["open_issues"]),
        "missing_evidence": list(normalized["missing_evidence"]),
        "missing_canon": list(normalized["missing_evidence"]),
        "contradictions": list(normalized["contradictions"]),
        "drafts": list(normalized["drafts"]),
        "decisions": list(normalized["decisions"]),
        "next_work_items": [normalized["next_step"]] if normalized["next_step"] else [],
        "review_posture": {
            "status": normalized["status"],
            "next_step": normalized["next_step"],
        },
        "operator_approvals": list(normalized["decisions"]),
        "status": normalized["status"],
        "product_wedge_selection": NO_FIRST_PRODUCT_WEDGE_SELECTED,
        "non_proof_posture": dict(NON_PROOF_POSTURE),
    }
