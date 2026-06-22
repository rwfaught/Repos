import inspect
import unittest

from orchestrator import provider_evidence_registry, route_selection_readiness
from orchestrator.model_router_policy import recommend_model_route
from orchestrator.provider_evidence_registry import (
    get_model_metadata_evidence,
    get_provider_evidence_registry,
    summarize_provider_evidence_for_catalog_key,
)
from orchestrator.route_selection_readiness import evaluate_route_selection_readiness


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
        "request_id": "phase163-local-first",
        "request_type": "general_answer",
        "confidence": 0.9,
        "required_capabilities": ["direct_answer"],
        "missing_inputs": [],
        "risk_level": "low",
        "allowed_to_answer_directly": True,
    }


class Phase163Qwen36ApiShowMetadataEvidenceContractTests(unittest.TestCase):
    def test_phase_162_qwen36_27b_show_metadata_evidence_is_registered(self):
        evidence = get_provider_evidence_registry()["phase_162_qwen36_27b_show_metadata_visibility"]

        self.assertEqual(evidence.source_phase, "PHASE_162_OPERATOR_PROOF")
        self.assertEqual(evidence.provider_catalog_key, "local_model_candidate")
        self.assertEqual(evidence.evidence_kind, "model_metadata_visibility")
        self.assertEqual(evidence.evidence_status, "read_only_metadata_visible")
        self.assertEqual(evidence.endpoint_shape, "http://127.0.0.1:11434/api/show")
        self.assertEqual(evidence.method, "POST")
        self.assertEqual(evidence.status_code, 200)
        self.assertEqual(evidence.content_type, "application/json; charset=utf-8")
        self.assertEqual(evidence.model_name, "qwen3.6:27b")
        self.assertTrue(evidence.metadata["metadata_details_visible"])
        self.assertTrue(evidence.metadata["license_present"])
        self.assertTrue(evidence.metadata["tensor_metadata_present"])
        self.assertTrue(evidence.metadata["model_metadata_present"])
        self.assertEqual(evidence.metadata["capabilities"], ("completion", "vision", "tools", "thinking"))
        self.assertTrue(evidence.metadata["modified_at_present"])
        self.assertTrue(evidence.metadata["raw_body_not_copied"])
        self.assertEqual(evidence.metadata["final_git_status"], "## main...origin/main")

    def test_unknown_metadata_fields_are_not_fabricated(self):
        evidence = get_model_metadata_evidence("qwen3.6:27b")

        self.assertIsNotNone(evidence)
        self.assertEqual(evidence.metadata["format"], "unknown_not_recorded")
        self.assertEqual(evidence.metadata["family"], "unknown_not_recorded")
        self.assertEqual(evidence.metadata["families"], "unknown_not_recorded")
        self.assertEqual(evidence.metadata["parameter_size"], "unknown_not_recorded")
        self.assertEqual(evidence.metadata["quantization_level"], "unknown_not_recorded")

    def test_generation_smoke_evidence_is_preserved_with_metadata_evidence(self):
        summary = summarize_provider_evidence_for_catalog_key("local_model_candidate")

        self.assertIn("phase_159_retry1_qwen36_27b_generate_marker_smoke", summary["evidence_keys"])
        self.assertIn("phase_162_qwen36_27b_show_metadata_visibility", summary["evidence_keys"])
        self.assertEqual(summary["model_name"], "qwen3.6:27b")
        self.assertEqual(summary["metadata_format"], "unknown_not_recorded")

    def test_readiness_clears_metadata_blocker_without_execution_authority(self):
        readiness = evaluate_route_selection_readiness(_local_first_request())

        self.assertEqual(
            readiness.route_selection_readiness,
            "future_probe_ready_qwen36_27b_evidence_registered",
        )
        self.assertEqual(readiness.readiness_status, "not_ready_for_execution")
        self.assertNotIn("qwen36_27b_api_show_metadata_proof_missing", readiness.blocked_conditions)
        self.assertEqual(
            readiness.next_required_boundary,
            "future_bounded_route_selection_readiness_recommendation_envelope_review",
        )
        self.assertFalse(readiness.provider_selection_allowed)
        self.assertFalse(readiness.provider_execution_allowed)
        self.assertFalse(readiness.route_execution_allowed)
        self.assertFalse(readiness.generation_allowed)
        self.assertFalse(readiness.production_readiness)
        self.assertTrue(all(flag is False for flag in readiness.activity_flags.values()))

    def test_recommendation_envelope_carries_phase_162_evidence(self):
        recommendation = recommend_model_route(_local_first_request())

        self.assertIn("phase_162_qwen36_27b_show_metadata_visibility", recommendation.provider_evidence_keys)
        self.assertIn("PHASE_162_OPERATOR_PROOF", recommendation.provider_evidence_source_phases)
        self.assertEqual(recommendation.model_metadata_evidence_name, "qwen3.6:27b")
        self.assertEqual(recommendation.model_metadata_format, "unknown_not_recorded")
        self.assertFalse(recommendation.provider_selection_allowed)
        self.assertFalse(recommendation.provider_execution_allowed)

    def test_touched_modules_do_not_import_runtime_provider_network_or_platform_surfaces(self):
        for module in (provider_evidence_registry, route_selection_readiness):
            source = inspect.getsource(module)
            for forbidden in FORBIDDEN_RUNTIME_IMPORTS:
                with self.subTest(module=module.__name__, forbidden=forbidden):
                    self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
