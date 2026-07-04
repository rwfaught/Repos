import unittest

from orchestrator.dossier_case_mapping_readback import (
    REQUIRED_NEUTRAL_FIELDS,
    build_dossier_case_mapping_readback,
    build_dossier_case_mapping_readback_dict,
)


class DossierCaseMappingReadbackTests(unittest.TestCase):
    def _minimal_case_packet(self) -> dict:
        return {
            "case_id": "readback_case",
            "case_type": "general_casework",
            "title": "Readback case",
            "objective": "Inspect the neutral mapping readback.",
            "source_materials": ["source.md"],
            "extracted_facts": ["fact from source"],
            "timeline_events": ["event one"],
            "open_issues": ["question one"],
            "missing_evidence": ["missing source"],
            "contradictions": ["conflicting source"],
            "drafts": ["draft one"],
            "decisions": ["operator reviewed"],
            "status": "in_review",
            "next_step": "review readback",
        }

    def test_readback_includes_all_required_neutral_fields(self):
        readback = build_dossier_case_mapping_readback()

        self.assertEqual(readback.missing_required_neutral_fields, ())
        for field in REQUIRED_NEUTRAL_FIELDS:
            self.assertIn(field, readback.neutral_fields)
            self.assertTrue(readback.required_field_coverage[field])

    def test_readback_exposes_mapping_to_case_packet_fields(self):
        readback = build_dossier_case_mapping_readback()

        self.assertEqual(readback.neutral_to_case_packet_mapping["objective"], ("objective",))
        self.assertEqual(readback.neutral_to_case_packet_mapping["chronology"], ("timeline_events",))
        self.assertEqual(readback.neutral_to_case_packet_mapping["open_questions"], ("open_issues",))
        self.assertEqual(readback.neutral_to_case_packet_mapping["review_posture"], ("status", "next_step"))

    def test_readback_preserves_missing_evidence_and_contradictions(self):
        readback = build_dossier_case_mapping_readback()

        self.assertTrue(readback.preserved_concepts["missing_evidence"])
        self.assertTrue(readback.preserved_concepts["missing_canon"])
        self.assertTrue(readback.preserved_concepts["contradictions"])
        self.assertEqual(readback.neutral_to_case_packet_mapping["missing_evidence"], ("missing_evidence",))
        self.assertEqual(readback.neutral_to_case_packet_mapping["contradictions"], ("contradictions",))

    def test_readback_says_no_first_product_wedge_is_selected(self):
        readback = build_dossier_case_mapping_readback()

        self.assertFalse(readback.first_product_wedge_selected)
        self.assertEqual(readback.product_wedge_selection, "no_first_product_wedge_selected")

    def test_readback_says_phase_387_is_not_implemented(self):
        readback = build_dossier_case_mapping_readback()

        self.assertFalse(readback.phase_387_implemented)

    def test_readback_preserves_explicit_non_proofs(self):
        readback = build_dossier_case_mapping_readback()
        non_proofs = set(readback.non_proofs)

        self.assertIn("no runtime proof", non_proofs)
        self.assertIn("no provider/model proof", non_proofs)
        self.assertIn("no semantic correctness proof", non_proofs)
        self.assertIn("no production readiness proof", non_proofs)
        self.assertIn("no first product wedge selection", non_proofs)
        self.assertIn("no product-domain implementation", non_proofs)

    def test_readback_is_domain_neutral(self):
        readback = build_dossier_case_mapping_readback()

        self.assertTrue(readback.domain_neutral)
        self.assertEqual(readback.domain_specific_terms_required, ())

    def test_readback_accepts_minimal_dictionary_fixture(self):
        readback = build_dossier_case_mapping_readback(self._minimal_case_packet())

        self.assertIsNotNone(readback.adapted_packet_readback)
        self.assertEqual(readback.adapted_packet_readback["objective"], "Inspect the neutral mapping readback.")
        self.assertEqual(readback.adapted_packet_readback["chronology"], ["event one"])
        self.assertEqual(readback.adapted_packet_readback["open_questions"], ["question one"])
        self.assertEqual(readback.adapted_packet_readback["missing_evidence"], ["missing source"])
        self.assertEqual(readback.adapted_packet_readback["contradictions"], ["conflicting source"])
        self.assertFalse(readback.adapted_packet_readback["non_proof_posture"]["first_product_wedge_selection"])

    def test_readback_dict_is_plain_data(self):
        payload = build_dossier_case_mapping_readback_dict(self._minimal_case_packet())

        self.assertEqual(payload["readback_name"], "dossier_case_mapping_readback")
        self.assertEqual(payload["boundary"], "DOSSIER_CASE_MAPPING_READBACK_SOURCE_TEST_DOCS")
        self.assertIsInstance(payload["neutral_fields"], list)
        self.assertIsInstance(payload["neutral_to_case_packet_mapping"]["chronology"], list)


if __name__ == "__main__":
    unittest.main()
