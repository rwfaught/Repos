import inspect
import unittest

from orchestrator import provider_probe_boundary_packet
from orchestrator.model_router_policy import recommend_model_route
from orchestrator.provider_probe_boundary_packet import (
    PROBE_PACKET_NON_PROOFS,
    ProviderProbeBoundaryPacketRequest,
    build_provider_probe_boundary_packet,
    render_provider_probe_boundary_packet_text,
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
    "production_readiness=true",
)


def _router_request(**overrides):
    values = {
        "request_id": "req-127",
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


def _probe_request(recommendation, **overrides):
    values = {
        "request_id": "probe-127",
        "source_router_recommendation": recommendation,
        "requested_probe_kind": "read_only_future_probe_plan",
        "requested_surface": "provider_runtime_surface",
        "operator_authorized_probe_boundary": True,
        "allowed_probe_scope": ("read_only_probe_command_draft",),
        "expected_evidence": ("captured_future_probe_output",),
        "stop_conditions": ("unexpected_execution_request",),
        "caveats": ("phase_127_test_packet",),
    }
    values.update(overrides)
    return ProviderProbeBoundaryPacketRequest(**values)


class Phase127ProviderProbeBoundaryPacketContractTests(unittest.TestCase):
    def assert_packet_no_activity(self, result):
        self.assertTrue(result.accepted)
        self.assertIsNotNone(result.packet_draft)
        self.assertTrue(all(flag is False for flag in result.activity_flags.values()))
        self.assertTrue(all(flag is False for flag in result.packet_draft.activity_flags.values()))
        self.assertTrue(result.packet_draft.coordinator_acceptance_required)
        for non_proof in PROBE_PACKET_NON_PROOFS:
            self.assertIn(non_proof, result.non_proofs)

    def test_local_first_recommendation_drafts_future_local_provider_probe_packet(self):
        recommendation = recommend_model_route(_router_request())
        result = build_provider_probe_boundary_packet(_probe_request(recommendation))

        self.assert_packet_no_activity(result)
        packet = result.packet_draft
        self.assertEqual(packet.provider_catalog_key, "local_model_candidate")
        self.assertEqual(packet.provider_tier, "local_first_candidate")
        self.assertEqual(packet.provider_allowed_boundary, "future_local_provider_model_probe_boundary")
        self.assertIn("probe_packet_is_not_provider_execution", packet.non_proofs)
        self.assertIn("probe_packet_is_not_model_execution", packet.non_proofs)
        self.assertIn("probe_packet_is_not_provider_availability_proof", packet.non_proofs)
        self.assertIn("probe_packet_is_not_model_availability_proof", packet.non_proofs)

    def test_frontier_provider_recommendation_requires_explicit_boundary_authorization(self):
        recommendation = recommend_model_route(
            _router_request(
                request_type="unsupported_or_requires_connector",
                required_capabilities=["provider_model", "platform_runtime"],
                allowed_to_answer_directly=False,
                requires_external_connector=True,
            )
        )
        result = build_provider_probe_boundary_packet(_probe_request(recommendation))

        self.assert_packet_no_activity(result)
        self.assertEqual(result.packet_draft.provider_catalog_key, "frontier_provider_candidate")
        self.assertEqual(
            result.packet_draft.provider_allowed_boundary,
            "future_frontier_provider_escalation_probe_boundary",
        )

    def test_worker_rag_scheduler_and_web_entries_draft_only_future_boundary_packets(self):
        cases = (
            (
                _router_request(
                    request_type="coding_task",
                    required_capabilities=["source_inspection", "patch_proposal", "filesystem_mutation_authority"],
                    allowed_to_answer_directly=False,
                    allowed_to_mutate_files=True,
                    requires_operator_confirmation=True,
                ),
                "worker_codex_boundary",
                "future_bounded_worker_codex_probe_boundary",
                ("worker_dispatched", "codex_dispatched"),
            ),
            (
                _router_request(
                    request_type="local_document_lookup",
                    required_capabilities=["local_document_lookup"],
                    allowed_to_answer_directly=False,
                    allowed_to_use_local_documents=True,
                ),
                "rag_local_document_boundary",
                "future_rag_local_document_probe_boundary",
                ("rag_lookup_performed",),
            ),
            (
                _router_request(
                    request_type="reminder_request",
                    required_capabilities=["scheduling_contract"],
                    allowed_to_answer_directly=False,
                    allowed_to_schedule=True,
                ),
                "scheduler_reminder_boundary",
                "future_scheduler_reminder_probe_boundary",
                ("scheduler_executed",),
            ),
            (
                _router_request(
                    request_type="research_request",
                    required_capabilities=["web_research"],
                    allowed_to_answer_directly=False,
                    allowed_to_use_web=True,
                ),
                "web_research_boundary",
                "future_web_research_probe_boundary",
                ("web_lookup_performed",),
            ),
        )

        for router_request, provider_key, boundary, false_flags in cases:
            with self.subTest(provider_key=provider_key):
                recommendation = recommend_model_route(router_request)
                result = build_provider_probe_boundary_packet(_probe_request(recommendation))
                self.assert_packet_no_activity(result)
                self.assertEqual(result.packet_draft.provider_catalog_key, provider_key)
                self.assertEqual(result.packet_draft.provider_allowed_boundary, boundary)
                for flag in false_flags:
                    self.assertFalse(result.packet_draft.activity_flags[flag])

    def test_block_and_clarification_recommendations_are_rejected(self):
        block = recommend_model_route(
            _router_request(
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
                result = build_provider_probe_boundary_packet(_probe_request(recommendation))
                self.assertFalse(result.accepted)
                self.assertIsNone(result.packet_draft)
                self.assertIn("router_recommendation_not_probe_eligible", result.blocked_conditions)
                self.assertTrue(all(flag is False for flag in result.activity_flags.values()))

    def test_missing_structured_router_recommendation_is_rejected(self):
        result = build_provider_probe_boundary_packet(_probe_request(None))

        self.assertFalse(result.accepted)
        self.assertIn("missing_structured_router_recommendation", result.blocked_conditions)
        self.assertIn("source_router_recommendation", result.missing_requirements)

    def test_missing_authorization_scope_or_expected_evidence_is_rejected(self):
        recommendation = recommend_model_route(_router_request())
        cases = (
            {"operator_authorized_probe_boundary": False},
            {"allowed_probe_scope": ()},
            {"expected_evidence": ()},
        )

        for overrides in cases:
            with self.subTest(overrides=overrides):
                result = build_provider_probe_boundary_packet(_probe_request(recommendation, **overrides))
                self.assertFalse(result.accepted)
                self.assertIn("probe_packet_missing_required_authority_or_scope", result.blocked_conditions)
                self.assertTrue(all(flag is False for flag in result.activity_flags.values()))

    def test_rendered_packet_text_includes_catalog_facts_and_exclusions_without_execution_claims(self):
        recommendation = recommend_model_route(_router_request())
        result = build_provider_probe_boundary_packet(_probe_request(recommendation))
        text = render_provider_probe_boundary_packet_text(result.packet_draft)

        self.assertIn("Provider Catalog Facts", text)
        self.assertIn("Explicit Exclusions", text)
        self.assertIn("provider_catalog_key=local_model_candidate", text)
        self.assertIn("provider_allowed_boundary=future_local_provider_model_probe_boundary", text)
        self.assertIn("No provider/model execution.", text)
        rendered = text.lower()
        for forbidden in FORBIDDEN_EXECUTION_CLAIMS:
            self.assertNotIn(forbidden, rendered)

    def test_module_uses_no_provider_runtime_or_execution_imports(self):
        source = inspect.getsource(provider_probe_boundary_packet)
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
            "filesystem",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
