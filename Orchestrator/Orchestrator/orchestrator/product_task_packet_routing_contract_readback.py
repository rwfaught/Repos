"""Pure routing-contract readback data for product task packets."""

from __future__ import annotations

from typing import Any


PHASE = 356
BOUNDARY = "PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"

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
PHASE_354_BOUNDARY = (
    "PHASE354_PRODUCT_TASK_PACKET_NEXT_SEAM_SELECTION_READBACK_SOURCE_TEST_DOCS"
)
PHASE_354_SOURCE = "orchestrator/product_task_packet_next_seam_selection_readback.py"
PHASE_354_MARKER = (
    "PHASE354_PRODUCT_TASK_PACKET_NEXT_SEAM_SELECTION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
)
PHASE_355_BOUNDARY = (
    "PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS"
)
PHASE_355_SOURCE = "orchestrator/product_task_packet_lifecycle_state_readback.py"
PHASE_355_MARKER = (
    "PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
)

RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE357_PRODUCT_TASK_PACKET_PATCH_WORKFLOW_CONTRACT_READBACK_SOURCE_TEST_DOCS"
)

COMPLETED_PACKET_SPINE = (
    "report_surface_phase_349",
    "negative_edge_contract_phase_351",
    "operator_decision_readback_phase_352",
    "next_seam_selection_readback_phase_354",
    "lifecycle_state_readback_phase_355",
)


def _route(
    route_id: str,
    description: str,
    eligible_from_lifecycle_states: tuple[str, ...],
    allowed_operations: tuple[str, ...],
    stop_conditions: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "description": description,
        "eligible_from_lifecycle_states": list(eligible_from_lifecycle_states),
        "required_preconditions": [
            "exact boundary declared",
            "source basis preserved",
            "lifecycle state known",
            "lockouts preserved",
        ],
        "required_evidence": [
            "current packet state",
            "accepted source basis",
            "operator boundary facts",
        ],
        "allowed_operations": list(allowed_operations),
        "excluded_operations": [
            "routing implementation",
            "route execution",
            "route selection execution",
            "worker dispatch",
            "patch application",
            "provider/model execution",
            "live mutation",
            "service/API/UI/dashboard/auth/deployment work",
        ],
        "stop_conditions": list(stop_conditions),
        "non_proofs": [
            "not_route_execution",
            "not_routing_implementation",
            "not_production_readiness",
        ],
    }


ROUTE_CONTRACTS = (
    _route(
        "route_to_read_only_review",
        "Read-only review route for inspection without mutation.",
        ("boundary_declared", "allowlist_declared", "source_basis_declared"),
        ("read files", "list files", "search text", "report findings"),
    ),
    _route(
        "route_to_bounded_source_test_docs_mutation",
        "Bounded mutation route for allowlisted source/test/docs changes.",
        ("mutation_authorized",),
        ("mutate allowlisted source/test/docs files",),
        ("out-of-allowlist mutation request",),
    ),
    _route(
        "route_to_coordinator_review",
        "Coordinator review route after local commit creation.",
        ("local_commit_created",),
        ("report local commit hash", "preserve non-proofs"),
    ),
    _route(
        "route_to_push_ref_verification",
        "Push/ref verification route after coordinator review.",
        ("push_ref_verify_authorized",),
        ("verify remote-before", "push reviewed commit", "verify remote ref"),
        ("remote-before mismatch",),
    ),
    _route(
        "route_to_handoff",
        "Handoff route when context saturation or boundary limits appear.",
        ("handoff_required", "blocked_by_context_saturation"),
        ("prepare handoff facts", "preserve scope"),
        ("context saturation/handoff needed",),
    ),
    _route(
        "route_to_stop_missing_boundary",
        "Stop route for missing exact boundary.",
        ("packet_unformed", "blocked_by_missing_boundary"),
        ("report missing boundary",),
        ("missing boundary",),
    ),
    _route(
        "route_to_stop_missing_allowlist",
        "Stop route for missing mutation allowlist.",
        ("boundary_declared", "blocked_by_missing_allowlist"),
        ("report missing allowlist",),
        ("missing allowlist",),
    ),
    _route(
        "route_to_stop_lockout",
        "Stop route for lockout conflict.",
        ("blocked_by_lockout",),
        ("report lockout conflict",),
        ("runtime/provider/model/platform request",),
    ),
    _route(
        "route_to_stop_proof_overclaim",
        "Stop route for proof claims that exceed evidence.",
        ("blocked_by_proof_overclaim", "validation_pending"),
        ("report proof overclaim",),
        ("proof overclaim",),
    ),
    _route(
        "route_to_stop_source_capsule_git_truth_conflation",
        "Stop route for conflating Git truth, Source Files, or capsule proof.",
        ("blocked_by_source_capsule_git_truth_conflation",),
        ("report truth conflation",),
        ("source/capsule/Git truth conflation",),
    ),
    _route(
        "route_to_stop_context_saturation",
        "Stop route that forces handoff instead of scope expansion.",
        ("blocked_by_context_saturation",),
        ("report context saturation",),
        ("context saturation/handoff needed",),
    ),
    _route(
        "route_to_deferred_patch_workflow_contract",
        "Deferred route to later patch workflow contract readback.",
        ("complete_for_current_boundary",),
        ("recommend patch workflow contract readback",),
    ),
    _route(
        "route_to_deferred_worker_dispatch_contract",
        "Deferred route to later worker dispatch contract readback.",
        ("complete_for_current_boundary",),
        ("recommend worker dispatch contract readback",),
    ),
    _route(
        "route_to_deferred_provider_policy_contract",
        "Deferred route to later provider policy contract readback.",
        ("complete_for_current_boundary",),
        ("recommend provider policy contract readback",),
    ),
    _route(
        "route_to_deferred_domain_general_intake_contract",
        "Deferred route to later domain-general intake contract readback.",
        ("complete_for_current_boundary",),
        ("recommend domain-general intake contract readback",),
    ),
    _route(
        "route_to_deferred_runtime_provider_execution",
        "Deferred route for runtime/provider execution under a separate boundary.",
        ("complete_for_current_boundary",),
        ("recommend separate runtime/provider boundary",),
    ),
)

