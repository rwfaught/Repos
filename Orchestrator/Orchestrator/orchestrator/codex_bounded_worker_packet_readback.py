"""Pure readback data for bounded Codex worker packet governance."""

from __future__ import annotations

from typing import Any


PHASE = 347
BOUNDARY = "PHASE347_CODEX_BOUNDED_WORKER_PACKET_OPERATOR_READBACK_SOURCE_TEST_DOCS"
MARKER = (
    "PHASE347_CODEX_BOUNDED_WORKER_PACKET_OPERATOR_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
)

PHASE_345_MARKER = (
    "PHASE345_CODEX_BOUNDED_AUTONOMY_PROMPT_SURFACE_DOCS_ONLY_PROVEN=PASS"
)

REQUIRED_PACKET_FIELDS = (
    "SESSION ROLE",
    "BOUNDARY",
    "PURPOSE",
    "ACTIVE CONTEXT",
    "AUTHORITY",
    "ALLOWED FILES",
    "LOCKOUTS",
    "REQUIRED DESIGN",
    "TEST/DOC REQUIREMENTS",
    "VALIDATION COMMAND BATCH REQUIREMENT",
    "CHANGED-FILE ALLOWLIST AUDIT",
    "COMMIT AUTHORIZATION",
    "PUSH AUTHORIZATION",
    "STOP CONDITIONS",
    "REPORT FORMAT",
)

BOUNDARY_MODES = (
    "read-only",
    "docs-only mutation",
    "source/test/docs mutation",
    "ref-only preservation",
    "push/ref verification",
)

STANDING_LOCKOUTS = (
    "No runtime/provider/model/platform execution.",
    "No WSL/Ollama/OpenClaw/Hermes/LightRAG/Discord/installer execution.",
    "No service/API/UI/dashboard/auth/deployment work.",
    "No general_answer resumption.",
    "No Source Files refresh, capsule refresh, export/package refresh, or official capsule proof extension unless explicitly listed.",
    "No semantic-correctness, autonomous-AI-coding, live-domain-execution, or production-readiness claims.",
    "No unrelated files.",
)

NON_PROOF_DOCTRINE = (
    "worker PASS is evidence, not coordinator ratification",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "fixture is not live integration",
    "readback/report surface is not runtime behavior",
    "Codex bounded work is not autonomous AI coding",
)

NEXT_OPERATOR_CAVEATS = (
    "readback_surface_only",
    "not_a_parser_runner_dispatcher_cli_service_or_live_worker_harness",
    "does_not_grant_coordinator_authority_to_codex",
    "does_not_execute_codex_or_worker_agents",
    "requires_separate_boundary_for_push",
    "requires_separate_boundary_for_capsule_export_package_work",
    "requires_separate_boundary_for_runtime_provider_model_platform_execution",
)


def read_codex_bounded_worker_packet_operator_readback() -> dict[str, Any]:
    """Return deterministic source-level readback for bounded worker packets."""
    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_basis": {
            "phase": 345,
            "document": "docs/CODEX_BOUNDED_AUTONOMY_PROMPT_SURFACE.md",
            "marker": PHASE_345_MARKER,
        },
        "packet_purpose": (
            "Bounded worker packets are inspectable control artifacts, "
            "not autonomous authority."
        ),
        "role_separation": {
            "roger_owner_operator": "approves direction and accepts or rejects results",
            "cto_coordinator_protocol_keeper": (
                "sets boundaries, reviews evidence, ratifies results, and selects next moves"
            ),
            "codex_bounded_worker": "works only inside the authorized packet boundary",
            "relay_operator_command_batches": (
                "execution surfaces when a boundary requires command transfer"
            ),
        },
        "required_packet_fields": list(REQUIRED_PACKET_FIELDS),
        "boundary_modes": list(BOUNDARY_MODES),
        "mutation_authority_rules": {
            "allowed_files_named_before_mutation": True,
            "local_commit_requires_explicit_authorization": True,
            "local_commit_requires_passing_validation": True,
            "push_requires_separate_authorization_unless_explicitly_included": True,
            "capsule_export_package_requires_separate_authorization": True,
            "runtime_provider_model_platform_execution_requires_separate_authorization": True,
        },
        "timestamp_rule": {
            "command_script_batches_require_start_timestamp": True,
            "command_script_batches_require_end_timestamp": True,
            "command_script_batches_require_elapsed_time": True,
        },
        "validation_expectations": (
            "targeted compile/check commands when source changes are authorized",
            "targeted unit tests when test/source changes are authorized",
            "marker search",
            "changed-file allowlist audit",
            "git diff --check",
            "git status --short --branch",
        ),
        "report_shapes": {
            "mutation_report_fields": (
                "BOUNDARY",
                "CHANGED FILES",
                "IMPLEMENTATION SUMMARY",
                "VALIDATION",
                "COMMIT",
                "GIT STATUS",
                "NON-PROOFS PRESERVED",
                "CAVEATS",
                "NEXT RECOMMENDED BOUNDARY",
            ),
            "read_only_assessment_report_fields": (
                "BOUNDARY",
                "INSPECTED SOURCES",
                "OBSERVED CURRENT STATE",
                "ASSESSMENT ANSWERS",
                "CANDIDATE BOUNDARY RANKING",
                "RECOMMENDED NEXT BOUNDARY",
                "NO CHANGES MADE CONFIRMATION",
                "RESPONSE_METADATA",
            ),
            "push_ref_verification_report_fields": (
                "BOUNDARY",
                "REFS VERIFIED",
                "REMOTE STATUS",
                "PUSH RESULT",
                "NON-PROOFS PRESERVED",
                "CAVEATS",
            ),
        },
        "standing_lockouts": list(STANDING_LOCKOUTS),
        "non_proof_doctrine": list(NON_PROOF_DOCTRINE),
        "false_execution_flags": {
            "runtime_provider_model_platform_execution": False,
            "service_api_ui_dashboard_auth_deployment": False,
            "general_answer_resumed": False,
            "live_integration": False,
            "capsule_export_package_refreshed": False,
            "autonomous_coding_authority": False,
            "codex_agent_execution": False,
            "worker_dispatch": False,
            "parser_runner_dispatcher_cli_service_harness": False,
            "production_readiness": False,
            "semantic_correctness": False,
        },
        "source_capsule_git_truth_separation_caveat": {
            "Git repo truth": "current tracked source state in the repository",
            "Source Files handoff snapshots": "orientation artifacts that may lag Git truth",
            "official clean product capsule proofs": (
                "separately generated and inspected capsule records"
            ),
            "full Git repo backups including .git": (
                "backup artifacts, not equivalent to official clean product capsules"
            ),
        },
        "next_operator_caveats": list(NEXT_OPERATOR_CAVEATS),
    }
