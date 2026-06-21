from abc import ABC, abstractmethod
from typing import Any

from orchestrator.task_schema import Task


ProviderResult = dict[str, Any]


class BaseProvider(ABC):
    @abstractmethod
    def execute(self, role: str, task: Task, context: dict[str, Any] | None = None) -> ProviderResult:
        raise NotImplementedError
