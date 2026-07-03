"""Pure next-seam selection/readback data for product task packets."""

from __future__ import annotations

from typing import Any


PHASE = 354
BOUNDARY = "PHASE354_PRODUCT_TASK_PACKET_NEXT_SEAM_SELECTION_READBACK_SOURCE_TEST_DOCS"
MARKER = (
    "PHASE354_PRODUCT_TASK_PACKET_NEXT_SEAM_SELECTION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
)

PHASE_349_BOUNDARY = "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS"
PHASE_349_SOURCE = "orchestrator/product_task_packet_operator_report.py"
PHASE_349_MARKER = (
    "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS_PROVEN=PASS"
)
PHASE_351_BOUNDARY = "PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS"
PHASE_351_SOURCE = "orchestrator/product_task_packet_negative_edge.py"
PHASE_351_MARKER = (
    "PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS"
)
PHASE_352_BOUNDARY = (
    "PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS"
)
PHASE_352_SOURCE = "orchestrator/product_task_packet_operator_decision_readback.py"
PHASE_352_MARKER = (
    "PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
)

RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS"
)

COMPLETED_PACKET_SPINE = (
    "report_surface_phase_349",
    "negative_edge_contract_phase_351",
    "operator_decision_readback_phase_352",
)

ELIGIBLE_NEXT_SEAMS = (
    {
        "seam_id": "packet_lifecycle_state_readback",
        "posture": "recommended_next_source_test_docs_readback",
        "allowed_operations": (
            "define static lifecycle states",
            "describe allowed transitions without executing them",
            "preserve stop/readback outcomes",
        ),
        "excluded_operations": (
            "live task execution",
            "live product task creation",
            "live mutation",
            "routing implementation",
        ),
        "required_preconditions": (
            "Phase 349 report surface preserved",
            "Phase 351 negative-edge contract preserved",
            "Phase 352 operator decision readback preserved",
        ),
        "proof_required": "source/test/docs deterministic lifecycle readback proof",
        "non_proofs": (
            "not_task_execution",
            "not_routing_implementation",
            "not_production_execution",
        ),
        "recommended_order": 1,
    },
    {
        "seam_id": "routing_contract_readback",
        "posture": "eligible_after_lifecycle_readback",
        "allowed_operations": (
            "describe routing contract candidates",
            "record routing preconditions",
            "preserve routing lockouts",
        ),
        "excluded_operations": (
            "routing implementation",
            "route execution",
            "provider/model execution",
        ),
        "required_preconditions": (
            "packet lifecycle/state readback exists",
            "exact boundary and allowlist exist",
        ),
        "proof_required": "source/test/docs routing contract readback proof",
        "non_proofs": (
            "not_routing_implementation",
            "not_route_execution",
            "not_provider_execution",
        ),
        "recommended_order": 2,
    },
    {
        "seam_id": "patch_workflow_contract_readback",
        "posture": "eligible_after_lifecycle_readback",
        "allowed_operations": (
            "describe patch workflow contract",
            "record patch preconditions",
            "preserve apply lockouts",
        ),
        "excluded_operations": (
            "patch application",
            "live mutation",
            "task finalization",
        ),
        "required_preconditions": (
            "packet lifecycle/state readback exists",
            "explicit patch boundary exists before patch application",
        ),
        "proof_required": "source/test/docs patch workflow contract readback proof",
        "non_proofs": (
            "not_patch_application",
            "not_live_mutation",
            "not_task_finalization",
        ),
        "recommended_order": 3,
    },
    {
        "seam_id": "worker_dispatch_contract_readback",
        "posture": "eligible_after_lifecycle_readback",
        "allowed_operations": (
            "describe worker dispatch contract",
            "record worker boundary requirements",
            "preserve dispatch lockouts",
        ),
        "excluded_operations": (
            "worker dispatch behavior",
            "Codex worker execution",
            "relay execution",
        ),
        "required_preconditions": (
            "packet lifecycle/state readback exists",
            "separate explicit worker boundary exists",
        ),
        "proof_required": "source/test/docs worker dispatch contract readback proof",
        "non_proofs": (
            "not_worker_dispatch",
            "not_codex_execution",
            "not_coordinator_ratification",
        ),
        "recommended_order": 4,
    },
    {
        "seam_id": "provider_policy_readback",
        "posture": "eligible_policy_readback_only",
        "allowed_operations": (
            "describe provider policy candidates",
            "record provider execution preconditions",
            "preserve runtime/provider/model/platform lockouts",
        ),
        "excluded_operations": (
            "provider policy implementation",
            "runtime/provider/model/platform execution",
            "model correctness proof",
        ),
        "required_preconditions": (
            "separate provider policy boundary exists",
            "separate provider execution boundary exists before execution",
        ),
        "proof_required": "source/test/docs provider policy readback proof",
        "non_proofs": (
            "not_provider_policy_implementation",
            "not_provider_execution",
            "not_model_correctness",
        ),
        "recommended_order": 5,
    },
    {
        "seam_id": "domain_general_intake_readback",
        "posture": "eligible_readback_only_deferred_from_implementation",
        "allowed_operations": (
            "describe domain-general intake readback candidates",
            "record intake preconditions",
            "preserve service/API/UI/dashboard lockouts",
        ),
        "excluded_operations": (
            "domain-general intake implementation",
            "service/API/UI/dashboard/auth/deployment work",
            "live business-data access",
        ),
        "required_preconditions": (
            "separate intake boundary exists",
            "service/API/UI/dashboard work remains locked out",
        ),
        "proof_required": "source/test/docs domain-general intake readback proof",
        "non_proofs": (
            "not_domain_general_intake_implementation",
            "not_service_api_ui_dashboard_auth_deployment",
            "not_live_business_data_access",
        ),
        "recommended_order": 6,
    },
    {
        "seam_id": "handoff_packet_readback",
        "posture": "eligible_when_context_saturation_appears",
        "allowed_operations": (
            "describe handoff packet readback",
            "record continuation facts and caveats",
            "preserve scope instead of expanding it",
        ),
        "excluded_operations": (
            "scope expansion",
            "unbounded continuation",
            "capsule/export/package refresh",
        ),
        "required_preconditions": (
            "context saturation or handoff need is explicit",
            "accepted facts and inference remain separated",
        ),
        "proof_required": "source/test/docs handoff packet readback proof",
        "non_proofs": (
            "not_scope_expansion",
            "not_capsule_refresh",
            "not_official_capsule_proof",
        ),
        "recommended_order": 7,
    },
)

