from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from orchestrator.backbone_control_loop import (
    BACKBONE_NATIVE_EVIDENCE_FIELDS,
    BACKBONE_V0_DECLARED,
    BackboneAdapterDescriptor,
    ordered_backbone_stage_names,
)


CODE_PATCHING_BOUNDED_CONTEXT = "code_patching"
CODE_PATCHING_BACKBONE_MAPPING_STATUS = (
    "code_patching_bounded_context_mapped_to_backbone_scaffold_not_migrated"
)
CODE_PATCHING_BACKBONE_ADAPTER = BackboneAdapterDescriptor(
    adapter_name="code_patching_backbone_mapping_adapter",
    bounded_context=CODE_PATCHING_BOUNDED_CONTEXT,
    execution_allowed=False,
)

CODE_PATCHING_MAPPING_NON_PROOFS = (
    "code_patching_mapping_is_not_semantic_correctness",
    "code_patching_mapping_is_not_production_readiness",
    "code_patching_mapping_is_not_autonomous_ai_coding",
    "code_patching_mapping_is_not_provider_model_runtime_platform_execution",
    "code_patching_mapping_does_not_declare_backbone_v0",
    "code_patching_mapping_does_not_migrate_patch_loop",
    "code_patching_mapping_does_not_execute_adapters",
)

CODE_PATCHING_MAPPING_COMPLETE = "mapped"
CODE_PATCHING_MAPPING_INCOMPLETE = "incomplete"

CODE_PATCHING_MAPPING_REASON_CODES = {
    "stage_name_missing": "stage_name_missing",
    "unknown_stage_name": "unknown_stage_name",
    "bounded_context_missing": "bounded_context_missing",
    "source_evidence_missing": "source_evidence_missing",
    "phase_evidence_missing": "phase_evidence_missing",
}


@dataclass(frozen=True)
class CodePatchingBackboneStageMapping:
    stage_name: str
    bounded_context: str = CODE_PATCHING_BOUNDED_CONTEXT
    source_modules: tuple[str, ...] = field(default_factory=tuple)
    phase_docs: tuple[str, ...] = field(default_factory=tuple)
    phase_tests: tuple[str, ...] = field(default_factory=tuple)
    mapping_note: str = ""
    reason_code: str = ""
    domain_payload: dict[str, Any] = field(default_factory=dict)
    non_proofs: tuple[str, ...] = CODE_PATCHING_MAPPING_NON_PROOFS

    def as_dict(self) -> dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "bounded_context": self.bounded_context,
            "source_modules": list(self.source_modules),
            "phase_docs": list(self.phase_docs),
            "phase_tests": list(self.phase_tests),
            "mapping_note": self.mapping_note,
            "reason_code": self.reason_code,
            "domain_payload": dict(self.domain_payload),
            "non_proofs": list(self.non_proofs),
            "backbone_native_evidence_fields": list(BACKBONE_NATIVE_EVIDENCE_FIELDS),
            "backbone_v0_declared": BACKBONE_V0_DECLARED,
            "adapter_execution_allowed": CODE_PATCHING_BACKBONE_ADAPTER.execution_allowed,
            "patch_loop_migrated": False,
        }


