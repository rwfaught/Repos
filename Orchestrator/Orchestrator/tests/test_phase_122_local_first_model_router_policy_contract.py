import inspect
import unittest

from orchestrator import model_router_policy
from orchestrator.model_router_policy import (
    NO_ACTIVITY_FLAGS,
    ROUTER_POLICY_NON_PROOFS,
    ModelRouterPolicyRecommendation,
    recommend_model_route,
)


def _request(**overrides):
    values = {
        "request_id": "req-122",
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
    values.update(overrides)
    return values


class Phase122LocalFirstModelRouterPolicyContractTests(unittest.TestCase):
    def assert_no_activity(self, recommendation: ModelRouterPolicyRecommendation):
        self.assertEqual(recommendation.activity_flags, NO_ACTIVITY_FLAGS)
        self.assertTrue(all(flag is False for flag in recommendation.activity_flags.values()))

    def assert_conservative_non_proofs(self, recommendation: ModelRouterPolicyRecommendation):
        for non_proof in ROUTER_POLICY_NON_PROOFS:
            self.assertIn(non_proof, recommendation.non_proofs)

    def test_local_first_direct_answer_recommendation(self):
        recommendation = recommend_model_route(_request())

        self.assertEqual(recommendation.recommended_route, "local_first_answer")
        self.assertEqual(recommendation.provider_posture, "local_first_when_authorized_no_provider_executed")
        self.assertEqual(recommendation.confidence, 0.9)
        self.assertEqual(recommendation.required_boundary, "direct_answer_or_report_only_boundary")
        self.assertEqual(recommendation.blocked_conditions, ())
        self.assertIn("Low-risk answer route", recommendation.reason)
        self.assert_no_activity(recommendation)
        self.assert_conservative_non_proofs(recommendation)

    def test_coding_task_routes_to_worker_boundary_without_provider_execution(self):
        recommendation = recommend_model_route(
            _request(
                request_type="coding_task",
                required_capabilities=["source_inspection", "patch_proposal", "filesystem_mutation_authority"],
                allowed_to_answer_directly=False,
                allowed_to_mutate_files=True,
                requires_operator_confirmation=True,
            )
        )

        self.assertEqual(recommendation.recommended_route, "worker_codex_boundary")
        self.assertEqual(recommendation.required_boundary, "bounded_worker_codex_boundary")
        self.assertEqual(recommendation.provider_posture, "provider_model_not_selected_for_direct_execution")
        self.assertIn("worker_dispatch_not_executed", recommendation.blocked_conditions)
        self.assert_no_activity(recommendation)
        self.assert_conservative_non_proofs(recommendation)

    def test_local_document_lookup_routes_to_rag_boundary_without_lookup(self):
        recommendation = recommend_model_route(
            _request(
                request_type="local_document_lookup",
                required_capabilities=["local_document_lookup"],
                allowed_to_answer_directly=False,
                allowed_to_use_local_documents=True,
            )
        )

        self.assertEqual(recommendation.recommended_route, "rag_local_document_boundary")
        self.assertEqual(recommendation.required_boundary, "rag_local_document_lookup_boundary")
        self.assertIn("rag_lookup_not_executed", recommendation.blocked_conditions)
        self.assert_no_activity(recommendation)

    def test_reminder_request_routes_to_scheduler_boundary_without_scheduling(self):
        recommendation = recommend_model_route(
            _request(
                request_type="reminder_request",
                required_capabilities=["scheduling_contract"],
                allowed_to_answer_directly=False,
                allowed_to_schedule=True,
                requires_operator_confirmation=True,
            )
        )

        self.assertEqual(recommendation.recommended_route, "scheduler_reminder_boundary")
        self.assertEqual(recommendation.required_boundary, "scheduler_reminder_boundary")
        self.assertIn("scheduler_not_executed", recommendation.blocked_conditions)
        self.assert_no_activity(recommendation)

    def test_research_request_routes_to_web_boundary_without_web_lookup(self):
        recommendation = recommend_model_route(
            _request(
                request_type="research_request",
                required_capabilities=["web_research"],
                allowed_to_answer_directly=False,
                allowed_to_use_web=True,
            )
        )

        self.assertEqual(recommendation.recommended_route, "web_research_boundary")
        self.assertEqual(recommendation.required_boundary, "web_research_boundary")
        self.assertIn("web_lookup_not_executed", recommendation.blocked_conditions)
        self.assert_no_activity(recommendation)

    def test_provider_model_and_platform_runtime_require_separate_boundary(self):
        for capability in ("provider_model", "platform_runtime"):
            with self.subTest(capability=capability):
                recommendation = recommend_model_route(
                    _request(
                        request_type="unsupported_or_requires_connector",
                        required_capabilities=[capability],
                        allowed_to_answer_directly=False,
                        requires_external_connector=True,
                    )
                )

                self.assertEqual(
                    recommendation.recommended_route,
                    "separate_provider_or_platform_boundary_required",
                )
                self.assertEqual(recommendation.required_boundary, "provider_model_or_platform_runtime_boundary")
                self.assertIn("provider_model_or_platform_runtime_boundary_required", recommendation.blocked_conditions)
                self.assert_no_activity(recommendation)

    def test_production_execution_blocks(self):
        recommendation = recommend_model_route(
            _request(
                request_type="unsupported_or_requires_connector",
                required_capabilities=["production_execution"],
                allowed_to_answer_directly=False,
                requires_external_connector=True,
            )
        )

        self.assertEqual(recommendation.recommended_route, "block")
        self.assertEqual(recommendation.required_boundary, "explicit_production_execution_boundary")
        self.assertIn("production_execution_blocked", recommendation.blocked_conditions)
        self.assert_no_activity(recommendation)

    def test_missing_confidence_request_type_or_capability_authority_clarifies(self):
        recommendation = recommend_model_route(
            {
                "request_id": "missing-fields",
                "request_type": "",
                "required_capabilities": [],
                "confidence": "unknown",
            }
        )

        self.assertEqual(recommendation.recommended_route, "ask_clarification")
        self.assertIn("request_type", recommendation.missing_requirements)
        self.assertIn("confidence", recommendation.missing_requirements)
        self.assertIn("required_capabilities", recommendation.missing_requirements)
        self.assertEqual(recommendation.required_boundary, "operator_clarification_boundary")
        self.assert_no_activity(recommendation)

    def test_unknown_capability_authority_clarifies_or_blocks(self):
        recommendation = recommend_model_route(_request(required_capabilities=["future_unknown_capability"]))

        self.assertEqual(recommendation.recommended_route, "ask_clarification")
        self.assertIn("unknown_capability_authority", recommendation.blocked_conditions)
        self.assert_no_activity(recommendation)

    def test_module_uses_no_execution_or_provider_imports(self):
        source = inspect.getsource(model_router_policy)

        for forbidden in (
            "import subprocess",
            "import requests",
            "import socket",
            "import urllib",
            "import openai",
            "import ollama",
            "import discord",
            "from orchestrator.provider",
            "from orchestrator.platform",
            "from orchestrator.scheduler",
            "from orchestrator.connector",
            "from orchestrator.openclaw",
            "from orchestrator.hermes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
