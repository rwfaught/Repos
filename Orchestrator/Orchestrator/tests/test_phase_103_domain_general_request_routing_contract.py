import unittest

from orchestrator.request_routing import (
    REQUEST_TYPES,
    ROUTE_ENVELOPE_REQUIRED_FIELDS,
    validate_route_envelope,
)


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


class Phase103DomainGeneralRequestRoutingContractTests(unittest.TestCase):
    def envelope(self, request_type: str = "general_answer", **overrides):
        base = {
            "request_id": "route_phase103",
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
        self.assertIn("no mutation", result["activity_statement"])
        self.assertIn("provider", result["activity_statement"])
        self.assertIn("archive", result["activity_statement"])
        self.assertIn("capability_assessment", result)
        self.assertFalse(result["capability_assessment"]["authorized_execution"])

    def assert_accepted(self, result, request_type):
        self.assertEqual(result["route_admission"], "accepted")
        self.assertTrue(result["accepted"])
        self.assertEqual(result["request_type"], request_type)
        self.assertEqual(result["missing_requirements"], [])
        self.assertEqual(result["blocked_conditions"], [])
        self.assertEqual(result["normalized_envelope"]["request_type"], request_type)
        self.assert_no_activity(result)

    def test_contract_exports_required_types_and_fields(self):
        self.assertEqual(
            REQUEST_TYPES,
            (
                "general_answer",
                "local_document_lookup",
                "reminder_request",
                "coding_task",
                "file_operation",
                "planning_request",
                "research_request",
                "creative_generation",
                "unsupported_or_requires_connector",
                "needs_clarification",
            ),
        )
        for field in (
            "request_id",
            "request_type",
            "confidence",
            "execution_policy",
            "allowed_to_answer_directly",
            "allowed_to_use_web",
            "caveats",
        ):
            self.assertIn(field, ROUTE_ENVELOPE_REQUIRED_FIELDS)

    def test_general_answer_route_can_answer_directly_when_low_risk_and_complete(self):
        result = validate_route_envelope(
            self.envelope(
                "general_answer",
                allowed_to_answer_directly=True,
                recommended_next_action="answer_directly_without_execution",
            )
        )
        self.assert_accepted(result, "general_answer")

    def test_local_document_lookup_route_is_rejected_until_registry_posture_is_unblocked(self):
        result = validate_route_envelope(
            self.envelope(
                "local_document_lookup",
                required_capabilities=["local_document_lookup"],
                allowed_to_use_local_documents=True,
                recommended_next_action="request_document_lookup_boundary",
                caveats=["local_document_lookup_not_implemented_by_phase103"],
            )
        )
        self.assertEqual(result["route_admission"], "rejected")
        self.assertFalse(result["accepted"])
        self.assertIn("blocked_or_external_required_capabilities", result["blocked_conditions"])
        self.assertIn("local_document_lookup", result["capability_assessment"]["blocked_or_external_capabilities"])
        self.assert_no_activity(result)

    def test_reminder_request_route_is_rejected_until_registry_posture_is_unblocked(self):
        result = validate_route_envelope(
            self.envelope(
                "reminder_request",
                required_capabilities=["scheduling_contract"],
                allowed_to_schedule=True,
                requires_operator_confirmation=True,
                recommended_next_action="request_future_reminder_boundary",
                caveats=["scheduling_not_implemented_by_phase103"],
            )
        )
        self.assertEqual(result["route_admission"], "rejected")
        self.assertFalse(result["accepted"])
        self.assertIn("blocked_or_external_required_capabilities", result["blocked_conditions"])
        self.assertIn("scheduling_contract", result["capability_assessment"]["blocked_or_external_capabilities"])
        self.assert_no_activity(result)

    def test_coding_task_route_can_request_capabilities_without_naming_substrate(self):
        result = validate_route_envelope(
            self.envelope(
                "coding_task",
                required_capabilities=["source_inspection", "patch_proposal", "filesystem_mutation_authority"],
                allowed_to_mutate_files=True,
                requires_operator_confirmation=True,
                execution_policy="operator_confirmed_bounded_filesystem_mutation",
                recommended_next_action="route_to_future_operator_confirmed_coding_boundary",
            )
        )
        self.assert_accepted(result, "coding_task")

    def test_file_operation_route_can_mutate_only_with_operator_confirmation(self):
        result = validate_route_envelope(
            self.envelope(
                "file_operation",
                required_capabilities=["bounded_file_write"],
                allowed_to_mutate_files=True,
                requires_operator_confirmation=True,
                execution_policy="operator_confirmed_file_operation",
            )
        )
        self.assert_accepted(result, "file_operation")

    def test_planning_request_route_is_non_mutating_and_non_executing(self):
        result = validate_route_envelope(
            self.envelope(
                "planning_request",
                required_capabilities=["planning_report"],
                recommended_next_action="prepare_non_executing_plan_for_operator_review",
            )
        )
        self.assert_accepted(result, "planning_request")

    def test_research_request_route_is_rejected_until_registry_posture_is_unblocked(self):
        result = validate_route_envelope(
            self.envelope(
                "research_request",
                required_capabilities=["web_research"],
                allowed_to_use_web=True,
                recommended_next_action="request_future_web_lookup_boundary",
                caveats=["web_lookup_not_implemented"],
            )
        )
        self.assertEqual(result["route_admission"], "rejected")
        self.assertFalse(result["accepted"])
        self.assertIn("blocked_or_external_required_capabilities", result["blocked_conditions"])
        self.assertIn("web_research", result["capability_assessment"]["blocked_or_external_capabilities"])
        self.assert_no_activity(result)

    def test_creative_generation_route_is_non_mutating_by_default(self):
        result = validate_route_envelope(
            self.envelope(
                "creative_generation",
                required_capabilities=["creative_text_generation"],
                recommended_next_action="prepare_creative_output_without_file_mutation",
            )
        )
        self.assert_accepted(result, "creative_generation")

    def test_unsupported_or_requires_connector_route_is_valid_rejection_without_capabilities(self):
        result = validate_route_envelope(
            self.envelope(
                "unsupported_or_requires_connector",
                requires_external_connector=True,
                required_capabilities=["external_connector"],
                recommended_next_action="explain_connector_requirement_to_operator",
            )
        )
        self.assertEqual(result["route_admission"], "rejected")
        self.assertFalse(result["accepted"])
        self.assertIn("unsupported_or_requires_connector", result["blocked_conditions"])
        self.assert_no_activity(result)

    def test_needs_clarification_route_requires_missing_inputs_and_no_capabilities(self):
        result = validate_route_envelope(
            self.envelope(
                "needs_clarification",
                missing_inputs=["target_document"],
                confidence=0.4,
                recommended_next_action="ask_operator_for_missing_target_document",
            )
        )
        self.assertEqual(result["route_admission"], "needs_clarification")
        self.assertFalse(result["accepted"])
        self.assertEqual(result["missing_requirements"], [])
        self.assertEqual(result["blocked_conditions"], [])
        self.assert_no_activity(result)

    def test_unknown_request_type_is_rejected(self):
        result = validate_route_envelope(self.envelope("run_everything"))
        self.assertEqual(result["route_admission"], "rejected")
        self.assertFalse(result["accepted"])
        self.assertIn("unknown_request_type", result["blocked_conditions"])
        self.assert_no_activity(result)

    def test_missing_required_fields_are_rejected_with_explicit_requirements(self):
        envelope = self.envelope()
        del envelope["request_id"]
        del envelope["risk_level"]
        result = validate_route_envelope(envelope)
        self.assertEqual(result["route_admission"], "rejected")
        self.assertIn("request_id", result["missing_requirements"])
        self.assertIn("risk_level", result["missing_requirements"])
        self.assertIn("missing_required_envelope_fields", result["blocked_conditions"])
        self.assert_no_activity(result)

    def test_confidence_must_be_numeric_and_in_range(self):
        string_result = validate_route_envelope(self.envelope(confidence="0.8"))
        high_result = validate_route_envelope(self.envelope(confidence=1.1))
        self.assertIn("confidence_must_be_numeric", string_result["blocked_conditions"])
        self.assertIn("confidence_out_of_range", high_result["blocked_conditions"])

    def test_boolean_permission_fields_must_be_real_booleans(self):
        result = validate_route_envelope(
            self.envelope(allowed_to_mutate_files="false", requires_operator_confirmation="true")
        )
        self.assertIn("allowed_to_mutate_files_must_be_boolean", result["blocked_conditions"])
        self.assertIn("requires_operator_confirmation_must_be_boolean", result["blocked_conditions"])
        self.assertFalse(result["accepted"])

    def test_needs_clarification_cannot_enable_answer_mutation_schedule_docs_or_web(self):
        result = validate_route_envelope(
            self.envelope(
                "needs_clarification",
                missing_inputs=["specific_date"],
                allowed_to_answer_directly=True,
                allowed_to_mutate_files=True,
                allowed_to_schedule=True,
                allowed_to_use_local_documents=True,
                allowed_to_use_web=True,
                caveats=["web_lookup_not_implemented"],
            )
        )
        self.assertEqual(result["route_admission"], "rejected")
        self.assertIn("needs_clarification_must_not_enable_capabilities", result["blocked_conditions"])

    def test_unsupported_route_cannot_enable_any_execution_capability(self):
        result = validate_route_envelope(
            self.envelope(
                "unsupported_or_requires_connector",
                allowed_to_answer_directly=True,
                allowed_to_mutate_files=True,
                allowed_to_schedule=True,
                allowed_to_use_local_documents=True,
                allowed_to_use_web=True,
                caveats=["web_lookup_not_implemented"],
            )
        )
        self.assertIn("unsupported_route_must_not_enable_capabilities", result["blocked_conditions"])
        self.assertFalse(result["accepted"])

    def test_mutation_requires_confirmation_and_coding_or_file_route(self):
        no_confirmation = validate_route_envelope(
            self.envelope("coding_task", allowed_to_mutate_files=True)
        )
        wrong_route = validate_route_envelope(
            self.envelope(
                "planning_request",
                allowed_to_mutate_files=True,
                requires_operator_confirmation=True,
            )
        )
        self.assertIn("mutation_requires_operator_confirmation", no_confirmation["blocked_conditions"])
        self.assertIn("mutation_only_allowed_for_coding_task_or_file_operation", wrong_route["blocked_conditions"])

    def test_scheduling_requires_reminder_request_and_confirmation(self):
        no_confirmation = validate_route_envelope(
            self.envelope("reminder_request", allowed_to_schedule=True)
        )
        wrong_route = validate_route_envelope(
            self.envelope(
                "planning_request",
                allowed_to_schedule=True,
                requires_operator_confirmation=True,
            )
        )
        self.assertIn("scheduling_requires_operator_confirmation", no_confirmation["blocked_conditions"])
        self.assertIn("scheduling_only_allowed_for_reminder_request", wrong_route["blocked_conditions"])

    def test_local_documents_are_limited_to_local_document_lookup(self):
        result = validate_route_envelope(
            self.envelope("general_answer", allowed_to_use_local_documents=True)
        )
        self.assertIn("local_documents_only_allowed_for_local_document_lookup", result["blocked_conditions"])
        self.assertFalse(result["accepted"])

    def test_web_requires_research_request_and_does_not_implement_lookup(self):
        wrong_route = validate_route_envelope(
            self.envelope(
                "general_answer",
                allowed_to_use_web=True,
                caveats=["web_lookup_not_implemented"],
            )
        )
        missing_caveat = validate_route_envelope(
            self.envelope("research_request", allowed_to_use_web=True)
        )
        self.assertIn("web_only_allowed_for_research_request", wrong_route["blocked_conditions"])
        self.assertIn("web_lookup_not_implemented_caveat", missing_caveat["missing_requirements"])

    def test_direct_answer_is_blocked_for_missing_inputs_high_risk_mutation_schedule_connector_docs_or_web(self):
        result = validate_route_envelope(
            self.envelope(
                "research_request",
                missing_inputs=["jurisdiction"],
                risk_level="high",
                allowed_to_answer_directly=True,
                allowed_to_mutate_files=True,
                allowed_to_schedule=True,
                allowed_to_use_local_documents=True,
                allowed_to_use_web=True,
                requires_external_connector=True,
                caveats=["web_lookup_not_implemented"],
            )
        )
        blockers = " ".join(result["blocked_conditions"])
        for expected in (
            "direct_answer_not_allowed",
            "missing_inputs",
            "high_risk",
            "mutation_allowed",
            "scheduling_allowed",
            "external_connector_required",
            "local_documents_required",
            "web_required",
        ):
            self.assertIn(expected, blockers)

    def test_substrate_named_coding_task_is_rejected(self):
        result = validate_route_envelope(
            self.envelope(
                "coding_task",
                required_capabilities=["source_inspection"],
                allowed_to_mutate_files=True,
                requires_operator_confirmation=True,
                execution_policy="execute with Codex as provider",
            )
        )
        self.assertEqual(result["route_admission"], "rejected")
        self.assertIn("route_must_be_substrate_agnostic", result["blocked_conditions"])

    def test_non_object_input_is_rejected_without_activity(self):
        result = validate_route_envelope(["not", "an", "envelope"])
        self.assertEqual(result["route_admission"], "rejected")
        self.assertIn("route_envelope_object", result["missing_requirements"])
        self.assert_no_activity(result)


if __name__ == "__main__":
    unittest.main()
