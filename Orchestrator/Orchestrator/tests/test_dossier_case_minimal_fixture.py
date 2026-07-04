import unittest

from orchestrator.dossier_case_mapping_readback import REQUIRED_NEUTRAL_FIELDS
from orchestrator.dossier_case_minimal_fixture import (
    ADMIN_CASE_SHAPE,
    BOUNDARY,
    CREATIVE_DOSSIER_SHAPE,
    build_admin_case_minimal_fixture,
    build_admin_case_shape_packet,
    build_creative_dossier_minimal_fixture,
    build_creative_dossier_shape_packet,
    build_minimal_fixture_readback_dicts,
    build_minimal_fixture_readbacks,
)


class DossierCaseMinimalFixtureTests(unittest.TestCase):
    def test_both_fixtures_are_available(self):
        fixtures = build_minimal_fixture_readbacks()

        self.assertEqual(len(fixtures), 2)
        self.assertEqual(fixtures[0].fixture_name, ADMIN_CASE_SHAPE)
        self.assertEqual(fixtures[1].fixture_name, CREATIVE_DOSSIER_SHAPE)
        self.assertEqual(fixtures[0].boundary, BOUNDARY)
        self.assertEqual(fixtures[1].boundary, BOUNDARY)

    def test_both_fixture_packets_contain_required_case_packet_fields(self):
        required_case_fields = {
            "case_id",
            "case_type",
            "title",
            "objective",
            "source_materials",
            "extracted_facts",
            "timeline_events",
            "open_issues",
            "missing_evidence",
            "contradictions",
            "drafts",
            "decisions",
            "status",
            "next_step",
        }

        self.assertTrue(required_case_fields.issubset(build_admin_case_shape_packet()))
        self.assertTrue(required_case_fields.issubset(build_creative_dossier_shape_packet()))

    def test_both_fixtures_cover_required_neutral_fields(self):
        for fixture in build_minimal_fixture_readbacks():
            self.assertEqual(set(fixture.required_neutral_field_coverage), set(REQUIRED_NEUTRAL_FIELDS))
            for field in REQUIRED_NEUTRAL_FIELDS:
                self.assertTrue(fixture.required_neutral_field_coverage[field])
                self.assertIn(field, fixture.adapted_dossier_case)

    def test_both_fixtures_pass_through_existing_mapping_adapter(self):
        admin = build_admin_case_minimal_fixture()
        creative = build_creative_dossier_minimal_fixture()

        self.assertEqual(admin.adapted_dossier_case["objective"], admin.case_packet["objective"])
        self.assertEqual(admin.adapted_dossier_case["chronology"], admin.case_packet["timeline_events"])
        self.assertEqual(admin.adapted_dossier_case["open_questions"], admin.case_packet["open_issues"])
        self.assertEqual(creative.adapted_dossier_case["objective"], creative.case_packet["objective"])
        self.assertEqual(creative.adapted_dossier_case["chronology"], creative.case_packet["timeline_events"])
        self.assertEqual(creative.adapted_dossier_case["open_questions"], creative.case_packet["open_issues"])

    def test_both_fixtures_are_represented_by_readback_seam(self):
        for fixture in build_minimal_fixture_readbacks():
            self.assertEqual(fixture.readback["readback_name"], "dossier_case_mapping_readback")
            self.assertEqual(
                fixture.readback["recommended_next_boundary"],
                "DOSSIER_CASE_MINIMAL_FIXTURE_SOURCE_TEST_DOCS",
            )
            self.assertIsNotNone(fixture.readback["adapted_packet_readback"])
            self.assertEqual(
                fixture.readback["adapted_packet_readback"]["objective"],
                fixture.case_packet["objective"],
            )

    def test_both_fixtures_preserve_missing_evidence_and_missing_canon(self):
        for fixture in build_minimal_fixture_readbacks():
            self.assertTrue(fixture.preserved_concepts["missing_evidence"])
            self.assertTrue(fixture.preserved_concepts["missing_canon"])
            self.assertEqual(
                fixture.adapted_dossier_case["missing_canon"],
                fixture.adapted_dossier_case["missing_evidence"],
            )

    def test_both_fixtures_preserve_contradictions(self):
        for fixture in build_minimal_fixture_readbacks():
            self.assertTrue(fixture.preserved_concepts["contradictions"])
            self.assertEqual(
                fixture.adapted_dossier_case["contradictions"],
                fixture.case_packet["contradictions"],
            )

    def test_both_fixtures_preserve_no_first_product_wedge_selected(self):
        for fixture in build_minimal_fixture_readbacks():
            self.assertFalse(fixture.first_product_wedge_selected)
            self.assertEqual(fixture.product_wedge_selection, "no_first_product_wedge_selected")
            self.assertEqual(
                fixture.adapted_dossier_case["product_wedge_selection"],
                "no_first_product_wedge_selected",
            )
            self.assertFalse(
                fixture.adapted_dossier_case["non_proof_posture"]["first_product_wedge_selection"]
            )

    def test_both_fixtures_preserve_phase_387_non_implementation(self):
        for fixture in build_minimal_fixture_readbacks():
            self.assertFalse(fixture.phase_387_implemented)
            self.assertFalse(fixture.readback["phase_387_implemented"])
            self.assertIn("no Phase 387 implementation", fixture.non_proofs)

    def test_both_fixtures_are_structural_examples_not_product_implementations(self):
        for fixture in build_minimal_fixture_readbacks():
            self.assertTrue(fixture.structural_example_only)
            self.assertFalse(fixture.domain_specific_workflow_implemented)
            self.assertFalse(fixture.product_implementation)
            self.assertIn("no claims/disputes/appeals product implementation", fixture.non_proofs)
            self.assertIn("no game/worldbuilding/design product implementation", fixture.non_proofs)

    def test_no_fixture_requires_runtime_provider_or_model_execution(self):
        for fixture in build_minimal_fixture_readbacks():
            self.assertFalse(fixture.runtime_provider_model_execution_required)
            self.assertIn("no runtime proof", fixture.non_proofs)
            self.assertIn("no provider/model proof", fixture.non_proofs)

    def test_fixture_readback_dicts_are_plain_data(self):
        payloads = build_minimal_fixture_readback_dicts()

        self.assertEqual(len(payloads), 2)
        self.assertIsInstance(payloads[0]["case_packet"], dict)
        self.assertIsInstance(payloads[0]["adapted_dossier_case"], dict)
        self.assertIsInstance(payloads[0]["readback"], dict)
        self.assertIsInstance(payloads[0]["non_proofs"], list)


if __name__ == "__main__":
    unittest.main()
