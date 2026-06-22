import inspect
import unittest

from orchestrator import coordinator_review_report, manual_review_runner
from orchestrator.manual_review_runner import run_named_fixture_review, run_structured_intake_review
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


def _authorized_probe_request(**overrides):
    values = {
        "requested_probe_kind": "read_only_future_probe_plan",
        "requested_surface": "provider_runtime_surface",
        "operator_authorized_probe_boundary": True,
        "allowed_probe_scope": ("read_only_probe_command_draft",),
        "expected_evidence": ("captured_future_probe_output",),
        "stop_conditions": ("unexpected_execution_request",),
        "caveats": ("phase_128_authorized_test_path",),
    }
    values.update(overrides)
    return values


def _intake(request_id: str, request_type: str, required_capabilities: tuple[str, ...], **overrides):
    values = {
        "request_id": request_id,
        "observed_request_summary": "Phase 128 provider probe packet status intake.",
        "request_type": request_type,
        "confidence": 0.9,
        "required_capabilities": required_capabilities,
        "missing_inputs": (),
        "risk_level": "low",
        "execution_policy": "phase_128_manual_review_only",
        "recommended_next_action": "review_provider_probe_packet_status",
        "requires_operator_confirmation": False,
        "requires_external_connector": False,
        "allowed_to_answer_directly": False,
        "allowed_to_mutate_files": False,
        "allowed_to_schedule": False,
        "allowed_to_use_local_documents": False,
        "allowed_to_use_web": False,
        "reasoning_summary_for_operator": "Probe packet status only; no execution.",
        "caveats": (),
        "intake_source": "phase_128_test_structured_intake",
    }
    values.update(overrides)
    return RequestIntakeRecord(**values)


class Phase128ProviderProbePacketManualReviewIntegrationContractTests(unittest.TestCase):
    def assert_no_forbidden_execution_claims(self, text: str):
        rendered = text.lower()
        for forbidden in FORBIDDEN_EXECUTION_CLAIMS:
            self.assertNotIn(forbidden, rendered)

    def assert_probe_flags_false(self, result):
        self.assertIsNotNone(result.provider_probe_packet_status)
        self.assertTrue(all(flag is False for flag in result.provider_probe_packet_status["activity_flags"].values()))
        self.assertTrue(all(flag is False for flag in result.no_activity_flags.values()))

    def test_safe_direct_answer_manual_review_renders_router_policy_and_probe_packet_status(self):
        result = run_named_fixture_review("safe_direct_answer")

        self.assertIn("Router Policy", result.review_text)
        self.assertIn("Provider Probe Packet", result.review_text)
        self.assertEqual(result.provider_probe_packet_status["accepted"], False)
        self.assertEqual(result.provider_probe_packet_status["provider_catalog_key"], "")
        self.assertIn("provider_catalog_key=local_model_candidate", result.review_text)
        self.assertIn("probe_packet_missing_required_authority_or_scope", result.provider_probe_packet_status["blocked_conditions"])
        for missing in ("operator_authorized_probe_boundary", "allowed_probe_scope", "expected_evidence"):
            self.assertIn(missing, result.provider_probe_packet_status["missing_requirements"])
        self.assertIn(
            "probe_packet_is_not_provider_execution",
            result.provider_probe_packet_status["non_proofs"],
        )
        self.assertIn("probe_packet_is_not_model_availability_proof", result.non_proofs)
        self.assert_probe_flags_false(result)
        self.assert_no_forbidden_execution_claims(result.review_text)

    def test_authorized_deterministic_path_drafts_probe_packet_without_execution(self):
        result = run_named_fixture_review(
            "safe_direct_answer",
            provider_probe_packet_request=_authorized_probe_request(),
        )

        self.assertEqual(result.provider_probe_packet_status["accepted"], True)
        self.assertEqual(result.provider_probe_packet_status["provider_catalog_key"], "local_model_candidate")
        self.assertEqual(
            result.provider_probe_packet_status["provider_allowed_boundary"],
            "future_local_provider_model_probe_boundary",
        )
        self.assertEqual(result.provider_probe_packet_status["coordinator_acceptance_required"], True)
        self.assertIn("provider_allowed_boundary=future_local_provider_model_probe_boundary", result.review_text)
        self.assert_probe_flags_false(result)
        self.assert_no_forbidden_execution_claims(result.review_text)

    def test_coding_worker_route_does_not_dispatch_worker_or_codex(self):
        result = run_named_fixture_review(
            "safe_coding_source_test_mutation",
            provider_probe_packet_request=_authorized_probe_request(),
        )

        self.assertEqual(result.router_policy_recommendation["recommended_route"], "worker_codex_boundary")
        self.assertEqual(result.provider_probe_packet_status["accepted"], True)
        self.assertEqual(result.provider_probe_packet_status["provider_catalog_key"], "worker_codex_boundary")
        self.assertFalse(result.no_activity_flags["worker_dispatched"])
        self.assertFalse(result.no_activity_flags["codex_dispatched"])
        self.assert_probe_flags_false(result)

    def test_rag_web_and_scheduler_routes_do_not_execute_lookup_web_or_scheduler(self):
        cases = (
            (
                _intake(
                    "phase128_rag",
                    "local_document_lookup",
                    ("local_document_lookup",),
                    allowed_to_use_local_documents=True,
                ),
                "rag_lookup_performed",
                "rag_local_document_boundary",
            ),
            (
                _intake(
                    "phase128_web",
                    "research_request",
                    ("web_research",),
                    allowed_to_use_web=True,
                ),
                "web_lookup_performed",
                "web_research_boundary",
            ),
            (
                _intake(
                    "phase128_scheduler",
                    "reminder_request",
                    ("scheduling_contract",),
                    allowed_to_schedule=True,
                    requires_operator_confirmation=True,
                ),
                "scheduler_executed",
                "scheduler_reminder_boundary",
            ),
        )

        for intake, false_flag, provider_key in cases:
            with self.subTest(provider_key=provider_key):
                result = run_structured_intake_review(
                    intake,
                    provider_probe_packet_request=_authorized_probe_request(),
                )
                self.assertEqual(result.provider_probe_packet_status["accepted"], True)
                self.assertEqual(result.provider_probe_packet_status["provider_catalog_key"], provider_key)
                self.assertFalse(result.no_activity_flags[false_flag])
                self.assertFalse(result.provider_probe_packet_status["activity_flags"][false_flag])
                self.assert_no_forbidden_execution_claims(result.review_text)

    def test_block_and_clarification_routes_do_not_draft_provider_probe_packets(self):
        for fixture_id in ("production_execution_blocked", "ambiguous_needs_clarification"):
            with self.subTest(fixture_id=fixture_id):
                result = run_named_fixture_review(
                    fixture_id,
                    provider_probe_packet_request=_authorized_probe_request(),
                )
                self.assertFalse(result.provider_probe_packet_status["accepted"])
                self.assertIn(
                    "router_recommendation_not_probe_eligible",
                    result.provider_probe_packet_status["blocked_conditions"],
                )
                self.assert_probe_flags_false(result)

    def test_no_forbidden_runtime_imports_were_introduced(self):
        for module in (coordinator_review_report, manual_review_runner):
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
                "from orchestrator.platform",
                "from orchestrator.scheduler",
                "from orchestrator.connector",
                "from orchestrator.openclaw",
                "from orchestrator.hermes",
            ):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
