from copy import deepcopy
import unittest

from orchestrator.case_packet import apply_case_packet_entry_preservation_operation


def packet(**overrides):
    candidate = {
        "case_id": "dossier-producer-1",
        "case_type": "neutral_dossier_case",
        "title": "Entry preservation producer fixture",
        "objective": "Preserve caller-declared source and fact entries.",
        "status": "structural_example_only",
        "next_step": "review explicit entry transitions",
    }
    candidate.update(overrides)
    return candidate


def operation(**overrides):
    candidate = {
        "case_id": "dossier-producer-1",
        "entry_kind": "source_material",
        "operation": "create",
        "entry_id": "source-1",
        "payload": {"label": "intake note"},
    }
    candidate.update(overrides)
    if candidate["operation"] in ("preserve", "retire") and "payload" not in overrides:
        candidate.pop("payload")
    return candidate


class CasePacketEntryPreservationProducerTests(unittest.TestCase):
    def test_source_material_create_preserve_edit_replace_and_retire_use_explicit_identity(self):
        created = apply_case_packet_entry_preservation_operation(packet(), operation())
        self.assertEqual(
            [{"entry_id": "source-1", "value": {"label": "intake note"}}],
            created["case_packet"]["source_materials"],
        )
        self.assertEqual("created", created["readback"]["transition"])

        preserved = apply_case_packet_entry_preservation_operation(
            created["case_packet"], operation(operation="preserve")
        )
        self.assertEqual(created["case_packet"]["source_materials"], preserved["case_packet"]["source_materials"])
        self.assertEqual("source-1", preserved["readback"]["resulting_entry_id"])

        edited = apply_case_packet_entry_preservation_operation(
            preserved["case_packet"],
            operation(operation="edit", payload={"label": "corrected intake note"}),
        )
        self.assertEqual("source-1", edited["case_packet"]["source_materials"][0]["entry_id"])
        self.assertEqual({"label": "corrected intake note"}, edited["case_packet"]["source_materials"][0]["value"])

        replaced = apply_case_packet_entry_preservation_operation(
            edited["case_packet"],
            operation(
                operation="replace",
                replacement_entry_id="source-2",
                payload={"label": "replacement intake note"},
            ),
        )
        self.assertEqual("source-1", replaced["readback"]["prior_entry_id"])
        self.assertEqual("source-2", replaced["readback"]["resulting_entry_id"])
        self.assertEqual("source-2", replaced["case_packet"]["source_materials"][0]["entry_id"])

        retired = apply_case_packet_entry_preservation_operation(
            replaced["case_packet"], operation(operation="retire", entry_id="source-2")
        )
        self.assertEqual([], retired["case_packet"]["source_materials"])
        self.assertEqual("retired", retired["readback"]["transition"])

    def test_extracted_fact_operations_target_only_the_matching_case_packet_field(self):
        source_packet = packet(source_materials=["legacy source"])
        result = apply_case_packet_entry_preservation_operation(
            source_packet,
            operation(
                entry_kind="extracted_fact",
                entry_id="fact-1",
                payload={"claim": "one source is available"},
            ),
        )
        self.assertEqual(["legacy source"], result["case_packet"]["source_materials"])
        self.assertEqual(
            [{"entry_id": "fact-1", "value": {"claim": "one source is available"}}],
            result["case_packet"]["extracted_facts"],
        )

    def test_rejects_duplicate_mismatched_and_missing_transitions(self):
        existing = packet(source_materials=[{"entry_id": "source-1", "value": "existing"}])
        with self.assertRaisesRegex(ValueError, "already exists"):
            apply_case_packet_entry_preservation_operation(existing, operation())
        with self.assertRaisesRegex(ValueError, "does not match"):
            apply_case_packet_entry_preservation_operation(
                existing, operation(case_id="another-case")
            )
        with self.assertRaisesRegex(ValueError, "not found"):
            apply_case_packet_entry_preservation_operation(packet(), operation(operation="preserve"))

    def test_anonymous_legacy_values_are_never_semantically_matched_or_assigned_an_identity(self):
        existing = packet(source_materials=[{"value": "same text"}, "same text"])
        before = deepcopy(existing)
        created = apply_case_packet_entry_preservation_operation(existing, operation(entry_id="source-1"))
        self.assertEqual(before, existing)
        self.assertEqual(before["source_materials"], created["case_packet"]["source_materials"][:2])
        with self.assertRaisesRegex(ValueError, "not found"):
            apply_case_packet_entry_preservation_operation(
                existing, operation(operation="preserve", entry_id="same text")
            )

    def test_results_are_deterministic_and_copy_safe(self):
        existing = packet(extracted_facts=[{"entry_id": "fact-1", "value": {"claim": "old"}}])
        update = operation(
            entry_kind="extracted_fact",
            operation="edit",
            entry_id="fact-1",
            payload={"claim": "corrected"},
        )
        first = apply_case_packet_entry_preservation_operation(existing, update)
        second = apply_case_packet_entry_preservation_operation(existing, update)
        self.assertEqual(first, second)
        self.assertIsNot(first["case_packet"], second["case_packet"])
        self.assertEqual({"claim": "old"}, existing["extracted_facts"][0]["value"])


if __name__ == "__main__":
    unittest.main()
