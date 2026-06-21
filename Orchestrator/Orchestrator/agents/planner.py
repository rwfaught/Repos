from orchestrator.paths import AGENTS_PROMPTS_DIR

ROLE_NAME = "planner"
PROMPT_PATH = AGENTS_PROMPTS_DIR / "planner.md"


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def build_payload(task_id: str, objective: str) -> dict:
    return {
        "role": ROLE_NAME,
        "task_id": task_id,
        "objective": objective,
        "prompt": load_prompt(),
    }
