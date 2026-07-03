from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.backbone_code_patching_adapter_mapping import (
    read_code_patching_backbone_operator_readback,
)


BACKBONE_MAPPING_OPERATOR_DECISION_BOUNDARY = (
    "PHASE320_BACKBONE_MAPPING_OPERATOR_DECISION_BOUNDARY_ASSESSMENT_SOURCE_TEST_DOCS"
)

BACKBONE_MAPPING_OPERATOR_RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE321_BACKBONE_NON_PATCH_FIXTURE_MAPPING_ASSESSMENT_READONLY"
)

BACKBONE_MAPPING_OPERATOR_ALLOWED_NEXT_BOUNDARIES = (
    BACKBONE_MAPPING_OPERATOR_RECOMMENDED_NEXT_BOUNDARY,
)

BACKBONE_MAPPING_OPERATOR_BLOCKED_DECISIONS = (
    "declare_backbone_v0",
    "execute_adapters",
    "migrate_patch_loop",
    "claim_semantic_correctness",
    "claim_production_readiness",
    "claim_autonomous_ai_coding",
    "claim_provider_model_runtime_platform_execution",
    "claim_service_api_ui_dashboard_auth_deployment",
    "resume_general_answer",
    "generate_official_capsule_without_authorization",
)

BACKBONE_MAPPING_OPERATOR_DEFERRED_DECISIONS = (
    "docs_only_backbone_v0_criteria_phase",
    "backbone_v0_declaration",
    "official_declaration_export_or_capsule_claim",
)

BACKBONE_MAPPING_OPERATOR_REASON_CODES = {
    "backbone_v0_not_declared": "backbone_v0_not_declared",
    "adapter_execution_disabled": "adapter_execution_disabled",
    "patch_loop_not_migrated": "patch_loop_not_migrated",
    "semantic_correctness_not_proven": "semantic_correctness_not_proven",
    "production_readiness_not_proven": "production_readiness_not_proven",
    "autonomous_ai_coding_not_proven": "autonomous_ai_coding_not_proven",
    "provider_model_runtime_platform_not_executed": (
        "provider_model_runtime_platform_not_executed"
    ),
    "service_api_ui_dashboard_auth_deployment_not_in_scope": (
        "service_api_ui_dashboard_auth_deployment_not_in_scope"
    ),
    "general_answer_not_resumed": "general_answer_not_resumed",
    "official_capsule_not_authorized": "official_capsule_not_authorized",
    "single_bounded_context_only": "single_bounded_context_only",
    "clean_capsule_required_before_declaration": (
        "clean_capsule_required_before_declaration"
    ),
    "non_patch_fixture_mapping_readonly_next": (
        "non_patch_fixture_mapping_readonly_next"
    ),
}


@dataclass(frozen=True)
class BackboneMappingOperatorDecision:
    decision: str
    status: str
    reason_code: str
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "status": self.status,
            "reason_code": self.reason_code,
            "notes": list(self.notes),
        }


