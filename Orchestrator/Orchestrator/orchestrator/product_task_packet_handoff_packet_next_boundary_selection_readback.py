"""Pure handoff packet next-boundary-selection readback data."""

from __future__ import annotations

from typing import Any


PHASE = 364
NAME = "product_task_packet_handoff_packet_next_boundary_selection_readback"
BOUNDARY = "PHASE364_PRODUCT_TASK_PACKET_HANDOFF_PACKET_NEXT_BOUNDARY_SELECTION_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE364_PRODUCT_TASK_PACKET_HANDOFF_PACKET_NEXT_BOUNDARY_SELECTION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE365_PRODUCT_TASK_PACKET_HANDOFF_PACKET_READY_STATE_READBACK_SOURCE_TEST_DOCS"
)

SOURCE_BASIS = {
    "phase_349": {"boundary": "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS", "marker": "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_operator_report.py"},
    "phase_351": {"boundary": "PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS", "marker": "PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_negative_edge.py"},
    "phase_352": {"boundary": "PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS", "marker": "PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_operator_decision_readback.py"},
    "phase_354": {"boundary": "PHASE354_PRODUCT_TASK_PACKET_NEXT_SEAM_SELECTION_READBACK_SOURCE_TEST_DOCS", "marker": "PHASE354_PRODUCT_TASK_PACKET_NEXT_SEAM_SELECTION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_next_seam_selection_readback.py"},
    "phase_355": {"boundary": "PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS", "marker": "PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_lifecycle_state_readback.py"},
    "phase_356": {"boundary": "PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS", "marker": "PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_routing_contract_readback.py"},
    "phase_357": {"boundary": "PHASE357_PRODUCT_TASK_PACKET_PATCH_WORKFLOW_CONTRACT_READBACK_SOURCE_TEST_DOCS", "marker": "PHASE357_PRODUCT_TASK_PACKET_PATCH_WORKFLOW_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_patch_workflow_contract_readback.py"},
    "phase_358": {"boundary": "PHASE358_PRODUCT_TASK_PACKET_WORKER_DISPATCH_CONTRACT_READBACK_SOURCE_TEST_DOCS", "marker": "PHASE358_PRODUCT_TASK_PACKET_WORKER_DISPATCH_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_worker_dispatch_contract_readback.py"},
    "phase_359": {"boundary": "PHASE359_PRODUCT_TASK_PACKET_PROVIDER_POLICY_CONTRACT_READBACK_SOURCE_TEST_DOCS", "marker": "PHASE359_PRODUCT_TASK_PACKET_PROVIDER_POLICY_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_provider_policy_contract_readback.py"},
    "phase_360": {"boundary": "PHASE360_PRODUCT_TASK_PACKET_DOMAIN_GENERAL_INTAKE_CONTRACT_READBACK_SOURCE_TEST_DOCS", "marker": "PHASE360_PRODUCT_TASK_PACKET_DOMAIN_GENERAL_INTAKE_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_domain_general_intake_contract_readback.py"},
    "phase_361": {"boundary": "PHASE361_PRODUCT_TASK_PACKET_HANDOFF_CONTRACT_READBACK_SOURCE_TEST_DOCS", "marker": "PHASE361_PRODUCT_TASK_PACKET_HANDOFF_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_handoff_contract_readback.py"},
    "phase_362": {"boundary": "PHASE362_PRODUCT_TASK_PACKET_HANDOFF_PACKET_REVIEW_READBACK_SOURCE_TEST_DOCS", "marker": "PHASE362_PRODUCT_TASK_PACKET_HANDOFF_PACKET_REVIEW_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_handoff_packet_review_readback.py"},
    "phase_363": {"boundary": "PHASE363_PRODUCT_TASK_PACKET_HANDOFF_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS", "marker": "PHASE363_PRODUCT_TASK_PACKET_HANDOFF_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS", "source_file": "orchestrator/product_task_packet_handoff_packet_operator_decision_readback.py"},
}

