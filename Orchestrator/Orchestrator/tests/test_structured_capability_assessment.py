import unittest

from orchestrator.intake_admission_pipeline import (
    run_structured_intake_admission_pipeline,
)
from orchestrator.route_proposal import (
    RequestIntakeRecord,
    admit_route_proposal,
    assess_structured_capability_assessment,
    build_candidate_route_envelope,
)


class StructuredCapabilityAssessmentTests(unittest.TestCase):
    def assessment(self, **overrides):
        value = {
            "input_completeness": "complete",
            "objective_clarity": "clear",
            "consequence_level": "low",
            "external_capability_dependency": False,
            "reviewability": "reviewable",
            "reversibility": "reversible",
            "requires_human_decision": False,
            "blocked_conditions": [],
            "missing_information": [],
        }
        value.update(overrides)
        return value

    def intake(self, **overrides):
        value = {
            "request_id": "capability_assessment_test",
            "observed_request_summary": "Structured operator context only.",
            "request_type": "planning_request",
            "confidence": 0.85,
            "required_capabilities": ("planning_report",),
            "missing_inputs": (),
            "risk_level": "low",
            "execution_policy": "structured_intake_validation_only",
            "recommended_next_action": "prepare_non_executing_plan_for_operator_review",
            "requires_operator_confirmation": False,
            "requires_external_connector": False,
            "allowed_to_answer_directly": False,
            "allowed_to_mutate_files": False,
            "allowed_to_schedule": False,
            "allowed_to_use_local_documents": False,
            "allowed_to_use_web": False,
            "reasoning_summary_for_operator": "Explicit structured fields supplied.",
            "structured_capability_assessment": self.assessment(),
        }
        value.update(overrides)
        return RequestIntakeRecord(**value)

    def assert_no_execution_side_effects(self, assessment):
        self.assertFalse(assessment["execution_authority"])
        self.assertFalse(assessment["authorization_created"])
        self.assertFalse(assessment["dispatch_performed"])
        self.assertFalse(assessment["canonical_execution_state_created"])

    def test_valid_structured_assessment_is_eligible_for_a_bounded_next_boundary(self):
        decision = admit_route_proposal(self.intake())

        self.assertTrue(decision.accepted)
        self.assertEqual(decision.next_boundary_kind, "ready_for_coordinator_boundary_decision")
        assessment = decision.structured_capability_assessment
        self.assertEqual(assessment["assessment_state"], "eligible_for_bounded_next_boundary")
        self.assertEqual(assessment["normalized_assessment"], self.assessment())
        self.assert_no_execution_side_effects(assessment)

    def test_incomplete_information_requires_clarification(self):
        decision = admit_route_proposal(
            self.intake(
                structured_capability_assessment=self.assessment(
                    input_completeness="incomplete",
                    objective_clarity="needs_clarification",
                    missing_information=["declared_scope"],
                )
            )
        )

        self.assertFalse(decision.accepted)
        self.assertEqual(decision.route_admission, "needs_clarification")
        self.assertEqual(decision.next_boundary_kind, "ask_clarification")
        self.assertIn("declared_scope", decision.missing_requirements)

    def test_malformed_types_and_unknown_fields_are_rejected_without_coercion(self):
        decision = admit_route_proposal(
            self.intake(
                structured_capability_assessment=self.assessment(
                    external_capability_dependency="false",
                    provider="codex",
                )
            )
        )

        assessment = decision.structured_capability_assessment
        self.assertFalse(decision.accepted)
        self.assertEqual(assessment["assessment_state"], "blocked")
        self.assertIsNone(assessment["normalized_assessment"])
        self.assertIn("structured_capability_assessment_unknown_fields", assessment["blocked_conditions"])
        self.assertIn(
            "capability_assessment_external_capability_dependency_must_be_boolean",
            assessment["blocked_conditions"],
        )

    def test_elevated_consequence_requires_operator_review_not_execution(self):
        decision = admit_route_proposal(
            self.intake(
                structured_capability_assessment=self.assessment(consequence_level="elevated")
            )
        )

        assessment = decision.structured_capability_assessment
        self.assertTrue(decision.accepted)
        self.assertEqual(assessment["assessment_state"], "operator_review_required")
        self.assertIn("elevated_consequence", assessment["review_reasons"])
        self.assert_no_execution_side_effects(assessment)

    def test_external_capability_dependency_requires_review_without_selecting_substrate(self):
        decision = admit_route_proposal(
            self.intake(
                structured_capability_assessment=self.assessment(
                    external_capability_dependency=True
                )
            )
        )

        assessment = decision.structured_capability_assessment
        self.assertEqual(assessment["assessment_state"], "operator_review_required")
        self.assertIn("external_capability_dependency", assessment["review_reasons"])
        self.assertFalse(any(
            key in assessment["normalized_assessment"]
            for key in ("provider", "model", "runtime", "worker", "execution_substrate")
        ))
        self.assert_no_execution_side_effects(assessment)

    def test_repeated_identical_input_is_deterministic_and_pipeline_has_no_side_effects(self):
        first = run_structured_intake_admission_pipeline(self.intake())
        second = run_structured_intake_admission_pipeline(self.intake())

        self.assertEqual(first, second)
        self.assertTrue(first.accepted)
        self.assertFalse(first.execution_authority)
        self.assertFalse(any(first.no_activity_flags.values()))
        self.assert_no_execution_side_effects(first.structured_capability_assessment)

    def test_existing_intake_behavior_remains_compatible_when_assessment_is_absent(self):
        intake = self.intake(structured_capability_assessment=None)
        proposal = build_candidate_route_envelope(intake)
        decision = admit_route_proposal(proposal)

        self.assertEqual(proposal.proposal_state, "candidate_route_proposed")
        self.assertTrue(decision.accepted)
        self.assertIsNone(decision.structured_capability_assessment)

    def test_direct_assessment_rejects_non_object_input(self):
        assessment = assess_structured_capability_assessment(["not", "an", "object"])

        self.assertEqual(assessment["assessment_state"], "blocked")
        self.assertIn(
            "structured_capability_assessment_must_be_object",
            assessment["blocked_conditions"],
        )
        self.assert_no_execution_side_effects(assessment)


if __name__ == "__main__":
    unittest.main()
