from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.dossier_case_mapping import (
    NO_FIRST_PRODUCT_WEDGE_SELECTED,
    adapt_case_packet_to_dossier_case,
)
from orchestrator.dossier_case_mapping_readback import REQUIRED_NEUTRAL_FIELDS


REPORT_NAME = "neutral_task_readiness_report"
BOUNDARY = "DOSSIER_CASE_TASK_READINESS_SOURCE_TEST_DOCS"

STRUCTURAL_FIELD_REQUIREMENTS = (
    "contradictions",
    "open_questions",
    "decisions",
    "next_work_items",
)

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

DOMAIN_SPECIFIC_TERMS_NOT_REQUIRED = (
    "claims",
    "disputes",
    "appeals",
    "game",
    "worldbuilding",
    "design",
)

RECOMMENDED_NEXT_STRUCTURAL_ACTION_READY = (
    "review neutral readiness report before any domain-specific boundary"
)
RECOMMENDED_NEXT_STRUCTURAL_ACTION_BLOCKED = (
    "add missing neutral structural fields before domain-specific boundary"
)


@dataclass(frozen=True)
class DossierCaseTaskReadinessReport:
    report_name: str
    boundary: str
    required_neutral_fields: tuple[str, ...]
    present_required_neutral_fields: tuple[str, ...]
    missing_required_neutral_fields: tuple[str, ...]
    open_questions: tuple[Any, ...]
    contradictions: tuple[Any, ...]
    decisions: tuple[Any, ...]
    next_work_items: tuple[Any, ...]
    structurally_ready_for_domain_specific_work: bool
    structural_readiness_blockers: tuple[str, ...]
    product_wedge_selected: bool
    product_wedge_selection: str
    phase_387_implemented: bool
    runtime_required: bool
    provider_model_required: bool
    domain_specific_terms_required: tuple[str, ...]
    non_proofs: tuple[str, ...]
    recommended_next_structural_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_name": self.report_name,
            "boundary": self.boundary,
            "required_neutral_fields": list(self.required_neutral_fields),
            "present_required_neutral_fields": list(self.present_required_neutral_fields),
            "missing_required_neutral_fields": list(self.missing_required_neutral_fields),
            "open_questions": list(self.open_questions),
            "contradictions": list(self.contradictions),
            "decisions": list(self.decisions),
            "next_work_items": list(self.next_work_items),
            "structurally_ready_for_domain_specific_work": (
                self.structurally_ready_for_domain_specific_work
            ),
            "structural_readiness_blockers": list(self.structural_readiness_blockers),
            "product_wedge_selected": self.product_wedge_selected,
            "product_wedge_selection": self.product_wedge_selection,
            "phase_387_implemented": self.phase_387_implemented,
            "runtime_required": self.runtime_required,
            "provider_model_required": self.provider_model_required,
            "domain_specific_terms_required": list(self.domain_specific_terms_required),
            "non_proofs": list(self.non_proofs),
            "recommended_next_structural_action": self.recommended_next_structural_action,
        }


