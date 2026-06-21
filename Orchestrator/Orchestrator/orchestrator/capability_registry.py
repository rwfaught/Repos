"""Deterministic capability registry contract for route admission assessment.

Registry lookup is evidence-only. It does not execute work, select providers,
choose runtimes, schedule reminders, access connectors, or authorize mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CapabilityClass(str, Enum):
    DIRECT_ANSWER = "direct_answer"
    CODING_TASK = "coding_task"
    FILE_OPERATION = "file_operation"
    LOCAL_DOCUMENT_LOOKUP = "local_document_lookup"
    WEB_RESEARCH = "web_research"
    REMINDER_SCHEDULER = "reminder_scheduler"
    CONNECTOR_ACCESS = "connector_access"
    PLATFORM_RUNTIME = "platform_runtime"
    PROVIDER_MODEL = "provider_model"
    ARTIFACT_EXPORT_PACKAGE = "artifact_export_package"
    PRODUCTION_EXECUTION = "production_execution"
    UNSUPPORTED_OR_BLOCKED = "unsupported_or_blocked"


class CapabilityMaturityStatus(str, Enum):
    NAMED_ONLY = "named_only"
    DOCS_CONTROL_DEFINED = "docs_control_defined"
    SOURCE_CONTRACT_DEFINED = "source_contract_defined"
    SOURCE_TEST_PROVEN = "source_test_proven"
    LOCAL_RUNTIME_PROVEN = "local_runtime_proven"
    ARTIFACT_PROVEN = "artifact_proven"
    PRODUCTION_READY = "production_ready"
    BLOCKED_OR_EXTERNAL = "blocked_or_external"


@dataclass(frozen=True)
class CapabilityRegistryEntry:
    capability_id: str
    display_name: str
    capability_class: CapabilityClass
    maturity_status: CapabilityMaturityStatus
    authority_docs: tuple[str, ...]
    implementation_refs: tuple[str, ...]
    allowed_route_types: tuple[str, ...]
    permission_burden: str
    validation_burden: str
    stop_conditions: tuple[str, ...]
    non_proofs: tuple[str, ...]
    owner_context: str
    external_track_dependency: str | None = None


AUTHORITY_DOCS = (
    "docs/CAPABILITY_REGISTRY.md",
    "docs/CONTEXT_MAP.md",
    "docs/TRACKS_AND_OPEN_THREADS.md",
)

NO_EXECUTION_NON_PROOFS = (
    "capability_label_is_not_execution_authority",
    "registry_lookup_is_not_execution",
    "registry_lookup_is_not_provider_model_substrate_selection",
    "registry_lookup_is_not_production_readiness",
)

BLOCKED_OR_EXTERNAL_STATUSES = {
    CapabilityMaturityStatus.NAMED_ONLY,
    CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL,
}


def _entry(
    capability_id: str,
    display_name: str,
    capability_class: CapabilityClass,
    maturity_status: CapabilityMaturityStatus,
    allowed_route_types: tuple[str, ...],
    permission_burden: str,
    validation_burden: str,
    stop_conditions: tuple[str, ...],
    non_proofs: tuple[str, ...],
    owner_context: str = "product_route_admission",
    implementation_refs: tuple[str, ...] = (),
    external_track_dependency: str | None = None,
) -> CapabilityRegistryEntry:
    return CapabilityRegistryEntry(
        capability_id=capability_id,
        display_name=display_name,
        capability_class=capability_class,
        maturity_status=maturity_status,
        authority_docs=AUTHORITY_DOCS,
        implementation_refs=implementation_refs,
        allowed_route_types=allowed_route_types,
        permission_burden=permission_burden,
        validation_burden=validation_burden,
        stop_conditions=stop_conditions,
        non_proofs=NO_EXECUTION_NON_PROOFS + non_proofs,
        owner_context=owner_context,
        external_track_dependency=external_track_dependency,
    )


_ENTRIES = (
    _entry(
        "artifact_export_package",
        "Artifact Export Or Package",
        CapabilityClass.ARTIFACT_EXPORT_PACKAGE,
        CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL,
        ("artifact_export",),
        "explicit artifact/export/package boundary",
        "hash, path, and upload evidence appropriate to the artifact boundary",
        ("missing_export_authority", "upload_ambiguity", "stale_artifact"),
        ("not_implied_by_local_docs_pass", "not_upload_acceptance"),
        external_track_dependency="artifact_export_package_track",
    ),
    _entry(
        "bounded_file_write",
        "Bounded File Write",
        CapabilityClass.FILE_OPERATION,
        CapabilityMaturityStatus.SOURCE_CONTRACT_DEFINED,
        ("file_operation", "coding_task"),
        "explicit bounded mutation authority and declared file scope",
        "path, scope, and effect evidence",
        ("undeclared_path", "broad_scope", "missing_operator_authorization"),
        ("not_general_filesystem_authority", "not_autonomous_writeback"),
        implementation_refs=("orchestrator/request_routing.py",),
    ),
    _entry(
        "coding_task",
        "Coding Task",
        CapabilityClass.CODING_TASK,
        CapabilityMaturityStatus.SOURCE_CONTRACT_DEFINED,
        ("coding_task",),
        "explicit bounded worker packet",
        "worker evidence plus coordinator review",
        ("ambiguous_scope", "undeclared_files", "mutation_beyond_boundary"),
        ("not_integrated_production_workflow", "not_coordinator_acceptance"),
        implementation_refs=("orchestrator/request_routing.py",),
    ),
    _entry(
        "connector_access",
        "Connector Access",
        CapabilityClass.CONNECTOR_ACCESS,
        CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL,
        ("unsupported_or_requires_connector",),
        "explicit connector boundary",
        "connector authority and result evidence",
        ("missing_connector_authority", "login_ambiguity", "write_risk"),
        ("not_blanket_external_access", "not_platform_execution"),
        external_track_dependency="connector_track",
    ),
    _entry(
        "creative_text_generation",
        "Creative Text Generation",
        CapabilityClass.DIRECT_ANSWER,
        CapabilityMaturityStatus.DOCS_CONTROL_DEFINED,
        ("creative_generation",),
        "answer-only unless a future boundary authorizes persistence or mutation",
        "preserve non-mutation caveats",
        ("requested_file_mutation", "provider_selection_required"),
        ("not_provider_model_selection", "not_productized_general_assistant_lane"),
    ),
    _entry(
        "direct_answer",
        "Direct Answer",
        CapabilityClass.DIRECT_ANSWER,
        CapabilityMaturityStatus.DOCS_CONTROL_DEFINED,
        ("general_answer", "creative_generation", "planning_request"),
        "low unless stale, consequential, missing, or boundary-sensitive",
        "state basis and caveats when needed",
        ("missing_facts", "high_risk_uncertainty", "retrieval_required"),
        ("not_productized_general_assistant_lane",),
    ),
    _entry(
        "external_connector",
        "External Connector",
        CapabilityClass.CONNECTOR_ACCESS,
        CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL,
        ("unsupported_or_requires_connector",),
        "explicit connector boundary",
        "connector authority and result evidence",
        ("missing_connector_authority", "external_policy_conflict"),
        ("not_connector_execution", "not_blanket_external_access"),
        external_track_dependency="connector_track",
    ),
    _entry(
        "filesystem_mutation_authority",
        "Filesystem Mutation Authority",
        CapabilityClass.FILE_OPERATION,
        CapabilityMaturityStatus.SOURCE_CONTRACT_DEFINED,
        ("coding_task", "file_operation"),
        "explicit operator authorization and declared scope",
        "path, scope, and effect evidence",
        ("undeclared_files", "unsafe_path", "hidden_cleanup"),
        ("not_general_filesystem_authority", "not_autonomous_writeback"),
        implementation_refs=("orchestrator/request_routing.py",),
    ),
    _entry(
        "local_document_lookup",
        "Local Document Lookup",
        CapabilityClass.LOCAL_DOCUMENT_LOOKUP,
        CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL,
        ("local_document_lookup",),
        "declared document source boundary",
        "source-grounded evidence paths once implemented",
        ("missing_source_authority", "stale_source_risk", "mutation_requested"),
        ("not_rag_implementation", "not_index_freshness_proof"),
        external_track_dependency="rag_local_document_lookup_track",
    ),
    _entry(
        "patch_proposal",
        "Patch Proposal",
        CapabilityClass.CODING_TASK,
        CapabilityMaturityStatus.SOURCE_CONTRACT_DEFINED,
        ("coding_task",),
        "explicit patch proposal boundary",
        "proposal artifact evidence plus coordinator review",
        ("missing_boundary", "proposal_used_as_apply_authority"),
        ("not_file_mutation_authority", "not_coordinator_acceptance"),
        implementation_refs=("orchestrator/patch_proposal.py",),
    ),
    _entry(
        "planning_report",
        "Planning Report",
        CapabilityClass.DIRECT_ANSWER,
        CapabilityMaturityStatus.DOCS_CONTROL_DEFINED,
        ("planning_request",),
        "report-only; no execution or mutation",
        "preserve assumptions and non-proof caveats",
        ("operator_requests_execution", "missing_scope"),
        ("not_execution_authority", "not_implementation_proof"),
    ),
    _entry(
        "platform_runtime",
        "Platform Runtime",
        CapabilityClass.PLATFORM_RUNTIME,
        CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL,
        ("platform_runtime",),
        "explicit platform crossing boundary",
        "fresh runtime/platform evidence",
        ("missing_crossing_boundary", "runtime_proof_missing"),
        ("not_product_route_correctness", "not_provider_readiness"),
        external_track_dependency="platform_runtime_track",
    ),
    _entry(
        "production_execution",
        "Production Execution",
        CapabilityClass.PRODUCTION_EXECUTION,
        CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL,
        ("production_execution",),
        "future explicit production boundary and acceptance criteria",
        "future production-grade evidence",
        ("missing_production_authority", "missing_production_runtime_proof"),
        ("not_implied_by_local_pass", "not_production_readiness"),
        external_track_dependency="future_production_track",
    ),
    _entry(
        "provider_model",
        "Provider Or Model",
        CapabilityClass.PROVIDER_MODEL,
        CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL,
        ("provider_model",),
        "explicit provider/model authority and data exposure review",
        "provider contract and output evidence",
        ("provider_unavailable", "model_output_used_as_proof"),
        ("not_route_correctness_proof", "not_provider_model_selection"),
        external_track_dependency="provider_model_track",
    ),
    _entry(
        "scheduling_contract",
        "Scheduling Contract",
        CapabilityClass.REMINDER_SCHEDULER,
        CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL,
        ("reminder_request",),
        "explicit operator confirmation for time, recurrence, target, and persistence",
        "parsed time and persistence semantics once implemented",
        ("ambiguous_time", "missing_confirmation", "unsupported_persistence"),
        ("not_scheduler_implementation", "not_durable_reminder_service"),
        external_track_dependency="reminder_scheduler_track",
    ),
    _entry(
        "source_inspection",
        "Source Inspection",
        CapabilityClass.CODING_TASK,
        CapabilityMaturityStatus.SOURCE_CONTRACT_DEFINED,
        ("coding_task",),
        "bounded read/inspection authority",
        "file/path evidence and scoped findings",
        ("scope_unclear", "inspection_used_as_mutation_authority"),
        ("not_mutation_authority", "not_route_execution"),
        implementation_refs=("orchestrator/request_routing.py",),
    ),
    _entry(
        "unsupported_or_blocked",
        "Unsupported Or Blocked",
        CapabilityClass.UNSUPPORTED_OR_BLOCKED,
        CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL,
        ("unsupported_or_requires_connector", "needs_clarification"),
        "clarification or explicit new boundary required",
        "explain missing authority, proof, connector, scope, or capability",
        ("required_capability_unavailable", "authority_missing"),
        ("not_permission_to_execute_adjacent_work",),
    ),
    _entry(
        "web_research",
        "Web Research",
        CapabilityClass.WEB_RESEARCH,
        CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL,
        ("research_request",),
        "explicit web-research boundary when required",
        "current source evidence and caveats",
        ("web_authority_missing", "connector_or_login_required"),
        ("not_web_lookup_implementation", "not_provider_selection"),
        external_track_dependency="web_research_track",
    ),
)

CAPABILITY_REGISTRY = {entry.capability_id: entry for entry in _ENTRIES}


def get_capability(capability_id: str) -> CapabilityRegistryEntry | None:
    """Return a registry entry without executing or authorizing any work."""

    return CAPABILITY_REGISTRY.get(capability_id)


def list_capabilities() -> tuple[CapabilityRegistryEntry, ...]:
    """Return registry entries in deterministic capability_id order."""

    return tuple(CAPABILITY_REGISTRY[capability_id] for capability_id in sorted(CAPABILITY_REGISTRY))


def assess_required_capabilities(required_capabilities: list[str] | tuple[str, ...]) -> dict[str, object]:
    """Assess capability labels conservatively without admitting execution."""

    requested = list(required_capabilities)
    known_entries = [CAPABILITY_REGISTRY[item] for item in requested if item in CAPABILITY_REGISTRY]
    unknown = [item for item in requested if item not in CAPABILITY_REGISTRY]
    blocked_or_external = [
        entry.capability_id
        for entry in known_entries
        if entry.maturity_status in BLOCKED_OR_EXTERNAL_STATUSES or entry.external_track_dependency
    ]
    production_ready = [
        entry.capability_id
        for entry in known_entries
        if entry.maturity_status == CapabilityMaturityStatus.PRODUCTION_READY
    ]
    non_proofs = sorted({proof for entry in known_entries for proof in entry.non_proofs})

    admission_notes = [
        "assessment_only_not_execution",
        "requested_capability_is_not_available_capability",
        "available_capability_is_not_implemented_capability",
        "implemented_capability_is_not_authorized_execution",
    ]
    if unknown:
        admission_notes.append("unknown_capabilities_require_clarification_or_future_registry_entry")
    if blocked_or_external:
        admission_notes.append("blocked_or_external_capabilities_require_separate_boundary")
    if not production_ready:
        admission_notes.append("no_requested_capability_is_production_ready")

    return {
        "requested_capabilities": requested,
        "known_capabilities": [entry.capability_id for entry in known_entries],
        "unknown_capabilities": unknown,
        "available_capabilities": [
            entry.capability_id
            for entry in known_entries
            if entry.maturity_status != CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL
        ],
        "implemented_capabilities": [
            entry.capability_id
            for entry in known_entries
            if entry.maturity_status
            in {
                CapabilityMaturityStatus.SOURCE_CONTRACT_DEFINED,
                CapabilityMaturityStatus.SOURCE_TEST_PROVEN,
                CapabilityMaturityStatus.LOCAL_RUNTIME_PROVEN,
                CapabilityMaturityStatus.ARTIFACT_PROVEN,
                CapabilityMaturityStatus.PRODUCTION_READY,
            }
        ],
        "authorized_execution": False,
        "maturity_statuses": {
            entry.capability_id: entry.maturity_status.value for entry in known_entries
        },
        "blocked_or_external_capabilities": blocked_or_external,
        "production_ready_capabilities": production_ready,
        "non_proofs": non_proofs,
        "admission_notes": admission_notes,
    }
