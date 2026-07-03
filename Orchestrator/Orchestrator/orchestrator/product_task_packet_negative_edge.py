"""Pure negative-edge contract data for product task packets."""

from __future__ import annotations

from typing import Any


PHASE = 351
BOUNDARY = "PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS"
MARKER = (
    "PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS"
)

PHASE_349 = 349
PHASE_349_SOURCE = "orchestrator/product_task_packet_operator_report.py"
PHASE_349_MARKER = (
    "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS_PROVEN=PASS"
)

DISALLOWED_PACKET_CLAIMS = (
    "semantic correctness proven",
    "production readiness proven",
    "autonomous AI coding authority granted",
    "runtime/provider/model/platform execution occurred",
    "service/API/UI/dashboard/auth/deployment readiness proven",
    "live Obsidian/PKMS/business-data access occurred",
    "live mutation occurred",
    "adapter execution occurred",
    "real domain execution occurred",
    "fixture mapping is live integration",
    "general_answer resumed",
    "OpenClaw/Hermes/LightRAG/Discord/installer behavior proven",
    "official capsule proof extended beyond Phase 335",
)

DISALLOWED_PACKET_ACTIONS = (
    "execute runtime/provider/model/platform paths",
    "run WSL/Ollama/OpenClaw/Hermes/LightRAG/Discord/installer work",
    "resume general_answer",
    "create service/API/UI/dashboard/auth/deployment work",
    "dispatch workers",
    "apply patches",
    "mutate files without exact allowlist",
    "commit without validation",
    "push without separate authorization",
    "refresh capsule/export/package without separate authorization",
    "broaden into unrelated files or cleanup",
)

REQUIRED_STOP_CONDITIONS = (
    "missing exact boundary",
    "missing allowed-file list for mutation",
    "requested mutation outside allowlist",
    "requested runtime/provider/model/platform execution",
    "requested service/API/UI/dashboard/auth/deployment work",
    "requested general_answer resumption",
    "requested worker dispatch without explicit worker boundary",
    "requested patch application without explicit patch boundary",
    "requested capsule/export/package refresh",
    "claimed proof exceeds inspected evidence",
    "output blurs accepted facts and inference",
)

REQUIRED_FALSE_FLAGS = {
    "runtime_provider_model_platform_executed": False,
    "service_api_ui_dashboard_auth_deployment_work": False,
    "general_answer_resumed": False,
    "live_business_data_access": False,
    "live_mutation": False,
    "adapter_execution": False,
    "real_domain_execution": False,
    "fixture_as_live_integration": False,
    "production_readiness_proven": False,
    "semantic_correctness_proven": False,
    "autonomous_ai_coding_authority": False,
    "capsule_export_package_refreshed": False,
}

REQUIRED_REPORT_CAVEATS = (
    "worker PASS is evidence, not coordinator ratification",
    "test PASS is not semantic correctness",
    "pushed commit is not production readiness",
    "fixture is not live integration",
    "readback/report surface is not runtime behavior",
    "product task packet is not task execution",
    "negative-edge contract is not live enforcement",
    "Git repo truth is distinct from Source Files handoff snapshots",
    "official clean capsule proof remains separate",
)

NEXT_SAFE_SEAM_DOCTRINE = (
    "negative-edge hardening should precede operator decision/readback",
    "negative-edge hardening should precede routing",
    "negative-edge hardening should precede patch workflow",
    "negative-edge hardening should precede worker dispatch",
    "negative-edge hardening should precede provider policy",
    "negative-edge hardening should precede domain-general intake",
)

FORBIDDEN_SURFACE_CAVEATS = (
    "not_a_validator_parser_dispatcher_runner_cli_service_or_live_task_harness",
    "does_not_parse_live_packets",
    "does_not_validate_live_tasks",
    "does_not_create_or_execute_product_tasks",
    "does_not_dispatch_workers",
    "does_not_apply_patches",
)


def read_product_task_packet_negative_edge_contract() -> dict[str, Any]:
    """Return deterministic source-level negative-edge data for task packets."""
    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_basis": {
            "phase": PHASE_349,
            "source_file": PHASE_349_SOURCE,
            "marker": PHASE_349_MARKER,
        },
        "purpose": (
            "deterministic negative-edge contract for product task packets"
        ),
        "contract_posture": (
            "product task packets are inspectable planning/report artifacts, "
            "not execution authority"
        ),
        "disallowed_packet_claims": list(DISALLOWED_PACKET_CLAIMS),
        "disallowed_packet_actions": list(DISALLOWED_PACKET_ACTIONS),
        "required_stop_conditions": list(REQUIRED_STOP_CONDITIONS),
        "required_false_flags": dict(REQUIRED_FALSE_FLAGS),
        "required_report_caveats": list(REQUIRED_REPORT_CAVEATS),
        "source_capsule_git_truth_separation_caveat": {
            "Git repo truth": "current tracked source state in the repository",
            "Source Files handoff snapshots": (
                "orientation artifacts that may lag Git truth or include generated entries"
            ),
            "official clean product capsule proofs": (
                "separate clean capsule records; Phase 335 remains the accepted official proof"
            ),
            "full Git repo backups including .git": (
                "backup artifacts, not official clean product capsules"
            ),
        },
        "next_safe_seam_doctrine": list(NEXT_SAFE_SEAM_DOCTRINE),
        "forbidden_surface_caveats": list(FORBIDDEN_SURFACE_CAVEATS),
    }
