from __future__ import annotations

import copy
import unittest

from orchestrator.governed_research_historical_record import (
    REQUIRED_NON_PROOFS,
    derive_operational_evidence_diagnostic,
    evaluate_historical_record_packet,
    validate_historical_record_packet,
)


def positive_packet() -> dict:
    sources = []
    categories = [
        "CONTEMPORANEOUS_EVENT", "INDEPENDENT_CONTEMPORANEOUS", "INSTITUTIONAL_INTERPRETATION",
        "OPERATIONAL_CONTINUITY", "SCHOLARLY_TREATMENT", "INSTITUTIONAL_INTERPRETATION",
    ]
    for number, category in enumerate(categories, 1):
        source_id = f"SRC-HR-00{number}"
        source = {
            "source_id": source_id, "source_role": "CORPUS_SOURCE", "source_plan_categories": [category],
            "institution_or_origin": f"institution-{number}", "corpus_status": "RATIFIED", "limitations": ["bounded corpus"],
            "permitted_uses": ["PARAPHRASE"], "quotation_posture": "PARAPHRASE_PREFERRED", "provenance_posture": "LIMITED", "enabled": True,
            "operational_bundle": number in {3, 4, 5},
        }
        if source_id == "SRC-HR-001":
            source.update({"provenance_posture": "SCAN_LEVEL_VERIFICATION_UNAVAILABLE", "quotation_posture": "EXACT_QUOTATION_REQUIRES_UNL_TRANSCRIPTION_ATTRIBUTION"})
        if source_id == "SRC-HR-002":
            source.update({"provenance_posture": "AUTHORITATIVE_SCAN_NOT_VISUALLY_INSPECTED", "quotation_posture": "EXACT_BODY_QUOTATION_NOT_AUTHORIZED"})
        if source_id == "SRC-HR-004":
            source["authority_posture"] = {"peer_reviewed": False, "university_press": False}
        sources.append(source)
    claims = []
    for number in range(1, 10):
        claim_id = f"CLM-HR-00{number}"
        claims.append({
            "claim_id": claim_id, "proposition": f"Caller-supplied bounded claim {number}.",
            "declared_status": "QUALIFIED" if number in {3, 5, 8, 9} else "SUPPORTED",
            "required_relationship_ids": [f"rel-{number}"],
            "inference_posture": "ANALYST_INFERENCE" if number in {8, 9} else "SOURCE_CONTENT",
            "materiality": "MATERIAL", "enabled": True,
        })
    relationship_types = ["SUPPORTS", "SUPPORTS", "QUALIFIES", "METHODOLOGICAL_LIMIT", "QUALIFIES", "SUPPORTS", "SUPPORTS", "QUALIFIES", "CONTEXTUALIZES"]
    relationships = []
    for number, relationship_type in enumerate(relationship_types, 1):
        source_id = f"SRC-HR-00{min(number, 6)}"
        relationships.append({
            "relationship_id": f"rel-{number}",
            "neutral_evidence_link": {"evidence_link_id": f"link-{number}", "subject_reference": {"subject_type": "historical_claim", "subject_id": f"CLM-HR-00{number}"}, "source_reference": source_id, "source_locator": f"claim-{number}"},
            "relationship_type": relationship_type, "source_role": "CORPUS_SOURCE", "use_type": "ANALYTICAL_INFERENCE" if number in {8, 9} else "PARAPHRASE",
            "inference_involved": number in {8, 9}, "limitation": "explicit limitation" if relationship_type in {"QUALIFIES", "METHODOLOGICAL_LIMIT"} else "", "enabled": True,
            "operational_bundle": number in {3, 5, 6, 7, 8, 9},
        })
    return {
        "case_id": "caller-supplied-historical-record", "question": "Bounded historical record question.", "corpus_count": 6,
        "primary_terminal_classification": "QUALIFIED_CONCLUSION", "analytical_recommendation": "Use nearby qualification with the compressed formulation.",
        "human_disposition": {"status": "ACCEPTED_BY_ROGER", "owner": "Roger"}, "non_proofs": sorted(REQUIRED_NON_PROOFS),
        "retired_claim": "CLM-HR-010_RETIRED_AND_RECLASSIFIED_AS_OPERATIONAL_DEFINITION_REQUIREMENT",
        "sources": sources, "claims": claims, "relationships": relationships,
        "endpoint_contexts": {"A": "QUALIFIED_CONCLUSION", "B": "MAY_10_COMPLETION_UNSUPPORTED", "C": "QUALIFIED_CONCLUSION", "D": "MAY_10_PROPOSITION_CONTRADICTED"},
    }


