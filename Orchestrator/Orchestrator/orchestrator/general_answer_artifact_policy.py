"""Deterministic general-answer artifact persistence policy.

The policy is report-only metadata. It does not create paths, write files,
execute providers/models/runtimes, dispatch workers, perform lookup, or expose
service/API/UI behavior.
"""

from __future__ import annotations


def build_general_answer_artifact_persistence_policy(write_review_json_path: str | None) -> dict[str, object]:
    """Return the JSON-safe persistence/default-surfacing policy."""

    persistence_requested = bool(write_review_json_path)
    return {
        "artifact_persistence_requested": persistence_requested,
        "artifact_path_required": persistence_requested,
        "artifact_path_source": "caller_supplied" if persistence_requested else "none",
        "default_artifact_path_enabled": False,
        "default_artifact_path": None,
        "artifact_write_notice_on_success": persistence_requested,
        "artifact_write_notice_when_omitted": False,
        "artifact_write_notice_for_rejected_input": False,
        "fixture_mode_artifact_persistence": False,
        "report_only": True,
        "production_readiness": False,
        "provider_execution": False,
        "model_execution": False,
        "runtime_execution": False,
        "rag_lookup": False,
        "web_lookup": False,
        "scheduler_execution": False,
        "connector_execution": False,
        "worker_dispatch": False,
        "codex_dispatch": False,
        "service_api_ui": False,
    }
