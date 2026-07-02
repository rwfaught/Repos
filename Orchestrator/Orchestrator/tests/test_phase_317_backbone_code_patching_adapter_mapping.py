import unittest

from orchestrator.backbone_code_patching_adapter_mapping import (
    CODE_PATCHING_BACKBONE_ADAPTER,
    CODE_PATCHING_MAPPING_NON_PROOFS,
    CodePatchingBackboneStageMapping,
    ordered_code_patching_backbone_stage_mappings,
    read_code_patching_backbone_mapping_status,
    validate_code_patching_backbone_stage_mapping,
)
from orchestrator.backbone_control_loop import ordered_backbone_stage_names


class Phase317BackboneCodePatchingAdapterMappingTests(unittest.TestCase):
    def test_every_backbone_stage_has_mapping_or_deterministic_reason(self):
        validations = [
            validate_code_patching_backbone_stage_mapping(mapping)
            for mapping in ordered_code_patching_backbone_stage_mappings()
        ]

        self.assertEqual(len(validations), len(ordered_backbone_stage_names()))
        for validation in validations:
            self.assertIn(validation["stage_name"], ordered_backbone_stage_names())
            self.assertTrue(validation["complete"] or validation["reason_code"])

    def test_ordered_mapping_stage_names_match_backbone_stage_names(self):
        self.assertEqual(
            tuple(mapping.stage_name for mapping in ordered_code_patching_backbone_stage_mappings()),
            ordered_backbone_stage_names(),
        )

    def test_mapping_names_code_patching_bounded_context_without_execution(self):
        status = read_code_patching_backbone_mapping_status()

        self.assertEqual(status["bounded_context"], "code_patching")
        self.assertEqual(CODE_PATCHING_BACKBONE_ADAPTER.bounded_context, "code_patching")
        self.assertFalse(status["adapter_execution_allowed"])
        self.assertFalse(CODE_PATCHING_BACKBONE_ADAPTER.execution_allowed)

    def test_mapping_references_patch_loop_sources_as_strings_only(self):
        source_modules = {
            source
            for mapping in ordered_code_patching_backbone_stage_mappings()
            for source in mapping.source_modules
        }

        self.assertIn(
            "orchestrator/packet_result_patch_proposal_eligibility.py",
            source_modules,
        )
        self.assertIn("orchestrator/authorized_draft_patch_apply.py", source_modules)
        self.assertIn(
            "orchestrator/verified_bounded_apply_task_finalization.py",
            source_modules,
        )
        for source in source_modules:
            self.assertIsInstance(source, str)

    def test_mapping_preserves_non_proofs(self):
        validation = validate_code_patching_backbone_stage_mapping(
            ordered_code_patching_backbone_stage_mappings()[0]
        )

        self.assertIn(
            "code_patching_mapping_is_not_semantic_correctness",
            validation["non_proofs"],
        )
        self.assertIn(
            "code_patching_mapping_does_not_migrate_patch_loop",
            validation["non_proofs"],
        )
        self.assertEqual(tuple(validation["non_proofs"]), CODE_PATCHING_MAPPING_NON_PROOFS)

    def test_mapping_reports_backbone_v0_not_declared(self):
        status = read_code_patching_backbone_mapping_status()

        self.assertFalse(status["backbone_v0_declared"])

    def test_patch_specific_references_remain_domain_specific(self):
        validation = validate_code_patching_backbone_stage_mapping(
            ordered_code_patching_backbone_stage_mappings()[2]
        )

        self.assertIn("patch_loop_role", validation["domain_payload_keys"])
        self.assertNotIn("patch_loop_role", validation["backbone_native_evidence_fields"])
        self.assertIn("source_modules", validation)
        self.assertNotIn("source_modules", validation["backbone_native_evidence_fields"])

    def test_missing_mapping_fields_have_deterministic_reason_codes(self):
        missing_stage = validate_code_patching_backbone_stage_mapping(
            {"stage_name": "", "bounded_context": "code_patching"}
        )
        missing_context = validate_code_patching_backbone_stage_mapping(
            CodePatchingBackboneStageMapping(
                stage_name="readback",
                bounded_context="",
                source_modules=("orchestrator/backbone_control_loop.py",),
                phase_docs=("docs/PHASE_316.md",),
            )
        )
        missing_source = validate_code_patching_backbone_stage_mapping(
            CodePatchingBackboneStageMapping(
                stage_name="readback",
                source_modules=(),
                phase_docs=("docs/PHASE_316.md",),
            )
        )
        missing_phase = validate_code_patching_backbone_stage_mapping(
            CodePatchingBackboneStageMapping(
                stage_name="readback",
                source_modules=("orchestrator/backbone_control_loop.py",),
            )
        )

        self.assertEqual(missing_stage["reason_code"], "stage_name_missing")
        self.assertEqual(missing_context["reason_code"], "bounded_context_missing")
        self.assertEqual(missing_source["reason_code"], "source_evidence_missing")
        self.assertEqual(missing_phase["reason_code"], "phase_evidence_missing")

    def test_mapping_can_produce_readback_status(self):
        status = read_code_patching_backbone_mapping_status()

        self.assertEqual(status["mapping_count"], len(ordered_backbone_stage_names()))
        self.assertTrue(status["all_stage_names_match_backbone"])
        self.assertTrue(status["complete"])

    def test_mapping_does_not_claim_forbidden_proofs_or_migration(self):
        status = read_code_patching_backbone_mapping_status()

        self.assertFalse(status["semantic_correctness_claimed"])
        self.assertFalse(status["production_readiness_claimed"])
        self.assertFalse(status["provider_model_runtime_platform_execution_claimed"])
        self.assertFalse(status["autonomous_ai_coding_claimed"])
        self.assertFalse(status["patch_loop_migrated"])


if __name__ == "__main__":
    unittest.main()
