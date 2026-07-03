from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.backbone_v0_criteria import (
    BACKBONE_V0_CRITERIA_READBACK_RECOMMENDED_NEXT_BOUNDARY,
    read_backbone_v0_criteria_operator_readback,
)


BACKBONE_V0_CRITERIA_DECISION_BOUNDARY = (
    "PHASE333_BACKBONE_V0_CRITERIA_READBACK_OPERATOR_DECISION_BOUNDARY_SOURCE_TEST_DOCS"
)

BACKBONE_V0_CRITERIA_BLOCKED_DECISIONS = (
    "declare_backbone_v0",
    "claim_semantic_correctness",
    "claim_production_readiness",
    "claim_autonomous_ai_coding",
    "claim_provider_model_runtime_platform_execution",
    "claim_service_api_ui_dashboard_auth_deployment",
    "access_live_obsidian_vault",
    "mutate_live_pkms",
    "mutate_live_business_data",
    "execute_real_domain_actions",
    "execute_adapters",
    "generate_official_capsule_without_authorization",
)

BACKBONE_V0_CRITERIA_DEFERRED_DECISIONS = (
    "backbone_v0_declaration",
    "official_declaration_export_or_capsule_claim",
)

BACKBONE_V0_CRITERIA_ALLOWED_NEXT_DECISIONS = (
    "read_only_declaration_readiness_assessment",
)

BACKBONE_V0_CRITERIA_REASON_CODES = {
    "backbone_v0_not_declared": "backbone_v0_not_declared",
    "semantic_correctness_not_proven": "semantic_correctness_not_proven",
    "production_readiness_not_proven": "production_readiness_not_proven",
    "autonomous_ai_coding_not_proven": "autonomous_ai_coding_not_proven",
    "provider_model_runtime_platform_not_executed": (
        "provider_model_runtime_platform_not_executed"
    ),
    "service_api_ui_dashboard_auth_deployment_not_proven": (
        "service_api_ui_dashboard_auth_deployment_not_proven"
    ),
    "live_obsidian_vault_access_not_allowed": (
        "live_obsidian_vault_access_not_allowed"
    ),
    "live_pkms_mutation_not_allowed": "live_pkms_mutation_not_allowed",
    "live_business_data_mutation_not_allowed": (
        "live_business_data_mutation_not_allowed"
    ),
    "real_domain_execution_not_allowed": "real_domain_execution_not_allowed",
    "adapter_execution_disabled": "adapter_execution_disabled",
    "official_capsule_not_authorized": "official_capsule_not_authorized",
    "declaration_readiness_assessment_next": (
        "declaration_readiness_assessment_next"
    ),
    "official_capsule_required_before_declaration": (
        "official_capsule_required_before_declaration"
    ),
}


@dataclass(frozen=True)
class BackboneV0CriteriaDecision:
    decision: str
    status: str
    reason_code: str
    note: str

    def as_dict(self) -> dict[str, str]:
        return {
            "decision": self.decision,
            "status": self.status,
            "reason_code": self.reason_code,
            "note": self.note,
        }


def assess_backbone_v0_criteria_decision_boundary() -> dict[str, Any]:
    readback = read_backbone_v0_criteria_operator_readback()
    return {
        "backbone_v0_criteria_decision_boundary": True,
        "active_boundary": BACKBONE_V0_CRITERIA_DECISION_BOUNDARY,
        "source_readback": "read_backbone_v0_criteria_operator_readback",
        "criteria_count": readback["criteria_count"],
        "all_criteria_satisfied_for_definition": readback[
            "current_satisfaction_status"
        ]["all_criteria_satisfied_for_definition"],
        "missing_requirements": list(readback["missing_requirements"]),
        "backbone_v0_declared": readback["backbone_v0_declared"],
        "backbone_v0_declaration_allowed_now": readback[
            "backbone_v0_declaration_allowed_now"
        ],
        "blocked_decisions": [
            decision.as_dict() for decision in _blocked_decisions()
        ],
        "deferred_decisions": [
            BackboneV0CriteriaDecision(
                decision=decision,
                status="deferred",
                reason_code=(
                    BACKBONE_V0_CRITERIA_REASON_CODES[
                        "official_capsule_required_before_declaration"
                    ]
                    if decision == "official_declaration_export_or_capsule_claim"
                    else BACKBONE_V0_CRITERIA_REASON_CODES["backbone_v0_not_declared"]
                ),
                note=f"{decision} requires a later explicit boundary.",
            ).as_dict()
            for decision in BACKBONE_V0_CRITERIA_DEFERRED_DECISIONS
        ],
        "allowed_next_decisions": [
            BackboneV0CriteriaDecision(
                decision=decision,
                status="future_read_only",
                reason_code=BACKBONE_V0_CRITERIA_REASON_CODES[
                    "declaration_readiness_assessment_next"
                ],
                note="Assess declaration readiness without declaring Backbone V0.",
            ).as_dict()
            for decision in BACKBONE_V0_CRITERIA_ALLOWED_NEXT_DECISIONS
        ],
        "non_proofs": list(readback["non_proofs"]),
        "official_capsule_proof_current": readback["official_capsule_proof_current"],
        "semantic_correctness_claimed": False,
        "production_readiness_claimed": False,
        "provider_model_runtime_platform_execution_claimed": False,
        "service_api_ui_dashboard_auth_deployment_claimed": False,
        "recommended_next_boundary": (
            BACKBONE_V0_CRITERIA_READBACK_RECOMMENDED_NEXT_BOUNDARY
        ),
        "caveats": [
            "Phase 333 consumes static criteria readback only.",
            "Criteria satisfaction is not Backbone V0 declaration.",
            "Official clean capsule proof remains a future requirement.",
        ],
    }


def read_backbone_v0_criteria_decision_boundary_status() -> dict[str, Any]:
    return assess_backbone_v0_criteria_decision_boundary()


def _blocked_decisions() -> tuple[BackboneV0CriteriaDecision, ...]:
    reason_by_decision = {
        "declare_backbone_v0": "backbone_v0_not_declared",
        "claim_semantic_correctness": "semantic_correctness_not_proven",
        "claim_production_readiness": "production_readiness_not_proven",
        "claim_autonomous_ai_coding": "autonomous_ai_coding_not_proven",
        "claim_provider_model_runtime_platform_execution": (
            "provider_model_runtime_platform_not_executed"
        ),
        "claim_service_api_ui_dashboard_auth_deployment": (
            "service_api_ui_dashboard_auth_deployment_not_proven"
        ),
        "access_live_obsidian_vault": "live_obsidian_vault_access_not_allowed",
        "mutate_live_pkms": "live_pkms_mutation_not_allowed",
        "mutate_live_business_data": "live_business_data_mutation_not_allowed",
        "execute_real_domain_actions": "real_domain_execution_not_allowed",
        "execute_adapters": "adapter_execution_disabled",
        "generate_official_capsule_without_authorization": (
            "official_capsule_not_authorized"
        ),
    }
    return tuple(
        BackboneV0CriteriaDecision(
            decision=decision,
            status="blocked",
            reason_code=BACKBONE_V0_CRITERIA_REASON_CODES[
                reason_by_decision[decision]
            ],
            note=f"{decision} is outside the Phase 333 criteria boundary.",
        )
        for decision in BACKBONE_V0_CRITERIA_BLOCKED_DECISIONS
    )
