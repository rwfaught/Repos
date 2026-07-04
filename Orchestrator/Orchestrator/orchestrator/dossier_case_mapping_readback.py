from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.dossier_case_mapping import (
    NO_FIRST_PRODUCT_WEDGE_SELECTED,
    NON_PROOF_POSTURE,
    adapt_case_packet_to_dossier_case,
    get_dossier_case_field_map,
)


READBACK_NAME = "dossier_case_mapping_readback"
BOUNDARY = "DOSSIER_CASE_MAPPING_READBACK_SOURCE_TEST_DOCS"

REQUIRED_NEUTRAL_FIELDS = (
    "objective",
    "source_materials",
    "extracted_facts",
    "chronology",
    "open_questions",
    "missing_evidence",
    "missing_canon",
    "contradictions",
    "drafts",
    "decisions",
    "next_work_items",
    "review_posture",
    "operator_approvals",
    "status",
)

PRESERVED_CONCEPTS = {
    "missing_evidence": True,
    "missing_canon": True,
    "contradictions": True,
}

NON_PROOFS = (
    "no runtime proof",
    "no provider/model proof",
    "no semantic correctness proof",
    "no production readiness proof",
    "no Phase 387 implementation",
    "no first product wedge selection",
    "no product-domain implementation",
    "no persistence migration",
    "no Source Files refresh/export/capsule proof",
)

SAFE_NEXT_OPTIONS = (
    "DOSSIER_CASE_MINIMAL_FIXTURE_SOURCE_TEST_DOCS",
    "FIRST_PRODUCT_WEDGE_RATIFICATION_OPERATOR_DECISION_DOCS_ONLY",
    "SOURCE_FILES_REFRESH_EXPORT_AFTER_FOUNDER_REALIGNMENT",
)

_DOMAIN_SPECIFIC_TERMS = (
    "claims",
    "disputes",
    "appeals",
    "game",
    "worldbuilding",
    "design",
)


@dataclass(frozen=True)
class DossierCaseMappingReadback:
    readback_name: str
    boundary: str
    neutral_fields: tuple[str, ...]
    neutral_to_case_packet_mapping: dict[str, tuple[str, ...]]
    required_field_coverage: dict[str, bool]
    missing_required_neutral_fields: tuple[str, ...]
    preserved_concepts: dict[str, bool]
    domain_neutral: bool
    domain_specific_terms_required: tuple[str, ...]
    first_product_wedge_selected: bool
    product_wedge_selection: str
    phase_387_implemented: bool
    non_proofs: tuple[str, ...]
    recommended_next_boundary: str
    safe_next_options: tuple[str, ...]
    adapted_packet_readback: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "readback_name": self.readback_name,
            "boundary": self.boundary,
            "neutral_fields": list(self.neutral_fields),
            "neutral_to_case_packet_mapping": {
                key: list(value) for key, value in self.neutral_to_case_packet_mapping.items()
            },
            "required_field_coverage": dict(self.required_field_coverage),
            "missing_required_neutral_fields": list(self.missing_required_neutral_fields),
            "preserved_concepts": dict(self.preserved_concepts),
            "domain_neutral": self.domain_neutral,
            "domain_specific_terms_required": list(self.domain_specific_terms_required),
            "first_product_wedge_selected": self.first_product_wedge_selected,
            "product_wedge_selection": self.product_wedge_selection,
            "phase_387_implemented": self.phase_387_implemented,
            "non_proofs": list(self.non_proofs),
            "recommended_next_boundary": self.recommended_next_boundary,
            "safe_next_options": list(self.safe_next_options),
            "adapted_packet_readback": self.adapted_packet_readback,
        }


def _find_required_domain_terms(neutral_fields: tuple[str, ...], field_map: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    surface = " ".join(list(neutral_fields) + [field for fields in field_map.values() for field in fields]).lower()
    return tuple(term for term in _DOMAIN_SPECIFIC_TERMS if term in surface)


def build_dossier_case_mapping_readback(case_packet: dict[str, Any] | None = None) -> DossierCaseMappingReadback:
    field_map = get_dossier_case_field_map()
    neutral_fields = tuple(field_map)
    required_coverage = {field: field in field_map for field in REQUIRED_NEUTRAL_FIELDS}
    missing_required = tuple(field for field, present in required_coverage.items() if not present)
    domain_terms_required = _find_required_domain_terms(neutral_fields, field_map)
    adapted_packet = adapt_case_packet_to_dossier_case(case_packet) if case_packet is not None else None

    return DossierCaseMappingReadback(
        readback_name=READBACK_NAME,
        boundary=BOUNDARY,
        neutral_fields=neutral_fields,
        neutral_to_case_packet_mapping=field_map,
        required_field_coverage=required_coverage,
        missing_required_neutral_fields=missing_required,
        preserved_concepts=dict(PRESERVED_CONCEPTS),
        domain_neutral=len(domain_terms_required) == 0,
        domain_specific_terms_required=domain_terms_required,
        first_product_wedge_selected=False,
        product_wedge_selection=NO_FIRST_PRODUCT_WEDGE_SELECTED,
        phase_387_implemented=False,
        non_proofs=NON_PROOFS,
        recommended_next_boundary="DOSSIER_CASE_MINIMAL_FIXTURE_SOURCE_TEST_DOCS",
        safe_next_options=SAFE_NEXT_OPTIONS,
        adapted_packet_readback=adapted_packet,
    )


def build_dossier_case_mapping_readback_dict(case_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    return build_dossier_case_mapping_readback(case_packet).to_dict()
