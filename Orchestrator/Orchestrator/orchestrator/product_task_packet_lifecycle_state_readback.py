"""Pure lifecycle/state readback data for product task packets."""

from __future__ import annotations

from typing import Any


PHASE = 355
BOUNDARY = "PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS"
MARKER = "PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"

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

RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS"
)

COMPLETED_PACKET_SPINE = (
    "report_surface_phase_349",
    "negative_edge_contract_phase_351",
    "operator_decision_readback_phase_352",
    "next_seam_selection_readback_phase_354",
)


def _state(
    state_id: str,
    description: str,
    allowed_next_states: tuple[str, ...] = (),
    blocked_next_states: tuple[str, ...] = (),
    required_evidence: tuple[str, ...] = (),
    allowed_operations: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "state_id": state_id,
        "description": description,
        "allowed_next_states": list(allowed_next_states),
        "blocked_next_states": list(blocked_next_states),
        "required_evidence": list(required_evidence),
        "non_proofs": [
            "not_transition_execution",
            "not_runtime_provider_model_platform_execution",
            "not_production_readiness",
        ],
        "allowed_operations": list(allowed_operations or ("readback only",)),
        "excluded_operations": [
            "transition execution",
            "live task execution",
            "live mutation",
            "routing implementation",
            "patch application",
            "worker dispatch",
            "provider/model execution",
            "service/API/UI/dashboard/auth/deployment work",
        ],
    }


LIFECYCLE_STATES = (
    _state(
        "packet_unformed",
        "No bounded packet has been formed.",
        ("boundary_declared",),
        ("mutation_authorized", "live_task_executed"),
        ("operator intent",),
    ),
    _state(
        "boundary_declared",
        "Exact boundary is declared, but mutation authority is not complete.",
        ("allowlist_declared",),
        ("mutation_authorized", "runtime/provider/model/platform execution"),
        ("exact boundary",),
    ),
    _state(
        "allowlist_declared",
        "Mutation allowlist is declared before implementation.",
        ("source_basis_declared", "read_only_review_pending"),
        ("mutation_in_progress",),
        ("file allowlist",),
    ),
    _state(
        "source_basis_declared",
        "Source basis and accepted facts are declared.",
        ("read_only_review_pending", "mutation_authorized"),
        ("provider/model execution",),
        ("source basis", "accepted facts"),
    ),
    _state(
        "read_only_review_pending",
        "Read-only review is pending and cannot mutate.",
        ("mutation_authorized", "handoff_required"),
        ("mutation_in_progress",),
        ("review findings",),
        ("read files", "list files", "search text", "report findings"),
    ),
    _state(
        "mutation_authorized",
        "Scoped source/test/docs mutation is authorized.",
        ("mutation_in_progress", "validation_pending"),
        ("out-of-allowlist mutation",),
        ("exact boundary", "file allowlist", "lockouts"),
    ),
    _state(
        "mutation_in_progress",
        "Allowed files are being changed within the boundary.",
        ("validation_pending", "blocked_by_lockout"),
        ("push_ref_verify_authorized",),
        ("changed files within allowlist",),
    ),
    _state(
        "validation_pending",
        "Validation must run before local commit authorization.",
        ("local_commit_authorized", "blocked_by_proof_overclaim"),
        ("push_ref_verify_authorized",),
        ("compile/test/marker/audit plan",),
    ),
    _state(
        "local_commit_authorized",
        "Validation passed and local commit is authorized.",
        ("local_commit_created",),
        ("remote_ref_verified",),
        ("passed validation", "changed-file audit"),
    ),
    _state(
        "local_commit_created",
        "Local commit exists and awaits coordinator review.",
        ("coordinator_review_pending",),
        ("push_ref_verify_authorized",),
        ("local commit hash",),
    ),
    _state(
        "coordinator_review_pending",
        "Coordinator review must precede push/ref verification.",
        ("push_ref_verify_authorized", "handoff_required"),
        ("remote_ref_verified",),
        ("worker report", "local commit hash"),
    ),
    _state(
        "push_ref_verify_authorized",
        "Push/ref verification is authorized for the reviewed commit only.",
        ("remote_ref_verified",),
        ("production readiness",),
        ("coordinator authorization", "remote-before check"),
    ),
    _state(
        "remote_ref_verified",
        "Remote ref verification may close current boundary without production proof.",
        ("complete_for_current_boundary",),
        ("production readiness", "semantic correctness"),
        ("remote ref hash",),
    ),
    _state(
        "handoff_required",
        "A handoff is required instead of scope expansion.",
        ("packet_unformed",),
        ("mutation_in_progress",),
        ("handoff packet",),
    ),
    _state(
        "blocked_by_missing_boundary",
        "Work is blocked because the exact boundary is missing.",
        ("boundary_declared", "handoff_required"),
        ("mutation_authorized",),
        ("missing boundary finding",),
    ),
    _state(
        "blocked_by_missing_allowlist",
        "Work is blocked because the file allowlist is missing.",
        ("allowlist_declared", "handoff_required"),
        ("mutation_in_progress",),
        ("missing allowlist finding",),
    ),
    _state(
        "blocked_by_lockout",
        "Work is blocked by a lockout request.",
        ("handoff_required",),
        ("runtime/provider/model/platform execution", "service/API/UI/dashboard/auth/deployment work"),
        ("lockout finding",),
    ),
    _state(
        "blocked_by_proof_overclaim",
        "Work is blocked because proof claims exceed evidence.",
        ("handoff_required", "validation_pending"),
        ("production readiness",),
        ("proof overclaim finding",),
    ),
    _state(
        "blocked_by_source_capsule_git_truth_conflation",
        "Work is blocked because Git, Source Files, or capsule proof are conflated.",
        ("handoff_required",),
        ("official capsule proof claim",),
        ("truth conflation finding",),
    ),
    _state(
        "blocked_by_context_saturation",
        "Context saturation requires handoff instead of expansion.",
        ("handoff_required",),
        ("scope expansion",),
        ("context saturation finding",),
    ),
    _state(
        "complete_for_current_boundary",
        "Current boundary is complete at the accepted proof level.",
        (),
        ("production readiness", "future boundary completion"),
        ("completed report",),
    ),
)

