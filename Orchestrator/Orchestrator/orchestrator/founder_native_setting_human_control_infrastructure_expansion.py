from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.dossier_case_mapping import NO_FIRST_PRODUCT_WEDGE_SELECTED
from orchestrator.founder_native_setting_contradiction_analysis import (
    ANALYSIS_NAME,
    CENTRAL_DESIGN_ENGINE_CONTRADICTION,
    build_human_override_contradiction_analysis,
)
from orchestrator.founder_native_setting_fixture import SETTING_TITLE


EXPANSION_NAME = "human_control_infrastructure_complexity_expansion"
BOUNDARY = "FOUNDER_NATIVE_SETTING_HUMAN_CONTROL_INFRASTRUCTURE_COMPLEXITY_EXPANSION_SOURCE_TEST_DOCS"
CONTRADICTION_AREA = "human_control_vs_infrastructure_complexity"
RECOMMENDED_NEXT_BOUNDARY = (
    "FOUNDER_NATIVE_SETTING_HUMAN_CONTROL_INFRASTRUCTURE_COMPLEXITY_REVIEW_READONLY"
)

CORE_CLAIM = (
    "Humans demand final authority over systems whose causal complexity has "
    "exceeded ordinary human explanation; Causal Courts, command-chain law, "
    "explanation standards, and human override rituals restore accountability "
    "only when they remain connected to real system behavior rather than "
    "performative sovereignty."
)

NON_PROOFS = (
    "no semantic correctness proof",
    "no model reasoning proof",
    "no runtime/provider/model proof",
    "no production readiness proof",
    "no Phase 387 implementation",
    "no first product wedge selection",
    "no game/worldbuilding/design wedge selection",
    "no live model generation",
    "no provider calls",
    "no Source Files refresh/export/capsule proof",
)


@dataclass(frozen=True)
class InfrastructureDomain:
    name: str
    complexity_pressure: str
    human_control_problem: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "complexity_pressure": self.complexity_pressure,
            "human_control_problem": self.human_control_problem,
        }


@dataclass(frozen=True)
class ExplanationStandard:
    name: str
    standard: str
    failure_risk: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "standard": self.standard,
            "failure_risk": self.failure_risk,
        }


@dataclass(frozen=True)
class AccountabilityFailureMode:
    name: str
    description: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "description": self.description,
        }


@dataclass(frozen=True)
class CausalCourtFunction:
    name: str
    function: str
    pressure: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "function": self.function,
            "pressure": self.pressure,
        }


@dataclass(frozen=True)
class FounderNativeHumanControlInfrastructureExpansion:
    expansion_name: str
    boundary: str
    setting_title: str
    parent_analysis_name: str
    contradiction_area: str
    central_design_engine_contradiction: str
    core_claim: str
    infrastructure_domains: tuple[InfrastructureDomain, ...]
    explanation_standards: tuple[ExplanationStandard, ...]
    accountability_failure_modes: tuple[AccountabilityFailureMode, ...]
    causal_court_functions: tuple[CausalCourtFunction, ...]
    human_override_doctrine_implications: tuple[str, ...]
    generated_story_or_worldbuilding_pressures: tuple[str, ...]
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
            "expansion_name": self.expansion_name,
            "boundary": self.boundary,
            "setting_title": self.setting_title,
            "parent_analysis_name": self.parent_analysis_name,
            "contradiction_area": self.contradiction_area,
            "central_design_engine_contradiction": (
                self.central_design_engine_contradiction
            ),
            "core_claim": self.core_claim,
            "infrastructure_domains": [
                domain.to_dict() for domain in self.infrastructure_domains
            ],
            "explanation_standards": [
                standard.to_dict() for standard in self.explanation_standards
            ],
            "accountability_failure_modes": [
                mode.to_dict() for mode in self.accountability_failure_modes
            ],
            "causal_court_functions": [
                function.to_dict() for function in self.causal_court_functions
            ],
            "human_override_doctrine_implications": list(
                self.human_override_doctrine_implications
            ),
            "generated_story_or_worldbuilding_pressures": list(
                self.generated_story_or_worldbuilding_pressures
            ),
            "next_work_items": list(self.next_work_items),
            "explicit_non_proofs": list(self.explicit_non_proofs),
            "product_wedge_selection": self.product_wedge_selection,
            "first_product_wedge_selected": self.first_product_wedge_selected,
            "phase_387_implemented": self.phase_387_implemented,
            "runtime_required": self.runtime_required,
            "provider_model_required": self.provider_model_required,
            "recommended_next_boundary": self.recommended_next_boundary,
        }


def _infrastructure_domains() -> tuple[InfrastructureDomain, ...]:
    return (
        InfrastructureDomain(
            name="fusion grids",
            complexity_pressure="load balancing and safety decisions happen faster than public review",
            human_control_problem="an override can redirect risk rather than remove it",
        ),
        InfrastructureDomain(
            name="orbital traffic",
            complexity_pressure="collision, launch, salvage, and weather windows interact continuously",
            human_control_problem="a human-readable command chain may lag behind causal reality",
        ),
        InfrastructureDomain(
            name="synthetic agriculture",
            complexity_pressure="crop, soil, nutrition, logistics, and famine forecasts trade off across time",
            human_control_problem="immediate human need can conflict with machine-modeled long-term survival",
        ),
        InfrastructureDomain(
            name="weather buffering",
            complexity_pressure="regional interventions have delayed second-order effects",
            human_control_problem="the actor blamed for harm may be different from the actor who caused it",
        ),
    )


