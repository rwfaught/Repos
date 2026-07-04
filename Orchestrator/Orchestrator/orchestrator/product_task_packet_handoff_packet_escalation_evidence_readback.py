"""Pure handoff packet escalation-evidence readback data."""

from __future__ import annotations

from typing import Any


PHASE = 372
NAME = "product_task_packet_handoff_packet_escalation_evidence_readback"
BOUNDARY = "PHASE372_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_EVIDENCE_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE372_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_EVIDENCE_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE373_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ESCALATION_BLOCKER_READBACK_SOURCE_TEST_DOCS"
)

ACCEPTED_FACTS = (
    "Phase 371 recorded escalation decision posture as readback only",
    "Phase 371 did not execute escalation",
    "Escalation evidence readback is not evidence collection from live systems",
    "Escalation evidence readback is not escalation execution",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

EVIDENCE_INPUTS = (
    "decision input evidence",
    "trigger-to-decision trace",
    "current git status evidence",
    "changed-file audit evidence",
    "validation output when available",
    "non-proof caveat preservation",
)

EVIDENCE_STATUS = {
    "status": "escalation_evidence_readback_only",
    "evidence_recorded": True,
    "live_evidence_collected": False,
    "escalation_executed": False,
    "worker_dispatched": False,
    "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
}

BLOCKING_CONDITIONS = (
    "missing decision input evidence",
    "missing trigger-to-decision trace",
    "ambiguous evidence source",
    "request for live business-data access",
    "request for live Obsidian/PKMS access",
    "request for runtime/provider/model/platform execution",
    "request for Source Files refresh",
)

REQUIRED_EVIDENCE = (
    "static accepted facts",
    "static decision trace",
    "static validation summary",
    "static changed-file audit summary",
    "explicit non-proof caveats",
)

RECOMMENDATION_AND_INFERENCE = (
    "record escalation evidence posture for review only",
    "treat evidence status as non-executing data",
    "preserve lockout and non-proof caveats",
    "require a later explicit boundary for any live evidence gathering",
    "continue only through source/test/docs readback boundaries",
)

FALSE_ACTIVITY_FLAGS = {
    "live_evidence_collected": False,
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
    "escalation evidence readback is not escalation execution",
    "escalation evidence readback is not live evidence collection",
    "escalation evidence status is not worker dispatch",
    "escalation evidence status is not handoff execution",
    "escalation evidence status is not cleanup/delete/archive",
    "escalation evidence status is not Source Files refresh",
    "escalation evidence status is not capsule/export/package refresh",
    "escalation evidence status is not route selection execution",
    "escalation evidence status is not provider/model execution",
    "escalation evidence status is not next-boundary execution",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
)

FUTURE_PHASE_ASSERTION_DOCTRINE = (
    "tests must not assert permanent absence of future phases",
    "tests may assert that the current phase did not implement the future phase",
    "future Phase 373 files may exist after a later legitimate boundary implements them",
)

LOCKOUT_TEXT = (
    "No runtime/provider/model/platform execution",
    "No live business-data access",
    "No live Obsidian/PKMS access",
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
    "No Phase 373 implementation",
)


def read_product_task_packet_handoff_packet_escalation_evidence_readback() -> dict[str, Any]:
    """Return deterministic handoff packet escalation-evidence readback data."""
    return {
        "phase": PHASE,
        "name": NAME,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "purpose": "Record escalation evidence posture as deterministic readback only.",
        "accepted_facts": list(ACCEPTED_FACTS),
        "evidence_inputs": list(EVIDENCE_INPUTS),
        "evidence_status": dict(EVIDENCE_STATUS),
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
