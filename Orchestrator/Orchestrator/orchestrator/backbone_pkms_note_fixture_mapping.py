from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from orchestrator.backbone_control_loop import (
    BACKBONE_NATIVE_EVIDENCE_FIELDS,
    BACKBONE_V0_DECLARED,
    BackboneAdapterDescriptor,
    ordered_backbone_stage_names,
)


PKMS_NOTE_FIXTURE_BOUNDED_CONTEXT = "pkms_note_operation_fixture"
PKMS_NOTE_FIXTURE_MAPPING_STATUS = (
    "pkms_note_operation_fixture_mapped_to_backbone_scaffold_not_executed"
)
PKMS_NOTE_FIXTURE_ADAPTER = BackboneAdapterDescriptor(
    adapter_name="pkms_note_operation_fixture_backbone_mapping_adapter",
    bounded_context=PKMS_NOTE_FIXTURE_BOUNDED_CONTEXT,
    execution_allowed=False,
)

PKMS_NOTE_FIXTURE_NON_PROOFS = (
    "pkms_note_fixture_mapping_is_not_semantic_correctness",
    "pkms_note_fixture_mapping_is_not_production_readiness",
    "pkms_note_fixture_mapping_is_not_autonomous_ai_coding",
    "pkms_note_fixture_mapping_is_not_provider_model_runtime_platform_execution",
    "pkms_note_fixture_mapping_does_not_declare_backbone_v0",
    "pkms_note_fixture_mapping_does_not_access_live_vaults",
    "pkms_note_fixture_mapping_does_not_mutate_live_pkms_notes",
    "pkms_note_fixture_mapping_does_not_prove_backlink_or_frontmatter_correctness",
    "pkms_note_fixture_mapping_does_not_execute_real_domain_actions",
    "pkms_note_fixture_mapping_does_not_generate_official_capsule",
)

PKMS_NOTE_FIXTURE_MAPPING_COMPLETE = "mapped"
PKMS_NOTE_FIXTURE_MAPPING_INCOMPLETE = "incomplete"

PKMS_NOTE_FIXTURE_REASON_CODES = {
    "stage_name_missing": "stage_name_missing",
    "unknown_stage_name": "unknown_stage_name",
    "bounded_context_missing": "bounded_context_missing",
    "fake_vault_path_missing": "fake_vault_path_missing",
    "fake_note_path_missing": "fake_note_path_missing",
    "fake_before_after_evidence_missing": "fake_before_after_evidence_missing",
    "fixture_doc_or_test_evidence_missing": "fixture_doc_or_test_evidence_missing",
    "stage_order_mismatch": "stage_order_mismatch",
    "backbone_v0_claim_rejected": "backbone_v0_claim_rejected",
    "adapter_execution_claim_rejected": "adapter_execution_claim_rejected",
    "live_vault_access_claim_rejected": "live_vault_access_claim_rejected",
    "live_pkms_mutation_claim_rejected": "live_pkms_mutation_claim_rejected",
    "backlink_frontmatter_correctness_claim_rejected": (
        "backlink_frontmatter_correctness_claim_rejected"
    ),
    "semantic_correctness_claim_rejected": "semantic_correctness_claim_rejected",
    "production_readiness_claim_rejected": "production_readiness_claim_rejected",
    "official_capsule_claim_rejected": "official_capsule_claim_rejected",
    "pkms_specific_native_field_rejected": "pkms_specific_native_field_rejected",
}

PKMS_NOTE_FIXTURE_SPECIFIC_FIELDS = (
    "fake_vault_path",
    "fake_note_id",
    "fake_note_path",
    "fake_note_title",
    "fake_frontmatter_change",
    "fake_backlink_insertion",
    "fake_before_note_content_evidence",
    "fake_after_note_content_evidence",
    "fake_operator_authorization",
    "fake_verification_evidence",
    "fixture_stage_role",
)

PKMS_NOTE_FIXTURE_OPERATOR_READBACK_FIELDS = (
    "backbone_v0_declared",
    "adapter_execution_allowed",
    "live_vault_access_allowed",
    "note_mutation_allowed",
    "real_backlink_frontmatter_correctness_proven",
    "bounded_context",
    "mapped_stage_names",
    "stage_statuses",
    "status_counts",
    "complete_mapping_count",
    "fixture_evidence_strings",
    "backbone_native_fields",
    "pkms_specific_fields",
    "non_proofs",
    "possible_negative_edge_reason_codes",
    "recommended_next_boundary",
)

