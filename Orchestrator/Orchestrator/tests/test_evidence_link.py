import copy
import unittest

from orchestrator.evidence_link import (
    BOUNDARY,
    NON_PROOFS,
    NeutralEvidenceLink,
    build_neutral_evidence_link,
    build_neutral_evidence_link_readback,
    normalize_evidence_link,
    validate_evidence_link,
)


class NeutralEvidenceLinkTests(unittest.TestCase):
    def _link(self, **overrides):
        payload = {
            "evidence_link_id": "evidence_link_001",
            "subject_reference": {
                "subject_type": "fact",
                "subject_id": "fact_001",
            },
            "source_reference": "source_note_001",
            "source_locator": "section: findings",
        }
        payload.update(overrides)
        return payload

    def test_valid_link_builds_typed_record(self):
        link = build_neutral_evidence_link(self._link())

        self.assertIsInstance(link, NeutralEvidenceLink)
        self.assertEqual(link.evidence_link_id, "evidence_link_001")
        self.assertEqual(link.subject_reference.subject_type, "fact")
        self.assertEqual(link.subject_reference.subject_id, "fact_001")
        self.assertEqual(link.source_reference, "source_note_001")
        self.assertEqual(link.source_locator, "section: findings")

    def test_serialization_is_stable_and_normalized(self):
        payload = self._link(
            evidence_link_id=" evidence_link_001 ",
            subject_reference={"subject_type": " fact ", "subject_id": " fact_001 "},
            source_reference=" source_note_001 ",
            source_locator=" section: findings ",
        )

        first = build_neutral_evidence_link(payload).to_dict()
        second = build_neutral_evidence_link(payload).to_dict()

        self.assertEqual(first, second)
        self.assertEqual(first["evidence_link_id"], "evidence_link_001")
        self.assertEqual(first["subject_reference"], {"subject_type": "fact", "subject_id": "fact_001"})

    def test_fact_like_subject_reference_is_valid(self):
        result = validate_evidence_link(self._link())

        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_non_fact_subject_reference_is_valid(self):
        result = validate_evidence_link(
            self._link(
                subject_reference={
                    "subject_type": "recommendation",
                    "subject_id": "recommendation_001",
                }
            )
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["normalized_evidence_link"]["subject_reference"]["subject_type"], "recommendation")

    def test_multiple_links_can_reference_one_subject(self):
        first = build_neutral_evidence_link(self._link(source_reference="source_a"))
        second = build_neutral_evidence_link(
            self._link(evidence_link_id="evidence_link_002", source_reference="source_b")
        )

        self.assertEqual(first.subject_reference, second.subject_reference)
        self.assertNotEqual(first.source_reference, second.source_reference)

    def test_one_source_can_reference_multiple_subjects(self):
        first = build_neutral_evidence_link(self._link())
        second = build_neutral_evidence_link(
            self._link(
                evidence_link_id="evidence_link_002",
                subject_reference={"subject_type": "chronology_item", "subject_id": "event_001"},
            )
        )

        self.assertEqual(first.source_reference, second.source_reference)
        self.assertNotEqual(first.subject_reference, second.subject_reference)

    def test_locator_is_optional(self):
        link = build_neutral_evidence_link(self._link(source_locator=None))

        self.assertIsNone(link.source_locator)
        self.assertTrue(validate_evidence_link(self._link(source_locator=None))["valid"])

    def test_missing_identity_is_rejected(self):
        result = validate_evidence_link(self._link(evidence_link_id=""))

        self.assertFalse(result["valid"])
        self.assertIn("evidence_link_id_required", result["errors"])

    def test_missing_subject_reference_is_rejected(self):
        result = validate_evidence_link(self._link(subject_reference={}))

        self.assertFalse(result["valid"])
        self.assertIn("subject_reference_subject_type_required", result["errors"])
        self.assertIn("subject_reference_subject_id_required", result["errors"])

    def test_missing_source_reference_is_rejected(self):
        result = validate_evidence_link(self._link(source_reference=""))

        self.assertFalse(result["valid"])
        self.assertIn("source_reference_required", result["errors"])

    def test_malformed_reference_shapes_are_rejected(self):
        malformed_subject = validate_evidence_link(self._link(subject_reference=["fact", "fact_001"]))
        malformed_type = validate_evidence_link(
            self._link(subject_reference={"subject_type": "fact-type", "subject_id": "fact_001"})
        )
        malformed_locator = validate_evidence_link(self._link(source_locator={"page": 1}))

        self.assertIn("subject_reference_must_be_mapping", malformed_subject["errors"])
        self.assertIn("subject_reference_subject_type_invalid", malformed_type["errors"])
        self.assertIn("source_locator_must_be_string_or_null", malformed_locator["errors"])

    def test_normalization_does_not_mutate_caller_mapping(self):
        payload = self._link()
        original = copy.deepcopy(payload)

        normalized = normalize_evidence_link(payload)

        self.assertEqual(payload, original)
        self.assertIsNot(normalized["subject_reference"], payload["subject_reference"])

    def test_readback_preserves_explicit_non_proof_posture(self):
        readback = build_neutral_evidence_link_readback(self._link())

        self.assertTrue(readback["evidence_link_contract"])
        self.assertEqual(readback["boundary"], BOUNDARY)
        self.assertTrue(readback["association_recorded"])
        self.assertEqual(readback["validation_errors"], [])
        self.assertEqual(readback["non_proofs"], list(NON_PROOFS))
        self.assertIn("asserts an association", readback["association_statement"])


if __name__ == "__main__":
    unittest.main()
