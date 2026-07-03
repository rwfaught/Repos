from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from orchestrator.backbone_control_loop import (
    BACKBONE_NATIVE_EVIDENCE_FIELDS,
    BACKBONE_V0_DECLARED,
    BackboneAdapterDescriptor,
    ordered_backbone_stage_names,
)


RESEARCH_CLAIM_FIXTURE_BOUNDED_CONTEXT = "research_claim_packet_fixture"
RESEARCH_CLAIM_FIXTURE_MAPPING_STATUS = (
    "research_claim_packet_fixture_mapped_to_backbone_scaffold_not_executed"
)
RESEARCH_CLAIM_FIXTURE_ADAPTER = BackboneAdapterDescriptor(
    adapter_name="research_claim_packet_fixture_backbone_mapping_adapter",
    bounded_context=RESEARCH_CLAIM_FIXTURE_BOUNDED_CONTEXT,
    execution_allowed=False,
)

RESEARCH_CLAIM_FIXTURE_NON_PROOFS = (
    "research_claim_fixture_mapping_is_not_semantic_correctness",
    "research_claim_fixture_mapping_is_not_production_readiness",
    "research_claim_fixture_mapping_is_not_autonomous_ai_coding",
    "research_claim_fixture_mapping_is_not_provider_model_runtime_platform_execution",
    "research_claim_fixture_mapping_does_not_declare_backbone_v0",
    "research_claim_fixture_mapping_does_not_execute_real_domain_actions",
    "research_claim_fixture_mapping_does_not_mutate_live_records",
    "research_claim_fixture_mapping_does_not_generate_official_capsule",
)

RESEARCH_CLAIM_FIXTURE_MAPPING_COMPLETE = "mapped"
RESEARCH_CLAIM_FIXTURE_MAPPING_INCOMPLETE = "incomplete"

RESEARCH_CLAIM_FIXTURE_REASON_CODES = {
    "stage_name_missing": "stage_name_missing",
    "unknown_stage_name": "unknown_stage_name",
    "bounded_context_missing": "bounded_context_missing",
    "fixture_source_missing": "fixture_source_missing",
    "fixture_doc_or_test_evidence_missing": "fixture_doc_or_test_evidence_missing",
    "stage_order_mismatch": "stage_order_mismatch",
    "backbone_v0_claim_rejected": "backbone_v0_claim_rejected",
    "adapter_execution_claim_rejected": "adapter_execution_claim_rejected",
    "real_domain_action_claim_rejected": "real_domain_action_claim_rejected",
    "official_capsule_claim_rejected": "official_capsule_claim_rejected",
    "fixture_specific_native_field_rejected": "fixture_specific_native_field_rejected",
}

RESEARCH_CLAIM_FIXTURE_SPECIFIC_FIELDS = (
    "fixture_packet_id",
    "claim_text",
    "claim_source_label",
    "fixture_operation",
    "fixture_confidence_label",
    "fixture_stage_role",
)

_FORBIDDEN_TRUE_CLAIM_REASON_FIELDS = {
    "backbone_v0_declared": "backbone_v0_claim_rejected",
    "adapter_execution_allowed": "adapter_execution_claim_rejected",
    "adapter_executed": "adapter_execution_claim_rejected",
    "real_domain_action_executed": "real_domain_action_claim_rejected",
    "live_record_mutated": "real_domain_action_claim_rejected",
    "official_capsule_generated": "official_capsule_claim_rejected",
    "semantic_correctness_claimed": "real_domain_action_claim_rejected",
    "production_readiness_claimed": "real_domain_action_claim_rejected",
}


