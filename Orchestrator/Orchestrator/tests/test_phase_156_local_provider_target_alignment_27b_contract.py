import unittest

from orchestrator.provider_evidence_registry import (
    get_model_metadata_evidence,
    get_provider_evidence_for_catalog_key,
    summarize_provider_evidence_for_catalog_key,
)
from orchestrator.provider_generation_smoke_probe_packet import get_local_provider_generation_smoke_probe_packet


class Phase156LocalProviderTargetAlignment27bContractTests(unittest.TestCase):
    def test_active_generation_smoke_probe_packet_targets_27b(self):
        packet = get_local_provider_generation_smoke_probe_packet()

        self.assertEqual(packet.provider_catalog_key, "local_model_candidate")
        self.assertEqual(packet.model_name, "qwen3.6:27b")
        self.assertEqual(packet.request_shape["model"], "qwen3.6:27b")
        self.assertEqual(packet.future_boundary, "PHASE_157_LOCAL_PROVIDER_GENERATION_SMOKE_PROBE_27B_OPERATOR_PROOF")

    def test_27b_visibility_is_model_list_only_without_metadata_or_generate_proof(self):
        records = get_provider_evidence_for_catalog_key("local_model_candidate")
        summary = summarize_provider_evidence_for_catalog_key("local_model_candidate")
        visible_model_names = tuple(name for record in records for name in record.model_names)

        self.assertIn("qwen3.6:27b", visible_model_names)
        self.assertIsNone(get_model_metadata_evidence("qwen3.6:27b"))
        self.assertEqual(summary["provider_evidence_status"], "read_only_metadata_visible")
        self.assertEqual(summary["model_name"], "qwen3-30b-24k:latest")

    def test_packet_preserves_non_executing_authority_flags(self):
        packet = get_local_provider_generation_smoke_probe_packet()

        self.assertFalse(packet.provider_selection_allowed)
        self.assertFalse(packet.provider_execution_allowed)
        self.assertFalse(packet.generation_allowed_now)
        self.assertFalse(packet.route_execution_allowed)
        self.assertFalse(packet.production_readiness)
        self.assertIn("packet_contract_is_not_generation", packet.non_proofs)
        self.assertIn("packet_contract_is_not_api_generate", packet.non_proofs)
        self.assertTrue(all(flag is False for flag in packet.activity_flags.values()))


if __name__ == "__main__":
    unittest.main()
