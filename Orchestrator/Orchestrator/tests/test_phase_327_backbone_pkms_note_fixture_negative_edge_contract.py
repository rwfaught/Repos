import unittest

from orchestrator.backbone_pkms_note_fixture_mapping import (
    PKMS_NOTE_FIXTURE_ADAPTER,
    PKMS_NOTE_FIXTURE_NON_PROOFS,
    PkmsNoteFixtureBackboneStageMapping,
    ordered_pkms_note_fixture_backbone_stage_mappings,
    read_pkms_note_fixture_backbone_mapping_status,
    validate_ordered_pkms_note_fixture_backbone_stage_mappings,
    validate_pkms_note_fixture_backbone_stage_mapping,
)


class Phase327BackbonePkmsNoteFixtureNegativeEdgeTests(unittest.TestCase):
    def _mapping(self, **overrides):
        values = {
            "stage_name": "readback",
            "bounded_context": "pkms_note_operation_fixture",
            "fixture_sources": ("fixtures/pkms_note_operation/static_note_operation.json",),
            "phase_docs": ("docs/PHASE_326.md",),
            "phase_tests": ("tests/test_phase_326_backbone_pkms_note_fixture_mapping.py",),
            "domain_payload": {
                "fake_vault_path": "C:/FAKE_OBSIDIAN_VAULT_DO_NOT_ACCESS",
                "fake_note_id": "fake-note-0001",
                "fake_note_path": "Areas/Fake Project/Fake Note.md",
                "fake_before_note_content_evidence": "before",
                "fake_after_note_content_evidence": "after",
                "fixture_stage_role": "fixture_readback",
            },
        }
        values.update(overrides)
        return PkmsNoteFixtureBackboneStageMapping(**values)

    def test_missing_fake_vault_path_returns_deterministic_reason(self):
        validation = validate_pkms_note_fixture_backbone_stage_mapping(
            self._mapping(
                domain_payload={
                    "fake_note_path": "Areas/Fake Project/Fake Note.md",
                    "fake_before_note_content_evidence": "before",
                    "fake_after_note_content_evidence": "after",
                }
            )
        )

        self.assertEqual(validation["status"], "incomplete")
        self.assertEqual(validation["reason_code"], "fake_vault_path_missing")

    def test_missing_fake_note_path_or_id_returns_deterministic_reason(self):
        validation = validate_pkms_note_fixture_backbone_stage_mapping(
            self._mapping(
                domain_payload={
                    "fake_vault_path": "C:/FAKE_OBSIDIAN_VAULT_DO_NOT_ACCESS",
                    "fake_before_note_content_evidence": "before",
                    "fake_after_note_content_evidence": "after",
                }
            )
        )

        self.assertEqual(validation["reason_code"], "fake_note_path_missing")

    def test_missing_before_after_content_evidence_returns_deterministic_reason(self):
        validation = validate_pkms_note_fixture_backbone_stage_mapping(
            self._mapping(
                domain_payload={
                    "fake_vault_path": "C:/FAKE_OBSIDIAN_VAULT_DO_NOT_ACCESS",
                    "fake_note_path": "Areas/Fake Project/Fake Note.md",
                }
            )
        )

        self.assertEqual(
            validation["reason_code"],
            "fake_before_after_evidence_missing",
        )

    def test_live_vault_access_and_real_mutation_claims_are_rejected(self):
        mapping = self._mapping().as_dict()

        vault_claim = validate_pkms_note_fixture_backbone_stage_mapping(
            {**mapping, "live_vault_accessed": True}
        )
        obsidian_claim = validate_pkms_note_fixture_backbone_stage_mapping(
            {**mapping, "live_obsidian_vault_accessed": True}
        )
        mutation_claim = validate_pkms_note_fixture_backbone_stage_mapping(
            {**mapping, "live_pkms_note_mutated": True}
        )

        self.assertEqual(
            vault_claim["reason_code"],
            "live_vault_access_claim_rejected",
        )
        self.assertEqual(
            obsidian_claim["reason_code"],
            "live_vault_access_claim_rejected",
        )
        self.assertEqual(
            mutation_claim["reason_code"],
            "live_pkms_mutation_claim_rejected",
        )

    def test_backlink_frontmatter_correctness_claims_are_rejected(self):
        mapping = self._mapping().as_dict()

        backlink_claim = validate_pkms_note_fixture_backbone_stage_mapping(
            {**mapping, "backlink_correctness_claimed": True}
        )
        frontmatter_claim = validate_pkms_note_fixture_backbone_stage_mapping(
            {**mapping, "frontmatter_correctness_claimed": True}
        )
        combined_claim = validate_pkms_note_fixture_backbone_stage_mapping(
            {**mapping, "real_backlink_frontmatter_correctness_claimed": True}
        )

        expected = "backlink_frontmatter_correctness_claim_rejected"
        self.assertEqual(backlink_claim["reason_code"], expected)
        self.assertEqual(frontmatter_claim["reason_code"], expected)
        self.assertEqual(combined_claim["reason_code"], expected)

    def test_smuggled_semantic_production_v0_and_adapter_claims_are_rejected(self):
        mapping = self._mapping().as_dict()

        semantic_claim = validate_pkms_note_fixture_backbone_stage_mapping(
            {**mapping, "semantic_correctness_claimed": True}
        )
        production_claim = validate_pkms_note_fixture_backbone_stage_mapping(
            {**mapping, "production_readiness_claimed": True}
        )
        v0_claim = validate_pkms_note_fixture_backbone_stage_mapping(
            {**mapping, "backbone_v0_declared": True}
        )
        adapter_claim = validate_pkms_note_fixture_backbone_stage_mapping(
            {**mapping, "adapter_executed": True}
        )

        self.assertFalse(PKMS_NOTE_FIXTURE_ADAPTER.execution_allowed)
        self.assertEqual(
            semantic_claim["reason_code"],
            "semantic_correctness_claim_rejected",
        )
        self.assertEqual(
            production_claim["reason_code"],
            "production_readiness_claim_rejected",
        )
        self.assertEqual(v0_claim["reason_code"], "backbone_v0_claim_rejected")
        self.assertEqual(
            adapter_claim["reason_code"],
            "adapter_execution_claim_rejected",
        )

    def test_official_capsule_claim_is_rejected(self):
        validation = validate_pkms_note_fixture_backbone_stage_mapping(
            {**self._mapping().as_dict(), "official_capsule_generated": True}
        )

        self.assertEqual(validation["reason_code"], "official_capsule_claim_rejected")

    def test_pkms_specific_fields_cannot_be_backbone_native(self):
        validation = validate_pkms_note_fixture_backbone_stage_mapping(
            {
                **self._mapping().as_dict(),
                "backbone_native_evidence_fields": [
                    "record_id",
                    "stage_name",
                    "fake_vault_path",
                ],
            }
        )

        self.assertEqual(
            validation["reason_code"],
            "pkms_specific_native_field_rejected",
        )

    def test_mismatched_stage_order_reports_incomplete(self):
        mappings = list(ordered_pkms_note_fixture_backbone_stage_mappings())
        swapped = [mappings[1], mappings[0], *mappings[2:]]

        validation = validate_ordered_pkms_note_fixture_backbone_stage_mappings(swapped)

        self.assertEqual(validation["status"], "incomplete")
        self.assertEqual(validation["reason_code"], "stage_order_mismatch")
        self.assertIn("stage_order_mismatch", validation["incomplete_reason_codes"])

    def test_incomplete_status_preserves_non_proofs_without_v0(self):
        status = read_pkms_note_fixture_backbone_mapping_status(
            [
                self._mapping(
                    domain_payload={
                        "fake_note_path": "Areas/Fake Project/Fake Note.md",
                        "fake_before_note_content_evidence": "before",
                        "fake_after_note_content_evidence": "after",
                    }
                )
            ]
        )

        self.assertFalse(status["complete"])
        self.assertEqual(status["incomplete_mapping_count"], 1)
        self.assertIn("fake_vault_path_missing", status["incomplete_reason_codes"])
        self.assertEqual(tuple(status["non_proofs"]), PKMS_NOTE_FIXTURE_NON_PROOFS)
        self.assertFalse(status["backbone_v0_declared"])
        self.assertFalse(status["live_vault_accessed"])


if __name__ == "__main__":
    unittest.main()
