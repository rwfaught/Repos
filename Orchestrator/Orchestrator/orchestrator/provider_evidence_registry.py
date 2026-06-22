"""Deterministic provider evidence registry.

This registry records accepted read-only provider/model evidence as static
source data. It does not probe providers, call models, select runtimes, dispatch
workers, execute routes, or prove production readiness.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


NO_PROVIDER_EVIDENCE_ACTIVITY_FLAGS = {
    "provider_executed": False,
    "model_executed": False,
    "runtime_executed": False,
    "platform_executed": False,
    "worker_dispatched": False,
    "codex_dispatched": False,
    "rag_lookup_performed": False,
    "web_lookup_performed": False,
    "scheduler_executed": False,
    "connector_executed": False,
    "route_executed": False,
    "production_executed": False,
}

PROVIDER_EVIDENCE_NON_PROOFS = (
    "provider_evidence_is_not_provider_execution",
    "provider_evidence_is_not_model_execution",
    "provider_evidence_is_not_model_generation",
    "provider_evidence_is_not_api_generate",
    "provider_evidence_is_not_api_chat",
    "provider_evidence_is_not_model_correctness",
    "provider_evidence_is_not_model_loadability_for_real_workloads",
    "provider_evidence_is_not_vram_sufficiency_for_real_workloads",
    "provider_evidence_is_not_route_execution",
    "provider_evidence_is_not_worker_dispatch",
    "provider_evidence_is_not_rag_lookup",
    "provider_evidence_is_not_web_lookup",
    "provider_evidence_is_not_scheduler_execution",
    "provider_evidence_is_not_connector_execution",
    "provider_evidence_is_not_production_readiness",
)


@dataclass(frozen=True)
class ProviderEvidenceRecord:
    evidence_key: str
    provider_catalog_key: str
    evidence_kind: str
    evidence_status: str
    source_phase: str
    endpoint_shape: str
    method: str
    status_code: int
    content_type: str
    model_name: str
    model_names: tuple[str, ...]
    metadata: dict[str, Any]
    accepted_meaning: str
    non_proofs: tuple[str, ...]
    activity_flags: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_PHASE_131_MODEL_NAMES = (
    "qwen3.6:27b",
    "qwen3.6:35b-a3b",
    "bge-m3:latest",
    "nomic-embed-text-v2-moe:latest",
    "qwen3-30b-24k:latest",
    "qwen3-30b-20k:latest",
    "qwen3-coder:30b",
    "qwen3:30b-a3b-instruct-2507-q4_K_M",
    "qwen3:0.6b",
)

_EVIDENCE_RECORDS = (
    ProviderEvidenceRecord(
        evidence_key="phase_131_local_ollama_tags_model_list_visibility",
        provider_catalog_key="local_model_candidate",
        evidence_kind="provider_surface_model_list_visibility",
        evidence_status="read_only_provider_surface_visible",
        source_phase="PHASE_131",
        endpoint_shape="http://127.0.0.1:11434/api/tags",
        method="GET",
        status_code=200,
        content_type="application/json; charset=utf-8",
        model_name="",
        model_names=_PHASE_131_MODEL_NAMES,
        metadata={"model_count": len(_PHASE_131_MODEL_NAMES)},
        accepted_meaning="Read-only provider-surface model-list visibility existed at that moment.",
        non_proofs=PROVIDER_EVIDENCE_NON_PROOFS,
        activity_flags=dict(NO_PROVIDER_EVIDENCE_ACTIVITY_FLAGS),
    ),
    ProviderEvidenceRecord(
        evidence_key="phase_133_qwen3_30b_24k_show_metadata_visibility",
        provider_catalog_key="local_model_candidate",
        evidence_kind="model_metadata_visibility",
        evidence_status="read_only_metadata_visible",
        source_phase="PHASE_133",
        endpoint_shape="http://127.0.0.1:11434/api/show",
        method="POST",
        status_code=200,
        content_type="application/json; charset=utf-8",
        model_name="qwen3-30b-24k:latest",
        model_names=(),
        metadata={
            "modified_at": "2026-06-14T07:14:30.490610583-05:00",
            "format": "gguf",
            "family": "qwen3moe",
            "families": "qwen3moe",
            "parameter_size": "30.5B",
            "quantization_level": "Q4_K_M",
            "model_info_key_count": 31,
            "template_present": True,
            "parameters_present": True,
            "license_present": True,
        },
        accepted_meaning=(
            "Read-only model metadata visibility existed for qwen3-30b-24k:latest "
            "at that moment."
        ),
        non_proofs=PROVIDER_EVIDENCE_NON_PROOFS,
        activity_flags=dict(NO_PROVIDER_EVIDENCE_ACTIVITY_FLAGS),
    ),
    ProviderEvidenceRecord(
        evidence_key="phase_159_retry1_qwen36_27b_generate_marker_smoke",
        provider_catalog_key="local_model_candidate",
        evidence_kind="model_generation_smoke_marker",
        evidence_status="accepted_generation_smoke_marker_visible",
        source_phase="PHASE_159_RETRY_1_OPERATOR_PROOF",
        endpoint_shape="http://127.0.0.1:11434/api/generate",
        method="POST",
        status_code=200,
        content_type="application/json; charset=utf-8",
        model_name="qwen3.6:27b",
        model_names=(),
        metadata={
            "prompt": "Return exactly this marker in your final response and do not explain: ORCH_PROVIDER_SMOKE_OK",
            "stream": False,
            "temperature": 0,
            "num_predict": 96,
            "curl_exit_code": 0,
            "json_parse_succeeded": True,
            "returned_model": "qwen3.6:27b",
            "response_field": "ORCH_PROVIDER_SMOKE_OK",
            "done": True,
            "done_reason": "stop",
            "marker_present_in_response_field": True,
            "marker_present_in_thinking_field": True,
            "marker_present_in_raw_body": True,
            "final_git_status": "## main...origin/main",
            "prior_phase_159_initial_failure": (
                "FAIL_HTTP_200_LOCAL_PROVIDER_GENERATED_THINKING_ONLY_LENGTH_NO_MARKER"
            ),
            "prior_phase_159_initial_failure_reason": (
                "num_predict=16 was too small; output was consumed by thinking; "
                "response field was empty; done_reason=length; no marker accepted."
            ),
            "prior_phase_155_retry3_30b_failure": (
                "FAIL_HTTP_500_PROVIDER_MODEL_LOAD_CUDA_OOM_RAW_BODY_CAPTURED_NO_GENERATION_PROOF"
            ),
            "prior_phase_155_retry3_30b_failure_reason": (
                "qwen3-30b-24k:latest reached /api/generate and failed model load "
                "with CUDA OOM; this was not a qwen3.6:27b failure."
            ),
        },
        accepted_meaning=(
            "Phase 159 Retry 1 accepted a bounded local Ollama /api/generate marker "
            "smoke proof for qwen3.6:27b with num_predict=96."
        ),
        non_proofs=PROVIDER_EVIDENCE_NON_PROOFS,
        activity_flags=dict(NO_PROVIDER_EVIDENCE_ACTIVITY_FLAGS),
    ),
)

_EVIDENCE_BY_KEY = {record.evidence_key: record for record in _EVIDENCE_RECORDS}


def get_provider_evidence_registry() -> dict[str, ProviderEvidenceRecord]:
    """Return deterministic provider evidence keyed by evidence key."""

    return dict(_EVIDENCE_BY_KEY)


def get_provider_evidence_for_catalog_key(provider_catalog_key: str) -> tuple[ProviderEvidenceRecord, ...]:
    """Return evidence records associated with one provider catalog key."""

    return tuple(record for record in _EVIDENCE_RECORDS if record.provider_catalog_key == provider_catalog_key)


def get_model_metadata_evidence(model_name: str) -> ProviderEvidenceRecord | None:
    """Return read-only metadata evidence for a model name when registered."""

    for record in _EVIDENCE_RECORDS:
        if record.evidence_kind == "model_metadata_visibility" and record.model_name == model_name:
            return record
    return None


def summarize_provider_evidence_for_catalog_key(provider_catalog_key: str) -> dict[str, Any]:
    """Return a report-friendly evidence summary without execution authority."""

    records = get_provider_evidence_for_catalog_key(provider_catalog_key)
    metadata_record = next((record for record in records if record.evidence_kind == "model_metadata_visibility"), None)
    surface_record = next(
        (record for record in records if record.evidence_kind == "provider_surface_model_list_visibility"),
        None,
    )
    selected = metadata_record or surface_record

    if selected is None:
        return {
            "provider_evidence_status": "no_registered_provider_evidence",
            "provider_catalog_key": provider_catalog_key,
            "evidence_keys": [],
            "source_phases": [],
            "model_name": "",
            "model_count": 0,
            "metadata_format": "",
            "metadata_family": "",
            "metadata_parameter_size": "",
            "metadata_quantization_level": "",
            "accepted_meaning": "No static provider evidence is registered for this catalog key.",
            "non_proofs": list(PROVIDER_EVIDENCE_NON_PROOFS),
            "activity_flags": dict(NO_PROVIDER_EVIDENCE_ACTIVITY_FLAGS),
        }

    metadata = dict(selected.metadata)
    model_count = 0
    if surface_record is not None:
        model_count = int(surface_record.metadata.get("model_count", 0))

    return {
        "provider_evidence_status": selected.evidence_status,
        "provider_catalog_key": provider_catalog_key,
        "evidence_keys": [record.evidence_key for record in records],
        "source_phases": [record.source_phase for record in records],
        "model_name": selected.model_name,
        "model_count": model_count,
        "metadata_format": metadata.get("format", ""),
        "metadata_family": metadata.get("family", ""),
        "metadata_parameter_size": metadata.get("parameter_size", ""),
        "metadata_quantization_level": metadata.get("quantization_level", ""),
        "accepted_meaning": selected.accepted_meaning,
        "non_proofs": list(selected.non_proofs),
        "activity_flags": dict(selected.activity_flags),
    }
