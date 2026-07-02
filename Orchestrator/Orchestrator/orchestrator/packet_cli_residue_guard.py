from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.paths import PROJECT_ROOT


_NO_ACTIVITY_FLAGS = {
    "cleanup_performed": False,
    "delete_performed": False,
    "archive_performed": False,
    "cleanup_authority_claimed": False,
    "model_executed": False,
    "runtime_executed": False,
    "platform_invoked": False,
    "live_provider_invoked": False,
    "ollama_invoked": False,
    "openclaw_invoked": False,
    "hermes_invoked": False,
    "discord_invoked": False,
    "installer_invoked": False,
    "autonomous_ai_coding_claimed": False,
    "production_readiness_claimed": False,
    "semantic_correctness_claimed": False,
}

_NON_PROOFS = [
    "no_cleanup_delete_archive_authority",
    "no_semantic_correctness_proof",
    "no_live_provider_model_proof",
    "no_runtime_platform_proof",
    "no_autonomous_ai_coding_proof",
    "no_production_readiness_proof",
]

_RESIDUE_DIRS = {
    "outputs": "outputs",
    "task_records": "data/tasks",
    "artifact_records": "data/artifacts",
    "verifier_results": "data/verifier_results",
}


def _relative_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _is_reportable_child(path: Path) -> bool:
    return path.name != ".gitkeep"


def inspect_packet_cli_generated_residue(project_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(project_root) if project_root is not None else PROJECT_ROOT
    root = root.resolve()

    generated_paths: list[str] = []
    residue_classes: dict[str, list[str]] = {}

    for residue_class, relative_dir in _RESIDUE_DIRS.items():
        directory = (root / relative_dir).resolve()
        class_paths: list[str] = []
        if directory.exists():
            for child in sorted(directory.rglob("*")):
                if not child.is_file() or not _is_reportable_child(child):
                    continue
                class_paths.append(_relative_path(child, root))
        residue_classes[residue_class] = class_paths
        generated_paths.extend(class_paths)

    generated_paths = sorted(set(generated_paths))

    return {
        "packet_cli_generated_residue_guard_surface": True,
        "residue_present": bool(generated_paths),
        "generated_paths": generated_paths,
        "residue_classes": residue_classes,
        "report_only": True,
        "cleanup_performed": False,
        "delete_performed": False,
        "archive_performed": False,
        "cleanup_authority_claimed": False,
        "operator_next_action": (
            "inspect_reported_generated_paths_under_explicit_cleanup_or_acceptance_boundary"
            if generated_paths
            else "packet_cli_generated_residue_guard_clean"
        ),
        "no_activity_flags": dict(_NO_ACTIVITY_FLAGS),
        "non_proofs": list(_NON_PROOFS),
    }
