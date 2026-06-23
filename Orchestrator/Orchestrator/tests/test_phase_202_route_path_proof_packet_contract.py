import json
import unittest

from orchestrator.route_path_proof_packet import (
    build_route_path_proof_packet,
    review_route_path_proof_capture,
    route_path_proof_packet_to_dict,
)


class Phase202RoutePathProofPacketContractTests(unittest.TestCase):
    def test_packet_builds_deterministically_and_serializes_json_safe_shape(self):
        first = route_path_proof_packet_to_dict(build_route_path_proof_packet())
        second = route_path_proof_packet_to_dict(build_route_path_proof_packet())

        self.assertEqual(first, second)
        json.dumps(first, sort_keys=True)
        self.assertEqual(first["phase"], "PHASE_202")
        self.assertEqual(first["artifact_kind"], "route_path_proof_packet_contract")
        self.assertEqual(first["prior_direct_marker_proof_phase"], "PHASE_194")

    def test_packet_targets_30b_and_keeps_35b_disallowed_only(self):
        payload = route_path_proof_packet_to_dict(build_route_path_proof_packet())

        self.assertEqual(payload["route_proof_target_model"], "qwen3:30b-a3b-instruct-2507-q4_K_M")
        self.assertEqual(payload["disallowed_model"], "qwen3.6:35b-a3b")
        self.assertEqual(payload["fallback_candidate"], "qwen3.6:27b")
        self.assertNotEqual(payload["route_proof_target_model"], payload["disallowed_model"])
        self.assertTrue(any("qwen36_35b_a3b_disallowed" in caveat for caveat in payload["caveats"]))

    def test_future_route_marker_is_distinct_from_direct_provider_marker(self):
        packet = build_route_path_proof_packet()

        self.assertEqual(packet.prior_direct_marker, "ORCH_PROVIDER_SMOKE_OK")
        self.assertEqual(packet.future_route_marker, "ORCH_ROUTE_PROVIDER_SMOKE_OK")
        self.assertNotEqual(packet.future_route_marker, packet.prior_direct_marker)

    def test_execution_authority_flags_remain_false(self):
        payload = route_path_proof_packet_to_dict(build_route_path_proof_packet())

        self.assertFalse(payload["route_execution_allowed"])
        self.assertFalse(payload["provider_execution_allowed"])
        self.assertFalse(payload["generation_allowed"])
        self.assertFalse(payload["production_readiness"])
        for value in payload["activity_flags"].values():
            self.assertFalse(value)

    def test_required_future_proof_fields_are_route_mediated_not_direct_only(self):
        packet = build_route_path_proof_packet()

        self.assertIn("request_intake_harness_evidence", packet.required_future_proof_fields)
        self.assertIn("route_recommendation_readiness_evidence", packet.required_future_proof_fields)
        self.assertIn("explicit_route_execution_boundary_evidence", packet.required_future_proof_fields)
        self.assertIn("provider_call_through_route_path_evidence", packet.required_future_proof_fields)
        self.assertIn("persisted_artifact_path_evidence", packet.required_future_proof_fields)
        self.assertIn("displayed_reviewable_outcome_evidence", packet.required_future_proof_fields)
        self.assertNotIn("direct_provider_only_evidence", packet.required_future_proof_fields)

    def test_reviewer_rejects_overclaiming_route_execution_from_direct_provider_smoke(self):
        review = review_route_path_proof_capture(
            {
                "request_intake_harness_evidence": True,
                "route_recommendation_readiness_evidence": True,
                "explicit_route_execution_boundary_evidence": True,
                "provider_call_through_route_path_evidence": True,
                "captured_http_status_json_model_marker_evidence": True,
                "persisted_artifact_path_evidence": True,
                "displayed_reviewable_outcome_evidence": True,
                "marker": "ORCH_PROVIDER_SMOKE_OK",
                "returned_model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
            }
        )

        self.assertEqual(review.status, "FAIL")
        self.assertEqual(review.classification, "direct_provider_marker_not_route_mediated_proof")
        self.assertFalse(review.accepted)
        self.assertFalse(review.route_execution_allowed)
        self.assertIn("prior_direct_provider_smoke_is_not_route_mediated_proof", review.non_proofs)


if __name__ == "__main__":
    unittest.main()