COMPLETED_PACKET_SPINE = (
    "report_surface_phase_349",
    "negative_edge_contract_phase_351",
    "operator_decision_readback_phase_352",
    "next_seam_selection_readback_phase_354",
    "lifecycle_state_readback_phase_355",
    "routing_contract_readback_phase_356",
    "patch_workflow_contract_readback_phase_357",
    "worker_dispatch_contract_readback_phase_358",
    "provider_policy_contract_readback_phase_359",
    "domain_general_intake_contract_readback_phase_360",
    "handoff_contract_readback_phase_361",
    "handoff_packet_review_readback_phase_362",
    "handoff_packet_operator_decision_readback_phase_363",
)

ACCEPTED_FACTS = (
    "Phase 363 operator decision readback accepted a future-boundary recommendation posture",
    "Phase 363 recommended Phase 364 as the next bounded readback seam",
    "Git repo truth remains distinct from Source Files handoff snapshots",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

INFERENCE_AND_RECOMMENDATION = (
    "a ready-state readback is the conservative next recommendation after selection doctrine",
    "future moves require their own explicit boundary and validation",
)

CANDIDATE_BOUNDARY_CATEGORIES = (
    "review/finalization readback",
    "handoff packet issuance readback",
    "worker prompt preparation readback",
    "operator push/ref verification prep",
    "deferral/handoff-to-new-session preparation",
    "blocked/no-op selection",
)

CANDIDATE_NEXT_BOUNDARIES = (
    {
        "category": "review/finalization readback",
        "boundary": RECOMMENDED_NEXT_BOUNDARY,
        "posture": "recommended readback only, not execution",
    },
    {
        "category": "handoff packet issuance readback",
        "boundary": "FUTURE_PRODUCT_TASK_PACKET_HANDOFF_PACKET_ISSUANCE_READBACK_SOURCE_TEST_DOCS",
        "posture": "candidate only",
    },
    {
        "category": "worker prompt preparation readback",
        "boundary": "FUTURE_PRODUCT_TASK_PACKET_WORKER_PROMPT_PREPARATION_READBACK_SOURCE_TEST_DOCS",
        "posture": "candidate only",
    },
    {
        "category": "operator push/ref verification prep",
        "boundary": "FUTURE_PRODUCT_TASK_PACKET_OPERATOR_PUSH_REF_VERIFY_PREP_READBACK_SOURCE_TEST_DOCS",
        "posture": "candidate only",
    },
    {
        "category": "deferral/handoff-to-new-session preparation",
        "boundary": "FUTURE_PRODUCT_TASK_PACKET_SESSION_HANDOFF_PREPARATION_READBACK_SOURCE_TEST_DOCS",
        "posture": "candidate only",
    },
    {
        "category": "blocked/no-op selection",
        "boundary": "NO_OP_BLOCKED_SELECTION_UNTIL_EVIDENCE_SETTLED",
        "posture": "blocked candidate only",
    },
)

SELECTION_EVIDENCE_REQUIREMENTS = (
    "exact current boundary present",
    "accepted operator decision state present",
    "reviewed handoff packet status present",
    "accepted facts separated from inference",
    "source basis identified",
    "expected HEAD/origin stated",
    "remote-before state stated when push may be relevant",
    "validation evidence stated",
    "changed files or mutation status stated",
    "non-proofs preserved",
    "lockouts preserved",
    "caveats/open threads stated",
    "candidate next boundary stated",
)

VALID_SELECTION_GATES = (
    "required selection evidence present",
    "current phase settled or explicitly reported as unsettled",
    "expected Git refs clear",
    "no dirty working tree unless inside explicit mutation boundary",
    "no source/capsule/Git conflation",
    "no proof overclaim",
    "candidate boundary is explicit and bounded",
    "candidate boundary does not require forbidden runtime/provider/model/platform/live domain execution",
    "lockouts are preserved",
)

DEFER_SELECTION_GATES = (
    "context saturation requiring handoff",
    "remote-before mismatch",
    "unclear expected HEAD/origin",
    "incomplete validation evidence",
    "unresolved failed checker or brittle review harness",
    "missing caveats",
    "ambiguous candidate boundary",
    "missing source basis",
    "operator uncertainty about current state",
    "dirty working tree outside explicit mutation boundary",
)

REJECT_SELECTION_GATES = (
    "missing boundary",
    "missing operator decision state",
    "proof overclaim",
    "source/capsule/Git truth conflation",
    "worker PASS treated as coordinator ratification",
    "test PASS treated as semantic correctness",
    "pushed commit treated as production readiness",
    "Source Files snapshot treated as official capsule proof",
    "request for live/runtime/provider/model/platform/domain execution",
    "request for worker dispatch",
    "request for patch application",
    "request for provider/model execution",
    "request for Source Files refresh as proof",
    "request for capsule/export/package refresh as proof",
    "request to treat selected boundary as already executed",
)

BLOCK_SELECTION_GATES = (
    "dirty working tree not inside explicit mutation boundary",
    "remote main changed before push",
    "unexpected changed files",
    "validation failure",
    "missing marker",
    "lockout violation",
    "source/capsule/Git truth conflation",
    "request to start Phase 365 before Phase 364 is settled",
)

SELECTOR_AUTHORITY_LIMITS = (
    "next-boundary selection readback is not next-boundary execution",
    "selecting a future boundary is not worker dispatch",
    "selecting a future boundary is not handoff execution",
    "selecting a future boundary is not patch application",
    "selecting a future boundary is not provider/model execution",
    "selecting a future boundary is not route selection execution",
    "selecting a future boundary means only that a future explicitly bounded move may be prepared",
)

INVALID_SELECTION_CLAIMS = (
    "next-boundary selection means next-boundary execution occurred",
    "selected boundary means worker dispatch occurred",
    "selected boundary means handoff execution occurred",
    "selected boundary means patch application occurred",
    "selected boundary means provider/model execution occurred",
    "selected boundary means route selection execution occurred",
    "operator decision acceptance from Phase 363 means implementation correctness",
    "review acceptance from Phase 362 means implementation correctness",
    "worker PASS means coordinator ratification",
    "test PASS means semantic correctness",
    "pushed commit means production readiness",
    "Git repo truth means Source Files handoff snapshot truth",
    "handoff packet means official capsule proof",
    "Phase 364 supersedes Phase 335 capsule proof",
)

STOP_CONDITIONS = (
    "dirty working tree not inside explicit mutation boundary",
    "remote main changed before push",
    "unexpected changed files",
    "validation failure",
    "missing marker",
    "lockout violation",
    "source/capsule/Git truth conflation",
    "request to start Phase 365 before Phase 364 is settled",
    "request for live/runtime/provider/model/platform/domain execution",
    "request for worker dispatch",
    "request for patch application",
    "request for provider/model execution",
    "request for Source Files refresh as proof",
    "request for capsule/export/package refresh as proof",
)

FALSE_ACTIVITY_FLAGS = {
    "next_boundary_selected_as_live_execution": False,
    "next_boundary_executed": False,
    "handoff_executed": False,
    "handoff_packet_executed": False,
    "worker_dispatched": False,
    "patch_applied": False,
    "route_selection_executed": False,
    "provider_model_executed": False,
    "runtime_provider_model_platform_executed": False,
    "domain_general_intake_implemented": False,
    "source_files_refreshed": False,
    "capsule_export_package_refreshed": False,
    "semantic_correctness_proven": False,
    "production_readiness_proven": False,
    "official_capsule_proof_superseded_phase_335": False,
}

REQUIRED_REPORT_CAVEATS = (
    "next-boundary selection readback is not next-boundary execution",
    "selecting a future boundary is not worker dispatch",
    "selecting a future boundary is not handoff execution",
    "selecting a future boundary is not patch application",
    "selecting a future boundary is not provider/model execution",
    "selecting a future boundary is not route selection execution",
    "selecting a future boundary means only that a future explicitly bounded move may be prepared",
    "operator decision acceptance from Phase 363 is not implementation correctness",
    "review acceptance from Phase 362 is not implementation correctness",
    "worker PASS is evidence, not coordinator ratification",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "Git repo truth is distinct from Source Files handoff snapshots",
    "a handoff packet is not an official capsule",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

SOURCE_CAPSULE_GIT_TRUTH_SEPARATION = {
    "Git repo truth": "current tracked source state in the repository",
    "Source Files handoff snapshots": "handoff/source snapshots, not Git truth or official capsule proof",
    "handoff packets": "operator-legible transfer context, not official capsule proof",
    "official clean product capsule proofs": "separate clean capsule records; Phase 335 remains accepted",
    "full Git repo backups including .git": "backup artifacts, not official clean product capsules",
}

FUTURE_PHASE_ASSERTION_DOCTRINE = (
    "tests must not assert permanent absence of future phases",
    "tests may assert that the current phase did not implement the future phase",
    "future phase files may exist after a later legitimate boundary implements them",
)

LOCKOUT_TEXT = (
    "No runtime/provider/model/platform execution",
    "No WSL/Ollama/OpenClaw/Hermes/LightRAG/Discord/installer execution",
    "No service/API/UI/dashboard/auth/deployment",
    "No general_answer resumption",
    "No live task execution",
    "No live business-data access",
    "No live Obsidian/PKMS access",
    "No adapter execution",
    "No real domain execution",
    "No handoff execution",
    "No handoff packet execution",
    "No worker dispatch",
    "No patch application",
    "No route selection execution",
    "No provider/model execution",
    "No next boundary execution",
    "No Source Files refresh",
    "No capsule/export/package refresh",
    "No official capsule proof claim",
    "No cleanup/delete/archive",
    "No oz",
    "No push",
    "No Phase 365 implementation",
)


def read_product_task_packet_handoff_packet_next_boundary_selection_readback() -> dict[str, Any]:
    """Return deterministic next-boundary-selection readback data."""
    return {
        "phase": PHASE,
        "name": NAME,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_basis": dict(SOURCE_BASIS),
        "completed_packet_spine": list(COMPLETED_PACKET_SPINE),
        "next_boundary_selection_purpose": (
            "Describe and recommend the next safe bounded move after Phase 363; "
            "next-boundary selection readback is not next-boundary execution."
        ),
        "accepted_facts": list(ACCEPTED_FACTS),
        "inference_and_recommendation": list(INFERENCE_AND_RECOMMENDATION),
        "candidate_boundary_categories": list(CANDIDATE_BOUNDARY_CATEGORIES),
        "candidate_next_boundaries": [dict(candidate) for candidate in CANDIDATE_NEXT_BOUNDARIES],
        "selection_evidence_requirements": list(SELECTION_EVIDENCE_REQUIREMENTS),
        "valid_selection_gates": list(VALID_SELECTION_GATES),
        "defer_selection_gates": list(DEFER_SELECTION_GATES),
        "reject_selection_gates": list(REJECT_SELECTION_GATES),
        "block_selection_gates": list(BLOCK_SELECTION_GATES),
        "selector_authority_limits": list(SELECTOR_AUTHORITY_LIMITS),
        "invalid_selection_claims": list(INVALID_SELECTION_CLAIMS),
        "stop_conditions": list(STOP_CONDITIONS),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "required_report_caveats": list(REQUIRED_REPORT_CAVEATS),
        "source_capsule_git_truth_separation": dict(SOURCE_CAPSULE_GIT_TRUTH_SEPARATION),
        "future_phase_assertion_doctrine": list(FUTURE_PHASE_ASSERTION_DOCTRINE),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "production_readiness": False,
        "lockout_text": list(LOCKOUT_TEXT),
    }
