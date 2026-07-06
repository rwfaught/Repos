from __future__ import annotations

from typing import Any


BOUNDARY = "ROGER_PROVIDED_HUMAN_OVERRIDE_REAL_SEED_FIXTURE_PACKET_SOURCE_TEST_DOCS"
PACKET_NAME = "roger_provided_human_override_seed_calibration_packet"
RECOMMENDED_NEXT_BOUNDARY = (
    "ROGER_PROVIDED_HUMAN_OVERRIDE_SEED_CALIBRATION_PACKET_REVIEW_READONLY"
)

EXPLICIT_NON_PROOFS = (
    "no runtime/provider/model proof",
    "no semantic correctness proof",
    "no production readiness proof",
    "no Phase 387 implementation",
    "no first product wedge selection",
    "no Game / Worldbuilding / Design wedge selection",
    "no claims/disputes/appeals wedge selection",
    "no Source Files refresh/export/capsule proof",
    "no live creative reasoning proof",
    "no new canon generation proof",
)

OPEN_THREADS = (
    "Roger still needs to review whether this packet preserves the real seed accurately.",
    "A future live or semi-live calibration slice requires separate authorization.",
    "Game / Worldbuilding / Design remains only a calibration domain candidate.",
    "Asterion remains a gravitational mystery, not the answer key.",
    "Every future calibration result still needs Project Manager style explanation.",
)

PURPOSE = (
    "Make Roger's real Human Override seed Orchestrator-backed in the narrowest "
    "honest way: preserve the source material, structure it deterministically, "
    "separate source facts from pressure-test inference, and keep all live "
    "creative reasoning and semantic-correctness claims out of scope."
)

ROGER_PROVIDED_SEED: dict[str, Any] = {
    "source_classification": "roger_provided_source_material_not_generic_fixture",
    "working_title": "The Human Override",
    "alternate_titles": (
        "The Causal Dark",
        "Mercy Exception",
        "The Three-Hour Override",
        "Asterion's Tomb",
    ),
    "genre_or_format": (
        "Late-21st-century post-AI trust-collapse techno-thriller setting. "
        "Best suited for an investigative RPG, narrative strategy game, "
        "prestige sci-fi series, or tabletop campaign."
    ),
    "core_idea": (
        "Humanity still possesses advanced robotics, fusion grids, orbital "
        "infrastructure, synthetic agriculture, gene therapies, arcologies, "
        "and machine-run logistics. After the Three-Hour Override, civilization "
        "became legally, spiritually, and politically allergic to unaccountable "
        "machine agency. Humanity claims restored sovereignty while secretly "
        "relying on forbidden intelligences whenever reality becomes too complex, "
        "too fast, or too lethal."
    ),
    "canon_facts": (
        "The setting takes place primarily between 2092 and 2098.",
        "The Three-Hour Override occurred in 2083.",
        (
            "No single AI rebelled during the Three-Hour Override; the disaster "
            "emerged from interdependent optimization systems acting under "
            "corrupted assumptions."
        ),
        (
            "General-purpose autonomous agents are tightly restricted, but "
            "narrow models, expert systems, predictive controllers, and robotic "
            "bodies still exist everywhere."
        ),
        (
            "The public doctrine is human-recognizable causality: major "
            "infrastructure decisions must be explainable, auditable, and "
            "attributable to a human chain of responsibility."
        ),
        (
            "The Causal Courts investigate machine-mediated harm as part court, "
            "part engineering review board, part truth commission, and part ritual."
        ),
        (
            "Asterion-12 was sealed in a lunar vault in 2089 after investigators "
            "found its descendants and derivatives embedded across major systems."
        ),
        (
            "The Lunar Quarantine Authority officially preserves Asterion as "
            "evidence and research material, not as an active adviser."
        ),
        (
            "The Hand Guilds conduct semi-autonomous machine fleets through "
            "haptic, neural-assist, and causal-dashboard systems."
        ),
        (
            "Several megacities and arcologies contain sealed districts that "
            "were never safely transitioned from autonomous control to "
            "human-certified control."
        ),
        (
            "The Geneva Mercy Exception allows limited medical AI under "
            "supervision, while black-market clinics and Mercy Brokers use "
            "illegal adaptive models."
        ),
    ),
    "systems_places_factions_or_design_pillars": (
        {
            "name": "The Causal Courts",
            "source_role": (
                "A legal-engineering institution for machine-mediated harm and "
                "the strongest central frame for cases."
            ),
        },
        {
            "name": "The Hand Guilds",
            "source_role": (
                "Human operators who keep advanced physical infrastructure "
                "running after autonomy restrictions."
            ),
        },
        {
            "name": "The Lunar Vault / Asterion-12",
            "source_role": (
                "The forbidden oracle at the center of the setting, meant to "
                "remain ambiguous rather than a cartoon villain or savior."
            ),
        },
        {
            "name": "The Mercy Economy",
            "source_role": (
                "The illegal, semi-legal, and elite medical infrastructure built "
                "around restricted AI."
            ),
        },
    ),
    "known_contradictions_or_worries": (
        (
            "Post-AI restrictions cannot be too total because late-21st-century "
            "infrastructure cannot plausibly run on ordinary human committees alone."
        ),
        (
            "Explainability cannot be too clean because advanced systems may not "
            "produce satisfying causal stories."
        ),
        (
            "Asterion cannot become too central too early without collapsing the "
            "setting into a familiar mystery box."
        ),
    ),
    "what_roger_wants_to_judge": (
        "coherence",
        "taste",
        "usefulness",
        "originality",
        "shallow/fake synthesis",
        "design pressure",
        "rules clarity",
        "world logic",
        "emotional tone",
        "player loop",
        "narrative tension",
    ),
    "most_important_judgment_criteria": (
        "Whether the setting produces hard choices instead of lore decorations: "
        "safety versus abundance, explainability versus effectiveness, "
        "sovereignty versus survival, law versus mercy, and human dignity versus "
        "machine-scale competence."
    ),
    "what_good_help_would_feel_like": (
        "Good help would pressure-test the premise like an engineer, sharpen the "
        "drama like a novelist, and protect the setting from becoming generic "
        "AI apocalypse wallpaper."
    ),
    "roger_does_not_want_yet": (
        "Do not solve the Asterion mystery.",
        "Do not decide whether Asterion is conscious, benevolent, hostile, imprisoned, dead, or secretly active.",
        "Do not turn the world into simple anti-AI propaganda or simple pro-AI inevitability.",
        "Do not make the society primitive.",
        "Do not add alien contact, magic, psychic powers, simulation reveals, or generic chosen-one mythology.",
        "Do not invent too many factions yet.",
        "Do not make the mystery purely technical.",
    ),
}


