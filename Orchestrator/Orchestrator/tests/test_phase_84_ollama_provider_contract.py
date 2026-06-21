import json
import unittest
from urllib import error
from unittest.mock import patch

from orchestrator.dispatcher import dispatch_task
from orchestrator.task_schema import Task
from providers import ollama_provider
from providers.ollama_provider import OllamaProvider


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


class Phase84OllamaProviderContractTests(unittest.TestCase):
    def _task(self):
        return Task(
            id="task_phase84_ollama_contract",
            run_id="run_phase84",
            title="Produce bounded model-backed provider output",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=[
                "Return bounded provider output.",
                "Preserve the task id in provider metadata.",
            ],
            files_in_scope=["demo/phase84_ollama_contract.py"],
            retry_count=0,
            expected_output=None,
        )

    def test_ollama_provider_posts_generate_payload_and_returns_model_metadata(self):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            captured["timeout"] = timeout
            captured["payload"] = json.loads(req.data.decode("utf-8"))
            captured["content_type"] = req.get_header("Content-type") or req.get_header("Content-Type")
            return _FakeResponse({"response": "bounded model output"})

        task = self._task()

        with patch.object(ollama_provider.request, "urlopen", side_effect=fake_urlopen):
            result = OllamaProvider().execute(
                role="coder",
                task=task,
                context={
                    "role_prompt": "You are a bounded coder.",
                    "ollama_model": "phase84-test-model",
                    "ollama_api_url": "http://127.0.0.1:11434/api/generate",
                },
            )

        self.assertEqual(result.get("status"), "success")
        self.assertEqual(result.get("provider"), "ollama")
        self.assertEqual(result.get("output"), "bounded model output")
        self.assertEqual(captured["url"], "http://127.0.0.1:11434/api/generate")
        self.assertEqual(captured["timeout"], 60)
        self.assertEqual(captured["payload"]["model"], "phase84-test-model")
        self.assertFalse(captured["payload"]["stream"])
        self.assertIn("Produce bounded model-backed provider output", captured["payload"]["prompt"])
        self.assertIn("You are a bounded coder.", captured["payload"]["prompt"])
        self.assertIn("demo/phase84_ollama_contract.py", captured["payload"]["prompt"])
        self.assertIn("OUTPUT CONTRACT", captured["payload"]["prompt"])
        self.assertIn("Return JSON-only output", captured["payload"]["prompt"])
        self.assertIn("one raw JSON object string", captured["payload"]["prompt"])
        self.assertIn("task_id, status, summary, evidence, files_touched, caveats", captured["payload"]["prompt"])
        self.assertIn("Do not include Markdown fences", captured["payload"]["prompt"])
        self.assertIn("prose before or after the JSON object", captured["payload"]["prompt"])
        self.assertIn("Do not use prospective language", captured["payload"]["prompt"])
        self.assertIn("I will", captured["payload"]["prompt"])
        self.assertIn("future steps", captured["payload"]["prompt"])
        self.assertIn("will execute", captured["payload"]["prompt"])

        metadata = result.get("metadata", {})
        self.assertEqual(metadata.get("task_id"), "task_phase84_ollama_contract")
        self.assertEqual(metadata.get("role"), "coder")
        self.assertEqual(metadata.get("model"), "phase84-test-model")
        self.assertEqual(metadata.get("provider_contract"), "ollama_generate_v1")
        self.assertTrue(metadata.get("model_backed_provider"))
        self.assertTrue(metadata.get("provider_request_attempted"))
        self.assertTrue(metadata.get("runtime_executed"))
        self.assertTrue(metadata.get("model_executed"))

    def test_ollama_provider_reports_request_failure_without_model_execution(self):
        task = self._task()

        with patch.object(
            ollama_provider.request,
            "urlopen",
            side_effect=error.URLError("phase84 simulated connection failure"),
        ):
            result = OllamaProvider().execute(
                role="coder",
                task=task,
                context={"ollama_model": "phase84-test-model"},
            )

        self.assertEqual(result.get("status"), "error")
        self.assertEqual(result.get("provider"), "ollama")
        self.assertIn("Ollama request failed", result.get("error", ""))

        metadata = result.get("metadata", {})
        self.assertTrue(metadata.get("model_backed_provider"))
        self.assertTrue(metadata.get("provider_request_attempted"))
        self.assertFalse(metadata.get("runtime_executed"))
        self.assertFalse(metadata.get("model_executed"))

    def test_ollama_provider_rejects_missing_string_response_field(self):
        task = self._task()

        with patch.object(
            ollama_provider.request,
            "urlopen",
            return_value=_FakeResponse({"not_response": "missing"}),
        ):
            result = OllamaProvider().execute(
                role="coder",
                task=task,
                context={"ollama_model": "phase84-test-model"},
            )

        self.assertEqual(result.get("status"), "error")
        self.assertIn("string 'response' field", result.get("error", ""))

        metadata = result.get("metadata", {})
        self.assertTrue(metadata.get("provider_request_attempted"))
        self.assertFalse(metadata.get("runtime_executed"))
        self.assertFalse(metadata.get("model_executed"))

    def test_dispatcher_routes_ollama_provider_under_mocked_http(self):
        task = self._task()

        with patch.object(
            ollama_provider.request,
            "urlopen",
            return_value=_FakeResponse({"response": "dispatcher-routed output"}),
        ):
            result = dispatch_task(
                task,
                provider_name="ollama",
                context={
                    "ollama_model": "phase84-dispatcher-test-model",
                    "ollama_api_url": "http://127.0.0.1:11434/api/generate",
                },
            )

        self.assertEqual(result.get("status"), "success")
        self.assertEqual(result.get("provider"), "ollama")
        self.assertEqual(result.get("output"), "dispatcher-routed output")
        self.assertEqual(result.get("metadata", {}).get("model"), "phase84-dispatcher-test-model")


if __name__ == "__main__":
    unittest.main()