class GovernedResearchHistoricalRecordTests(unittest.TestCase):
    def test_positive_packet_validates_and_evaluates_as_qualified(self):
        result = evaluate_historical_record_packet(positive_packet())
        self.assertEqual("ready", result["evaluation_status"])
        self.assertEqual("QUALIFIED_CONCLUSION", result["primary_terminal_classification"])
        self.assertEqual(6, result["result"]["corpus_count"])
        self.assertTrue(result["result"]["source_plan_valid"])
        self.assertEqual("QUALIFIED", result["result"]["claim_states"]["CLM-HR-003"])

    def test_ids_non_corpus_and_endpoint_contexts_are_preserved(self):
        packet = positive_packet()
        packet["sources"].append({"source_id": "NON-CORPUS-1", "source_role": "CONTEXTUAL_SOURCE", "source_plan_categories": [], "institution_or_origin": "context", "corpus_status": "NON_CORPUS", "limitations": [], "permitted_uses": [], "quotation_posture": "NONE", "provenance_posture": "NONE", "enabled": True})
        result = evaluate_historical_record_packet(packet)
        self.assertEqual(6, result["result"]["corpus_count"])
        self.assertEqual("QUALIFIED_CONCLUSION", result["result"]["endpoint_contexts"]["A"])
        self.assertEqual("MAY_10_PROPOSITION_CONTRADICTED", result["result"]["endpoint_contexts"]["D"])

    def test_invalid_relationship_and_references_fail(self):
        packet = positive_packet()
        packet["relationships"][0]["relationship_type"] = "UNSCOPED"
        packet["relationships"][1]["neutral_evidence_link"]["source_reference"] = "missing"
        packet["relationships"][2]["neutral_evidence_link"]["subject_reference"]["subject_id"] = "missing"
        errors = validate_historical_record_packet(packet)["errors"]
        self.assertIn("relationship_type_invalid:rel-1", errors)
        self.assertIn("relationship_source_reference_missing:rel-2", errors)
        self.assertIn("relationship_claim_reference_missing:rel-3", errors)

    def test_duplicate_ids_and_neutral_link_validation_fail(self):
        packet = positive_packet()
        packet["sources"][1]["source_id"] = "SRC-HR-001"
        packet["relationships"][0]["neutral_evidence_link"]["evidence_link_id"] = ""
        errors = validate_historical_record_packet(packet)["errors"]
        self.assertIn("source_ids_must_be_unique", errors)
        self.assertIn("neutral_link_invalid:rel-1:evidence_link_id_required", errors)

    def test_source_specific_quotation_and_authority_controls_fail_when_inflated(self):
        packet = positive_packet()
        packet["relationships"][0].update({"use_type": "EXACT_QUOTATION_WITH_UNL_TRANSCRIPTION_ATTRIBUTION", "quotation_attribution": "missing"})
        packet["relationships"][1]["use_type"] = "EXACT_QUOTATION_WITH_UNL_TRANSCRIPTION_ATTRIBUTION"
        packet["sources"][3]["authority_posture"] = {"peer_reviewed": True, "university_press": True}
        errors = validate_historical_record_packet(packet)["errors"]
        self.assertIn("src_hr_001_exact_quote_requires_unl_attribution:rel-1", errors)
        self.assertIn("src_hr_002_exact_body_quotation_not_authorized:rel-2", errors)
        self.assertIn("src_hr_004_peer_reviewed_must_be_false", errors)
        self.assertIn("src_hr_004_university_press_must_be_false", errors)

    def test_disposition_case_id_and_positive_input_are_not_result_controls(self):
        packet = positive_packet()
        changed = copy.deepcopy(packet)
        changed["case_id"] = "another-caller-supplied-case"
        changed["human_disposition"] = {"status": "REJECTED", "owner": "someone else"}
        self.assertEqual(
            evaluate_historical_record_packet(packet)["primary_terminal_classification"],
            evaluate_historical_record_packet(changed)["primary_terminal_classification"],
        )

    def test_diagnostic_is_derived_immutable_and_blocks_operational_claims(self):
        packet = positive_packet()
        original = copy.deepcopy(packet)
        diagnostic = derive_operational_evidence_diagnostic(packet)
        result = evaluate_historical_record_packet(diagnostic)
        self.assertEqual(original, packet)
        self.assertEqual("INSUFFICIENT_EVIDENCE", result["primary_terminal_classification"])
        self.assertEqual("EXPLICIT_GAP", result["result"]["source_plan"]["OPERATIONAL_CONTINUITY"])
        self.assertEqual("BLOCKED_OR_DOWNGRADED", result["result"]["material_operational_claims"])
        self.assertEqual("INSUFFICIENT", result["result"]["claim_states"]["CLM-HR-003"])

    def test_inference_and_non_proofs_remain_explicit(self):
        result = evaluate_historical_record_packet(positive_packet())["result"]
        self.assertTrue(result["inference_remains_explicit"])
        self.assertTrue(REQUIRED_NON_PROOFS.issubset(set(result["non_proofs"])))


if __name__ == "__main__":
    unittest.main()
