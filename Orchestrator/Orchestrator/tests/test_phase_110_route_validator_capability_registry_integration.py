import inspect
import unittest

from orchestrator import request_routing
from orchestrator.request_routing import validate_route_envelope


NO_ACTIVITY_FIELDS = (
    "mutation_performed",
    "execution_performed",
    "provider_executed",
    "model_executed",
    "runtime_executed",
    "wsl_executed",
    "installer_executed",
    "discord_executed",
    "bridge_executed",
    "adapter_executed",
    "platform_executed",
    "export_performed",
    "package_performed",
    "cleanup_performed",
    "deletion_performed",
    "archive_performed",
)


class Phase110RouteValidatorCapabilityRegistryIntegrationTests(unittest.TestCase):
    def envelope(self, request_type: str = "general_answer", **overrides):
        base = {
            "request_id": "route_phase110",
            "request_type": request_type,
            "confidence": 0.8,
            "user_intent_summary": "Classify a structured request envelope.",
            "required_capabilities": [],
            "missing_inputs": [],
            "risk_level": "low",
            "execution_policy": "route_validation_only",
            "recommended_next_action": "operator_review_route_envelope",
            "requires_operator_confirmation": False,
            "requires_external_connector": False,
            "allowed_to_answer_directly": False,
            "allowed_to_mutate_files": False,
            "allowed_to_schedule": False,
            "allowed_to_use_local_documents": False,
            "allowed_to_use_web": False,
            "reasoning_summary_for_operator": "Structured envelope satisfies the route contract.",
            "caveats": [],
        }
        base.update(overrides)
        return base

    def assert_no_activity(self, result):
        for field in NO_ACTIVITY_FIELDS:
            self.assertIn(field, result)
            self.assertFalse(result[field])
        self.assertFalse(result["capability_assessment"]["authorized_execution"])

    def test_validate_route_envelope_returns_capability_assessment(self):
        result = validate_route_envelope(
            self.envelope(
                "planning_request",
                required_capabilities=["planning_report"],
                recommended_next_action="prepare_non_executing_plan_for_operator_review",
            )
        )

        self.assertIn("capability_assessment", result)
        assessment = result["capability_assessment"]
        for key in (
            "requested_capabilities",
            "known_capabilities",
            "unknown_capabilities",
            "maturity_statuses",
            "blocked_or_external_capabilities",
            "production_ready_capabilities",
            "non_proofs",
            "admission_notes",
        ):
            self.assertIn(key, assessment)

    def test_known_non_blocked_capability_ids_can_remain_accepted(self):
        result = validate_route_envelope(
            self.envelope(
                "coding_task",
                required_capabilities=[
                    "source_inspection",
                    "patch_proposal",
                    "filesystem_mutation_authority",
                ],
                allowed_to_mutate_files=True,
                requires_operator_confirmation=True,
                execution_policy="operator_confirmed_bounded_filesystem_mutation",
                recommended_next_action="route_to_future_operator_confirmed_coding_boundary",
            )
        )

        self.assertTrue(result["accepted"])
        self.assertEqual(result["blocked_conditions"], [])
        self.assertEqual(result["capability_assessment"]["unknown_capabilities"], [])
        self.assertEqual(result["capability_assessment"]["blocked_or_external_capabilities"], [])
        self.assert_no_activity(result)

    def test_unknown_capability_ids_reject_admission(self):
        result = validate_route_envelope(
            self.envelope(
                "planning_request",
                required_capabilities=["planning_report", "future_unknown_capability"],
                recommended_next_action="prepare_non_executing_plan_for_operator_review",
            )
        )

        self.assertFalse(result["accepted"])
        self.assertEqual(result["route_admission"], "rejected")
        self.assertIn("unknown_required_capabilities", result["blocked_conditions"])
        self.assertEqual(result["capability_assessment"]["unknown_capabilities"], ["future_unknown_capability"])
        self.assert_no_activity(result)

    def test_blocked_external_capability_ids_reject_admission_conservatively(self):
        result = validate_route_envelope(
            self.envelope(
                "research_request",
                required_capabilities=["web_research"],
                allowed_to_use_web=True,
                caveats=["web_lookup_not_implemented"],
                recommended_next_action="request_future_web_lookup_boundary",
            )
        )

        self.assertFalse(result["accepted"])
        self.assertIn("blocked_or_external_required_capabilities", result["blocked_conditions"])
        self.assertEqual(result["capability_assessment"]["blocked_or_external_capabilities"], ["web_research"])
        self.assert_no_activity(result)

    def test_blocked_external_capabilities_are_allowed_only_for_non_admitted_routes(self):
        result = validate_route_envelope(
            self.envelope(
                "unsupported_or_requires_connector",
                required_capabilities=["external_connector"],
                requires_external_connector=True,
                recommended_next_action="explain_connector_requirement_to_operator",
            )
        )

        self.assertFalse(result["accepted"])
        self.assertIn("unsupported_or_requires_connector", result["blocked_conditions"])
        self.assertNotIn("blocked_or_external_required_capabilities", result["blocked_conditions"])
        self.assertEqual(result["capability_assessment"]["blocked_or_external_capabilities"], ["external_connector"])
        self.assert_no_activity(result)

    def test_capability_assessment_does_not_authorize_execution_or_select_substrate(self):
        result = validate_route_envelope(
            self.envelope(
                "planning_request",
                required_capabilities=["provider_model", "platform_runtime"],
                recommended_next_action="prepare_non_executing_plan_for_operator_review",
            )
        )

        assessment = result["capability_assessment"]
        self.assertFalse(assessment["authorized_execution"])
        self.assertNotIn("selected_provider", assessment)
        self.assertNotIn("selected_model", assessment)
        self.assertNotIn("selected_runtime", assessment)
        self.assertNotIn("selected_platform", assessment)
        self.assertNotIn("selected_worker_substrate", assessment)
        self.assert_no_activity(result)

    def test_activity_flags_remain_false_when_capability_blocks_admission(self):
        result = validate_route_envelope(
            self.envelope(
                "local_document_lookup",
                required_capabilities=["local_document_lookup"],
                allowed_to_use_local_documents=True,
                recommended_next_action="request_document_lookup_boundary",
            )
        )

        self.assertFalse(result["accepted"])
        self.assert_no_activity(result)

    def test_capability_assessment_preserves_structured_fields(self):
        result = validate_route_envelope(
            self.envelope(
                "planning_request",
                required_capabilities=["planning_report", "unknown_capability"],
                recommended_next_action="prepare_non_executing_plan_for_operator_review",
            )
        )
        assessment = result["capability_assessment"]

        self.assertEqual(assessment["requested_capabilities"], ["planning_report", "unknown_capability"])
        self.assertEqual(assessment["known_capabilities"], ["planning_report"])
        self.assertEqual(assessment["unknown_capabilities"], ["unknown_capability"])
        self.assertEqual(assessment["maturity_statuses"], {"planning_report": "docs_control_defined"})
        self.assertIn("capability_label_is_not_execution_authority", assessment["non_proofs"])
        self.assertIn(
            "unknown_capabilities_require_clarification_or_future_registry_entry",
            assessment["admission_notes"],
        )

    def test_phase_103_capability_strings_follow_registry_posture(self):
        accepted = validate_route_envelope(
            self.envelope(
                "file_operation",
                required_capabilities=["bounded_file_write"],
                allowed_to_mutate_files=True,
                requires_operator_confirmation=True,
                execution_policy="operator_confirmed_file_operation",
            )
        )
        rejected = validate_route_envelope(
            self.envelope(
                "reminder_request",
                required_capabilities=["scheduling_contract"],
                allowed_to_schedule=True,
                requires_operator_confirmation=True,
                recommended_next_action="request_future_reminder_boundary",
            )
        )

        self.assertTrue(accepted["accepted"])
        self.assertFalse(rejected["accepted"])
        self.assertIn("blocked_or_external_required_capabilities", rejected["blocked_conditions"])
        self.assertIn("scheduling_contract", rejected["capability_assessment"]["blocked_or_external_capabilities"])

    def test_route_validation_remains_substrate_agnostic(self):
        source = inspect.getsource(request_routing)

        self.assertIn("assess_required_capabilities", source)
        for forbidden in (
            "selected_provider",
            "selected_model",
            "selected_runtime",
            "selected_platform",
            "selected_worker_substrate",
            "import openai",
            "import ollama",
            "import requests",
            "import subprocess",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
