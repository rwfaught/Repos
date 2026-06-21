"""Admission-to-boundary-packet draft contract.

Packet drafting is deterministic and non-executing. It does not dispatch
workers, choose substrates, select providers/models, mutate files, or perform
production work.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from orchestrator.intake_admission_pipeline import IntakeAdmissionPipelineResult
from orchestrator.route_proposal import AdmissionDecision


REPO_PATH = r"C:\Users\accou\Desktop\Repos\Orchestrator\Orchestrator"

NO_ACTIVITY_FLAGS = {
    "mutation_performed": False,
    "execution_performed": False,
    "provider_executed": False,
    "model_executed": False,
    "runtime_executed": False,
    "wsl_executed": False,
    "installer_executed": False,
    "discord_executed": False,
    "bridge_executed": False,
    "adapter_executed": False,
    "platform_executed": False,
    "export_performed": False,
    "package_performed": False,
    "cleanup_performed": False,
    "deletion_performed": False,
    "archive_performed": False,
}

PACKET_NON_PROOFS = (
    "packet_drafting_is_not_execution",
    "packet_drafting_is_not_coordinator_acceptance",
    "packet_drafting_is_not_worker_execution",
    "packet_drafting_is_not_substrate_selection",
    "packet_drafting_is_not_provider_model_selection",
    "packet_drafting_is_not_route_execution",
    "packet_drafting_is_not_production_readiness",
)

EXPLICIT_EXCLUSIONS = (
    "No worker execution.",
    "No concrete substrate selection.",
    "No Codex invocation.",
    "No Relay invocation.",
    "No OpenClaw, Hermes, Ollama, WSL, Discord, provider, model, runtime, platform, scheduler, or connector execution.",
    "No RAG/local lookup or web lookup.",
    "No file operation behavior beyond the authorized draft boundary.",
    "No artifact export/package behavior.",
    "No cleanup/delete/archive behavior.",
    "No production execution or production readiness claim.",
)

REPORT_FORMAT = (
    "Boundary",
    "Files changed or reviewed",
    "Commands run",
    "Validation results",
    "Exact marker or proof status",
    "Deviations",
    "Explicit non-proofs",
    "Caveats",
)

STOP_CONDITIONS = (
    "missing admission decision",
    "non-accepted admission",
    "unknown capability",
    "blocked or external capability",
    "platform/provider/model/runtime route",
    "production execution route",
    "substrate selection request",
    "scope or allowed files missing for mutation packet",
)


@dataclass(frozen=True)
class BoundaryPacketDraft:
    packet_id: str
    source_request_id: str
    packet_kind: str
    boundary_name: str
    purpose: str
    role: str
    allowed_files: tuple[str, ...]
    allowed_operations: tuple[str, ...]
    explicit_exclusions: tuple[str, ...]
    validation_commands: tuple[str, ...]
    report_format: tuple[str, ...]
    expected_proof: str
    non_proofs: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    next_review_boundary: str
    caveats: tuple[str, ...]


@dataclass(frozen=True)
class BoundaryPacketDraftResult:
    accepted: bool
    packet_draft: BoundaryPacketDraft | None
    blocked_conditions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    recommended_next_action: str
    capability_assessment: dict[str, Any]
    non_proofs: tuple[str, ...]
    no_activity_flags: dict[str, bool]


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _tuple_of_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _assessment_from_admission(admission: AdmissionDecision | None) -> dict[str, Any]:
    if admission is None:
        return {
            "requested_capabilities": [],
            "known_capabilities": [],
            "unknown_capabilities": [],
            "maturity_statuses": {},
            "blocked_or_external_capabilities": [],
            "production_ready_capabilities": [],
            "non_proofs": [],
            "admission_notes": ["packet_drafting_stopped_before_admission"],
            "authorized_execution": False,
        }
    return deepcopy(admission.capability_assessment)


def _admission_from_input(
    source: IntakeAdmissionPipelineResult | AdmissionDecision,
) -> tuple[AdmissionDecision | None, IntakeAdmissionPipelineResult | None]:
    if isinstance(source, IntakeAdmissionPipelineResult):
        return source.admission_decision, source
    if isinstance(source, AdmissionDecision):
        return source, None
    raise TypeError("source must be IntakeAdmissionPipelineResult or AdmissionDecision")


def _route_values(
    pipeline_result: IntakeAdmissionPipelineResult | None,
    admission: AdmissionDecision,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    if pipeline_result and pipeline_result.candidate_route:
        envelope = pipeline_result.candidate_route.route_envelope
        return (
            _tuple_of_text(envelope.get("required_capabilities")),
            _tuple_of_text(envelope.get("caveats")),
            _tuple_of_text(pipeline_result.intake_record.caveats if pipeline_result.intake_record else ()),
        )
    assessment = admission.capability_assessment
    return (
        _tuple_of_text(assessment.get("requested_capabilities")),
        (),
        (),
    )


def _blocked_result(
    blocked_conditions: tuple[str, ...],
    missing_requirements: tuple[str, ...],
    recommended_next_action: str,
    capability_assessment: dict[str, Any],
    non_proofs: tuple[str, ...],
) -> BoundaryPacketDraftResult:
    return BoundaryPacketDraftResult(
        accepted=False,
        packet_draft=None,
        blocked_conditions=_dedupe(blocked_conditions),
        missing_requirements=_dedupe(missing_requirements),
        recommended_next_action=recommended_next_action,
        capability_assessment=deepcopy(capability_assessment),
        non_proofs=_dedupe(PACKET_NON_PROOFS + non_proofs),
        no_activity_flags=dict(NO_ACTIVITY_FLAGS),
    )


def _packet_kind(admission: AdmissionDecision, capabilities: tuple[str, ...], caveats: tuple[str, ...]) -> str:
    if admission.request_type in {"general_answer", "creative_generation"}:
        return "direct_answer_response"
    if admission.request_type == "planning_request":
        return "coding_worker_report_only" if "planning_report" in capabilities else "relay_read_only_review"
    if admission.request_type in {"coding_task", "file_operation"}:
        if any("docs_only" in caveat for caveat in caveats):
            return "coding_worker_docs_only_mutation"
        return "coding_worker_source_test_mutation"
    return "relay_read_only_review"


def _allowed_files(packet_kind: str, caveats: tuple[str, ...]) -> tuple[str, ...]:
    declared = tuple(
        caveat.split("allowed_files:", 1)[1].strip()
        for caveat in caveats
        if caveat.startswith("allowed_files:") and caveat.split("allowed_files:", 1)[1].strip()
    )
    if declared:
        return declared
    if packet_kind == "direct_answer_response":
        return ("no file mutation",)
    if packet_kind in {"relay_read_only_review", "coding_worker_report_only"}:
        return ("read-only repository scope declared by coordinator",)
    if packet_kind == "coding_worker_docs_only_mutation":
        return ("docs/**",)
    return ("declared source/test files only",)


def _validation_commands(packet_kind: str) -> tuple[str, ...]:
    if packet_kind == "direct_answer_response":
        return ("read/search validation only if needed",)
    if packet_kind in {"relay_read_only_review", "coding_worker_report_only"}:
        return ("git status --short", "read/search validation only")
    if packet_kind == "coding_worker_docs_only_mutation":
        return ("git status --short", "read/search validation only; no tests unless explicitly authorized")
    return ("git status --short", "targeted py_compile/unittest commands declared by coordinator")


def _purpose(packet_kind: str, admission: AdmissionDecision) -> str:
    purposes = {
        "direct_answer_response": "Draft a direct answer response without worker execution.",
        "relay_read_only_review": "Draft a bounded read-only review packet.",
        "coding_worker_report_only": "Draft a bounded report-only coding worker packet.",
        "coding_worker_docs_only_mutation": "Draft a bounded docs-only mutation worker packet.",
        "coding_worker_source_test_mutation": "Draft a bounded source/test mutation worker packet.",
    }
    return purposes.get(packet_kind, f"Draft a bounded packet for {admission.request_type}.")


def build_boundary_packet_draft(
    source: IntakeAdmissionPipelineResult | AdmissionDecision,
) -> BoundaryPacketDraftResult:
    """Build a human-mediated packet draft from accepted admission posture."""

    admission, pipeline_result = _admission_from_input(source)
    if admission is None:
        if pipeline_result is not None:
            return _blocked_result(
                pipeline_result.blocked_conditions or ("missing_admission_decision",),
                pipeline_result.missing_requirements,
                pipeline_result.recommended_next_action or "route_or_clarify_before_packet_drafting",
                deepcopy(pipeline_result.capability_assessment),
                pipeline_result.non_proofs,
            )
        return _blocked_result(
            ("missing_admission_decision",),
            ("admission_decision",),
            "route_or_clarify_before_packet_drafting",
            _assessment_from_admission(admission),
            (),
        )

    source_non_proofs = tuple(admission.non_proofs)
    if pipeline_result is not None:
        source_non_proofs = _dedupe(source_non_proofs + pipeline_result.non_proofs)

    if not admission.accepted:
        return _blocked_result(
            admission.blocked_conditions or ("non_accepted_admission",),
            admission.missing_requirements,
            admission.recommended_next_action or "clarify_or_reframe_before_packet_drafting",
            _assessment_from_admission(admission),
            source_non_proofs,
        )

    assessment = _assessment_from_admission(admission)
    if assessment.get("unknown_capabilities"):
        return _blocked_result(
            ("unknown_capabilities_block_packet_drafting",),
            tuple(assessment["unknown_capabilities"]),
            "clarify_unknown_capabilities_before_packet_drafting",
            assessment,
            source_non_proofs,
        )
    if assessment.get("blocked_or_external_capabilities"):
        return _blocked_result(
            ("blocked_or_external_capabilities_require_separate_boundary",),
            tuple(assessment["blocked_or_external_capabilities"]),
            "route_external_capabilities_under_separate_boundary",
            assessment,
            source_non_proofs,
        )

    capabilities, caveats, intake_caveats = _route_values(pipeline_result, admission)
    all_caveats = _dedupe(caveats + intake_caveats)
    if any(item in capabilities for item in ("provider_model", "platform_runtime", "production_execution")):
        return _blocked_result(
            ("platform_provider_model_runtime_or_production_route_blocked",),
            (),
            "route_to_external_boundary_or_reframe",
            assessment,
            source_non_proofs,
        )

    packet_kind = _packet_kind(admission, capabilities, all_caveats)
    if packet_kind in {"coding_worker_docs_only_mutation", "coding_worker_source_test_mutation"}:
        if _allowed_files(packet_kind, all_caveats) in {("docs/**",), ("declared source/test files only",)}:
            extra_caveat = ("coordinator_must_finalize_allowed_files_before_dispatch",)
        else:
            extra_caveat = ()
    else:
        extra_caveat = ()

    packet = BoundaryPacketDraft(
        packet_id=f"packet_{admission.request_id}",
        source_request_id=admission.request_id,
        packet_kind=packet_kind,
        boundary_name=f"{admission.request_id}_{packet_kind}".upper(),
        purpose=_purpose(packet_kind, admission),
        role="human_mediated_worker_packet_draft" if "worker" in packet_kind else "coordinator_response_draft",
        allowed_files=_allowed_files(packet_kind, all_caveats),
        allowed_operations=(packet_kind,),
        explicit_exclusions=EXPLICIT_EXCLUSIONS,
        validation_commands=_validation_commands(packet_kind),
        report_format=REPORT_FORMAT,
        expected_proof="worker_report_or_response_draft_only_not_execution",
        non_proofs=_dedupe(PACKET_NON_PROOFS + source_non_proofs),
        stop_conditions=STOP_CONDITIONS,
        next_review_boundary="coordinator_review_required_before_any_dispatch_or_acceptance",
        caveats=_dedupe(all_caveats + extra_caveat),
    )

    return BoundaryPacketDraftResult(
        accepted=True,
        packet_draft=packet,
        blocked_conditions=(),
        missing_requirements=(),
        recommended_next_action="coordinator_review_packet_draft_before_any_dispatch",
        capability_assessment=assessment,
        non_proofs=packet.non_proofs,
        no_activity_flags=dict(NO_ACTIVITY_FLAGS),
    )


def render_boundary_packet_text(packet_draft: BoundaryPacketDraft) -> str:
    """Render a copyable human-mediated packet draft."""

    lines = [
        "ROLE:",
        packet_draft.role,
        "",
        "REPO:",
        REPO_PATH,
        "",
        "BOUNDARY:",
        packet_draft.boundary_name,
        "",
        "PURPOSE:",
        packet_draft.purpose,
        "",
        "ALLOWED FILES OR FILE CLASSES:",
        *[f"- {item}" for item in packet_draft.allowed_files],
        "",
        "ALLOWED OPERATIONS:",
        *[f"- {item}" for item in packet_draft.allowed_operations],
        "",
        "EXCLUSIONS:",
        *[f"- {item}" for item in packet_draft.explicit_exclusions],
        "",
        "VALIDATION:",
        *[f"- {item}" for item in packet_draft.validation_commands],
        "",
        "REPORT FORMAT:",
        *[f"- {item}" for item in packet_draft.report_format],
        "",
        "EXPECTED PROOF:",
        packet_draft.expected_proof,
        "",
        "NON-PROOFS:",
        *[f"- {item}" for item in packet_draft.non_proofs],
        "",
        "STOP CONDITIONS:",
        *[f"- {item}" for item in packet_draft.stop_conditions],
        "",
        "CAVEATS:",
        *[f"- {item}" for item in packet_draft.caveats],
    ]
    return "\n".join(lines)
