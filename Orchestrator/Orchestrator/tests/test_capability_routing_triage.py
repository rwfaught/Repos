import json
import unittest

from orchestrator.capability_routing_triage import (
    ROUTES,
    build_capability_routing_fixture_library,
    build_capability_routing_review_report,
    build_capability_routing_summary,
    classify_capability_task,
    render_capability_routing_markdown,
)


class CapabilityRoutingTriageTests(unittest.TestCase):
    def test_fixtures_cover_required_routes(self):
        fixtures = build_capability_routing_fixture_library()
        routes = {classify_capability_task(task)["route"] for task in fixtures.values()}

        self.assertEqual(len(fixtures), 5)
        self.assertEqual(routes, set(ROUTES))

    def test_fixture_routes_are_deterministic_and_inspectable(self):
        fixtures = build_capability_routing_fixture_library()
        for task_id, task in fixtures.items():
            first = classify_capability_task(task)
            second = classify_capability_task(task)
            with self.subTest(task_id=task_id):
                self.assertEqual(first, second)
                self.assertTrue(first["recommendation_before_execution"])
                self.assertFalse(first["execution_authorized"])
                self.assertTrue(first["explicit_non_proofs"])

    def test_specific_fixture_route_expectations(self):
        fixtures = build_capability_routing_fixture_library()
        expected = {
            "simple_deterministic_classification": "deterministic_code_only",
            "local_model_drafting_candidate": "local_model_candidate",
            "frontier_coding_architecture": "frontier_model_or_codex_required",
            "sensitive_high_risk_review": "human_review_or_blocked",
            "external_api_integration_deferred": "external_api_required",
        }
        self.assertEqual(
            {task_id: classify_capability_task(task)["route"] for task_id, task in fixtures.items()},
            expected,
        )

    def test_rationale_and_next_action_are_present_for_every_route(self):
        for task_id, task in build_capability_routing_fixture_library().items():
            result = classify_capability_task(task)
            with self.subTest(task_id=task_id):
                self.assertTrue(result["rationale"])
                self.assertTrue(result["next_bounded_action"])
                self.assertTrue(result["local_first_posture"])

    def test_missing_or_invalid_fields_route_to_human_review(self):
        result = classify_capability_task({"task_id": "incomplete", "complexity": "unknown"})

        self.assertEqual(result["route"], "human_review_or_blocked")
        self.assertIn("capability_triage_underdetermined", result["blocked_or_deferred_conditions"])
        self.assertTrue(result["missing_or_invalid_requirements"])

    def test_summary_groups_routes_and_recommends_local_review(self):
        summary = build_capability_routing_summary()

        self.assertEqual(summary["task_count"], 5)
        self.assertEqual(summary["recommended_next_review_task"], "local_model_drafting_candidate")
        self.assertEqual(
            summary["tasks_by_route"]["external_api_required"],
            ["external_api_integration_deferred"],
        )
        json.dumps(summary, sort_keys=True)

    def test_report_and_markdown_surface_are_pm_readable(self):
        report = build_capability_routing_review_report("frontier_coding_architecture")
        rendered = render_capability_routing_markdown(report)

        self.assertTrue(report["found"])
        self.assertEqual(
            report["routing_recommendation"]["route"],
            "frontier_model_or_codex_required",
        )
        self.assertIn("## Routing Decision", rendered)
        self.assertIn("## Capability Factors", rendered)
        self.assertIn("## Explicit Non-Proofs", rendered)


if __name__ == "__main__":
    unittest.main()
