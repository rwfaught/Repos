from agents.coder import load_prompt as load_coder_prompt
from agents.planner import load_prompt as load_planner_prompt
from agents.reviewer import load_prompt as load_reviewer_prompt
from orchestrator.task_schema import Task
from providers.base import BaseProvider
from providers.codex_provider import CodexProvider
from providers.mock_provider import MockProvider
from providers.ollama_provider import OllamaProvider
from providers.local_file_provider import LocalFileProvider

ROLE_PROMPT_LOADERS = {
    "planner": load_planner_prompt,
    "coder": load_coder_prompt,
    "reviewer": load_reviewer_prompt,
}


def _get_provider(provider_name: str = "mock") -> BaseProvider | None:
    if provider_name == "mock":
        return MockProvider()
    if provider_name == "local_file":
        return LocalFileProvider()
    if provider_name == "ollama":
        return OllamaProvider()
    if provider_name == "codex":
        return CodexProvider()
    return None


def dispatch_task(task: Task, provider_name: str = "mock", context: dict | None = None, provider: BaseProvider | None = None) -> dict:
    role_prompt = None
    prompt_loader = ROLE_PROMPT_LOADERS.get(task.role)
    if prompt_loader is not None:
        role_prompt = prompt_loader()

    dispatch_context = dict(context or {})
    if role_prompt is not None:
        dispatch_context["role_prompt"] = role_prompt

    active_provider = provider or _get_provider(provider_name)
    if active_provider is None:
        return {
            "status": "error",
            "output": None,
            "provider": provider_name,
            "metadata": {"task_id": task.id, "role": task.role},
            "error": f"Unknown provider requested: {provider_name}",
        }

    return active_provider.execute(role=task.role, task=task, context=dispatch_context)
