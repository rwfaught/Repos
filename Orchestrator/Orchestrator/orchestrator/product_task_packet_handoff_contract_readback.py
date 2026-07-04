"""Pure handoff contract readback data for product task packets."""

from __future__ import annotations

from typing import Any


PHASE = 361
BOUNDARY = "PHASE361_PRODUCT_TASK_PACKET_HANDOFF_CONTRACT_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE361_PRODUCT_TASK_PACKET_HANDOFF_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE362_PRODUCT_TASK_PACKET_HANDOFF_PACKET_REVIEW_READBACK_SOURCE_TEST_DOCS"
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
)

HANDOFF_PREREQUISITES = (
    "exact active boundary declared",
    "completed packet spine through Phase 360 preserved",
    "allowed file list and mutation authority preserved",
    "working tree clean before handoff claim",
    "remote-before ref matches expected commit before handoff claim",
    "accepted facts and inference separated",
    "source/capsule/Git truth separated",
    "context saturation or explicit handoff need stated",
)

HANDOFF_PAYLOAD_DOCTRINE = (
    "handoff payload is operator-legible readback context only",
    "handoff payload is not task execution",
    "handoff payload must preserve boundary, source basis, validation status, changed files, non-proofs, and stop gates",
    "handoff payload must not claim Source Files refresh or official capsule proof",
    "handoff payload must not imply semantic correctness or production readiness",
)

HANDOFF_RECIPIENT_DOCTRINE = (
    "handoff recipient description is not provider/model execution",
    "handoff recipient may identify a future human/coordinator/worker review boundary",
    "handoff recipient does not authorize worker dispatch",
    "handoff recipient does not authorize route selection execution",
    "handoff recipient does not authorize patch application or real domain execution",
)

HANDOFF_AUTHORITY_LIMITS = (
    "handoff contract readback is not handoff execution",
    "handoff eligibility is not worker dispatch",
    "handoff readback cannot ratify worker PASS",
    "handoff readback cannot prove semantic correctness",
    "handoff readback cannot prove production readiness",
    "handoff readback cannot supersede Phase 335 capsule proof",
)

HANDOFF_STOP_GATES = (
    "missing boundary",
    "dirty working tree",
    "remote-before mismatch",
    "proof overclaim",
    "source/capsule/Git truth conflation",
    "context saturation/handoff needed",
    "request for live/runtime/provider/model/platform/domain execution",
    "request for service/API/UI/dashboard/auth/deployment",
    "request for Source Files refresh",
    "request for capsule/export/package refresh",
    "request for worker dispatch",
    "request for patch application",
)

BLOCKED_OR_DEFERRED_ACTIONS = (
    "handoff execution",
    "worker dispatch",
    "patch application",
    "route selection execution",
    "provider/model execution",
    "runtime/provider/model/platform execution",
    "domain-general intake implementation",
    "live business-data access",
    "live Obsidian/PKMS access",
    "adapter execution",
    "real domain execution",
    "Source Files refresh",
    "capsule/export/package refresh",
    "official capsule proof beyond Phase 335",
)

INVALID_HANDOFF_CLAIMS = (
    "handoff contract readback means handoff execution occurred",
    "handoff eligibility means worker dispatch occurred",
    "handoff payload means task execution occurred",
    "handoff recipient description means provider/model execution occurred",
    "worker PASS means coordinator ratification",
    "test PASS means semantic correctness",
    "pushed commit means production readiness",
    "Git repo truth means Source Files handoff snapshot truth",
    "Source Files handoff snapshot means official capsule proof",
    "Phase 361 supersedes Phase 335 capsule proof",
)

STOP_CONDITIONS = (
    "missing boundary",
    "missing allowlist",
    "dirty working tree",
    "remote-before mismatch",
    "proof overclaim",
    "source/capsule/Git truth conflation",
    "context saturation/handoff needed",
    "live/runtime/provider/model/platform/domain execution request",
    "service/API/UI/dashboard/auth/deployment request",
    "Source Files refresh request",
    "capsule/export/package refresh request",
    "worker dispatch request",
    "patch application request",
)