@dataclass(frozen=True)
class ResearchClaimFixtureBackboneStageMapping:
    stage_name: str
    bounded_context: str = RESEARCH_CLAIM_FIXTURE_BOUNDED_CONTEXT
    fixture_sources: tuple[str, ...] = field(default_factory=tuple)
    phase_docs: tuple[str, ...] = field(default_factory=tuple)
    phase_tests: tuple[str, ...] = field(default_factory=tuple)
    mapping_note: str = ""
    reason_code: str = ""
    domain_payload: dict[str, Any] = field(default_factory=dict)
    non_proofs: tuple[str, ...] = RESEARCH_CLAIM_FIXTURE_NON_PROOFS

    def as_dict(self) -> dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "bounded_context": self.bounded_context,
            "fixture_sources": list(self.fixture_sources),
            "phase_docs": list(self.phase_docs),
            "phase_tests": list(self.phase_tests),
            "mapping_note": self.mapping_note,
            "reason_code": self.reason_code,
            "domain_payload": dict(self.domain_payload),
            "non_proofs": list(self.non_proofs),
            "backbone_native_evidence_fields": list(BACKBONE_NATIVE_EVIDENCE_FIELDS),
            "backbone_v0_declared": BACKBONE_V0_DECLARED,
            "adapter_execution_allowed": RESEARCH_CLAIM_FIXTURE_ADAPTER.execution_allowed,
            "real_domain_action_executed": False,
            "live_record_mutated": False,
        }


def _fixture_mapping(
    stage_name: str,
    fixture_stage_role: str,
    mapping_note: str,
) -> ResearchClaimFixtureBackboneStageMapping:
    return ResearchClaimFixtureBackboneStageMapping(
        stage_name=stage_name,
        fixture_sources=("fixtures/research_claim_packet/static_claim_packet.json",),
        phase_docs=("docs/PHASE_322.md",),
        phase_tests=("tests/test_phase_322_backbone_non_patch_fixture_mapping.py",),
        mapping_note=mapping_note,
        domain_payload={
            "fixture_packet_id": "static_research_claim_packet_fixture_001",
            "claim_text": "Fixture claim only; no semantic correctness asserted.",
            "claim_source_label": "static_fixture_source_label",
            "fixture_operation": "describe_only",
            "fixture_confidence_label": "not_evaluated",
            "fixture_stage_role": fixture_stage_role,
        },
    )


RESEARCH_CLAIM_FIXTURE_BACKBONE_STAGE_MAPPINGS = (
    _fixture_mapping("intake_result", "claim_packet_intake", "Static claim packet enters the fixture context."),
    _fixture_mapping("eligibility_record", "fixture_eligibility", "Fixture eligibility is described, not executed."),
    _fixture_mapping("candidate_artifact", "claim_candidate", "Claim candidate artifact remains fake fixture data."),
    _fixture_mapping("operator_decision", "operator_review_placeholder", "Operator decision is a placeholder mapping only."),
    _fixture_mapping("promotion_record", "promotion_placeholder", "Promotion record is static fixture linkage only."),
    _fixture_mapping("draft_action_proposal", "draft_note_operation_placeholder", "Draft action proposal is descriptive only."),
    _fixture_mapping("authorization_eligibility", "authorization_eligibility_placeholder", "Authorization eligibility is not live authority."),
    _fixture_mapping("authorization_record", "authorization_record_placeholder", "Authorization record is a fixture record only."),
    _fixture_mapping("bounded_action_attempt", "non_executed_fixture_attempt", "Bounded action attempt is explicitly not executed."),
    _fixture_mapping("action_result_evidence", "static_result_evidence", "Result evidence is reference-only fixture evidence."),
    _fixture_mapping("mechanical_verification", "mechanical_shape_check", "Mechanical verification is shape-only, not semantic."),
    _fixture_mapping("finalization_record", "fixture_finalization", "Finalization preserves caveats and non-proofs."),
    _fixture_mapping("readback", "fixture_readback", "Readback surfaces fixture status without Backbone V0."),
)


def ordered_research_claim_fixture_backbone_stage_mappings() -> tuple[
    ResearchClaimFixtureBackboneStageMapping, ...
]:
    return RESEARCH_CLAIM_FIXTURE_BACKBONE_STAGE_MAPPINGS


