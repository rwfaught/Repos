"""Pure operator report data for product task packets."""

from __future__ import annotations

from typing import Any


PHASE = 349
BOUNDARY = "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS"
MARKER = (
    "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS_PROVEN=PASS"
)

PHASE_347_MARKER = (
    "PHASE347_CODEX_BOUNDED_WORKER_PACKET_OPERATOR_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
)
PHASE_348_BOUNDARY = (
    "PHASE348_POST_BACKBONE_V0_PRODUCT_CAPABILITY_SEAM_SELECTION_READONLY"
)

PRODUCT_TASK_PACKET_FIELDS = (
    "task_packet_id",
    "boundary",
    "mode",
    "operator_intent",
    "accepted_facts",
    "inference",
    "allowed_files",
    "lockouts",
    "validation_plan",
    "stop_conditions",
    "report_metadata",
    "non_proofs_to_preserve",
)

REPORT_SECTIONS = (
    "Assessment",
    "Accepted Facts",
    "Decision",
    "NBM",
    "Deliverable/Command",
    "RESPONSE_METADATA",
)

READBACK_DEPENDENCIES = (
    "Phase 347 bounded Codex worker packet operator readback",
    "Phase 348 post-Backbone V0 read-only seam selection",
)

STANDING_LOCKOUTS = (
    "No runtime/provider/model/platform execution.",
    "No WSL/Ollama/OpenClaw/Hermes/LightRAG/Discord/installer execution.",
    "No service/API/UI/dashboard/auth/deployment work.",
    "No general_answer resumption.",
    "No Source Files refresh, capsule refresh, export/package refresh, or official capsule proof extension.",
    "No semantic-correctness, autonomous-AI-coding, live-domain-execution, or production-readiness claims.",
    "No unrelated files.",
)

NON_PROOFS = (
    "not_semantic_correctness",
    "not_production_readiness",
    "not_autonomous_ai_coding",
    "not_provider_model_runtime_platform_execution",
    "not_service_api_ui_dashboard_auth_deployment_readiness",
    "not_live_obsidian_pkms_business_data_access",
    "not_live_mutation",
    "not_adapter_execution",
    "not_real_domain_execution",
    "not_fixture_mapping_as_live_integration",
    "not_general_answer_resumption",
    "not_openclaw_hermes_lightrag_discord_installer_behavior",
    "not_future_phase_completion",
    "not_official_capsule_proof_beyond_phase_335",
)

FALSE_ACTIVITY_FLAGS = {
    "task_created": False,
    "task_mutated": False,
    "task_executed": False,
    "worker_dispatched": False,
    "codex_agent_executed": False,
    "provider_model_runtime_platform_execution": False,
    "wsl_ollama_openclaw_hermes_lightrag_discord_installer_execution": False,
    "service_api_ui_dashboard_auth_deployment_behavior": False,
    "general_answer_resumed": False,
    "source_files_capsule_export_package_refreshed": False,
    "semantic_correctness_claimed": False,
    "production_readiness_claimed": False,
    "autonomous_ai_coding_claimed": False,
    "live_domain_execution_claimed": False,
}

NEXT_OPERATOR_CAVEATS = (
    "operator_report_surface_only",
    "not_a_parser_runner_dispatcher_cli_service_or_live_worker_harness",
    "does_not_create_or_execute_product_tasks",
    "does_not_grant_mutation_authority_outside_future_allowed_files",
    "requires_separate_boundary_for_runtime_provider_model_platform_execution",
    "requires_separate_boundary_for_capsule_export_package_work",
    "requires_separate_boundary_for_push",
)


def read_product_task_packet_operator_report() -> dict[str, Any]:
    """Return deterministic source-level report data for product task packets."""
    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_basis": {
            "phase_347_marker": PHASE_347_MARKER,
            "phase_348_boundary": PHASE_348_BOUNDARY,
            "dependencies": list(READBACK_DEPENDENCIES),
        },
        "surface_purpose": (
            "Make product task packets inspectable as operator report artifacts "
            "without executing tasks, dispatching workers, or crossing runtime boundaries."
        ),
        "product_task_packet_fields": list(PRODUCT_TASK_PACKET_FIELDS),
        "report_sections": list(REPORT_SECTIONS),
        "accepted_fact_inference_separation": {
            "accepted_facts_required": True,
            "inference_must_be_marked": True,
            "worker_report_is_not_coordinator_acceptance": True,
            "test_pass_is_not_semantic_correctness": True,
        },
        "operator_legibility": {
            "nbm_required": True,
            "decision_required": True,
            "deliverable_or_command_required": True,
            "response_metadata_required": True,
            "changed_files_must_match_allowed_files": True,
        },
        "standing_lockouts": list(STANDING_LOCKOUTS),
        "validation_expectations": (
            "git status --short --branch",
            "python -m py_compile orchestrator/product_task_packet_operator_report.py",
            "python -m unittest tests.test_phase_349_product_task_packet_operator_report_surface",
            "marker search",
            "non-proof and lockout text search",
            "git diff --check",
            "changed-file allowlist audit",
        ),
        "false_activity_flags": dict(FALSE_ACTIVITY_FLAGS),
        "non_proofs": list(NON_PROOFS),
        "source_capsule_git_truth_separation_caveat": {
            "Git repo truth": "current tracked source state in the repository",
            "Source Files handoff snapshots": "orientation artifacts that may include generated entries or lag Git truth",
            "official clean product capsule proofs": "separate clean capsule records; Phase 335 remains the accepted official proof",
            "full Git repo backups including .git": "backup artifacts, not official clean product capsules",
        },
        "next_operator_caveats": list(NEXT_OPERATOR_CAVEATS),
    }
