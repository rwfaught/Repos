import unittest

from orchestrator.backbone_code_patching_adapter_mapping import (
    CODE_PATCHING_BACKBONE_RECOMMENDED_NEXT_BOUNDARY,
    CODE_PATCHING_MAPPING_NON_PROOFS,
    CodePatchingBackboneStageMapping,
    ordered_code_patching_backbone_stage_mappings,
    read_code_patching_backbone_operator_readback,
)


class Phase319BackboneMappingReadbackOperatorRunbookTests(unittest.TestCase):
    def test_operator_readback_exists_and_is_deterministic(self):
        first = read_code_patching_backbone_operator_readback()
        second = read_code_patching_backbone_operator_readback()

        self.assertEqual(first, second)
        self.assertTrue(first["code_patching_backbone_operator_readback"])

    def test_readback_preserves_false_v0_execution_and_migration_claims(self):
        readback = read_code_patching_backbone_operator_readback()

        self.assertFalse(readback["backbone_v0_declared"])
        self.assertFalse(readback["adapter_execution_allowed"])
        self.assertFalse(readback["adapters_executable_through_mapping"])
        self.assertFalse(readback["patch_loop_migrated"])

    def test_readback_reports_code_patching_context_and_ordered_stages(self):
        readback = read_code_patching_backbone_operator_readback()
        expected_stage_names = [
            mapping.stage_name for mapping in ordered_code_patching_backbone_stage_mappings()
        ]

        self.assertEqual(readback["bounded_context"], "code_patching")
        self.assertEqual(readback["mapped_stage_names"], expected_stage_names)
        self.assertEqual(
            readback["mapped_stage_names"],
            readback["expected_backbone_stage_names"],
        )

    def test_readback_includes_status_counts_and_stage_statuses(self):
        readback = read_code_patching_backbone_operator_readback()

        self.assertEqual(readback["status_counts"]["mapped"], 13)
        self.assertEqual(readback["status_counts"]["incomplete"], 0)
        self.assertEqual(readback["status_counts"]["blocked"], 0)
        self.assertEqual(readback["status_counts"]["not_applicable"], 0)
        self.assertEqual(len(readback["stage_statuses"]), 13)
        self.assertTrue(all(stage["complete"] for stage in readback["stage_statuses"]))

    def test_readback_preserves_non_proofs(self):
        readback = read_code_patching_backbone_operator_readback()

        self.assertEqual(tuple(readback["non_proofs"]), CODE_PATCHING_MAPPING_NON_PROOFS)
        self.assertFalse(readback["semantic_correctness_claimed"])
        self.assertFalse(readback["production_readiness_claimed"])
        self.assertFalse(readback["provider_model_runtime_platform_execution_claimed"])
        self.assertFalse(readback["autonomous_ai_coding_claimed"])

    def test_readback_separates_backbone_native_and_code_patching_fields(self):
        readback = read_code_patching_backbone_operator_readback()

        self.assertIn("stage_name", readback["backbone_native_fields"])
        self.assertIn("patch_loop_role", readback["code_patching_specific_fields"])
        self.assertNotIn("patch_loop_role", readback["backbone_native_fields"])

    def test_readback_exposes_source_doc_test_evidence_as_reference_only(self):
        readback = read_code_patching_backbone_operator_readback()
        evidence = readback["source_doc_test_evidence_strings"]

        self.assertTrue(evidence["evidence_is_reference_only"])
        self.assertIn(
            "orchestrator/packet_result_patch_proposal_eligibility.py",
            evidence["source_modules"],
        )
        self.assertIn("docs/PHASE_316.md", evidence["phase_docs"])
        self.assertIn(
            "tests/test_phase_316_backbone_v0_abstraction_scaffold.py",
            evidence["phase_tests"],
        )

    def test_readback_exposes_negative_edge_reason_codes(self):
        readback = read_code_patching_backbone_operator_readback()

        self.assertIn(
            "adapter_execution_claim_rejected",
            readback["possible_negative_edge_reason_codes"],
        )
        self.assertIn(
            "patch_specific_native_field_rejected",
            readback["possible_negative_edge_reason_codes"],
        )

    def test_incomplete_readback_reports_blocked_conditions_without_v0(self):
        incomplete_mapping = CodePatchingBackboneStageMapping(
            stage_name="readback",
            source_modules=(),
            phase_docs=("docs/PHASE_316.md",),
            phase_tests=("tests/test_phase_316_backbone_v0_abstraction_scaffold.py",),
        )

        readback = read_code_patching_backbone_operator_readback([incomplete_mapping])

        self.assertEqual(readback["status_counts"]["incomplete"], 1)
        self.assertIn("source_evidence_missing", readback["blocked_conditions"])
        self.assertFalse(readback["backbone_v0_declared"])

    def test_readback_recommends_next_boundary_without_declaring_backbone_v0(self):
        readback = read_code_patching_backbone_operator_readback()

        self.assertEqual(
            readback["recommended_next_boundary"],
            CODE_PATCHING_BACKBONE_RECOMMENDED_NEXT_BOUNDARY,
        )
        self.assertNotIn("V0_DECLARATION", readback["recommended_next_boundary"])
        self.assertFalse(readback["backbone_v0_declared"])


if __name__ == "__main__":
    unittest.main()