def validate_research_claim_fixture_backbone_stage_mapping(
    mapping: ResearchClaimFixtureBackboneStageMapping | dict[str, Any],
) -> dict[str, Any]:
    data = (
        mapping.as_dict()
        if isinstance(mapping, ResearchClaimFixtureBackboneStageMapping)
        else dict(mapping)
    )
    reason_code = _first_mapping_reason(data)
    status = (
        RESEARCH_CLAIM_FIXTURE_MAPPING_INCOMPLETE
        if reason_code
        else RESEARCH_CLAIM_FIXTURE_MAPPING_COMPLETE
    )
    return {
        "research_claim_fixture_backbone_stage_mapping_validation": True,
        "status": status,
        "complete": status == RESEARCH_CLAIM_FIXTURE_MAPPING_COMPLETE,
        "reason_code": reason_code,
        "stage_name": data.get("stage_name", ""),
        "bounded_context": data.get("bounded_context", ""),
        "fixture_sources": list(data.get("fixture_sources") or []),
        "phase_docs": list(data.get("phase_docs") or []),
        "phase_tests": list(data.get("phase_tests") or []),
        "domain_payload_keys": sorted(
            str(key) for key in dict(data.get("domain_payload") or {}).keys()
        ),
        "backbone_native_evidence_fields": list(BACKBONE_NATIVE_EVIDENCE_FIELDS),
        "fixture_specific_fields": list(RESEARCH_CLAIM_FIXTURE_SPECIFIC_FIELDS),
        "non_proofs": list(data.get("non_proofs") or RESEARCH_CLAIM_FIXTURE_NON_PROOFS),
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "adapter_execution_allowed": RESEARCH_CLAIM_FIXTURE_ADAPTER.execution_allowed,
        "real_domain_action_executed": False,
        "live_record_mutated": False,
    }


def validate_ordered_research_claim_fixture_backbone_stage_mappings(
    mappings: tuple[ResearchClaimFixtureBackboneStageMapping, ...] | list[Any] | None = None,
) -> dict[str, Any]:
    selected_mappings = list(
        ordered_research_claim_fixture_backbone_stage_mappings()
        if mappings is None
        else mappings
    )
    stage_names = [
        mapping.stage_name if isinstance(mapping, ResearchClaimFixtureBackboneStageMapping)
        else str(dict(mapping).get("stage_name") or "")
        for mapping in selected_mappings
    ]
    expected_stage_names = list(ordered_backbone_stage_names())
    validations = [
        validate_research_claim_fixture_backbone_stage_mapping(mapping)
        for mapping in selected_mappings
    ]
    order_reason = (
        RESEARCH_CLAIM_FIXTURE_REASON_CODES["stage_order_mismatch"]
        if stage_names != expected_stage_names
        else ""
    )
    incomplete_reason_codes = [
        validation["reason_code"] for validation in validations if validation["reason_code"]
    ]
    if order_reason:
        incomplete_reason_codes.append(order_reason)
    return {
        "research_claim_fixture_backbone_ordered_mapping_validation": True,
        "stage_names": stage_names,
        "expected_stage_names": expected_stage_names,
        "all_stage_names_match_backbone": not order_reason,
        "mapping_count": len(selected_mappings),
        "complete": not incomplete_reason_codes,
        "status": (
            RESEARCH_CLAIM_FIXTURE_MAPPING_COMPLETE
            if not incomplete_reason_codes
            else RESEARCH_CLAIM_FIXTURE_MAPPING_INCOMPLETE
        ),
        "reason_code": order_reason,
        "incomplete_reason_codes": incomplete_reason_codes,
        "non_proofs": list(RESEARCH_CLAIM_FIXTURE_NON_PROOFS),
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "adapter_execution_allowed": RESEARCH_CLAIM_FIXTURE_ADAPTER.execution_allowed,
        "real_domain_action_executed": False,
        "live_record_mutated": False,
    }


