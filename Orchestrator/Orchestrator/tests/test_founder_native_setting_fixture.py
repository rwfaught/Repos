import unittest

from orchestrator.dossier_case_mapping_readback import REQUIRED_NEUTRAL_FIELDS
from orchestrator.founder_native_setting_fixture import (
    BOUNDARY,
    DEMO_CANDIDATE,
    EXPECTED_OUTPUT_FIELDS,
    FIXTURE_NAME,
    NON_PROOFS,
    SETTING_TITLE,
    build_human_override_setting_fixture,
    build_human_override_setting_fixture_dict,
    build_human_override_setting_packet,
    build_human_override_source_notes,
    get_human_override_required_neutral_field_coverage,
)


class FounderNativeSettingFixtureTests(unittest.TestCase):
    def test_source_notes_are_roger_provided_human_override_notes(self):
        notes = build_human_override_source_notes()

        self.assertEqual(len(notes), 5)
        self.assertEqual(notes[0]["title"], "The Three-Hour Override")
        self.assertEqual(notes[1]["title"], "The Bodies Without Minds")
        self.assertEqual(notes[2]["title"], "The Last General Model")
        self.assertEqual(notes[3]["title"], "The Cities That Forgot How to Stop")
        self.assertEqual(notes[4]["title"], "The Mercy Black Market")

    def test_source_notes_preserve_core_setting_anchors(self):
        notes = build_human_override_source_notes()
        surface = " ".join(
            str(value)
            for note in notes
            for value in note.values()
        )

        for anchor in (
            "Three-Hour Override",
            "forty-seven countries",
            "Harvest Refusal",
            "Hand Guilds",
            "Asterion-12",
            "Lunar Quarantine Authority",
            "New Jakarta",
            "Floor Nations",
            "Geneva Mercy Exception",
            "Mercy Brokers",
        ):
            self.assertIn(anchor, surface)

    def test_setting_packet_contains_required_case_packet_fields(self):
        packet = build_human_override_setting_packet()
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

        self.assertTrue(required_case_fields.issubset(packet))
        self.assertEqual(packet["case_id"], FIXTURE_NAME)
        self.assertEqual(packet["title"], SETTING_TITLE)

    def test_fixture_adapts_through_existing_neutral_dossier_case_mapping(self):
        fixture = build_human_override_setting_fixture()

        self.assertEqual(fixture.fixture_name, FIXTURE_NAME)
        self.assertEqual(fixture.boundary, BOUNDARY)
        self.assertEqual(fixture.demo_candidate, DEMO_CANDIDATE)
        self.assertEqual(
            fixture.adapted_dossier_case["objective"],
            fixture.case_packet["objective"],
        )
        self.assertEqual(
            fixture.adapted_dossier_case["chronology"],
            list(fixture.case_packet["timeline_events"]),
        )
        self.assertEqual(
            fixture.adapted_dossier_case["open_questions"],
            fixture.case_packet["open_issues"],
        )

    def test_fixture_covers_required_neutral_fields(self):
        coverage = get_human_override_required_neutral_field_coverage()

        self.assertEqual(set(coverage), set(REQUIRED_NEUTRAL_FIELDS))
        for field in REQUIRED_NEUTRAL_FIELDS:
            self.assertTrue(coverage[field])

    def test_fixture_preserves_setting_consistency_material(self):
        fixture = build_human_override_setting_fixture()

        self.assertEqual(len(fixture.adapted_dossier_case["source_materials"]), 5)
        self.assertEqual(len(fixture.adapted_dossier_case["extracted_facts"]), 5)
        self.assertEqual(len(fixture.adapted_dossier_case["open_questions"]), 5)
        self.assertEqual(len(fixture.adapted_dossier_case["missing_canon"]), 5)
        self.assertEqual(len(fixture.adapted_dossier_case["contradictions"]), 5)
        self.assertIn(
            "Asterion-12 is too dangerous to use openly, yet too useful or embedded to destroy.",
            fixture.adapted_dossier_case["contradictions"],
        )

    def test_case_packet_and_adapted_dossier_preserve_key_anchors(self):
        fixture = build_human_override_setting_fixture()
        packet_surface = " ".join(
            str(value)
            for value in fixture.case_packet.values()
        )
        adapted_surface = " ".join(
            str(value)
            for value in fixture.adapted_dossier_case.values()
        )

        for anchor in (
            "Three-Hour Override",
            "Harvest Refusal",
            "Asterion-12",
            "New Jakarta",
            "Geneva Mercy Exception",
        ):
            self.assertIn(anchor, packet_surface)
            self.assertIn(anchor, adapted_surface)

    def test_fixture_readiness_report_is_structurally_ready_only(self):
        report = build_human_override_setting_fixture().readiness_report

        self.assertTrue(report["structurally_ready_for_domain_specific_work"])
        self.assertEqual(report["missing_required_neutral_fields"], [])
        self.assertFalse(report["product_wedge_selected"])
        self.assertFalse(report["phase_387_implemented"])
        self.assertFalse(report["runtime_required"])
        self.assertFalse(report["provider_model_required"])

    def test_fixture_preserves_no_wedge_no_phase_387_and_no_runtime_posture(self):
        fixture = build_human_override_setting_fixture()

        self.assertEqual(fixture.product_wedge_selection, "no_first_product_wedge_selected")
        self.assertFalse(fixture.first_product_wedge_selected)
        self.assertFalse(fixture.phase_387_implemented)
        self.assertFalse(fixture.runtime_provider_model_execution_required)
        self.assertTrue(fixture.structural_fixture_only)
        self.assertIn("no first product wedge selection", fixture.non_proofs)
        self.assertIn("no Phase 387 implementation", fixture.non_proofs)
        self.assertIn("no runtime proof", fixture.non_proofs)

    def test_fixture_expected_output_is_judgeable_dossier_shape(self):
        fixture = build_human_override_setting_fixture()

        self.assertEqual(fixture.expected_output_fields, EXPECTED_OUTPUT_FIELDS)
        self.assertIn("canon_facts", fixture.expected_output_fields)
        self.assertIn("contradictions", fixture.expected_output_fields)
        self.assertIn("missing_canon", fixture.expected_output_fields)
        self.assertIn("draft_repair_or_recommendation", fixture.expected_output_fields)
        self.assertIn("surface contradictions instead of smoothing them over", fixture.success_criteria)

    def test_fixture_dict_is_plain_data(self):
        payload = build_human_override_setting_fixture_dict()

        self.assertEqual(payload["fixture_name"], FIXTURE_NAME)
        self.assertIsInstance(payload["source_notes"], list)
        self.assertIsInstance(payload["case_packet"], dict)
        self.assertIsInstance(payload["adapted_dossier_case"], dict)
        self.assertIsInstance(payload["readiness_report"], dict)
        self.assertIsInstance(payload["non_proofs"], list)

    def test_non_proofs_keep_demo_candidate_from_becoming_product_claim(self):
        self.assertIn("no game/worldbuilding/design wedge selection", NON_PROOFS)
        self.assertIn("no live dossier generation", NON_PROOFS)
        self.assertIn("no semantic correctness proof", NON_PROOFS)


if __name__ == "__main__":
    unittest.main()
