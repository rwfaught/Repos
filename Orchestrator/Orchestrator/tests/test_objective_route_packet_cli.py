import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from orchestrator.objective_route_packet_cli import main


class ObjectiveRoutePacketCLITests(unittest.TestCase):
    def test_operator_objective_command_returns_pm_readback(self):
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
        self.assertIn("Recommended route: `local_model_candidate`", rendered)
        self.assertIn("Local model attempt appropriate: `True`", rendered)
        self.assertIn("Owner-Review Packet", rendered)
        self.assertIn("next bounded action", rendered.lower())

    def test_json_mode_preserves_machine_readable_loop(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--objective", "Classify this fixed status list into three labels"])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["route_readback"]["route"], "deterministic_code_only")
        self.assertTrue(payload["owner_review_packet"]["evidence_produced"])

    def test_empty_or_missing_objective_is_blocked_without_execution(self):
        for args in ([], ["--objective", ""]):
            output = StringIO()
            with redirect_stdout(output):
                code = main(args)

            payload = json.loads(output.getvalue())
            with self.subTest(args=args):
                self.assertEqual(code, 2)
                self.assertTrue(payload["blocked"])

    def test_external_and_frontier_objectives_report_their_boundary(self):
        for objective, marker in (
            ("Sync live CRM records through an external API", "External API needed: `True`"),
            ("Design a multi-module architecture migration with compatibility constraints", "Frontier/Codex needed: `True`"),
        ):
            output = StringIO()
            with redirect_stdout(output):
                code = main(["--objective", objective, "--format", "markdown"])
            with self.subTest(objective=objective):
                self.assertEqual(code, 0)
                self.assertIn(marker, output.getvalue())


if __name__ == "__main__":
    unittest.main()
