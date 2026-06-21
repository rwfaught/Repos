import inspect
import unittest

from orchestrator import route_proposal
from orchestrator.route_proposal import (
    AdmissionDecision,
    CandidateRouteProposal,
    RequestIntakeRecord,
    admit_route_proposal,
    build_candidate_route_envelope,
)


class Phase111RouteProposalSourceContractTests(unittest.TestCase):
    def intake(self, request_type: str = "planning_request", **overrides):
        base = {
            "request_id": "route_phase111",
            "observed_request_summary": "Classify a structured request intake record.",
            "request_type": request_type,
            "confidence": 0.82,
            "required_capabilities": ("planning_report",),
            "missing_inputs": (),
            "risk_level": "low",
            "execution_policy": "route_proposal_validation_only",
            "recommended_next_action": "prepare_non_executing_plan_for_operator_review",
            "requires_operator_confirmation": False,
            "requires_external_connector": False,
            "allowed_to_answer_directly": False,
            "allowed_to_mutate_files": False,
            "allowed_to_schedule": False,
            "allowed_to_use_local_documents": False,
            "allowed_to_use_web": False,
            "reasoning_summary_for_operator": "Structured intake record already declares route fields.",
            "caveats": (),
            "intake_source": "structured_operator_intake",
        }
        base.update(overrides)
        return RequestIntakeRecord(**base)

    def test_build_candidate_route_envelope_creates_phase_103_compatible_envelope(self):
        proposal = build_candidate_route_envelope(self.intake())

        self.assertIsInstance(proposal, CandidateRouteProposal)
        self.assertEqual(proposal.proposal_state, "candidate_route_proposed")
        envelope = proposal.route_envelope
        for field in (
            "request_id",
            "request_type",
            "confidence",
            "user_intent_summary",
            "required_capabilities",
            "missing_inputs",
            "risk_level",
            "execution_policy",
            "recommended_next_action",
            "requires_operator_confirmation",
            "requires_external_connector",
            "allowed_to_answer_directly",
            "allowed_to_mutate_files",
            "allowed_to_schedule",
            "allowed_to_use_local_documents",
            "allowed_to_use_web",
            "reasoning_summary_for_operator",
            "caveats",
        ):
            self.assertIn(field, envelope)
        self.assertEqual(envelope["user_intent_summary"], "Classify a structured request intake record.")
        self.assertEqual(envelope["required_capabilities"], ["planning_report"])

    def test_admit_route_proposal_calls_validation_and_returns_capability_assessment(self):
        decision = admit_route_proposal(self.intake())

        self.assertIsInstance(decision, AdmissionDecision)
        self.assertEqual(decision.route_admission, "accepted")
        self.assertIn("planning_report", decision.capability_assessment["known_capabilities"])
        self.assertEqual(decision.capability_assessment["unknown_capabilities"], [])
        self.assertFalse(decision.execution_authority)

    def test_accepted_structured_coding_route_is_non_executing_boundary_ready_only(self):
        decision = admit_route_proposal(
            self.intake(
                "coding_task",
                required_capabilities=("source_inspection", "patch_proposal", "filesystem_mutation_authority"),
                allowed_to_mutate_files=True,
                requires_operator_confirmation=True,
                execution_policy="operator_confirmed_bounded_filesystem_mutation",
                recommended_next_action="route_to_future_operator_confirmed_coding_boundary",
            )
        )

        self.assertTrue(decision.accepted)
        self.assertEqual(decision.next_boundary_kind, "ready_for_coordinator_boundary_decision")
        self.assertEqual(decision.accepted_route_state, "accepted_route_without_execution_authority")
        self.assertFalse(decision.execution_authority)
        self.assertTrue(all(flag is False for flag in decision.activity_flags.values()))

    def test_unknown_capabilities_are_rejected_through_admission_decision(self):
        decision = admit_route_proposal(
            self.intake(required_capabilities=("planning_report", "future_unknown_capability"))
        )

        self.assertFalse(decision.accepted)
        self.assertEqual(decision.route_admission, "rejected")
        self.assertIn("unknown_required_capabilities", decision.blocked_conditions)
        self.assertEqual(decision.capability_assessment["unknown_capabilities"], ["future_unknown_capability"])
        self.assertEqual(decision.next_boundary_kind, "reject_or_reframe")

    def test_blocked_external_capabilities_produce_separate_boundary_behavior(self):
        decision = admit_route_proposal(
            self.intake(
                "research_request",
                required_capabilities=("web_research",),
                allowed_to_use_web=True,
                recommended_next_action="request_future_web_lookup_boundary",
                caveats=("web_lookup_not_implemented",),
            )
        )

        self.assertFalse(decision.accepted)
        self.assertIn("blocked_or_external_required_capabilities", decision.blocked_conditions)
        self.assertEqual(decision.capability_assessment["blocked_or_external_capabilities"], ["web_research"])
        self.assertEqual(decision.next_boundary_kind, "separate_boundary_required")

    def test_needs_clarification_input_does_not_execute_and_emits_ask_clarification(self):
        decision = admit_route_proposal(
            self.intake(
                "needs_clarification",
                required_capabilities=(),
                missing_inputs=("target_document",),
                confidence=0.4,
                recommended_next_action="ask_operator_for_missing_target_document",
            )
        )

        self.assertFalse(decision.accepted)
        self.assertEqual(decision.route_admission, "needs_clarification")
        self.assertEqual(decision.next_boundary_kind, "ask_clarification")
        self.assertFalse(decision.execution_authority)
        self.assertTrue(all(flag is False for flag in decision.activity_flags.values()))

    def test_unsupported_connector_input_emits_external_boundary_required(self):
        decision = admit_route_proposal(
            self.intake(
                "unsupported_or_requires_connector",
                required_capabilities=("external_connector",),
                requires_external_connector=True,
                recommended_next_action="explain_connector_requirement_to_operator",
            )
        )

        self.assertFalse(decision.accepted)
        self.assertEqual(decision.route_admission, "rejected")
        self.assertEqual(decision.next_boundary_kind, "external_boundary_required")
        self.assertIn("external_connector", decision.capability_assessment["blocked_or_external_capabilities"])
        self.assertFalse(decision.execution_authority)

    def test_raw_unclassified_request_text_is_not_inferred_into_route(self):
        decision = admit_route_proposal(
            {
                "request_id": "raw_phase111",
                "raw_prompt": "Please figure out what route this should be and do it.",
            }
        )

        self.assertEqual(decision.request_id, "raw_phase111")
        self.assertEqual(decision.route_admission, "needs_clarification")
        self.assertEqual(decision.next_boundary_kind, "ask_clarification")
        self.assertEqual(decision.candidate_proposal_state, "not_proposed")
        self.assertIn("structured_route_fields_required", decision.missing_requirements)
        self.assertIn("raw_or_unclassified_request_was_not_inferred", decision.non_proofs)

    def test_provider_model_runtime_platform_worker_substrate_smuggling_is_blocked(self):
        decision = admit_route_proposal(
            self.intake(
                "planning_request",
                execution_policy="execute with Codex as provider",
                recommended_next_action="handled by OpenClaw runtime",
            )
        )

        self.assertFalse(decision.accepted)
        self.assertEqual(decision.route_admission, "rejected")
        self.assertEqual(decision.next_boundary_kind, "reject_or_reframe")
        self.assertIn("route_proposal_substrate_smuggling_blocked", decision.blocked_conditions)
        self.assertIn("substrate_specific_smuggling_detected", decision.non_proofs)

    def test_no_activity_flags_remain_false_and_statement_is_present(self):
        decision = admit_route_proposal(self.intake())

        self.assertIn("no mutation", decision.activity_statement)
        self.assertIn("provider", decision.activity_statement)
        self.assertTrue(all(flag is False for flag in decision.activity_flags.values()))

    def test_route_proposal_source_does_not_import_forbidden_execution_libraries(self):
        source = inspect.getsource(route_proposal)

        for forbidden in (
            "import requests",
            "import subprocess",
            "import openai",
            "import ollama",
            "import discord",
            "from orchestrator.provider",
            "from orchestrator.platform",
            "from orchestrator.connector",
            "from orchestrator.scheduler",
        ):
            self.assertNotIn(forbidden, source)

    def test_admission_decision_preserves_proposal_validation_admission_execution_distinctions(self):
        decision = admit_route_proposal(self.intake())

        self.assertEqual(decision.candidate_proposal_state, "candidate_route_proposed")
        self.assertEqual(decision.validated_envelope_state, "validated_envelope_metadata_only")
        self.assertEqual(decision.accepted_route_state, "accepted_route_without_execution_authority")
        self.assertFalse(decision.execution_authority)
        self.assertIn("candidate_route_proposal_is_not_authorization", decision.non_proofs)
        self.assertIn("validated_route_envelope_is_not_execution", decision.non_proofs)
        self.assertIn("accepted_route_is_not_execution_authority", decision.non_proofs)


if __name__ == "__main__":
    unittest.main()
