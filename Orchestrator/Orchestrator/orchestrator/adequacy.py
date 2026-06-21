import json

from orchestrator.task_schema import Task
from providers.ollama_provider import parse_ollama_task_output, validate_ollama_task_output_envelope

DEFLECTIVE_PATTERNS = [
    "please provide",
    "need more context",
    "cannot proceed",
    "can't proceed",
    "provide files",
    "share files",
]


def _normalize_output(output: object) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output.strip()
    return json.dumps(output, ensure_ascii=True).strip()


def _is_ollama_provider_result(provider_result: dict) -> bool:
    return str(provider_result.get("provider", "")).strip().lower() == "ollama"


def _assess_ollama_output_contract(task: Task, output: object) -> tuple[bool, str, str, str | None]:
    if not isinstance(output, str) or not output.strip():
        return False, "Ollama output contract invalid: output must be a non-empty raw JSON object string.", "", None

    try:
        parsed = parse_ollama_task_output(output)
    except ValueError as exc:
        return False, f"Ollama output contract invalid: {exc}.", "", None

    valid, reason = validate_ollama_task_output_envelope(parsed, task_id=task.id)
    if not valid:
        return False, f"Ollama output contract invalid: {reason}.", "", None

    normalized_contract_text = json.dumps(parsed, ensure_ascii=True, sort_keys=True)
    return True, "Ollama output contract valid.", normalized_contract_text, str(parsed["status"])


def assess_output_adequacy(task: Task, provider_result: dict) -> dict:
    expected_output = (task.expected_output or "").strip()
    provider_status = None

    if _is_ollama_provider_result(provider_result):
        contract_valid, reason, output_text, provider_status = _assess_ollama_output_contract(
            task,
            provider_result.get("output"),
        )
        if not contract_valid:
            return {"is_adequate": False, "reason": reason, "provider_status": None}
    else:
        output_text = _normalize_output(provider_result.get("output"))

    if not output_text:
        return {"is_adequate": False, "reason": "Output is missing.", "provider_status": provider_status}

    lowered = output_text.lower()
    for pattern in DEFLECTIVE_PATTERNS:
        if pattern in lowered:
            return {
                "is_adequate": False,
                "reason": f"Output appears deflective ({pattern}).",
                "provider_status": provider_status,
            }

    if len(output_text) < 20:
        return {
            "is_adequate": False,
            "reason": "Output is trivially short for the task.",
            "provider_status": provider_status,
        }

    if expected_output and expected_output.lower() not in lowered:
        return {
            "is_adequate": False,
            "reason": "Output does not match expected_output.",
            "provider_status": provider_status,
        }

    return {
        "is_adequate": True,
        "reason": "Output is adequate.",
        "provider_status": provider_status,
    }
