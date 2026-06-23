import inspect
import json
import tempfile
import unittest
from pathlib import Path

from orchestrator import route_mediated_provider_smoke_cli, route_mediated_provider_smoke_runner
from orchestrator.route_mediated_provider_smoke_cli import run_route_mediated_provider_smoke_cli
from orchestrator.route_mediated_provider_smoke_runner import (
    DEFAULT_OLLAMA_URL,
    FUTURE_ROUTE_MARKER,
    LIVE_OLLAMA_EXECUTION_MODE,
    PROMPT,
    ROUTE_PROOF_TARGET_MODEL,
    execute_route_mediated_provider_smoke_with_live_ollama_transport,
)


FORBIDDEN_SOURCE_SNIPPETS = (
    "import requests",
    "http.client",
    "import subprocess",
    "import socket",
    "import openai",
    "import ollama",
    "orchestrator.ollama_provider",
    "api/chat",
    "api/tags",
    "api/version",
)


def successful_transport_result(*, request_body):
    return {
        "http_status": 200,
        "json_parse_success": True,
        "returned_model": request_body["model"],
        "response_text": "ORCH_ROUTE_PROVIDER_SMOKE_OK",
        "marker": "ORCH_ROUTE_PROVIDER_SMOKE_OK",
        "done": True,
        "done_reason": "stop",
    }


class RecordingTransport:
    def __init__(self, result_factory=successful_transport_result):
        self.calls = []
        self.result_factory = result_factory

    def __call__(self, *, ollama_url, request_body):
        self.calls.append({"ollama_url": ollama_url, "request_body": request_body})
        return self.result_factory(request_body=request_body)


def live_kwargs(**overrides):
    kwargs = {
        "execute_live_ollama_route_smoke": True,
        "allow_route_execution": True,
        "allow_provider_call": True,
        "allow_ollama_http": True,
        "execution_mode": LIVE_OLLAMA_EXECUTION_MODE,
        "target_model": ROUTE_PROOF_TARGET_MODEL,
        "route_marker": FUTURE_ROUTE_MARKER,
        "prompt": PROMPT,
        "production_readiness": False,
        "ollama_url": DEFAULT_OLLAMA_URL,
    }
    kwargs.update(overrides)
    return kwargs