FALSE_ACTIVITY_FLAGS = {
    "handoff_executed": False,
    "runtime_provider_model_platform_executed": False,
    "service_api_ui_dashboard_auth_deployment_work": False,
    "general_answer_resumed": False,
    "worker_dispatched": False,
    "patch_applied": False,
    "patch_workflow_implemented": False,
    "routing_implemented": False,
    "route_selection_executed": False,
    "provider_policy_implemented": False,
    "provider_model_executed": False,
    "domain_general_intake_implemented": False,
    "lifecycle_transition_executed": False,
    "live_task_created": False,
    "live_task_executed": False,
    "live_mutation": False,
    "live_business_data_access": False,
    "live_obsidian_pkms_access": False,
    "adapter_execution": False,
    "real_domain_execution": False,
    "source_files_refreshed": False,
    "capsule_export_package_refreshed": False,
    "semantic_correctness_proven": False,
    "production_readiness_proven": False,
    "autonomous_ai_coding_authority": False,
    "official_capsule_proof_beyond_phase_335": False,
}

REQUIRED_REPORT_CAVEATS = (
    "readback is not execution",
    "handoff contract readback is not handoff execution",
    "handoff eligibility is not worker dispatch",
    "eligibility is not implementation",
    "handoff payload is not task execution",
    "handoff recipient description is not provider/model execution",
    "worker PASS is evidence, not coordinator ratification",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "Git repo truth is distinct from Source Files handoff snapshots",
    "official clean capsule proof remains separate",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

SOURCE_CAPSULE_GIT_TRUTH_SEPARATION = {
    "Git repo truth": "current tracked source state in the repository",
    "Source Files handoff snapshots": "handoff/source snapshots, not Git truth or official capsule proof",
    "official clean product capsule proofs": "separate clean capsule records; Phase 335 remains accepted",
    "full Git repo backups including .git": "backup artifacts, not official clean product capsules",
}

LOCKOUT_TEXT = (
    "No runtime/provider/model/platform execution",
    "No service/API/UI/dashboard/auth/deployment",
    "No general_answer",
    "No Source Files refresh",
    "No capsule/export/package refresh",
    "No semantic correctness",
    "No production readiness",
    "No autonomous AI coding authority",
    "No live business-data access",
    "No live Obsidian/PKMS access",
    "No adapter execution",
    "No real domain execution",
    "No patch application",
    "No worker dispatch",
    "No provider/model execution",
    "No route selection execution",
    "No domain-general intake implementation",
    "No official capsule proof beyond Phase 335",
)


def read_product_task_packet_handoff_contract_readback() -> dict[str, Any]:
    """Return deterministic handoff contract readback data."""
    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_basis": dict(SOURCE_BASIS),
        "completed_packet_spine": list(COMPLETED_PACKET_SPINE),
        "handoff_contract_purpose": (
            "Define product task packet handoff eligibility and stop doctrine only; "
            "handoff contract readback is not handoff execution."
        ),
        "handoff_prerequisites": list(HANDOFF_PREREQUISITES),
        "handoff_payload_doctrine": list(HANDOFF_PAYLOAD_DOCTRINE),
        "handoff_recipient_doctrine": list(HANDOFF_RECIPIENT_DOCTRINE),
        "handoff_authority_limits": list(HANDOFF_AUTHORITY_LIMITS),
        "handoff_stop_gates": list(HANDOFF_STOP_GATES),
        "blocked_or_deferred_actions": list(BLOCKED_OR_DEFERRED_ACTIONS),
        "invalid_handoff_claims": list(INVALID_HANDOFF_CLAIMS),
        "stop_conditions": list(STOP_CONDITIONS),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "required_report_caveats": list(REQUIRED_REPORT_CAVEATS),
        "source_capsule_git_truth_separation": dict(SOURCE_CAPSULE_GIT_TRUTH_SEPARATION),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "lockout_text": list(LOCKOUT_TEXT),
    }
