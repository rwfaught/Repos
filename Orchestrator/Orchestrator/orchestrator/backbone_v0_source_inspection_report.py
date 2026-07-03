"""Pure source-level inspection report for Backbone V0 state."""

from __future__ import annotations

from typing import Any

from orchestrator.backbone_v0_declaration import (
    read_backbone_v0_declaration_status,
)
from orchestrator.backbone_v0_declaration_operator_status import (
    read_backbone_v0_declaration_operator_status,
)
from orchestrator.backbone_v0_proof_chain_operator_index import (
    read_backbone_v0_proof_chain_operator_index,
)


PHASE = 342
BOUNDARY = "PHASE342_BACKBONE_V0_SOURCE_INSPECTION_REPORT_SURFACE_SOURCE_TEST_DOCS"
MARKER = (
    "PHASE342_BACKBONE_V0_SOURCE_INSPECTION_REPORT_SURFACE_SOURCE_TEST_DOCS_PROVEN=PASS"
)

PHASE_337_FORK_POINT_COMMIT = "12e70023d638c0f919aa8e00e50ceccfaf36a6de"
PHASE_338_COMMIT = "3d322fcb7d04ca8655d4234816a990e4ea6d24cb"
PHASE_340_COMMIT = "e629a49920d6933dba5c95c952e353955fc71e4f"

PHASE_335_CAPSULE_CAVEAT = (
    "This is only the accepted Phase 335 official clean capsule proof "
    "reference; Phase 342 does not refresh capsules, exports, or packages."
)

OPERATOR_INSPECTION_SUMMARY = (
    "Phase 342 is a pure source/test/docs report surface over the existing "
    "Backbone V0 declaration, declaration operator status, and proof-chain "
    "operator index. It is not a second declaration and not a replacement for "
    "the Phase 340 proof-chain operator index."
)

REPORT_SURFACE_SCOPE = {
    "report_surface_only": True,
    "second_declaration": False,
    "phase_340_replacement": False,
    "runtime_execution": False,
    "provider_execution": False,
    "model_execution": False,
    "platform_execution": False,
    "git_execution": False,
    "file_read_execution": False,
    "subprocess_execution": False,
    "service_api_ui_dashboard_auth_deployment_behavior": False,
    "general_answer_resumption": False,
}

NEXT_OPERATOR_CAVEATS = (
    "source_inspection_report_only",
    "does_not_expand_product_capability",
    "does_not_execute_git_files_subprocesses_or_environment_access",
    "does_not_execute_runtime_provider_model_platform_paths",
    "does_not_create_cli_service_api_ui_dashboard_auth_or_deployment_behavior",
    "does_not_resume_general_answer",
    "does_not_refresh_capsules_exports_or_packages",
    "does_not_replace_phase_340_operator_index",
)


def _all_flags_false(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def _source_surface_status(
    name: str,
    source: str,
    report: dict[str, Any],
    expected_marker: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "source": source,
        "present": True,
        "marker": report["marker"],
        "expected_marker": expected_marker,
        "expected_marker_preserved": report["marker"] == expected_marker,
        "expected_non_proofs_preserved": bool(report["non_proofs"]),
        "execution_flags_remain_false": _all_flags_false(report["execution_flags"]),
    }


def read_backbone_v0_source_inspection_report() -> dict[str, Any]:
    """Return a deterministic source-level report over existing Backbone V0 data."""
    declaration = read_backbone_v0_declaration_status()
    operator_status = read_backbone_v0_declaration_operator_status()
    proof_chain_index = read_backbone_v0_proof_chain_operator_index()

    source_surfaces = [
        _source_surface_status(
            "Backbone V0 declaration",
            "orchestrator.backbone_v0_declaration.read_backbone_v0_declaration_status",
            declaration,
            "PHASE337_BACKBONE_V0_DECLARATION_SOURCE_TEST_DOCS_PROVEN=PASS",
        ),
        _source_surface_status(
            "Backbone V0 declaration operator status",
            (
                "orchestrator.backbone_v0_declaration_operator_status."
                "read_backbone_v0_declaration_operator_status"
            ),
            operator_status,
            (
                "PHASE338_BACKBONE_V0_DECLARATION_READBACK_OPERATOR_STATUS_"
                "SOURCE_TEST_DOCS_PROVEN=PASS"
            ),
        ),
        _source_surface_status(
            "Backbone V0 proof-chain operator index",
            (
                "orchestrator.backbone_v0_proof_chain_operator_index."
                "read_backbone_v0_proof_chain_operator_index"
            ),
            proof_chain_index,
            "PHASE340_BACKBONE_V0_PROOF_CHAIN_OPERATOR_INDEX_SOURCE_TEST_DOCS_PROVEN=PASS",
        ),
    ]

    execution_flags = {
        **proof_chain_index["execution_flags"],
        "git_execution_occurred": False,
        "file_read_execution_occurred": False,
        "subprocess_execution_occurred": False,
        "service_api_ui_dashboard_auth_deployment_work_occurred": False,
    }

    return {
        "phase": PHASE,
        "boundary": BOUNDARY,
        "marker": MARKER,
        "source_surfaces_inspected": source_surfaces,
        "accepted_commit_reference_facts": {
            "phase_337_fork_point_commit": PHASE_337_FORK_POINT_COMMIT,
            "phase_338_commit": PHASE_338_COMMIT,
            "phase_340_commit": PHASE_340_COMMIT,
        },
        "preserved_markers": {
            "phase_337_marker": declaration["marker"],
            "phase_338_marker": operator_status["marker"],
            "phase_340_marker": proof_chain_index["marker"],
        },
        "phase_335_capsule_proof_reference": {
            "reference": dict(proof_chain_index["phase_335_official_clean_capsule_proof"]),
            "caveat": PHASE_335_CAPSULE_CAVEAT,
        },
        "ordered_proof_chain_phase_summary": list(
            proof_chain_index["ordered_proof_chain_phases"]
        ),
        "read_only_assessment_phase_summary": list(
            proof_chain_index["read_only_assessment_phases"]
        ),
        "operator_facing_inspection_summary": OPERATOR_INSPECTION_SUMMARY,
        "source_capsule_git_truth_separation_caveat": dict(
            proof_chain_index["source_capsule_separation_caveat"]
        ),
        "non_proofs": list(proof_chain_index["non_proofs"]),
        "forbidden_claims": list(proof_chain_index["forbidden_claims"]),
        "execution_flags": execution_flags,
        "next_operator_caveats": list(NEXT_OPERATOR_CAVEATS),
        "report_surface_scope": dict(REPORT_SURFACE_SCOPE),
    }
