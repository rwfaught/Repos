from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request

from orchestrator.task_schema import Task
from providers.base import BaseProvider, ProviderResult


DEFAULT_OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434/api/generate")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_PROVIDER_CONTRACT = "ollama_generate_v1"
OLLAMA_TASK_OUTPUT_STATUSES = {"completed", "blocked", "needs_review"}
OLLAMA_TASK_OUTPUT_FIELDS = {"task_id", "status", "summary", "evidence", "files_touched", "caveats"}
OLLAMA_PROSPECTIVE_LANGUAGE_PHRASES = [
    "i will",
    "i'll",
    "i can",
    "i would",
    "i plan",
    "future steps",
    "next i",
    "next, i",
    "will execute",
]


def _brief_lines(items: list[str], limit: int = 8) -> str:
    if not items:
        return "- (none)"

    clipped = items[:limit]
    lines = [f"- {item}" for item in clipped]

    if len(items) > limit:
        lines.append(f"- ... ({len(items) - limit} more)")

    return "\n".join(lines)


def _context_string(context: dict[str, Any] | None, key: str, default: str) -> str:
    value = (context or {}).get(key)
    if value is None:
        return default

    text = str(value).strip()
    return text or default


def _task_output_contract() -> str:
    return (
        "OUTPUT CONTRACT\n"
        "Return JSON-only output. The entire response must be one raw JSON object string.\n"
        "Do not include Markdown fences, prose before or after the JSON object, or example output.\n"
        "The JSON object must contain exactly these task result fields: task_id, status, summary, evidence, files_touched, caveats.\n"
        "task_id must equal the Task ID above.\n"
        "status must be one of: completed, blocked, needs_review.\n"
        "summary must be a non-empty string describing what was completed, blocked, or needs review.\n"
        "evidence must be a non-empty list of strings with concrete evidence for the status.\n"
        "files_touched must be a list of strings; use an empty list if no files were touched.\n"
        "caveats must be a list of strings; use an empty list when there are no caveats.\n"
        "Do not use prospective language such as 'I will', 'I can', 'I would', 'I'll', 'next I', 'future steps', or 'will execute' unless quoting source evidence.\n"
        "Do not describe future steps or include a sample Hello World/example response.\n"
    )


def _reviewer_output_contract() -> str:
    return (
        "REVIEWER OUTPUT CONTRACT\n"
        "Return JSON-only output. The entire response must be one raw JSON object string.\n"
        "Do not include Markdown fences, prose before or after the JSON object, or example output.\n"
        "The JSON object must contain exactly these reviewer recommendation fields: recommendation_type, reason.\n"
        "recommendation_type must be one of: accept_result, manual_followup, repair_candidate.\n"
        "reason must be a non-empty string explaining the recommendation.\n"
    )


def _build_prompt(role: str, task: Task, context: dict[str, Any] | None = None) -> str:
    context_data = context or {}
    role_prompt = str(context_data.get("role_prompt", "")).strip() or "(no role prompt provided)"

    success_criteria = [str(item) for item in task.success_criteria]
    files_in_scope = [str(item) for item in task.files_in_scope]
    expected_output = str(task.expected_output).strip() if task.expected_output is not None else ""
    expected_output_section = ""
    if expected_output:
        expected_output_section = (
            "\n\n"
            "EXPECTED OUTPUT\n"
            f"{expected_output}\n"
        )

    output_contract = _reviewer_output_contract() if role.strip().lower() == "reviewer" else _task_output_contract()

    return (
        "ROLE INSTRUCTIONS\n"
        f"{role_prompt}\n\n"
        "TASK\n"
        f"Title: {task.title}\n"
        f"Role: {role}\n"
        f"Task ID: {task.id}\n\n"
        "SUCCESS CRITERIA\n"
        f"{_brief_lines(success_criteria)}\n\n"
        "FILES IN SCOPE\n"
        f"{_brief_lines(files_in_scope)}"
        f"{expected_output_section}\n\n"
        f"{output_contract}"
    )


def parse_ollama_task_output(output_text: str) -> dict[str, Any]:
    """Parse strict Ollama task output as a raw JSON object string."""
    if not isinstance(output_text, str):
        raise ValueError("output must be a string")

    raw = output_text.strip()
    if not raw:
        raise ValueError("output is missing")

    if raw.startswith("```") or raw.endswith("```"):
        raise ValueError("output must be raw JSON, not Markdown-fenced JSON")

    if not (raw.startswith("{") and raw.endswith("}")):
        raise ValueError("output must be a single raw JSON object with no prose wrapper")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"output is not valid JSON: {exc.msg}") from exc

    if not isinstance(data, dict):
        raise ValueError("output JSON must be an object")

    return data


