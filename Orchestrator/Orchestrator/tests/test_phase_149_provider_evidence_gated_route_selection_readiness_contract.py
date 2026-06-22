import inspect
import unittest

from orchestrator import coordinator_review_report, route_selection_readiness
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


def _local_first_request():
    return {
        "request_id": "phase149-local-first",
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


class Phase149ProviderEvidenceGatedRouteSelectionReadinessContractTests(unittest.TestCase):
    def test_local_model_candidate_recommendation_produces_readiness_result(self):
        recommendation = recommend_model_route(_local_first_request())
        readiness = evaluate_route_selection_readiness(recommendation)

        self.assertEqual(readiness.request_id, "phase149-local-first")
        self.assertEqual(readiness.provider_catalog_key, "local_model_candidate")
        self.assertEqual(readiness.recommended_route, "local_first_answer")
        self.assertEqual(readiness.provider_evidence_status, recommendation.provider_evidence_status)

    def test_readiness_carries_phase_131_and_phase_133_evidence(self):
        readiness = evaluate_route_selection_readiness(_local_first_request())

        self.assertIn("phase_131_local_ollama_tags_model_list_visibility", readiness.provider_evidence_keys)
        self.assertIn("phase_133_qwen3_30b_24k_show_metadata_visibility", readiness.provider_evidence_keys)
        self.assertIn("phase_159_retry1_qwen36_27b_generate_marker_smoke", readiness.provider_evidence_keys)
        self.assertIn("PHASE_131", readiness.provider_evidence_source_phases)
        self.assertIn("PHASE_133", readiness.provider_evidence_source_phases)
        self.assertIn("PHASE_159_RETRY_1_OPERATOR_PROOF", readiness.provider_evidence_source_phases)

    def test_readiness_blocks_pending_27b_metadata_proof_after_smoke_evidence(self):
        readiness = evaluate_route_selection_readiness(_local_first_request())

        self.assertEqual(readiness.provider_evidence_status, "read_only_metadata_visible")
        self.assertEqual(readiness.route_selection_readiness, "blocked_pending_qwen36_27b_metadata_proof")
        self.assertEqual(readiness.readiness_status, "not_ready_for_execution")
        self.assertIn("qwen36_27b_api_show_metadata_proof_missing", readiness.blocked_conditions)
        self.assertEqual(
            readiness.next_required_boundary,
            "future_qwen36_27b_api_show_metadata_proof_boundary",
        )
        self.assertEqual(readiness.next_required_proof, "bounded_qwen36_27b_api_show_metadata_operator_proof")

    def test_readiness_preserves_all_execution_permissions_false(self):
        readiness = evaluate_route_selection_readiness(_local_first_request())

        self.assertFalse(readiness.provider_selection_allowed)
        self.assertFalse(readiness.provider_execution_allowed)
        self.assertFalse(readiness.route_execution_allowed)
        self.assertFalse(readiness.generation_allowed)
        self.assertFalse(readiness.production_readiness)
        self.assertTrue(all(flag is False for flag in readiness.activity_flags.values()))

    def test_readiness_non_proofs_cover_generation_and_route_execution(self):
        readiness = evaluate_route_selection_readiness(_local_first_request())

        self.assertIn("readiness_contract_is_not_generation", readiness.non_proofs)
        self.assertIn("readiness_contract_is_not_api_generate", readiness.non_proofs)
        self.assertIn("readiness_contract_is_not_api_chat", readiness.non_proofs)
        self.assertIn("readiness_contract_is_not_route_execution", readiness.non_proofs)
        self.assertIn("readiness_contract_is_not_production_readiness", readiness.non_proofs)

    def test_manual_review_report_renders_route_selection_readiness_without_execution(self):
        result = run_named_fixture_review("safe_direct_answer")
        report = result.review_report_result.report
        readiness = report.route_selection_readiness_summary

        self.assertIn("Route Selection Readiness", result.review_text)
        self.assertEqual(readiness["provider_evidence_status"], "read_only_metadata_visible")
        self.assertEqual(readiness["route_selection_readiness"], "blocked_pending_qwen36_27b_metadata_proof")
        self.assertEqual(readiness["next_required_boundary"], "future_qwen36_27b_api_show_metadata_proof_boundary")
        self.assertFalse(readiness["provider_selection_allowed"])
        self.assertFalse(readiness["provider_execution_allowed"])
        self.assertFalse(readiness["route_execution_allowed"])
        self.assertFalse(readiness["generation_allowed"])
        self.assertFalse(readiness["production_readiness"])
        self.assertIn("generation_allowed=False", result.review_text)
        self.assertIn("production_readiness=False", result.review_text)

    def test_touched_modules_do_not_import_runtime_provider_network_or_platform_surfaces(self):
        for module in (route_selection_readiness, coordinator_review_report):
            source = inspect.getsource(module)
            for forbidden in FORBIDDEN_RUNTIME_IMPORTS:
                with self.subTest(module=module.__name__, forbidden=forbidden):
                    self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
