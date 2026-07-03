import unittest

from orchestrator.backbone_v0_criteria import (
    BACKBONE_V0_CRITERIA_NON_PROOFS,
    evaluate_backbone_v0_criteria,
    read_current_backbone_v0_criteria_evidence,
)


class Phase331BackboneV0CriteriaScaffoldTests(unittest.TestCase):
    def test_current_evidence_contains_three_mapped_contexts(self):
        evidence = read_current_backbone_v0_criteria_evidence()

        self.assertIn("code_patching", evidence["mapped_contexts"])
        self.assertIn("research_claim_packet_fixture", evidence["mapped_contexts"])
        self.assertIn("pkms_note_operation_fixture", evidence["mapped_contexts"])

    def test_criteria_scaffold_defines_required_criteria_without_v0_declaration(self):
        evaluation = evaluate_backbone_v0_criteria()
        criterion_ids = {item["criterion_id"] for item in evaluation["criteria"]}

        self.assertTrue(evaluation["backbone_v0_criteria_evaluation"])
        self.assertFalse(evaluation["backbone_v0_declared"])
        self.assertFalse(evaluation["declaration_allowed_now"])
        self.assertEqual(evaluation["criteria_count"], 13)
        self.assertIn("domain_neutral_scaffold_exists", criterion_ids)
        self.assertIn("real_product_bounded_context_mapping_exists", criterion_ids)
        self.assertIn("two_non_patch_fixture_mappings_exist", criterion_ids)
        self.assertIn("official_clean_capsule_required", criterion_ids)
        self.assertIn("semantic_and_production_not_implied", criterion_ids)

    def test_current_static_source_test_docs_posture_satisfies_definition_criteria(self):
        evaluation = evaluate_backbone_v0_criteria()

        self.assertTrue(evaluation["all_criteria_satisfied_for_definition"])
        self.assertEqual(evaluation["unsatisfied_criteria_count"], 0)
        self.assertEqual(evaluation["missing_requirements"], [])

    def test_declaration_remains_blocked_and_capsule_proof_absent(self):
        evaluation = evaluate_backbone_v0_criteria()

        self.assertIn(
            "backbone_v0_declaration_boundary_not_authorized",
            evaluation["declaration_blockers"],
        )
        self.assertIn(
            "official_clean_capsule_proof_missing",
            evaluation["declaration_blockers"],
        )
        self.assertTrue(evaluation["official_clean_capsule_required_before_declaration"])
        self.assertFalse(evaluation["official_capsule_proof_current"])

    def test_non_proofs_are_preserved(self):
        evaluation = evaluate_backbone_v0_criteria()

        self.assertEqual(
            tuple(evaluation["non_proofs"]),
            BACKBONE_V0_CRITERIA_NON_PROOFS,
        )
        self.assertIn(
            "criteria_do_not_prove_semantic_correctness",
            evaluation["non_proofs"],
        )
        self.assertIn(
            "criteria_do_not_prove_production_readiness",
            evaluation["non_proofs"],
        )


if __name__ == "__main__":
    unittest.main()
