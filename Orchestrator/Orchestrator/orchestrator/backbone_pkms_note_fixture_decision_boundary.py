from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.backbone_pkms_note_fixture_mapping import (
    PKMS_NOTE_FIXTURE_RECOMMENDED_NEXT_BOUNDARY,
    read_pkms_note_fixture_backbone_operator_readback,
)


PKMS_NOTE_FIXTURE_DECISION_BOUNDARY = (
    "PHASE328_BACKBONE_PKMS_NOTE_OPERATION_FIXTURE_READBACK_DECISION_BOUNDARY_SOURCE_TEST_DOCS"
)

PKMS_NOTE_FIXTURE_ALLOWED_NEXT_BOUNDARIES = (
    PKMS_NOTE_FIXTURE_RECOMMENDED_NEXT_BOUNDARY,
)

PKMS_NOTE_FIXTURE_BLOCKED_DECISIONS = (
    "declare_backbone_v0",
    "create_backbone_v0_criteria",
    "execute_adapters",
    "access_live_vault",
    "mutate_live_pkms_notes",
    "execute_real_domain_actions",
    "claim_backlink_frontmatter_correctness",
    "claim_semantic_correctness",
    "claim_production_readiness",
    "claim_autonomous_ai_coding",
    "claim_provider_model_runtime_platform_execution",
    "claim_service_api_ui_dashboard_auth_deployment",
    "resume_general_answer",
    "generate_official_capsule_without_authorization",
)

PKMS_NOTE_FIXTURE_REASON_CODES = {
    "backbone_v0_not_declared": "backbone_v0_not_declared",
    "backbone_v0_criteria_not_authorized": "backbone_v0_criteria_not_authorized",
    "adapter_execution_disabled": "adapter_execution_disabled",
    "live_vault_access_not_allowed": "live_vault_access_not_allowed",
    "live_pkms_mutation_not_allowed": "live_pkms_mutation_not_allowed",
    "real_domain_execution_not_allowed": "real_domain_execution_not_allowed",
    "backlink_frontmatter_correctness_not_proven": (
        "backlink_frontmatter_correctness_not_proven"
    ),
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
    "criteria_readiness_assessment_next": "criteria_readiness_assessment_next",
}


@dataclass(frozen=True)
class PkmsNoteFixtureDecision:
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


def assess_pkms_note_fixture_decision_boundary() -> dict[str, Any]:
    readback = read_pkms_note_fixture_backbone_operator_readback()
    return {
        "pkms_note_fixture_decision_boundary": True,
        "active_boundary": PKMS_NOTE_FIXTURE_DECISION_BOUNDARY,
        "source_readback": "read_pkms_note_fixture_backbone_operator_readback",
        "bounded_context": readback["bounded_context"],
        "mapping_complete": readback["status_counts"]["incomplete"] == 0,
        "backbone_v0_declared": readback["backbone_v0_declared"],
        "adapter_execution_allowed": readback["adapter_execution_allowed"],
        "live_vault_access_allowed": readback["live_vault_access_allowed"],
        "note_mutation_allowed": readback["note_mutation_allowed"],
        "real_backlink_frontmatter_correctness_proven": readback[
            "real_backlink_frontmatter_correctness_proven"
        ],
        "allowed_next_moves": [
            PkmsNoteFixtureDecision(
                decision="multi_fixture_criteria_readiness_assessment",
                status="future_read_only",
                reason_code=PKMS_NOTE_FIXTURE_REASON_CODES[
                    "criteria_readiness_assessment_next"
                ],
                note=(
                    "Assess criteria readiness after code-patching, research-claim, "
                    "and PKMS fixture mappings; do not declare Backbone V0."
                ),
            ).as_dict()
        ],
        "allowed_next_boundaries": list(PKMS_NOTE_FIXTURE_ALLOWED_NEXT_BOUNDARIES),
        "blocked_decisions": [
            decision.as_dict() for decision in _blocked_decisions()
        ],
        "reason_codes": sorted(PKMS_NOTE_FIXTURE_REASON_CODES.values()),
        "non_proofs": list(readback["non_proofs"]),
        "recommended_next_boundary": PKMS_NOTE_FIXTURE_RECOMMENDED_NEXT_BOUNDARY,
        "official_capsule_proof_current": False,
        "semantic_correctness_claimed": False,
        "production_readiness_claimed": False,
        "provider_model_runtime_platform_execution_claimed": False,
        "autonomous_ai_coding_claimed": False,
        "service_api_ui_dashboard_auth_deployment_claimed": False,
        "caveats": [
            "Phase 328 consumes static readback only.",
            "Backbone V0 criteria remain outside this mutating phase.",
            "Backbone V0 declaration remains blocked.",
        ],
    }


def read_pkms_note_fixture_decision_boundary_status() -> dict[str, Any]:
    return assess_pkms_note_fixture_decision_boundary()


def _blocked_decisions() -> tuple[PkmsNoteFixtureDecision, ...]:
    reason_by_decision = {
        "declare_backbone_v0": "backbone_v0_not_declared",
        "create_backbone_v0_criteria": "backbone_v0_criteria_not_authorized",
        "execute_adapters": "adapter_execution_disabled",
        "access_live_vault": "live_vault_access_not_allowed",
        "mutate_live_pkms_notes": "live_pkms_mutation_not_allowed",
        "execute_real_domain_actions": "real_domain_execution_not_allowed",
        "claim_backlink_frontmatter_correctness": (
            "backlink_frontmatter_correctness_not_proven"
        ),
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
        PkmsNoteFixtureDecision(
            decision=decision,
            status="blocked",
            reason_code=PKMS_NOTE_FIXTURE_REASON_CODES[reason_by_decision[decision]],
            note=f"{decision} is outside the Phase 328 PKMS fixture boundary.",
        )
        for decision in PKMS_NOTE_FIXTURE_BLOCKED_DECISIONS
    )
