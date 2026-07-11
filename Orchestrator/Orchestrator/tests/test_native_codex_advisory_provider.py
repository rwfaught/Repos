import json
import unittest

from orchestrator.local_model_reasoning_contract import (
    build_local_model_interpretation_request,
    render_local_model_interpretation_prompt,
)
from orchestrator.local_model_provider_stub import (
    AdvisoryProviderRegistry,
    ProviderInterpretationResult,
)
from orchestrator.native_codex_advisory_provider import (
    CodexInvocationConfig,
    CodexProcessResult,
    NativeCodexAdvisoryProvider,
    build_native_codex_invocation,
    classify_authentication_status,
    classify_process_failure,
)


def valid_payload(request):
    return {
        "contract_version": "local_model_reasoning_v1", "request_id": request.request_id,
        "objective": request.objective, "normalized_objective": request.objective.lower(),
        "capability_task": {
            "task_id": "task-001", "title": "Classify labels", "objective": request.objective,
            "complexity": "simple", "code_generation_required": False, "long_context_required": False,
            "safety_risk": "low", "privacy_sensitivity": "internal", "external_tool_or_api_need": False,
            "live_runtime_execution_need": False, "tolerance_for_mistakes": "medium",
            "deterministic_validation_available": True, "local_model_output_reviewable": True,
        },
        "matched_signals": {"deterministic": ["fixed labels"]}, "confidence": 0.91,
        "clarification_needed": [], "risk_flags": [], "assumptions": [],
    }


def jsonl_response(request, payload=None, *, model="gpt-5.5"):
    payload = payload or valid_payload(request)
    return "\n".join((
        json.dumps({"type": "thread.started", "thread_id": "thr-test"}),
        json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": json.dumps(payload)}}),
        json.dumps({"type": "turn.completed", "model": model}),
    ))


