import unittest

from orchestrator.dossier_case_mapping import (
    NO_FIRST_PRODUCT_WEDGE_SELECTED,
    NON_PROOF_POSTURE,
    adapt_case_packet_to_dossier_case,
    get_dossier_case_field_map,
    get_dossier_case_field_mappings,
)


class DossierCaseMappingTests(unittest.TestCase):
    def _minimal_case_packet(self) -> dict:
        return {
            "case_id": "neutral_mapping_case",
            "case_type": "general_casework",
            "title": "Neutral mapping case",
            "objective": "Represent existing case-packet fields in neutral dossier language.",
            "source_materials": ["source-a.md"],
            "extracted_facts": [{"fact": "source field is present", "source": "source-a.md"}],
            "timeline_events": ["first event"],
            "open_issues": ["unresolved question"],
            "missing_evidence": ["missing source"],
            "contradictions": ["conflicting source statements"],
            "drafts": ["draft output"],
            "decisions": [{"decision": "operator reviewed mapping"}],
            "status": "in_review",
            "next_step": "inspect neutral adapter",
        }

    def test_mapping_exposes_required_neutral_fields(self):
        field_map = get_dossier_case_field_map()
        required = {
            "objective",
            "source_materials",
            "extracted_facts",
            "chronology",
            "open_questions",
            "missing_evidence",
            "missing_canon",
            "contradictions",
            "drafts",
            "decisions",
            "next_work_items",
            "review_posture",
            "operator_approvals",
            "status",
        }

        self.assertTrue(required.issubset(set(field_map)))

    def test_mapping_points_to_existing_case_packet_compatible_fields(self):
        allowed_case_packet_fields = {
            "case_id",
            "case_type",
            "title",
            "objective",
            "status",
            "next_step",
            "counterparties",
            "source_materials",
            "extracted_facts",
            "timeline_events",
            "open_issues",
            "missing_evidence",
            "contradictions",
            "drafts",
            "decisions",
        }

        for mapping in get_dossier_case_field_mappings():
            self.assertTrue(mapping.case_packet_fields)
            self.assertTrue(set(mapping.case_packet_fields).issubset(allowed_case_packet_fields))

    def test_mapping_preserves_missing_evidence_and_contradictions(self):
        field_map = get_dossier_case_field_map()

        self.assertEqual(field_map["missing_evidence"], ("missing_evidence",))
        self.assertEqual(field_map["missing_canon"], ("missing_evidence",))
        self.assertEqual(field_map["contradictions"], ("contradictions",))

    def test_mapping_does_not_select_first_product_wedge(self):
        view = adapt_case_packet_to_dossier_case(self._minimal_case_packet())

        self.assertEqual(view["product_wedge_selection"], NO_FIRST_PRODUCT_WEDGE_SELECTED)
        self.assertFalse(view["non_proof_posture"]["first_product_wedge_selection"])

    def test_mapping_is_domain_neutral(self):
        domain_terms = {
            "claims",
            "disputes",
            "appeals",
            "game",
            "worldbuilding",
            "design",
        }
        surface_text = " ".join(
            [mapping.neutral_field for mapping in get_dossier_case_field_mappings()]
            + [field for mapping in get_dossier_case_field_mappings() for field in mapping.case_packet_fields]
        )

        for term in domain_terms:
            self.assertNotIn(term, surface_text)

    def test_adapter_extracts_neutral_fields_from_minimal_case_packet(self):
        view = adapt_case_packet_to_dossier_case(self._minimal_case_packet())

        self.assertEqual(
            view["objective"],
            "Represent existing case-packet fields in neutral dossier language.",
        )
        self.assertEqual(view["source_materials"], ["source-a.md"])
        self.assertEqual(view["chronology"], ["first event"])
        self.assertEqual(view["open_questions"], ["unresolved question"])
        self.assertEqual(view["missing_evidence"], ["missing source"])
        self.assertEqual(view["missing_canon"], ["missing source"])
        self.assertEqual(view["contradictions"], ["conflicting source statements"])
        self.assertEqual(view["next_work_items"], ["inspect neutral adapter"])
        self.assertEqual(view["review_posture"], {"status": "in_review", "next_step": "inspect neutral adapter"})
        self.assertEqual(view["operator_approvals"], [{"decision": "operator reviewed mapping"}])

    def test_non_proof_posture_is_exported(self):
        self.assertFalse(NON_PROOF_POSTURE["runtime_proof"])
        self.assertFalse(NON_PROOF_POSTURE["provider_model_proof"])
        self.assertFalse(NON_PROOF_POSTURE["semantic_correctness_proof"])
        self.assertFalse(NON_PROOF_POSTURE["production_readiness_proof"])
        self.assertFalse(NON_PROOF_POSTURE["phase_387_implementation"])


if __name__ == "__main__":
    unittest.main()