TRANSITION_DOCTRINE = (
    "packet_unformed may only move to boundary_declared",
    "boundary_declared requires allowlist before mutation",
    "allowlist_declared requires source basis before implementation",
    "read_only_review_pending cannot mutate",
    "mutation_authorized must remain within allowlist",
    "validation_pending must precede local_commit_authorized",
    "local_commit_created must precede coordinator_review_pending",
    "coordinator_review_pending must precede push_ref_verify_authorized",
    "push_ref_verify_authorized may only verify Git refs and push the reviewed commit",
    "remote-ref verification does not prove production readiness",
    "remote_ref_verified may close the current boundary but does not prove production readiness",
    "blocked states cannot advance without a new bounded correction or handoff",
    "context saturation must route to handoff_required",
    "Source Files refresh requires separate authorization",
    "capsule/export/package proof requires separate authorization",
    "runtime/provider/model/platform work requires separate authorization",
    "service/API/UI/dashboard/auth/deployment work requires separate authorization",
)

INVALID_TRANSITIONS = (
    "packet_unformed_to_mutation",
    "boundary_declared_to_runtime_execution",
    "allowlist_missing_to_mutation",
    "read_only_review_to_mutation",
    "validation_pending_to_push",
    "local_commit_without_validation",
    "push_without_coordinator_review",
    "push_without_remote_before_check",
    "remote_ref_verified_to_production_ready",
    "source_files_refresh_as_capsule_proof",
    "capsule_snapshot_as_git_truth",
    "worker_pass_as_coordinator_ratification",
    "test_pass_as_semantic_correctness",
    "general_answer_resumption_without_boundary",
    "worker_dispatch_without_worker_boundary",
    "patch_application_without_patch_boundary",
    "provider_execution_without_provider_boundary",
    "service_api_ui_dashboard_without_service_boundary",
)

LIFECYCLE_GATES = (
    "exact boundary",
    "file allowlist",
    "lockout preservation",
    "source basis",
    "validation",
    "marker search",
    "changed-file audit",
    "local commit",
    "coordinator review",
    "push/ref verification",
    "handoff",
    "capsule-proof separation",
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
    "lifecycle state readback is not transition execution",
    "lifecycle eligibility is not implementation",
    "transition doctrine is not runtime enforcement",
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
    "lifecycle state readback is not transition execution",
    "remote-ref verification does not prove production readiness",
)


def read_product_task_packet_lifecycle_state_readback() -> dict[str, Any]:
    """Return deterministic source-level lifecycle/state readback data."""
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
        },
        "lifecycle_surface_purpose": (
            "Deterministic readback surface for product task packet lifecycle "
            "states and transition doctrine; it is not transition execution."
        ),
        "completed_packet_spine": list(COMPLETED_PACKET_SPINE),
        "lifecycle_states": [dict(state) for state in LIFECYCLE_STATES],
        "transition_doctrine": list(TRANSITION_DOCTRINE),
        "invalid_transitions": list(INVALID_TRANSITIONS),
        "lifecycle_gates": list(LIFECYCLE_GATES),
        "stop_conditions": list(STOP_CONDITIONS),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "required_report_caveats": list(REQUIRED_REPORT_CAVEATS),
        "source_capsule_git_truth_separation": dict(
            SOURCE_CAPSULE_GIT_TRUTH_SEPARATION
        ),
        "recommended_next_boundary": RECOMMENDED_NEXT_BOUNDARY,
        "recommended_next_boundary_rationale": (
            "After lifecycle-state readback, a routing contract readback can "
            "define route eligibility and route-stop doctrine without implementing routing."
        ),
        "lockout_text": list(LOCKOUT_TEXT),
    }
