from __future__ import annotations

from typing import Any


BOUNDARY = "ROGER_LEGIBLE_GAME_WORLDBUILDING_DESIGN_CALIBRATION_PACKET_SOURCE_TEST_DOCS"
PACKET_NAME = "roger_legible_game_worldbuilding_design_calibration_packet"
RECOMMENDED_NEXT_BOUNDARY = (
    "ROGER_LEGIBLE_GAME_WORLDBUILDING_DESIGN_CALIBRATION_PACKET_REVIEW_READONLY"
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
    "Roger still needs a live or semi-live calibration slice later.",
    "Game / Worldbuilding / Design remains only a calibration domain candidate.",
    "Future live model execution would require separate authorization.",
    "Every calibration result needs Project Manager style explanation.",
    "A real Roger-provided seed is still needed after the fixture packet.",
)

PURPOSE = (
    "Give Roger a deterministic calibration packet over a compact Game / "
    "Worldbuilding / Design fixture seed so he can judge coherence, usefulness, "
    "shallow synthesis, fake insight, and milestone comprehension without "
    "selecting a product wedge."
)

STATIC_FIXTURE_SEED: dict[str, Any] = {
    "working_title": "The Glass Orchard",
    "genre_or_format": "single-session narrative design seed for a post-collapse exploration game",
    "canon_facts": (
        "The city grows memory-bearing fruit from glass trees.",
        "Each fruit contains one preserved civic memory from before the collapse.",
        "Harvesters can eat a fruit once, then the memory is gone.",
        "The Orchard Council rationed memories after the winter blackout.",
        "Children born after the collapse treat memories as currency, not history.",
        "The last working tram line runs through the orchard at midnight.",
        "A forbidden cultivar produces memories nobody alive claims to have lived.",
    ),
    "factions_systems_places_mechanics_or_design_pillars": (
        "memory economy",
        "orchard traversal",
        "civic trust",
        "irreversible harvest choices",
    ),
    "known_contradictions_or_worries": (
        "Memories are both survival resource and cultural record.",
        "Preserving history may require refusing the survival mechanism.",
        "Unclaimed memories may indicate ghosts, fabrication, or institutional fraud.",
    ),
    "what_roger_would_judge": (
        "Roger would judge whether the packet clarifies coherence, taste, "
        "usefulness, and whether it catches shallow or fake insight."
    ),
    "what_good_help_would_feel_like": (
        "Good help would make the central design tension clearer without "
        "inventing new lore."
    ),
}


def _input_summary() -> dict[str, Any]:
    return {
        "fixture_status": "static_fixture_seed_not_roger_provided_live_input",
        "working_title": STATIC_FIXTURE_SEED["working_title"],
        "genre_or_format": STATIC_FIXTURE_SEED["genre_or_format"],
        "what_roger_would_judge": STATIC_FIXTURE_SEED["what_roger_would_judge"],
        "what_good_help_would_feel_like": STATIC_FIXTURE_SEED[
            "what_good_help_would_feel_like"
        ],
    }


def _deterministic_structuring_step() -> dict[str, str]:
    return {
        "what_orchestrator_does": (
            "deterministically groups the fixture seed into source facts, "
            "design pillars, coherence pressures, missing material, judgment "
            "questions, and good/bad result criteria"
        ),
        "what_orchestrator_does_not_do": (
            "does not perform live creative reasoning, provider/model execution, "
            "new canon generation, product wedge selection, or Phase 387 work"
        ),
        "classification": "deterministic_structuring_not_live_creative_reasoning",
    }


def _coherence_pressures() -> tuple[dict[str, str], ...]:
    return (
        {
            "pressure": "Memory is simultaneously food, money, and history.",
            "source_basis": "memory-bearing fruit; one-use harvest; memory economy",
        },
        {
            "pressure": "Survival incentives may destroy the archive they depend on.",
            "source_basis": "eating fruit removes memories; preserving history competes with survival",
        },
        {
            "pressure": "The forbidden cultivar strains institutional trust.",
            "source_basis": "unclaimed memories; Orchard Council rationing; civic trust",
        },
    )


def _missing_or_underspecified_material() -> tuple[str, ...]:
    return (
        "Whether eaten memories transfer reliably, distort, or disappear after use.",
        "What authority the Orchard Council actually has outside rationing.",
        "Whether unclaimed memories are supernatural, fraudulent, technical, or unresolved.",
        "What the player's repeatable action loop would be beyond traversal and harvest choices.",
    )