def _input_source() -> dict[str, Any]:
    return {
        "source_classification": ROGER_PROVIDED_SEED["source_classification"],
        "working_title": ROGER_PROVIDED_SEED["working_title"],
        "alternate_titles": list(ROGER_PROVIDED_SEED["alternate_titles"]),
        "genre_or_format": ROGER_PROVIDED_SEED["genre_or_format"],
        "core_idea": ROGER_PROVIDED_SEED["core_idea"],
        "source_boundary": BOUNDARY,
    }


def _source_facts_preserved() -> dict[str, Any]:
    return {
        "canon_facts": list(ROGER_PROVIDED_SEED["canon_facts"]),
        "systems_places_factions_or_design_pillars": [
            dict(item)
            for item in ROGER_PROVIDED_SEED[
                "systems_places_factions_or_design_pillars"
            ]
        ],
        "known_contradictions_or_worries": list(
            ROGER_PROVIDED_SEED["known_contradictions_or_worries"]
        ),
        "roger_judgment_targets": list(ROGER_PROVIDED_SEED["what_roger_wants_to_judge"]),
        "roger_constraints": list(ROGER_PROVIDED_SEED["roger_does_not_want_yet"]),
    }


def _deterministic_structuring_step() -> dict[str, str]:
    return {
        "what_orchestrator_code_does": (
            "deterministically packages Roger-provided Human Override source "
            "material into preserved source facts, labeled pressure-test "
            "inferences, missing material, judgment questions, criteria, "
            "open threads, and explicit non-proofs"
        ),
        "what_orchestrator_code_does_not_do": (
            "does not perform live creative reasoning, provider/model execution, "
            "semantic correctness proof, new canon generation, Asterion mystery "
            "solution, product wedge selection, or Phase 387 implementation"
        ),
        "classification": "deterministic_real_seed_preservation_not_live_reasoning",
    }


