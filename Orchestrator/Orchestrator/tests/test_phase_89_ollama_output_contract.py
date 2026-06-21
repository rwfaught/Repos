import json
import unittest

from orchestrator.adequacy import assess_output_adequacy
from orchestrator.task_schema import Task
from providers.ollama_provider import _build_prompt, parse_ollama_task_output, validate_ollama_task_output_envelope


class Phase89OllamaOutputContractTests(unittest.TestCase):
    def _task(self, expected_output="phase89-marker"):
        return Task(
            id="task_phase89_ollama_output_contract",
            run_id="run_phase89",
            title="Produce strict Ollama task result",
            role="coder",
            status="queued",
            dependencies=[],
            success_criteria=["Return a strict machine-reviewable task result."],
            files_in_scope=["providers/ollama_provider.py"],
            retry_count=0,
            expected_output=expected_output,
        )

    def _valid_envelope(self, **overrides):
        payload = {
            "task_id": "task_phase89_ollama_output_contract",
            "status": "completed",
            "summary": "Task completed with strict bounded result.",
            "evidence": ["Observed expected marker phase89-marker in the completed result."],
            "files_touched": ["providers/ollama_provider.py"],
            "caveats": [],
        }
        payload.update(overrides)
        return payload

    def _valid_envelope_text(self, **overrides):
        return json.dumps(self._valid_envelope(**overrides))

    def test_prompt_includes_strict_json_only_envelope_and_expected_output(self):
        task = self._task(expected_output="expected phase89 containment marker")
        prompt = _build_prompt(
            role="coder",
            task=task,
            context={"role_prompt": "You are a bounded implementation worker."},
        )

        self.assertIn("OUTPUT CONTRACT", prompt)
        self.assertIn("Return JSON-only output", prompt)
        self.assertIn("one raw JSON object string", prompt)
        self.assertIn("task_id, status, summary, evidence, files_touched, caveats", prompt)
        self.assertIn("task_id must equal the Task ID above", prompt)
        self.assertIn("status must be one of: completed, blocked, needs_review", prompt)
        self.assertIn("evidence must be a non-empty list of strings", prompt)
        self.assertIn("files_touched must be a list of strings", prompt)
        self.assertIn("caveats must be a list of strings", prompt)
        self.assertIn("Do not include Markdown fences", prompt)
        self.assertIn("prose before or after the JSON object", prompt)
        self.assertIn("Do not use prospective language", prompt)
        self.assertIn("I will", prompt)
        self.assertIn("I can", prompt)
        self.assertIn("I would", prompt)
        self.assertIn("I'll", prompt)
        self.assertIn("future steps", prompt)
        self.assertIn("will execute", prompt)
        self.assertIn("EXPECTED OUTPUT", prompt)
        self.assertIn("expected phase89 containment marker", prompt)
        self.assertNotIn("recommendation_type", prompt)
        self.assertNotIn("```", prompt)

    def test_reviewer_prompt_uses_recommendation_schema_not_task_result_schema(self):
        task = self._task(expected_output="concise review")
        task.role = "reviewer"

        prompt = _build_prompt(
            role="reviewer",
            task=task,
            context={"role_prompt": "Review the source artifact."},
        )

        self.assertIn("REVIEWER OUTPUT CONTRACT", prompt)
        self.assertIn("recommendation_type, reason", prompt)
        self.assertIn("accept_result, manual_followup, repair_candidate", prompt)
        self.assertNotIn("task_id, status, summary, evidence, files_touched, caveats", prompt)
        self.assertNotIn("status must be one of: completed, blocked, needs_review", prompt)

    def test_valid_ollama_json_envelope_passes_adequacy(self):
        task = self._task()
        result = assess_output_adequacy(
            task,
            {"provider": "ollama", "output": self._valid_envelope_text()},
        )

        self.assertTrue(result["is_adequate"], result)

    def test_plain_text_output_fails_adequacy_for_ollama(self):
        task = self._task(expected_output=None)
        result = assess_output_adequacy(
            task,
            {"provider": "ollama", "output": "Task completed with loose plaintext."},
        )

        self.assertFalse(result["is_adequate"])
        self.assertIn("Ollama output contract invalid:", result["reason"])

    def test_markdown_fenced_json_fails_adequacy_for_ollama(self):
        task = self._task(expected_output=None)
        fenced = "```json\n" + self._valid_envelope_text() + "\n```"
        result = assess_output_adequacy(task, {"provider": "ollama", "output": fenced})

        self.assertFalse(result["is_adequate"])
        self.assertIn("Ollama output contract invalid:", result["reason"])
        self.assertIn("Markdown-fenced", result["reason"])

    def test_prose_wrapped_json_fails_adequacy_for_ollama(self):
        task = self._task(expected_output=None)
        wrapped = "Here is the result: " + self._valid_envelope_text()
        result = assess_output_adequacy(task, {"provider": "ollama", "output": wrapped})

        self.assertFalse(result["is_adequate"])
        self.assertIn("Ollama output contract invalid:", result["reason"])
        self.assertIn("no prose wrapper", result["reason"])

    def test_prospective_language_fails_adequacy_for_ollama(self):
        task = self._task(expected_output=None)
        payload = self._valid_envelope()
        payload["summary"] = "I will execute this task and report the result."
        result = assess_output_adequacy(task, {"provider": "ollama", "output": json.dumps(payload)})

        self.assertFalse(result["is_adequate"])
        self.assertIn("Ollama output contract invalid:", result["reason"])
        self.assertIn("prospective language", result["reason"])
        self.assertIn("i will", result["reason"])

    def test_invalid_status_fails_contract(self):
        result = assess_output_adequacy(
            self._task(expected_output=None),
            {"provider": "ollama", "output": self._valid_envelope_text(status="success")},
        )

        self.assertFalse(result["is_adequate"])
        self.assertIn("Ollama output contract invalid:", result["reason"])
        self.assertIn("status must be one of", result["reason"])

    def test_missing_and_extra_fields_fail_contract(self):
        missing = self._valid_envelope()
        del missing["summary"]
        extra = self._valid_envelope(unexpected="value")

        for payload in (missing, extra):
            with self.subTest(payload=payload):
                result = assess_output_adequacy(
                    self._task(expected_output=None),
                    {"provider": "ollama", "output": json.dumps(payload)},
                )
                self.assertFalse(result["is_adequate"])
                self.assertIn("Ollama output contract invalid:", result["reason"])
                self.assertIn("contain exactly", result["reason"])

    def test_task_id_mismatch_fails_contract(self):
        result = assess_output_adequacy(
            self._task(expected_output=None),
            {"provider": "ollama", "output": self._valid_envelope_text(task_id="wrong_task")},
        )

        self.assertFalse(result["is_adequate"])
        self.assertIn("task_id does not match task", result["reason"])

    def test_empty_summary_and_evidence_fail_contract(self):
        payloads = [
            self._valid_envelope(summary=""),
            self._valid_envelope(evidence=[]),
        ]

        for payload in payloads:
            with self.subTest(payload=payload):
                result = assess_output_adequacy(
                    self._task(expected_output=None),
                    {"provider": "ollama", "output": json.dumps(payload)},
                )
                self.assertFalse(result["is_adequate"])
                self.assertIn("Ollama output contract invalid:", result["reason"])

    def test_invalid_json_and_non_object_json_fail_contract(self):
        for output in ('{"task_id":', '["not", "an", "object"]'):
            with self.subTest(output=output):
                result = assess_output_adequacy(
                    self._task(expected_output=None),
                    {"provider": "ollama", "output": output},
                )
                self.assertFalse(result["is_adequate"])
                self.assertIn("Ollama output contract invalid:", result["reason"])

    def test_prospective_language_in_evidence_and_caveats_fails_contract(self):
        payloads = [
            self._valid_envelope(evidence=["I can provide evidence later."]),
            self._valid_envelope(caveats=["Future steps include another execution."]),
        ]

        for payload in payloads:
            with self.subTest(payload=payload):
                result = assess_output_adequacy(
                    self._task(expected_output=None),
                    {"provider": "ollama", "output": json.dumps(payload)},
                )
                self.assertFalse(result["is_adequate"])
                self.assertIn("prospective language", result["reason"])

    def test_valid_envelope_exposes_semantic_provider_status(self):
        task = self._task(expected_output=None)

        for status in ("completed", "blocked", "needs_review"):
            with self.subTest(status=status):
                result = assess_output_adequacy(
                    task,
                    {"provider": "ollama", "output": self._valid_envelope_text(status=status)},
                )
                self.assertTrue(result["is_adequate"], result)
                self.assertEqual(result["provider_status"], status)

    def test_non_ollama_provider_keeps_existing_adequacy_rules_without_json_requirement(self):
        task = self._task(expected_output="plain expected marker")
        result = assess_output_adequacy(
            task,
            {
                "provider": "mock",
                "output": "This non-Ollama plaintext output includes the plain expected marker and remains adequate.",
            },
        )

        self.assertTrue(result["is_adequate"], result)

    def test_parser_and_validator_accept_valid_raw_json_object(self):
        data = parse_ollama_task_output(self._valid_envelope_text())
        valid, reason = validate_ollama_task_output_envelope(
            data,
            task_id="task_phase89_ollama_output_contract",
        )

        self.assertTrue(valid, reason)


if __name__ == "__main__":
    unittest.main()