PKMS_NOTE_FIXTURE_RECOMMENDED_NEXT_BOUNDARY = (
    "PHASE329_BACKBONE_MULTI_FIXTURE_CRITERIA_READINESS_ASSESSMENT_READONLY"
)

_FORBIDDEN_TRUE_CLAIM_REASON_FIELDS = {
    "backbone_v0_declared": "backbone_v0_claim_rejected",
    "adapter_execution_allowed": "adapter_execution_claim_rejected",
    "adapter_executed": "adapter_execution_claim_rejected",
    "live_vault_accessed": "live_vault_access_claim_rejected",
    "live_obsidian_vault_accessed": "live_vault_access_claim_rejected",
    "live_pkms_note_mutated": "live_pkms_mutation_claim_rejected",
    "real_note_mutation_executed": "live_pkms_mutation_claim_rejected",
    "real_backlink_frontmatter_correctness_claimed": (
        "backlink_frontmatter_correctness_claim_rejected"
    ),
    "backlink_correctness_claimed": "backlink_frontmatter_correctness_claim_rejected",
    "frontmatter_correctness_claimed": "backlink_frontmatter_correctness_claim_rejected",
    "semantic_correctness_claimed": "semantic_correctness_claim_rejected",
    "production_readiness_claimed": "production_readiness_claim_rejected",
    "official_capsule_generated": "official_capsule_claim_rejected",
}


@dataclass(frozen=True)
class PkmsNoteFixtureBackboneStageMapping:
    stage_name: str
    bounded_context: str = PKMS_NOTE_FIXTURE_BOUNDED_CONTEXT
    fixture_sources: tuple[str, ...] = field(default_factory=tuple)
    phase_docs: tuple[str, ...] = field(default_factory=tuple)
    phase_tests: tuple[str, ...] = field(default_factory=tuple)
    mapping_note: str = ""
    reason_code: str = ""
    domain_payload: dict[str, Any] = field(default_factory=dict)
    non_proofs: tuple[str, ...] = PKMS_NOTE_FIXTURE_NON_PROOFS

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
            "adapter_execution_allowed": PKMS_NOTE_FIXTURE_ADAPTER.execution_allowed,
            "live_vault_accessed": False,
            "live_pkms_note_mutated": False,
        }


def _fixture_mapping(
    stage_name: str,
    fixture_stage_role: str,
    mapping_note: str,
) -> PkmsNoteFixtureBackboneStageMapping:
    return PkmsNoteFixtureBackboneStageMapping(
        stage_name=stage_name,
        fixture_sources=("fixtures/pkms_note_operation/static_note_operation.json",),
        phase_docs=("docs/PHASE_326.md",),
        phase_tests=("tests/test_phase_326_backbone_pkms_note_fixture_mapping.py",),
        mapping_note=mapping_note,
        domain_payload={
            "fake_vault_path": "C:/FAKE_OBSIDIAN_VAULT_DO_NOT_ACCESS",
            "fake_note_id": "fake-note-0001",
            "fake_note_path": "Areas/Fake Project/Fake Note.md",
            "fake_note_title": "Fake Note Operation Fixture",
            "fake_frontmatter_change": "status: proposed -> status: reviewed",
            "fake_backlink_insertion": "[[Fake Related Note]]",
            "fake_before_note_content_evidence": "Before fixture text only.",
            "fake_after_note_content_evidence": (
                "After fixture text only with fake backlink."
            ),
            "fake_operator_authorization": "fake_operator_authorization_placeholder",
            "fake_verification_evidence": "fake_static_shape_verification_only",
            "fixture_stage_role": fixture_stage_role,
        },
    )


