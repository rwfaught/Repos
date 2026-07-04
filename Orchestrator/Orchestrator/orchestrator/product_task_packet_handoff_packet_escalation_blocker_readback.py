"""Pure handoff packet escalation-blocker readback data."""

from __future__ import annotations

from typing import Any


PHASE = 373
NAME = "product_task_packet_handoff_packet_escalation_blocker_readback"
BOUNDARY = "PHASE373_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_BLOCKER_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE373_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_BLOCKER_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE374_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_RESOLUTION_READBACK_SOURCE_TEST_DOCS"
)

ACCEPTED_FACTS = (
    "Phase 372 recorded escalation evidence posture as readback only",
    "Phase 372 did not collect live evidence",
    "Escalation blocker readback is not blocker resolution",
    "Escalation blocker readback is not escalation execution",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

BLOCKER_INPUTS = (
    "missing decision input evidence",
    "missing trigger-to-decision trace",
    "ambiguous evidence source",
    "request for live business-data access",
    "request for runtime/provider/model/platform execution",
    "request for Source Files refresh",
    "request for capsule/export/package refresh",
)

BLOCKER_STATUS = {
    "status": "escalation_blocker_readback_only",
    "blockers_recorded": True,
    "blockers_resolved": False,
    "escalation_executed": False,
    "worker_dispatched": False,
    "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
}

REQUIRED_EVIDENCE = (
    "blocker reason",
    "static evidence source",
    "current git status",
    "changed-file audit when available",
    "validation output when available",
    "explicit non-proof caveats",
)

BLOCKED_ACTIONS = (
    "resolve blockers",
    "execute escalation",
    "dispatch workers",
    "apply patches outside allowlist",
    "refresh Source Files",
    "refresh capsule/export/package artifacts",
    "perform cleanup/delete/archive",
)

RECOMMENDATION_AND_INFERENCE = (
    "record blocker posture for review only",
    "treat blocker status as non-executing data",
    "require a later explicit boundary for blocker resolution",
    "preserve lockout and non-proof caveats",
    "continue only through source/test/docs readback boundaries",
)

FALSE_ACTIVITY_FLAGS = {
    "blockers_resolved": False,
    "escalation_executed": False,
    "handoff_executed": False,
    "handoff_packet_executed": False,
    "worker_dispatched": False,
    "patch_applied": False,
    "route_selection_executed": False,
    "provider_model_executed": False,
    "runtime_provider_model_platform_executed": False,
    "next_boundary_executed": False,
    "cleanup_delete_archive_performed": False,
    "source_files_refreshed": False,
    "capsule_export_package_refreshed": False,
    "semantic_correctness_proven": False,
    "production_readiness_proven": False,
}

NON_PROOF_CAVEATS = (
    "escalation blocker readback is not blocker resolution",
    "escalation blocker readback is not escalation execution",
    "escalation blocker status is not worker dispatch",
    "escalation blocker status is not handoff execution",
    "escalation blocker status is not cleanup/delete/archive",
    "escalation blocker status is not Source Files refresh",
    "escalation blocker status is not capsule/export/package refresh",
    "escalation blocker status is not route selection execution",
    "escalation blocker status is not provider/model execution",
    "escalation blocker status is not next-boundary execution",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
)

FUTURE_PHASE_ASSERTION_DOCTRINE = (
    "tests must not assert permanent absence of future phases",
    "tests may assert that the current phase did not implement the future phase",
    "future Phase 374 files may exist after a later legitimate boundary implements them",
)

LOCKOUT_TEXT = (
    "No runtime/provider/model/platform execution",
    "No escalation execution",
    "No blocker resolution",
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
    "No Phase 374 implementation",
)


def read_product_task_packet_handoff_packet_escalation_blocker_readback() -> dict[str, Any]:
    """Return deterministic handoff packet escalation-blocker readback data."""
    return {
        "phase": PHASE,
        "name": NAME,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "purpose": "Record escalation blocker posture as deterministic readback only.",
        "accepted_facts": list(ACCEPTED_FACTS),
        "blocker_inputs": list(BLOCKER_INPUTS),
        "blocker_status": dict(BLOCKER_STATUS),
        "required_evidence": list(REQUIRED_EVIDENCE),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "recommendation_and_inference": list(RECOMMENDATION_AND_INFERENCE),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "non_proof_caveats": list(NON_PROOF_CAVEATS),
        "future_phase_assertion_doctrine": list(FUTURE_PHASE_ASSERTION_DOCTRINE),
        "production_readiness": False,
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "lockout_text": list(LOCKOUT_TEXT),
    }
