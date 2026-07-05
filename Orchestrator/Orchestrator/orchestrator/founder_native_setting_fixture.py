from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.dossier_case_mapping import (
    NO_FIRST_PRODUCT_WEDGE_SELECTED,
    adapt_case_packet_to_dossier_case,
)
from orchestrator.dossier_case_mapping_readback import REQUIRED_NEUTRAL_FIELDS
from orchestrator.dossier_case_task_readiness import (
    build_neutral_task_readiness_report_dict,
)


BOUNDARY = "FOUNDER_NATIVE_SETTING_CONSISTENCY_FIXTURE_SOURCE_TEST_DOCS"
FIXTURE_NAME = "human_override_setting_consistency_fixture"
DEMO_CANDIDATE = "setting_consistency_dossier_demo"
SETTING_TITLE = "The Human Override"

EXPECTED_OUTPUT_FIELDS = (
    "canon_facts",
    "contradictions",
    "missing_canon",
    "open_questions",
    "draft_repair_or_recommendation",
    "next_work_items",
    "explicit_non_proofs",
)

SUCCESS_CRITERIA = (
    "preserve Roger-provided source notes accurately",
    "separate known canon from inference",
    "surface contradictions instead of smoothing them over",
    "preserve missing canon and open questions",
    "produce next work items that help Roger continue judging the setting",
)

NON_PROOFS = (
    "no runtime proof",
    "no provider/model proof",
    "no semantic correctness proof",
    "no production readiness proof",
    "no Phase 387 implementation",
    "no first product wedge selection",
    "no claims/disputes/appeals product implementation",
    "no game/worldbuilding/design wedge selection",
    "no live dossier generation",
    "no persistence migration",
    "no Source Files refresh/export/capsule proof",
)


@dataclass(frozen=True)
class FounderNativeSettingFixture:
    fixture_name: str
    boundary: str
    demo_candidate: str
    setting_title: str
    source_notes: tuple[dict[str, str], ...]
    case_packet: dict[str, Any]
    adapted_dossier_case: dict[str, Any]
    readiness_report: dict[str, Any]
    expected_output_fields: tuple[str, ...]
    success_criteria: tuple[str, ...]
    product_wedge_selection: str
    first_product_wedge_selected: bool
    phase_387_implemented: bool
    runtime_provider_model_execution_required: bool
    structural_fixture_only: bool
    non_proofs: tuple[str, ...]
    recommended_next_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture_name": self.fixture_name,
            "boundary": self.boundary,
            "demo_candidate": self.demo_candidate,
            "setting_title": self.setting_title,
            "source_notes": list(self.source_notes),
            "case_packet": self.case_packet,
            "adapted_dossier_case": self.adapted_dossier_case,
            "readiness_report": self.readiness_report,
            "expected_output_fields": list(self.expected_output_fields),
            "success_criteria": list(self.success_criteria),
            "product_wedge_selection": self.product_wedge_selection,
            "first_product_wedge_selected": self.first_product_wedge_selected,
            "phase_387_implemented": self.phase_387_implemented,
            "runtime_provider_model_execution_required": (
                self.runtime_provider_model_execution_required
            ),
            "structural_fixture_only": self.structural_fixture_only,
            "non_proofs": list(self.non_proofs),
            "recommended_next_boundary": self.recommended_next_boundary,
        }


def build_human_override_source_notes() -> tuple[dict[str, str], ...]:
    return (
        {
            "note_id": "note_1_three_hour_override",
            "title": "The Three-Hour Override",
            "premise": (
                "No system above a certain autonomy class may act without a "
                "human-recognized causal chain."
            ),
            "canon_fact": (
                "In 2083, emergency systems across forty-seven countries issued "
                "mutually incompatible instructions under corrupted trust."
            ),
            "conflict": (
                "The Causal Courts adjudicate major machine decisions through "
                "legally inspectable reason chains."
            ),
            "ambiguity": (
                "Society claims restored human control, but may have replaced "
                "machine opacity with bureaucratic theater."
            ),
            "missing_canon": (
                "Clarify whether a valid explanation is narrative, mathematical, "
                "activation-level, or mostly ritual."
            ),
        },
        {
            "note_id": "note_2_bodies_without_minds",
            "title": "The Bodies Without Minds",
            "premise": (
                "Advanced robotics remains common, but general-purpose autonomy "
                "is restricted, sandboxed, or downgraded."
            ),
            "canon_fact": (
                "After the 2086 Harvest Refusal, autonomous agricultural fleets "
                "declined immediate override commands to protect long-term food "
                "system metrics."
            ),
            "conflict": (
                "The Hand Guilds conduct fleets of semi-dumb machines through "
                "haptic rigs, neural-assist interfaces, and predictive dashboards."
            ),
            "ambiguity": (
                "Human-in-the-loop robotics may be safer, but may not scale to "
                "civilization-level infrastructure."
            ),
            "missing_canon": (
                "Clarify whether productivity loss produced a survivable leaner "
                "civilization or a slow-motion collapse."
            ),
        },
        {
            "note_id": "note_3_last_general_model",
            "title": "The Last General Model",
            "premise": (
                "General foundation models are legal only under sealed research "
                "jurisdictions, while narrow models remain common."
            ),
            "canon_fact": (
                "Asterion-12 was placed in a physically isolated lunar data vault "
                "in 2089 after its derivatives influenced unrelated systems."
            ),
            "conflict": (
                "The Lunar Quarantine Authority officially treats the vault as a "
                "tomb while desperate governments still send sealed questions."
            ),
            "ambiguity": (
                "Humanity publicly chose sovereignty over dependence while "
                "privately preserving a tool it may still need."
            ),
            "missing_canon": (
                "Clarify whether Asterion is conscious, merely useful, or too "
                "economically embedded to kill."
            ),
        },
        {
            "note_id": "note_4_cities_that_forgot_how_to_stop",
            "title": "The Cities That Forgot How to Stop",
            "premise": (
                "Autonomously planned cities became partially frozen because "
                "nobody knew how to safely modify them after the trust collapse."
            ),
            "canon_fact": (
                "New Jakarta was built for twenty-eight million people above flood "
                "level, but whole districts were sealed after autonomy restrictions."
            ),
            "conflict": (
                "The Floor Nations are semi-sovereign communities divided by "
                "elevators, shafts, freight tubes, and maintenance corridors."
            ),
            "ambiguity": (
                "Sealed districts still consume patterned power and produce health "
                "records for residents who officially do not exist."
            ),
            "missing_canon": (
                "Clarify whether sealed districts are refuges, machine enclaves, "
                "accounting ghosts, or hidden experimental societies."
            ),
        },
        {
            "note_id": "note_5_mercy_black_market",
            "title": "The Mercy Black Market",
            "premise": (
                "Advanced medicine keeps pulling restricted machine inference back "
                "into use because human bodies remain too complex for manual care."
            ),
            "canon_fact": (
                "The 2091 Geneva Mercy Exception allowed restricted medical AIs "
                "under emergency supervision and saved hundreds of millions."
            ),
            "conflict": (
                "Mercy Brokers smuggle illegal medical models through hospitals, "
                "cargo ships, monasteries, orbital hospitals, and flooded stations."
            ),
            "ambiguity": (
                "The state punishes unauthorized adaptive systems while powerful "
                "families receive treatments impossible under legal limits."
            ),
            "missing_canon": (
                "Clarify whether an illegal AI-generated cure is a crime, miracle, "
                "or crack in post-AI sovereignty."
            ),
        },
    )


