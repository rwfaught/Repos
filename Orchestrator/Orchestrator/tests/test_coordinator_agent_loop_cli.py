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

    def test_cli_accepts_caller_supplied_model_json_through_stub_seam(self):
        objective = "Classify this fixed status list into three labels"
        payload = {
            "contract_version": "local_model_reasoning_v1",
            "request_id": "prompt-001",
            "objective": objective,
            "normalized_objective": objective.lower(),
            "capability_task": {
                "task_id": "task-001", "title": "Classify supplied labels", "objective": objective,
                "complexity": "simple", "code_generation_required": False, "long_context_required": False,
                "safety_risk": "low", "privacy_sensitivity": "internal", "external_tool_or_api_need": False,
                "live_runtime_execution_need": False, "tolerance_for_mistakes": "medium",
                "deterministic_validation_available": True, "local_model_output_reviewable": True,
            },
            "matched_signals": {"deterministic": ["fixed labels"]}, "confidence": 0.91,
            "clarification_needed": [], "risk_flags": [], "assumptions": [],
        }
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--objective", objective, "--format", "operator", "--model-output-json", json.dumps(payload)])

        rendered = output.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Mode: `validated_model_stub`", rendered)
        self.assertIn("deterministic policy selects the route", rendered)

    def test_cli_rejects_invalid_model_json_without_running_the_loop(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--objective", "Classify this fixed status list into three labels", "--model-output-json", "not-json"])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertTrue(payload["blocked"])

    def test_missing_objective_is_blocked(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main([])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertTrue(payload["blocked"])


if __name__ == "__main__":
    unittest.main()
