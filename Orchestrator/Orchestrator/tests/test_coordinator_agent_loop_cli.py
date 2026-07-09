import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from orchestrator.coordinator_agent_loop_cli import main


class CoordinatorAgentLoopCLITests(unittest.TestCase):
    def test_markdown_demo_shows_whole_loop(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main([
                "--objective",
                "Summarize these internal policy notes for staff review",
                "--format",
                "markdown",
            ])

        rendered = output.getvalue()
        self.assertEqual(code, 0)
        for section in (
            "## Intake Interpretation",
            "## Coordinator Plan",
            "## Worker Handoff",
            "## Dry Worker Result",
            "## Review/Evaluation",
            "## Coordinator Closeout",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(section, rendered)
        self.assertIn("Dispatched: `False`", rendered)

    def test_json_demo_contains_all_typed_loop_surfaces(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--objective", "Classify this fixed status list into three labels"])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        for key in (
            "operator_prompt", "intake_interpretation", "capability_route",
            "coordinator_plan", "worker_handoff", "worker_result",
            "review_evaluation", "coordinator_closeout",
            "operator_review_packet",
        ):
            self.assertIn(key, payload)

    def test_operator_format_is_concise_and_includes_governance_fields(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main([
                "--objective",
                "Classify this fixed status list into three labels",
                "--format",
                "operator",
            ])

        rendered = output.getvalue()
        self.assertEqual(code, 0)
        for section in (
            "## Safe Local Exploration (Planning Only)",
            "## Owner Approval Gates",
            "## Blocked or Deferred",
            "## Neutral Dossier/Case Relationship",
            "## Next Bounded Action",
            "## Explicit Non-Proofs",
        ):
            self.assertIn(section, rendered)
        self.assertIn("Execution authorized: `False`", rendered)

    def test_missing_objective_is_blocked(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main([])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertTrue(payload["blocked"])


if __name__ == "__main__":
    unittest.main()