def _roger_judgment_questions() -> tuple[str, ...]:
    return (
        "Does the packet preserve the fixture seed without inventing new canon?",
        "Does it identify the central coherence pressure Roger can judge?",
        "Does it distinguish useful structure from fake creative synthesis?",
        "Would this format help Roger evaluate a real seed later?",
        "Is the Game / Worldbuilding / Design posture clearly calibration-only?",
    )


def _good_result_bad_result_criteria() -> dict[str, tuple[str, ...]]:
    return {
        "good_result": (
            "keeps source facts separate from coherence pressures and recommendations",
            "makes the central tension easier for Roger to inspect",
            "names missing material without filling it in as new canon",
            "explains what happened in Project Manager style",
            "keeps Game / Worldbuilding / Design as a calibration domain candidate only",
        ),
        "bad_or_fake_result": (
            "sounds creative while adding unsupported lore",
            "smooths over contradictions instead of surfacing them",
            "pretends deterministic structuring is live creative reasoning",
            "implies product wedge selection or production readiness",
            "hides what would still require runtime/provider/model authorization",
        ),
    }


def _output_artifact() -> dict[str, str]:
    return {
        "artifact_name": PACKET_NAME,
        "founder_facing_summary": (
            "A compact calibration packet showing what went in, what "
            "Orchestrator did, what came out, what Roger can judge, and what "
            "remains unproven."
        ),
        "output_posture": (
            "deterministic source/test/docs fixture packet; no live creative "
            "reasoning and no new canon generated"
        ),
    }


def build_roger_legible_game_worldbuilding_design_calibration_packet_dict() -> dict[str, Any]:
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": PURPOSE,
        "input_summary": _input_summary(),
        "source_facts": list(STATIC_FIXTURE_SEED["canon_facts"]),
        "deterministic_structuring_step": _deterministic_structuring_step(),
        "output_artifact": _output_artifact(),
        "coherence_pressures": [dict(item) for item in _coherence_pressures()],
        "missing_or_underspecified_material": list(_missing_or_underspecified_material()),
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
    }


def _render_bullets(items: list[Any]) -> list[str]:
    return [f"- {item}" for item in items]


def render_roger_legible_game_worldbuilding_design_calibration_packet_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = (
        packet
        or build_roger_legible_game_worldbuilding_design_calibration_packet_dict()
    )
    input_summary = payload["input_summary"]
    structuring_step = payload["deterministic_structuring_step"]
    output_artifact = payload["output_artifact"]
    criteria = payload["good_result_bad_result_criteria"]

    sections = [
        "# Roger-Legible Game / Worldbuilding / Design Calibration Packet",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Packet: `{payload['packet_name']}`",
        f"Purpose: {payload['purpose']}",
        "",
        "## What Went In",
        f"- Fixture status: {input_summary['fixture_status']}",
        f"- Working title: {input_summary['working_title']}",
        f"- Genre or format: {input_summary['genre_or_format']}",
        f"- Roger judgment target: {input_summary['what_roger_would_judge']}",
        f"- Good help feel: {input_summary['what_good_help_would_feel_like']}",
        "",
        "## Source Facts",
        *_render_bullets(payload["source_facts"]),
        "",
        "## What Orchestrator Did",
        f"- {structuring_step['what_orchestrator_does']}",
        f"- Not performed: {structuring_step['what_orchestrator_does_not_do']}",
        f"- Classification: `{structuring_step['classification']}`",
        "",
        "## What Came Out",
        f"- Artifact: `{output_artifact['artifact_name']}`",
        f"- {output_artifact['founder_facing_summary']}",
        f"- Posture: {output_artifact['output_posture']}",
        "",
        "## Coherence Pressures",
        *[
            f"- {item['pressure']} Source basis: {item['source_basis']}"
            for item in payload["coherence_pressures"]
        ],
        "",
        "## Missing Or Underspecified Material",
        *_render_bullets(payload["missing_or_underspecified_material"]),
        "",
        "## What Roger Can Judge",
        *_render_bullets(payload["roger_judgment_questions"]),
        "",
        "## Good Result",
        *_render_bullets(criteria["good_result"]),
        "",
        "## Bad Or Fake Result",
        *_render_bullets(criteria["bad_or_fake_result"]),
        "",
        "## Open Threads",
        *_render_bullets(payload["open_threads"]),
        "",
        "## Explicit Non-Proofs",
        *_render_bullets(payload["explicit_non_proofs"]),
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
        f"- recommended_next_boundary={payload['recommended_next_boundary']}",
    ]
    return "\n".join(sections)
