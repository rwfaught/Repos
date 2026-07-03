from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.backbone_code_patching_adapter_mapping import (
    read_code_patching_backbone_operator_readback,
)
from orchestrator.backbone_control_loop import (
    BACKBONE_V0_DECLARED,
    read_backbone_scaffold_status,
)
from orchestrator.backbone_mapping_operator_decision_boundary import (
    assess_backbone_mapping_operator_decision_boundary,
)
from orchestrator.backbone_pkms_note_fixture_decision_boundary import (
    assess_pkms_note_fixture_decision_boundary,
)
from orchestrator.backbone_pkms_note_fixture_mapping import (
    read_pkms_note_fixture_backbone_operator_readback,
)
from orchestrator.backbone_research_claim_fixture_decision_boundary import (
    assess_research_claim_fixture_decision_boundary,
)
from orchestrator.backbone_research_claim_fixture_mapping import (
    read_research_claim_fixture_backbone_operator_readback,
)


BACKBONE_V0_CRITERIA_STATUS = "backbone_v0_criteria_defined_not_declared"
BACKBONE_V0_CRITERIA_RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE332_BACKBONE_V0_CRITERIA_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS"
)
OFFICIAL_CLEAN_CAPSULE_REQUIRED = True

BACKBONE_V0_CRITERIA_NON_PROOFS = (
    "criteria_do_not_declare_backbone_v0",
    "criteria_do_not_prove_semantic_correctness",
    "criteria_do_not_prove_production_readiness",
    "criteria_do_not_prove_autonomous_ai_coding",
    "criteria_do_not_prove_provider_model_runtime_platform_execution",
    "criteria_do_not_prove_service_api_ui_dashboard_auth_deployment",
    "criteria_do_not_prove_live_obsidian_vault_access",
    "criteria_do_not_prove_live_pkms_mutation",
    "criteria_do_not_prove_live_business_data_mutation",
    "criteria_do_not_prove_real_domain_execution",
    "criteria_do_not_include_official_clean_capsule_proof",
)

BACKBONE_V0_DECLARATION_BLOCKERS = (
    "backbone_v0_declaration_boundary_not_authorized",
    "official_clean_capsule_proof_missing",
    "semantic_correctness_not_proven",
    "production_readiness_not_proven",
)

BACKBONE_V0_CRITERIA_VALID = "criteria_valid"
BACKBONE_V0_CRITERIA_INVALID = "criteria_invalid"

BACKBONE_V0_CRITERIA_REASON_CODES = {
    "missing_scaffold_evidence": "missing_scaffold_evidence",
    "missing_mapped_context": "missing_mapped_context",
    "missing_non_patch_fixture": "missing_non_patch_fixture",
    "missing_negative_edge_coverage": "missing_negative_edge_coverage",
    "missing_readback_decision_boundary": "missing_readback_decision_boundary",
    "backbone_v0_declaration_claim_rejected": "backbone_v0_declaration_claim_rejected",
    "semantic_correctness_claim_rejected": "semantic_correctness_claim_rejected",
    "production_readiness_claim_rejected": "production_readiness_claim_rejected",
    "provider_model_runtime_claim_rejected": "provider_model_runtime_claim_rejected",
    "real_domain_execution_claim_rejected": "real_domain_execution_claim_rejected",
    "official_capsule_claim_rejected": "official_capsule_claim_rejected",
    "fixture_live_integration_claim_rejected": "fixture_live_integration_claim_rejected",
}

_FORBIDDEN_TRUE_CLAIM_REASON_FIELDS = {
    "backbone_v0_declared": "backbone_v0_declaration_claim_rejected",
    "backbone_v0_declaration_allowed_now": "backbone_v0_declaration_claim_rejected",
    "semantic_correctness_claimed": "semantic_correctness_claim_rejected",
    "production_readiness_claimed": "production_readiness_claim_rejected",
    "provider_model_runtime_platform_execution_claimed": (
        "provider_model_runtime_claim_rejected"
    ),
    "provider_model_runtime_claimed": "provider_model_runtime_claim_rejected",
    "real_domain_execution_claimed": "real_domain_execution_claim_rejected",
    "real_domain_action_executed": "real_domain_execution_claim_rejected",
    "official_capsule_generated": "official_capsule_claim_rejected",
    "official_capsule_proof_current": "official_capsule_claim_rejected",
    "fixture_mapping_treated_as_live_integration": (
        "fixture_live_integration_claim_rejected"
    ),
    "live_fixture_integration_claimed": "fixture_live_integration_claim_rejected",
}


