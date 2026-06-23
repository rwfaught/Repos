import inspect
import unittest

from orchestrator import supervised_provider_call_tracer
from orchestrator.supervised_provider_call_tracer import (
    SUPERVISED_PROVIDER_CALL_TRACER_NON_PROOFS,
    SupervisedProviderCallTracerPacket,
    SupervisedProviderCallTracerReview,
    build_supervised_provider_call_tracer_packet,
    classify_supervised_provider_call_tracer_result,
    render_supervised_provider_call_tracer_packet_text,
    supervised_provider_call_tracer_packet_to_dict,
)


FORBIDDEN_SOURCE_SNIPPETS = (
    "import requests",
    "urllib.request",
    "http.client",
    "import subprocess",
    "import socket",
    "import openai",
    "import ollama",
    "import discord",
    "import click",
    "import typer",
    "orchestrator.provider",
    "orchestrator.platform",
    "orchestrator.connector",
    "orchestrator.scheduler",
    "orchestrator.service",
    "orchestrator.api",
    "orchestrator.ui",
    "orchestrator.openclaw",
    "orchestrator.hermes",
    "orchestrator.wsl",
)

FALSE_AUTHORITY_FIELDS = (
    "provider_selection_allowed",
    "provider_execution_allowed",
    "route_execution_allowed",
    "generation_allowed",
    "production_readiness",
)

FALSE_ACTIVITY_FLAGS = (
    "provider_selected",
    "provider_executed",
    "model_selected",
    "model_executed",
    "runtime_executed",
    "platform_executed",
    "route_executed",
    "generation_performed",
    "api_generate_called",
    "api_chat_called",
    "api_show_called",
    "api_tags_called",
    "worker_dispatched",
    "codex_dispatched",
    "ollama_executed",
    "wsl_executed",
    "openclaw_executed",
    "hermes_executed",
    "discord_executed",
    "rag_lookup_performed",
    "web_lookup_performed",
    "scheduler_executed",
    "connector_executed",
    "service_executed",
    "api_endpoint_executed",
    "ui_executed",
    "product_executed",
    "cleanup_performed",
    "deletion_performed",
    "archive_performed",
    "production_executed",
)