def _require_string_field(data: dict[str, Any], field_name: str) -> tuple[bool, str]:
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        return False, f"{field_name} must be a non-empty string"
    return True, ""


def _require_string_list(data: dict[str, Any], field_name: str, *, require_item: bool = False) -> tuple[bool, str]:
    value = data.get(field_name)
    if not isinstance(value, list):
        return False, f"{field_name} must be a list of strings"

    if require_item and not value:
        return False, f"{field_name} must include at least one string"

    for index, item in enumerate(value):
        if not isinstance(item, str):
            return False, f"{field_name}[{index}] must be a string"

    return True, ""


def _contains_prospective_language(text: str) -> str | None:
    lowered = text.lower()
    for phrase in OLLAMA_PROSPECTIVE_LANGUAGE_PHRASES:
        if phrase in lowered:
            return phrase
    return None


def validate_ollama_task_output_envelope(data: dict[str, Any], task_id: str | None = None) -> tuple[bool, str]:
    """Validate the strict Ollama JSON envelope."""
    if not isinstance(data, dict):
        return False, "output JSON must be an object"

    if set(data.keys()) != OLLAMA_TASK_OUTPUT_FIELDS:
        return False, "output JSON must contain exactly task_id, status, summary, evidence, files_touched, caveats"

    ok, reason = _require_string_field(data, "task_id")
    if not ok:
        return False, reason

    actual_task_id = data["task_id"].strip()
    if task_id is not None and actual_task_id != str(task_id):
        return False, "task_id does not match task"

    status = data.get("status")
    if not isinstance(status, str) or status not in OLLAMA_TASK_OUTPUT_STATUSES:
        return False, "status must be one of completed, blocked, needs_review"

    ok, reason = _require_string_field(data, "summary")
    if not ok:
        return False, reason

    ok, reason = _require_string_list(data, "evidence", require_item=True)
    if not ok:
        return False, reason

    ok, reason = _require_string_list(data, "files_touched")
    if not ok:
        return False, reason

    ok, reason = _require_string_list(data, "caveats")
    if not ok:
        return False, reason

    texts_to_scan = [("summary", data["summary"])]
    texts_to_scan.extend((f"evidence[{index}]", value) for index, value in enumerate(data["evidence"]))
    texts_to_scan.extend((f"caveats[{index}]", value) for index, value in enumerate(data["caveats"]))

    for field_name, value in texts_to_scan:
        phrase = _contains_prospective_language(value)
        if phrase is not None:
            return False, f"{field_name} contains prospective language ({phrase})"

    return True, "Ollama output contract valid."

def _base_metadata(task: Task, role: str, model: str, api_url: str) -> dict[str, Any]:
    return {
        "task_id": task.id,
        "role": role,
        "model": model,
        "ollama_api_url": api_url,
        "provider_contract": OLLAMA_PROVIDER_CONTRACT,
        "model_backed_provider": True,
        "provider_request_attempted": False,
        "runtime_executed": False,
        "model_executed": False,
    }


class OllamaProvider(BaseProvider):
    provider_name = "ollama"

    def execute(self, role: str, task: Task, context: dict[str, Any] | None = None) -> ProviderResult:
        prompt = _build_prompt(role=role, task=task, context=context)
        model = _context_string(context, "ollama_model", DEFAULT_OLLAMA_MODEL)
        api_url = _context_string(context, "ollama_api_url", DEFAULT_OLLAMA_API_URL)
        metadata = _base_metadata(task=task, role=role, model=model, api_url=api_url)

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            req = request.Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            metadata["provider_request_attempted"] = True

            with request.urlopen(req, timeout=60) as response:
                body = response.read().decode("utf-8")

            response_data = json.loads(body)
            output = response_data.get("response")

            if not isinstance(output, str):
                return {
                    "status": "error",
                    "output": None,
                    "provider": self.provider_name,
                    "metadata": metadata,
                    "error": "Ollama response did not include a string 'response' field.",
                }

            success_metadata = dict(metadata)
            success_metadata["runtime_executed"] = True
            success_metadata["model_executed"] = True

            return {
                "status": "success",
                "output": output,
                "provider": self.provider_name,
                "metadata": success_metadata,
                "error": None,
            }

        except error.URLError as exc:
            return {
                "status": "error",
                "output": None,
                "provider": self.provider_name,
                "metadata": metadata,
                "error": f"Ollama request failed: {exc}",
            }
        except Exception as exc:
            return {
                "status": "error",
                "output": None,
                "provider": self.provider_name,
                "metadata": metadata,
                "error": str(exc),
            }
