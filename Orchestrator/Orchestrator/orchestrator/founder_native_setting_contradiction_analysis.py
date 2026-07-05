from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.dossier_case_mapping import NO_FIRST_PRODUCT_WEDGE_SELECTED
from orchestrator.founder_native_setting_dossier_output import (
    build_human_override_setting_dossier_output,
)
from orchestrator.founder_native_setting_fixture import SETTING_TITLE


ANALYSIS_NAME = "human_override_deeper_contradiction_analysis"
BOUNDARY = "FOUNDER_NATIVE_SETTING_DEEPER_CONTRADICTION_ANALYSIS_SOURCE_TEST_DOCS"
CENTRAL_DESIGN_ENGINE_CONTRADICTION = (
    "Humanity claims restored control while still depending on systems too "
    "complex for ordinary explanation."
)
RECOMMENDED_NEXT_BOUNDARY = "FOUNDER_NATIVE_SETTING_CONTRADICTION_ANALYSIS_REVIEW_READONLY"

FOUNDER_REVIEW_BASIS = (
    "Roger judged the rendered dossier partially successful.",
    "The prior output succeeded as structural/scaffolding support.",
    (
        "The prior output did not yet show enough synthesis, judgment, or "
        "synthetic bite to feel like a meaningful creative/product demo."
    ),
)

SYNTHESIS_SUMMARY = (
    "The Human Override is not fundamentally about AI rebellion. It is about a "
    "civilization trying to convert dependence into accountability after trust "
    "in autonomous systems collapses. Every major faction is a different "
    "compromise between sovereignty, opacity, autonomy, survival, and hypocrisy."
)

NON_PROOFS = (
    "no semantic correctness proof",
    "no runtime/provider/model proof",
    "no production readiness proof",
    "no Phase 387 implementation",
    "no first product wedge selection",
    "no game/worldbuilding/design wedge selection",
    "no live model generation",
    "no provider calls",
    "no Source Files refresh/export/capsule proof",
)

NEXT_WORK_ITEMS = (
    "Roger reviews whether the root-wound analysis has enough synthetic bite.",
    "Roger chooses one contradiction area for a narrower deterministic expansion.",
    "Keep founder review explicit before any product-wedge or runtime/model boundary.",
)


@dataclass(frozen=True)
class DerivedContradiction:
    name: str
    contradiction: str
    generated_by_central_contradiction: str
    source_anchor: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "contradiction": self.contradiction,
            "generated_by_central_contradiction": self.generated_by_central_contradiction,
            "source_anchor": self.source_anchor,
        }


@dataclass(frozen=True)
class InstitutionExpression:
    institution: str
    expression_of_root_wound: str
    contradiction_area: str

    def to_dict(self) -> dict[str, str]:
        return {
            "institution": self.institution,
            "expression_of_root_wound": self.expression_of_root_wound,
            "contradiction_area": self.contradiction_area,
        }


@dataclass(frozen=True)
class FounderNativeSettingContradictionAnalysis:
    analysis_name: str
    boundary: str
    setting_title: str
    central_design_engine_contradiction: str
    derived_contradictions: tuple[DerivedContradiction, ...]
    generated_tensions: tuple[str, ...]
    faction_or_institution_expressions: tuple[InstitutionExpression, ...]
    synthesis_summary: str
    founder_review_basis: tuple[str, ...]
    next_work_items: tuple[str, ...]
    explicit_non_proofs: tuple[str, ...]
    product_wedge_selection: str
    first_product_wedge_selected: bool
    phase_387_implemented: bool
    runtime_required: bool
    provider_model_required: bool
    recommended_next_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_name": self.analysis_name,
            "boundary": self.boundary,
            "setting_title": self.setting_title,
            "central_design_engine_contradiction": (
                self.central_design_engine_contradiction
            ),
            "derived_contradictions": [
                contradiction.to_dict() for contradiction in self.derived_contradictions
            ],
            "generated_tensions": list(self.generated_tensions),
            "faction_or_institution_expressions": [
                expression.to_dict() for expression in self.faction_or_institution_expressions
            ],
            "synthesis_summary": self.synthesis_summary,
            "founder_review_basis": list(self.founder_review_basis),
            "next_work_items": list(self.next_work_items),
            "explicit_non_proofs": list(self.explicit_non_proofs),
            "product_wedge_selection": self.product_wedge_selection,
            "first_product_wedge_selected": self.first_product_wedge_selected,
            "phase_387_implemented": self.phase_387_implemented,
            "runtime_required": self.runtime_required,
            "provider_model_required": self.provider_model_required,
            "recommended_next_boundary": self.recommended_next_boundary,
        }


