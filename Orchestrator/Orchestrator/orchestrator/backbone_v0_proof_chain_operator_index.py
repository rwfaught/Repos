"""Deterministic operator index for the Backbone V0 proof chain."""

from __future__ import annotations

from typing import Any

from orchestrator.backbone_v0_declaration import (
    read_backbone_v0_declaration_status,
)
from orchestrator.backbone_v0_declaration_operator_status import (
    read_backbone_v0_declaration_operator_status,
)


PHASE = 340
BOUNDARY = "PHASE340_BACKBONE_V0_PROOF_CHAIN_OPERATOR_INDEX_SOURCE_TEST_DOCS"
MARKER = (
    "PHASE340_BACKBONE_V0_PROOF_CHAIN_OPERATOR_INDEX_SOURCE_TEST_DOCS_PROVEN=PASS"
)

PHASE_337_FORK_POINT_COMMIT = "12e70023d638c0f919aa8e00e50ceccfaf36a6de"
PHASE_338_COMMIT = "3d322fcb7d04ca8655d4234816a990e4ea6d24cb"

ORDERED_PROOF_CHAIN_PHASES = (
    (316, "neutral Backbone scaffold"),
    (317, "code-patching Backbone mapping"),
    (318, "code-patching negative-edge hardening"),
    (319, "code-patching operator readback/runbook"),
    (320, "code-patching operator decision boundary"),
    (322, "static research/intelligence claim fixture mapping"),
    (323, "research fixture negative-edge hardening"),
    (324, "research fixture readback/decision boundary"),
    (326, "static PKMS note-operation fixture mapping"),
    (327, "PKMS fixture negative-edge hardening"),
    (328, "PKMS fixture readback/decision boundary"),
    (331, "Backbone V0 criteria scaffold"),
    (332, "criteria negative-edge hardening"),
    (333, "criteria readback/operator decision boundary"),
    (335, "official clean capsule proof"),
    (337, "Backbone V0 declaration"),
    (338, "Backbone V0 declaration operator status"),
    (340, "Backbone V0 proof-chain operator index"),
)

READ_ONLY_ASSESSMENT_PHASES = (321, 325, 329, 330, 334, 336, 339)

OPERATOR_CAVEATS = (
    "operator_index_only",
    "source_test_docs_orientation_only",
    "does_not_expand_product_capability",
    "does_not_execute_runtime_provider_model_platform_paths",
    "does_not_resume_general_answer",
    "does_not_refresh_capsules_exports_or_packages",
)

SOURCE_CAPSULE_SEPARATION_CAVEAT = {
    "git_repo_truth": "Current source truth lives in the Git repository.",
    "source_files_handoff_snapshots": (
        "Source Files handoff snapshots are orientation artifacts and may lag "
        "the Git repository."
    ),
    "official_clean_product_capsule_proofs": (
        "Official clean product capsule proof remains limited to the accepted "
        "Phase 335 record unless a later boundary refreshes it."
    ),
    "full_git_repo_backups_including_git": (
        "Full Git repo backups including .git are separate preservation "
        "artifacts, not the Phase 335 clean capsule proof."
    ),
}

EXECUTION_FLAGS = {
    "runtime_execution_occurred": False,
    "provider_execution_occurred": False,
    "model_execution_occurred": False,
    "platform_execution_occurred": False,
    "service_api_ui_dashboard_auth_deployment_ready": False,
    "semantic_correctness_claimed": False,
    "production_readiness_claimed": False,
    "autonomous_ai_coding_claimed": False,
    "adapter_execution_allowed": False,
    "real_domain_execution_claimed": False,
    "general_answer_resumed": False,
    "capsule_export_package_refreshed": False,
}


def _proof_chain_entries() -> list[dict[str, Any]]:
    return [
        {"phase": phase, "description": description}
        for phase, description in ORDERED_PROOF_CHAIN_PHASES
    ]


def read_backbone_v0_proof_chain_operator_index() -> dict[str, Any]:
    """Return a deterministic source/test/docs index for Backbone V0 proof facts."""
    declaration = read_backbone_v0_declaration_status()
    operator_status = read_backbone_v0_declaration_operator_status()

    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "declaration_boundary": declaration["boundary"],
        "declaration_marker": declaration["marker"],
        "phase_337_fork_point_commit": PHASE_337_FORK_POINT_COMMIT,
        "phase_338_boundary": operator_status["boundary"],
        "phase_338_marker": operator_status["marker"],
        "phase_338_commit": PHASE_338_COMMIT,
        "phase_335_official_clean_capsule_proof": dict(
            declaration["official_capsule_proof"]
        ),
        "accepted_proof_markers": list(declaration["accepted_proof_markers"]),
        "ordered_proof_chain_phases": _proof_chain_entries(),
        "read_only_assessment_phases": list(READ_ONLY_ASSESSMENT_PHASES),
        "non_proofs": list(declaration["non_proofs"]),
        "forbidden_claims": list(declaration["forbidden_claims"]),
        "execution_flags": dict(EXECUTION_FLAGS),
        "operator_caveats": list(OPERATOR_CAVEATS),
        "source_capsule_separation_caveat": dict(SOURCE_CAPSULE_SEPARATION_CAVEAT),
    }