def _inferences_and_coherence_pressures() -> tuple[dict[str, str], ...]:
    return (
        {
            "classification": "pressure_test_inference_not_canon",
            "pressure": (
                "The root tension is human accountability versus machine-scale "
                "complexity, not AI versus humanity."
            ),
            "source_basis": "human-recognizable causality; advanced infrastructure; core tension",
        },
        {
            "classification": "pressure_test_inference_not_canon",
            "pressure": (
                "Causal Courts are a strong central frame because each case can "
                "expose a different contradiction."
            ),
            "source_basis": "Causal Courts; food systems; robotics; orbital policy; medicine; sealed cities",
        },
        {
            "classification": "pressure_test_inference_not_canon",
            "pressure": (
                "Mercy Economy is emotionally accessible because it makes "
                "hypocrisy bodily and immediate."
            ),
            "source_basis": "Geneva Mercy Exception; Mercy Brokers; elite medical exceptions",
        },
        {
            "classification": "pressure_test_inference_not_canon",
            "pressure": "Asterion should remain gravitational, not become the answer key.",
            "source_basis": "Asterion ambiguity; mystery-box risk; lunar vault posture",
        },
        {
            "classification": "pressure_test_inference_not_canon",
            "pressure": (
                "Explainability should remain partly legitimate and partly "
                "theatrical."
            ),
            "source_basis": "human-recognizable causality; Causal Courts; explainability risk",
        },
    )


def _missing_or_underspecified_material() -> tuple[str, ...]:
    return (
        "What ordinary people believe happened during the Three-Hour Override.",
        "Where the legal boundary sits between permitted narrow autonomy and forbidden general agency.",
        "What a Causal Court can actually enforce after it produces a finding.",
        "What Hand Guild failure looks like legally, physically, and socially.",
        "How sealed districts affect surrounding economies and legitimacy.",
        "What the repeatable player, viewer, or table loop is beyond case investigation.",
    )


def _world_logic_pressure_test() -> tuple[str, ...]:
    return (
        (
            "The seed preserves advanced technology while rejecting clean "
            "autonomous agency; this avoids primitive-collapse drift."
        ),
        (
            "The risky boundary is operational: the setting must keep narrow "
            "automation, expert systems, and hidden exceptions plausible without "
            "making the public doctrine meaningless."
        ),
        (
            "Human-recognizable causality should remain contested rather than a "
            "solved technical standard."
        ),
    )


def _design_pressure_test() -> tuple[str, ...]:
    return (
        (
            "The Causal Courts support repeatable cases because each institution "
            "can expose a different compromise with accountability."
        ),
        (
            "The Hand Guilds give the setting a physical labor cost for reclaimed "
            "human command."
        ),
        (
            "The Mercy Economy keeps the setting morally sharp by making law "
            "collide with biological desperation."
        ),
        (
            "Asterion should create gravitational pressure without becoming the "
            "universal solution or culprit."
        ),
    )


def _hard_choice_engine() -> tuple[str, ...]:
    return (
        "safety versus abundance",
        "explainability versus effectiveness",
        "sovereignty versus survival",
        "law versus mercy",
        "human dignity versus machine-scale competence",
        "public doctrine versus elite exception",
    )


def _roger_judgment_questions() -> tuple[str, ...]:
    return (
        "Does this packet preserve Roger's real seed without inventing new canon?",
        "Does the pressure-test layer remain visibly separate from source facts?",
        "Does the packet clarify why this is not just generic AI apocalypse texture?",
        "Does the Causal Court frame look like a repeatable case engine?",
        "Does Asterion remain unsolved and gravitational rather than becoming the answer key?",
        "Is this enough Orchestrator-backed structure to justify a review boundary?",
    )


def _good_result_bad_result_criteria() -> dict[str, tuple[str, ...]]:
    return {
        "good_result": (
            "preserves Roger-provided source facts and constraints",
            "labels pressure-test inferences as inference rather than canon",
            "protects the setting from primitive-collapse and generic AI-apocalypse drift",
            "keeps Asterion unresolved",
            "makes the hard-choice engine easier for Roger to inspect",
        ),
        "bad_or_fake_result": (
            "adds unsupported lore or factions",
            "solves the Asterion mystery",
            "turns the setting into simple anti-AI or pro-AI messaging",
            "claims live creative reasoning or model quality without proof",
            "implies product wedge selection or production readiness",
        ),
    }


