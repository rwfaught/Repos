from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.dossier_case_mapping import (
    NO_FIRST_PRODUCT_WEDGE_SELECTED,
    adapt_case_packet_to_dossier_case,
)
from orchestrator.dossier_case_mapping_readback import (
    REQUIRED_NEUTRAL_FIELDS,
    build_dossier_case_mapping_readback_dict,
)


BOUNDARY = "DOSSIER_CASE_MINIMAL_FIXTURE_SOURCE_TEST_DOCS"
ADMIN_CASE_SHAPE = "admin_case_shape"
CREATIVE_DOSSIER_SHAPE = "creative_dossier_shape"

SAFE_NEXT_OPTIONS = (
    "FIRST_PRODUCT_WEDGE_RATIFICATION_OPERATOR_DECISION_DOCS_ONLY",
    "SOURCE_FILES_REFRESH_EXPORT_AFTER_FOUNDER_REALIGNMENT",
)

NON_PROOFS = (
    "no runtime proof",
    "no provider/model proof",
    "no semantic correctness proof",
    "no production readiness proof",
    "no Phase 387 implementation",
    "no first product wedge selection",
    "no claims/disputes/appeals product implementation",
    "no game/worldbuilding/design product implementation",
    "no persistence migration",
    "no Source Files refresh/export/capsule proof",
)


@dataclass(frozen=True)
class DossierCaseMinimalFixture:
    fixture_name: str
    boundary: str
    case_packet: dict[str, Any]
    adapted_dossier_case: dict[str, Any]
    readback: dict[str, Any]
    required_neutral_field_coverage: dict[str, bool]
    preserved_concepts: dict[str, bool]
    product_wedge_selection: str
    first_product_wedge_selected: bool
    phase_387_implemented: bool
    structural_example_only: bool
    domain_specific_workflow_implemented: bool
    product_implementation: bool
    runtime_provider_model_execution_required: bool
    non_proofs: tuple[str, ...]
    recommended_next_boundary: str
    safe_next_options: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture_name": self.fixture_name,
            "boundary": self.boundary,
            "case_packet": self.case_packet,
            "adapted_dossier_case": self.adapted_dossier_case,
            "readback": self.readback,
            "required_neutral_field_coverage": dict(self.required_neutral_field_coverage),
            "preserved_concepts": dict(self.preserved_concepts),
            "product_wedge_selection": self.product_wedge_selection,
            "first_product_wedge_selected": self.first_product_wedge_selected,
            "phase_387_implemented": self.phase_387_implemented,
            "structural_example_only": self.structural_example_only,
            "domain_specific_workflow_implemented": self.domain_specific_workflow_implemented,
            "product_implementation": self.product_implementation,
            "runtime_provider_model_execution_required": self.runtime_provider_model_execution_required,
            "non_proofs": list(self.non_proofs),
            "recommended_next_boundary": self.recommended_next_boundary,
            "safe_next_options": list(self.safe_next_options),
        }


def build_admin_case_shape_packet() -> dict[str, Any]:
    return {
        "case_id": ADMIN_CASE_SHAPE,
        "case_type": "neutral_admin_case_shape",
        "title": "Neutral admin case shape",
        "objective": "Track a bounded administrative matter through shared dossier case fields.",
        "source_materials": ["admin-note.md", "reference-summary.md"],
        "extracted_facts": [
            {"fact": "The matter has two source notes.", "source": "admin-note.md"},
            {"fact": "The next review depends on one missing item.", "source": "reference-summary.md"},
        ],
        "timeline_events": ["source notes received", "operator review requested"],
        "open_issues": ["which source item should be checked next"],
        "missing_evidence": ["missing administrative reference"],
        "contradictions": ["source notes disagree about the review date"],
        "drafts": ["neutral administrative summary draft"],
        "decisions": ["operator has not selected a first product wedge"],
        "status": "structural_example_only",
        "next_step": "compare the fixture through the neutral mapping readback",
    }


def build_creative_dossier_shape_packet() -> dict[str, Any]:
    return {
        "case_id": CREATIVE_DOSSIER_SHAPE,
        "case_type": "neutral_creative_dossier_shape",
        "title": "Neutral creative dossier shape",
        "objective": "Track a bounded creative matter through shared dossier case fields.",
        "source_materials": ["creative-note.md", "reference-list.md"],
        "extracted_facts": [
            {"fact": "The matter has a source note and a reference list.", "source": "creative-note.md"},
            {"fact": "The next review depends on one unresolved reference.", "source": "reference-list.md"},
        ],
        "timeline_events": ["source note drafted", "reference list reviewed"],
        "open_issues": ["which reference should anchor the next revision"],
        "missing_evidence": ["missing canon reference"],
        "contradictions": ["source note and reference list disagree about sequence"],
        "drafts": ["neutral creative dossier summary draft"],
        "decisions": ["operator has not selected a first product wedge"],
        "status": "structural_example_only",
        "next_step": "compare the fixture through the neutral mapping readback",
    }


def _build_minimal_fixture(fixture_name: str, case_packet: dict[str, Any]) -> DossierCaseMinimalFixture:
    adapted = adapt_case_packet_to_dossier_case(case_packet)
    readback = build_dossier_case_mapping_readback_dict(case_packet)
    coverage = {field: field in adapted for field in REQUIRED_NEUTRAL_FIELDS}

    return DossierCaseMinimalFixture(
        fixture_name=fixture_name,
        boundary=BOUNDARY,
        case_packet=case_packet,
        adapted_dossier_case=adapted,
        readback=readback,
        required_neutral_field_coverage=coverage,
        preserved_concepts={
            "missing_evidence": bool(adapted["missing_evidence"]),
            "missing_canon": bool(adapted["missing_canon"]),
            "contradictions": bool(adapted["contradictions"]),
        },
        product_wedge_selection=NO_FIRST_PRODUCT_WEDGE_SELECTED,
        first_product_wedge_selected=False,
        phase_387_implemented=False,
        structural_example_only=True,
        domain_specific_workflow_implemented=False,
        product_implementation=False,
        runtime_provider_model_execution_required=False,
        non_proofs=NON_PROOFS,
        recommended_next_boundary="FIRST_PRODUCT_WEDGE_RATIFICATION_OPERATOR_DECISION_DOCS_ONLY",
        safe_next_options=SAFE_NEXT_OPTIONS,
    )


def build_admin_case_minimal_fixture() -> DossierCaseMinimalFixture:
    return _build_minimal_fixture(ADMIN_CASE_SHAPE, build_admin_case_shape_packet())


def build_creative_dossier_minimal_fixture() -> DossierCaseMinimalFixture:
    return _build_minimal_fixture(CREATIVE_DOSSIER_SHAPE, build_creative_dossier_shape_packet())


def build_minimal_fixture_readbacks() -> tuple[DossierCaseMinimalFixture, DossierCaseMinimalFixture]:
    return (
        build_admin_case_minimal_fixture(),
        build_creative_dossier_minimal_fixture(),
    )


def build_minimal_fixture_readback_dicts() -> list[dict[str, Any]]:
    return [fixture.to_dict() for fixture in build_minimal_fixture_readbacks()]