@dataclass(frozen=True)
class BackboneV0Criterion:
    criterion_id: str
    description: str
    satisfied: bool
    evidence: tuple[str, ...]
    missing: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "description": self.description,
            "satisfied": self.satisfied,
            "evidence": list(self.evidence),
            "missing": list(self.missing),
        }


def evaluate_backbone_v0_criteria(
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selected_evidence = (
        read_current_backbone_v0_criteria_evidence()
        if evidence is None
        else dict(evidence)
    )
    criteria = _criteria_from_evidence(selected_evidence)
    satisfied_count = sum(1 for criterion in criteria if criterion.satisfied)
    missing_requirements = [
        missing
        for criterion in criteria
        for missing in criterion.missing
        if missing
    ]
    return {
        "backbone_v0_criteria_evaluation": True,
        "criteria_status": BACKBONE_V0_CRITERIA_STATUS,
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "criteria_count": len(criteria),
        "satisfied_criteria_count": satisfied_count,
        "unsatisfied_criteria_count": len(criteria) - satisfied_count,
        "criteria": [criterion.as_dict() for criterion in criteria],
        "all_criteria_satisfied_for_definition": satisfied_count == len(criteria),
        "declaration_allowed_now": False,
        "declaration_blockers": list(BACKBONE_V0_DECLARATION_BLOCKERS),
        "official_clean_capsule_required_before_declaration": (
            OFFICIAL_CLEAN_CAPSULE_REQUIRED
        ),
        "official_capsule_proof_current": False,
        "missing_requirements": missing_requirements,
        "non_proofs": list(BACKBONE_V0_CRITERIA_NON_PROOFS),
        "recommended_next_boundary": BACKBONE_V0_CRITERIA_RECOMMENDED_NEXT_BOUNDARY,
    }


def read_current_backbone_v0_criteria_evidence() -> dict[str, Any]:
    scaffold = read_backbone_scaffold_status()
    code_patching = read_code_patching_backbone_operator_readback()
    code_patching_decision = assess_backbone_mapping_operator_decision_boundary()
    research_claim = read_research_claim_fixture_backbone_operator_readback()
    research_claim_decision = assess_research_claim_fixture_decision_boundary()
    pkms_note = read_pkms_note_fixture_backbone_operator_readback()
    pkms_note_decision = assess_pkms_note_fixture_decision_boundary()
    return {
        "scaffold": scaffold,
        "mapped_contexts": {
            "code_patching": code_patching,
            "research_claim_packet_fixture": research_claim,
            "pkms_note_operation_fixture": pkms_note,
        },
        "decision_boundaries": {
            "code_patching": code_patching_decision,
            "research_claim_packet_fixture": research_claim_decision,
            "pkms_note_operation_fixture": pkms_note_decision,
        },
        "negative_edge_contexts": {
            "code_patching": True,
            "research_claim_packet_fixture": True,
            "pkms_note_operation_fixture": True,
        },
        "official_capsule_proof_current": False,
    }


def validate_backbone_v0_criteria_evidence(
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selected_evidence = (
        read_current_backbone_v0_criteria_evidence()
        if evidence is None
        else dict(evidence)
    )
    reason_code = _first_criteria_evidence_reason(selected_evidence)
    status = BACKBONE_V0_CRITERIA_INVALID if reason_code else BACKBONE_V0_CRITERIA_VALID
    return {
        "backbone_v0_criteria_evidence_validation": True,
        "status": status,
        "valid": status == BACKBONE_V0_CRITERIA_VALID,
        "reason_code": reason_code,
        "possible_reason_codes": sorted(BACKBONE_V0_CRITERIA_REASON_CODES.values()),
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "declaration_allowed_now": False,
        "non_proofs": list(BACKBONE_V0_CRITERIA_NON_PROOFS),
    }


def _criteria_from_evidence(evidence: dict[str, Any]) -> tuple[BackboneV0Criterion, ...]:
    scaffold = dict(evidence.get("scaffold") or {})
    mapped_contexts = dict(evidence.get("mapped_contexts") or {})
    decision_boundaries = dict(evidence.get("decision_boundaries") or {})
    negative_edge_contexts = dict(evidence.get("negative_edge_contexts") or {})
    real_contexts = [
        name for name in mapped_contexts if name == "code_patching"
    ]
    non_patch_contexts = [
        name for name in mapped_contexts if name != "code_patching"
    ]
    ordered_contexts = [
        name
        for name, readback in mapped_contexts.items()
        if _readback_has_ordered_complete_mapping(dict(readback))
    ]
    readback_contexts = [
        name for name, readback in mapped_contexts.items() if dict(readback)
    ]
    decision_contexts = [
        name
        for name, decision in decision_boundaries.items()
        if dict(decision).get("mapping_complete") is True
        or name == "code_patching"
    ]
    adapter_disabled_contexts = [
        name
        for name, readback in mapped_contexts.items()
        if dict(readback).get("adapter_execution_allowed") is False
    ]
    no_real_domain_contexts = [
        name
        for name, readback in mapped_contexts.items()
        if dict(readback).get("real_domain_action_executed") is not True
    ]
    non_proof_contexts = [
        name for name, readback in mapped_contexts.items() if dict(readback).get("non_proofs")
    ]
    criteria = (
        _criterion(
            "domain_neutral_scaffold_exists",
            "Domain-neutral Backbone scaffold exists.",
            scaffold.get("backbone_v0_declared") is False
            and bool(scaffold.get("ordered_stage_names")),
            ("read_backbone_scaffold_status",),
            "domain-neutral scaffold evidence missing",
        ),
        _criterion(
            "real_product_bounded_context_mapping_exists",
            "At least one existing real product bounded context mapping exists.",
            bool(real_contexts),
            tuple(real_contexts),
            "real product bounded context mapping missing",
        ),
        _criterion(
            "two_non_patch_fixture_mappings_exist",
            "At least two static non-patch fixture bounded-context mappings exist.",
            len(non_patch_contexts) >= 2,
            tuple(non_patch_contexts),
            "two non-patch fixture mappings required",
        ),
        _criterion(
            "ordered_stage_mapping_coverage",
            "Each mapped context has ordered stage mapping coverage.",
            set(ordered_contexts) == set(mapped_contexts) and bool(mapped_contexts),
            tuple(ordered_contexts),
            "ordered stage mapping coverage missing",
        ),
        _criterion(
            "negative_edge_handling",
            "Each mapped context has negative-edge handling.",
            set(negative_edge_contexts) >= set(mapped_contexts) and bool(mapped_contexts),
            tuple(sorted(negative_edge_contexts)),
            "negative-edge handling missing",
        ),
        _criterion(
            "operator_readback_exists",
            "Each mapped context has operator readback.",
            set(readback_contexts) == set(mapped_contexts) and bool(mapped_contexts),
            tuple(readback_contexts),
            "operator readback missing",
        ),
        _criterion(
            "decision_boundary_assessment_exists",
            "Each mapped context has decision-boundary assessment.",
            set(decision_contexts) == set(mapped_contexts) and bool(mapped_contexts),
            tuple(decision_contexts),
            "decision-boundary assessment missing",
        ),
        _criterion(
            "declaration_separate_from_criteria",
            "Backbone V0 declaration remains separate from criteria definition.",
            BACKBONE_V0_DECLARED is False,
            ("BACKBONE_V0_DECLARED=False",),
            "criteria attempted to declare Backbone V0",
        ),
        _criterion(
            "non_proofs_preserved",
            "Non-proofs are preserved.",
            set(non_proof_contexts) == set(mapped_contexts) and bool(mapped_contexts),
            tuple(non_proof_contexts),
            "non-proofs missing",
        ),
        _criterion(
            "adapter_execution_disabled",
            "Adapter execution remains disabled unless explicitly authorized later.",
            set(adapter_disabled_contexts) == set(mapped_contexts) and bool(mapped_contexts),
            tuple(adapter_disabled_contexts),
            "adapter execution disabled evidence missing",
        ),
        _criterion(
            "fixtures_do_not_imply_real_domain_execution",
            "Real domain execution is not implied by fixture mappings.",
            set(no_real_domain_contexts) == set(mapped_contexts) and bool(mapped_contexts),
            tuple(no_real_domain_contexts),
            "real domain execution non-proof missing",
        ),
        _criterion(
            "official_clean_capsule_required",
            "Official clean capsule proof is required before declaration/export claims.",
            OFFICIAL_CLEAN_CAPSULE_REQUIRED
            and evidence.get("official_capsule_proof_current") is False,
            ("official_capsule_proof_current=False",),
            "official clean capsule requirement missing",
        ),
        _criterion(
            "semantic_and_production_not_implied",
            "Semantic correctness and production readiness are not implied.",
            True,
            ("semantic_correctness_not_proven", "production_readiness_not_proven"),
            "semantic or production non-proof missing",
        ),
    )
    return criteria


def _first_criteria_evidence_reason(evidence: dict[str, Any]) -> str:
    claim_reason = _forbidden_claim_reason(evidence)
    if claim_reason:
        return claim_reason
    scaffold = dict(evidence.get("scaffold") or {})
    if not scaffold or not scaffold.get("ordered_stage_names"):
        return BACKBONE_V0_CRITERIA_REASON_CODES["missing_scaffold_evidence"]
    mapped_contexts = dict(evidence.get("mapped_contexts") or {})
    if "code_patching" not in mapped_contexts:
        return BACKBONE_V0_CRITERIA_REASON_CODES["missing_mapped_context"]
    non_patch_contexts = [name for name in mapped_contexts if name != "code_patching"]
    if len(non_patch_contexts) < 2:
        return BACKBONE_V0_CRITERIA_REASON_CODES["missing_non_patch_fixture"]
    negative_edge_contexts = set(dict(evidence.get("negative_edge_contexts") or {}))
    if not negative_edge_contexts >= set(mapped_contexts):
        return BACKBONE_V0_CRITERIA_REASON_CODES["missing_negative_edge_coverage"]
    decision_boundaries = dict(evidence.get("decision_boundaries") or {})
    if set(decision_boundaries) != set(mapped_contexts):
        return BACKBONE_V0_CRITERIA_REASON_CODES[
            "missing_readback_decision_boundary"
        ]
    for name, readback in mapped_contexts.items():
        readback_data = dict(readback)
        if not _readback_has_ordered_complete_mapping(readback_data):
            return BACKBONE_V0_CRITERIA_REASON_CODES["missing_readback_decision_boundary"]
        nested_claim_reason = _forbidden_claim_reason(readback_data)
        if nested_claim_reason:
            return nested_claim_reason
        if name != "code_patching" and readback_data.get("live_vault_accessed") is True:
            return BACKBONE_V0_CRITERIA_REASON_CODES[
                "fixture_live_integration_claim_rejected"
            ]
    return ""


def _forbidden_claim_reason(data: dict[str, Any]) -> str:
    for field_name, reason_code in _FORBIDDEN_TRUE_CLAIM_REASON_FIELDS.items():
        if data.get(field_name) is True:
            return BACKBONE_V0_CRITERIA_REASON_CODES[reason_code]
    return ""


def _criterion(
    criterion_id: str,
    description: str,
    satisfied: bool,
    evidence: tuple[str, ...],
    missing_message: str,
) -> BackboneV0Criterion:
    return BackboneV0Criterion(
        criterion_id=criterion_id,
        description=description,
        satisfied=satisfied,
        evidence=evidence,
        missing=() if satisfied else (missing_message,),
    )


def _readback_has_ordered_complete_mapping(readback: dict[str, Any]) -> bool:
    status_counts = dict(readback.get("status_counts") or {})
    return (
        bool(readback.get("mapped_stage_names"))
        and readback.get("mapped_stage_names") == readback.get("expected_backbone_stage_names")
        and status_counts.get("incomplete") == 0
        and readback.get("backbone_v0_declared") is False
    )
