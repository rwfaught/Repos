from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


BACKBONE_V0_DECLARED = False
BACKBONE_SCAFFOLD_STATUS = "backbone_v0_not_declared_scaffold_only"

BACKBONE_STAGE_NAMES = (
    "intake_result",
    "eligibility_record",
    "candidate_artifact",
    "operator_decision",
    "promotion_record",
    "draft_action_proposal",
    "authorization_eligibility",
    "authorization_record",
    "bounded_action_attempt",
    "action_result_evidence",
    "mechanical_verification",
    "finalization_record",
    "readback",
)

BACKBONE_RESERVED_CONTEXT_NAMES = (
    "linked_evidence_chain",
    "non_proofs",
    "activity_flags",
    "bounded_context_adapter",
)

BACKBONE_NATIVE_EVIDENCE_FIELDS = (
    "record_id",
    "stage_name",
    "stage_index",
    "linked_evidence_chain",
    "non_proofs",
    "activity_flags",
    "bounded_context_adapter",
)

BACKBONE_REQUIRED_EVIDENCE_CHAIN_FIELDS = (
    "source_record_id",
    "stage_evidence_id",
)

BACKBONE_DEFAULT_NON_PROOFS = (
    "backbone_scaffold_is_not_semantic_correctness",
    "backbone_scaffold_is_not_production_readiness",
    "backbone_scaffold_is_not_autonomous_ai_coding",
    "backbone_scaffold_is_not_provider_model_runtime_platform_execution",
    "backbone_scaffold_does_not_declare_backbone_v0",
)

BACKBONE_INCOMPLETE = "incomplete"
BACKBONE_COMPLETE = "complete"

BACKBONE_REASON_CODES = {
    "unknown_stage_name": "unknown_stage_name",
    "record_id_missing": "record_id_missing",
    "linked_evidence_chain_missing": "linked_evidence_chain_missing",
    "source_record_id_missing": "source_record_id_missing",
    "stage_evidence_id_missing": "stage_evidence_id_missing",
}


@dataclass(frozen=True)
class BackboneAdapterDescriptor:
    adapter_name: str
    bounded_context: str
    execution_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "adapter_name": self.adapter_name,
            "bounded_context": self.bounded_context,
            "execution_allowed": self.execution_allowed,
        }


@dataclass(frozen=True)
class BackboneStageRecord:
    stage_name: str
    record_id: str
    linked_evidence_chain: dict[str, Any] = field(default_factory=dict)
    domain_evidence: dict[str, Any] = field(default_factory=dict)
    domain_payload: dict[str, Any] = field(default_factory=dict)
    non_proofs: tuple[str, ...] = BACKBONE_DEFAULT_NON_PROOFS
    activity_flags: dict[str, bool] = field(default_factory=dict)
    bounded_context_adapter: BackboneAdapterDescriptor | None = None

    def as_dict(self) -> dict[str, Any]:
        adapter = (
            self.bounded_context_adapter.as_dict()
            if self.bounded_context_adapter
            else None
        )
        return {
            "stage_name": self.stage_name,
            "stage_index": stage_index(self.stage_name),
            "record_id": self.record_id,
            "linked_evidence_chain": dict(self.linked_evidence_chain),
            "domain_evidence": dict(self.domain_evidence),
            "domain_payload": dict(self.domain_payload),
            "non_proofs": list(self.non_proofs),
            "activity_flags": dict(self.activity_flags),
            "bounded_context_adapter": adapter,
            "backbone_v0_declared": BACKBONE_V0_DECLARED,
        }


def ordered_backbone_stage_names() -> tuple[str, ...]:
    return BACKBONE_STAGE_NAMES


def stage_index(stage_name: str) -> int | None:
    try:
        return BACKBONE_STAGE_NAMES.index(stage_name)
    except ValueError:
        return None


def validate_backbone_stage_record(
    record: BackboneStageRecord | dict[str, Any],
) -> dict[str, Any]:
    data = record.as_dict() if isinstance(record, BackboneStageRecord) else dict(record)
    reason_code = _first_incomplete_reason(data)
    status = BACKBONE_INCOMPLETE if reason_code else BACKBONE_COMPLETE
    return {
        "backbone_stage_record_validation": True,
        "status": status,
        "complete": status == BACKBONE_COMPLETE,
        "reason_code": reason_code,
        "stage_name": data.get("stage_name", ""),
        "record_id": data.get("record_id", ""),
        "native_evidence_fields": list(BACKBONE_NATIVE_EVIDENCE_FIELDS),
        "domain_specific_payload_keys": sorted(
            str(key) for key in dict(data.get("domain_payload") or {}).keys()
        ),
        "domain_evidence_keys": sorted(
            str(key) for key in dict(data.get("domain_evidence") or {}).keys()
        ),
        "non_proofs": list(data.get("non_proofs") or []),
        "activity_flags": dict(data.get("activity_flags") or {}),
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
    }


def read_backbone_scaffold_status() -> dict[str, Any]:
    return {
        "backbone_scaffold_status": BACKBONE_SCAFFOLD_STATUS,
        "backbone_v0_declared": BACKBONE_V0_DECLARED,
        "ordered_stage_names": list(BACKBONE_STAGE_NAMES),
        "native_evidence_fields": list(BACKBONE_NATIVE_EVIDENCE_FIELDS),
        "reserved_context_names": list(BACKBONE_RESERVED_CONTEXT_NAMES),
        "required_evidence_chain_fields": list(BACKBONE_REQUIRED_EVIDENCE_CHAIN_FIELDS),
        "non_proofs": list(BACKBONE_DEFAULT_NON_PROOFS),
        "activity_flags_claim_semantic_correctness": False,
    }


def _first_incomplete_reason(data: dict[str, Any]) -> str:
    stage_name = str(data.get("stage_name") or "").strip()
    if stage_name not in BACKBONE_STAGE_NAMES:
        return BACKBONE_REASON_CODES["unknown_stage_name"]
    if not str(data.get("record_id") or "").strip():
        return BACKBONE_REASON_CODES["record_id_missing"]
    chain = data.get("linked_evidence_chain")
    if not isinstance(chain, dict) or not chain:
        return BACKBONE_REASON_CODES["linked_evidence_chain_missing"]
    for field_name in BACKBONE_REQUIRED_EVIDENCE_CHAIN_FIELDS:
        if not str(chain.get(field_name) or "").strip():
            return BACKBONE_REASON_CODES[f"{field_name}_missing"]
    return ""
