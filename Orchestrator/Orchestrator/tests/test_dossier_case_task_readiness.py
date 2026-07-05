import unittest

from orchestrator.dossier_case_mapping import adapt_case_packet_to_dossier_case
from orchestrator.dossier_case_mapping_readback import REQUIRED_NEUTRAL_FIELDS
from orchestrator.dossier_case_minimal_fixture import (
    build_admin_case_minimal_fixture,
    build_admin_case_shape_packet,
    build_creative_dossier_minimal_fixture,
)
from orchestrator.dossier_case_task_readiness import (
    BOUNDARY,
    REPORT_NAME,
    build_neutral_task_readiness_report,
    build_neutral_task_readiness_report_dict,
)


class DossierCaseTaskReadinessTests(unittest.TestCase):
    def _complete_packet(self) -> dict:
        return build_admin_case_shape_packet()

    def test_complete_fixture_produces_readiness_report(self):
        report = build_neutral_task_readiness_report(self._complete_packet())

        self.assertEqual(report.report_name, REPORT_NAME)
        self.assertEqual(report.boundary, BOUNDARY)
        self.assertTrue(report.structurally_ready_for_domain_specific_work)
        self.assertEqual(report.structural_readiness_blockers, ())

    def test_both_existing_minimal_fixtures_produce_readiness_reports(self):
        for fixture in (
            build_admin_case_minimal_fixture(),
            build_creative_dossier_minimal_fixture(),
        ):
            report = build_neutral_task_readiness_report(fixture)

            self.assertTrue(report.structurally_ready_for_domain_specific_work)
            self.assertEqual(report.missing_required_neutral_fields, ())
            self.assertFalse(report.product_wedge_selected)

    def test_report_lists_required_neutral_fields(self):
        report = build_neutral_task_readiness_report(self._complete_packet())

        self.assertEqual(report.required_neutral_fields, REQUIRED_NEUTRAL_FIELDS)

    def test_report_identifies_present_required_fields(self):
        report = build_neutral_task_readiness_report(self._complete_packet())

        self.assertEqual(set(report.present_required_neutral_fields), set(REQUIRED_NEUTRAL_FIELDS))
        self.assertEqual(report.missing_required_neutral_fields, ())

    def test_report_identifies_missing_required_fields(self):
        adapted = adapt_case_packet_to_dossier_case(self._complete_packet())
        adapted.pop("open_questions")

        report = build_neutral_task_readiness_report(adapted)

        self.assertIn("open_questions", report.missing_required_neutral_fields)
        self.assertFalse(report.structurally_ready_for_domain_specific_work)
        self.assertIn(
            "missing required neutral field: open_questions",
            report.structural_readiness_blockers,
        )

    def test_report_preserves_open_questions(self):
        report = build_neutral_task_readiness_report(self._complete_packet())

        self.assertEqual(report.open_questions, ("which source item should be checked next",))

    def test_report_preserves_contradictions(self):
        report = build_neutral_task_readiness_report(self._complete_packet())

        self.assertEqual(
            report.contradictions,
            ("source notes disagree about the review date",),
        )

    def test_report_preserves_decisions(self):
        report = build_neutral_task_readiness_report(self._complete_packet())

        self.assertEqual(report.decisions, ("operator has not selected a first product wedge",))

    def test_report_preserves_next_work_items(self):
        report = build_neutral_task_readiness_report(self._complete_packet())

        self.assertEqual(
            report.next_work_items,
            ("compare the fixture through the neutral mapping readback",),
        )

    def test_report_says_no_product_wedge_is_selected(self):
        report = build_neutral_task_readiness_report(self._complete_packet())

        self.assertFalse(report.product_wedge_selected)
        self.assertEqual(report.product_wedge_selection, "no_first_product_wedge_selected")

    def test_report_says_phase_387_is_not_implemented(self):
        report = build_neutral_task_readiness_report(self._complete_packet())

        self.assertFalse(report.phase_387_implemented)

    def test_report_says_runtime_provider_model_are_not_required(self):
        report = build_neutral_task_readiness_report(self._complete_packet())

        self.assertFalse(report.runtime_required)
        self.assertFalse(report.provider_model_required)

    def test_report_includes_explicit_non_proofs(self):
        report = build_neutral_task_readiness_report(self._complete_packet())
        non_proofs = set(report.non_proofs)

        self.assertIn("no runtime proof", non_proofs)
        self.assertIn("no provider/model proof", non_proofs)
        self.assertIn("no semantic correctness proof", non_proofs)
        self.assertIn("no production readiness proof", non_proofs)
        self.assertIn("no first product wedge selection", non_proofs)
        self.assertIn("no product-domain implementation", non_proofs)

    def test_report_is_domain_neutral(self):
        report = build_neutral_task_readiness_report(self._complete_packet())
        surface = " ".join(
            [report.report_name, report.recommended_next_structural_action]
            + list(report.required_neutral_fields)
            + list(report.domain_specific_terms_required)
        )

        self.assertEqual(report.domain_specific_terms_required, ())
        for term in ("claims", "disputes", "appeals", "game", "worldbuilding", "design"):
            self.assertNotIn(term, surface)

    def test_report_dict_is_plain_data(self):
        payload = build_neutral_task_readiness_report_dict(self._complete_packet())

        self.assertEqual(payload["report_name"], REPORT_NAME)
        self.assertIsInstance(payload["required_neutral_fields"], list)
        self.assertIsInstance(payload["open_questions"], list)
        self.assertFalse(payload["product_wedge_selected"])


if __name__ == "__main__":
    unittest.main()
