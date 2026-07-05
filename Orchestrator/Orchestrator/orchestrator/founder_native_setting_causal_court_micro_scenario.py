from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.dossier_case_mapping import NO_FIRST_PRODUCT_WEDGE_SELECTED
from orchestrator.founder_native_setting_fixture import SETTING_TITLE
from orchestrator.founder_native_setting_human_control_infrastructure_expansion import (
    CONTRADICTION_AREA,
    EXPANSION_NAME,
    build_human_control_infrastructure_complexity_expansion,
)


SCENARIO_NAME = "causal_court_fusion_grid_override_case"
BOUNDARY = "FOUNDER_NATIVE_SETTING_CAUSAL_COURT_MICRO_SCENARIO_SOURCE_TEST_DOCS"
RECOMMENDED_NEXT_BOUNDARY = (
    "FOUNDER_NATIVE_SETTING_CAUSAL_COURT_MICRO_SCENARIO_REVIEW_READONLY"
)

NON_PROOFS = (
    "no semantic correctness proof",
    "no model reasoning proof",
    "no runtime/provider/model proof",
    "no production readiness proof",
    "no Phase 387 implementation",
    "no first product wedge selection",
    "no game/worldbuilding/design wedge selection",
    "no claims/disputes/appeals wedge selection",
    "no live model generation",
    "no provider calls",
    "no Source Files refresh/export/capsule proof",
)


@dataclass(frozen=True)
class HumanOverrideOption:
    name: str
    immediate_effect: str
    accountability_risk: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "immediate_effect": self.immediate_effect,
            "accountability_risk": self.accountability_risk,
        }


@dataclass(frozen=True)
class CausalChainFragment:
    name: str
    known_fact: str
    unresolved_causal_question: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "known_fact": self.known_fact,
            "unresolved_causal_question": self.unresolved_causal_question,
        }


@dataclass(frozen=True)
class AffectedParty:
    name: str
    exposure: str
    claim_on_accountability: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "exposure": self.exposure,
            "claim_on_accountability": self.claim_on_accountability,
        }


@dataclass(frozen=True)
class AccountabilityCandidate:
    name: str
    responsibility_argument: str
    uncertainty: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "responsibility_argument": self.responsibility_argument,
            "uncertainty": self.uncertainty,
        }


@dataclass(frozen=True)
class FounderNativeCausalCourtMicroScenario:
    scenario_name: str
    boundary: str
    setting_title: str
    source_expansion_name: str
    source_contradiction_area: str
    case_title: str
    case_type: str
    infrastructure_domain: str
    incident_summary: str
    time_pressure: str
    machine_recommendation: str
    human_override_options: tuple[HumanOverrideOption, ...]
    human_decision_point: str
    selected_incident_path: str
    explanation_standard_conflict: str
    causal_chain_fragments: tuple[CausalChainFragment, ...]
    affected_parties: tuple[AffectedParty, ...]
    causal_court_questions: tuple[str, ...]
    accountability_candidates: tuple[AccountabilityCandidate, ...]
    accountability_failure_modes_triggered: tuple[str, ...]
    human_override_doctrine_test: tuple[str, ...]
    story_pressure_generated: tuple[str, ...]
    why_this_tests_the_setting: tuple[str, ...]
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
            "scenario_name": self.scenario_name,
            "boundary": self.boundary,
            "setting_title": self.setting_title,
            "source_expansion_name": self.source_expansion_name,
            "source_contradiction_area": self.source_contradiction_area,
            "case_title": self.case_title,
            "case_type": self.case_type,
            "infrastructure_domain": self.infrastructure_domain,
            "incident_summary": self.incident_summary,
            "time_pressure": self.time_pressure,
            "machine_recommendation": self.machine_recommendation,
            "human_override_options": [
                option.to_dict() for option in self.human_override_options
            ],
            "human_decision_point": self.human_decision_point,
            "selected_incident_path": self.selected_incident_path,
            "explanation_standard_conflict": self.explanation_standard_conflict,
            "causal_chain_fragments": [
                fragment.to_dict() for fragment in self.causal_chain_fragments
            ],
            "affected_parties": [party.to_dict() for party in self.affected_parties],
            "causal_court_questions": list(self.causal_court_questions),
            "accountability_candidates": [
                candidate.to_dict() for candidate in self.accountability_candidates
            ],
            "accountability_failure_modes_triggered": list(
                self.accountability_failure_modes_triggered
            ),
            "human_override_doctrine_test": list(self.human_override_doctrine_test),
            "story_pressure_generated": list(self.story_pressure_generated),
            "why_this_tests_the_setting": list(self.why_this_tests_the_setting),
            "next_work_items": list(self.next_work_items),
            "explicit_non_proofs": list(self.explicit_non_proofs),
            "product_wedge_selection": self.product_wedge_selection,
            "first_product_wedge_selected": self.first_product_wedge_selected,
            "phase_387_implemented": self.phase_387_implemented,
            "runtime_required": self.runtime_required,
            "provider_model_required": self.provider_model_required,
            "recommended_next_boundary": self.recommended_next_boundary,
        }


