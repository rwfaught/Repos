from providers.base import BaseProvider, ProviderResult
from orchestrator.task_schema import Task


class MockProvider(BaseProvider):
    def execute(self, role: str, task: Task, context: dict | None = None) -> ProviderResult:
        return {
            "status": "success",
            "output": f"Mock execution complete for task {task.id} ({task.title}) as role {role}.",
            "provider": "mock",
            "metadata": {"task_id": task.id, "role": role},
            "error": None,
        }
