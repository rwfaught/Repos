"""Pure handoff packet review readback data for product task packets."""

from __future__ import annotations

from typing import Any


PHASE = 362
BOUNDARY = "PHASE362_PRODUCT_TASK_PACKET_HANDOFF_PACKET_REVIEW_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE362_PRODUCT_TASK_PACKET_HANDOFF_PACKET_REVIEW_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE363_PRODUCT_TASK_PACKET_HANDOFF_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS"
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
)

HANDOFF_PACKET_PREREQUISITES = (
    "exact boundary present",
    "role/context present",
    "repo path present",
    "expected Git refs present",
    "accepted facts separated from inference",
    "source basis identified",
    "changed files or mutation status identified",
    "validation status identified",
    "non-proofs preserved",
    "lockouts preserved",
    "next boundary stated",
    "caveats/open threads stated",
)

REQUIRED_HANDOFF_PACKET_FIELDS = (
    "boundary",
    "role_context",
    "repo_path",
    "expected_head",
    "expected_origin_main",
    "accepted_facts",
    "inference",
    "source_basis",
    "changed_files_or_mutation_status",
    "validation_status",
    "non_proofs",
    "lockouts",
    "next_boundary",
    "caveats_or_open_threads",
)

REVIEW_EVIDENCE_DOCTRINE = (
    "review evidence is structural packet evidence only",
    "accepted facts must remain separate from inference",
    "worker PASS is evidence, not coordinator ratification",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "handoff packet is not Source Files refresh",
    "handoff packet is not an official capsule",
    "Git repo truth is distinct from Source Files handoff snapshots",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

REVIEW_STATUS_VOCABULARY = (
    "review_not_started",
    "review_blocked",
    "review_deferred",
    "review_accepted_for_next_boundary",
    "review_rejected",
)

REVIEW_ACCEPTANCE_GATES = (
    "required packet fields present",
    "review acceptance is structural eligibility only",
    "future explicitly bounded next move stated",
    "no dirty working tree claim unless explicitly reported as such",
    "remote-before truth preserved",
    "no source/capsule/Git conflation",
    "no runtime/provider/model/platform execution claim",
    "no worker dispatch claim",
    "no patch application claim",
    "no semantic correctness claim",
    "no production readiness claim",
    "no Source Files refresh claim",
    "no official capsule proof claim beyond Phase 335",
)

REVIEW_REJECTION_GATES = (
    "missing boundary",
    "missing role/context",
    "missing source basis",
    "missing validation status",
    "proof overclaim",
    "source/capsule/Git truth conflation",
    "worker PASS treated as coordinator ratification",
    "test PASS treated as semantic correctness",
    "pushed commit treated as production readiness",
    "Source Files snapshot treated as official capsule proof",
    "request for live/runtime/provider/model/platform/domain execution",
    "request for worker dispatch",
    "request for patch application",
)

REVIEW_DEFERRAL_GATES = (
    "context saturation requiring handoff",
    "remote-before mismatch",
    "unclear expected HEAD/origin",
    "incomplete validation evidence",
    "unresolved prior failed checker or brittle review harness",
    "missing caveats",
    "ambiguous next boundary",
)

REVIEWER_AUTHORITY_LIMITS = (
    "handoff packet review readback is not handoff execution",
    "review eligibility is not worker dispatch",
    "review acceptance is not coordinator ratification of implementation correctness",
    "review acceptance only means the packet is structurally eligible for a future explicitly bounded next move",
    "review status vocabulary does not transition live state",
    "review readback does not implement Phase 363",
)

INVALID_REVIEW_CLAIMS = (
    "review readback means handoff execution occurred",
    "review eligibility means worker dispatch occurred",
    "review acceptance means implementation correctness was ratified",
    "review acceptance means semantic correctness",
    "review acceptance means production readiness",
    "handoff packet means Source Files refresh",
    "handoff packet means official capsule proof",
    "worker PASS means coordinator ratification",
    "test PASS means semantic correctness",
    "pushed commit means production readiness",
    "Git repo truth means Source Files handoff snapshot truth",
    "Phase 362 supersedes Phase 335 capsule proof",
)

STOP_CONDITIONS = (
    "missing boundary",
    "missing role/context",
    "missing source basis",
    "missing validation status",
    "proof overclaim",
    "source/capsule/Git truth conflation",
    "dirty working tree claim ambiguity",
    "remote-before mismatch",
    "context saturation requiring handoff",
    "live/runtime/provider/model/platform/domain execution request",
    "worker dispatch request",
    "patch application request",
    "Source Files refresh request",
    "official capsule proof claim beyond Phase 335",
)

FALSE_ACTIVITY_FLAGS = {
    "handoff_executed": False,
    "handoff_packet_review_executed_as_live_action": False,
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
    "readback is not execution",
    "handoff packet review readback is not handoff execution",
    "review eligibility is not worker dispatch",
    "review acceptance is not coordinator ratification of implementation correctness",
    "review acceptance only means structural eligibility for a future explicitly bounded next move",
    "handoff packet is not a Source Files refresh",
    "handoff packet is not an official capsule",
    "worker PASS is evidence, not coordinator ratification",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "Git repo truth is distinct from Source Files handoff snapshots",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

SOURCE_CAPSULE_GIT_TRUTH_SEPARATION = {
    "Git repo truth": "current tracked source state in the repository",
    "Source Files handoff snapshots": "handoff/source snapshots, not Git truth or official capsule proof",
    "handoff packets": "operator-legible transfer context, not Source Files refresh or official capsule proof",
    "official clean product capsule proofs": "separate clean capsule records; Phase 335 remains accepted",
    "full Git repo backups including .git": "backup artifacts, not official clean product capsules",
}

LOCKOUT_TEXT = (
    "No runtime/provider/model/platform execution",
    "No service/API/UI/dashboard/auth/deployment",
    "No general_answer",
    "No live task execution",
    "No live mutation beyond allowed source/test/docs files",
    "No live business-data access",
    "No live Obsidian/PKMS access",
    "No adapter execution",
    "No real domain execution",
    "No worker dispatch",
    "No handoff execution",
    "No patch application",
    "No route selection execution",
    "No provider/model execution",
    "No Source Files refresh",
    "No capsule/export/package refresh",
    "No official capsule proof claim",
    "No semantic correctness",
    "No production readiness",
    "No Phase 363 implementation",
)


def read_product_task_packet_handoff_packet_review_readback() -> dict[str, Any]:
    """Return deterministic handoff packet review readback data."""
    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_basis": dict(SOURCE_BASIS),
        "completed_packet_spine": list(COMPLETED_PACKET_SPINE),
        "review_contract_purpose": (
            "Define product task packet handoff packet review doctrine only; "
            "handoff packet review readback is not handoff execution."
        ),
        "handoff_packet_prerequisites": list(HANDOFF_PACKET_PREREQUISITES),
        "required_handoff_packet_fields": list(REQUIRED_HANDOFF_PACKET_FIELDS),
        "review_evidence_doctrine": list(REVIEW_EVIDENCE_DOCTRINE),
        "review_status_vocabulary": list(REVIEW_STATUS_VOCABULARY),
        "review_acceptance_gates": list(REVIEW_ACCEPTANCE_GATES),
        "review_rejection_gates": list(REVIEW_REJECTION_GATES),
        "review_deferral_gates": list(REVIEW_DEFERRAL_GATES),
        "reviewer_authority_limits": list(REVIEWER_AUTHORITY_LIMITS),
        "invalid_review_claims": list(INVALID_REVIEW_CLAIMS),
        "stop_conditions": list(STOP_CONDITIONS),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "required_report_caveats": list(REQUIRED_REPORT_CAVEATS),
        "source_capsule_git_truth_separation": dict(SOURCE_CAPSULE_GIT_TRUTH_SEPARATION),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "lockout_text": list(LOCKOUT_TEXT),
    }