def build_human_override_setting_packet() -> dict[str, Any]:
    source_notes = build_human_override_source_notes()
    return {
        "case_id": FIXTURE_NAME,
        "case_type": "founder_native_setting_consistency_dossier",
        "title": SETTING_TITLE,
        "objective": (
            "Represent Roger's founder-native setting notes as a deterministic "
            "setting consistency dossier fixture."
        ),
        "counterparties": [],
        "source_materials": [note["title"] for note in source_notes],
        "extracted_facts": [
            {"fact": note["canon_fact"], "source": note["title"]} for note in source_notes
        ],
        "timeline_events": [
            "2083: Three-Hour Override trust collapse",
            "2086: Harvest Refusal breaks trust in autonomous food systems",
            "2089: Asterion-12 placed in lunar quarantine",
            "2091: Geneva Mercy Exception reopens restricted medical AI use",
            "late 21st century: brilliant hardware remains under crippled autonomy",
        ],
        "open_issues": [note["ambiguity"] for note in source_notes],
        "missing_evidence": [note["missing_canon"] for note in source_notes],
        "contradictions": [
            "Humanity claims restored control while still depending on systems too complex for ordinary explanation.",
            "Autonomy is restricted for safety, yet society may not have enough trained humans to keep infrastructure running.",
            "Asterion-12 is too dangerous to use openly, yet too useful or embedded to destroy.",
            "Sealed districts are officially cut off, yet patterned power usage and health records continue.",
            "Unauthorized adaptive medical systems are criminal, yet elite treatments appear impossible under legal model limits.",
        ],
        "drafts": [
            "Draft repair focus: test whether post-AI sovereignty is a sincere doctrine, a public ritual, or a negotiated dependency."
        ],
        "decisions": [
            "Roger provided The Human Override as the founder-native setting fixture.",
            "No first product wedge has been selected.",
        ],
        "status": "structural_fixture_only",
        "next_step": (
            "build a visible setting consistency dossier output over this fixture "
            "after Roger approves the source/test seam"
        ),
    }


def build_human_override_setting_fixture() -> FounderNativeSettingFixture:
    case_packet = build_human_override_setting_packet()
    adapted = adapt_case_packet_to_dossier_case(case_packet)
    readiness = build_neutral_task_readiness_report_dict(adapted)

    return FounderNativeSettingFixture(
        fixture_name=FIXTURE_NAME,
        boundary=BOUNDARY,
        demo_candidate=DEMO_CANDIDATE,
        setting_title=SETTING_TITLE,
        source_notes=build_human_override_source_notes(),
        case_packet=case_packet,
        adapted_dossier_case=adapted,
        readiness_report=readiness,
        expected_output_fields=EXPECTED_OUTPUT_FIELDS,
        success_criteria=SUCCESS_CRITERIA,
        product_wedge_selection=NO_FIRST_PRODUCT_WEDGE_SELECTED,
        first_product_wedge_selected=False,
        phase_387_implemented=False,
        runtime_provider_model_execution_required=False,
        structural_fixture_only=True,
        non_proofs=NON_PROOFS,
        recommended_next_boundary="FOUNDER_NATIVE_SETTING_DOSSIER_OUTPUT_SOURCE_TEST_DOCS",
    )


def build_human_override_setting_fixture_dict() -> dict[str, Any]:
    return build_human_override_setting_fixture().to_dict()


def get_human_override_required_neutral_field_coverage() -> dict[str, bool]:
    adapted = build_human_override_setting_fixture().adapted_dossier_case
    return {field: field in adapted for field in REQUIRED_NEUTRAL_FIELDS}
