"""Pure operator decision/readback data for product task packets."""

from __future__ import annotations

from typing import Any


PHASE = 352
BOUNDARY = "PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS"
MARKER = (
    "PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
)

PHASE_349 = 349
PHASE_349_SOURCE = "orchestrator/product_task_packet_operator_report.py"
PHASE_349_MARKER = (
    "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS_PROVEN=PASS"
)
PHASE_351 = 351
PHASE_351_SOURCE = "orchestrator/product_task_packet_negative_edge.py"
PHASE_351_MARKER = (
    "PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS"
)

ALLOWED_OPERATOR_DECISIONS = (
    "proceed_to_bounded_mutation",
    "request_read_only_seam_selection",
    "stop_missing_boundary",
    "stop_missing_allowlist",
    "stop_runtime_provider_model_platform_lockout",
    "stop_service_api_ui_dashboard_auth_deployment_lockout",
    "stop_general_answer_lockout",
    "stop_worker_dispatch_boundary_missing",
    "stop_patch_application_boundary_missing",
    "stop_proof_overclaim",
    "stop_source_capsule_git_truth_conflation",
    "stop_context_saturation_handoff_needed",
)

DECISION_REQUIREMENTS = (
    "exact boundary required",
    "allowed file list required before mutation",
    "lockouts must be preserved",
    "accepted facts and inference must remain separated",
    "validation plan required before commit",
    "push requires separate authorization",
    "capsule/export/package refresh requires separate authorization",
    "runtime/provider/model/platform work requires separate authorization",
    "service/API/UI/dashboard/auth/deployment work requires separate authorization",
    "worker dispatch requires separate explicit worker boundary",
    "patch application requires separate explicit patch boundary",
    "context saturation requires handoff rather than scope expansion",
)

STOP_CONDITIONS = (
    "missing boundary",
    "missing allowlist",
    "requested out-of-allowlist mutation",
    "requested runtime/provider/model/platform execution",
    "requested service/API/UI/dashboard/auth/deployment work",
    "requested general_answer resumption",
    "requested worker dispatch without worker boundary",
    "requested patch application without patch boundary",
    "proof overclaim",
    "source/capsule/Git truth conflation",
    "context saturation/handoff needed",
)

FALSE_ACTIVITY_FLAGS = {
    "runtime_provider_model_platform_executed": False,
    "service_api_ui_dashboard_auth_deployment_work": False,
    "general_answer_resumed": False,
    "worker_dispatched": False,
    "patch_applied": False,
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
    "operator decision readback is not task execution",
    "decision state is not live enforcement",
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

NEXT_SAFE_SEAM_DOCTRINE = (
    "operator decision/readback may precede later routing but proves no routing",
    "operator decision/readback may precede later patch workflow but proves no patch workflow",
    "operator decision/readback may precede later worker dispatch but proves no worker dispatch",
    "operator decision/readback may precede later provider policy but proves no provider policy",
    "operator decision/readback may precede later domain-general intake but proves no domain-general intake",
)

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

FORBIDDEN_SURFACE_CAVEATS = (
    "does_not_create_cli_parser_runner_dispatcher_behavior",
    "does_not_create_service_api_ui_dashboard_auth_deployment_behavior",
    "does_not_parse_live_packets",
    "does_not_execute_live_tasks",
    "does_not_dispatch_workers",
    "does_not_apply_patches",
    "does_not_resume_general_answer",
    "does_not_extend_official_capsule_proof_beyond_phase_335",
)


def read_product_task_packet_operator_decision_readback() -> dict[str, Any]:
    """Return deterministic source-level decision/readback data for task packets."""
    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_basis": {
            "phase_349": {
                "phase": PHASE_349,
                "source_file": PHASE_349_SOURCE,
                "marker": PHASE_349_MARKER,
            },
            "phase_351": {
                "phase": PHASE_351,
                "source_file": PHASE_351_SOURCE,
                "marker": PHASE_351_MARKER,
            },
        },
        "decision_surface_purpose": (
            "Operator decision/readback surface for product task packets; "
            "it is not live execution authority."
        ),
        "allowed_operator_decisions": list(ALLOWED_OPERATOR_DECISIONS),
        "decision_requirements": list(DECISION_REQUIREMENTS),
        "stop_conditions": list(STOP_CONDITIONS),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "required_report_caveats": list(REQUIRED_REPORT_CAVEATS),
        "source_capsule_git_truth_separation": dict(
            SOURCE_CAPSULE_GIT_TRUTH_SEPARATION
        ),
        "next_safe_seam_doctrine": list(NEXT_SAFE_SEAM_DOCTRINE),
        "lockout_text": list(LOCKOUT_TEXT),
        "forbidden_surface_caveats": list(FORBIDDEN_SURFACE_CAVEATS),
    }
