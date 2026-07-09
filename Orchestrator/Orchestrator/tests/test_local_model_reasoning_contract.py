import unittest

from orchestrator.local_model_reasoning_contract import (
    CONTRACT_VERSION,
    MIN_ACCEPTED_CONFIDENCE,
    build_local_model_interpretation_request,
    validate_local_model_interpretation,
)


def valid_payload(request):
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request.request_id,
        "objective": request.objective,
        "normalized_objective": request.objective.lower(),
        "capability_task": {
            "task_id": "task-001",
            "title": "Classify supplied labels",
            "objective": request.objective,
            "complexity": "simple",
            "code_generation_required": False,
            "long_context_required": False,
            "safety_risk": "low",
            "privacy_sensitivity": "internal",
            "external_tool_or_api_need": False,
            "live_runtime_execution_need": False,
            "tolerance_for_mistakes": "medium",
            "deterministic_validation_available": True,
            "local_model_output_reviewable": True,
        },
        "matched_signals": {"deterministic": ["fixed labels"]},
        "confidence": 0.91,
        "clarification_needed": [],
        "risk_flags": [],
        "assumptions": ["inputs are supplied by the operator"],
    }


class LocalModelReasoningContractTests(unittest.TestCase):
    def setUp(self):
        self.request = build_local_model_interpretation_request(
            "prompt-001", "Classify this fixed status list into three labels"
        )

    def test_valid_structured_interpretation_is_accepted(self):
        result = validate_local_model_interpretation(self.request, valid_payload(self.request))

        self.assertTrue(result.accepted)
        self.assertEqual(result.status, "accepted")
        self.assertEqual(result.interpretation.confidence, 0.91)
        self.assertEqual(result.interpretation.capability_task["complexity"], "simple")

    def test_extra_authority_fields_are_rejected(self):
        payload = valid_payload(self.request)
        payload["execution_authorized"] = True

        result = validate_local_model_interpretation(self.request, payload)

        self.assertFalse(result.accepted)
        self.assertEqual(result.status, "rejected")
        self.assertIn("unsupported_response_fields:execution_authorized", result.reasons)

    def test_low_confidence_is_quarantined(self):
        payload = valid_payload(self.request)
        payload["confidence"] = MIN_ACCEPTED_CONFIDENCE - 0.01

        result = validate_local_model_interpretation(self.request, payload)

        self.assertFalse(result.accepted)
        self.assertEqual(result.status, "quarantined")
        self.assertIn("model_confidence_below_acceptance_threshold", result.reasons)

    def test_ambiguous_output_is_quarantined(self):
        payload = valid_payload(self.request)
        payload["clarification_needed"] = ["which label vocabulary should apply"]

        result = validate_local_model_interpretation(self.request, payload)

        self.assertFalse(result.accepted)
        self.assertEqual(result.status, "quarantined")
        self.assertIn("model_interpretation_is_ambiguous", result.reasons)

    def test_high_risk_output_is_quarantined(self):
        payload = valid_payload(self.request)
        payload["capability_task"]["safety_risk"] = "high"

        result = validate_local_model_interpretation(self.request, payload)

        self.assertFalse(result.accepted)
        self.assertEqual(result.status, "quarantined")
        self.assertIn("high_risk_interpretation_requires_owner_review", result.reasons)

    def test_request_and_response_identity_must_match(self):
        payload = valid_payload(self.request)
        payload["request_id"] = "different-request"

        result = validate_local_model_interpretation(self.request, payload)

        self.assertFalse(result.accepted)
        self.assertIn("request_id_mismatch", result.reasons)
        self.assertIn("not local model execution", result.non_proofs)


if __name__ == "__main__":
    unittest.main()
