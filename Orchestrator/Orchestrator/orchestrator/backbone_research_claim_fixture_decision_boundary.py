from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.backbone_research_claim_fixture_mapping import (
    RESEARCH_CLAIM_FIXTURE_RECOMMENDED_NEXT_BOUNDARY_AFTER_STOP,
    read_research_claim_fixture_backbone_operator_readback,
)


RESEARCH_CLAIM_FIXTURE_DECISION_BOUNDARY = (
    "PHASE324_BACKBONE_NON_PATCH_FIXTURE_READBACK_DECISION_BOUNDARY_SOURCE_TEST_DOCS"
)

RESEARCH_CLAIM_FIXTURE_ALLOWED_NEXT_BOUNDARIES_AFTER_STOP = (
    RESEARCH_CLAIM_FIXTURE_RECOMMENDED_NEXT_BOUNDARY_AFTER_STOP,
)

RESEARCH_CLAIM_FIXTURE_BLOCKED_DECISIONS = (
    "declare_backbone_v0",
    "execute_adapters",
    "execute_real_domain_actions",
    "mutate_live_records",
    "claim_semantic_correctness",
    "claim_production_readiness",
    "claim_autonomous_ai_coding",
    "claim_provider_model_runtime_platform_execution",
    "claim_service_api_ui_dashboard_auth_deployment",
    "resume_general_answer",
    "generate_official_capsule_without_authorization",
)

RESEARCH_CLAIM_FIXTURE_REASON_CODES = {
    "backbone_v0_not_declared": "backbone_v0_not_declared",
    "adapter_execution_disabled": "adapter_execution_disabled",
    "real_domain_execution_not_allowed": "real_domain_execution_not_allowed",
    "live_record_mutation_not_allowed": "live_record_mutation_not_allowed",
    "semantic_correctness_not_proven": "semantic_correctness_not_proven",
    "production_readiness_not_proven": "production_readiness_not_proven",
    "autonomous_ai_coding_not_proven": "autonomous_ai_coding_not_proven",
    "provider_model_runtime_platform_not_executed": (
        "provider_model_runtime_platform_not_executed"
    ),
    "service_api_ui_dashboard_auth_deployment_not_proven": (
        "service_api_ui_dashboard_auth_deployment_not_proven"
    ),
    "general_answer_not_resumed": "general_answer_not_resumed",
    "official_capsule_not_authorized": "official_capsule_not_authorized",
    "campaign_stop_after_phase_324": "campaign_stop_after_phase_324",
}


@dataclass(frozen=True)
class ResearchClaimFixtureDecision:
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


def assess_research_claim_fixture_decision_boundary() -> dict[str, Any]:
    readback = read_research_claim_fixture_backbone_operator_readback()
    return {
        "research_claim_fixture_decision_boundary": True,
        "active_boundary": RESEARCH_CLAIM_FIXTURE_DECISION_BOUNDARY,
        "source_readback": "read_research_claim_fixture_backbone_operator_readback",
        "bounded_context": readback["bounded_context"],
        "mapping_complete": readback["status_counts"]["incomplete"] == 0,
        "backbone_v0_declared": readback["backbone_v0_declared"],
        "adapter_execution_allowed": readback["adapter_execution_allowed"],
        "real_domain_action_executed": readback["real_domain_action_executed"],
        "live_record_mutated": readback["live_record_mutated"],
        "allowed_next_moves_after_campaign_stop": [
            ResearchClaimFixtureDecision(
                decision="additional_non_patch_fixture_assessment",
                status="future_only",
                reason_code=RESEARCH_CLAIM_FIXTURE_REASON_CODES[
                    "campaign_stop_after_phase_324"
                ],
                note=(
                    "Campaign must stop after Phase 324; this boundary is a future "
                    "safe NBM, not current authorization."
                ),
            ).as_dict()
        ],
        "allowed_next_boundaries_after_campaign_stop": list(
            RESEARCH_CLAIM_FIXTURE_ALLOWED_NEXT_BOUNDARIES_AFTER_STOP
        ),
        "blocked_decisions": [
            decision.as_dict() for decision in _blocked_decisions()
        ],
        "reason_codes": sorted(RESEARCH_CLAIM_FIXTURE_REASON_CODES.values()),
        "non_proofs": list(readback["non_proofs"]),
        "campaign_stop_required_after_phase_324": True,
        "recommended_next_boundary_after_campaign_stop": (
            RESEARCH_CLAIM_FIXTURE_RECOMMENDED_NEXT_BOUNDARY_AFTER_STOP
        ),
        "official_capsule_proof_current": False,
        "semantic_correctness_claimed": False,
        "production_readiness_claimed": False,
        "provider_model_runtime_platform_execution_claimed": False,
        "autonomous_ai_coding_claimed": False,
        "service_api_ui_dashboard_auth_deployment_claimed": False,
        "caveats": [
            "Phase 324 consumes static readback only.",
            "Campaign stop is required after Phase 324.",
            "Backbone V0 declaration remains blocked.",
        ],
    }


def read_research_claim_fixture_decision_boundary_status() -> dict[str, Any]:
    return assess_research_claim_fixture_decision_boundary()


def _blocked_decisions() -> tuple[ResearchClaimFixtureDecision, ...]:
    reason_by_decision = {
        "declare_backbone_v0": "backbone_v0_not_declared",
        "execute_adapters": "adapter_execution_disabled",
        "execute_real_domain_actions": "real_domain_execution_not_allowed",
        "mutate_live_records": "live_record_mutation_not_allowed",
        "claim_semantic_correctness": "semantic_correctness_not_proven",
        "claim_production_readiness": "production_readiness_not_proven",
        "claim_autonomous_ai_coding": "autonomous_ai_coding_not_proven",
        "claim_provider_model_runtime_platform_execution": (
            "provider_model_runtime_platform_not_executed"
        ),
        "claim_service_api_ui_dashboard_auth_deployment": (
            "service_api_ui_dashboard_auth_deployment_not_proven"
        ),
        "resume_general_answer": "general_answer_not_resumed",
        "generate_official_capsule_without_authorization": (
            "official_capsule_not_authorized"
        ),
    }
    return tuple(
        ResearchClaimFixtureDecision(
            decision=decision,
            status="blocked",
            reason_code=RESEARCH_CLAIM_FIXTURE_REASON_CODES[reason_by_decision[decision]],
            note=f"{decision} is outside the Phase 324 fixture readback boundary.",
        )
        for decision in RESEARCH_CLAIM_FIXTURE_BLOCKED_DECISIONS
    )
