import inspect
import json
import tempfile
import unittest
from pathlib import Path

from orchestrator import route_mediated_provider_smoke_cli, route_mediated_provider_smoke_runner
from orchestrator.route_mediated_provider_smoke_cli import run_route_mediated_provider_smoke_cli
from orchestrator.route_mediated_provider_smoke_runner import (
    build_route_mediated_provider_smoke_dry_artifact,
    review_route_mediated_provider_smoke_capture,
    route_mediated_provider_smoke_artifact_to_dict,
    write_route_mediated_provider_smoke_artifact,
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
)


def complete_capture(**overrides):
    payload = {
        "request_intake_harness_evidence": {"request_id": "phase206_fake"},
        "route_recommendation_readiness_evidence": {"route": "local_model_candidate"},
        "explicit_route_execution_boundary_evidence": {"boundary": "future_operator"},
        "provider_call_through_route_path_evidence": {"path": "route_mediated"},
        "captured_http_status_json_model_marker_evidence": {"http_status": 200},
        "persisted_artifact_path_evidence": {"path": "caller_supplied.json"},
        "displayed_reviewable_outcome_evidence": {"displayed": True},
        "marker": "ORCH_ROUTE_PROVIDER_SMOKE_OK",
        "returned_model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
        "production_readiness": False,
    }
    payload.update(overrides)
    return payload


class Phase206RouteMediatedProviderSmokeRunnerContractTests(unittest.TestCase):
    def test_deterministic_dry_artifact_creation_and_json_serialization(self):
        first = build_route_mediated_provider_smoke_dry_artifact()
        second = build_route_mediated_provider_smoke_dry_artifact()

        self.assertEqual(first.payload, second.payload)
        json.dumps(first.payload, sort_keys=True)
        self.assertEqual(first.payload["phase"], "PHASE_206")
        self.assertEqual(first.payload["artifact_kind"], "route_mediated_provider_smoke_runner_contract")
        self.assertEqual(first.classification, "dry_artifact_shape_only_not_runtime_proof")
        self.assertFalse(first.accepted)

    def test_active_model_policy_and_distinct_route_marker(self):
        result = build_route_mediated_provider_smoke_dry_artifact()
        payload = result.payload

        self.assertEqual(payload["target_model"], "qwen3:30b-a3b-instruct-2507-q4_K_M")
        self.assertEqual(payload["disallowed_model"], "qwen3.6:35b-a3b")
        self.assertEqual(payload["fallback_candidate"], "qwen3.6:27b")
        self.assertNotEqual(payload["target_model"], payload["disallowed_model"])
        self.assertEqual(payload["route_marker"], "ORCH_ROUTE_PROVIDER_SMOKE_OK")
        self.assertNotEqual(payload["route_marker"], "ORCH_PROVIDER_SMOKE_OK")

    def test_default_runner_and_cli_do_not_execute_runtime_surfaces(self):
        result = build_route_mediated_provider_smoke_dry_artifact()
        cli_result = run_route_mediated_provider_smoke_cli(("--dry-run",))

        self.assertEqual(cli_result["exit_code"], 0)
        self.assertFalse(result.payload["route_execution_allowed"])
        self.assertFalse(result.payload["provider_execution_allowed"])
        self.assertFalse(result.payload["generation_allowed"])
        self.assertFalse(result.payload["production_readiness"])
        for flag, value in result.payload["activity_flags"].items():
            if flag == "dry_artifact_prepared":
                self.assertTrue(value)
            else:
                self.assertFalse(value)

    def test_fake_complete_capture_reviews_shape_valid_without_production_readiness(self):
        result = review_route_mediated_provider_smoke_capture(complete_capture())

        self.assertTrue(result.accepted)
        self.assertEqual(result.classification, "route_mediated_provider_smoke_shape_valid_review_only")
        self.assertFalse(result.payload["production_readiness"])
        self.assertFalse(result.payload["route_execution_allowed"])
        self.assertIn("review_only_does_not_execute_route", result.payload["route_path_packet_review"]["caveats"])

    def test_direct_provider_marker_missing_route_evidence_and_wrong_model_are_rejected(self):
        direct_marker = review_route_mediated_provider_smoke_capture(complete_capture(marker="ORCH_PROVIDER_SMOKE_OK"))
        missing_evidence_payload = complete_capture()
        missing_evidence_payload.pop("provider_call_through_route_path_evidence")
        missing_evidence = review_route_mediated_provider_smoke_capture(missing_evidence_payload)
        wrong_model = review_route_mediated_provider_smoke_capture(complete_capture(returned_model="qwen3.6:35b-a3b"))

        self.assertFalse(direct_marker.accepted)
        self.assertEqual(direct_marker.classification, "direct_provider_marker_not_route_mediated_proof")
        self.assertFalse(missing_evidence.accepted)
        self.assertEqual(missing_evidence.classification, "missing_route_mediated_proof_fields")
        self.assertFalse(wrong_model.accepted)
        self.assertEqual(wrong_model.classification, "wrong_route_model")

    def test_production_readiness_claim_is_rejected(self):
        result = review_route_mediated_provider_smoke_capture(complete_capture(production_readiness=True))

        self.assertFalse(result.accepted)
        self.assertEqual(result.classification, "production_readiness_claim_rejected")
        self.assertFalse(result.payload["production_readiness"])

    def test_artifact_write_uses_caller_supplied_path_without_runtime_execution(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = write_route_mediated_provider_smoke_artifact(temp_dir)
            written = Path(result.written_path)
            payload = json.loads(written.read_text(encoding="utf-8"))

        self.assertTrue(written.name.endswith(".json"))
        self.assertEqual(payload["phase"], "PHASE_206")
        self.assertTrue(payload["activity_flags"]["artifact_persisted"])
        self.assertFalse(payload["route_execution_allowed"])
        self.assertFalse(payload["provider_execution_allowed"])

    def test_cli_rejects_provider_call_flag_and_reviews_caller_supplied_capture(self):
        rejected = run_route_mediated_provider_smoke_cli(("--allow-provider-call",))
        self.assertEqual(rejected["exit_code"], 2)
        self.assertIn("requires --out-dir", rejected["error_text"])

        with tempfile.TemporaryDirectory() as temp_dir:
            capture_path = Path(temp_dir) / "capture.json"
            capture_path.write_text(json.dumps(complete_capture()), encoding="utf-8")
            reviewed = run_route_mediated_provider_smoke_cli(("--review-captured", str(capture_path)))

        self.assertEqual(reviewed["exit_code"], 0)
        self.assertEqual(reviewed["payload"]["route_marker"], "ORCH_ROUTE_PROVIDER_SMOKE_OK")
        self.assertFalse(reviewed["payload"]["production_readiness"])

    def test_sources_do_not_import_or_call_runtime_surfaces(self):
        source = inspect.getsource(route_mediated_provider_smoke_runner) + inspect.getsource(route_mediated_provider_smoke_cli)

        for forbidden in FORBIDDEN_SOURCE_SNIPPETS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
