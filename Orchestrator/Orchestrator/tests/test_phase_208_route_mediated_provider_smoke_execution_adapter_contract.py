import inspect
import json
import tempfile
import unittest
from pathlib import Path

from orchestrator import route_mediated_provider_smoke_cli, route_mediated_provider_smoke_runner
from orchestrator.route_mediated_provider_smoke_cli import run_route_mediated_provider_smoke_cli
from orchestrator.route_mediated_provider_smoke_runner import (
    EXECUTION_MODE,
    execute_route_mediated_provider_smoke_with_injected_provider,
)


FORBIDDEN_SOURCE_SNIPPETS = (
    "import requests",
    "urllib.request",
    "http.client",
    "import subprocess",
    "import socket",
    "import openai",
    "import ollama",
    "orchestrator.ollama_provider",
)


def successful_provider_result(*, model, prompt):
    return {
        "http_status": 200,
        "json_parse_success": True,
        "returned_model": model,
        "response_text": "ORCH_ROUTE_PROVIDER_SMOKE_OK",
        "marker": "ORCH_ROUTE_PROVIDER_SMOKE_OK",
        "done": True,
        "done_reason": "stop",
        "observed_prompt": prompt,
    }


class RecordingProvider:
    def __init__(self, result_factory=successful_provider_result):
        self.calls = []
        self.result_factory = result_factory

    def __call__(self, *, model, prompt):
        self.calls.append({"model": model, "prompt": prompt})
        return self.result_factory(model=model, prompt=prompt)


