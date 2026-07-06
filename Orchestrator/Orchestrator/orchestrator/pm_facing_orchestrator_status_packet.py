from __future__ import annotations

from typing import Any

from orchestrator.dry_mvp_loop_closeout_review import (
    build_dry_mvp_loop_closeout_review_dict,
)


BOUNDARY = "PM_FACING_ORCHESTRATOR_STATUS_PACKET_SOURCE_TEST_DOCS"
PACKET_NAME = "pm_facing_orchestrator_status_packet"
RECOMMENDED_NEXT_BOUNDARY = "DRY_MVP_INTEGRATED_ACCEPTANCE_SOURCE_TEST_DOCS"

EXPLICIT_NON_PROOFS = (
    "no runtime/provider/model execution",
    "no live coordinator reasoning proof",
    "no autonomous task dispatch proof",
    "no real worker execution proof",
    "no local model capability proof",
    "no frontier model escalation proof",
    "no semantic correctness proof",
    "no production readiness proof",
    "no file mutation execution proof",
    "no Phase 387 implementation",
    "no first product wedge selection",
)


def build_pm_facing_orchestrator_status_packet_dict(
    closeout_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    closeout = closeout_review or build_dry_mvp_loop_closeout_review_dict()
    can_do = (
        "Preserve a broad operator goal as structured intake.",
        "Surface missing inputs and risk before doing work.",
        "Propose one bounded task packet.",
        "Require Roger approval before creating a queued task.",
        "Create a queued report-only task record in a caller-supplied task store.",
        "Review that queued task before any execution boundary.",
        "Create a deterministic dry worker-result artifact in a caller-supplied artifact store.",
        "Review the dry result and expose operator response options.",
    )
    cannot_do = (
        "It cannot yet run a real local worker in this new dry MVP spine.",
        "It cannot yet call a local model or frontier provider in this spine.",
        "It cannot yet mutate project files from this spine.",
        "It cannot yet prove semantic correctness or product usefulness.",
        "It cannot yet run unattended multi-step production work.",
    )
    return {
        "packet_name": PACKET_NAME,
        "boundary": BOUNDARY,
        "purpose": "Give Roger a compact PM-facing readout of current Orchestrator capability after the dry MVP loop.",
        "source_closeout_decision": str(closeout.get("closeout_decision", "")),
        "overall_status": (
            "dry_mvp_loop_structurally_present"
            if closeout.get("closeout_decision") == "dry_mvp_loop_closeout_pass"
            else "dry_mvp_loop_not_yet_closed"
        ),
        "what_orchestrator_can_do_now": list(can_do),
        "what_orchestrator_cannot_do_yet": list(cannot_do),
        "practical_pm_assessment": (
            "Orchestrator now has a deterministic, inspectable dry loop from broad goal to reviewed dry artifact. "
            "This is not live autonomy, but it is a credible skeleton for the intended product."
        ),
        "recommended_next_moves": (
            "Run the integrated dry MVP acceptance packet.",
            "Run a commit-ready verification pass after acceptance.",
            "Ask Roger before any real local-worker, model, provider, or mutation boundary.",
        ),
        "explicit_non_proofs": list(EXPLICIT_NON_PROOFS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "first_product_wedge_selected": False,
        "phase_387_implemented": False,
        "runtime_required": False,
        "provider_model_required": False,
        "worker_dispatched": False,
        "real_worker_executed": False,
        "mutation_authorized": False,
        "production_readiness_claimed": False,
    }


def render_pm_facing_orchestrator_status_packet_markdown(
    packet: dict[str, Any] | None = None,
) -> str:
    payload = packet or build_pm_facing_orchestrator_status_packet_dict()
    lines = [
        "# PM-Facing Orchestrator Status Packet",
        "",
        f"Boundary: `{payload['boundary']}`",
        f"Status: `{payload['overall_status']}`",
        "",
        "## Practical PM Assessment",
        payload["practical_pm_assessment"],
        "",
        "## What Orchestrator Can Do Now",
        *[f"- {item}" for item in payload["what_orchestrator_can_do_now"]],
        "",
        "## What Orchestrator Cannot Do Yet",
        *[f"- {item}" for item in payload["what_orchestrator_cannot_do_yet"]],
        "",
        "## Recommended Next Moves",
        *[f"- {item}" for item in payload["recommended_next_moves"]],
        "",
        "## Explicit Non-Proofs",
        *[f"- {item}" for item in payload["explicit_non_proofs"]],
        "",
        "## Posture",
        f"- first_product_wedge_selected={payload['first_product_wedge_selected']}",
        f"- phase_387_implemented={payload['phase_387_implemented']}",
        f"- worker_dispatched={payload['worker_dispatched']}",
        f"- real_worker_executed={payload['real_worker_executed']}",
        f"- mutation_authorized={payload['mutation_authorized']}",
        f"- recommended_next_boundary={payload['recommended_next_boundary']}",
    ]
    return "\n".join(lines)