def read_research_claim_fixture_backbone_mapping_status(
    mappings: tuple[ResearchClaimFixtureBackboneStageMapping, ...] | list[Any] | None = None,
) -> dict[str, Any]:
    selected_mappings = list(
        ordered_research_claim_fixture_backbone_stage_mappings()
        if mappings is None
        else mappings
    )
    validations = [
        validate_research_claim_fixture_backbone_stage_mapping(mapping)
        for mapping in selected_mappings
    ]
    ordered_validation = validate_ordered_research_claim_fixture_backbone_stage_mappings(
        selected_mappings
    )
    return {
        "research_claim_fixture_backbone_mapping_status": RESEARCH_CLAIM_FIXTURE_MAPPING_STATUS,
        "bounded_context": RESEARCH_CLAIM_FIXTURE_BOUNDED_CONTEXT,
        "adapter": RESEARCH_CLAIM_FIXTURE_ADAPTER.as_dict(),
        "adapter_execution_allowed": RESEARCH_CLAIM_FIXTURE_ADAPTER.execution_allowed,
        "stage_names": ordered_validation["stage_names"],
        "expected_stage_names": list(ordered_backbone_stage_names()),
        "all_stage_names_match_backbone": ordered_validation["all_stage_names_match_backbone"],
        "mapping_count": len(selected_mappings),
        "incomplete_mapping_count": sum(
            1 for validation in validations if not validation["complete"]
        ),
        "complete": all(validation["complete"] for validation in validations)
        and ordered_validation["complete"],
        "incomplete_reason_codes": ordered_validation["incomplete_reason_codes"],
        "non_proofs": list(RESEARCH_CLAIM_FIXTURE_NON_PROOFS),
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "real_domain_action_executed": False,
        "live_record_mutated": False,
        "semantic_correctness_claimed": False,
        "production_readiness_claimed": False,
        "provider_model_runtime_platform_execution_claimed": False,
        "autonomous_ai_coding_claimed": False,
    }


def _first_mapping_reason(data: dict[str, Any]) -> str:
    stage_name = str(data.get("stage_name") or "").strip()
    if not stage_name:
        return RESEARCH_CLAIM_FIXTURE_REASON_CODES["stage_name_missing"]
    if stage_name not in ordered_backbone_stage_names():
        return RESEARCH_CLAIM_FIXTURE_REASON_CODES["unknown_stage_name"]
    if str(data.get("bounded_context") or "").strip() != RESEARCH_CLAIM_FIXTURE_BOUNDED_CONTEXT:
        return RESEARCH_CLAIM_FIXTURE_REASON_CODES["bounded_context_missing"]
    claim_reason = _forbidden_claim_reason(data)
    if claim_reason:
        return claim_reason
    native_leak_reason = _fixture_specific_native_field_reason(data)
    if native_leak_reason:
        return native_leak_reason
    if not data.get("fixture_sources"):
        return RESEARCH_CLAIM_FIXTURE_REASON_CODES["fixture_source_missing"]
    if not data.get("phase_docs") and not data.get("phase_tests"):
        return RESEARCH_CLAIM_FIXTURE_REASON_CODES[
            "fixture_doc_or_test_evidence_missing"
        ]
    return ""


def _forbidden_claim_reason(data: dict[str, Any]) -> str:
    for field_name, reason_code in _FORBIDDEN_TRUE_CLAIM_REASON_FIELDS.items():
        if data.get(field_name) is True:
            return RESEARCH_CLAIM_FIXTURE_REASON_CODES[reason_code]
    return ""


def _fixture_specific_native_field_reason(data: dict[str, Any]) -> str:
    native_fields = {
        str(field_name)
        for field_name in data.get(
            "backbone_native_evidence_fields",
            BACKBONE_NATIVE_EVIDENCE_FIELDS,
        )
    }
    for field_name in RESEARCH_CLAIM_FIXTURE_SPECIFIC_FIELDS:
        if field_name in native_fields:
            return RESEARCH_CLAIM_FIXTURE_REASON_CODES[
                "fixture_specific_native_field_rejected"
            ]
    return ""
