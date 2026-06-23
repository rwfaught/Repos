import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.route_mediated_provider_smoke_cli import run_route_mediated_provider_smoke_cli
from orchestrator.route_mediated_provider_smoke_runner import (
    DEFAULT_OLLAMA_URL,
    FUTURE_ROUTE_MARKER,
    LIVE_OLLAMA_EXECUTION_MODE,
    LIVE_TRANSPORT_FAILURE_CLASSIFICATION,
    PROMPT,
    ROUTE_PROOF_TARGET_MODEL,
    execute_route_mediated_provider_smoke_with_live_ollama_transport,
)


class FailingTransport:
    def __init__(self, exc):
        self.calls = []
        self.exc = exc

    def __call__(self, *, ollama_url, request_body):
        self.calls.append({"ollama_url": ollama_url, "request_body": request_body})
        raise self.exc


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


class Phase217RouteMediatedProviderSmokeLiveTransportFailureArtifactContractTests(unittest.TestCase):
    def test_injected_transport_exception_writes_json_safe_non_proof_artifact(self):
        transport = FailingTransport(TimeoutError("connect timed out\nwhile posting token=abc"))
        with tempfile.TemporaryDirectory() as temp_dir:
            result = execute_route_mediated_provider_smoke_with_live_ollama_transport(
                transport_callable=transport,
                output_path=temp_dir,
                **live_kwargs(),
            )
            written = Path(result.written_path)
            payload = json.loads(written.read_text(encoding="utf-8"))

        evidence = payload["captured_http_status_json_model_marker_evidence"]
        flags = payload["activity_flags"]

        self.assertFalse(result.accepted)
        self.assertEqual(result.classification, LIVE_TRANSPORT_FAILURE_CLASSIFICATION)
        self.assertEqual(payload["phase"], "PHASE_217")
        self.assertEqual(payload["mode"], "live_ollama_transport_failure_artifact")
        self.assertEqual(payload["route_marker"], "ORCH_ROUTE_PROVIDER_SMOKE_OK")
        self.assertEqual(payload["target_model"], "qwen3:30b-a3b-instruct-2507-q4_K_M")
        self.assertEqual(payload["disallowed_model"], "qwen3.6:35b-a3b")
        self.assertNotEqual(payload["target_model"], payload["disallowed_model"])
        self.assertFalse(payload["production_readiness"])
        self.assertIsNone(evidence["http_status"])
        self.assertFalse(evidence["json_parse_success"])
        self.assertEqual(evidence["returned_model"], "")
        self.assertEqual(evidence["response_text"], "")
        self.assertIsNone(evidence["done"])
        self.assertFalse(evidence["marker_present"])
        self.assertEqual(evidence["exception_type"], "TimeoutError")
        self.assertEqual(evidence["exception_message"], "connect timed out while posting token=abc")
        self.assertEqual(evidence["request_body_redacted_or_safe"]["model"], payload["target_model"])
        self.assertEqual(evidence["request_body_redacted_or_safe"]["prompt"], payload["prompt"])
        self.assertFalse(evidence["request_body_redacted_or_safe"]["stream"])
        self.assertEqual(evidence["request_body_redacted_or_safe"]["options"]["num_ctx"], 4096)
        self.assertEqual(evidence["request_body_redacted_or_safe"]["options"]["num_predict"], 64)
        self.assertEqual(evidence["request_body_redacted_or_safe"]["options"]["temperature"], 0)
        self.assertTrue(flags["route_executed"])
        self.assertFalse(flags["provider_executed"])
        self.assertTrue(flags["api_generate_called"])
        self.assertFalse(flags["ollama_executed"])
        self.assertTrue(flags["artifact_persisted"])
        self.assertTrue(payload["route_path_packet_review"]["no_runtime_proof_accepted"])
        self.assertIn("route_mediated_provider_smoke_runner_is_not_production_readiness", payload["non_proofs"])
        self.assertEqual(len(transport.calls), 1)
        json.dumps(payload, sort_keys=True)

    def test_cli_live_transport_exception_writes_artifact_and_returns_nonzero_without_traceback(self):
        transport = FailingTransport(ConnectionError("connection refused"))
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
            written = Path(result["payload"]["written_path"])
            payload = json.loads(written.read_text(encoding="utf-8"))

        self.assertEqual(result["exit_code"], 2)
        self.assertEqual(result["payload"]["phase"], "PHASE_217")
        self.assertEqual(
            result["payload"]["route_path_packet_review"]["phase_217_live_transport_failure_classification"],
            LIVE_TRANSPORT_FAILURE_CLASSIFICATION,
        )
        self.assertEqual(payload["captured_http_status_json_model_marker_evidence"]["exception_type"], "ConnectionError")
        self.assertIn("structured failure artifact written", result["error_text"])
        self.assertNotIn("Traceback", result["error_text"])
        self.assertNotIn("Traceback", result["output_text"])
        self.assertTrue(written.name.endswith("phase_217_route_mediated_provider_smoke_live_transport_failure_artifact.json"))


if __name__ == "__main__":
    unittest.main()