class Phase208RouteMediatedProviderSmokeExecutionAdapterContractTests(unittest.TestCase):
    def test_default_cli_still_does_not_execute_provider_model_runtime(self):
        provider = RecordingProvider()
        result = run_route_mediated_provider_smoke_cli(("--dry-run",), provider_callable=provider)

        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(provider.calls, [])
        self.assertFalse(result["payload"]["route_execution_allowed"])
        self.assertFalse(result["payload"]["provider_execution_allowed"])
        self.assertFalse(result["payload"]["generation_allowed"])
        self.assertFalse(result["payload"]["production_readiness"])

    def test_execution_adapter_rejects_missing_allow_flags_without_invoking_provider(self):
        provider = RecordingProvider()

        missing_route = execute_route_mediated_provider_smoke_with_injected_provider(
            provider_callable=provider,
            allow_provider_call=True,
            execution_mode=EXECUTION_MODE,
        )
        missing_provider = execute_route_mediated_provider_smoke_with_injected_provider(
            provider_callable=provider,
            allow_route_execution=True,
            execution_mode=EXECUTION_MODE,
        )
        missing_mode = execute_route_mediated_provider_smoke_with_injected_provider(
            provider_callable=provider,
            allow_route_execution=True,
            allow_provider_call=True,
        )

        self.assertEqual(provider.calls, [])
        self.assertEqual(missing_route.classification, "missing_allow_route_execution")
        self.assertEqual(missing_provider.classification, "missing_allow_provider_call")
        self.assertEqual(missing_mode.classification, "missing_explicit_route_smoke_execution_mode")

    def test_execution_adapter_rejects_disallowed_fallback_wrong_marker_and_production_readiness(self):
        provider = RecordingProvider()
        cases = (
            (
                {"target_model": "qwen3.6:35b-a3b"},
                "disallowed_35b_target_rejected",
            ),
            (
                {"target_model": "qwen3.6:27b"},
                "fallback_candidate_not_active_target",
            ),
            (
                {"route_marker": "ORCH_PROVIDER_SMOKE_OK"},
                "wrong_route_marker",
            ),
            (
                {"production_readiness": True},
                "production_readiness_claim_rejected",
            ),
        )

        for kwargs, expected in cases:
            with self.subTest(expected=expected):
                result = execute_route_mediated_provider_smoke_with_injected_provider(
                    provider_callable=provider,
                    allow_route_execution=True,
                    allow_provider_call=True,
                    execution_mode=EXECUTION_MODE,
                    **kwargs,
                )
                self.assertEqual(result.classification, expected)
                self.assertFalse(result.accepted)
        self.assertEqual(provider.calls, [])

    def test_fake_provider_callable_invoked_only_with_all_guards_and_receives_prompt_and_model(self):
        provider = RecordingProvider()
        result = execute_route_mediated_provider_smoke_with_injected_provider(
            provider_callable=provider,
            allow_route_execution=True,
            allow_provider_call=True,
            execution_mode=EXECUTION_MODE,
        )

        self.assertEqual(provider.calls, [{"model": "qwen3:30b-a3b-instruct-2507-q4_K_M", "prompt": "Return exactly: ORCH_ROUTE_PROVIDER_SMOKE_OK"}])
        self.assertTrue(result.accepted)
        self.assertEqual(result.classification, "fake_route_mediated_provider_smoke_shape_valid_not_runtime_proof")
        self.assertEqual(result.payload["phase"], "PHASE_208")
        self.assertEqual(result.payload["artifact_kind"], "route_mediated_provider_smoke_execution_adapter_contract")
        self.assertFalse(result.payload["production_readiness"])
        self.assertTrue(result.payload["activity_flags"]["route_executed"])
        self.assertTrue(result.payload["activity_flags"]["provider_executed"])
        self.assertTrue(result.payload["activity_flags"]["model_executed"])
        self.assertTrue(result.payload["activity_flags"]["generation_performed"])
        self.assertTrue(result.payload["activity_flags"]["api_generate_called"])
        json.dumps(result.payload, sort_keys=True)

    def test_fake_provider_direct_marker_and_wrong_returned_model_are_rejected(self):
        direct_provider = RecordingProvider(
            lambda *, model, prompt: {
                "http_status": 200,
                "json_parse_success": True,
                "returned_model": model,
                "response_text": "ORCH_PROVIDER_SMOKE_OK",
                "marker": "ORCH_PROVIDER_SMOKE_OK",
                "done": True,
            }
        )
        wrong_model_provider = RecordingProvider(
            lambda *, model, prompt: {
                "http_status": 200,
                "json_parse_success": True,
                "returned_model": "qwen3.6:35b-a3b",
                "response_text": "ORCH_ROUTE_PROVIDER_SMOKE_OK",
                "marker": "ORCH_ROUTE_PROVIDER_SMOKE_OK",
                "done": True,
            }
        )

        direct_result = execute_route_mediated_provider_smoke_with_injected_provider(
            provider_callable=direct_provider,
            allow_route_execution=True,
            allow_provider_call=True,
            execution_mode=EXECUTION_MODE,
        )
        wrong_model_result = execute_route_mediated_provider_smoke_with_injected_provider(
            provider_callable=wrong_model_provider,
            allow_route_execution=True,
            allow_provider_call=True,
            execution_mode=EXECUTION_MODE,
        )

        self.assertFalse(direct_result.accepted)
        self.assertEqual(direct_result.classification, "direct_provider_marker_not_route_mediated_proof")
        self.assertFalse(wrong_model_result.accepted)
        self.assertEqual(wrong_model_result.classification, "wrong_route_model")

    def test_persisted_artifact_path_is_recorded_for_caller_supplied_output_path(self):
        provider = RecordingProvider()
        with tempfile.TemporaryDirectory() as temp_dir:
            result = execute_route_mediated_provider_smoke_with_injected_provider(
                provider_callable=provider,
                allow_route_execution=True,
                allow_provider_call=True,
                execution_mode=EXECUTION_MODE,
                output_path=temp_dir,
            )
            written = Path(result.written_path)
            payload = json.loads(written.read_text(encoding="utf-8"))

        self.assertEqual(written.name, "phase_208_route_mediated_provider_smoke_execution_adapter_artifact.json")
        self.assertEqual(payload["persisted_artifact_path_evidence"]["path"], str(written))
        self.assertTrue(payload["activity_flags"]["artifact_persisted"])
        self.assertFalse(payload["production_readiness"])

    def test_cli_execution_flags_require_out_dir_and_can_use_injected_provider(self):
        provider = RecordingProvider()
        missing_out = run_route_mediated_provider_smoke_cli(
            ("--execute-route-smoke", "--allow-route-execution", "--allow-provider-call"),
            provider_callable=provider,
        )
        self.assertEqual(missing_out["exit_code"], 2)
        self.assertEqual(provider.calls, [])

        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_route_mediated_provider_smoke_cli(
                ("--execute-route-smoke", "--allow-route-execution", "--allow-provider-call", "--out-dir", temp_dir),
                provider_callable=provider,
            )

        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(provider.calls, [{"model": "qwen3:30b-a3b-instruct-2507-q4_K_M", "prompt": "Return exactly: ORCH_ROUTE_PROVIDER_SMOKE_OK"}])
        self.assertFalse(result["payload"]["production_readiness"])

    def test_sources_do_not_import_or_call_network_subprocess_runtime_surfaces(self):
        source = inspect.getsource(route_mediated_provider_smoke_runner) + inspect.getsource(route_mediated_provider_smoke_cli)

        for forbidden in FORBIDDEN_SOURCE_SNIPPETS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
