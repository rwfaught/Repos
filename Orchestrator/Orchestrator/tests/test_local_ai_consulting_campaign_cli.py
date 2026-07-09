import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from orchestrator.local_ai_consulting_campaign_cli import main


class LocalAIConsultingCampaignCLITests(unittest.TestCase):
    def test_default_json_readback_is_operator_inspectable(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main([])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["selection"], "all")
        self.assertFalse(payload["execution_authorized"])
        self.assertIn("owner_review_ready_scenarios", payload["campaign"]["comparison"])

    def test_selected_blocked_scenario_returns_zero_and_explicit_blocker(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--scenario", "regulated_sensitive_data"])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["readiness_status"], "blocked_by_sensitivity")
        self.assertEqual(payload["blocked_conditions"], ["blocked_by_sensitivity"])
        self.assertFalse(payload["execution_authorized"])

    def test_unknown_scenario_is_a_nonzero_readable_result(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--scenario", "not-a-scenario"])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 1)
        self.assertFalse(payload["found"])
        self.assertIn("internal_knowledge_helpdesk", payload["available_scenarios"])

    def test_markdown_mode_is_concise_and_declares_non_proofs(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--scenario", "internal_knowledge_helpdesk", "--format", "markdown"])

        rendered = output.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("# Local AI Consulting Operator Readback", rendered)
        self.assertIn("Readiness: `owner_review_ready`", rendered)
        self.assertIn("not production readiness", rendered)

    def test_selected_markdown_is_a_pm_review_report(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--scenario", "regulated_sensitive_data", "--format", "markdown"])

        rendered = output.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("## Scenario Summary", rendered)
        self.assertIn("## Readiness Decision", rendered)
        self.assertIn("## Safe Local Exploration", rendered)
        self.assertIn("## Owner Approval Gates", rendered)
        self.assertIn("## Blocked or Deferred", rendered)
        self.assertIn("## Evidence Produced", rendered)
        self.assertIn("## Neutral Dossier/Case Relationship", rendered)
        self.assertIn("## Next Bounded Action", rendered)

    def test_summary_markdown_is_compact_dashboard(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--summary", "--format", "markdown"])

        rendered = output.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("## Readiness Dashboard", rendered)
        self.assertIn("Why Scenarios Are Blocked", rendered)
        self.assertIn("Recommended next review: `internal_knowledge_helpdesk`", rendered)
        self.assertNotIn("source_materials", rendered)

    def test_summary_and_scenario_are_mutually_exclusive(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--summary", "--scenario", "internal_knowledge_helpdesk"])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertIn("cannot be used together", payload["detail"])

    def test_invalid_arguments_are_blocked_without_side_effects(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--format", "xml"])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertTrue(payload["blocked"])
        self.assertIn("Usage:", payload["detail"])


if __name__ == "__main__":
    unittest.main()
