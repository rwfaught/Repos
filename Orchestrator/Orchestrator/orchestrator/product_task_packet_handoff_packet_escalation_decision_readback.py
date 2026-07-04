"""Pure handoff packet escalation-decision readback data."""

from __future__ import annotations

from typing import Any


PHASE = 371
NAME = "product_task_packet_handoff_packet_escalation_decision_readback"
BOUNDARY = "PHASE371_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_DECISION_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE371_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_DECISION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE372_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_EVIDENCE_READBACK_SOURCE_TEST_DOCS"
)

ACCEPTED_FACTS = (
    "Phase 370 recorded escalation posture as readback only",
    "Phase 370 did not execute escalation",
    "Escalation decision readback is not escalation execution",
    "No worker dispatch, handoff execution, cleanup/delete/archive, Source Files refresh, or capsule/export/package refresh may occur",
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

DECISION_INPUTS = (
    "accepted trigger evidence",
    "current git status evidence",
    "changed-file allowlist audit",
    "validation evidence when available",
    "operator-facing blocker summary",
    "explicit future boundary proposal when safe",
)

ESCALATION_DECISION_STATUS = {
    "status": "escalation_decision_readback_only",
    "decision_recorded": True,
    "escalation_executed": False,
    "handoff_executed": False,
    "worker_dispatched": False,
    "cleanup_delete_archive_performed": False,
    "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
}

BLOCKING_CONDITIONS = (
    "missing accepted trigger evidence",
    "ambiguous decision target",
    "request to execute escalation",
    "request to dispatch workers",
    "request for cleanup/delete/archive",
    "request for Source Files refresh",
    "request for capsule/export/package refresh",
)

REQUIRED_EVIDENCE = (
    "decision input evidence",
    "trigger-to-decision trace",
    "current git status",
    "changed-file audit",
    "validation output when available",
    "non-proof caveat preservation",
)

RECOMMENDATION_AND_INFERENCE = (
    "record decision posture for review only",
    "treat escalation decision status as non-executing data",
    "request a later explicit execution boundary for any actual escalation",
    "preserve lockout and non-proof caveats",
    "continue only through source/test/docs readback boundaries",
)

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
    "escalation decision readback is not escalation execution",
    "escalation decision status is not worker dispatch",
    "escalation decision status is not handoff execution",
    "escalation decision status is not handoff packet execution",
    "escalation decision status is not cleanup/delete/archive",
    "escalation decision status is not Source Files refresh",
    "escalation decision status is not capsule/export/package refresh",
    "escalation decision status is not route selection execution",
    "escalation decision status is not provider/model execution",
    "escalation decision status is not next-boundary execution",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

FUTURE_PHASE_ASSERTION_DOCTRINE = (
    "tests must not assert permanent absence of future phases",
    "tests may assert that the current phase did not implement the future phase",
    "future Phase 372 files may exist after a later legitimate boundary implements them",
)

LOCKOUT_TEXT = (
    "No runtime/provider/model/platform execution",
    "No escalation execution",
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
    "No Phase 372 implementation",
)


def read_product_task_packet_handoff_packet_escalation_decision_readback() -> dict[str, Any]:
    """Return deterministic handoff packet escalation-decision readback data."""
    return {
        "phase": PHASE,
        "name": NAME,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "purpose": "Record escalation decision posture as deterministic readback only.",
        "accepted_facts": list(ACCEPTED_FACTS),
        "escalation_triggers": list(ESCALATION_TRIGGERS),
        "decision_inputs": list(DECISION_INPUTS),
        "escalation_decision_status": dict(ESCALATION_DECISION_STATUS),
        "blocking_conditions": list(BLOCKING_CONDITIONS),
        "required_evidence": list(REQUIRED_EVIDENCE),
        "recommendation_and_inference": list(RECOMMENDATION_AND_INFERENCE),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "non_proof_caveats": list(NON_PROOF_CAVEATS),
        "future_phase_assertion_doctrine": list(FUTURE_PHASE_ASSERTION_DOCTRINE),
        "production_readiness": False,
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "lockout_text": list(LOCKOUT_TEXT),
    }
