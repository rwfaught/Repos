from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import orchestrator.alpha_runtime as alpha_runtime
import orchestrator.case_packet as case_packet
from orchestrator.case_packet import (
    load_case_packet,
    save_case_packet,
    save_case_packet_entry_preservation_operation,
)


def packet(**overrides):
    candidate = {
        "case_id": "persistence-case-1",
        "case_type": "neutral_dossier_case",
        "title": "Persistence fixture",
        "objective": "Preserve explicit source and fact identities after reload.",
        "status": "structural_example_only",
        "next_step": "review persisted transition",
        "counterparties": [],
        "source_materials": [],
        "extracted_facts": [],
        "timeline_events": [],
        "open_issues": [],
        "missing_evidence": [],
        "contradictions": [],
        "drafts": [],
        "decisions": [],
    }
    candidate.update(overrides)
    return candidate


def operation(**overrides):
    candidate = {
        "case_id": "persistence-case-1",
        "entry_kind": "source_material",
        "operation": "create",
        "entry_id": "source-1",
        "payload": {"label": "intake note"},
    }
    candidate.update(overrides)
    if candidate["operation"] in ("preserve", "retire") and "payload" not in overrides:
        candidate.pop("payload")
    return candidate


class CasePacketEntryPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.case_dir = Path(self.temporary.name)
        self.patch = patch.object(case_packet, "CASE_PACKETS_DIR", self.case_dir)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.temporary.cleanup()

    def test_identified_source_and_fact_entries_round_trip_with_mixed_legacy_values_and_order(self):
        original = packet(
            source_materials=[
                "legacy source",
                {"entry_id": "source-1", "value": {"label": "invoice"}},
                {"value": "anonymous source"},
                {"entry_id": "source-2", "value": "email"},
            ],
            extracted_facts=[
                {"entry_id": "fact-1", "value": {"claim": "amount due"}},
                "legacy fact",
            ],
        )
        before = deepcopy(original)

        save_case_packet(original)
        loaded = load_case_packet("persistence-case-1")

        self.assertEqual(before, original)
        self.assertEqual(original, loaded)
        self.assertEqual(["source-1", "source-2"], [entry["entry_id"] for entry in loaded["source_materials"] if isinstance(entry, dict) and "entry_id" in entry])
        self.assertEqual("fact-1", loaded["extracted_facts"][0]["entry_id"])
        self.assertEqual(["legacy source", {"entry_id": "source-1", "value": {"label": "invoice"}}, {"value": "anonymous source"}, {"entry_id": "source-2", "value": "email"}], loaded["source_materials"])
        self.assertEqual(json.dumps(original, sort_keys=True), json.dumps(loaded, sort_keys=True))

    def test_all_explicit_transitions_continue_after_reload_and_target_the_correct_field(self):
        save_case_packet(
            packet(
                source_materials=[{"entry_id": "source-1", "value": "old source"}, "legacy source"],
                extracted_facts=[{"entry_id": "fact-1", "value": "old fact"}, "legacy fact"],
            )
        )

        created = save_case_packet_entry_preservation_operation(
            "persistence-case-1", operation(entry_id="source-2", payload="new source")
        )
        preserved = save_case_packet_entry_preservation_operation(
            "persistence-case-1", operation(operation="preserve", entry_id="source-2")
        )
        edited = save_case_packet_entry_preservation_operation(
            "persistence-case-1", operation(operation="edit", entry_id="source-2", payload="edited source")
        )
        replaced = save_case_packet_entry_preservation_operation(
            "persistence-case-1",
            operation(operation="replace", entry_id="source-2", replacement_entry_id="source-3", payload="replacement source"),
        )
        retired = save_case_packet_entry_preservation_operation(
            "persistence-case-1", operation(operation="retire", entry_id="source-3")
        )
        fact = save_case_packet_entry_preservation_operation(
            "persistence-case-1",
            operation(entry_kind="extracted_fact", entry_id="fact-2", payload="new fact"),
        )

        self.assertEqual("created", created["readback"]["transition"])
        self.assertEqual("preserved", preserved["readback"]["transition"])
        self.assertEqual("edited", edited["readback"]["transition"])
        self.assertEqual("replaced", replaced["readback"]["transition"])
        self.assertEqual("retired", retired["readback"]["transition"])
        self.assertEqual([{"entry_id": "source-1", "value": "old source"}, "legacy source"], retired["case_packet"]["source_materials"])
        self.assertEqual(
            [{"entry_id": "fact-1", "value": "old fact"}, "legacy fact", {"entry_id": "fact-2", "value": "new fact"}],
            fact["case_packet"]["extracted_facts"],
        )
        self.assertEqual(retired["case_packet"]["source_materials"], fact["case_packet"]["source_materials"])

    def test_case_id_mismatch_malformed_and_incompatible_packets_fail_diagnostically(self):
        self.case_dir.mkdir(parents=True, exist_ok=True)
        (self.case_dir / "wrong-id.json").write_text(json.dumps(packet(case_id="different-case")), encoding="utf-8")
        (self.case_dir / "malformed.json").write_text("{not json", encoding="utf-8")
        (self.case_dir / "missing-fields.json").write_text(json.dumps({"case_id": "missing-fields"}), encoding="utf-8")
        (self.case_dir / "bad-entry.json").write_text(
            json.dumps(packet(case_id="bad-entry", source_materials=[{"entry_id": " source-1 ", "value": "x"}])),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "does not match requested"):
            load_case_packet("wrong-id")
        with self.assertRaisesRegex(ValueError, "malformed persisted case packet JSON"):
            load_case_packet("malformed")
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            load_case_packet("missing-fields")
        with self.assertRaisesRegex(ValueError, "source_materials are malformed.*noncanonical"):
            load_case_packet("bad-entry")

    def test_load_and_transition_results_are_copy_safe_without_synthesizing_or_matching_ids(self):
        original = packet(source_materials=["same text", {"value": "same text"}])
        save_case_packet(original)
        loaded = load_case_packet("persistence-case-1")
        loaded["source_materials"].append("mutated only in memory")
        reloaded = load_case_packet("persistence-case-1")

        self.assertEqual(original["source_materials"], reloaded["source_materials"])
        result = save_case_packet_entry_preservation_operation(
            "persistence-case-1", operation(entry_id="new-source", payload="same text")
        )
        self.assertEqual(original["source_materials"], result["case_packet"]["source_materials"][:2])
        self.assertTrue(all(not (isinstance(entry, dict) and "entry_id" in entry) for entry in result["case_packet"]["source_materials"][:2]))
        with self.assertRaisesRegex(ValueError, "not found"):
            save_case_packet_entry_preservation_operation(
                "persistence-case-1", operation(operation="preserve", entry_id="same text")
            )

    def test_whole_packet_replacement_cannot_drop_or_rewrite_explicit_identity(self):
        original = packet(source_materials=[{"entry_id": "source-1", "value": "original"}])
        save_case_packet(original)
        dropped = packet(source_materials=[])
        rewritten = packet(source_materials=[{"entry_id": "source-2", "value": "original"}])

        with self.assertRaisesRegex(ValueError, "whole-packet update changes explicit source_materials identities"):
            save_case_packet(dropped)
        with self.assertRaisesRegex(ValueError, "whole-packet update changes explicit source_materials identities"):
            save_case_packet(rewritten)
        self.assertEqual(original, load_case_packet("persistence-case-1"))

    def test_atomic_write_failure_leaves_existing_packet_and_no_temporary_residue(self):
        original = packet(status="original")
        save_case_packet(original)
        changed = packet(status="changed")
        target = self.case_dir / "persistence-case-1.json"

        with patch.object(alpha_runtime.os, "replace", side_effect=OSError("replace failed")):
            with self.assertRaisesRegex(OSError, "replace failed"):
                save_case_packet(changed)

        self.assertEqual(original, load_case_packet("persistence-case-1"))
        self.assertEqual([], list(self.case_dir.glob(f".{target.name}.*.tmp")))


if __name__ == "__main__":
    unittest.main()
