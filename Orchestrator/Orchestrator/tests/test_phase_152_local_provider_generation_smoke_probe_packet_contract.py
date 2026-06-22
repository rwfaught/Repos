import inspect
import unittest

from orchestrator import coordinator_review_report, provider_generation_smoke_probe_packet
from orchestrator.manual_review_runner import run_named_fixture_review
from orchestrator.provider_generation_smoke_probe_packet import (
    get_local_provider_generation_smoke_probe_packet,
    provider_generation_smoke_probe_packet_to_dict,
    summarize_provider_generation_smoke_probe_packet,
)


FORBIDDEN_RUNTIME_IMPORTS = (
    "import subprocess",
    "import requests",
    "import socket",
    "import urllib",
    "import openai",
    "import ollama",
    "import discord",
    "from providers",
    "import providers",
    "from orchestrator.providers",
    "from orchestrator.platform",
    "from orchestrator.scheduler",
    "from orchestrator.connector",
    "from orchestrator.openclaw",
    "from orchestrator.hermes",
    "from orchestrator.wsl",
)


class Phase152LocalProviderGenerationSmokeProbePacketContractTests(unittest.TestCase):
    def test_smoke_probe_packet_exists_and_is_deterministic(self):
        first = get_local_provider_generation_smoke_probe_packet()
        second = get_local_provider_generation_smoke_probe_packet()

        self.assertEqual(first, second)
        self.assertEqual(first.packet_key, "local_provider_generation_smoke_probe_packet")
        self.assertIn("packet_contract_only=true", summarize_provider_generation_smoke_probe_packet(first))

    def test_packet_targets_local_model_candidate_and_qwen_model(self):
        packet = get_local_provider_generation_smoke_probe_packet()

        self.assertEqual(packet.provider_catalog_key, "local_model_candidate")
        self.assertEqual(packet.model_name, "qwen3.6:27b")
        self.assertEqual(packet.future_boundary, "PHASE_157_LOCAL_PROVIDER_GENERATION_SMOKE_PROBE_27B_OPERATOR_PROOF")

    def test_api_generate_is_future_endpoint_shape_only(self):
        packet = get_local_provider_generation_smoke_probe_packet()

        self.assertEqual(packet.endpoint_surface, "local_ollama_http")
        self.assertEqual(packet.endpoint_path, "/api/generate")
        self.assertEqual(packet.method, "POST")
        self.assertFalse(packet.activity_flags["api_generate_called"])
        self.assertFalse(packet.activity_flags["generation_performed"])

    def test_packet_requires_acceptance_and_preserves_all_permissions_false(self):
        packet = get_local_provider_generation_smoke_probe_packet()

        self.assertTrue(packet.coordinator_acceptance_required)
        self.assertFalse(packet.provider_selection_allowed)
        self.assertFalse(packet.provider_execution_allowed)
        self.assertFalse(packet.generation_allowed_now)
        self.assertFalse(packet.route_execution_allowed)
        self.assertFalse(packet.production_readiness)
        self.assertTrue(all(flag is False for flag in packet.activity_flags.values()))

    def test_request_shape_is_descriptive_not_executable(self):
        packet = get_local_provider_generation_smoke_probe_packet()

        self.assertEqual(packet.request_shape["model"], "qwen3.6:27b")
        self.assertEqual(packet.request_shape["prompt"], "Return exactly: ORCH_PROVIDER_SMOKE_OK")
        self.assertIs(packet.request_shape["stream"], False)
        self.assertEqual(packet.request_shape["tool_calls"], "none")
        self.assertEqual(packet.request_shape["external_lookup"], "none")
        self.assertEqual(packet.request_shape["route_execution"], "none")

    def test_operator_evidence_and_acceptance_criteria_are_conservative(self):
        packet = get_local_provider_generation_smoke_probe_packet()

        evidence = packet.operator_evidence_to_capture
        self.assertIn("http_status_code", evidence)
        self.assertIn("content_type", evidence)
        self.assertIn("response_bytes_count", evidence)
        self.assertIn("response_text_marker_ORCH_PROVIDER_SMOKE_OK", evidence)
        self.assertIn("exit_code", evidence)
        self.assertIn("elapsed_time_if_present", evidence)
        self.assertIn("operator_captures_http_status_code", packet.response_acceptance_criteria)
        self.assertIn("response_text_includes_ORCH_PROVIDER_SMOKE_OK_or_bounded_equivalent", packet.response_acceptance_criteria)

    def test_non_proofs_cover_generation_generate_chat_route_and_production(self):
        packet = get_local_provider_generation_smoke_probe_packet()

        self.assertIn("packet_contract_is_not_generation", packet.non_proofs)
        self.assertIn("packet_contract_is_not_api_generate", packet.non_proofs)
        self.assertIn("packet_contract_is_not_api_chat", packet.non_proofs)
        self.assertIn("future_smoke_pass_would_not_prove_route_execution", packet.non_proofs)
        self.assertIn("future_smoke_pass_would_not_prove_semantic_correctness", packet.non_proofs)
        self.assertIn("future_smoke_pass_would_not_prove_vram_sufficiency_for_real_workloads", packet.non_proofs)
        self.assertIn("future_smoke_pass_would_not_prove_production_readiness", packet.non_proofs)

    def test_packet_serializes_for_reports_without_authority(self):
        packet_dict = provider_generation_smoke_probe_packet_to_dict(get_local_provider_generation_smoke_probe_packet())

        self.assertEqual(packet_dict["request_shape"]["model"], "qwen3.6:27b")
        self.assertFalse(packet_dict["generation_allowed_now"])
        self.assertFalse(packet_dict["provider_execution_allowed"])
        self.assertFalse(packet_dict["route_execution_allowed"])
        self.assertFalse(packet_dict["production_readiness"])

    def test_manual_review_report_renders_future_packet_without_execution(self):
        result = run_named_fixture_review("safe_direct_answer")
        packet = result.review_report_result.report.future_provider_generation_smoke_probe_packet

        self.assertIn("Future Provider Generation Smoke Probe Packet", result.review_text)
        self.assertIn("packet_contract_only=true", result.review_text)
        self.assertIn("generation_allowed_now=False", result.review_text)
        self.assertIn("coordinator_acceptance_required=True", result.review_text)
        self.assertEqual(packet["endpoint_path"], "/api/generate")
        self.assertFalse(packet["generation_allowed_now"])
        self.assertFalse(packet["provider_execution_allowed"])

    def test_touched_modules_do_not_import_runtime_provider_network_or_platform_surfaces(self):
        for module in (provider_generation_smoke_probe_packet, coordinator_review_report):
            source = inspect.getsource(module)
            for forbidden in FORBIDDEN_RUNTIME_IMPORTS:
                with self.subTest(module=module.__name__, forbidden=forbidden):
                    self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
