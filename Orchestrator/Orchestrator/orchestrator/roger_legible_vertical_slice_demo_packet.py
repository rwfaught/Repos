from __future__ import annotations

from typing import Any

from orchestrator.founder_native_setting_causal_court_micro_scenario import (
    build_causal_court_micro_scenario_dict,
)


BOUNDARY = "ROGER_LEGIBLE_VERTICAL_SLICE_DEMO_PACKET_SOURCE_TEST_DOCS"
PACKET_NAME = "roger_legible_human_override_causal_court_vertical_slice_demo_packet"
RECOMMENDED_NEXT_BOUNDARY = "ROGER_LEGIBLE_VERTICAL_SLICE_DEMO_PACKET_REVIEW_READONLY"

EXPLICIT_NON_PROOFS = (
    "no runtime/provider/model proof",
    "no semantic correctness proof",
    "no production readiness proof",
    "no Phase 387 implementation",
    "no first product wedge selection",
    "no Game / Worldbuilding / Design wedge selection",
    "no claims/disputes/appeals wedge selection",
    "no Source Files refresh/export/capsule proof",
)

PURPOSE = (
    "Give Roger a compact milestone demo surface showing what went in, what "
    "Orchestrator did, what came out, what was verified, what Roger can judge, "
    "and what remains unproven."
)


def _demo_input(micro_scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_material": (
            "Existing deterministic Human Override / Causal Court material, "
            "centered on one Causal Court micro-scenario."
        ),
        "setting": micro_scenario["setting_title"],
        "case_title": micro_scenario["case_title"],
        "case_type": micro_scenario["case_type"],
        "source_contradiction_area": micro_scenario["source_contradiction_area"],
        "infrastructure_domain": micro_scenario["infrastructure_domain"],
        "source_boundary": micro_scenario["boundary"],
    }


def _orchestration_step() -> dict[str, Any]:
    return {
        "what_orchestrator_does": (
            "deterministic structuring, readback, and packetization of existing "
            "source/test/docs material into a compact founder-facing demo packet"
        ),
        "what_orchestrator_does_not_do": (
            "live autonomous reasoning, provider/model execution, product wedge "
            "selection, production task execution, or Phase 387 implementation"
        ),
        "classification": "deterministic_packetization_not_live_reasoning",
    }


def _output_artifact(micro_scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_name": PACKET_NAME,
        "founder_facing_summary": (
            "A compact demo packet showing what went in, what Orchestrator did, "
            "what came out, what was checked, what Roger can judge, and what "
            "remains unproven."
        ),
        "visible_case": micro_scenario["case_title"],
        "visible_output_focus": (
            "The Six-Minute New Jakarta Fusion-Grid Override is used as support "
            "material to make the milestone legible, not as the current product "
            "direction."
        ),
        "judgment_surface": (
            "Roger can judge whether this packet clarifies capability, coherence, "
            "and milestone meaning without reading the full governance trail."
        ),
    }


def _verification() -> tuple[str, ...]:
    return (
        "focused tests assert packet dictionary shape and exact boundary",
        "focused tests assert required demo sections are present",
        "focused tests assert deterministic packetization is separated from live reasoning",
        "focused tests assert false flags remain false",
        "focused tests assert non-proofs and open threads are preserved",
        "py_compile checks the source modules for syntax validity",
        "git diff --check checks whitespace safety",
    )


def _founder_judgment_questions() -> tuple[str, ...]:
    return (
        "Does this help me understand what Orchestrator did?",
        "Is the output coherent enough to judge?",
        "Does this reveal capability or just documentation?",
        "Would a Game / Worldbuilding / Design calibration slice be easier for me to evaluate next?",
        "Does the packet make the non-proofs visible enough before any live provider/model work?",
    )


def _open_threads() -> tuple[str, ...]:
    return (
        "Game / Worldbuilding / Design remains a Roger-legible calibration domain candidate, not a selected first product wedge.",
        "Human Override / Causal Court remains useful principle and supporting material, not current product direction.",
        "A future live or semi-live vertical slice is still needed when runtime/provider/model execution is authorized.",
        "Every demo result still needs Project Manager style explanation: what went in, what happened, what came out, what was verified, what Roger can judge, and what is not proven.",
    )


def build_roger_legible_vertical_slice_demo_packet_dict() -> dict[str, Any]:
    micro_scenario = build_causal_court_micro_scenario_dict()

    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": PURPOSE,
        "input": _demo_input(micro_scenario),
        "orchestration_step": _orchestration_step(),
        "output_artifact": _output_artifact(micro_scenario),
        "verification": list(_verification()),
        "founder_judgment_questions": list(_founder_judgment_questions()),
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "open_threads": list(_open_threads()),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "first_product_wedge_selected": False,
        "phase_387_implemented": False,
        "runtime_required": False,
        "provider_model_required": False,
        "game_worldbuilding_design_wedge_selected": False,
        "claims_disputes_appeals_wedge_selected": False,
    }


def _render_bullets(items: list[Any]) -> list[str]:
    return [f"- {item}" for item in items]


def render_roger_legible_vertical_slice_demo_packet_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = packet or build_roger_legible_vertical_slice_demo_packet_dict()
    demo_input = payload["input"]
    orchestration_step = payload["orchestration_step"]
    output_artifact = payload["output_artifact"]

    sections = [
        "# Roger-Legible Vertical Slice Demo Packet",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Packet: `{payload['packet_name']}`",
        f"Purpose: {payload['purpose']}",
        "",
        "## What Went In",
        f"- Source material: {demo_input['source_material']}",
        f"- Setting: {demo_input['setting']}",
        f"- Case: {demo_input['case_title']}",
        f"- Contradiction area: {demo_input['source_contradiction_area']}",
        "",
        "## What Orchestrator Did",
        f"- {orchestration_step['what_orchestrator_does']}",
        f"- Not performed: {orchestration_step['what_orchestrator_does_not_do']}",
        f"- Classification: `{orchestration_step['classification']}`",
        "",
        "## What Came Out",
        f"- Artifact: `{output_artifact['artifact_name']}`",
        f"- {output_artifact['founder_facing_summary']}",
        f"- Visible case: {output_artifact['visible_case']}",
        f"- {output_artifact['visible_output_focus']}",
        "",
        "## Verification",
        *_render_bullets(payload["verification"]),
        "",
        "## What Roger Can Judge",
        *_render_bullets(payload["founder_judgment_questions"]),
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
        f"- recommended_next_boundary={payload['recommended_next_boundary']}",
    ]
    return "\n".join(sections)
