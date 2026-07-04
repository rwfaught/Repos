"""Pure handoff packet operator decision readback data for product task packets."""

from __future__ import annotations

from typing import Any


PHASE = 363
BOUNDARY = "PHASE363_PRODUCT_TASK_PACKET_HANDOFF_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE363_PRODUCT_TASK_PACKET_HANDOFF_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE364_PRODUCT_TASK_PACKET_HANDOFF_PACKET_NEXT_BOUNDARY_SELECTION_READBACK_SOURCE_TEST_DOCS"
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
)

ALLOWED_DECISION_STATES = (
    "decision_not_started",
    "decision_blocked",
    "decision_deferred",
    "decision_rejected",
    "decision_accepted_for_next_boundary",
)

DECISION_EVIDENCE_REQUIREMENTS = (
    "exact boundary present",
    "reviewed packet status present",
    "accepted facts separated from inference",
    "source basis identified",
    "expected HEAD/origin stated",
    "remote-before state stated when push may be relevant",
    "validation evidence stated",
    "changed files or mutation status stated",
    "non-proofs preserved",
    "lockouts preserved",
    "caveats/open threads stated",
    "next boundary stated",
)

PROCEED_DECISION_GATES = (
    "required packet fields present",
    "reviewed packet is structurally eligible",
    "expected Git refs are clear",
    "no dirty working tree claim unless explicitly reported",
    "no source/capsule/Git conflation",
    "no proof overclaim",
    "next boundary is explicit and bounded",
    "lockouts are preserved",
    "structural eligibility only",
    "no semantic correctness claim",
    "no production readiness claim",
)

DEFER_DECISION_GATES = (
    "context saturation requiring handoff",
    "remote-before mismatch",
    "unclear expected HEAD/origin",
    "incomplete validation evidence",
    "unresolved failed checker or brittle review harness",
    "missing caveats",
    "ambiguous next boundary",
    "missing source basis",
    "operator uncertainty about current state",
)

REJECT_DECISION_GATES = (
    "missing boundary",
    "missing reviewed packet status",
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
)

STOP_DECISION_GATES = (
    "dirty working tree not inside explicit mutation boundary",
    "remote main changed before push",
    "unexpected changed files",
    "validation failure",
    "missing marker",
    "lockout violation",
    "source/capsule/Git truth conflation",
    "request to start Phase 364 before Phase 363 is settled",
)

OPERATOR_AUTHORITY_LIMITS = (
    "operator decision readback is not handoff execution",
    "decision accepted for next boundary is not worker dispatch",
    "decision accepted for next boundary is not patch application",
    "decision accepted for next boundary is not provider/model execution",
    "decision accepted for next boundary is not route selection execution",
    "decision accepted for next boundary means only that a future explicitly bounded move may be prepared",
    "decision state vocabulary does not transition live state",
)

COORDINATOR_AUTHORITY_LIMITS = (
    "review acceptance from Phase 362 is not implementation correctness",
    "worker PASS is evidence, not coordinator ratification",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "coordinator ratification requires a separate explicit boundary when requested",
)

INVALID_DECISION_CLAIMS = (
    "operator decision readback means handoff execution occurred",
    "decision accepted for next boundary means worker dispatch occurred",
    "decision accepted for next boundary means patch application occurred",
    "decision accepted for next boundary means provider/model execution occurred",
    "decision accepted for next boundary means route selection execution occurred",
    "decision accepted for next boundary means production readiness",
    "review acceptance means implementation correctness",
    "worker PASS means coordinator ratification",
    "test PASS means semantic correctness",
    "pushed commit means production readiness",
    "Git repo truth means Source Files handoff snapshot truth",
    "Source Files snapshot means official capsule proof",
    "handoff packet means official capsule proof",
    "Phase 363 supersedes Phase 335 capsule proof",
)

STOP_CONDITIONS = (
    "dirty working tree not inside explicit mutation boundary",
    "remote main changed before push",
    "unexpected changed files",
    "validation failure",
    "missing marker",
    "lockout violation",
    "source/capsule/Git truth conflation",
    "request to start Phase 364 before Phase 363 is settled",
    "request for live/runtime/provider/model/platform/domain execution",
    "request for worker dispatch",
    "request for patch application",
    "request for provider/model execution",
    "request for Source Files refresh as proof",
    "request for capsule/export/package refresh as proof",
)

FALSE_ACTIVITY_FLAGS = {
    "operator_decision_executed_as_live_action": False,
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
    "operator decision readback is not handoff execution",
    "decision accepted for next boundary is not worker dispatch",
    "decision accepted for next boundary is not patch application",
    "decision accepted for next boundary is not provider/model execution",
    "decision accepted for next boundary is not route selection execution",
    "decision accepted for next boundary means only that a future explicitly bounded move may be prepared",
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

LOCKOUT_TEXT = (
    "No runtime/provider/model/platform execution",
    "No WSL/Ollama/OpenClaw/Hermes/LightRAG/Discord/installer execution",
    "No service/API/UI/dashboard/auth/deployment",
    "No general_answer resumption",
    "No live task execution",
    "No live mutation beyond allowed source/test/docs files",
    "No live business-data access",
    "No live Obsidian/PKMS access",
    "No adapter execution",
    "No real domain execution",
    "No worker dispatch",
    "No handoff execution",
    "No handoff packet execution",
    "No patch application",
    "No route selection execution",
    "No provider/model execution",
    "No Source Files refresh",
    "No capsule/export/package refresh",
    "No official capsule proof claim",
    "No cleanup/delete/archive",
    "No oz",
    "No broad mutation",
    "No Phase 364 implementation",
)


def read_product_task_packet_handoff_packet_operator_decision_readback() -> dict[str, Any]:
    """Return deterministic handoff packet operator decision readback data."""
    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_basis": dict(SOURCE_BASIS),
        "completed_packet_spine": list(COMPLETED_PACKET_SPINE),
        "decision_contract_purpose": (
            "Define operator/coordinator decision doctrine after handoff packet review only; "
            "operator decision readback is not handoff execution."
        ),
        "allowed_decision_states": list(ALLOWED_DECISION_STATES),
        "decision_evidence_requirements": list(DECISION_EVIDENCE_REQUIREMENTS),
        "proceed_decision_gates": list(PROCEED_DECISION_GATES),
        "defer_decision_gates": list(DEFER_DECISION_GATES),
        "reject_decision_gates": list(REJECT_DECISION_GATES),
        "stop_decision_gates": list(STOP_DECISION_GATES),
        "operator_authority_limits": list(OPERATOR_AUTHORITY_LIMITS),
        "coordinator_authority_limits": list(COORDINATOR_AUTHORITY_LIMITS),
        "invalid_decision_claims": list(INVALID_DECISION_CLAIMS),
        "stop_conditions": list(STOP_CONDITIONS),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "required_report_caveats": list(REQUIRED_REPORT_CAVEATS),
        "source_capsule_git_truth_separation": dict(SOURCE_CAPSULE_GIT_TRUTH_SEPARATION),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "lockout_text": list(LOCKOUT_TEXT),
    }