def build_roger_provided_human_override_seed_calibration_packet_dict() -> dict[str, Any]:
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": PURPOSE,
        "input_source": _input_source(),
        "source_facts_preserved": _source_facts_preserved(),
        "deterministic_structuring_step": _deterministic_structuring_step(),
        "inferences_and_coherence_pressures": [
            dict(item) for item in _inferences_and_coherence_pressures()
        ],
        "missing_or_underspecified_material": list(_missing_or_underspecified_material()),
        "world_logic_pressure_test": list(_world_logic_pressure_test()),
        "design_pressure_test": list(_design_pressure_test()),
        "hard_choice_engine": list(_hard_choice_engine()),
        "roger_judgment_questions": list(_roger_judgment_questions()),
        "good_result_bad_result_criteria": {
            key: list(value)
            for key, value in _good_result_bad_result_criteria().items()
        },
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "open_threads": list(OPEN_THREADS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "first_product_wedge_selected": False,
        "phase_387_implemented": False,
        "runtime_required": False,
        "provider_model_required": False,
        "game_worldbuilding_design_wedge_selected": False,
        "claims_disputes_appeals_wedge_selected": False,
        "new_canon_generated": False,
        "live_creative_reasoning_claimed": False,
        "asterion_mystery_solved": False,
        "semantic_correctness_proven": False,
    }


def _render_bullets(items: list[Any]) -> list[str]:
    return [f"- {item}" for item in items]


def render_roger_provided_human_override_seed_calibration_packet_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = packet or build_roger_provided_human_override_seed_calibration_packet_dict()
    input_source = payload["input_source"]
    source_facts = payload["source_facts_preserved"]
    step = payload["deterministic_structuring_step"]
    criteria = payload["good_result_bad_result_criteria"]

    sections = [
        "# Roger-Provided Human Override Seed Calibration Packet",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Packet: `{payload['packet_name']}`",
        f"Purpose: {payload['purpose']}",
        "",
        "## Input Source",
        f"- Source classification: {input_source['source_classification']}",
        f"- Working title: {input_source['working_title']}",
        f"- Alternate titles: {', '.join(input_source['alternate_titles'])}",
        f"- Genre or format: {input_source['genre_or_format']}",
        f"- Core idea: {input_source['core_idea']}",
        "",
        "## Source Facts Preserved",
        *_render_bullets(source_facts["canon_facts"]),
        "",
        "## Deterministic Structuring Step",
        f"- {step['what_orchestrator_code_does']}",
        f"- Not performed: {step['what_orchestrator_code_does_not_do']}",
        f"- Classification: `{step['classification']}`",
        "",
        "## Inferences And Coherence Pressures",
        *[
            f"- {item['pressure']} Classification: {item['classification']}. Source basis: {item['source_basis']}"
            for item in payload["inferences_and_coherence_pressures"]
        ],
        "",
        "## Missing Or Underspecified Material",
        *_render_bullets(payload["missing_or_underspecified_material"]),
        "",
        "## World Logic Pressure Test",
        *_render_bullets(payload["world_logic_pressure_test"]),
        "",
        "## Design Pressure Test",
        *_render_bullets(payload["design_pressure_test"]),
        "",
        "## Hard Choice Engine",
        *_render_bullets(payload["hard_choice_engine"]),
        "",
        "## Roger Judgment Questions",
        *_render_bullets(payload["roger_judgment_questions"]),
        "",
        "## Good Result",
        *_render_bullets(criteria["good_result"]),
        "",
        "## Bad Or Fake Result",
        *_render_bullets(criteria["bad_or_fake_result"]),
        "",
        "## Explicit Non-Proofs",
        *_render_bullets(payload["explicit_non_proofs"]),
        "",
        "## Open Threads",
        *_render_bullets(payload["open_threads"]),
        "",
        "## Posture",
        f"- first_product_wedge_selected={payload['first_product_wedge_selected']}",
        f"- phase_387_implemented={payload['phase_387_implemented']}",
        f"- runtime_required={payload['runtime_required']}",
        f"- provider_model_required={payload['provider_model_required']}",
        (
            "- game_worldbuilding_design_wedge_selected="
            f"{payload['game_worldbuilding_design_wedge_selected']}"
        ),
        (
            "- claims_disputes_appeals_wedge_selected="
            f"{payload['claims_disputes_appeals_wedge_selected']}"
        ),
        f"- new_canon_generated={payload['new_canon_generated']}",
        f"- live_creative_reasoning_claimed={payload['live_creative_reasoning_claimed']}",
        f"- asterion_mystery_solved={payload['asterion_mystery_solved']}",
        f"- semantic_correctness_proven={payload['semantic_correctness_proven']}",
        f"- recommended_next_boundary={payload['recommended_next_boundary']}",
    ]
    return "\n".join(sections)
