import unittest

from orchestrator.backbone_control_loop import ordered_backbone_stage_names
from orchestrator.backbone_pkms_note_fixture_mapping import (
    PKMS_NOTE_FIXTURE_ADAPTER,
    PKMS_NOTE_FIXTURE_NON_PROOFS,
    PkmsNoteFixtureBackboneStageMapping,
    ordered_pkms_note_fixture_backbone_stage_mappings,
    read_pkms_note_fixture_backbone_mapping_status,
    validate_ordered_pkms_note_fixture_backbone_stage_mappings,
    validate_pkms_note_fixture_backbone_stage_mapping,
)


class Phase326BackbonePkmsNoteFixtureMappingTests(unittest.TestCase):
    def test_pkms_note_fixture_maps_every_backbone_stage(self):
        mappings = ordered_pkms_note_fixture_backbone_stage_mappings()

        self.assertEqual(len(mappings), len(ordered_backbone_stage_names()))
        self.assertEqual(
            tuple(mapping.stage_name for mapping in mappings),
            ordered_backbone_stage_names(),
        )

    def test_mapping_names_pkms_context_without_execution_or_mutation(self):
        status = read_pkms_note_fixture_backbone_mapping_status()

        self.assertEqual(status["bounded_context"], "pkms_note_operation_fixture")
        self.assertEqual(
            PKMS_NOTE_FIXTURE_ADAPTER.bounded_context,
            "pkms_note_operation_fixture",
        )
        self.assertFalse(status["adapter_execution_allowed"])
        self.assertFalse(PKMS_NOTE_FIXTURE_ADAPTER.execution_allowed)
        self.assertFalse(status["live_vault_accessed"])
        self.assertFalse(status["live_pkms_note_mutated"])

    def test_mapping_is_complete_shape_only_second_non_patch_action_fixture(self):
        status = read_pkms_note_fixture_backbone_mapping_status()

        self.assertTrue(status["complete"])
        self.assertTrue(status["all_stage_names_match_backbone"])
        self.assertEqual(status["mapping_count"], len(ordered_backbone_stage_names()))
        self.assertFalse(status["backbone_v0_declared"])

    def test_mapping_uses_fake_pkms_note_operation_strings_only(self):
        mapping = ordered_pkms_note_fixture_backbone_stage_mappings()[0]
        payload = mapping.domain_payload

        self.assertEqual(payload["fake_vault_path"], "C:/FAKE_OBSIDIAN_VAULT_DO_NOT_ACCESS")
        self.assertEqual(payload["fake_note_id"], "fake-note-0001")
        self.assertEqual(payload["fake_note_path"], "Areas/Fake Project/Fake Note.md")
        self.assertIn("fake_frontmatter_change", payload)
        self.assertIn("fake_backlink_insertion", payload)
        self.assertIn("fake_before_note_content_evidence", payload)
        self.assertIn("fake_after_note_content_evidence", payload)
        self.assertIn("fake_operator_authorization", payload)
        self.assertIn("fake_verification_evidence", payload)

    def test_pkms_specific_fields_remain_domain_payload(self):
        validation = validate_pkms_note_fixture_backbone_stage_mapping(
            ordered_pkms_note_fixture_backbone_stage_mappings()[0]
        )

        self.assertIn("fake_vault_path", validation["domain_payload_keys"])
        self.assertIn("fake_note_path", validation["domain_payload_keys"])
        self.assertIn("fake_backlink_insertion", validation["domain_payload_keys"])
        self.assertNotIn(
            "fake_vault_path",
            validation["backbone_native_evidence_fields"],
        )

    def test_mapping_preserves_non_proofs_and_blocks_readiness_claims(self):
        validation = validate_pkms_note_fixture_backbone_stage_mapping(
            ordered_pkms_note_fixture_backbone_stage_mappings()[0]
        )
        status = read_pkms_note_fixture_backbone_mapping_status()

        self.assertEqual(tuple(validation["non_proofs"]), PKMS_NOTE_FIXTURE_NON_PROOFS)
        self.assertIn(
            "pkms_note_fixture_mapping_does_not_access_live_vaults",
            validation["non_proofs"],
        )
        self.assertFalse(status["semantic_correctness_claimed"])
        self.assertFalse(status["production_readiness_claimed"])
        self.assertFalse(status["provider_model_runtime_platform_execution_claimed"])
        self.assertFalse(status["autonomous_ai_coding_claimed"])
        self.assertFalse(status["real_backlink_frontmatter_correctness_claimed"])

    def test_missing_fake_fixture_fields_have_deterministic_reason_codes(self):
        missing_vault = validate_pkms_note_fixture_backbone_stage_mapping(
            PkmsNoteFixtureBackboneStageMapping(
                stage_name="readback",
                phase_docs=("docs/PHASE_326.md",),
                domain_payload={
                    "fake_note_path": "Areas/Fake Project/Fake Note.md",
                    "fake_before_note_content_evidence": "before",
                    "fake_after_note_content_evidence": "after",
                },
            )
        )
        missing_note = validate_pkms_note_fixture_backbone_stage_mapping(
            PkmsNoteFixtureBackboneStageMapping(
                stage_name="readback",
                phase_docs=("docs/PHASE_326.md",),
                domain_payload={
                    "fake_vault_path": "C:/FAKE_OBSIDIAN_VAULT_DO_NOT_ACCESS",
                    "fake_before_note_content_evidence": "before",
                    "fake_after_note_content_evidence": "after",
                },
            )
        )
        missing_before_after = validate_pkms_note_fixture_backbone_stage_mapping(
            PkmsNoteFixtureBackboneStageMapping(
                stage_name="readback",
                phase_docs=("docs/PHASE_326.md",),
                domain_payload={
                    "fake_vault_path": "C:/FAKE_OBSIDIAN_VAULT_DO_NOT_ACCESS",
                    "fake_note_path": "Areas/Fake Project/Fake Note.md",
                },
            )
        )

        self.assertEqual(missing_vault["reason_code"], "fake_vault_path_missing")
        self.assertEqual(missing_note["reason_code"], "fake_note_path_missing")
        self.assertEqual(
            missing_before_after["reason_code"],
            "fake_before_after_evidence_missing",
        )

    def test_order_mismatch_reports_incomplete_without_backbone_v0(self):
        mappings = list(ordered_pkms_note_fixture_backbone_stage_mappings())
        swapped = [mappings[1], mappings[0], *mappings[2:]]

        validation = validate_ordered_pkms_note_fixture_backbone_stage_mappings(swapped)

        self.assertEqual(validation["status"], "incomplete")
        self.assertEqual(validation["reason_code"], "stage_order_mismatch")
        self.assertIn("stage_order_mismatch", validation["incomplete_reason_codes"])
        self.assertFalse(validation["backbone_v0_declared"])


if __name__ == "__main__":
    unittest.main()
