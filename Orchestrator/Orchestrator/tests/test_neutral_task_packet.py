import unittest

from orchestrator.neutral_task_packet import (
    BOUNDARY,
    NO_FIRST_PRODUCT_WEDGE_SELECTED,
    NOT_PRODUCTION_READINESS,
    PHASE_387_REMAINS_PARKED,
    REQUIRED_PACKET_FIELDS,
    RUNTIME_PROVIDER_MODEL_EXECUTION_EXCLUDED,
    build_neutral_task_packet,
    build_neutral_task_packet_report,
    build_neutral_task_packet_report_dict,
)


class NeutralTaskPacketTests(unittest.TestCase):
    def test_valid_packet_report_shows_required_fields_are_present(self):
        packet = build_neutral_task_packet()

        report = build_neutral_task_packet_report(packet)

        self.assertEqual(report.boundary, BOUNDARY)
        self.assertEqual(report.required_packet_fields, REQUIRED_PACKET_FIELDS)
        self.assertEqual(set(report.present_required_packet_fields), set(REQUIRED_PACKET_FIELDS))
        self.assertEqual(report.missing_required_packet_fields, ())
        self.assertTrue(report.structurally_ready)
        self.assertEqual(report.structural_blockers, ())

    def test_missing_field_path_reports_missing_required_fields(self):
        packet = build_neutral_task_packet().to_dict()
        packet.pop("operator_goal")
        packet.pop("blocked_until")

        report = build_neutral_task_packet_report(packet)

        self.assertIn("operator_goal", report.missing_required_packet_fields)
        self.assertIn("blocked_until", report.missing_required_packet_fields)
        self.assertIn(
            "missing required packet field: operator_goal",
            report.structural_blockers,
        )
        self.assertFalse(report.structurally_ready)

    def test_review_queues_remain_visible(self):
        report = build_neutral_task_packet_report(build_neutral_task_packet())

        self.assertEqual(
            report.open_questions,
            ("which domain, if any, should later become the first proving domain",),
        )
        self.assertEqual(
            report.contradictions_or_tensions,
            ("product-shaped planning must not silently choose a wedge",),
        )
        self.assertEqual(
            report.decisions_needed,
            ("Roger/CTO must choose a domain or explicitly continue abstraction-first",),
        )
        self.assertEqual(
            report.next_work_items,
            ("review neutral packet structure before any domain-specific boundary",),
        )

    def test_stop_postures_remain_explicit(self):
        report = build_neutral_task_packet_report(build_neutral_task_packet())

        self.assertTrue(report.runtime_provider_model_execution_excluded)
        self.assertTrue(report.phase_387_remains_parked)
        self.assertTrue(report.no_first_product_wedge_selected)

    def test_stop_posture_mismatch_blocks_structural_readiness(self):
        packet = build_neutral_task_packet().to_dict()
        packet["runtime_provider_model_posture"] = "runtime proof requested"

        report = build_neutral_task_packet_report(packet)

        self.assertFalse(report.runtime_provider_model_execution_excluded)
        self.assertFalse(report.structurally_ready)
        self.assertIn(
            "runtime/provider/model execution exclusion is not explicit",
            report.structural_blockers,
        )

    def test_packet_preserves_required_marker_text(self):
        packet = build_neutral_task_packet()
        surface = " ".join(
            [
                packet.boundary_name,
                packet.wedge_posture,
                packet.phase_387_posture,
                packet.runtime_provider_model_posture,
                *packet.explicit_non_proofs,
            ]
        )

        self.assertIn("NEUTRAL_TASK_PACKET_SOURCE_TEST_DOCS", surface)
        self.assertIn(NO_FIRST_PRODUCT_WEDGE_SELECTED, surface)
        self.assertIn(PHASE_387_REMAINS_PARKED, surface)
        self.assertIn(RUNTIME_PROVIDER_MODEL_EXECUTION_EXCLUDED, surface)
        self.assertIn(NOT_PRODUCTION_READINESS, surface)

    def test_packet_remains_domain_neutral(self):
        packet = build_neutral_task_packet()
        report = build_neutral_task_packet_report(packet)
        surface = " ".join(
            [
                packet.operator_goal,
                packet.neutral_subject,
                *packet.success_shape,
                *report.structural_blockers,
            ]
        )

        for term in ("claims", "disputes", "appeals", "game", "worldbuilding", "design"):
            self.assertNotIn(term, surface)

    def test_report_dict_is_plain_data(self):
        payload = build_neutral_task_packet_report_dict(build_neutral_task_packet())

        self.assertEqual(payload["boundary"], BOUNDARY)
        self.assertIsInstance(payload["required_packet_fields"], list)
        self.assertIsInstance(payload["open_questions"], list)
        self.assertTrue(payload["runtime_provider_model_execution_excluded"])


if __name__ == "__main__":
    unittest.main()