BLOCKED_OR_DEFERRED_SEAMS = (
    "runtime/provider/model/platform execution",
    "service/API/UI/dashboard/auth/deployment",
    "live business-data access",
    "live Obsidian/PKMS access",
    "live mutation",
    "adapter execution",
    "real domain execution",
    "general_answer resumption",
    "Source Files refresh",
    "capsule/export/package refresh",
    "production execution",
)

SELECTION_RULES = (
    "choose readback before execution",
    "choose lifecycle before routing",
    "choose routing contract before routing implementation",
    "choose patch contract before patch application",
    "choose worker contract before worker dispatch",
    "choose provider policy before provider/model execution",
    "choose handoff when context saturation appears",
    "require separate push/ref verification after local commit",
    "require separate capsule-proof boundary for official capsule claims",
)

STOP_CONDITIONS = (
    "missing boundary",
    "missing allowlist",
    "out-of-allowlist mutation",
    "runtime/provider/model/platform request",
    "service/API/UI/dashboard/auth/deployment request",
    "general_answer resumption request",
    "worker dispatch request without worker boundary",
    "patch application request without patch boundary",
    "provider execution request without provider boundary",
    "source/capsule/Git truth conflation",
    "proof overclaim",
    "context saturation/handoff needed",
)

FALSE_ACTIVITY_FLAGS = {
    "runtime_provider_model_platform_executed": False,
    "service_api_ui_dashboard_auth_deployment_work": False,
    "general_answer_resumed": False,
    "worker_dispatched": False,
    "patch_applied": False,
    "routing_implemented": False,
    "provider_policy_implemented": False,
    "domain_general_intake_implemented": False,
    "live_task_created": False,
    "live_task_executed": False,
    "live_mutation": False,
    "live_business_data_access": False,
    "adapter_execution": False,
    "real_domain_execution": False,
    "source_files_refreshed": False,
    "capsule_export_package_refreshed": False,
    "semantic_correctness_proven": False,
    "production_readiness_proven": False,
    "autonomous_ai_coding_authority": False,
}

REQUIRED_REPORT_CAVEATS = (
    "seam selection readback is not execution",
    "candidate seam eligibility is not implementation",
    "recommended next boundary is not authorization for later seams",
    "worker PASS is evidence, not coordinator ratification",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "Git repo truth is distinct from Source Files handoff snapshots",
    "official clean capsule proof remains separate",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
)

SOURCE_CAPSULE_GIT_TRUTH_SEPARATION = {
    "Git repo truth": "current tracked source state in the repository",
    "Source Files handoff snapshots": (
        "orientation snapshots that may lag Git truth and are not official capsule proof"
    ),
    "official clean product capsule proofs": (
        "separate clean capsule records; Phase 335 remains the accepted official proof"
    ),
    "full Git repo backups including .git": (
        "backup artifacts, not official clean product capsules"
    ),
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
    RECOMMENDED_NEXT_BOUNDARY,
)


def read_product_task_packet_next_seam_selection_readback() -> dict[str, Any]:
    """Return deterministic source-level next-seam selection data."""
    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_basis": {
            "phase_349": {
                "boundary": PHASE_349_BOUNDARY,
                "marker": PHASE_349_MARKER,
                "source_file": PHASE_349_SOURCE,
            },
            "phase_351": {
                "boundary": PHASE_351_BOUNDARY,
                "marker": PHASE_351_MARKER,
                "source_file": PHASE_351_SOURCE,
            },
            "phase_352": {
                "boundary": PHASE_352_BOUNDARY,
                "marker": PHASE_352_MARKER,
                "source_file": PHASE_352_SOURCE,
            },
        },
        "seam_selection_purpose": (
            "Deterministic readback surface for deciding the next safe seam "
            "after the product task packet report, negative-edge, and "
            "operator-decision chain."
        ),
        "completed_packet_spine": list(COMPLETED_PACKET_SPINE),
        "eligible_next_seams": [dict(seam) for seam in ELIGIBLE_NEXT_SEAMS],
        "blocked_or_deferred_seams": list(BLOCKED_OR_DEFERRED_SEAMS),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "recommended_next_boundary_rationale": (
            "Before routing, worker dispatch, patch application, or provider "
            "policy, the packet should have a deterministic lifecycle/state "
            "model that describes transitions without executing them."
        ),
        "selection_rules": list(SELECTION_RULES),
        "stop_conditions": list(STOP_CONDITIONS),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "required_report_caveats": list(REQUIRED_REPORT_CAVEATS),
        "source_capsule_git_truth_separation": dict(
            SOURCE_CAPSULE_GIT_TRUTH_SEPARATION
        ),
        "lockout_text": list(LOCKOUT_TEXT),
    }
