import unittest

from orchestrator.backbone_research_claim_fixture_mapping import (
    RESEARCH_CLAIM_FIXTURE_ADAPTER,
    RESEARCH_CLAIM_FIXTURE_NON_PROOFS,
    ResearchClaimFixtureBackboneStageMapping,
    ordered_research_claim_fixture_backbone_stage_mappings,
    read_research_claim_fixture_backbone_mapping_status,
    validate_research_claim_fixture_backbone_stage_mapping,
    validate_ordered_research_claim_fixture_backbone_stage_mappings,
)


class Phase323BackboneNonPatchFixtureNegativeEdgeTests(unittest.TestCase):
    def _mapping(self, **overrides):
        values = {
            "stage_name": "readback",
            "bounded_context": "research_claim_packet_fixture",
            "fixture_sources": ("fixtures/research_claim_packet/static_claim_packet.json",),
            "phase_docs": ("docs/PHASE_322.md",),
            "phase_tests": ("tests/test_phase_322_backbone_non_patch_fixture_mapping.py",),
            "domain_payload": {
                "fixture_packet_id": "static_research_claim_packet_fixture_001",
                "fixture_stage_role": "fixture_readback",
            },
        }
        values.update(overrides)
        return ResearchClaimFixtureBackboneStageMapping(**values)

    def test_missing_stage_returns_deterministic_reason(self):
        validation = validate_research_claim_fixture_backbone_stage_mapping(
            {"stage_name": "", "bounded_context": "research_claim_packet_fixture"}
        )

        self.assertEqual(validation["status"], "incomplete")
        self.assertEqual(validation["reason_code"], "stage_name_missing")

    def test_unknown_stage_returns_deterministic_reason(self):
        validation = validate_research_claim_fixture_backbone_stage_mapping(
            self._mapping(stage_name="unknown_phase323_stage")
        )

        self.assertEqual(validation["reason_code"], "unknown_stage_name")

    def test_wrong_bounded_context_returns_deterministic_reason(self):
        validation = validate_research_claim_fixture_backbone_stage_mapping(
            self._mapping(bounded_context="code_patching")
        )

        self.assertEqual(validation["reason_code"], "bounded_context_missing")

    def test_missing_fixture_evidence_returns_deterministic_reasons(self):
        missing_source = validate_research_claim_fixture_backbone_stage_mapping(
            self._mapping(fixture_sources=())
        )
        missing_phase = validate_research_claim_fixture_backbone_stage_mapping(
            self._mapping(phase_docs=(), phase_tests=())
        )

        self.assertEqual(missing_source["reason_code"], "fixture_source_missing")
        self.assertEqual(
            missing_phase["reason_code"],
            "fixture_doc_or_test_evidence_missing",
        )

    def test_mismatched_stage_order_reports_incomplete(self):
        mappings = list(ordered_research_claim_fixture_backbone_stage_mappings())
        swapped = [mappings[1], mappings[0], *mappings[2:]]

        validation = validate_ordered_research_claim_fixture_backbone_stage_mappings(swapped)

        self.assertEqual(validation["status"], "incomplete")
        self.assertEqual(validation["reason_code"], "stage_order_mismatch")
        self.assertIn("stage_order_mismatch", validation["incomplete_reason_codes"])

    def test_backbone_v0_and_adapter_execution_claims_are_rejected(self):
        mapping = self._mapping().as_dict()

        v0_claim = validate_research_claim_fixture_backbone_stage_mapping(
            {**mapping, "backbone_v0_declared": True}
        )
        adapter_claim = validate_research_claim_fixture_backbone_stage_mapping(
            {**mapping, "adapter_executed": True}
        )

        self.assertFalse(RESEARCH_CLAIM_FIXTURE_ADAPTER.execution_allowed)
        self.assertEqual(v0_claim["reason_code"], "backbone_v0_claim_rejected")
        self.assertEqual(adapter_claim["reason_code"], "adapter_execution_claim_rejected")

    def test_real_domain_and_live_record_claims_are_rejected(self):
        mapping = self._mapping().as_dict()

        real_action_claim = validate_research_claim_fixture_backbone_stage_mapping(
            {**mapping, "real_domain_action_executed": True}
        )
        live_record_claim = validate_research_claim_fixture_backbone_stage_mapping(
            {**mapping, "live_record_mutated": True}
        )

        self.assertEqual(
            real_action_claim["reason_code"],
            "real_domain_action_claim_rejected",
        )
        self.assertEqual(
            live_record_claim["reason_code"],
            "real_domain_action_claim_rejected",
        )

    def test_smuggled_semantic_and_production_claims_are_rejected(self):
        mapping = self._mapping().as_dict()

        semantic_claim = validate_research_claim_fixture_backbone_stage_mapping(
            {**mapping, "semantic_correctness_claimed": True}
        )
        production_claim = validate_research_claim_fixture_backbone_stage_mapping(
            {**mapping, "production_readiness_claimed": True}
        )

        self.assertEqual(
            semantic_claim["reason_code"],
            "real_domain_action_claim_rejected",
        )
        self.assertEqual(
            production_claim["reason_code"],
            "real_domain_action_claim_rejected",
        )

    def test_official_capsule_claim_is_rejected(self):
        validation = validate_research_claim_fixture_backbone_stage_mapping(
            {**self._mapping().as_dict(), "official_capsule_generated": True}
        )

        self.assertEqual(validation["reason_code"], "official_capsule_claim_rejected")

    def test_fixture_specific_fields_cannot_be_backbone_native(self):
        validation = validate_research_claim_fixture_backbone_stage_mapping(
            {
                **self._mapping().as_dict(),
                "backbone_native_evidence_fields": [
                    "record_id",
                    "stage_name",
                    "fixture_packet_id",
                ],
            }
        )

        self.assertEqual(
            validation["reason_code"],
            "fixture_specific_native_field_rejected",
        )

    def test_incomplete_status_preserves_non_proofs_without_v0(self):
        status = read_research_claim_fixture_backbone_mapping_status(
            [self._mapping(fixture_sources=())]
        )

        self.assertFalse(status["complete"])
        self.assertEqual(status["incomplete_mapping_count"], 1)
        self.assertIn("fixture_source_missing", status["incomplete_reason_codes"])
        self.assertEqual(tuple(status["non_proofs"]), RESEARCH_CLAIM_FIXTURE_NON_PROOFS)
        self.assertFalse(status["backbone_v0_declared"])
        self.assertFalse(status["real_domain_action_executed"])


if __name__ == "__main__":
    unittest.main()
