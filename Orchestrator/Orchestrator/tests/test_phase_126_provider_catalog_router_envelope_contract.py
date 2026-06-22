import inspect
import unittest

from orchestrator import model_provider_catalog, model_router_policy
from orchestrator.manual_review_runner import run_named_fixture_review, run_structured_intake_review
from orchestrator.model_router_policy import recommend_model_route
from orchestrator.route_proposal import RequestIntakeRecord


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
    "production_readiness=true",
)


def _request(**overrides):
    values = {
        "request_id": "req-126",
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


def _intake(request_id: str, request_type: str, required_capabilities: tuple[str, ...], **overrides):
    values = {
        "request_id": request_id,
        "observed_request_summary": "Phase 126 provider catalog envelope intake.",
        "request_type": request_type,
        "confidence": 0.9,
        "required_capabilities": required_capabilities,
        "missing_inputs": (),
        "risk_level": "low",
        "execution_policy": "phase_126_manual_review_only",
        "recommended_next_action": "review_provider_catalog_envelope",
        "requires_operator_confirmation": False,
        "requires_external_connector": False,
        "allowed_to_answer_directly": False,
        "allowed_to_mutate_files": False,
        "allowed_to_schedule": False,
        "allowed_to_use_local_documents": False,
        "allowed_to_use_web": False,
        "reasoning_summary_for_operator": "Provider catalog envelope only; no execution.",
        "caveats": (),
        "intake_source": "phase_126_test_structured_intake",
    }
    values.update(overrides)
    return RequestIntakeRecord(**values)


class Phase126ProviderCatalogRouterEnvelopeContractTests(unittest.TestCase):
    def assert_catalog_envelope(self, recommendation, provider_key: str, boundary: str):
        self.assertEqual(recommendation.provider_catalog_key, provider_key)
        self.assertEqual(recommendation.provider_allowed_boundary, boundary)
        self.assertFalse(recommendation.provider_execution_allowed)
        self.assertFalse(recommendation.provider_selection_allowed)
        self.assertTrue(all(flag is False for flag in recommendation.provider_catalog_activity_flags.values()))
        self.assertIn("provider_catalog_is_not_provider_execution", recommendation.provider_catalog_non_proofs)
        self.assertIn("provider_catalog_is_not_model_execution", recommendation.provider_catalog_non_proofs)
        self.assertIn("provider_catalog_is_not_runtime_execution", recommendation.provider_catalog_non_proofs)
        self.assertIn("provider_catalog_is_not_platform_execution", recommendation.provider_catalog_non_proofs)
        self.assertIn("provider_catalog_is_not_worker_dispatch", recommendation.provider_catalog_non_proofs)
        self.assertIn("provider_catalog_is_not_route_execution", recommendation.provider_catalog_non_proofs)
        self.assertIn("provider_catalog_is_not_production_readiness", recommendation.provider_catalog_non_proofs)

    def test_local_first_direct_answer_includes_provider_catalog_envelope(self):
        recommendation = recommend_model_route(_request())

        self.assertEqual(recommendation.recommended_route, "local_first_answer")
        self.assertEqual(recommendation.provider_posture, "local_first_when_authorized_no_provider_executed")
        self.assertEqual(recommendation.provider_tier, "local_first_candidate")
        self.assertEqual(recommendation.provider_maturity_status, "policy_candidate_only")
        self.assert_catalog_envelope(
            recommendation,
            "local_model_candidate",
            "direct_answer_or_report_only_boundary",
        )
        self.assertIn("local_first_preference_is_not_local_model_execution", recommendation.provider_catalog_non_proofs)

    def test_frontier_provider_platform_route_uses_frontier_catalog_entry_without_execution(self):
        recommendation = recommend_model_route(
            _request(
                request_type="unsupported_or_requires_connector",
                required_capabilities=["provider_model", "platform_runtime"],
                allowed_to_answer_directly=False,
                requires_external_connector=True,
            )
        )

        self.assertEqual(recommendation.recommended_route, "separate_provider_or_platform_boundary_required")
        self.assert_catalog_envelope(
            recommendation,
            "frontier_provider_candidate",
            "frontier_provider_escalation_boundary",
        )
        self.assertFalse(recommendation.provider_catalog_activity_flags["provider_executed"])
        self.assertFalse(recommendation.provider_catalog_activity_flags["model_executed"])
        self.assertFalse(recommendation.provider_catalog_activity_flags["runtime_executed"])
        self.assertFalse(recommendation.provider_catalog_activity_flags["platform_executed"])

    def test_worker_codex_route_uses_worker_boundary_entry_without_dispatch(self):
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
        self.assert_catalog_envelope(recommendation, "worker_codex_boundary", "bounded_worker_codex_boundary")
        self.assertFalse(recommendation.provider_catalog_activity_flags["worker_dispatched"])
        self.assertFalse(recommendation.provider_catalog_activity_flags["codex_dispatched"])

    def test_rag_scheduler_and_web_routes_use_matching_catalog_entries_without_execution(self):
        cases = (
            (
                _request(
                    request_type="local_document_lookup",
                    required_capabilities=["local_document_lookup"],
                    allowed_to_answer_directly=False,
                    allowed_to_use_local_documents=True,
                ),
                "rag_local_document_boundary",
                "rag_local_document_lookup_boundary",
                "rag_lookup_performed",
            ),
            (
                _request(
                    request_type="reminder_request",
                    required_capabilities=["scheduling_contract"],
                    allowed_to_answer_directly=False,
                    allowed_to_schedule=True,
                ),
                "scheduler_reminder_boundary",
                "scheduler_reminder_boundary",
                "scheduler_executed",
            ),
            (
                _request(
                    request_type="research_request",
                    required_capabilities=["web_research"],
                    allowed_to_answer_directly=False,
                    allowed_to_use_web=True,
                ),
                "web_research_boundary",
                "web_research_boundary",
                "web_lookup_performed",
            ),
        )

        for request, provider_key, boundary, activity_flag in cases:
            with self.subTest(provider_key=provider_key):
                recommendation = recommend_model_route(request)
                self.assert_catalog_envelope(recommendation, provider_key, boundary)
                self.assertFalse(recommendation.provider_catalog_activity_flags[activity_flag])

    def test_block_and_clarification_routes_fall_back_to_blocked_catalog_entry(self):
        block = recommend_model_route(
            _request(
                request_type="unsupported_or_requires_connector",
                required_capabilities=["production_execution"],
                allowed_to_answer_directly=False,
            )
        )
        clarification = recommend_model_route(
            {
                "request_id": "missing-fields",
                "request_type": "",
                "required_capabilities": [],
                "confidence": "unknown",
            }
        )

        for recommendation in (block, clarification):
            with self.subTest(route=recommendation.recommended_route):
                self.assert_catalog_envelope(
                    recommendation,
                    "provider_blocked_or_unavailable",
                    "operator_clarification_or_explicit_future_boundary",
                )

    def test_manual_review_text_renders_provider_catalog_fields_without_execution_claims(self):
        result = run_named_fixture_review("safe_direct_answer")

        self.assertEqual(result.router_policy_recommendation["provider_catalog_key"], "local_model_candidate")
        self.assertIn("provider_catalog_key=local_model_candidate", result.review_text)
        self.assertIn("provider_tier=local_first_candidate", result.review_text)
        self.assertIn("provider_maturity_status=policy_candidate_only", result.review_text)
        self.assertIn("provider_allowed_boundary=direct_answer_or_report_only_boundary", result.review_text)
        self.assertIn(
            "provider_required_authority=explicit_future_provider_model_boundary_before_execution",
            result.review_text,
        )
        self.assertIn("provider_execution_allowed=False", result.review_text)
        self.assertIn("provider_selection_allowed=False", result.review_text)

        rendered = result.review_text.lower()
        for forbidden in FORBIDDEN_EXECUTION_CLAIMS:
            self.assertNotIn(forbidden, rendered)

    def test_manual_review_artifacts_preserve_catalog_flags_and_non_proofs(self):
        result = run_structured_intake_review(
            _intake(
                "phase126_web",
                "research_request",
                ("web_research",),
                allowed_to_use_web=True,
            )
        )

        recommendation = result.router_policy_recommendation
        self.assertEqual(recommendation["provider_catalog_key"], "web_research_boundary")
        self.assertEqual(recommendation["provider_allowed_boundary"], "web_research_boundary")
        self.assertFalse(recommendation["provider_catalog_activity_flags"]["web_lookup_performed"])
        self.assertFalse(result.no_activity_flags["web_lookup_performed"])
        self.assertFalse(result.no_activity_flags["route_executed"])
        self.assertIn("provider_catalog_is_not_web_lookup", result.non_proofs)
        self.assertIn("provider_catalog_is_not_route_execution", result.non_proofs)

    def test_policy_modules_still_avoid_provider_runtime_and_execution_imports(self):
        for module in (model_router_policy, model_provider_catalog):
            source = inspect.getsource(module)
            for forbidden in (
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
