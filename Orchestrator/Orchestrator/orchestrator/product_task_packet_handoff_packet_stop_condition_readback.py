"""Pure handoff packet stop-condition readback data."""

from __future__ import annotations

from typing import Any


PHASE = 369
NAME = "product_task_packet_handoff_packet_stop_condition_readback"
BOUNDARY = "PHASE369_PRODUCT_TASK_PACKET_HANDOFF_PACKET_STOP_CONDITION_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE369_PRODUCT_TASK_PACKET_HANDOFF_PACKET_STOP_CONDITION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
RECOMMENDED_NEXT_BOUNDARY = "PHASE370_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_READBACK_SOURCE_TEST_DOCS"

ACCEPTED_FACTS = (
    "Phase 368 recorded operator approval posture as readback only",
    "Phase 368 did not perform operator action",
    "Stop-condition readback may recommend stopping but does not execute a stop",
    "Cleanup/delete/archive is locked out",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

STOP_TRIGGERS = (
    "failed precheck",
    "failed validation",
    "unexpected changed file",
    "stale future-file absence assertion",
    "ambiguous next boundary",
    "request for runtime/provider/model/platform execution",
    "request for handoff packet execution",
    "request for cleanup/delete/archive",
    "proof overclaim",
)

BLOCKING_CONDITIONS = (
    "stop trigger present",
    "needed repair outside current allowlist",
    "operator approval missing where required",
    "execution boundary missing",
    "dirty working tree outside explicit mutation boundary",
    "lockout violation",
)

REQUIRED_ESCALATION = (
    "report the stop trigger",
    "preserve changed-file evidence",
    "do not execute cleanup/delete/archive",
    "do not dispatch workers",
    "recommend a later explicit boundary if one is safe and unambiguous",
)

STOP_RECOMMENDATION = {
    "status": "stop_conditions_recorded_readback_only",
    "stop_executed": False,
    "cleanup_delete_archive_performed": False,
    "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
}

FALSE_ACTIVITY_FLAGS = {
    "stop_executed": False,
    "cleanup_delete_archive_performed": False,
    "handoff_executed": False,
    "handoff_packet_executed": False,
    "worker_dispatched": False,
    "patch_applied": False,
    "route_selection_executed": False,
    "provider_model_executed": False,
    "runtime_provider_model_platform_executed": False,
    "next_boundary_executed": False,
    "source_files_refreshed": False,
    "capsule_export_package_refreshed": False,
    "semantic_correctness_proven": False,
    "production_readiness_proven": False,
}

NON_PROOF_CAVEATS = (
    "stop-condition readback is not stop execution",
    "stop-condition readback is not cleanup/delete/archive",
    "stop-condition readback is not handoff execution",
    "stop-condition readback is not handoff packet execution",
    "stop-condition readback is not worker dispatch",
    "stop-condition readback is not patch application",
    "stop-condition readback is not route selection execution",
    "stop-condition readback is not provider/model execution",
    "stop-condition readback is not next-boundary execution",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

FUTURE_PHASE_ASSERTION_DOCTRINE = (
    "tests must not assert permanent absence of future phases",
    "tests may assert that the current phase did not implement the future phase",
    "future Phase 370 files may exist after a later legitimate boundary implements them",
)

LOCKOUT_TEXT = (
    "No runtime/provider/model/platform execution",
    "No handoff execution",
    "No handoff packet execution",
    "No worker dispatch",
    "No patch application",
    "No route selection execution",
    "No provider/model execution",
    "No next-boundary execution",
    "No Source Files refresh",
    "No capsule/export/package refresh",
    "No cleanup/delete/archive",
    "No push",
    "No Phase 370 implementation",
)


def read_product_task_packet_handoff_packet_stop_condition_readback() -> dict[str, Any]:
    """Return deterministic handoff packet stop-condition readback data."""
    return {
        "phase": PHASE,
        "name": NAME,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "purpose": "Record stop conditions as deterministic readback only.",
        "accepted_facts": list(ACCEPTED_FACTS),
        "stop_triggers": list(STOP_TRIGGERS),
        "blocking_conditions": list(BLOCKING_CONDITIONS),
        "required_escalation": list(REQUIRED_ESCALATION),
        "stop_recommendation": dict(STOP_RECOMMENDATION),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "non_proof_caveats": list(NON_PROOF_CAVEATS),
        "future_phase_assertion_doctrine": list(FUTURE_PHASE_ASSERTION_DOCTRINE),
        "production_readiness": False,
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "lockout_text": list(LOCKOUT_TEXT),
    }