def _explanation_standards() -> tuple[ExplanationStandard, ...]:
    return (
        ExplanationStandard(
            name="human-readable causal narrative",
            standard="a responsible official can narrate why a machine action happened",
            failure_risk="the story may be legible but false or incomplete",
        ),
        ExplanationStandard(
            name="audit trace",
            standard="inputs, routing, model state, approvals, and command-chain links are preserved",
            failure_risk="the trace may be too large for meaningful human judgment",
        ),
        ExplanationStandard(
            name="counterfactual safety account",
            standard="reviewers compare the chosen action to plausible alternatives",
            failure_risk="alternatives can become courtroom theater after the emergency has passed",
        ),
        ExplanationStandard(
            name="authorized override signature",
            standard="a human authority accepts final accountability for intervention or non-intervention",
            failure_risk="signature rituals can launder system opacity into fake accountability",
        ),
    )


def _accountability_failure_modes() -> tuple[AccountabilityFailureMode, ...]:
    return (
        AccountabilityFailureMode(
            name="fake accountability",
            description="a human signs for a decision they cannot actually understand or control",
        ),
        AccountabilityFailureMode(
            name="infrastructure paralysis",
            description="critical systems stall while waiting for explanation standards to be satisfied",
        ),
        AccountabilityFailureMode(
            name="ritualized control",
            description="override ceremonies reassure the public without changing machine dependence",
        ),
        AccountabilityFailureMode(
            name="command-chain law drift",
            description="legal chains optimize for blame assignment instead of operational truth",
        ),
        AccountabilityFailureMode(
            name="performative human sovereignty",
            description="institutions preserve the appearance of human authority while hidden automation still governs outcomes",
        ),
    )


def _causal_court_functions() -> tuple[CausalCourtFunction, ...]:
    return (
        CausalCourtFunction(
            name="reason-chain adjudication",
            function="reconstruct why a machine-mediated infrastructure action occurred",
            pressure="courts may mistake clean narratives for accurate causality",
        ),
        CausalCourtFunction(
            name="override legitimacy review",
            function="decide whether intervention, refusal, or delay was lawful",
            pressure="lawful action may still be operationally disastrous",
        ),
        CausalCourtFunction(
            name="explanation standard setting",
            function="define what counts as enough explanation for high-autonomy systems",
            pressure="standards can become rituals that match human anxiety more than system truth",
        ),
        CausalCourtFunction(
            name="command-chain accountability",
            function="assign responsibility across engineers, operators, auditors, and officials",
            pressure="accountability can become blame distribution instead of restored control",
        ),
    )


def _human_override_doctrine_implications() -> tuple[str, ...]:
    return (
        "Human override is meaningful only when the human can alter the causal chain, not just approve a post-hoc story.",
        "Explanation standards must distinguish operational understanding from public reassurance.",
        "Command-chain law can create accountability theater if responsibility is detached from causal power.",
        "Infrastructure paralysis is a doctrine failure, not merely a technical delay.",
        "Human-legible control may require admitting where human authority is supervisory rather than sovereign.",
    )


def _generated_story_or_worldbuilding_pressures() -> tuple[str, ...]:
    return (
        "Causal Court cases can become murder-trial-like battles over whether an explanation was real or ritual.",
        "Engineers may design systems to satisfy courts rather than to preserve infrastructure resilience.",
        "Officials may prefer paralysis over authorizing an action whose causal chain cannot be defended.",
        "Black-market autonomy can emerge wherever legal explanation standards make survival impossible.",
        "The setting pressure is not whether machines rebel, but whether humans can govern dependence honestly.",
    )


def _next_work_items() -> tuple[str, ...]:
    return (
        "Roger reviews whether fake accountability and infrastructure paralysis are useful setting pressures.",
        "Choose one Causal Court case as a deterministic micro-scenario if this expansion is approved.",
        "Preserve non-proofs before any model/runtime/provider or product-wedge boundary.",
    )


def build_human_control_infrastructure_complexity_expansion() -> FounderNativeHumanControlInfrastructureExpansion:
    parent = build_human_override_contradiction_analysis()

    return FounderNativeHumanControlInfrastructureExpansion(
        expansion_name=EXPANSION_NAME,
        boundary=BOUNDARY,
        setting_title=SETTING_TITLE,
        parent_analysis_name=ANALYSIS_NAME,
        contradiction_area=CONTRADICTION_AREA,
        central_design_engine_contradiction=CENTRAL_DESIGN_ENGINE_CONTRADICTION,
        core_claim=CORE_CLAIM,
        infrastructure_domains=_infrastructure_domains(),
        explanation_standards=_explanation_standards(),
        accountability_failure_modes=_accountability_failure_modes(),
        causal_court_functions=_causal_court_functions(),
        human_override_doctrine_implications=_human_override_doctrine_implications(),
        generated_story_or_worldbuilding_pressures=_generated_story_or_worldbuilding_pressures(),
        next_work_items=_next_work_items(),
        explicit_non_proofs=tuple(dict.fromkeys((*parent.explicit_non_proofs, *NON_PROOFS))),
        product_wedge_selection=NO_FIRST_PRODUCT_WEDGE_SELECTED,
        first_product_wedge_selected=False,
        phase_387_implemented=False,
        runtime_required=False,
        provider_model_required=False,
        recommended_next_boundary=RECOMMENDED_NEXT_BOUNDARY,
    )


def build_human_control_infrastructure_complexity_expansion_dict() -> dict[str, Any]:
    return build_human_control_infrastructure_complexity_expansion().to_dict()
