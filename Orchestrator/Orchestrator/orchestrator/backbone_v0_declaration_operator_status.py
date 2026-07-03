"""Operator-facing readback for the Backbone V0 declaration."""

from __future__ import annotations

from typing import Any

from orchestrator.backbone_v0_declaration import (
    read_backbone_v0_declaration_status,
)


PHASE = 338
BOUNDARY = "PHASE338_BACKBONE_V0_DECLARATION_READBACK_OPERATOR_STATUS_SOURCE_TEST_DOCS"
MARKER = (
    "PHASE338_BACKBONE_V0_DECLARATION_READBACK_OPERATOR_STATUS_SOURCE_TEST_DOCS_PROVEN=PASS"
)
SOURCE_OF_TRUTH = "orchestrator.backbone_v0_declaration.read_backbone_v0_declaration_status"

OPERATOR_SUMMARY = (
    "Backbone V0 is declared only as a narrow source/test/docs structural "
    "milestone for Orchestrator's domain-neutral control-loop architecture."
)

OPERATOR_CAVEATS = (
    "does_not_prove_semantic_correctness",
    "does_not_prove_production_readiness",
    "does_not_prove_autonomous_ai_coding",
    "does_not_prove_provider_model_runtime_platform_execution",
    "does_not_prove_service_api_ui_dashboard_auth_deployment_readiness",
    "does_not_prove_live_obsidian_pkms_business_data_access",
    "does_not_prove_live_business_data_access",
    "does_not_prove_real_domain_execution",
    "does_not_prove_adapter_execution",
    "does_not_treat_fixture_mappings_as_live_integrations",
    "does_not_resume_general_answer",
    "does_not_prove_openclaw_hermes_lightrag_discord_installer_behavior",
    "does_not_complete_future_phases",
    "does_not_extend_official_capsule_proof_beyond_phase_335_record",
)

GIT_REF_PRESERVATION_STATUS = {
    "local_refs_independently_verified": True,
    "verified_target_commit": "12e70023d638c0f919aa8e00e50ceccfaf36a6de",
    "local_tag": "backbone-v0-structural-declaration",
    "local_tag_points_to": "12e70023d638c0f919aa8e00e50ceccfaf36a6de",
    "local_branch": "fork/backbone-v0-structural-declaration",
    "local_branch_points_to": "12e70023d638c0f919aa8e00e50ceccfaf36a6de",
    "verification_commands": (
        "git rev-parse refs/tags/backbone-v0-structural-declaration^{}",
        "git rev-parse refs/heads/fork/backbone-v0-structural-declaration",
    ),
    "remote_refs_independently_verified": False,
    "remote_ref_status": "not_independently_verified",
}


def read_backbone_v0_declaration_operator_status() -> dict[str, Any]:
    """Return deterministic operator-facing status for Backbone V0."""
    declaration = read_backbone_v0_declaration_status()
    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_of_truth": SOURCE_OF_TRUTH,
        "backbone_v0_declared": declaration["backbone_v0_declared"],
        "declaration_boundary": declaration["boundary"],
        "declaration_marker": declaration["marker"],
        "declared_claim": declaration["declared_claim"],
        "declaration_scope": list(declaration["declaration_scope"]),
        "accepted_proof_markers": list(declaration["accepted_proof_markers"]),
        "official_capsule_proof": dict(declaration["official_capsule_proof"]),
        "non_proofs": list(declaration["non_proofs"]),
        "forbidden_claims": list(declaration["forbidden_claims"]),
        "execution_flags": dict(declaration["execution_flags"]),
        "operator_summary": OPERATOR_SUMMARY,
        "operator_caveats": list(OPERATOR_CAVEATS),
        "git_ref_preservation_status": {
            **GIT_REF_PRESERVATION_STATUS,
            "verification_commands": list(
                GIT_REF_PRESERVATION_STATUS["verification_commands"]
            ),
        },
    }
