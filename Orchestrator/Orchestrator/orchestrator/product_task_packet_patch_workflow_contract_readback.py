"""Pure patch-workflow contract readback data for product task packets."""

from __future__ import annotations

from typing import Any


PHASE = 357
BOUNDARY = "PHASE357_PRODUCT_TASK_PACKET_PATCH_WORKFLOW_CONTRACT_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE357_PRODUCT_TASK_PACKET_PATCH_WORKFLOW_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE358_PRODUCT_TASK_PACKET_WORKER_DISPATCH_CONTRACT_READBACK_SOURCE_TEST_DOCS"
)

SOURCE_BASIS = {
    "phase_349": {
        "boundary": "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS",
        "marker": "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS_PROVEN=PASS",
        "source_file": "orchestrator/product_task_packet_operator_report.py",
    },
    "phase_351": {
        "boundary": "PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS",
        "marker": "PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS",
        "source_file": "orchestrator/product_task_packet_negative_edge.py",
    },
    "phase_352": {
        "boundary": "PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS",
        "marker": "PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS",
        "source_file": "orchestrator/product_task_packet_operator_decision_readback.py",
    },
    "phase_354": {
        "boundary": "PHASE354_PRODUCT_TASK_PACKET_NEXT_SEAM_SELECTION_READBACK_SOURCE_TEST_DOCS",
        "marker": "PHASE354_PRODUCT_TASK_PACKET_NEXT_SEAM_SELECTION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS",
        "source_file": "orchestrator/product_task_packet_next_seam_selection_readback.py",
    },
    "phase_355": {
        "boundary": "PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS",
        "marker": "PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS",
        "source_file": "orchestrator/product_task_packet_lifecycle_state_readback.py",
    },
    "phase_356": {
        "boundary": "PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS",
        "marker": "PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS",
        "source_file": "orchestrator/product_task_packet_routing_contract_readback.py",
    },
}

COMPLETED_PACKET_SPINE = (
    "report_surface_phase_349",
    "negative_edge_contract_phase_351",
    "operator_decision_readback_phase_352",
    "next_seam_selection_readback_phase_354",
    "lifecycle_state_readback_phase_355",
    "routing_contract_readback_phase_356",
)

PATCH_WORKFLOW_GATES = (
    "exact boundary declared",
    "file allowlist declared",
    "routing contract preserved",
    "patch eligibility state declared",
    "patch preparation evidence present",
    "patch review required before apply",
    "patch application requires future explicit boundary",
    "validation plan present",
    "changed-file audit available",
)

PATCH_ELIGIBILITY_STATES = (
    "patch_contract_readback_only",
    "patch_preparation_allowed",
    "patch_review_required",
    "patch_application_blocked_without_future_boundary",
)

PATCH_PREPARATION_CONTRACT = (
    "identify allowlisted files",
    "describe intended source/test/docs changes",
    "preserve lockouts before mutation",
)

PATCH_REVIEW_CONTRACT = (
    "review diff before local commit",
    "run validation before local commit",
    "worker PASS is evidence, not coordinator ratification",
)

PATCH_VALIDATION_REQUIREMENTS = (
    "compile targeted sources",
    "run targeted tests",
    "marker search",
    "changed-file audit",
    "git diff --check",
)

BLOCKED_OR_DEFERRED_ACTIONS = (
    "patch application behavior",
    "patch workflow implementation",
    "live mutation",
    "worker dispatch behavior",
    "runtime/provider/model/platform execution",
    "service/API/UI/dashboard/auth/deployment work",
)

INVALID_CLAIMS = (
    "patch contract means patch workflow implementation exists",
    "patch eligibility means patch application occurred",
    "patch review means coordinator ratified",
    "test PASS means semantic correctness",
    "pushed commit means production readiness",
    "Source Files refresh means official capsule proof",
)

STOP_CONDITIONS = (
    "missing boundary",
    "missing allowlist",
    "out-of-allowlist mutation",
    "runtime/provider/model/platform request",
    "service/API/UI/dashboard/auth/deployment request",
    "patch application request without patch boundary",
    "worker dispatch request without worker boundary",
    "proof overclaim",
    "dirty working tree",
    "remote-before mismatch",
    "source/capsule/Git truth conflation",
    "context saturation/handoff needed",
)

FALSE_ACTIVITY_FLAGS = {
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
}

REQUIRED_REPORT_CAVEATS = (
    "readback is not execution",
    "eligibility is not implementation",
    "contract is not runtime enforcement",
    "worker PASS is evidence, not coordinator ratification",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "Git repo truth is distinct from Source Files handoff snapshots",
    "official clean capsule proof remains separate",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

SOURCE_CAPSULE_GIT_TRUTH_SEPARATION = {
    "Git repo truth": "current tracked source state in the repository",
    "Source Files handoff snapshots": "handoff/source snapshots, not official capsule proof",
    "official clean product capsule proofs": "separate clean capsule records; Phase 335 remains accepted",
    "full Git repo backups including .git": "backup artifacts, not official clean product capsules",
}

LOCKOUT_TEXT = (
    "No runtime/provider/model/platform execution",
    "No service/API/UI/dashboard/auth/deployment",
    "No general_answer",
    "No Source Files refresh",
    "No capsule/export/package refresh",
    "semantic correctness",
    "production readiness",
    "autonomous AI coding",
    "Phase 335",
)


def read_product_task_packet_patch_workflow_contract_readback() -> dict[str, Any]:
    """Return deterministic patch workflow contract readback data."""
    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_basis": dict(SOURCE_BASIS),
        "patch_workflow_contract_purpose": (
            "Define patch workflow eligibility and stop doctrine only; readback is not execution."
        ),
        "completed_packet_spine": list(COMPLETED_PACKET_SPINE),
        "patch_workflow_gates": list(PATCH_WORKFLOW_GATES),
        "patch_eligibility_states": list(PATCH_ELIGIBILITY_STATES),
        "patch_preparation_contract": list(PATCH_PREPARATION_CONTRACT),
        "patch_review_contract": list(PATCH_REVIEW_CONTRACT),
        "patch_application_status": "blocked unless future explicit boundary",
        "patch_validation_requirements": list(PATCH_VALIDATION_REQUIREMENTS),
        "blocked_or_deferred_actions": list(BLOCKED_OR_DEFERRED_ACTIONS),
        "invalid_claims": list(INVALID_CLAIMS),
        "stop_conditions": list(STOP_CONDITIONS),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "required_report_caveats": list(REQUIRED_REPORT_CAVEATS),
        "source_capsule_git_truth_separation": dict(SOURCE_CAPSULE_GIT_TRUTH_SEPARATION),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "lockout_text": list(LOCKOUT_TEXT),
    }