class Phase183SupervisedProviderCallTracerPacketContractTests(unittest.TestCase):
    def test_module_exposes_required_names(self):
        self.assertIs(
            supervised_provider_call_tracer.SupervisedProviderCallTracerPacket,
            SupervisedProviderCallTracerPacket,
        )
        self.assertIs(
            supervised_provider_call_tracer.SupervisedProviderCallTracerReview,
            SupervisedProviderCallTracerReview,
        )
        self.assertIs(
            supervised_provider_call_tracer.SUPERVISED_PROVIDER_CALL_TRACER_NON_PROOFS,
            SUPERVISED_PROVIDER_CALL_TRACER_NON_PROOFS,
        )
        self.assertIs(
            supervised_provider_call_tracer.build_supervised_provider_call_tracer_packet,
            build_supervised_provider_call_tracer_packet,
        )
        self.assertIs(
            supervised_provider_call_tracer.supervised_provider_call_tracer_packet_to_dict,
            supervised_provider_call_tracer_packet_to_dict,
        )
        self.assertIs(
            supervised_provider_call_tracer.render_supervised_provider_call_tracer_packet_text,
            render_supervised_provider_call_tracer_packet_text,
        )
        self.assertIs(
            supervised_provider_call_tracer.classify_supervised_provider_call_tracer_result,
            classify_supervised_provider_call_tracer_result,
        )

    def test_packet_builder_returns_exact_expected_fields(self):
        packet = build_supervised_provider_call_tracer_packet()
        payload = supervised_provider_call_tracer_packet_to_dict(packet)

        expected = {
            "phase": "PHASE_187",
            "artifact_kind": "supervised_provider_call_tracer_packet_contract",
            "fixture_id": "safe_direct_answer",
            "original_packet_phase": "PHASE_183",
            "target_reconciliation_phase": "PHASE_187",
            "inventory_evidence_phase": "PHASE_186_RETRY4",
            "source_tracer_phase": "PHASE_169",
            "adapter_phase": "PHASE_176",
            "operator_smoke_phase": "PHASE_179",
            "provider_catalog_key": "local_model_candidate",
            "model_name": "qwen3.6:35b-a3b",
            "endpoint_shape": "POST local_ollama_http/api/generate",
            "endpoint_url": "http://127.0.0.1:11434/api/generate",
            "prompt_contract": "Return exactly: ORCH_PROVIDER_SMOKE_OK",
            "expected_marker": "ORCH_PROVIDER_SMOKE_OK",
            "required_future_boundary": "future_supervised_provider_call_tracer_operator_proof",
            "required_future_proof": "captured_http_status_json_response_marker_and_no_route_execution",
            "current_readiness": "target_reconciliation_complete_future_marker_smoke_required",
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(payload[key], value)
        self.assertEqual(payload["request_parameters"]["stream"], False)
        self.assertEqual(payload["request_parameters"]["num_predict"], 96)

    def test_packet_carries_phase_186_retry4_inventory_visibility_only(self):
        packet = build_supervised_provider_call_tracer_packet()

        self.assertEqual(
            packet.provider_evidence_keys,
            ("phase_186_retry4_qwen36_35b_a3b_inventory_visibility_only",),
        )
        self.assertIn(
            "phase_186_retry4_qwen36_35b_a3b_present_in_inventory",
            packet.accepted_facts,
        )
        self.assertIn(
            "phase_186_retry4_qwen36_27b_absent_from_inventory",
            packet.accepted_facts,
        )

    def test_packet_does_not_transfer_qwen36_27b_marker_smoke_evidence_to_35b(self):
        packet = build_supervised_provider_call_tracer_packet()
        payload_text = repr(supervised_provider_call_tracer_packet_to_dict(packet))

        self.assertNotIn("phase_159_retry1_qwen36_27b_generate_marker_smoke", packet.provider_evidence_keys)
        self.assertNotIn("phase_162_qwen36_27b_show_metadata_visibility", packet.provider_evidence_keys)
        self.assertIn("qwen36_27b_marker_smoke_evidence_not_transferred_to_qwen36_35b_a3b", packet.caveats)
        self.assertIn("qwen36_35b_a3b_requires_future_supervised_marker_smoke_proof", packet.caveats)
        self.assertIn("qwen36_35b_a3b_supervised_marker_smoke_proof_missing_until_future_boundary", packet.missing_requirements)
        self.assertIn("qwen3.6:35b-a3b", payload_text)

    def test_packet_preserves_all_execution_authority_false(self):
        payload = supervised_provider_call_tracer_packet_to_dict(build_supervised_provider_call_tracer_packet())

        for field in FALSE_AUTHORITY_FIELDS:
            with self.subTest(field=field):
                self.assertFalse(payload[field])

    def test_packet_activity_flags_are_false_for_execution_surfaces(self):
        packet = build_supervised_provider_call_tracer_packet()

        for flag in FALSE_ACTIVITY_FLAGS:
            with self.subTest(flag=flag):
                self.assertIn(flag, packet.activity_flags)
                self.assertFalse(packet.activity_flags[flag])

    def test_rendering_text_includes_required_review_sections(self):
        rendered = render_supervised_provider_call_tracer_packet_text(
            build_supervised_provider_call_tracer_packet()
        )

        for expected in (
            "Assessment",
            "Accepted Facts",
            "Decision",
            "NBM",
            "Deliverable/Command",
            "RESPONSE_METADATA",
        ):
            self.assertIn(expected, rendered)
        self.assertIn("future_supervised_provider_call_tracer_operator_proof", rendered)

    def test_source_does_not_import_or_call_forbidden_execution_surfaces(self):
        source = inspect.getsource(supervised_provider_call_tracer)

        for forbidden in FORBIDDEN_SOURCE_SNIPPETS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_classifier_returns_pass_for_synthetic_future_35b_marker_smoke_shape(self):
        review = classify_supervised_provider_call_tracer_result(
            {
                "http_status": 200,
                "json_parse_success": True,
                "returned_model": "qwen3.6:35b-a3b",
                "response_text": "ORCH_PROVIDER_SMOKE_OK",
                "done": True,
                "done_reason": "stop",
            }
        )

        self.assertEqual(review.status, "PASS")
        self.assertEqual(review.classification, "captured_marker_smoke_pass_not_route_execution")
        self.assertTrue(review.accepted)
        self.assertIn("http_status=200", review.accepted_facts)
        self.assertIn("returned_model=qwen3.6:35b-a3b", review.accepted_facts)
        self.assertIn("response_text_contains=ORCH_PROVIDER_SMOKE_OK", review.accepted_facts)

    def test_classifier_returns_conservative_failure_classifications(self):
        cases = (
            (
                {"http_status": 500, "json_parse_success": True, "returned_model": "qwen3.6:35b-a3b", "response_text": "ORCH_PROVIDER_SMOKE_OK", "done": True},
                "non_200_http_status",
            ),
            (
                {"http_status": 200, "json_parse_success": False, "returned_model": "qwen3.6:35b-a3b", "response_text": "ORCH_PROVIDER_SMOKE_OK", "done": True},
                "json_parse_failure",
            ),
            (
                {"http_status": 200, "json_parse_success": True, "returned_model": "other", "response_text": "ORCH_PROVIDER_SMOKE_OK", "done": True},
                "wrong_model",
            ),
            (
                {"http_status": 200, "json_parse_success": True, "returned_model": "qwen3.6:35b-a3b", "response_text": "no marker", "done": True},
                "missing_marker",
            ),
            (
                {"http_status": 200, "json_parse_success": True, "returned_model": "qwen3.6:35b-a3b", "response_text": "ORCH_PROVIDER_SMOKE_OK", "done": False},
                "incomplete_done_false",
            ),
            (
                {"http_status": 200, "json_parse_success": True},
                "missing_required_fields",
            ),
        )

        for captured, expected in cases:
            with self.subTest(expected=expected):
                review = classify_supervised_provider_call_tracer_result(captured)
                self.assertEqual(review.status, "FAIL")
                self.assertEqual(review.classification, expected)
                self.assertFalse(review.accepted)
                self.assertTrue(review.blocked_conditions or review.missing_requirements)

    def test_classifier_rejects_retired_qwen36_27b_returned_model(self):
        review = classify_supervised_provider_call_tracer_result(
            {
                "http_status": 200,
                "json_parse_success": True,
                "returned_model": "qwen3.6:27b",
                "response_text": "ORCH_PROVIDER_SMOKE_OK",
                "done": True,
            }
        )

        self.assertEqual(review.status, "FAIL")
        self.assertEqual(review.classification, "wrong_model")
        self.assertFalse(review.accepted)
        self.assertIn("returned_model=qwen3.6:27b", review.accepted_facts)

    def test_even_pass_classifier_output_preserves_non_execution_non_proofs(self):
        review = classify_supervised_provider_call_tracer_result(
            {
                "http_status": 200,
                "json_parse_success": True,
                "returned_model": "qwen3.6:35b-a3b",
                "response_text": "prefix ORCH_PROVIDER_SMOKE_OK suffix",
                "done": True,
                "done_reason": "stop",
            }
        )

        self.assertFalse(review.route_execution_allowed)
        self.assertFalse(review.production_readiness)
        self.assertIn("future_smoke_pass_would_not_prove_semantic_correctness", review.non_proofs)
        self.assertIn("future_smoke_pass_would_not_prove_real_workload_loadability", review.non_proofs)
        self.assertIn("future_smoke_pass_would_not_prove_production_readiness", review.non_proofs)


if __name__ == "__main__":
    unittest.main()
