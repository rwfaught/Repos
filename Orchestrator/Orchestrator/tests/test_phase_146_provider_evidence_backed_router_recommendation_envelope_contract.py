import inspect
import unittest

from orchestrator import coordinator_review_report, model_router_policy, provider_evidence_registry
from orchestrator.manual_review_runner import run_named_fixture_review
from orchestrator.model_router_policy import recommend_model_route


FORBIDDEN_EXECUTION_CLAIMS = (
    "provider_executed=true",
    "model_executed=true",
    "runtime_executed=true",
    "platform_executed=true",
    "worker_dispatched=true",
    "codex_dispatched=true",
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


def _local_first_request():
    return {
        "request_id": "phase146-local-first",
        "request_type": "general_answer",
        "confidence": 0.9,
        "required_capabilities": ["direct_answer"],
        "missing_inputs": [],
        "risk_level": "low",
        "allowed_to_answer_directly": True,
        "allowed_to_mutate_files": False,
        "allowed_to_schedule": False,
        "allowed_to_use_local_documents": False,
        "allowed_to_use_web": False,
        "requires_operator_confirmation": False,
        "requires_external_connector": False,
    }


class Phase146ProviderEvidenceBackedRouterRecommendationEnvelopeContractTests(unittest.TestCase):
    def test_local_model_candidate_recommendation_includes_provider_evidence_fields(self):
        recommendation = recommend_model_route(_local_first_request())

        self.assertEqual(recommendation.provider_catalog_key, "local_model_candidate")
        self.assertEqual(recommendation.provider_evidence_status, "read_only_metadata_visible")
        self.assertTrue(recommendation.provider_evidence_keys)
        self.assertTrue(recommendation.provider_evidence_source_phases)
        self.assertEqual(
            recommendation.provider_evidence_summary,
            "Read-only model metadata visibility existed for qwen3-30b-24k:latest at that moment.",
        )

    def test_recommendation_includes_phase_131_and_phase_133_evidence_posture(self):
        recommendation = recommend_model_route(_local_first_request())

        self.assertIn("phase_131_local_ollama_tags_model_list_visibility", recommendation.provider_evidence_keys)
        self.assertIn("phase_133_qwen3_30b_24k_show_metadata_visibility", recommendation.provider_evidence_keys)
        self.assertIn("PHASE_131", recommendation.provider_evidence_source_phases)
        self.assertIn("PHASE_133", recommendation.provider_evidence_source_phases)

    def test_recommendation_exposes_qwen3_metadata_evidence_fields(self):
        recommendation = recommend_model_route(_local_first_request())

        self.assertEqual(recommendation.model_metadata_evidence_name, "qwen3-30b-24k:latest")
        self.assertEqual(recommendation.model_metadata_format, "gguf")
        self.assertEqual(recommendation.model_metadata_family, "qwen3moe")
        self.assertEqual(recommendation.model_metadata_parameter_size, "30.5B")
        self.assertEqual(recommendation.model_metadata_quantization_level, "Q4_K_M")

    def test_evidence_visibility_does_not_flip_execution_or_selection_authority(self):
        recommendation = recommend_model_route(_local_first_request())

        self.assertFalse(recommendation.provider_execution_allowed)
        self.assertFalse(recommendation.provider_selection_allowed)
        self.assertTrue(all(flag is False for flag in recommendation.provider_evidence_activity_flags.values()))
        self.assertIn("provider_evidence_is_not_model_generation", recommendation.provider_evidence_non_proofs)
        self.assertIn("provider_evidence_is_not_route_execution", recommendation.provider_evidence_non_proofs)
        self.assertIn("provider_evidence_is_not_production_readiness", recommendation.provider_evidence_non_proofs)

    def test_manual_review_rendering_includes_envelope_evidence_without_execution_claims(self):
        result = run_named_fixture_review("safe_direct_answer")
        text = result.review_text

        self.assertIn("Router Policy", text)
        self.assertIn("provider_evidence_status=read_only_metadata_visible", text)
        self.assertIn("phase_131_local_ollama_tags_model_list_visibility", text)
        self.assertIn("phase_133_qwen3_30b_24k_show_metadata_visibility", text)
        self.assertIn("model_metadata_evidence_name=qwen3-30b-24k:latest", text)
        self.assertIn("model_metadata_format=gguf", text)
        self.assertIn("model_metadata_family=qwen3moe", text)
        self.assertIn("model_metadata_parameter_size=30.5B", text)
        self.assertIn("model_metadata_quantization_level=Q4_K_M", text)
        self.assertIn("evidence_visibility_is_not_provider_model_execution", text)

        rendered = text.lower()
        for forbidden in FORBIDDEN_EXECUTION_CLAIMS:
            self.assertNotIn(forbidden, rendered)

    def test_manual_review_recommendation_dictionary_preserves_conservative_authority(self):
        result = run_named_fixture_review("safe_direct_answer")
        recommendation = result.router_policy_recommendation

        self.assertEqual(recommendation["provider_evidence_status"], "read_only_metadata_visible")
        self.assertEqual(recommendation["model_metadata_format"], "gguf")
        self.assertFalse(recommendation["provider_execution_allowed"])
        self.assertFalse(recommendation["provider_selection_allowed"])
        self.assertTrue(all(flag is False for flag in recommendation["provider_evidence_activity_flags"].values()))

    def test_touched_modules_do_not_import_runtime_or_provider_surfaces(self):
        for module in (model_router_policy, provider_evidence_registry, coordinator_review_report):
            source = inspect.getsource(module)
            for forbidden in FORBIDDEN_RUNTIME_IMPORTS:
                with self.subTest(module=module.__name__, forbidden=forbidden):
                    self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
