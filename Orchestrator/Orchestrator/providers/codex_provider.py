from providers.base import BaseProvider, ProviderResult
from orchestrator.task_schema import Task


class CodexProvider(BaseProvider):
    def execute(self, role: str, task: Task, context: dict | None = None) -> ProviderResult:
        return {
            "status": "not_implemented",
            "output": None,
            "provider": "codex",
            "metadata": {"task_id": task.id, "role": role},
            "error": "Codex provider is not implemented in Phase 05.",
        }