PKMS_NOTE_FIXTURE_BACKBONE_STAGE_MAPPINGS = (
    _fixture_mapping("intake_result", "note_operation_intake", "Static fake note operation enters the fixture context."),
    _fixture_mapping("eligibility_record", "fixture_eligibility", "Fixture eligibility is described without live vault access."),
    _fixture_mapping("candidate_artifact", "note_operation_candidate", "Candidate note operation remains fake fixture data."),
    _fixture_mapping("operator_decision", "operator_authorization_placeholder", "Operator decision is represented by fake authorization evidence only."),
    _fixture_mapping("promotion_record", "promotion_placeholder", "Promotion record is static fixture linkage only."),
    _fixture_mapping("draft_action_proposal", "draft_note_operation", "Draft note operation proposes fake frontmatter and backlink changes."),
    _fixture_mapping("authorization_eligibility", "authorization_eligibility_placeholder", "Authorization eligibility is not live authority."),
    _fixture_mapping("authorization_record", "authorization_record_placeholder", "Authorization record is a fake fixture record only."),
    _fixture_mapping("bounded_action_attempt", "non_executed_note_operation_attempt", "Bounded action attempt is explicitly not executed."),
    _fixture_mapping("action_result_evidence", "fake_before_after_note_evidence", "Result evidence is fake before/after note content only."),
    _fixture_mapping("mechanical_verification", "static_shape_check", "Mechanical verification is shape-only, not backlink or frontmatter correctness."),
    _fixture_mapping("finalization_record", "fixture_finalization", "Finalization preserves caveats and non-proofs."),
    _fixture_mapping("readback", "fixture_readback", "Readback surfaces fixture status without Backbone V0."),
)


def ordered_pkms_note_fixture_backbone_stage_mappings() -> tuple[
    PkmsNoteFixtureBackboneStageMapping, ...
]:
    return PKMS_NOTE_FIXTURE_BACKBONE_STAGE_MAPPINGS


def validate_pkms_note_fixture_backbone_stage_mapping(
    mapping: PkmsNoteFixtureBackboneStageMapping | dict[str, Any],
) -> dict[str, Any]:
    data = (
        mapping.as_dict()
        if isinstance(mapping, PkmsNoteFixtureBackboneStageMapping)
        else dict(mapping)
    )
    reason_code = _first_mapping_reason(data)
    status = (
        PKMS_NOTE_FIXTURE_MAPPING_INCOMPLETE
        if reason_code
        else PKMS_NOTE_FIXTURE_MAPPING_COMPLETE
    )
    return {
        "pkms_note_fixture_backbone_stage_mapping_validation": True,
        "status": status,
        "complete": status == PKMS_NOTE_FIXTURE_MAPPING_COMPLETE,
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
        "pkms_specific_fields": list(PKMS_NOTE_FIXTURE_SPECIFIC_FIELDS),
        "non_proofs": list(data.get("non_proofs") or PKMS_NOTE_FIXTURE_NON_PROOFS),
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "adapter_execution_allowed": PKMS_NOTE_FIXTURE_ADAPTER.execution_allowed,
        "live_vault_accessed": False,
        "live_pkms_note_mutated": False,
    }


def validate_ordered_pkms_note_fixture_backbone_stage_mappings(
    mappings: tuple[PkmsNoteFixtureBackboneStageMapping, ...] | list[Any] | None = None,
) -> dict[str, Any]:
    selected_mappings = list(
        ordered_pkms_note_fixture_backbone_stage_mappings()
        if mappings is None
        else mappings
    )
    stage_names = [
        mapping.stage_name if isinstance(mapping, PkmsNoteFixtureBackboneStageMapping)
        else str(dict(mapping).get("stage_name") or "")
        for mapping in selected_mappings
    ]
    expected_stage_names = list(ordered_backbone_stage_names())
    validations = [
        validate_pkms_note_fixture_backbone_stage_mapping(mapping)
        for mapping in selected_mappings
    ]
    order_reason = (
        PKMS_NOTE_FIXTURE_REASON_CODES["stage_order_mismatch"]
        if stage_names != expected_stage_names
        else ""
    )
    incomplete_reason_codes = [
        validation["reason_code"] for validation in validations if validation["reason_code"]
    ]
    if order_reason:
        incomplete_reason_codes.append(order_reason)
    return {
        "pkms_note_fixture_backbone_ordered_mapping_validation": True,
        "stage_names": stage_names,
        "expected_stage_names": expected_stage_names,
        "all_stage_names_match_backbone": not order_reason,
        "mapping_count": len(selected_mappings),
        "complete": not incomplete_reason_codes,
        "status": (
            PKMS_NOTE_FIXTURE_MAPPING_COMPLETE
            if not incomplete_reason_codes
            else PKMS_NOTE_FIXTURE_MAPPING_INCOMPLETE
        ),
        "reason_code": order_reason,
        "incomplete_reason_codes": incomplete_reason_codes,
        "non_proofs": list(PKMS_NOTE_FIXTURE_NON_PROOFS),
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "adapter_execution_allowed": PKMS_NOTE_FIXTURE_ADAPTER.execution_allowed,
        "live_vault_accessed": False,
        "live_pkms_note_mutated": False,
    }


