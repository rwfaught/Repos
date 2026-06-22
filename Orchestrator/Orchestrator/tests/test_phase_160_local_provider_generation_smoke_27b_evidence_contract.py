import unittest

from orchestrator.provider_evidence_registry import (
    get_model_metadata_evidence,
    get_provider_evidence_registry,
    summarize_provider_evidence_for_catalog_key,
)
from orchestrator.route_selection_readiness import evaluate_route_selection_readiness


class Phase160LocalProviderGenerationSmoke27bEvidenceContractTests(unittest.TestCase):
    def test_phase_159_retry1_27b_generation_smoke_evidence_is_registered(self):
        evidence = get_provider_evidence_registry()["phase_159_retry1_qwen36_27b_generate_marker_smoke"]

        self.assertEqual(evidence.source_phase, "PHASE_159_RETRY_1_OPERATOR_PROOF")
        self.assertEqual(evidence.provider_catalog_key, "local_model_candidate")
        self.assertEqual(evidence.evidence_kind, "model_generation_smoke_marker")
        self.assertEqual(evidence.evidence_status, "accepted_generation_smoke_marker_visible")
        self.assertEqual(evidence.endpoint_shape, "http://127.0.0.1:11434/api/generate")
        self.assertEqual(evidence.method, "POST")
        self.assertEqual(evidence.status_code, 200)
        self.assertEqual(evidence.content_type, "application/json; charset=utf-8")
        self.assertEqual(evidence.model_name, "qwen3.6:27b")
        self.assertEqual(evidence.metadata["returned_model"], "qwen3.6:27b")
        self.assertEqual(evidence.metadata["response_field"], "ORCH_PROVIDER_SMOKE_OK")
        self.assertEqual(evidence.metadata["done_reason"], "stop")
        self.assertEqual(evidence.metadata["num_predict"], 96)
        self.assertIs(evidence.metadata["marker_present_in_response_field"], True)
        self.assertIs(evidence.metadata["marker_present_in_thinking_field"], True)
        self.assertIs(evidence.metadata["marker_present_in_raw_body"], True)

    def test_prior_failure_caveats_are_preserved_without_reclassifying_27b(self):
        evidence = get_provider_evidence_registry()["phase_159_retry1_qwen36_27b_generate_marker_smoke"]

        self.assertEqual(
            evidence.metadata["prior_phase_159_initial_failure"],
            "FAIL_HTTP_200_LOCAL_PROVIDER_GENERATED_THINKING_ONLY_LENGTH_NO_MARKER",
        )
        self.assertIn("num_predict=16 was too small", evidence.metadata["prior_phase_159_initial_failure_reason"])
        self.assertEqual(
            evidence.metadata["prior_phase_155_retry3_30b_failure"],
            "FAIL_HTTP_500_PROVIDER_MODEL_LOAD_CUDA_OOM_RAW_BODY_CAPTURED_NO_GENERATION_PROOF",
        )
        self.assertIn("not a qwen3.6:27b failure", evidence.metadata["prior_phase_155_retry3_30b_failure_reason"])

    def test_27b_metadata_proof_remains_missing(self):
        summary = summarize_provider_evidence_for_catalog_key("local_model_candidate")

        self.assertIn("phase_159_retry1_qwen36_27b_generate_marker_smoke", summary["evidence_keys"])
        self.assertIsNone(get_model_metadata_evidence("qwen3.6:27b"))

    def test_route_selection_readiness_moves_to_metadata_blocker_only(self):
        readiness = evaluate_route_selection_readiness(
            {
                "request_id": "phase160-local-first",
                "request_type": "general_answer",
                "confidence": 0.9,
                "required_capabilities": ["direct_answer"],
                "missing_inputs": [],
                "risk_level": "low",
                "allowed_to_answer_directly": True,
            }
        )

        self.assertIn("phase_159_retry1_qwen36_27b_generate_marker_smoke", readiness.provider_evidence_keys)
        self.assertEqual(readiness.route_selection_readiness, "blocked_pending_qwen36_27b_metadata_proof")
        self.assertIn("qwen36_27b_api_show_metadata_proof_missing", readiness.blocked_conditions)
        self.assertEqual(readiness.next_required_boundary, "future_qwen36_27b_api_show_metadata_proof_boundary")
        self.assertEqual(readiness.next_required_proof, "bounded_qwen36_27b_api_show_metadata_operator_proof")
        self.assertFalse(readiness.provider_selection_allowed)
        self.assertFalse(readiness.provider_execution_allowed)
        self.assertFalse(readiness.route_execution_allowed)
        self.assertFalse(readiness.generation_allowed)
        self.assertFalse(readiness.production_readiness)


if __name__ == "__main__":
    unittest.main()