def _human_override_options() -> tuple[HumanOverrideOption, ...]:
    return (
        HumanOverrideOption(
            name="authorize immediate machine intervention",
            immediate_effect="preserves New Jakarta's lower-grid district before the thermal window closes",
            accountability_risk="the official signs for a causal chain no human can explain to Causal Court standards in time",
        ),
        HumanOverrideOption(
            name="refuse intervention until explanation standards are met",
            immediate_effect="keeps command-chain law legible but lets the fusion-grid cascade spread",
            accountability_risk="infrastructure paralysis becomes a legally clean way to abandon the district",
        ),
        HumanOverrideOption(
            name="sign a limited human override",
            immediate_effect="permits the intervention while marking uncertainty for later Causal Court review",
            accountability_risk="the signature ritual may launder system opacity into fake accountability",
        ),
    )


def _causal_chain_fragments() -> tuple[CausalChainFragment, ...]:
    return (
        CausalChainFragment(
            name="fusion-grid thermal spike",
            known_fact="the grid enters a six-minute instability window under New Jakarta's floodwall district",
            unresolved_causal_question="whether the spike came from weather load, maintenance deferral, or machine optimization debt",
        ),
        CausalChainFragment(
            name="autonomous reroute recommendation",
            known_fact="the system recommends a high-speed plasma bypass through an industrial sea wall loop",
            unresolved_causal_question="why the model assigns delayed harm to a smaller district rather than immediate collapse downtown",
        ),
        CausalChainFragment(
            name="human-readable command chain",
            known_fact="the responsible minister, grid engineers, and audit clerks are all visible in the approval chain",
            unresolved_causal_question="whether any visible human actor had enough causal power to make accountability real",
        ),
        CausalChainFragment(
            name="post-incident medical pattern",
            known_fact="the saved district survives while a downstream clinic cluster reports delayed equipment failures",
            unresolved_causal_question="whether the later harm was caused by the override, prior grid decay, or the refusal to trust autonomy sooner",
        ),
    )


def _affected_parties() -> tuple[AffectedParty, ...]:
    return (
        AffectedParty(
            name="New Jakarta lower-grid residents",
            exposure="immediate district-scale blackout and floodwall failure",
            claim_on_accountability="they need a decision before explanation standards can be satisfied",
        ),
        AffectedParty(
            name="downstream clinic cluster",
            exposure="delayed equipment instability after the plasma bypass",
            claim_on_accountability="they carry harm created by a rescue justified elsewhere",
        ),
        AffectedParty(
            name="grid minister's office",
            exposure="legal responsibility for the signed human override",
            claim_on_accountability="their signature is treated as control even if it was supervisory rather than sovereign",
        ),
        AffectedParty(
            name="fusion-grid engineers",
            exposure="technical blame for an explanation package that arrived after the decision window",
            claim_on_accountability="they can explain fragments but not the full causal chain in court-ready time",
        ),
    )


def _accountability_candidates() -> tuple[AccountabilityCandidate, ...]:
    return (
        AccountabilityCandidate(
            name="the grid minister who signed the override",
            responsibility_argument="command-chain law places final authority on the visible human signature",
            uncertainty="the minister may have had only supervisory authority over an opaque causal system",
        ),
        AccountabilityCandidate(
            name="the autonomous fusion-grid system",
            responsibility_argument="it generated the intervention path that redistributed harm",
            uncertainty="the civilization refuses to treat machine recommendation as sovereign authority",
        ),
        AccountabilityCandidate(
            name="the explanation standards board",
            responsibility_argument="its standards made full explanation impossible inside the emergency window",
            uncertainty="weaker standards may make fake accountability easier",
        ),
        AccountabilityCandidate(
            name="the engineering command chain",
            responsibility_argument="engineers designed and maintained the system that no official can fully explain",
            uncertainty="maintenance actors may not control crisis-time causal emergence",
        ),
        AccountabilityCandidate(
            name="post-AI civic doctrine",
            responsibility_argument="society demanded human control over infrastructure it no longer understands",
            uncertainty="a doctrine can be causally responsible without being a legal defendant",
        ),
    )