def assess_backbone_mapping_operator_decision_boundary(
    readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_readback = (
        read_code_patching_backbone_operator_readback()
        if readback is None
        else dict(readback)
    )
    readback_complete = _readback_complete(source_readback)
    allowed_next_moves = (
        [
            BackboneMappingOperatorDecision(
                decision="cross_domain_fixture_mapping_proof_boundary",
                status="recommended",
                reason_code=BACKBONE_MAPPING_OPERATOR_REASON_CODES[
                    "non_patch_fixture_mapping_readonly_next"
                ],
                notes=(
                    "Use a read-only non-code-patching fixture assessment before any "
                    "Backbone V0 criteria or declaration boundary.",
                ),
            ).as_dict()
        ]
        if readback_complete
        else []
    )
    return {
        "backbone_mapping_operator_decision_boundary": True,
        "active_boundary": BACKBONE_MAPPING_OPERATOR_DECISION_BOUNDARY,
        "bounded_context": source_readback.get("bounded_context", ""),
        "source_readback_used": "read_code_patching_backbone_operator_readback",
        "source_readback_complete": readback_complete,
        "allowed_next_moves": allowed_next_moves,
        "allowed_next_boundaries": list(BACKBONE_MAPPING_OPERATOR_ALLOWED_NEXT_BOUNDARIES),
        "blocked_decisions": _blocked_decisions(),
        "deferred_decisions": _deferred_decisions(),
        "reason_codes": sorted(BACKBONE_MAPPING_OPERATOR_REASON_CODES.values()),
        "non_proofs": list(source_readback.get("non_proofs") or []),
        "backbone_v0_declared": False,
        "adapter_execution_allowed": False,
        "patch_loop_migrated": False,
        "official_clean_capsule_required_before_declaration": True,
        "official_capsule_proof_current": False,
        "recommended_next_boundary": BACKBONE_MAPPING_OPERATOR_RECOMMENDED_NEXT_BOUNDARY,
        "caveats": (
            "Phase 320 consumes static readback only.",
            "No adapters, patch-loop modules, providers, models, runtimes, or platforms are executed.",
            "Backbone V0 declaration remains blocked.",
        ),
    }


def read_backbone_mapping_operator_decision_boundary_status() -> dict[str, Any]:
    return assess_backbone_mapping_operator_decision_boundary()


def _blocked_decisions() -> list[dict[str, Any]]:
    reason_by_decision = {
        "declare_backbone_v0": "backbone_v0_not_declared",
        "execute_adapters": "adapter_execution_disabled",
        "migrate_patch_loop": "patch_loop_not_migrated",
        "claim_semantic_correctness": "semantic_correctness_not_proven",
        "claim_production_readiness": "production_readiness_not_proven",
        "claim_autonomous_ai_coding": "autonomous_ai_coding_not_proven",
        "claim_provider_model_runtime_platform_execution": (
            "provider_model_runtime_platform_not_executed"
        ),
        "claim_service_api_ui_dashboard_auth_deployment": (
            "service_api_ui_dashboard_auth_deployment_not_in_scope"
        ),
        "resume_general_answer": "general_answer_not_resumed",
        "generate_official_capsule_without_authorization": "official_capsule_not_authorized",
    }
    return [
        BackboneMappingOperatorDecision(
            decision=decision,
            status="blocked",
            reason_code=BACKBONE_MAPPING_OPERATOR_REASON_CODES[reason_by_decision[decision]],
        ).as_dict()
        for decision in BACKBONE_MAPPING_OPERATOR_BLOCKED_DECISIONS
    ]


def _deferred_decisions() -> list[dict[str, Any]]:
    return [
        BackboneMappingOperatorDecision(
            decision="docs_only_backbone_v0_criteria_phase",
            status="deferred",
            reason_code=BACKBONE_MAPPING_OPERATOR_REASON_CODES[
                "single_bounded_context_only"
            ],
            notes=(
                "Defer until at least one non-code-patching fixture or mapping proof exists.",
            ),
        ).as_dict(),
        BackboneMappingOperatorDecision(
            decision="backbone_v0_declaration",
            status="blocked",
            reason_code=BACKBONE_MAPPING_OPERATOR_REASON_CODES[
                "clean_capsule_required_before_declaration"
            ],
            notes=(
                "Any future declaration/export claim requires separate official clean capsule proof.",
            ),
        ).as_dict(),
        BackboneMappingOperatorDecision(
            decision="official_declaration_export_or_capsule_claim",
            status="deferred",
            reason_code=BACKBONE_MAPPING_OPERATOR_REASON_CODES[
                "clean_capsule_required_before_declaration"
            ],
            notes=(
                "Capsule proof is a future prerequisite, not current Phase 320 proof.",
            ),
        ).as_dict(),
    ]


def _readback_complete(readback: dict[str, Any]) -> bool:
    if readback.get("backbone_v0_declared") is True:
        return False
    if readback.get("adapter_execution_allowed") is True:
        return False
    if readback.get("patch_loop_migrated") is True:
        return False
    status_counts = dict(readback.get("status_counts") or {})
    return int(status_counts.get("incomplete") or 0) == 0 and bool(
        readback.get("non_proofs")
    )
