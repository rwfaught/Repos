import unittest

from orchestrator.backbone_code_patching_adapter_mapping import (
    CODE_PATCHING_BACKBONE_ADAPTER,
    CODE_PATCHING_MAPPING_NON_PROOFS,
    CodePatchingBackboneStageMapping,
    ordered_code_patching_backbone_stage_mappings,
    read_code_patching_backbone_mapping_status,
    validate_code_patching_backbone_stage_mapping,
    validate_ordered_code_patching_backbone_stage_mappings,
)


class Phase318BackboneMappingNegativeEdgeContractTests(unittest.TestCase):
    def _mapping(self, **overrides):
        values = {
            "stage_name": "readback",
            "bounded_context": "code_patching",
            "source_modules": ("orchestrator/backbone_control_loop.py",),
            "phase_docs": ("docs/PHASE_316.md",),
            "phase_tests": ("tests/test_phase_316_backbone_v0_abstraction_scaffold.py",),
            "domain_payload": {"patch_loop_role": "readback"},
        }
        values.update(overrides)
        return CodePatchingBackboneStageMapping(**values)

    def test_missing_stage_returns_deterministic_reason(self):
        validation = validate_code_patching_backbone_stage_mapping(
            {"stage_name": "", "bounded_context": "code_patching"}
        )

        self.assertEqual(validation["status"], "incomplete")
        self.assertEqual(validation["reason_code"], "stage_name_missing")

    def test_unknown_stage_returns_deterministic_reason(self):
        validation = validate_code_patching_backbone_stage_mapping(
            self._mapping(stage_name="unknown_phase318_stage")
        )

        self.assertEqual(validation["reason_code"], "unknown_stage_name")

    def test_wrong_bounded_context_returns_deterministic_reason(self):
        validation = validate_code_patching_backbone_stage_mapping(
            self._mapping(bounded_context="general_answer")
        )

        self.assertEqual(validation["reason_code"], "bounded_context_missing")

    def test_missing_evidence_returns_deterministic_reasons(self):
        missing_source = validate_code_patching_backbone_stage_mapping(
            self._mapping(source_modules=())
        )
        missing_phase = validate_code_patching_backbone_stage_mapping(
            self._mapping(phase_docs=(), phase_tests=())
        )

        self.assertEqual(missing_source["reason_code"], "source_evidence_missing")
        self.assertEqual(missing_phase["reason_code"], "phase_evidence_missing")

    def test_mismatched_stage_order_reports_incomplete(self):
        mappings = list(ordered_code_patching_backbone_stage_mappings())
        swapped = [mappings[1], mappings[0], *mappings[2:]]

        validation = validate_ordered_code_patching_backbone_stage_mappings(swapped)

        self.assertEqual(validation["status"], "incomplete")
        self.assertEqual(validation["reason_code"], "stage_order_mismatch")
        self.assertIn("stage_order_mismatch", validation["incomplete_reason_codes"])

    def test_adapter_execution_stays_disabled_and_execution_claim_is_rejected(self):
        validation = validate_code_patching_backbone_stage_mapping(
            {
                **self._mapping().as_dict(),
                "adapter_execution_allowed": True,
            }
        )

        self.assertFalse(CODE_PATCHING_BACKBONE_ADAPTER.execution_allowed)
        self.assertEqual(validation["reason_code"], "adapter_execution_claim_rejected")

    def test_backbone_v0_and_patch_loop_migration_claims_are_rejected(self):
        v0_claim = validate_code_patching_backbone_stage_mapping(
            {**self._mapping().as_dict(), "backbone_v0_declared": True}
        )
        migration_claim = validate_code_patching_backbone_stage_mapping(
            {**self._mapping().as_dict(), "patch_loop_migrated": True}
        )

        self.assertEqual(v0_claim["reason_code"], "backbone_v0_claim_rejected")
        self.assertEqual(
            migration_claim["reason_code"],
            "patch_loop_migration_claim_rejected",
        )

    def test_patch_specific_fields_cannot_be_backbone_native(self):
        validation = validate_code_patching_backbone_stage_mapping(
            {
                **self._mapping().as_dict(),
                "backbone_native_evidence_fields": [
                    "record_id",
                    "stage_name",
                    "patch_loop_role",
                ],
            }
        )

        self.assertEqual(
            validation["reason_code"],
            "patch_specific_native_field_rejected",
        )

    def test_domain_payload_keys_remain_domain_payload(self):
        validation = validate_code_patching_backbone_stage_mapping(self._mapping())

        self.assertIn("patch_loop_role", validation["domain_payload_keys"])
        self.assertNotIn("patch_loop_role", validation["backbone_native_evidence_fields"])

    def test_incomplete_readback_preserves_non_proofs(self):
        status = read_code_patching_backbone_mapping_status([self._mapping(source_modules=())])

        self.assertFalse(status["complete"])
        self.assertEqual(status["incomplete_mapping_count"], 1)
        self.assertIn("source_evidence_missing", status["incomplete_reason_codes"])
        self.assertEqual(tuple(status["non_proofs"]), CODE_PATCHING_MAPPING_NON_PROOFS)
        self.assertFalse(status["backbone_v0_declared"])
        self.assertFalse(status["patch_loop_migrated"])


if __name__ == "__main__":
    unittest.main()