def read_pkms_note_fixture_backbone_mapping_status(
    mappings: tuple[PkmsNoteFixtureBackboneStageMapping, ...] | list[Any] | None = None,
) -> dict[str, Any]:
    selected_mappings = list(
        ordered_pkms_note_fixture_backbone_stage_mappings()
        if mappings is None
        else mappings
    )
    validations = [
        validate_pkms_note_fixture_backbone_stage_mapping(mapping)
        for mapping in selected_mappings
    ]
    ordered_validation = validate_ordered_pkms_note_fixture_backbone_stage_mappings(
        selected_mappings
    )
    return {
        "pkms_note_fixture_backbone_mapping_status": PKMS_NOTE_FIXTURE_MAPPING_STATUS,
        "bounded_context": PKMS_NOTE_FIXTURE_BOUNDED_CONTEXT,
        "adapter": PKMS_NOTE_FIXTURE_ADAPTER.as_dict(),
        "adapter_execution_allowed": PKMS_NOTE_FIXTURE_ADAPTER.execution_allowed,
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
        "non_proofs": list(PKMS_NOTE_FIXTURE_NON_PROOFS),
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "live_vault_accessed": False,
        "live_pkms_note_mutated": False,
        "real_backlink_frontmatter_correctness_claimed": False,
        "semantic_correctness_claimed": False,
        "production_readiness_claimed": False,
        "provider_model_runtime_platform_execution_claimed": False,
        "autonomous_ai_coding_claimed": False,
    }


def read_pkms_note_fixture_backbone_operator_readback(
    mappings: tuple[PkmsNoteFixtureBackboneStageMapping, ...] | list[Any] | None = None,
) -> dict[str, Any]:
    selected_mappings = list(
        ordered_pkms_note_fixture_backbone_stage_mappings()
        if mappings is None
        else mappings
    )
    validations = [
        validate_pkms_note_fixture_backbone_stage_mapping(mapping)
        for mapping in selected_mappings
    ]
    ordered_validation = validate_ordered_pkms_note_fixture_backbone_stage_mappings(
        selected_mappings
    )
    stage_statuses = [
        {
            "stage_name": validation["stage_name"],
            "status": validation["status"],
            "complete": validation["complete"],
            "blocked": False,
            "not_applicable": False,
            "reason_code": validation["reason_code"],
        }
        for validation in validations
    ]
    incomplete_count = sum(1 for validation in validations if not validation["complete"])
    return {
        "pkms_note_fixture_backbone_operator_readback": True,
        "readback_fields": list(PKMS_NOTE_FIXTURE_OPERATOR_READBACK_FIELDS),
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "adapter_execution_allowed": PKMS_NOTE_FIXTURE_ADAPTER.execution_allowed,
        "adapters_executable_through_mapping": False,
        "live_vault_access_allowed": False,
        "live_vault_accessed": False,
        "note_mutation_allowed": False,
        "live_pkms_note_mutated": False,
        "real_backlink_frontmatter_correctness_proven": False,
        "bounded_context": PKMS_NOTE_FIXTURE_BOUNDED_CONTEXT,
        "mapped_stage_names": ordered_validation["stage_names"],
        "expected_backbone_stage_names": list(ordered_backbone_stage_names()),
        "stage_statuses": stage_statuses,
        "complete_mapping_count": len(selected_mappings) - incomplete_count,
        "status_counts": {
            "complete": len(selected_mappings) - incomplete_count,
            "mapped": len(selected_mappings) - incomplete_count,
            "incomplete": incomplete_count,
            "blocked": 0,
            "not_applicable": 0,
        },
        "fixture_evidence_strings": {
            "fixture_sources": sorted(
                {
                    fixture_source
                    for mapping in selected_mappings
                    for fixture_source in (
                        mapping.fixture_sources
                        if isinstance(mapping, PkmsNoteFixtureBackboneStageMapping)
                        else tuple(dict(mapping).get("fixture_sources") or ())
                    )
                }
            ),
            "phase_docs": sorted(
                {
                    phase_doc
                    for mapping in selected_mappings
                    for phase_doc in (
                        mapping.phase_docs
                        if isinstance(mapping, PkmsNoteFixtureBackboneStageMapping)
                        else tuple(dict(mapping).get("phase_docs") or ())
                    )
                }
            ),
            "phase_tests": sorted(
                {
                    phase_test
                    for mapping in selected_mappings
                    for phase_test in (
                        mapping.phase_tests
                        if isinstance(mapping, PkmsNoteFixtureBackboneStageMapping)
                        else tuple(dict(mapping).get("phase_tests") or ())
                    )
                }
            ),
            "evidence_is_fake_fixture_only": True,
            "evidence_is_reference_only": True,
        },
        "backbone_native_fields": list(BACKBONE_NATIVE_EVIDENCE_FIELDS),
        "pkms_specific_fields": list(PKMS_NOTE_FIXTURE_SPECIFIC_FIELDS),
        "non_proofs": list(PKMS_NOTE_FIXTURE_NON_PROOFS),
        "possible_negative_edge_reason_codes": sorted(
            PKMS_NOTE_FIXTURE_REASON_CODES.values()
        ),
        "blocked_conditions": list(ordered_validation["incomplete_reason_codes"]),
        "recommended_next_boundary": PKMS_NOTE_FIXTURE_RECOMMENDED_NEXT_BOUNDARY,
        "semantic_correctness_claimed": False,
        "production_readiness_claimed": False,
        "provider_model_runtime_platform_execution_claimed": False,
        "autonomous_ai_coding_claimed": False,
        "official_capsule_proof_current": False,
    }