class Phase212RouteMediatedProviderSmokeLiveTransportAdapterContractTests(unittest.TestCase):
    def test_default_runner_and_cli_still_do_not_execute_provider_model_runtime(self):
        transport = RecordingTransport()
        result = run_route_mediated_provider_smoke_cli(("--dry-run",), live_transport_callable=transport)

        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(transport.calls, [])
        self.assertFalse(result["payload"]["route_execution_allowed"])
        self.assertFalse(result["payload"]["provider_execution_allowed"])
        self.assertFalse(result["payload"]["generation_allowed"])
        self.assertFalse(result["payload"]["production_readiness"])

    def test_live_transport_adapter_rejects_missing_flags_without_invoking_transport(self):
        transport = RecordingTransport()
        cases = (
            ({"execute_live_ollama_route_smoke": False}, "missing_execute_live_ollama_route_smoke"),
            ({"allow_route_execution": False}, "missing_allow_route_execution"),
            ({"allow_provider_call": False}, "missing_allow_provider_call"),
            ({"allow_ollama_http": False}, "missing_allow_ollama_http"),
            ({"execution_mode": ""}, "missing_explicit_live_ollama_execution_mode"),
            ({"output_path": None}, "output_path_required"),
        )

        for overrides, expected in cases:
            with self.subTest(expected=expected):
                result = execute_route_mediated_provider_smoke_with_live_ollama_transport(
                    transport_callable=transport,
                    **live_kwargs(**overrides),
                )
                self.assertEqual(result.classification, expected)
                self.assertFalse(result.accepted)

        self.assertEqual(transport.calls, [])

    def test_live_transport_adapter_rejects_models_marker_and_production_readiness(self):
        transport = RecordingTransport()
        with tempfile.TemporaryDirectory() as temp_dir:
            cases = (
                ({"target_model": "qwen3.6:35b-a3b"}, "disallowed_35b_target_rejected"),
                ({"target_model": "qwen3.6:27b"}, "fallback_candidate_not_active_target"),
                ({"route_marker": "ORCH_PROVIDER_SMOKE_OK"}, "wrong_route_marker"),
                ({"prompt": "Return exactly: ORCH_PROVIDER_SMOKE_OK"}, "wrong_prompt"),
                ({"production_readiness": True}, "production_readiness_claim_rejected"),
            )
            for overrides, expected in cases:
                with self.subTest(expected=expected):
                    result = execute_route_mediated_provider_smoke_with_live_ollama_transport(
                        transport_callable=transport,
                        output_path=temp_dir,
                        **live_kwargs(**overrides),
                    )
                    self.assertEqual(result.classification, expected)
                    self.assertFalse(result.accepted)

        self.assertEqual(transport.calls, [])

    def test_injected_transport_receives_exact_url_model_prompt_options_and_writes_artifact(self):
        transport = RecordingTransport()
        with tempfile.TemporaryDirectory() as temp_dir:
            result = execute_route_mediated_provider_smoke_with_live_ollama_transport(
                transport_callable=transport,
                output_path=temp_dir,
                **live_kwargs(),
            )
            written = Path(result.written_path)
            payload = json.loads(written.read_text(encoding="utf-8"))

        self.assertEqual(
            transport.calls,
            [
                {
                    "ollama_url": "http://127.0.0.1:11434",
                    "request_body": {
                        "model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
                        "prompt": "Return exactly: ORCH_ROUTE_PROVIDER_SMOKE_OK",
                        "stream": False,
                        "options": {"num_ctx": 4096, "num_predict": 64, "temperature": 0},
                    },
                }
            ],
        )
        self.assertTrue(result.accepted)
        self.assertEqual(result.classification, "test_injected_live_transport_shape_valid_not_runtime_proof")
        self.assertEqual(payload["phase"], "PHASE_212")
        self.assertEqual(payload["artifact_kind"], "route_mediated_provider_smoke_live_transport_adapter_contract")
        self.assertEqual(payload["route_marker"], "ORCH_ROUTE_PROVIDER_SMOKE_OK")
        self.assertEqual(payload["target_model"], "qwen3:30b-a3b-instruct-2507-q4_K_M")
        self.assertEqual(payload["disallowed_model"], "qwen3.6:35b-a3b")
        self.assertEqual(payload["fallback_candidate"], "qwen3.6:27b")
        self.assertEqual(payload["ollama_url"], "http://127.0.0.1:11434")
        self.assertEqual(payload["persisted_artifact_path_evidence"]["path"], str(written))
        self.assertTrue(payload["activity_flags"]["artifact_persisted"])
        self.assertFalse(payload["production_readiness"])
        json.dumps(payload, sort_keys=True)

    def test_runtime_pass_classification_is_reserved_for_non_injected_live_http_evidence(self):
        transport = RecordingTransport()
        with tempfile.TemporaryDirectory() as temp_dir:
            result = execute_route_mediated_provider_smoke_with_live_ollama_transport(
                transport_callable=transport,
                output_path=temp_dir,
                **live_kwargs(),
            )

        self.assertNotEqual(result.classification, "route_mediated_provider_smoke_runtime_marker_pass")
        self.assertEqual(
            result.payload["route_path_packet_review"]["runtime_pass_classification_reserved_for_non_injected_live_http"],
            "route_mediated_provider_smoke_runtime_marker_pass",
        )

    def test_direct_provider_marker_and_wrong_returned_model_remain_rejected(self):
        direct_transport = RecordingTransport(
            lambda *, request_body: {
                "http_status": 200,
                "json_parse_success": True,
                "returned_model": request_body["model"],
                "response_text": "ORCH_PROVIDER_SMOKE_OK",
                "marker": "ORCH_PROVIDER_SMOKE_OK",
                "done": True,
            }
        )
        wrong_model_transport = RecordingTransport(
            lambda *, request_body: {
                "http_status": 200,
                "json_parse_success": True,
                "returned_model": "qwen3.6:35b-a3b",
                "response_text": "ORCH_ROUTE_PROVIDER_SMOKE_OK",
                "marker": "ORCH_ROUTE_PROVIDER_SMOKE_OK",
                "done": True,
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            direct_result = execute_route_mediated_provider_smoke_with_live_ollama_transport(
                transport_callable=direct_transport,
                output_path=temp_dir,
                **live_kwargs(),
            )
            wrong_model_result = execute_route_mediated_provider_smoke_with_live_ollama_transport(
                transport_callable=wrong_model_transport,
                output_path=temp_dir,
                **live_kwargs(),
            )

        self.assertFalse(direct_result.accepted)
        self.assertEqual(direct_result.classification, "direct_provider_marker_not_route_mediated_proof")
        self.assertFalse(wrong_model_result.accepted)
        self.assertEqual(wrong_model_result.classification, "wrong_route_model")

    def test_cli_live_flags_require_out_dir_and_can_use_injected_transport(self):
        transport = RecordingTransport()
        missing_out = run_route_mediated_provider_smoke_cli(
            (
                "--execute-live-ollama-route-smoke",
                "--allow-route-execution",
                "--allow-provider-call",
                "--allow-ollama-http",
            ),
            live_transport_callable=transport,
        )
        self.assertEqual(missing_out["exit_code"], 2)
        self.assertEqual(transport.calls, [])

        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_route_mediated_provider_smoke_cli(
                (
                    "--execute-live-ollama-route-smoke",
                    "--allow-route-execution",
                    "--allow-provider-call",
                    "--allow-ollama-http",
                    "--out-dir",
                    temp_dir,
                ),
                live_transport_callable=transport,
            )

        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["payload"]["phase"], "PHASE_212")
        self.assertEqual(result["payload"]["request_body_redacted_or_safe"]["options"]["num_ctx"], 4096)
        self.assertEqual(transport.calls[0]["request_body"]["options"]["num_predict"], 64)

    def test_sources_do_not_import_third_party_or_call_forbidden_runtime_surfaces(self):
        source = inspect.getsource(route_mediated_provider_smoke_runner) + inspect.getsource(route_mediated_provider_smoke_cli)

        for forbidden in FORBIDDEN_SOURCE_SNIPPETS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
