import unittest

from orchestrator.backbone_pkms_note_fixture_decision_boundary import (
    PKMS_NOTE_FIXTURE_BLOCKED_DECISIONS,
    PKMS_NOTE_FIXTURE_RECOMMENDED_NEXT_BOUNDARY,
    assess_pkms_note_fixture_decision_boundary,
    read_pkms_note_fixture_decision_boundary_status,
)
from orchestrator.backbone_pkms_note_fixture_mapping import (
    PKMS_NOTE_FIXTURE_NON_PROOFS,
    PkmsNoteFixtureBackboneStageMapping,
    ordered_pkms_note_fixture_backbone_stage_mappings,
    read_pkms_note_fixture_backbone_operator_readback,
)


class Phase328BackbonePkmsNoteFixtureReadbackDecisionBoundaryTests(unittest.TestCase):
    def _blocked_decision_map(self):
        assessment = assess_pkms_note_fixture_decision_boundary()
        return {item["decision"]: item for item in assessment["blocked_decisions"]}

    def test_operator_readback_exists_and_is_deterministic(self):
        first = read_pkms_note_fixture_backbone_operator_readback()
        second = read_pkms_note_fixture_backbone_operator_readback()

        self.assertEqual(first, second)
        self.assertTrue(first["pkms_note_fixture_backbone_operator_readback"])

    def test_readback_reports_pkms_context_and_ordered_stages(self):
        readback = read_pkms_note_fixture_backbone_operator_readback()
        expected_stage_names = [
            mapping.stage_name
            for mapping in ordered_pkms_note_fixture_backbone_stage_mappings()
        ]

        self.assertEqual(readback["bounded_context"], "pkms_note_operation_fixture")
        self.assertEqual(readback["mapped_stage_names"], expected_stage_names)
        self.assertEqual(
            readback["mapped_stage_names"],
            readback["expected_backbone_stage_names"],
        )
        self.assertEqual(readback["status_counts"]["incomplete"], 0)

    def test_readback_answers_boundary_questions_false(self):
        readback = read_pkms_note_fixture_backbone_operator_readback()

        self.assertFalse(readback["backbone_v0_declared"])
        self.assertFalse(readback["adapter_execution_allowed"])
        self.assertFalse(readback["adapters_executable_through_mapping"])
        self.assertFalse(readback["live_vault_access_allowed"])
        self.assertFalse(readback["note_mutation_allowed"])
        self.assertFalse(readback["real_backlink_frontmatter_correctness_proven"])

    def test_readback_exposes_fake_reference_only_fixture_evidence(self):
        readback = read_pkms_note_fixture_backbone_operator_readback()
        evidence = readback["fixture_evidence_strings"]

        self.assertTrue(evidence["evidence_is_fake_fixture_only"])
        self.assertTrue(evidence["evidence_is_reference_only"])
        self.assertIn(
            "fixtures/pkms_note_operation/static_note_operation.json",
            evidence["fixture_sources"],
        )
        self.assertIn("docs/PHASE_326.md", evidence["phase_docs"])
        self.assertIn(
            "tests/test_phase_326_backbone_pkms_note_fixture_mapping.py",
            evidence["phase_tests"],
        )

    def test_readback_preserves_native_and_pkms_specific_field_separation(self):
        readback = read_pkms_note_fixture_backbone_operator_readback()

        self.assertIn("record_id", readback["backbone_native_fields"])
        self.assertIn("fake_vault_path", readback["pkms_specific_fields"])
        self.assertNotIn("fake_vault_path", readback["backbone_native_fields"])

    def test_readback_preserves_non_proofs_and_negative_edge_reasons(self):
        readback = read_pkms_note_fixture_backbone_operator_readback()

        self.assertEqual(tuple(readback["non_proofs"]), PKMS_NOTE_FIXTURE_NON_PROOFS)
        self.assertIn(
            "live_vault_access_claim_rejected",
            readback["possible_negative_edge_reason_codes"],
        )
        self.assertIn(
            "backlink_frontmatter_correctness_claim_rejected",
            readback["possible_negative_edge_reason_codes"],
        )
        self.assertFalse(readback["official_capsule_proof_current"])

    def test_incomplete_readback_reports_blocked_conditions_without_v0(self):
        incomplete_mapping = PkmsNoteFixtureBackboneStageMapping(
            stage_name="readback",
            phase_docs=("docs/PHASE_326.md",),
            phase_tests=("tests/test_phase_326_backbone_pkms_note_fixture_mapping.py",),
            domain_payload={
                "fake_note_path": "Areas/Fake Project/Fake Note.md",
                "fake_before_note_content_evidence": "before",
                "fake_after_note_content_evidence": "after",
            },
        )

        readback = read_pkms_note_fixture_backbone_operator_readback(
            [incomplete_mapping]
        )

        self.assertEqual(readback["status_counts"]["incomplete"], 1)
        self.assertIn("fake_vault_path_missing", readback["blocked_conditions"])
        self.assertFalse(readback["backbone_v0_declared"])

    def test_decision_boundary_assessment_exists_and_is_deterministic(self):
        first = assess_pkms_note_fixture_decision_boundary()
        second = read_pkms_note_fixture_decision_boundary_status()

        self.assertEqual(first, second)
        self.assertTrue(first["pkms_note_fixture_decision_boundary"])

    def test_required_blocked_decisions_are_present(self):
        blocked = self._blocked_decision_map()

        for decision in PKMS_NOTE_FIXTURE_BLOCKED_DECISIONS:
            self.assertIn(decision, blocked)
            self.assertEqual(blocked[decision]["status"], "blocked")

    def test_decision_boundary_blocks_v0_live_access_mutation_and_claims(self):
        blocked = self._blocked_decision_map()

        self.assertEqual(
            blocked["declare_backbone_v0"]["reason_code"],
            "backbone_v0_not_declared",
        )
        self.assertEqual(
            blocked["access_live_vault"]["reason_code"],
            "live_vault_access_not_allowed",
        )
        self.assertEqual(
            blocked["mutate_live_pkms_notes"]["reason_code"],
            "live_pkms_mutation_not_allowed",
        )
        self.assertEqual(
            blocked["claim_backlink_frontmatter_correctness"]["reason_code"],
            "backlink_frontmatter_correctness_not_proven",
        )
        self.assertEqual(
            blocked["claim_semantic_correctness"]["reason_code"],
            "semantic_correctness_not_proven",
        )

    def test_decision_boundary_recommends_phase_329_read_only(self):
        assessment = assess_pkms_note_fixture_decision_boundary()

        self.assertEqual(
            assessment["recommended_next_boundary"],
            PKMS_NOTE_FIXTURE_RECOMMENDED_NEXT_BOUNDARY,
        )
        self.assertEqual(
            assessment["recommended_next_boundary"],
            "PHASE329_BACKBONE_MULTI_FIXTURE_CRITERIA_READINESS_ASSESSMENT_READONLY",
        )
        self.assertNotIn("V0_DECLARATION", PKMS_NOTE_FIXTURE_RECOMMENDED_NEXT_BOUNDARY)

    def test_decision_boundary_preserves_expected_non_proofs(self):
        assessment = assess_pkms_note_fixture_decision_boundary()

        self.assertIn(
            "pkms_note_fixture_mapping_does_not_access_live_vaults",
            assessment["non_proofs"],
        )
        self.assertFalse(assessment["backbone_v0_declared"])
        self.assertFalse(assessment["official_capsule_proof_current"])
        self.assertFalse(assessment["provider_model_runtime_platform_execution_claimed"])
        self.assertFalse(assessment["service_api_ui_dashboard_auth_deployment_claimed"])


if __name__ == "__main__":
    unittest.main()
