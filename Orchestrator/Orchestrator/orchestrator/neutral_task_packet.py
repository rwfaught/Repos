from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


BOUNDARY = "NEUTRAL_TASK_PACKET_SOURCE_TEST_DOCS"
REPORT_NAME = "neutral_task_packet_report"

NO_FIRST_PRODUCT_WEDGE_SELECTED = "no first product wedge selected"
PHASE_387_REMAINS_PARKED = "Phase 387 remains parked"
RUNTIME_PROVIDER_MODEL_EXECUTION_EXCLUDED = (
    "runtime/provider/model execution remains excluded"
)
NOT_PRODUCTION_READINESS = "not production readiness"

NOT_SEMANTIC_CORRECTNESS_PROOF = "not semantic correctness proof"
NOT_CLAIMS_DISPUTES_APPEALS_PRODUCT_COMMITMENT = (
    "not claims/disputes/appeals product commitment"
)
NOT_GAME_WORLDBUILDING_DESIGN_PRODUCT_COMMITMENT = (
    "not game/worldbuilding/design product commitment"
)

REQUIRED_PACKET_FIELDS = (
    "packet_id",
    "boundary_name",
    "operator_goal",
    "neutral_subject",
    "inputs_available",
    "required_neutral_fields",
    "open_questions",
    "contradictions_or_tensions",
    "decisions_needed",
    "next_work_items",
    "blocked_until",
    "success_shape",
    "explicit_non_proofs",
    "runtime_provider_model_posture",
    "phase_387_posture",
    "wedge_posture",
)

NON_PROOFS = (
    NOT_PRODUCTION_READINESS,
    NOT_SEMANTIC_CORRECTNESS_PROOF,
    "not runtime/provider/model proof",
    "not Phase 387 implementation",
    "not first product wedge selection",
    NOT_CLAIMS_DISPUTES_APPEALS_PRODUCT_COMMITMENT,
    NOT_GAME_WORLDBUILDING_DESIGN_PRODUCT_COMMITMENT,
)


@dataclass(frozen=True)
class NeutralTaskPacket:
    packet_id: str
    boundary_name: str
    operator_goal: str
    neutral_subject: str
    inputs_available: tuple[Any, ...]
    required_neutral_fields: tuple[str, ...]
    open_questions: tuple[Any, ...]
    contradictions_or_tensions: tuple[Any, ...]
    decisions_needed: tuple[Any, ...]
    next_work_items: tuple[Any, ...]
    blocked_until: tuple[Any, ...]
    success_shape: tuple[Any, ...]
    explicit_non_proofs: tuple[str, ...]
    runtime_provider_model_posture: str
    phase_387_posture: str
    wedge_posture: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "boundary_name": self.boundary_name,
            "operator_goal": self.operator_goal,
            "neutral_subject": self.neutral_subject,
            "inputs_available": list(self.inputs_available),
            "required_neutral_fields": list(self.required_neutral_fields),
            "open_questions": list(self.open_questions),
            "contradictions_or_tensions": list(self.contradictions_or_tensions),
            "decisions_needed": list(self.decisions_needed),
            "next_work_items": list(self.next_work_items),
            "blocked_until": list(self.blocked_until),
            "success_shape": list(self.success_shape),
            "explicit_non_proofs": list(self.explicit_non_proofs),
            "runtime_provider_model_posture": self.runtime_provider_model_posture,
            "phase_387_posture": self.phase_387_posture,
            "wedge_posture": self.wedge_posture,
        }


@dataclass(frozen=True)
class NeutralTaskPacketReport:
    report_name: str
    boundary: str
    required_packet_fields: tuple[str, ...]
    present_required_packet_fields: tuple[str, ...]
    missing_required_packet_fields: tuple[str, ...]
    open_questions: tuple[Any, ...]
    contradictions_or_tensions: tuple[Any, ...]
    decisions_needed: tuple[Any, ...]
    next_work_items: tuple[Any, ...]
    runtime_provider_model_execution_excluded: bool
    phase_387_remains_parked: bool
    no_first_product_wedge_selected: bool
    structurally_ready: bool
    structural_blockers: tuple[str, ...]
    explicit_non_proofs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_name": self.report_name,
            "boundary": self.boundary,
            "required_packet_fields": list(self.required_packet_fields),
            "present_required_packet_fields": list(self.present_required_packet_fields),
            "missing_required_packet_fields": list(self.missing_required_packet_fields),
            "open_questions": list(self.open_questions),
            "contradictions_or_tensions": list(self.contradictions_or_tensions),
            "decisions_needed": list(self.decisions_needed),
            "next_work_items": list(self.next_work_items),
            "runtime_provider_model_execution_excluded": (
                self.runtime_provider_model_execution_excluded
            ),
            "phase_387_remains_parked": self.phase_387_remains_parked,
            "no_first_product_wedge_selected": self.no_first_product_wedge_selected,
            "structurally_ready": self.structurally_ready,
            "structural_blockers": list(self.structural_blockers),
            "explicit_non_proofs": list(self.explicit_non_proofs),
        }


