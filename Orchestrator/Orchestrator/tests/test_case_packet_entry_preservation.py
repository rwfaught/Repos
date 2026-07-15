from copy import deepcopy
import unittest

from orchestrator.case_packet_entry_preservation import (
    NON_PROOF_STATEMENTS,
    apply_case_scoped_entry_operation,
    normalize_case_scoped_entry_operation,
    serialize_case_scoped_entry_preservation_result,
)


def operation(**overrides):
    candidate = {
        "case_id": "case-preservation-1",
        "entry_kind": "source_material",
        "operation": "create",
        "entry_id": "source-1",
        "payload": {"label": "invoice"},
    }
    candidate.update(overrides)
    if candidate["operation"] in ("preserve", "retire") and "payload" not in overrides:
        candidate.pop("payload")
    return candidate


def identified(entry_id="source-1", value=None):
    return {"entry_id": entry_id, "value": value if value is not None else {"label": "invoice"}}


class CasePacketEntryPreservationTests(unittest.TestCase):
    def test_case_id_validation_uses_case_packet_rules(self):
        for case_id in ("", "   ", "../outside", "case id"):
            with self.subTest(case_id=case_id), self.assertRaises(ValueError):
                normalize_case_scoped_entry_operation(operation(case_id=case_id))

    def test_unsupported_kind_and_operation_are_rejected(self):
        for field, value in (("entry_kind", "draft"), ("operation", "merge")):
            with self.subTest(field=field), self.assertRaises(ValueError):
                normalize_case_scoped_entry_operation(operation(**{field: value}))

    def test_blank_entry_id_is_rejected(self):
        for entry_id in ("", "  ", None):
            with self.subTest(entry_id=entry_id), self.assertRaises(ValueError):
                normalize_case_scoped_entry_operation(operation(entry_id=entry_id))

    def test_normalization_and_serialization_are_deterministic(self):
        normalized = normalize_case_scoped_entry_operation(
            operation(case_id=" case-1 ", entry_id=" source-1 ")
        )
        self.assertEqual("case-1", normalized["case_id"])
        self.assertEqual("source-1", normalized["entry_id"])
        result = apply_case_scoped_entry_operation([], normalized)
        serialized = serialize_case_scoped_entry_preservation_result(result)
        self.assertEqual(serialized, serialize_case_scoped_entry_preservation_result(result))
        self.assertIsNot(serialized, result)

    def test_create_supports_source_material_and_extracted_fact(self):
        source_result = apply_case_scoped_entry_operation([], operation())
        fact_result = apply_case_scoped_entry_operation(
            [], operation(entry_kind="extracted_fact", entry_id="fact-1", payload={"claim": "amount due"})
        )
        self.assertEqual([identified()], source_result["entries"])
        self.assertEqual([identified("fact-1", {"claim": "amount due"})], fact_result["entries"])
        with self.assertRaisesRegex(ValueError, "already exists"):
            apply_case_scoped_entry_operation([identified()], operation())
        with self.assertRaisesRegex(ValueError, "payload is required"):
            apply_case_scoped_entry_operation([], operation(payload=None))

    def test_preserve_retains_exact_entry_and_rejects_missing_or_payload_replacement(self):
        entries = [identified(), "legacy source"]
        result = apply_case_scoped_entry_operation(entries, operation(operation="preserve"))
        self.assertEqual(entries, result["entries"])
        self.assertTrue(result["readback"]["caller_declared_continuity"])
        with self.assertRaisesRegex(ValueError, "not found"):
            apply_case_scoped_entry_operation([], operation(operation="preserve"))
        with self.assertRaisesRegex(ValueError, "not allowed"):
            apply_case_scoped_entry_operation(entries, operation(operation="preserve", payload="replacement"))

    def test_edit_preserves_identity_but_makes_only_caller_declared_continuity_claim(self):
        result = apply_case_scoped_entry_operation(
            [identified()], operation(operation="edit", payload={"label": "corrected invoice"})
        )
        self.assertEqual([identified("source-1", {"label": "corrected invoice"})], result["entries"])
        self.assertTrue(result["readback"]["caller_declared_continuity"])
        with self.assertRaisesRegex(ValueError, "not found"):
            apply_case_scoped_entry_operation([], operation(operation="edit"))
        with self.assertRaisesRegex(ValueError, "payload is required"):
            apply_case_scoped_entry_operation([identified()], operation(operation="edit", payload=None))

    def test_replace_uses_distinct_new_id_and_exposes_both_ids(self):
        result = apply_case_scoped_entry_operation(
            [identified(), identified("source-2")],
            operation(operation="replace", replacement_entry_id="source-3", payload={"label": "new invoice"}),
        )
        self.assertEqual(
            [identified("source-3", {"label": "new invoice"}), identified("source-2")],
            result["entries"],
        )
        self.assertEqual("source-1", result["readback"]["prior_entry_id"])
        self.assertEqual("source-3", result["readback"]["resulting_entry_id"])
        for invalid in (
            operation(operation="replace", replacement_entry_id="source-1"),
            operation(operation="replace", replacement_entry_id="source-2"),
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                apply_case_scoped_entry_operation([identified(), identified("source-2")], invalid)
        with self.assertRaisesRegex(ValueError, "not found"):
            apply_case_scoped_entry_operation([], operation(operation="replace", replacement_entry_id="source-3"))

    def test_retire_removes_target_without_hidden_archive_and_exposes_id(self):
        result = apply_case_scoped_entry_operation([identified(), "anonymous"], operation(operation="retire"))
        self.assertEqual(["anonymous"], result["entries"])
        self.assertEqual("source-1", result["readback"]["prior_entry_id"])
        self.assertIsNone(result["readback"]["resulting_entry_id"])
        self.assertEqual({"entries", "readback"}, set(result))
        with self.assertRaisesRegex(ValueError, "not found"):
            apply_case_scoped_entry_operation([], operation(operation="retire"))
        with self.assertRaisesRegex(ValueError, "not allowed"):
            apply_case_scoped_entry_operation([identified()], operation(operation="retire", payload="x"))

    def test_malformed_and_duplicate_structured_entries_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly"):
            apply_case_scoped_entry_operation(
                [{"entry_id": "source-1", "value": "x", "extra": "no"}], operation()
            )
        with self.assertRaisesRegex(ValueError, "duplicate"):
            apply_case_scoped_entry_operation([identified(), identified()], operation())

    def test_existing_structured_entry_id_must_be_a_string(self):
        with self.assertRaisesRegex(ValueError, "existing entry_id must be a non-empty string"):
            apply_case_scoped_entry_operation([identified(entry_id=1)], operation())

    def test_noncanonical_existing_ids_are_rejected_for_every_operation(self):
        malformed_entries = [identified(" source-1 ")]
        operations = (
            operation(),
            operation(operation="preserve"),
            operation(operation="edit"),
            operation(operation="replace", replacement_entry_id="source-2"),
            operation(operation="retire"),
        )
        for candidate in operations:
            with self.subTest(operation=candidate["operation"]), self.assertRaisesRegex(ValueError, "noncanonical"):
                apply_case_scoped_entry_operation(malformed_entries, candidate)
        self.assertEqual([identified(" source-1 ")], malformed_entries)

    def test_canonical_existing_ids_match_normalized_caller_ids_and_readback(self):
        entries = [identified("source-1")]
        result = apply_case_scoped_entry_operation(
            entries, operation(operation="preserve", entry_id=" source-1 ")
        )
        self.assertEqual(entries, result["entries"])
        self.assertEqual("source-1", result["entries"][0]["entry_id"])
        self.assertEqual("source-1", result["readback"]["prior_entry_id"])
        self.assertEqual("source-1", result["readback"]["resulting_entry_id"])
        with self.assertRaisesRegex(ValueError, "noncanonical"):
            apply_case_scoped_entry_operation(
                [identified("source-1"), identified(" source-1 ")], operation()
            )

    def test_anonymous_legacy_entries_coexist_without_matching_or_silent_id_assignment(self):
        anonymous = [{"value": "same text"}, " same text "]
        result = apply_case_scoped_entry_operation(anonymous, operation(entry_id="new-source"))
        self.assertEqual(anonymous, result["entries"][:2])
        self.assertTrue(all(not (isinstance(entry, dict) and "entry_id" in entry) for entry in result["entries"][:2]))
        with self.assertRaisesRegex(ValueError, "not found"):
            apply_case_scoped_entry_operation(anonymous, operation(operation="preserve", entry_id="same text"))

    def test_case_scope_allows_same_id_without_global_collision_and_does_not_reconcile_other_cases(self):
        first_case = apply_case_scoped_entry_operation([], operation(case_id="case-a"))
        second_case = apply_case_scoped_entry_operation([], operation(case_id="case-b"))
        self.assertEqual(first_case["entries"], second_case["entries"])
        with self.assertRaisesRegex(ValueError, "not found"):
            apply_case_scoped_entry_operation([], operation(case_id="case-b", operation="preserve"))

    def test_operation_is_pure_and_repeated_inputs_are_deterministic(self):
        entries = [identified(), {"legacy": "entry"}]
        before = deepcopy(entries)
        edit = operation(operation="edit", payload={"label": "updated"})
        first = apply_case_scoped_entry_operation(entries, edit)
        second = apply_case_scoped_entry_operation(entries, edit)
        self.assertEqual(before, entries)
        self.assertEqual(first, second)
        self.assertEqual(list(NON_PROOF_STATEMENTS), first["readback"]["non_proofs"])


if __name__ == "__main__":
    unittest.main()