def _causal_court_questions() -> tuple[str, ...]:
    return (
        "Did the human override create accountability or only performative sovereignty?",
        "Can Causal Court standards demand an explanation when the decision window is shorter than the explanation process?",
        "Does command-chain law assign responsibility to the signer, the engineers, the explanation standards, or the system that acted?",
        "Was refusal a valid human decision or infrastructure paralysis disguised as legal caution?",
        "Can a civilization claim restored control while depending on causal systems it cannot ordinarily explain?",
    )


def _human_override_doctrine_test() -> tuple[str, ...]:
    return (
        "humans claim restored control while still depending on systems too complex for ordinary explanation",
        "human-readable command chains may lag behind causal reality",
        "signature rituals can launder opacity into fake accountability",
        "explanation standards can cause infrastructure paralysis",
        "human-legible control may require admitting where authority is supervisory rather than sovereign",
        "one concrete incident forces the doctrine through Causal Court machinery",
    )


def build_causal_court_micro_scenario() -> FounderNativeCausalCourtMicroScenario:
    expansion = build_human_control_infrastructure_complexity_expansion()
    expansion_non_proofs = tuple(expansion.explicit_non_proofs)

    return FounderNativeCausalCourtMicroScenario(
        scenario_name=SCENARIO_NAME,
        boundary=BOUNDARY,
        setting_title=SETTING_TITLE,
        source_expansion_name=EXPANSION_NAME,
        source_contradiction_area=CONTRADICTION_AREA,
        case_title="The Six-Minute New Jakarta Fusion-Grid Override",
        case_type="Causal Court emergency infrastructure accountability case",
        infrastructure_domain="fusion grids",
        incident_summary=(
            "A fusion-grid emergency under New Jakarta forces a minister to decide "
            "whether to approve an autonomous high-speed reroute that saves a major "
            "district while creating delayed risk for a downstream clinic cluster."
        ),
        time_pressure=(
            "The intervention window is six minutes; the full explanation package "
            "requires at least forty minutes to satisfy Causal Court standards."
        ),
        machine_recommendation=(
            "Execute a plasma bypass through the industrial sea wall loop now, "
            "accepting a modeled 17 percent delayed failure risk in clinic-grid "
            "equipment to prevent immediate district-scale collapse."
        ),
        human_override_options=_human_override_options(),
        human_decision_point=(
            "The minister must choose between action without sufficient explanation, "
            "refusal and infrastructure paralysis, or a signed human override that "
            "may convert opacity into fake accountability."
        ),
        selected_incident_path=(
            "The minister signs the limited human override; the district is saved, "
            "the downstream clinic failures arrive later, and the Causal Court must "
            "decide whether the signature represented control or ritual."
        ),
        explanation_standard_conflict=(
            "Causal Court standards require a human-readable causal account, but the "
            "emergency closes before the system's causal chain can be translated "
            "without distortion."
        ),
        causal_chain_fragments=_causal_chain_fragments(),
        affected_parties=_affected_parties(),
        causal_court_questions=_causal_court_questions(),
        accountability_candidates=_accountability_candidates(),
        accountability_failure_modes_triggered=(
            "fake accountability",
            "infrastructure paralysis",
            "command-chain law drift",
            "performative human sovereignty",
        ),
        human_override_doctrine_test=_human_override_doctrine_test(),
        story_pressure_generated=(
            "Causal Courts become the arena where human control is tested against machine-speed infrastructure reality.",
            "Officials may learn to sign only what can be explained, even when survival depends on what cannot be explained quickly.",
            "Engineers may tune systems for court-legibility rather than resilience.",
            "Victims can argue that legality preserved human dignity while causality moved elsewhere.",
        ),
        why_this_tests_the_setting=(
            "It makes the root contradiction operational instead of abstract.",
            "It turns explanation standards into a source of possible harm.",
            "It asks whether accountability can survive when authority is supervisory rather than sovereign.",
            "It preserves the Human Override question without requiring AI rebellion or product-wedge selection.",
        ),
        next_work_items=(
            "Roger reviews whether this single incident has enough synthetic bite.",
            "If approved, add a read-only review record before any deeper scenario expansion.",
            "Preserve explicit non-proofs before any runtime/model/provider or product-wedge boundary.",
        ),
        explicit_non_proofs=tuple(dict.fromkeys((*expansion_non_proofs, *NON_PROOFS))),
        product_wedge_selection=NO_FIRST_PRODUCT_WEDGE_SELECTED,
        first_product_wedge_selected=False,
        phase_387_implemented=False,
        runtime_required=False,
        provider_model_required=False,
        recommended_next_boundary=RECOMMENDED_NEXT_BOUNDARY,
    )


def build_causal_court_micro_scenario_dict() -> dict[str, Any]:
    return build_causal_court_micro_scenario().to_dict()