class NativeCodexProviderTests(unittest.TestCase):
    def setUp(self):
        self.request = build_local_model_interpretation_request("prompt-001", "Classify labels")
        self.config = CodexInvocationConfig()

    def provider(self, process, auth="subscription_authenticated"):
        return NativeCodexAdvisoryProvider(
            self.config,
            process_runner=lambda args, timeout, prompt: process,
            auth_checker=lambda executable: auth,
        )

    def test_invocation_is_wsl_gpt55_read_only_no_approval_and_no_credentials(self):
        args = build_native_codex_invocation(self.config, "prompt")
        self.assertEqual(args[:3], ("wsl.exe", "-e", "/home/roger/.local/bin/codex"))
        self.assertIn("--model", args)
        self.assertEqual(args[args.index("--model") + 1], "gpt-5.5")
        self.assertIn(("--sandbox", "read-only"), zip(args, args[1:]))
        self.assertIn(("--ask-for-approval", "never"), zip(args, args[1:]))
        self.assertNotIn("OPENAI_API_KEY", args)
        self.assertNotIn("CODEX_API_KEY", args)
        self.assertNotIn("prompt", args)

    def test_subscription_auth_is_distinct_and_api_key_is_blocked(self):
        self.assertEqual(classify_authentication_status("Logged in using ChatGPT"), "subscription_authenticated")
        self.assertEqual(classify_authentication_status("\x1b[31mLogged in using ChatGPT\x1b[0m"), "subscription_authenticated")
        self.assertEqual(classify_authentication_status("Logged in using API key"), "api_key_path_detected_not_authorized")
        blocked = self.provider(CodexProcessResult("", "", 0), auth="api_key_path_detected_not_authorized").interpret(self.request)
        self.assertEqual(blocked.status, "api_key_path_detected_not_authorized")
        self.assertFalse(blocked.invocation_performed)

    def test_valid_jsonl_is_extracted_preserved_and_admitted(self):
        stdout = jsonl_response(self.request)
        result = self.provider(CodexProcessResult(stdout, "progress", 0, elapsed_seconds=0.2)).interpret(self.request)
        self.assertEqual(result.status, "candidate_admitted")
        self.assertEqual(result.requested_model, "gpt-5.5")
        self.assertEqual(result.resolved_model, "gpt-5.5")
        self.assertEqual(result.raw_stdout, stdout)
        self.assertEqual(result.raw_stderr, "progress")
        self.assertEqual(result.extraction_classification, "jsonl_agent_message")
        self.assertTrue(result.invocation_performed)
        self.assertFalse(result.execution_performed)

    def test_failures_fallback(self):
        cases = (
            (CodexProcessResult("", "", 1), "non_zero_exit"),
            (CodexProcessResult("", "", -1, timed_out=True), "timeout"),
            (CodexProcessResult("", "", 0), "empty_final_response"),
            (CodexProcessResult("not json", "", 0), "malformed_jsonl"),
        )
        for process, status in cases:
            with self.subTest(status=status):
                result = self.provider(process).interpret(self.request)
                self.assertEqual(result.status, status)
                self.assertEqual(result.fallback_status, "deterministic_fallback")

    def test_authority_shaped_output_is_quarantined(self):
        payload = valid_payload(self.request)
        payload["dispatch"] = False
        result = self.provider(CodexProcessResult(jsonl_response(self.request, payload), "", 0)).interpret(self.request)
        self.assertEqual(result.status, "candidate_quarantined")
        self.assertTrue(result.authority_quarantined)
        self.assertEqual(result.validation_classification, "rejected_authority_or_execution_claim")

    def test_tool_activity_is_rejected(self):
        stdout = "\n".join((
            json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": "touch x"}}),
            json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": json.dumps(valid_payload(self.request))}}),
        ))
        result = self.provider(CodexProcessResult(stdout, "", 0)).interpret(self.request)
        self.assertEqual(result.status, "unauthorized_tool_activity")
        self.assertTrue(result.tool_activity_detected)

    def test_prompt_enumerates_only_canonical_signal_categories(self):
        prompt = render_local_model_interpretation_prompt(self.request)
        for category in ("deterministic", "local_model", "frontier", "external", "human"):
            self.assertIn(category, prompt)
        self.assertIn("only these keys", prompt)
        self.assertIn("Do not invent matched_signals keys", prompt)
        self.assertIn("clarification_needed", prompt)
        self.assertIn("advisory evidence only", prompt)

    def test_process_failure_classification_preserves_launch_evidence(self):
        args = ("wsl.exe", "-e", self.config.executable)
        self.assertEqual(
            classify_process_failure(
                CodexProcessResult("", "[WinError 2] wsl.exe not found", 127, launch_error="FileNotFoundError", process_creation_stage="windows_launcher_creation"),
                args,
            ),
            "windows_launcher_unavailable",
        )
        self.assertEqual(
            classify_process_failure(
                CodexProcessResult("", "FileNotFoundError: [WinError 206] The filename or extension is too long", 127, launch_error="FileNotFoundError", process_creation_stage="windows_launcher_creation"),
                args,
            ),
            "windows_command_line_too_long",
        )
        self.assertEqual(
            classify_process_failure(CodexProcessResult("", "Wsl is not installed", 1), args),
            "wsl_unavailable",
        )
        self.assertEqual(
            classify_process_failure(CodexProcessResult("", "no distribution found", 1), args),
            "wsl_distribution_unavailable",
        )
        self.assertEqual(
            classify_process_failure(CodexProcessResult("", "target executable unavailable", 127), args),
            "target_linux_executable_unavailable",
        )
        self.assertEqual(
            classify_process_failure(CodexProcessResult("", "permission denied", 1), args),
            "permission_denied",
        )

    def test_transport_retry_is_bounded_and_preserved_in_result(self):
        calls = []

        def runner(args, timeout, prompt):
            calls.append(args)
            return CodexProcessResult("", "temporary transport failure", 1)

        result = NativeCodexAdvisoryProvider(
            self.config,
            process_runner=runner,
            auth_checker=lambda executable: "subscription_authenticated",
        ).interpret(self.request)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result.retry_count, 1)
        self.assertEqual(result.transport_failure_classification, "non_zero_exit")
        self.assertEqual(result.fallback_status, "deterministic_fallback")

    def test_prompt_is_sent_via_stdin_and_not_argv(self):
        captured = {}

        def runner(args, timeout, prompt):
            captured["args"] = args
            captured["prompt"] = prompt
            return CodexProcessResult(jsonl_response(long_request), "", 0)

        long_request = build_local_model_interpretation_request("prompt-large", "evidence " * 10_000)
        result = NativeCodexAdvisoryProvider(
            CodexInvocationConfig(max_response_chars=500_000),
            process_runner=runner,
            auth_checker=lambda executable: "subscription_authenticated",
        ).interpret(long_request)
        self.assertEqual(result.status, "candidate_admitted")
        self.assertGreater(len(captured["prompt"]), 70_000)
        self.assertNotIn(captured["prompt"], captured["args"])
        self.assertEqual(captured["args"][-2:], ("--cd", "/tmp"))

    def test_command_line_length_failure_is_not_retried(self):
        calls = []

        def runner(args, timeout, prompt):
            calls.append((args, prompt))
            raise FileNotFoundError(206, "The filename or extension is too long")

        result = NativeCodexAdvisoryProvider(
            self.config,
            process_runner=runner,
            auth_checker=lambda executable: "subscription_authenticated",
        ).interpret(self.request)
        self.assertEqual(result.status, "windows_command_line_too_long")
        self.assertEqual(result.retry_count, 0)
        self.assertEqual(len(calls), 1)

    def test_explicit_registry_selection_keeps_fake_provider_independent_of_codex(self):
        fake = object()
        registry = AdvisoryProviderRegistry({"fake": fake})
        self.assertIs(registry.select("fake"), fake)
        with self.assertRaises(ValueError):
            registry.select("native_codex_subscription_advisory")


if __name__ == "__main__":
    unittest.main()