def _as_tuple(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return (value,)


def _coerce_to_dossier_case(candidate: Any) -> dict[str, Any]:
    if hasattr(candidate, "adapted_dossier_case"):
        return dict(candidate.adapted_dossier_case)

    if isinstance(candidate, dict) and "adapted_dossier_case" in candidate:
        return dict(candidate["adapted_dossier_case"])

    if isinstance(candidate, dict):
        if any(
            field in candidate
            for field in (
                "case_id",
                "case_type",
                "title",
                "timeline_events",
                "open_issues",
                "next_step",
            )
        ):
            return adapt_case_packet_to_dossier_case(candidate)
        if any(field in candidate for field in REQUIRED_NEUTRAL_FIELDS):
            return dict(candidate)
        return adapt_case_packet_to_dossier_case(candidate)

    raise TypeError("readiness report requires a dictionary or minimal fixture")


def _field_presence(adapted_dossier_case: dict[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    present = tuple(field for field in REQUIRED_NEUTRAL_FIELDS if field in adapted_dossier_case)
    missing = tuple(field for field in REQUIRED_NEUTRAL_FIELDS if field not in adapted_dossier_case)
    return present, missing


def _extract_product_wedge_selected(adapted_dossier_case: dict[str, Any]) -> bool:
    if "product_wedge_selected" in adapted_dossier_case:
        return bool(adapted_dossier_case["product_wedge_selected"])
    return adapted_dossier_case.get("product_wedge_selection") != NO_FIRST_PRODUCT_WEDGE_SELECTED


def _extract_phase_387_implemented(adapted_dossier_case: dict[str, Any]) -> bool:
    if "phase_387_implemented" in adapted_dossier_case:
        return bool(adapted_dossier_case["phase_387_implemented"])
    posture = adapted_dossier_case.get("non_proof_posture", {})
    if isinstance(posture, dict):
        return bool(posture.get("phase_387_implementation", False))
    return False


def _extract_runtime_required(adapted_dossier_case: dict[str, Any]) -> bool:
    if "runtime_required" in adapted_dossier_case:
        return bool(adapted_dossier_case["runtime_required"])
    posture = adapted_dossier_case.get("non_proof_posture", {})
    if isinstance(posture, dict):
        return bool(posture.get("runtime_proof", False))
    return False


def _extract_provider_model_required(adapted_dossier_case: dict[str, Any]) -> bool:
    if "provider_model_required" in adapted_dossier_case:
        return bool(adapted_dossier_case["provider_model_required"])
    posture = adapted_dossier_case.get("non_proof_posture", {})
    if isinstance(posture, dict):
        return bool(posture.get("provider_model_proof", False))
    return False


def _build_blockers(
    missing_required: tuple[str, ...],
    product_wedge_selected: bool,
    phase_387_implemented: bool,
    runtime_required: bool,
    provider_model_required: bool,
) -> tuple[str, ...]:
    blockers: list[str] = []
    blockers.extend(f"missing required neutral field: {field}" for field in missing_required)

    if product_wedge_selected:
        blockers.append("product wedge selection is present")
    if phase_387_implemented:
        blockers.append("Phase 387 implementation is present")
    if runtime_required:
        blockers.append("runtime requirement is present")
    if provider_model_required:
        blockers.append("provider/model requirement is present")

    return tuple(blockers)


def build_neutral_task_readiness_report(candidate: Any) -> DossierCaseTaskReadinessReport:
    adapted = _coerce_to_dossier_case(candidate)
    present, missing = _field_presence(adapted)
    product_wedge_selected = _extract_product_wedge_selected(adapted)
    phase_387_implemented = _extract_phase_387_implemented(adapted)
    runtime_required = _extract_runtime_required(adapted)
    provider_model_required = _extract_provider_model_required(adapted)
    blockers = _build_blockers(
        missing,
        product_wedge_selected,
        phase_387_implemented,
        runtime_required,
        provider_model_required,
    )
    structurally_ready = len(blockers) == 0

    return DossierCaseTaskReadinessReport(
        report_name=REPORT_NAME,
        boundary=BOUNDARY,
        required_neutral_fields=REQUIRED_NEUTRAL_FIELDS,
        present_required_neutral_fields=present,
        missing_required_neutral_fields=missing,
        open_questions=_as_tuple(adapted.get("open_questions")),
        contradictions=_as_tuple(adapted.get("contradictions")),
        decisions=_as_tuple(adapted.get("decisions")),
        next_work_items=_as_tuple(adapted.get("next_work_items")),
        structurally_ready_for_domain_specific_work=structurally_ready,
        structural_readiness_blockers=blockers,
        product_wedge_selected=product_wedge_selected,
        product_wedge_selection=adapted.get(
            "product_wedge_selection",
            NO_FIRST_PRODUCT_WEDGE_SELECTED,
        ),
        phase_387_implemented=phase_387_implemented,
        runtime_required=runtime_required,
        provider_model_required=provider_model_required,
        domain_specific_terms_required=(),
        non_proofs=NON_PROOFS,
        recommended_next_structural_action=(
            RECOMMENDED_NEXT_STRUCTURAL_ACTION_READY
            if structurally_ready
            else RECOMMENDED_NEXT_STRUCTURAL_ACTION_BLOCKED
        ),
    )


def build_neutral_task_readiness_report_dict(candidate: Any) -> dict[str, Any]:
    return build_neutral_task_readiness_report(candidate).to_dict()
