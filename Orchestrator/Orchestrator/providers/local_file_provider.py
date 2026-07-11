from __future__ import annotations

import orchestrator.paths as project_paths
from orchestrator.task_schema import Task
from providers.base import BaseProvider, ProviderResult


class LocalFileProvider(BaseProvider):
    """Deterministic bounded provider for current-success demonstration work.

    This provider is intentionally not a model/runtime provider. It writes the
    operator-supplied task.expected_output to exactly one declared file in scope,
    then returns a normal provider result so the engine can persist an artifact,
    run deterministic verification, and classify the task.
    """

    provider_name = "local_file"

    def _resolve_safe_target(self, raw_target: str):
        target_text = str(raw_target or "").strip()
        if not target_text:
            raise ValueError("Local file provider requires one non-empty file path.")
        return project_paths.resolve_declared_project_path(target_text)

    def execute(self, role: str, task: Task, context: dict | None = None) -> ProviderResult:
        if len(task.files_in_scope) != 1:
            return {
                "status": "error",
                "output": None,
                "provider": self.provider_name,
                "metadata": {
                    "task_id": task.id,
                    "role": role,
                    "files_in_scope_count": len(task.files_in_scope),
                    "error_code": "scope_file_count_invalid",
                },
                "error": "Local file provider requires exactly one file in scope.",
            }

        content = task.expected_output or ""
        if not content.strip():
            return {
                "status": "error",
                "output": None,
                "provider": self.provider_name,
                "metadata": {"task_id": task.id, "role": role, "error_code": "expected_output_missing"},
                "error": "Local file provider requires non-empty task.expected_output content.",
            }

        try:
            target = self._resolve_safe_target(task.files_in_scope[0])
            existed_before = target.exists()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        except Exception as error:
            return {
                "status": "error",
                "output": None,
                "provider": self.provider_name,
                "metadata": {"task_id": task.id, "role": role, "error_code": "declared_path_invalid"},
                "error": str(error),
            }

        return {
            "status": "success",
            "output": content,
            "provider": self.provider_name,
            "metadata": {
                "task_id": task.id,
                "role": role,
                "target_path": str(target),
                "declared_file_in_scope": task.files_in_scope[0],
                "bytes_written": len(content.encode("utf-8")),
                "existed_before": existed_before,
                "deterministic_provider": True,
                "runtime_executed": False,
                "model_executed": False,
            },
            "error": None,
        }
