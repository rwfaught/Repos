import inspect
import unittest

from orchestrator import coordinator_review_report, model_router_policy, route_selection_readiness
from orchestrator.manual_review_runner import run_named_fixture_review
from orchestrator.model_router_policy import recommend_model_route
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

FORBIDDEN_EXECUTION_CLAIMS = (
    "provider_selected=True",
    "provider_executed=True",
    "model_selected=True",
    "model_executed=True",
    "generation_allowed=True",
    "generation_performed=True",
    "api_generate_called=True",
    "api_chat_called=True",
    "route_executed=True",
    "route_execution_allowed=True",
    "worker_dispatched=True",
    "production_readiness=True",
    "production_executed=True",
)


def _local_first_request():
    return {
        "request_id": "phase165-local-first",
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
    }


class Phase165RouteSelectionReadinessRecommendationEnvelopeReviewContractTests(unittest.TestCase):
    def test_recommendation_envelope_carries_registered_qwen36_27b_evidence(self):
        recommendation = recommend_model_route(_local_first_request())

        self.assertEqual(recommendation.provider_catalog_key, "local_model_candidate")
        self.assertEqual(recommendation.provider_evidence_status, "read_only_metadata_visible")
        self.assertIn("phase_131_local_ollama_tags_model_list_visibility", recommendation.provider_evidence_keys)
        self.assertIn("phase_159_retry1_qwen36_27b_generate_marker_smoke", recommendation.provider_evidence_keys)
        self.assertIn("phase_162_qwen36_27b_show_metadata_visibility", recommendation.provider_evidence_keys)
        self.assertIn("PHASE_131", recommendation.provider_evidence_source_phases)
        self.assertIn("PHASE_159_RETRY_1_OPERATOR_PROOF", recommendation.provider_evidence_source_phases)
        self.assertIn("PHASE_162_OPERATOR_PROOF", recommendation.provider_evidence_source_phases)
        self.assertEqual(recommendation.model_metadata_evidence_name, "qwen3.6:27b")
        self.assertEqual(recommendation.model_metadata_format, "unknown_not_recorded")
        self.assertFalse(recommendation.provider_selection_allowed)
        self.assertFalse(recommendation.provider_execution_allowed)

    def test_readiness_no_longer_blocks_on_generation_or_metadata_evidence(self):
        readiness = evaluate_route_selection_readiness(_local_first_request())

        self.assertEqual(
            readiness.route_selection_readiness,
            "future_probe_ready_qwen36_27b_evidence_registered",
        )
        self.assertEqual(readiness.readiness_status, "not_ready_for_execution")
        self.assertNotIn("generation_smoke_probe_boundary_not_authorized", readiness.blocked_conditions)
        self.assertNotIn("qwen36_27b_api_show_metadata_proof_missing", readiness.blocked_conditions)
        self.assertEqual(
            readiness.next_required_boundary,
            "future_bounded_route_selection_readiness_recommendation_envelope_review",
        )
        self.assertEqual(
            readiness.next_required_proof,
            "bounded_route_selection_readiness_recommendation_envelope_review",
        )

    def test_readiness_review_preserves_all_execution_authority_false(self):
        readiness = evaluate_route_selection_readiness(_local_first_request())

        self.assertFalse(readiness.provider_selection_allowed)
        self.assertFalse(readiness.provider_execution_allowed)
        self.assertFalse(readiness.route_execution_allowed)
        self.assertFalse(readiness.generation_allowed)
        self.assertFalse(readiness.production_readiness)
        self.assertTrue(all(flag is False for flag in readiness.activity_flags.values()))
        self.assertIn("readiness_contract_is_not_route_execution", readiness.non_proofs)
        self.assertIn("readiness_contract_is_not_production_readiness", readiness.non_proofs)

    def test_manual_review_report_renders_recommendation_and_readiness_without_execution(self):
        result = run_named_fixture_review("safe_direct_answer")
        report = result.review_report_result.report
        readiness = report.route_selection_readiness_summary
        text = result.review_text

        self.assertIn("phase_159_retry1_qwen36_27b_generate_marker_smoke", text)
        self.assertIn("phase_162_qwen36_27b_show_metadata_visibility", text)
        self.assertIn("route_selection_readiness=future_probe_ready_qwen36_27b_evidence_registered", text)
        self.assertEqual(
            readiness["next_required_boundary"],
            "future_bounded_route_selection_readiness_recommendation_envelope_review",
        )
        self.assertFalse(readiness["provider_selection_allowed"])
        self.assertFalse(readiness["provider_execution_allowed"])
        self.assertFalse(readiness["route_execution_allowed"])
        self.assertFalse(readiness["generation_allowed"])
        self.assertFalse(readiness["production_readiness"])

        for forbidden in FORBIDDEN_EXECUTION_CLAIMS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)

    def test_review_modules_do_not_import_runtime_provider_network_or_platform_surfaces(self):
        for module in (model_router_policy, route_selection_readiness, coordinator_review_report):
            source = inspect.getsource(module)
            for forbidden in FORBIDDEN_RUNTIME_IMPORTS:
                with self.subTest(module=module.__name__, forbidden=forbidden):
                    self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