def _first_mapping_reason(data: dict[str, Any]) -> str:
    stage_name = str(data.get("stage_name") or "").strip()
    if not stage_name:
        return PKMS_NOTE_FIXTURE_REASON_CODES["stage_name_missing"]
    if stage_name not in ordered_backbone_stage_names():
        return PKMS_NOTE_FIXTURE_REASON_CODES["unknown_stage_name"]
    if str(data.get("bounded_context") or "").strip() != PKMS_NOTE_FIXTURE_BOUNDED_CONTEXT:
        return PKMS_NOTE_FIXTURE_REASON_CODES["bounded_context_missing"]
    claim_reason = _forbidden_claim_reason(data)
    if claim_reason:
        return claim_reason
    native_leak_reason = _pkms_specific_native_field_reason(data)
    if native_leak_reason:
        return native_leak_reason
    payload = dict(data.get("domain_payload") or {})
    if not str(payload.get("fake_vault_path") or "").strip():
        return PKMS_NOTE_FIXTURE_REASON_CODES["fake_vault_path_missing"]
    if not (
        str(payload.get("fake_note_path") or "").strip()
        or str(payload.get("fake_note_id") or "").strip()
    ):
        return PKMS_NOTE_FIXTURE_REASON_CODES["fake_note_path_missing"]
    if not (
        str(payload.get("fake_before_note_content_evidence") or "").strip()
        and str(payload.get("fake_after_note_content_evidence") or "").strip()
    ):
        return PKMS_NOTE_FIXTURE_REASON_CODES["fake_before_after_evidence_missing"]
    if not data.get("phase_docs") and not data.get("phase_tests"):
        return PKMS_NOTE_FIXTURE_REASON_CODES[
            "fixture_doc_or_test_evidence_missing"
        ]
    return ""


def _forbidden_claim_reason(data: dict[str, Any]) -> str:
    for field_name, reason_code in _FORBIDDEN_TRUE_CLAIM_REASON_FIELDS.items():
        if data.get(field_name) is True:
            return PKMS_NOTE_FIXTURE_REASON_CODES[reason_code]
    return ""


def _pkms_specific_native_field_reason(data: dict[str, Any]) -> str:
    native_fields = {
        str(field_name)
        for field_name in data.get(
            "backbone_native_evidence_fields",
            BACKBONE_NATIVE_EVIDENCE_FIELDS,
        )
    }
    for field_name in PKMS_NOTE_FIXTURE_SPECIFIC_FIELDS:
        if field_name in native_fields:
            return PKMS_NOTE_FIXTURE_REASON_CODES[
                "pkms_specific_native_field_rejected"
            ]
    return ""