def _as_tuple(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return (value,)


def _coerce_mapping(packet: NeutralTaskPacket | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(packet, NeutralTaskPacket):
        return packet.to_dict()
    if isinstance(packet, Mapping):
        return dict(packet)
    raise TypeError("neutral task packet report requires a packet or mapping")


def _field_presence(packet: Mapping[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    present = tuple(field for field in REQUIRED_PACKET_FIELDS if field in packet)
    missing = tuple(field for field in REQUIRED_PACKET_FIELDS if field not in packet)
    return present, missing


def _build_blockers(
    missing_required: tuple[str, ...],
    runtime_provider_model_execution_excluded: bool,
    phase_387_remains_parked: bool,
    no_first_product_wedge_selected: bool,
) -> tuple[str, ...]:
    blockers: list[str] = []
    blockers.extend(f"missing required packet field: {field}" for field in missing_required)

    if not runtime_provider_model_execution_excluded:
        blockers.append("runtime/provider/model execution exclusion is not explicit")
    if not phase_387_remains_parked:
        blockers.append("Phase 387 parked posture is not explicit")
    if not no_first_product_wedge_selected:
        blockers.append("no first product wedge selected posture is not explicit")

    return tuple(blockers)


def build_neutral_task_packet(
    *,
    packet_id: str = "neutral-task-packet-001",
    boundary_name: str = BOUNDARY,
    operator_goal: str = "Inspect a neutral task packet before domain-specific work.",
    neutral_subject: str = "domain-neutral dossier/case candidate",
) -> NeutralTaskPacket:
    return NeutralTaskPacket(
        packet_id=packet_id,
        boundary_name=boundary_name,
        operator_goal=operator_goal,
        neutral_subject=neutral_subject,
        inputs_available=(
            "dossier/case task-readiness operator review",
            "neutral task packet plan",
            "continue abstraction-first ratification record",
        ),
        required_neutral_fields=REQUIRED_PACKET_FIELDS,
        open_questions=("which domain, if any, should later become the first proving domain",),
        contradictions_or_tensions=(
            "product-shaped planning must not silently choose a wedge",
        ),
        decisions_needed=(
            "Roger/CTO must choose a domain or explicitly continue abstraction-first",
        ),
        next_work_items=(
            "review neutral packet structure before any domain-specific boundary",
        ),
        blocked_until=(
            "Roger chooses a domain or explicitly continues abstraction-first",
        ),
        success_shape=(
            "required neutral packet fields can be represented and checked",
            "missing required packet fields can be reported",
            "stop postures remain explicit",
        ),
        explicit_non_proofs=NON_PROOFS,
        runtime_provider_model_posture=RUNTIME_PROVIDER_MODEL_EXECUTION_EXCLUDED,
        phase_387_posture=PHASE_387_REMAINS_PARKED,
        wedge_posture=NO_FIRST_PRODUCT_WEDGE_SELECTED,
    )


def build_neutral_task_packet_report(
    packet: NeutralTaskPacket | Mapping[str, Any],
) -> NeutralTaskPacketReport:
    packet_data = _coerce_mapping(packet)
    present, missing = _field_presence(packet_data)
    runtime_excluded = (
        packet_data.get("runtime_provider_model_posture")
        == RUNTIME_PROVIDER_MODEL_EXECUTION_EXCLUDED
    )
    phase_387_parked = packet_data.get("phase_387_posture") == PHASE_387_REMAINS_PARKED
    no_wedge_selected = packet_data.get("wedge_posture") == NO_FIRST_PRODUCT_WEDGE_SELECTED
    blockers = _build_blockers(
        missing,
        runtime_excluded,
        phase_387_parked,
        no_wedge_selected,
    )

    return NeutralTaskPacketReport(
        report_name=REPORT_NAME,
        boundary=BOUNDARY,
        required_packet_fields=REQUIRED_PACKET_FIELDS,
        present_required_packet_fields=present,
        missing_required_packet_fields=missing,
        open_questions=_as_tuple(packet_data.get("open_questions")),
        contradictions_or_tensions=_as_tuple(packet_data.get("contradictions_or_tensions")),
        decisions_needed=_as_tuple(packet_data.get("decisions_needed")),
        next_work_items=_as_tuple(packet_data.get("next_work_items")),
        runtime_provider_model_execution_excluded=runtime_excluded,
        phase_387_remains_parked=phase_387_parked,
        no_first_product_wedge_selected=no_wedge_selected,
        structurally_ready=len(blockers) == 0,
        structural_blockers=blockers,
        explicit_non_proofs=_as_tuple(packet_data.get("explicit_non_proofs")),
    )


def build_neutral_task_packet_report_dict(
    packet: NeutralTaskPacket | Mapping[str, Any],
) -> dict[str, Any]:
    return build_neutral_task_packet_report(packet).to_dict()
