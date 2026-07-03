import unittest

from orchestrator.backbone_control_loop import ordered_backbone_stage_names
from orchestrator.backbone_research_claim_fixture_mapping import (
    RESEARCH_CLAIM_FIXTURE_ADAPTER,
    RESEARCH_CLAIM_FIXTURE_NON_PROOFS,
    ResearchClaimFixtureBackboneStageMapping,
    ordered_research_claim_fixture_backbone_stage_mappings,
    read_research_claim_fixture_backbone_mapping_status,
    validate_research_claim_fixture_backbone_stage_mapping,
    validate_ordered_research_claim_fixture_backbone_stage_mappings,
)


class Phase322BackboneNonPatchFixtureMappingTests(unittest.TestCase):
    def test_research_claim_fixture_maps_every_backbone_stage(self):
        mappings = ordered_research_claim_fixture_backbone_stage_mappings()

        self.assertEqual(len(mappings), len(ordered_backbone_stage_names()))
        self.assertEqual(
            tuple(mapping.stage_name for mapping in mappings),
            ordered_backbone_stage_names(),
        )

    def test_mapping_names_non_patch_fixture_context_without_execution(self):
        status = read_research_claim_fixture_backbone_mapping_status()

        self.assertEqual(status["bounded_context"], "research_claim_packet_fixture")
        self.assertEqual(
            RESEARCH_CLAIM_FIXTURE_ADAPTER.bounded_context,
            "research_claim_packet_fixture",
        )
        self.assertFalse(status["adapter_execution_allowed"])
        self.assertFalse(RESEARCH_CLAIM_FIXTURE_ADAPTER.execution_allowed)
        self.assertFalse(status["real_domain_action_executed"])
        self.assertFalse(status["live_record_mutated"])

    def test_mapping_is_complete_shape_only_second_bounded_context(self):
        status = read_research_claim_fixture_backbone_mapping_status()

        self.assertTrue(status["complete"])
        self.assertTrue(status["all_stage_names_match_backbone"])
        self.assertEqual(status["mapping_count"], len(ordered_backbone_stage_names()))
        self.assertFalse(status["backbone_v0_declared"])

    def test_mapping_references_static_fixture_sources_as_strings_only(self):
        fixture_sources = {
            source
            for mapping in ordered_research_claim_fixture_backbone_stage_mappings()
            for source in mapping.fixture_sources
        }

        self.assertEqual(
            fixture_sources,
            {"fixtures/research_claim_packet/static_claim_packet.json"},
        )
        for source in fixture_sources:
            self.assertIsInstance(source, str)

    def test_fixture_specific_fields_remain_domain_payload(self):
        validation = validate_research_claim_fixture_backbone_stage_mapping(
            ordered_research_claim_fixture_backbone_stage_mappings()[0]
        )

        self.assertIn("fixture_packet_id", validation["domain_payload_keys"])
        self.assertIn("fixture_stage_role", validation["domain_payload_keys"])
        self.assertNotIn(
            "fixture_packet_id",
            validation["backbone_native_evidence_fields"],
        )

    def test_mapping_preserves_non_proofs_and_blocks_claims(self):
        validation = validate_research_claim_fixture_backbone_stage_mapping(
            ordered_research_claim_fixture_backbone_stage_mappings()[0]
        )
        status = read_research_claim_fixture_backbone_mapping_status()

        self.assertEqual(tuple(validation["non_proofs"]), RESEARCH_CLAIM_FIXTURE_NON_PROOFS)
        self.assertIn(
            "research_claim_fixture_mapping_does_not_execute_real_domain_actions",
            validation["non_proofs"],
        )
        self.assertFalse(status["semantic_correctness_claimed"])
        self.assertFalse(status["production_readiness_claimed"])
        self.assertFalse(status["provider_model_runtime_platform_execution_claimed"])
        self.assertFalse(status["autonomous_ai_coding_claimed"])

    def test_missing_mapping_fields_have_deterministic_reason_codes(self):
        missing_stage = validate_research_claim_fixture_backbone_stage_mapping(
            {"stage_name": "", "bounded_context": "research_claim_packet_fixture"}
        )
        missing_context = validate_research_claim_fixture_backbone_stage_mapping(
            ResearchClaimFixtureBackboneStageMapping(
                stage_name="readback",
                bounded_context="",
                fixture_sources=("fixtures/research_claim_packet/static_claim_packet.json",),
                phase_docs=("docs/PHASE_322.md",),
            )
        )
        missing_source = validate_research_claim_fixture_backbone_stage_mapping(
            ResearchClaimFixtureBackboneStageMapping(
                stage_name="readback",
                fixture_sources=(),
                phase_docs=("docs/PHASE_322.md",),
            )
        )
        missing_phase = validate_research_claim_fixture_backbone_stage_mapping(
            ResearchClaimFixtureBackboneStageMapping(
                stage_name="readback",
                fixture_sources=("fixtures/research_claim_packet/static_claim_packet.json",),
            )
        )

        self.assertEqual(missing_stage["reason_code"], "stage_name_missing")
        self.assertEqual(missing_context["reason_code"], "bounded_context_missing")
        self.assertEqual(missing_source["reason_code"], "fixture_source_missing")
        self.assertEqual(
            missing_phase["reason_code"],
            "fixture_doc_or_test_evidence_missing",
        )

    def test_order_mismatch_reports_incomplete_without_backbone_v0(self):
        mappings = list(ordered_research_claim_fixture_backbone_stage_mappings())
        swapped = [mappings[1], mappings[0], *mappings[2:]]

        validation = validate_ordered_research_claim_fixture_backbone_stage_mappings(swapped)

        self.assertEqual(validation["status"], "incomplete")
        self.assertEqual(validation["reason_code"], "stage_order_mismatch")
        self.assertIn("stage_order_mismatch", validation["incomplete_reason_codes"])
        self.assertFalse(validation["backbone_v0_declared"])

    def test_execution_and_live_mutation_claims_are_rejected(self):
        mapping = ordered_research_claim_fixture_backbone_stage_mappings()[0].as_dict()

        adapter_claim = validate_research_claim_fixture_backbone_stage_mapping(
            {**mapping, "adapter_execution_allowed": True}
        )
        action_claim = validate_research_claim_fixture_backbone_stage_mapping(
            {**mapping, "real_domain_action_executed": True}
        )
        live_mutation_claim = validate_research_claim_fixture_backbone_stage_mapping(
            {**mapping, "live_record_mutated": True}
        )

        self.assertEqual(adapter_claim["reason_code"], "adapter_execution_claim_rejected")
        self.assertEqual(action_claim["reason_code"], "real_domain_action_claim_rejected")
        self.assertEqual(
            live_mutation_claim["reason_code"],
            "real_domain_action_claim_rejected",
        )


if __name__ == "__main__":
    unittest.main()