CODE_PATCHING_BACKBONE_STAGE_MAPPINGS = (
    CodePatchingBackboneStageMapping(
        stage_name="intake_result",
        source_modules=("orchestrator/packet_result_patch_proposal_eligibility.py",),
        phase_docs=("docs/PHASE_288.md",),
        phase_tests=(
            "tests/test_phase_288_packet_result_to_patch_proposal_eligibility_contract.py",
        ),
        mapping_note="Packet result intake evidence enters the bounded code-patching context.",
        domain_payload={"phase": "288", "patch_loop_role": "packet_result_intake"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="eligibility_record",
        source_modules=("orchestrator/packet_result_patch_proposal_eligibility.py",),
        phase_docs=("docs/PHASE_288.md",),
        phase_tests=(
            "tests/test_phase_288_packet_result_to_patch_proposal_eligibility_contract.py",
        ),
        mapping_note="Eligibility record evaluates packet result suitability.",
        domain_payload={"phase": "288", "patch_loop_role": "proposal_eligibility"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="candidate_artifact",
        source_modules=("orchestrator/packet_result_patch_proposal_candidate.py",),
        phase_docs=("docs/PHASE_289.md",),
        phase_tests=("tests/test_phase_289_packet_result_patch_proposal_candidate_artifact.py",),
        mapping_note="Candidate artifact preserves structured patch proposal evidence.",
        domain_payload={"phase": "289", "patch_loop_role": "candidate_artifact"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="operator_decision",
        source_modules=("orchestrator/patch_proposal_candidate_promotion.py",),
        phase_docs=("docs/PHASE_290.md",),
        phase_tests=("tests/test_phase_290_patch_proposal_candidate_operator_promotion_gate.py",),
        mapping_note="Operator promotion gate records promote, reject, or defer decisions.",
        domain_payload={"phase": "290", "patch_loop_role": "operator_promotion_gate"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="promotion_record",
        source_modules=("orchestrator/patch_proposal_candidate_promotion.py",),
        phase_docs=("docs/PHASE_290.md",),
        phase_tests=("tests/test_phase_290_patch_proposal_candidate_operator_promotion_gate.py",),
        mapping_note="Promotion record links the candidate to later draft proposal work.",
        domain_payload={"phase": "290", "patch_loop_role": "candidate_promotion"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="draft_action_proposal",
        source_modules=("orchestrator/promoted_candidate_draft_patch_proposal.py",),
        phase_docs=("docs/PHASE_294.md",),
        phase_tests=(
            "tests/test_phase_294_promoted_candidate_to_draft_patch_proposal_artifact.py",
        ),
        mapping_note="Draft patch proposal is the domain-specific action proposal.",
        domain_payload={"phase": "294", "patch_loop_role": "draft_patch_proposal"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="authorization_eligibility",
        source_modules=(
            "orchestrator/draft_patch_proposal_apply_authorization_eligibility.py",
        ),
        phase_docs=("docs/PHASE_296.md",),
        phase_tests=(
            "tests/test_phase_296_draft_patch_proposal_apply_authorization_eligibility_readback.py",
        ),
        mapping_note="Authorization eligibility remains separate from apply authorization.",
        domain_payload={"phase": "296", "patch_loop_role": "authorization_eligibility"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="authorization_record",
        source_modules=(
            "orchestrator/draft_patch_proposal_apply_authorization_record.py",
        ),
        phase_docs=("docs/PHASE_299.md", "docs/PHASE_300.md", "docs/PHASE_301.md"),
        phase_tests=(
            "tests/test_phase_299_draft_patch_proposal_operator_apply_authorization_record.py",
            "tests/test_phase_300_patch_apply_authorization_record_negative_edge_contract.py",
            "tests/test_phase_301_patch_apply_authorization_readback.py",
        ),
        mapping_note="Operator apply authorization record precedes bounded apply attempts.",
        domain_payload={"phase": "299-301", "patch_loop_role": "authorization_record"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="bounded_action_attempt",
        source_modules=("orchestrator/authorized_draft_patch_apply.py",),
        phase_docs=("docs/PHASE_303.md", "docs/PHASE_304.md", "docs/PHASE_305.md"),
        phase_tests=(
            "tests/test_phase_303_authorized_draft_patch_proposal_bounded_apply_execution.py",
            "tests/test_phase_304_authorized_draft_patch_apply_negative_edge_contract.py",
            "tests/test_phase_305_authorized_bounded_apply_attempt_readback.py",
        ),
        mapping_note="Authorized bounded patch apply attempt remains domain-specific.",
        domain_payload={"phase": "303-305", "patch_loop_role": "bounded_apply_attempt"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="action_result_evidence",
        source_modules=("orchestrator/authorized_draft_patch_apply.py",),
        phase_docs=("docs/PHASE_303.md", "docs/PHASE_305.md"),
        phase_tests=(
            "tests/test_phase_303_authorized_draft_patch_proposal_bounded_apply_execution.py",
            "tests/test_phase_305_authorized_bounded_apply_attempt_readback.py",
        ),
        mapping_note="Apply attempt result evidence is read as domain evidence only.",
        domain_payload={"phase": "303-305", "patch_loop_role": "apply_result_evidence"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="mechanical_verification",
        source_modules=("orchestrator/authorized_bounded_apply_result_verification.py",),
        phase_docs=("docs/PHASE_307.md", "docs/PHASE_308.md", "docs/PHASE_309.md"),
        phase_tests=(
            "tests/test_phase_307_authorized_bounded_apply_result_verification.py",
            "tests/test_phase_308_authorized_bounded_apply_result_verification_negative_edge_contract.py",
            "tests/test_phase_309_authorized_bounded_apply_result_verification_readback.py",
        ),
        mapping_note="Mechanical verification does not prove semantic correctness.",
        domain_payload={"phase": "307-309", "patch_loop_role": "mechanical_verification"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="finalization_record",
        source_modules=("orchestrator/verified_bounded_apply_task_finalization.py",),
        phase_docs=("docs/PHASE_311.md", "docs/PHASE_312.md", "docs/PHASE_313.md"),
        phase_tests=(
            "tests/test_phase_311_verified_bounded_apply_task_finalization_record.py",
            "tests/test_phase_312_verified_bounded_apply_task_finalization_negative_edge_contract.py",
            "tests/test_phase_313_verified_bounded_apply_task_finalization_readback.py",
        ),
        mapping_note="Finalization record preserves caveats and non-proofs.",
        domain_payload={"phase": "311-313", "patch_loop_role": "task_finalization"},
    ),
    CodePatchingBackboneStageMapping(
        stage_name="readback",
        source_modules=(
            "orchestrator/authorized_bounded_apply_result_verification.py",
            "orchestrator/verified_bounded_apply_task_finalization.py",
            "orchestrator/backbone_control_loop.py",
        ),
        phase_docs=("docs/PHASE_309.md", "docs/PHASE_313.md", "docs/PHASE_316.md"),
        phase_tests=(
            "tests/test_phase_309_authorized_bounded_apply_result_verification_readback.py",
            "tests/test_phase_313_verified_bounded_apply_task_finalization_readback.py",
            "tests/test_phase_316_backbone_v0_abstraction_scaffold.py",
        ),
        mapping_note="Readback surfaces status without Backbone V0 declaration.",
        domain_payload={"phase": "309,313,316", "patch_loop_role": "readback"},
    ),
)


def ordered_code_patching_backbone_stage_mappings() -> tuple[CodePatchingBackboneStageMapping, ...]:
    return CODE_PATCHING_BACKBONE_STAGE_MAPPINGS


def validate_code_patching_backbone_stage_mapping(
    mapping: CodePatchingBackboneStageMapping | dict[str, Any],
) -> dict[str, Any]:
    data = mapping.as_dict() if isinstance(mapping, CodePatchingBackboneStageMapping) else dict(mapping)
    reason_code = _first_mapping_reason(data)
    status = CODE_PATCHING_MAPPING_INCOMPLETE if reason_code else CODE_PATCHING_MAPPING_COMPLETE
    return {
        "code_patching_backbone_stage_mapping_validation": True,
        "status": status,
        "complete": status == CODE_PATCHING_MAPPING_COMPLETE,
        "reason_code": reason_code,
        "stage_name": data.get("stage_name", ""),
        "bounded_context": data.get("bounded_context", ""),
        "source_modules": list(data.get("source_modules") or []),
        "phase_docs": list(data.get("phase_docs") or []),
        "phase_tests": list(data.get("phase_tests") or []),
        "domain_payload_keys": sorted(str(key) for key in dict(data.get("domain_payload") or {}).keys()),
        "backbone_native_evidence_fields": list(BACKBONE_NATIVE_EVIDENCE_FIELDS),
        "non_proofs": list(data.get("non_proofs") or []),
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "adapter_execution_allowed": CODE_PATCHING_BACKBONE_ADAPTER.execution_allowed,
        "patch_loop_migrated": False,
    }


def read_code_patching_backbone_mapping_status() -> dict[str, Any]:
    mappings = ordered_code_patching_backbone_stage_mappings()
    validations = [validate_code_patching_backbone_stage_mapping(mapping) for mapping in mappings]
    return {
        "code_patching_backbone_mapping_status": CODE_PATCHING_BACKBONE_MAPPING_STATUS,
        "bounded_context": CODE_PATCHING_BOUNDED_CONTEXT,
        "adapter": CODE_PATCHING_BACKBONE_ADAPTER.as_dict(),
        "adapter_execution_allowed": CODE_PATCHING_BACKBONE_ADAPTER.execution_allowed,
        "stage_names": [mapping.stage_name for mapping in mappings],
        "expected_stage_names": list(ordered_backbone_stage_names()),
        "all_stage_names_match_backbone": [mapping.stage_name for mapping in mappings]
        == list(ordered_backbone_stage_names()),
        "mapping_count": len(mappings),
        "complete": all(validation["complete"] for validation in validations),
        "incomplete_reason_codes": [
            validation["reason_code"] for validation in validations if validation["reason_code"]
        ],
        "non_proofs": list(CODE_PATCHING_MAPPING_NON_PROOFS),
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "patch_loop_migrated": False,
        "semantic_correctness_claimed": False,
        "production_readiness_claimed": False,
        "provider_model_runtime_platform_execution_claimed": False,
        "autonomous_ai_coding_claimed": False,
    }


def _first_mapping_reason(data: dict[str, Any]) -> str:
    stage_name = str(data.get("stage_name") or "").strip()
    if not stage_name:
        return CODE_PATCHING_MAPPING_REASON_CODES["stage_name_missing"]
    if stage_name not in ordered_backbone_stage_names():
        return CODE_PATCHING_MAPPING_REASON_CODES["unknown_stage_name"]
    if str(data.get("bounded_context") or "").strip() != CODE_PATCHING_BOUNDED_CONTEXT:
        return CODE_PATCHING_MAPPING_REASON_CODES["bounded_context_missing"]
    if not data.get("source_modules"):
        return CODE_PATCHING_MAPPING_REASON_CODES["source_evidence_missing"]
    if not data.get("phase_docs") and not data.get("phase_tests"):
        return CODE_PATCHING_MAPPING_REASON_CODES["phase_evidence_missing"]
    return ""
