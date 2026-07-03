import unittest

from orchestrator.backbone_v0_criteria import (
    BACKBONE_V0_CRITERIA_NON_PROOFS,
    read_current_backbone_v0_criteria_evidence,
    validate_backbone_v0_criteria_evidence,
)


class Phase332BackboneV0CriteriaNegativeEdgeTests(unittest.TestCase):
    def _evidence(self):
        return read_current_backbone_v0_criteria_evidence()

    def test_current_evidence_validates_without_declaring_v0(self):
        validation = validate_backbone_v0_criteria_evidence()

        self.assertTrue(validation["valid"])
        self.assertEqual(validation["status"], "criteria_valid")
        self.assertEqual(validation["reason_code"], "")
        self.assertFalse(validation["backbone_v0_declared"])

    def test_missing_scaffold_evidence_is_rejected(self):
        evidence = self._evidence()
        evidence["scaffold"] = {}

        validation = validate_backbone_v0_criteria_evidence(evidence)

        self.assertFalse(validation["valid"])
        self.assertEqual(validation["reason_code"], "missing_scaffold_evidence")

    def test_missing_real_product_context_is_rejected(self):
        evidence = self._evidence()
        evidence["mapped_contexts"].pop("code_patching")

        validation = validate_backbone_v0_criteria_evidence(evidence)

        self.assertEqual(validation["reason_code"], "missing_mapped_context")

    def test_missing_second_non_patch_fixture_is_rejected(self):
        evidence = self._evidence()
        evidence["mapped_contexts"].pop("pkms_note_operation_fixture")

        validation = validate_backbone_v0_criteria_evidence(evidence)

        self.assertEqual(validation["reason_code"], "missing_non_patch_fixture")

    def test_missing_negative_edge_coverage_is_rejected(self):
        evidence = self._evidence()
        evidence["negative_edge_contexts"].pop("pkms_note_operation_fixture")

        validation = validate_backbone_v0_criteria_evidence(evidence)

        self.assertEqual(validation["reason_code"], "missing_negative_edge_coverage")

    def test_missing_readback_or_decision_boundary_is_rejected(self):
        evidence = self._evidence()
        evidence["decision_boundaries"].pop("research_claim_packet_fixture")

        validation = validate_backbone_v0_criteria_evidence(evidence)

        self.assertEqual(
            validation["reason_code"],
            "missing_readback_decision_boundary",
        )

    def test_smuggled_declaration_and_semantic_claims_are_rejected(self):
        declaration = validate_backbone_v0_criteria_evidence(
            {**self._evidence(), "backbone_v0_declared": True}
        )
        semantic = validate_backbone_v0_criteria_evidence(
            {**self._evidence(), "semantic_correctness_claimed": True}
        )

        self.assertEqual(
            declaration["reason_code"],
            "backbone_v0_declaration_claim_rejected",
        )
        self.assertEqual(
            semantic["reason_code"],
            "semantic_correctness_claim_rejected",
        )

    def test_smuggled_production_provider_and_execution_claims_are_rejected(self):
        production = validate_backbone_v0_criteria_evidence(
            {**self._evidence(), "production_readiness_claimed": True}
        )
        provider = validate_backbone_v0_criteria_evidence(
            {
                **self._evidence(),
                "provider_model_runtime_platform_execution_claimed": True,
            }
        )
        execution = validate_backbone_v0_criteria_evidence(
            {**self._evidence(), "real_domain_execution_claimed": True}
        )

        self.assertEqual(
            production["reason_code"],
            "production_readiness_claim_rejected",
        )
        self.assertEqual(
            provider["reason_code"],
            "provider_model_runtime_claim_rejected",
        )
        self.assertEqual(
            execution["reason_code"],
            "real_domain_execution_claim_rejected",
        )

    def test_official_capsule_claim_without_authority_is_rejected(self):
        validation = validate_backbone_v0_criteria_evidence(
            {**self._evidence(), "official_capsule_proof_current": True}
        )

        self.assertEqual(validation["reason_code"], "official_capsule_claim_rejected")

    def test_fixture_mapping_as_live_integration_is_rejected(self):
        validation = validate_backbone_v0_criteria_evidence(
            {**self._evidence(), "fixture_mapping_treated_as_live_integration": True}
        )

        self.assertEqual(
            validation["reason_code"],
            "fixture_live_integration_claim_rejected",
        )

    def test_non_proofs_preserved_on_invalid_evidence(self):
        validation = validate_backbone_v0_criteria_evidence({})

        self.assertEqual(tuple(validation["non_proofs"]), BACKBONE_V0_CRITERIA_NON_PROOFS)
        self.assertFalse(validation["backbone_v0_declared"])
        self.assertFalse(validation["declaration_allowed_now"])


if __name__ == "__main__":
    unittest.main()