ROUTING_GATES = (
    "exact boundary declared",
    "file allowlist declared",
    "source basis preserved",
    "lifecycle state known",
    "lockouts preserved",
    "validation plan present",
    "changed-file audit available",
    "coordinator review before push",
    "remote-before check before push",
    "handoff when context saturation appears",
    "separate boundary for patch workflow",
    "separate boundary for worker dispatch",
    "separate boundary for provider policy",
    "separate boundary for provider/model execution",
    "separate boundary for Source Files refresh",
    "separate boundary for official capsule proof",
)

BLOCKED_ROUTES = (
    "route_to_runtime_provider_model_platform_execution",
    "route_to_service_api_ui_dashboard_auth_deployment",
    "route_to_live_business_data_access",
    "route_to_live_obsidian_pkms_access",
    "route_to_live_mutation",
    "route_to_adapter_execution",
    "route_to_real_domain_execution",
    "route_to_general_answer_resumption",
    "route_to_worker_dispatch_without_boundary",
    "route_to_patch_application_without_boundary",
    "route_to_provider_execution_without_boundary",
    "route_to_source_files_refresh_as_capsule_proof",
    "route_to_capsule_export_package_without_boundary",
    "route_to_production_execution",
)

ROUTING_DOCTRINE = (
    "readback precedes route execution",
    "lifecycle state precedes route eligibility",
    "routing contract precedes routing implementation",
    "patch workflow contract precedes patch application",
    "worker dispatch contract precedes worker dispatch",
    "provider policy contract precedes provider/model execution",
    "domain-general intake contract precedes domain-general intake",
    "coordinator review precedes push/ref verification",
    "remote-before check precedes push",
    "pushed commit does not prove production readiness",
    "test PASS does not prove semantic correctness",
    "worker PASS is evidence, not coordinator ratification",
    "Source Files refresh is not official capsule proof",
    "Phase 335 remains accepted capsule proof unless explicitly superseded",
    "context saturation routes to handoff, not scope expansion",
)

INVALID_ROUTE_CLAIMS = (
    "route contract means routing implementation exists",
    "route eligibility means route execution occurred",
    "route to worker means worker dispatch occurred",
    "route to patch means patch application occurred",
    "route to provider means provider/model execution occurred",
    "route to review means coordinator ratified",
    "route to push means push was performed",
    "route to Source Files means capsule proof",
    "test PASS means semantic correctness",
    "pushed commit means production readiness",
    "source snapshot means Git truth",
    "capsule snapshot means live system readiness",
)

STOP_CONDITIONS = (
    "missing boundary",
    "missing allowlist",
    "unknown lifecycle state",
    "out-of-allowlist mutation request",
    "runtime/provider/model/platform request",
    "service/API/UI/dashboard/auth/deployment request",
    "general_answer resumption request",
    "worker dispatch request without worker boundary",
    "patch application request without patch boundary",
    "provider execution request without provider boundary",
    "source/capsule/Git truth conflation",
    "proof overclaim",
    "failed validation",
    "dirty working tree",
    "remote-before mismatch",
    "context saturation/handoff needed",
)

FALSE_ACTIVITY_FLAGS = {
    "runtime_provider_model_platform_executed": False,
    "service_api_ui_dashboard_auth_deployment_work": False,
    "general_answer_resumed": False,
    "worker_dispatched": False,
    "patch_applied": False,
    "routing_implemented": False,
    "route_selection_executed": False,
    "provider_policy_implemented": False,
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
    "routing contract readback is not route execution",
    "route eligibility is not routing implementation",
    "route contract is not runtime enforcement",
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
    "routing contract readback is not route execution",
    "route eligibility is not routing implementation",
    "Source Files refresh is not official capsule proof",
)


def read_product_task_packet_routing_contract_readback() -> dict[str, Any]:
    """Return deterministic source-level routing-contract readback data."""
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
            "phase_354": {
                "boundary": PHASE_354_BOUNDARY,
                "marker": PHASE_354_MARKER,
                "source_file": PHASE_354_SOURCE,
            },
            "phase_355": {
                "boundary": PHASE_355_BOUNDARY,
                "marker": PHASE_355_MARKER,
                "source_file": PHASE_355_SOURCE,
            },
        },
        "routing_contract_purpose": (
            "Deterministic readback surface for routing eligibility and "
            "routing-stop doctrine; it is not route execution or routing implementation."
        ),
        "completed_packet_spine": list(COMPLETED_PACKET_SPINE),
        "route_contracts": [dict(route) for route in ROUTE_CONTRACTS],
        "routing_gates": list(ROUTING_GATES),
        "blocked_routes": list(BLOCKED_ROUTES),
        "routing_doctrine": list(ROUTING_DOCTRINE),
        "invalid_route_claims": list(INVALID_ROUTE_CLAIMS),
        "stop_conditions": list(STOP_CONDITIONS),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "required_report_caveats": list(REQUIRED_REPORT_CAVEATS),
        "source_capsule_git_truth_separation": dict(
            SOURCE_CAPSULE_GIT_TRUTH_SEPARATION
        ),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "recommended_next_boundary_rationale": (
            "After routing-contract readback, a patch-workflow contract readback "
            "can define patch eligibility and patch-stop doctrine without applying patches."
        ),
        "lockout_text": list(LOCKOUT_TEXT),
    }
