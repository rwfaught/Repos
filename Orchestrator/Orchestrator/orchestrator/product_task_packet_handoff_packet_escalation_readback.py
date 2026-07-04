"""Pure handoff packet escalation readback data."""

from __future__ import annotations

from typing import Any


PHASE = 370
NAME = "product_task_packet_handoff_packet_escalation_readback"
BOUNDARY = "PHASE370_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE370_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE371_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_DECISION_READBACK_SOURCE_TEST_DOCS"
)

ACCEPTED_FACTS = (
    "Phase 369 recorded stop conditions as readback only",
    "Phase 369 did not execute a stop",
    "Escalation readback is not escalation execution",
    "No worker dispatch, route execution, cleanup/delete/archive, Source Files refresh, or capsule/export/package refresh may occur",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

ESCALATION_TRIGGERS = (
    "failed precheck",
    "failed validation",
    "unexpected changed file",
    "ambiguous next boundary",
    "needed repair outside current allowlist",
    "operator approval required",
    "lockout violation",
    "proof overclaim",
)

ESCALATION_RECOMMENDATIONS = (
    "report blocker with evidence",
    "request a later explicit boundary",
    "preserve non-proof caveats",
    "do not execute escalation",
    "do not dispatch workers",
)

REQUIRED_EVIDENCE = (
    "trigger evidence",
    "current git status",
    "changed-file audit",
    "validation output when available",
    "explicit next-boundary proposal when unambiguous",
)

BLOCKED_ESCALATION_CONDITIONS = (
    "missing trigger evidence",
    "ambiguous escalation target",
    "request to execute escalation",
    "request to dispatch workers",
    "request for cleanup/delete/archive",
    "request for Source Files refresh",
    "request for capsule/export/package refresh",
)

ESCALATION_STATUS = {
    "status": "escalation_recommendation_readback_only",
    "escalation_executed": False,
    "worker_dispatched": False,
    "cleanup_delete_archive_performed": False,
    "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
}

FALSE_ACTIVITY_FLAGS = {
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
    "escalation readback is not escalation execution",
    "escalation readback is not handoff execution",
    "escalation readback is not handoff packet execution",
    "escalation readback is not worker dispatch",
    "escalation readback is not patch application",
    "escalation readback is not route selection execution",
    "escalation readback is not provider/model execution",
    "escalation readback is not next-boundary execution",
    "escalation readback is not cleanup/delete/archive",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

FUTURE_PHASE_ASSERTION_DOCTRINE = (
    "tests must not assert permanent absence of future phases",
    "tests may assert that the current phase did not implement the future phase",
    "future Phase 371 files may exist after a later legitimate boundary implements them",
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
    "No Phase 371 implementation",
)


def read_product_task_packet_handoff_packet_escalation_readback() -> dict[str, Any]:
    """Return deterministic handoff packet escalation readback data."""
    return {
        "phase": PHASE,
        "name": NAME,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "purpose": "Record escalation posture as deterministic readback only.",
        "accepted_facts": list(ACCEPTED_FACTS),
        "escalation_triggers": list(ESCALATION_TRIGGERS),
        "escalation_recommendations": list(ESCALATION_RECOMMENDATIONS),
        "required_evidence": list(REQUIRED_EVIDENCE),
        "blocked_escalation_conditions": list(BLOCKED_ESCALATION_CONDITIONS),
        "escalation_status": dict(ESCALATION_STATUS),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "non_proof_caveats": list(NON_PROOF_CAVEATS),
        "future_phase_assertion_doctrine": list(FUTURE_PHASE_ASSERTION_DOCTRINE),
        "production_readiness": False,
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "lockout_text": list(LOCKOUT_TEXT),
    }
