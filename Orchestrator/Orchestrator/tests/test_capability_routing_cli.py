import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from orchestrator.capability_routing_cli import main


class CapabilityRoutingCLITests(unittest.TestCase):
    def test_summary_markdown_is_compact_and_local_first(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--summary", "--format", "markdown"])

        rendered = output.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("# Capability Routing Triage", rendered)
        self.assertIn("deterministic_code_only", rendered)
        self.assertIn("local_model_candidate", rendered)
        self.assertIn("Recommended next review: `local_model_drafting_candidate`", rendered)
        self.assertIn("not model execution", rendered)

    def test_selected_task_report_exposes_external_deferral(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--task", "external_api_integration_deferred"])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["routing_recommendation"]["route"], "external_api_required")
        self.assertIn("external_service_boundary_required", payload["routing_recommendation"]["blocked_or_deferred_conditions"])
        self.assertFalse(payload["routing_recommendation"]["execution_authorized"])

    def test_unknown_task_is_readable_nonzero_result(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--task", "not-a-fixture", "--format", "markdown"])

        self.assertEqual(code, 1)
        self.assertIn("Task not found.", output.getvalue())

    def test_summary_and_task_are_mutually_exclusive(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--summary", "--task", "local_model_drafting_candidate"])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertIn("cannot be used together", payload["detail"])


if __name__ == "__main__":
    unittest.main()