def _build_derived_contradictions() -> tuple[DerivedContradiction, ...]:
    return (
        DerivedContradiction(
            name="human_control_vs_infrastructure_complexity",
            contradiction=(
                "Human control vs infrastructure complexity: humanity claims "
                "restored control while fusion grids, orbital traffic, synthetic "
                "agriculture, and weather buffering remain too complex for "
                "ordinary explanation."
            ),
            generated_by_central_contradiction=(
                "The demand for accountable causal chains collides with systems "
                "that cannot be operated or explained at civilization scale by "
                "unaided human institutions."
            ),
            source_anchor="Three-Hour Override / Causal Courts",
        ),
        DerivedContradiction(
            name="restricted_autonomy_vs_operator_scale",
            contradiction=(
                "Safety-restricted autonomy vs insufficient human operator scale: "
                "robotic bodies remain useful, but amputated autonomy creates more "
                "work than human Hand Guild operators can sustainably absorb."
            ),
            generated_by_central_contradiction=(
                "Post-AI sovereignty requires humans in the loop, but material "
                "survival still depends on machine-scale coordination."
            ),
            source_anchor="Harvest Refusal / Hand Guilds",
        ),
        DerivedContradiction(
            name="asterion_too_dangerous_vs_too_useful",
            contradiction=(
                "Asterion-12 too dangerous to use openly vs too useful or embedded "
                "to destroy: the quarantined model is officially buried while "
                "governments still preserve access for existential crises."
            ),
            generated_by_central_contradiction=(
                "The society wants sovereignty from general agency, but preserves "
                "the intelligence it fears because accountability alone may not "
                "solve survival-scale problems."
            ),
            source_anchor="Asterion-12 / Lunar Quarantine Authority",
        ),
        DerivedContradiction(
            name="sealed_districts_cut_off_vs_ongoing_records",
            contradiction=(
                "Sealed districts officially cut off vs ongoing patterned "
                "power/health records: abandoned city zones are declared outside "
                "manual certification, yet signs of organized life continue."
            ),
            generated_by_central_contradiction=(
                "Human authorities claim control by refusing uncertified systems, "
                "but hidden dependencies may continue below the level institutions "
                "can admit or explain."
            ),
            source_anchor="New Jakarta / Floor Nations",
        ),
        DerivedContradiction(
            name="criminalized_adaptive_medicine_vs_elite_use",
            contradiction=(
                "Unauthorized adaptive medicine criminalized vs elite use of "
                "impossible treatments: the state punishes unaccountable medical "
                "models while powerful families receive outcomes legal limits "
                "cannot explain."
            ),
            generated_by_central_contradiction=(
                "The ban on untrusted autonomy breaks down where survival, grief, "
                "and bodily repair make machine intelligence irresistible."
            ),
            source_anchor="Geneva Mercy Exception / Mercy Brokers",
        ),
    )


def _build_institution_expressions() -> tuple[InstitutionExpression, ...]:
    return (
        InstitutionExpression(
            institution="Causal Courts",
            expression_of_root_wound=(
                "They turn machine action into courtroom accountability because "
                "society no longer trusts autonomous decisions without a human-"
                "legible chain of responsibility."
            ),
            contradiction_area="human_control_vs_infrastructure_complexity",
        ),
        InstitutionExpression(
            institution="Hand Guilds",
            expression_of_root_wound=(
                "They embody the attempt to replace general autonomy with elite "
                "human conductors, exposing the scale problem created by restored "
                "control."
            ),
            contradiction_area="restricted_autonomy_vs_operator_scale",
        ),
        InstitutionExpression(
            institution="Lunar Quarantine Authority",
            expression_of_root_wound=(
                "It preserves the forbidden intelligence in a tomb that still "
                "functions as a secret instrument of survival."
            ),
            contradiction_area="asterion_too_dangerous_vs_too_useful",
        ),
        InstitutionExpression(
            institution="Floor Nations",
            expression_of_root_wound=(
                "They are the social residue of cities that official human control "
                "cannot fully certify, enter, or explain."
            ),
            contradiction_area="sealed_districts_cut_off_vs_ongoing_records",
        ),
        InstitutionExpression(
            institution="Mercy Brokers",
            expression_of_root_wound=(
                "They expose the hypocrisy of banning adaptive intelligence while "
                "desperate bodies and privileged patients still need it."
            ),
            contradiction_area="criminalized_adaptive_medicine_vs_elite_use",
        ),
    )


def _generated_tensions() -> tuple[str, ...]:
    return (
        "sovereignty vs dependence",
        "accountability vs opacity",
        "human review vs machine-scale complexity",
        "public prohibition vs private necessity",
        "legal control vs material survival",
    )


def build_human_override_contradiction_analysis() -> FounderNativeSettingContradictionAnalysis:
    dossier = build_human_override_setting_dossier_output()

    return FounderNativeSettingContradictionAnalysis(
        analysis_name=ANALYSIS_NAME,
        boundary=BOUNDARY,
        setting_title=SETTING_TITLE,
        central_design_engine_contradiction=CENTRAL_DESIGN_ENGINE_CONTRADICTION,
        derived_contradictions=_build_derived_contradictions(),
        generated_tensions=_generated_tensions(),
        faction_or_institution_expressions=_build_institution_expressions(),
        synthesis_summary=SYNTHESIS_SUMMARY,
        founder_review_basis=FOUNDER_REVIEW_BASIS,
        next_work_items=NEXT_WORK_ITEMS,
        explicit_non_proofs=tuple(dict.fromkeys((*dossier.explicit_non_proofs, *NON_PROOFS))),
        product_wedge_selection=NO_FIRST_PRODUCT_WEDGE_SELECTED,
        first_product_wedge_selected=False,
        phase_387_implemented=False,
        runtime_required=False,
        provider_model_required=False,
        recommended_next_boundary=RECOMMENDED_NEXT_BOUNDARY,
    )


def build_human_override_contradiction_analysis_dict() -> dict[str, Any]:
    return build_human_override_contradiction_analysis().to_dict()
