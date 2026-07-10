import json
import unittest

from orchestrator.local_model_provider_adapter import InjectedLocalModelProvider
from orchestrator.local_model_reasoning_contract import build_local_model_interpretation_request


def valid_payload(request):
    return {
        "contract_version": "local_model_reasoning_v1", "request_id": request.request_id,
        "objective": request.objective, "normalized_objective": request.objective.lower(),
        "capability_task": {
            "task_id": "task-001", "title": "Classify labels", "objective": request.objective,
            "complexity": "simple", "code_generation_required": False, "long_context_required": False,
            "safety_risk": "low", "privacy_sensitivity": "internal", "external_tool_or_api_need": False,
            "live_runtime_execution_need": False, "tolerance_for_mistakes": "medium",
            "deterministic_validation_available": True, "local_model_output_reviewable": True,
        },
        "matched_signals": {"deterministic": ["fixed labels"]}, "confidence": 0.91,
        "clarification_needed": [], "risk_flags": [], "assumptions": [],
    }


class LocalModelProviderAdapterTests(unittest.TestCase):
    def setUp(self):
        self.request = build_local_model_interpretation_request("prompt-001", "Classify labels")

    def test_valid_qwen_wrapper_is_admitted_and_preserved(self):
        raw = "<think>\n\n</think>\n" + json.dumps(valid_payload(self.request)) + " [end of text]"
        result = InjectedLocalModelProvider(lambda request: raw).interpret(self.request)
        self.assertEqual(result.status, "candidate_admitted")
        self.assertEqual(result.normalization_classification, "extracted_embedded_json")
        self.assertEqual(result.validation_classification, "extracted_embedded_json")
        self.assertTrue(result.candidate_admitted)
        self.assertEqual(result.raw_output, raw)
        self.assertTrue(result.raw_output_reference.startswith("sha256:"))
        self.assertFalse(result.execution_performed)

    def test_malformed_and_authority_shaped_output_are_quarantined(self):
        malformed = InjectedLocalModelProvider(lambda request: "{not-json").interpret(self.request)
        self.assertEqual(malformed.validation_classification, "rejected_malformed_json")
        self.assertEqual(malformed.fallback_status, "deterministic_fallback")
        payload = valid_payload(self.request)
        payload["dispatch"] = False
        authority = InjectedLocalModelProvider(lambda request: json.dumps(payload)).interpret(self.request)
        self.assertEqual(authority.validation_classification, "rejected_authority_or_execution_claim")
        self.assertTrue(authority.authority_quarantined)
        self.assertFalse(authority.candidate_admitted)

    def test_transport_exception_is_deterministic_fallback(self):
        def failing(request):
            raise RuntimeError("transport unavailable")
        result = InjectedLocalModelProvider(failing).interpret(self.request)
        self.assertEqual(result.status, "transport_exception")
        self.assertEqual(result.fallback_status, "deterministic_fallback")
        self.assertIsNone(result.raw_output)
        self.assertFalse(result.execution_performed)


if __name__ == "__main__":
    unittest.main()
