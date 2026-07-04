"""Pure handoff packet execution-precondition readback data."""

from __future__ import annotations

from typing import Any


PHASE = 367
NAME = "product_task_packet_handoff_packet_execution_precondition_readback"
BOUNDARY = "PHASE367_PRODUCT_TASK_PACKET_HANDOFF_PACKET_EXECUTION_PRECONDITION_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE367_PRODUCT_TASK_PACKET_HANDOFF_PACKET_EXECUTION_PRECONDITION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE368_PRODUCT_TASK_PACKET_HANDOFF_PACKET_OPERATOR_APPROVAL_READBACK_SOURCE_TEST_DOCS"
)

ACCEPTED_FACTS = (
    "Phase 366 reviewed execution authority as readback only",
    "Phase 366 did not grant execution authority",
    "Execution authority is not execution",
    "Git repo truth remains distinct from Source Files handoff snapshots",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

REQUIRED_PRECONDITIONS = (
    "explicit later execution boundary",
    "fresh working tree and ref verification",
    "operator approval when required",
    "allowed operation scope for the later boundary",
    "validation plan for the later boundary",
    "non-proof caveats preserved",
)

MISSING_PRECONDITIONS = (
    "no later execution boundary exists in Phase 367",
    "no handoff packet execution authority is granted by Phase 367",
    "no operator approval action is performed by Phase 367",
    "no runtime/provider/model/platform evidence is created by Phase 367",
)

PRECONDITION_INFERENCE_AND_RECOMMENDATION = (
    "execution preconditions are represented for review only",
    "missing preconditions block execution unless a later explicit boundary resolves them",
    "execution authority may be a precondition but is not execution",
    "no packet may be treated as executable in Phase 367",
)

BLOCKING_CONDITIONS = (
    "missing explicit later execution boundary",
    "missing allowed operation scope",
    "missing operator approval where required",
    "missing validation plan",
    "dirty working tree outside explicit mutation boundary",
    "unexpected changed files",
    "lockout violation",
    "proof overclaim",
    "request to treat execution authority as execution",
)

REQUIRED_EVIDENCE_BEFORE_FUTURE_EXECUTION = (
    "new explicit execution boundary",
    "fresh preflight evidence",
    "authorization evidence when required",
    "operation allowlist",
    "validation evidence",
    "explicit non-proof preservation",
)

PRECONDITION_STATUS = {
    "status": "execution_preconditions_missing_readback_only",
    "execution_authority_is_execution": False,
    "execution_precondition_readback_is_execution": False,
    "packet_executable_now": False,
    "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
}

FALSE_ACTIVITY_FLAGS = {
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
    "execution_authority_granted": False,
    "semantic_correctness_proven": False,
    "production_readiness_proven": False,
}

NON_PROOF_CAVEATS = (
    "execution authority is not execution",
    "execution precondition readback is not execution",
    "execution precondition readback is not handoff execution",
    "execution precondition readback is not handoff packet execution",
    "execution precondition readback is not worker dispatch",
    "execution precondition readback is not patch application",
    "execution precondition readback is not route selection execution",
    "execution precondition readback is not provider/model execution",
    "execution precondition readback is not next-boundary execution",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "Git repo truth is distinct from Source Files handoff snapshots",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

FUTURE_PHASE_ASSERTION_DOCTRINE = (
    "tests must not assert permanent absence of future phases",
    "tests may assert that the current phase did not implement the future phase",
    "future Phase 368 files may exist after a later legitimate boundary implements them",
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
    "No Phase 368 implementation",
)


def read_product_task_packet_handoff_packet_execution_precondition_readback() -> dict[str, Any]:
    """Return deterministic handoff packet execution-precondition readback data."""
    return {
        "phase": PHASE,
        "name": NAME,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "purpose": "Record execution preconditions as deterministic readback only.",
        "accepted_facts": list(ACCEPTED_FACTS),
        "required_preconditions": list(REQUIRED_PRECONDITIONS),
        "missing_preconditions": list(MISSING_PRECONDITIONS),
        "precondition_inference_and_recommendation": list(PRECONDITION_INFERENCE_AND_RECOMMENDATION),
        "blocking_conditions": list(BLOCKING_CONDITIONS),
        "required_evidence_before_future_execution": list(REQUIRED_EVIDENCE_BEFORE_FUTURE_EXECUTION),
        "precondition_status": dict(PRECONDITION_STATUS),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "non_proof_caveats": list(NON_PROOF_CAVEATS),
        "future_phase_assertion_doctrine": list(FUTURE_PHASE_ASSERTION_DOCTRINE),
        "production_readiness": False,
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "lockout_text": list(LOCKOUT_TEXT),
    }
