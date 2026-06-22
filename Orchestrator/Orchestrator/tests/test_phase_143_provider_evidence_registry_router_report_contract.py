import inspect
import unittest

from orchestrator import coordinator_review_report, provider_evidence_registry
from orchestrator.manual_review_runner import run_named_fixture_review
from orchestrator.provider_evidence_registry import (
    get_model_metadata_evidence,
    get_provider_evidence_for_catalog_key,
    get_provider_evidence_registry,
    summarize_provider_evidence_for_catalog_key,
)


FORBIDDEN_EXECUTION_CLAIMS = (
    "provider_executed=true",
    "model_executed=true",
    "runtime_executed=true",
    "platform_executed=true",
    "worker_dispatched=true",
    "codex_dispatched=true",
    "rag_lookup_performed=true",
    "web_lookup_performed=true",
    "scheduler_executed=true",
    "connector_executed=true",
    "route_executed=true",
    "route_execution=true",
    "production_readiness=true",
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


class Phase143ProviderEvidenceRegistryRouterReportContractTests(unittest.TestCase):
    def test_registry_exposes_phase_131_provider_surface_evidence(self):
        registry = get_provider_evidence_registry()
        evidence = registry["phase_131_local_ollama_tags_model_list_visibility"]

        self.assertEqual(evidence.source_phase, "PHASE_131")
        self.assertEqual(evidence.provider_catalog_key, "local_model_candidate")
        self.assertEqual(evidence.evidence_status, "read_only_provider_surface_visible")
        self.assertEqual(evidence.endpoint_shape, "http://127.0.0.1:11434/api/tags")
        self.assertEqual(evidence.method, "GET")
        self.assertEqual(evidence.status_code, 200)
        self.assertEqual(evidence.metadata["model_count"], 9)
        self.assertIn("qwen3-30b-24k:latest", evidence.model_names)

    def test_registry_exposes_phase_133_model_metadata_evidence(self):
        evidence = get_model_metadata_evidence("qwen3-30b-24k:latest")

        self.assertIsNotNone(evidence)
        self.assertEqual(evidence.source_phase, "PHASE_133")
        self.assertEqual(evidence.evidence_status, "read_only_metadata_visible")
        self.assertEqual(evidence.endpoint_shape, "http://127.0.0.1:11434/api/show")
        self.assertEqual(evidence.method, "POST")
        self.assertEqual(evidence.status_code, 200)
        self.assertEqual(evidence.metadata["format"], "gguf")
        self.assertEqual(evidence.metadata["family"], "qwen3moe")
        self.assertEqual(evidence.metadata["parameter_size"], "30.5B")
        self.assertEqual(evidence.metadata["quantization_level"], "Q4_K_M")
        self.assertTrue(evidence.metadata["template_present"])
        self.assertTrue(evidence.metadata["parameters_present"])
        self.assertTrue(evidence.metadata["license_present"])

    def test_registry_exposes_phase_159_retry1_27b_generation_smoke_evidence(self):
        registry = get_provider_evidence_registry()
        evidence = registry["phase_159_retry1_qwen36_27b_generate_marker_smoke"]

        self.assertEqual(evidence.source_phase, "PHASE_159_RETRY_1_OPERATOR_PROOF")
        self.assertEqual(evidence.provider_catalog_key, "local_model_candidate")
        self.assertEqual(evidence.evidence_kind, "model_generation_smoke_marker")
        self.assertEqual(evidence.evidence_status, "accepted_generation_smoke_marker_visible")
        self.assertEqual(evidence.endpoint_shape, "http://127.0.0.1:11434/api/generate")
        self.assertEqual(evidence.method, "POST")
        self.assertEqual(evidence.status_code, 200)
        self.assertEqual(evidence.model_name, "qwen3.6:27b")
        self.assertEqual(evidence.metadata["num_predict"], 96)
        self.assertEqual(evidence.metadata["response_field"], "ORCH_PROVIDER_SMOKE_OK")
        self.assertTrue(evidence.metadata["marker_present_in_response_field"])
        self.assertEqual(
            evidence.metadata["prior_phase_159_initial_failure"],
            "FAIL_HTTP_200_LOCAL_PROVIDER_GENERATED_THINKING_ONLY_LENGTH_NO_MARKER",
        )
        self.assertEqual(
            evidence.metadata["prior_phase_155_retry3_30b_failure"],
            "FAIL_HTTP_500_PROVIDER_MODEL_LOAD_CUDA_OOM_RAW_BODY_CAPTURED_NO_GENERATION_PROOF",
        )

    def test_all_provider_evidence_activity_flags_are_false(self):
        for evidence in get_provider_evidence_registry().values():
            with self.subTest(evidence_key=evidence.evidence_key):
                self.assertTrue(all(flag is False for flag in evidence.activity_flags.values()))

    def test_registry_non_proofs_preserve_execution_blocks(self):
        for evidence in get_provider_evidence_for_catalog_key("local_model_candidate"):
            with self.subTest(evidence_key=evidence.evidence_key):
                for non_proof in (
                    "provider_evidence_is_not_api_generate",
                    "provider_evidence_is_not_api_chat",
                    "provider_evidence_is_not_route_execution",
                    "provider_evidence_is_not_production_readiness",
                ):
                    self.assertIn(non_proof, evidence.non_proofs)

    def test_manual_review_report_renders_provider_evidence_for_safe_direct_answer(self):
        result = run_named_fixture_review("safe_direct_answer")
        text = result.review_text

        self.assertIn("Provider Evidence", text)
        self.assertIn("provider_evidence_status=read_only_metadata_visible", text)
        self.assertIn("provider_catalog_key=local_model_candidate", text)
        self.assertIn("model_name=qwen3-30b-24k:latest", text)
        self.assertIn("metadata_format=gguf", text)
        self.assertIn("metadata_family=qwen3moe", text)
        self.assertIn("metadata_parameter_size=30.5B", text)
        self.assertIn("metadata_quantization_level=Q4_K_M", text)
        self.assertIn("evidence_visibility_is_not_provider_model_execution", text)

    def test_manual_review_report_remains_non_executing(self):
        result = run_named_fixture_review("safe_direct_answer")

        self.assertTrue(all(flag is False for flag in result.no_activity_flags.values()))
        rendered = result.review_text.lower()
        for forbidden in FORBIDDEN_EXECUTION_CLAIMS:
            self.assertNotIn(forbidden, rendered)

    def test_provider_catalog_selection_remains_conservative(self):
        result = run_named_fixture_review("safe_direct_answer")
        recommendation = result.router_policy_recommendation
        summary = summarize_provider_evidence_for_catalog_key(recommendation["provider_catalog_key"])

        self.assertEqual(summary["provider_evidence_status"], "read_only_metadata_visible")
        self.assertEqual(recommendation["provider_catalog_key"], "local_model_candidate")
        self.assertFalse(recommendation["provider_execution_allowed"])
        self.assertFalse(recommendation["provider_selection_allowed"])

    def test_new_and_touched_modules_avoid_forbidden_runtime_imports(self):
        for module in (provider_evidence_registry, coordinator_review_report):
            source = inspect.getsource(module)
            for forbidden in FORBIDDEN_RUNTIME_IMPORTS:
                with self.subTest(module=module.__name__, forbidden=forbidden):
                    self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
