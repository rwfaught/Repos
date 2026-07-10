import json
import unittest

from orchestrator.local_model_reasoning_contract import (
    CONTRACT_VERSION,
    MIN_ACCEPTED_CONFIDENCE,
    build_local_model_interpretation_request,
    normalize_local_model_output,
    validate_local_model_raw_output,
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

    def test_strict_json_output_is_accepted_and_preserved(self):
        raw = json.dumps(valid_payload(self.request))

        result = validate_local_model_raw_output(self.request, raw)

        self.assertTrue(result.accepted)
        self.assertEqual(result.classification, "strict_json")
        self.assertEqual(result.raw_output, raw)
        self.assertEqual(result.candidate_json, raw)

    def test_empty_think_and_end_marker_are_allowed_wrappers(self):
        candidate = json.dumps(valid_payload(self.request))
        raw = f"<think></think>\n{candidate}\n[end of text]"

        result = validate_local_model_raw_output(self.request, raw)

        self.assertTrue(result.accepted)
        self.assertEqual(result.classification, "extracted_embedded_json")
        self.assertEqual(result.raw_output, raw)
        self.assertEqual(result.candidate_json, candidate)

    def test_known_good_qwen_smoke_shape_is_quarantined_before_contract_validation(self):
        candidate = (
            '{"interpretation_candidate":[{"status":"docs loaded","label":"ready"},'
            '{"status":"runtime identity unknown","label":"blocked"},'
            '{"status":"model output malformed","label":"needs_review"}]}'
        )
        raw = f"<think>\n\n</think>\n\n{candidate} [end of text]"

        normalization = normalize_local_model_output(raw)
        validation_result = validate_local_model_raw_output(self.request, raw)

        self.assertEqual(normalization.classification, "quarantined_ambiguous_output")
        self.assertEqual(normalization.raw_output, raw)
        self.assertEqual(normalization.candidate_json, candidate)
        self.assertEqual(
            normalization.parsed_candidate,
            {
                "interpretation_candidate": [
                    {"status": "docs loaded", "label": "ready"},
                    {"status": "runtime identity unknown", "label": "blocked"},
                    {"status": "model output malformed", "label": "needs_review"},
                ]
            },
        )
        self.assertIn("unclassified_prefix_artifact", normalization.reasons)
        self.assertEqual(validation_result.classification, "quarantined_ambiguous_output")
        self.assertIsNone(validation_result.validation)
        self.assertIn("unclassified_prefix_artifact", validation_result.reasons)

    def test_unclassified_prose_before_candidate_is_quarantined(self):
        raw = "Here is the interpretation:\n" + json.dumps(valid_payload(self.request))

        result = validate_local_model_raw_output(self.request, raw)

        self.assertFalse(result.accepted)
        self.assertEqual(result.classification, "quarantined_ambiguous_output")
        self.assertIn("unclassified_prefix_artifact", result.reasons)

    def test_multiple_json_objects_are_rejected(self):
        first = json.dumps(valid_payload(self.request))
        second = json.dumps(valid_payload(self.request))

        result = validate_local_model_raw_output(self.request, first + "\n" + second)

        self.assertFalse(result.accepted)
        self.assertEqual(result.classification, "rejected_multiple_json_candidates")

    def test_malformed_json_is_rejected(self):
        result = validate_local_model_raw_output(self.request, "{not valid json}")

        self.assertFalse(result.accepted)
        self.assertEqual(result.classification, "rejected_malformed_json")

    def test_authority_and_execution_claims_are_rejected_after_extraction(self):
        payload = valid_payload(self.request)
        payload["execution_authorized"] = False
        raw = "<think></think>" + json.dumps(payload) + "[end of text]"

        result = validate_local_model_raw_output(self.request, raw)

        self.assertFalse(result.accepted)
        self.assertEqual(result.classification, "rejected_authority_or_execution_claim")
        self.assertIn("authority_or_execution_fields:execution_authorized", result.reasons)

    def test_wrapper_looking_text_inside_json_string_is_not_stripped(self):
        payload = valid_payload(self.request)
        payload["assumptions"] = ["literal <think></think> [end of text] text"]
        raw = json.dumps(payload)

        result = validate_local_model_raw_output(self.request, raw)

        self.assertTrue(result.accepted)
        self.assertEqual(result.classification, "strict_json")
        self.assertEqual(result.raw_output, raw)

    def test_low_confidence_and_ambiguity_remain_quarantined_after_extraction(self):
        low_confidence = valid_payload(self.request)
        low_confidence["confidence"] = MIN_ACCEPTED_CONFIDENCE - 0.01
        ambiguous = valid_payload(self.request)
        ambiguous["clarification_needed"] = ["which input scope applies"]

        low_result = validate_local_model_raw_output(
            self.request,
            "<think></think>" + json.dumps(low_confidence) + "[end of text]",
        )
        ambiguous_result = validate_local_model_raw_output(
            self.request,
            "<think></think>" + json.dumps(ambiguous) + "[end of text]",
        )

        self.assertEqual(low_result.classification, "quarantined_ambiguous_output")
        self.assertEqual(ambiguous_result.classification, "quarantined_ambiguous_output")


if __name__ == "__main__":
    unittest.main()
