import unittest

from orchestrator.manual_review_cli import build_manual_review_cli_output
from orchestrator.manual_review_runner import run_named_fixture_review, run_structured_intake_review
from orchestrator.route_proposal import RequestIntakeRecord


FORBIDDEN_EXECUTION_CLAIMS = (
    "provider_executed=true",
    "model_executed=true",
    "worker_dispatched=true",
    "codex_dispatched=true",
    "route_execution=true",
    "production_readiness=true",
)


def _intake(request_id: str, request_type: str, required_capabilities: tuple[str, ...], **overrides):
    values = {
        "request_id": request_id,
        "observed_request_summary": "Phase 123 router policy manual review integration intake.",
        "request_type": request_type,
        "confidence": 0.9,
        "required_capabilities": required_capabilities,
        "missing_inputs": (),
        "risk_level": "low",
        "execution_policy": "phase_123_manual_review_only",
        "recommended_next_action": "review_router_policy_posture",
        "requires_operator_confirmation": False,
        "requires_external_connector": False,
        "allowed_to_answer_directly": False,
        "allowed_to_mutate_files": False,
        "allowed_to_schedule": False,
        "allowed_to_use_local_documents": False,
        "allowed_to_use_web": False,
        "reasoning_summary_for_operator": "Router policy posture only; no execution.",
        "caveats": (),
        "intake_source": "phase_123_test_structured_intake",
    }
    values.update(overrides)
    return RequestIntakeRecord(**values)


class Phase123ModelRouterPolicyManualReviewIntegrationContractTests(unittest.TestCase):
    def assert_no_activity(self, result):
        self.assertTrue(all(flag is False for flag in result.no_activity_flags.values()))
        text = result.review_text.lower()
        for forbidden in FORBIDDEN_EXECUTION_CLAIMS:
            self.assertNotIn(forbidden, text)

    def assert_router_text(self, text: str, *expected: str):
        self.assertIn("Router Policy", text)
        for item in expected:
            self.assertIn(item, text)

    def test_safe_direct_answer_renders_local_first_router_posture(self):
        result = run_named_fixture_review("safe_direct_answer")

        self.assertEqual(result.router_policy_recommendation["recommended_route"], "local_first_answer")
        self.assertEqual(
            result.router_policy_recommendation["provider_posture"],
            "local_first_when_authorized_no_provider_executed",
        )
        self.assert_router_text(
            result.review_text,
            "recommended_route=local_first_answer",
            "provider_posture=local_first_when_authorized_no_provider_executed",
        )
        self.assertIn("router_policy_is_not_provider_execution", result.non_proofs)
        self.assertIn("router_policy_is_not_model_execution", result.non_proofs)
        self.assert_no_activity(result)

    def test_coding_fixture_renders_worker_boundary_without_dispatch(self):
        result = run_named_fixture_review("safe_coding_source_test_mutation")

        self.assertEqual(result.router_policy_recommendation["recommended_route"], "worker_codex_boundary")
        self.assertEqual(result.router_policy_recommendation["required_boundary"], "bounded_worker_codex_boundary")
        self.assert_router_text(
            result.review_text,
            "recommended_route=worker_codex_boundary",
            "required_boundary=bounded_worker_codex_boundary",
        )
        self.assertFalse(result.no_activity_flags["worker_dispatched"])
        self.assert_no_activity(result)

    def test_local_document_intake_renders_rag_boundary_without_lookup(self):
        result = run_structured_intake_review(
            _intake(
                "phase123_local_docs",
                "local_document_lookup",
                ("local_document_lookup",),
                allowed_to_use_local_documents=True,
            )
        )

        self.assertEqual(result.router_policy_recommendation["recommended_route"], "rag_local_document_boundary")
        self.assertIn("rag_lookup_not_executed", result.router_policy_recommendation["blocked_conditions"])
        self.assert_router_text(result.review_text, "recommended_route=rag_local_document_boundary")
        self.assertFalse(result.no_activity_flags["rag_lookup_performed"])
        self.assert_no_activity(result)

    def test_reminder_intake_renders_scheduler_boundary_without_scheduling(self):
        result = run_structured_intake_review(
            _intake(
                "phase123_reminder",
                "reminder_request",
                ("scheduling_contract",),
                allowed_to_schedule=True,
                requires_operator_confirmation=True,
            )
        )

        self.assertEqual(result.router_policy_recommendation["recommended_route"], "scheduler_reminder_boundary")
        self.assertIn("scheduler_not_executed", result.router_policy_recommendation["blocked_conditions"])
        self.assert_router_text(result.review_text, "recommended_route=scheduler_reminder_boundary")
        self.assertFalse(result.no_activity_flags["scheduler_executed"])
        self.assert_no_activity(result)

    def test_web_research_intake_renders_web_boundary_without_web_lookup(self):
        result = run_structured_intake_review(
            _intake(
                "phase123_web",
                "research_request",
                ("web_research",),
                allowed_to_use_web=True,
                caveats=("web_lookup_not_implemented",),
            )
        )

        self.assertEqual(result.router_policy_recommendation["recommended_route"], "web_research_boundary")
        self.assertIn("web_lookup_not_executed", result.router_policy_recommendation["blocked_conditions"])
        self.assert_router_text(result.review_text, "recommended_route=web_research_boundary")
        self.assertFalse(result.no_activity_flags["web_lookup_performed"])
        self.assert_no_activity(result)

    def test_provider_platform_fixture_requires_separate_boundary_without_selection(self):
        result = run_named_fixture_review("platform_provider_external_boundary")

        self.assertEqual(
            result.router_policy_recommendation["recommended_route"],
            "separate_provider_or_platform_boundary_required",
        )
        self.assertEqual(
            result.router_policy_recommendation["provider_posture"],
            "provider_model_runtime_platform_not_selected",
        )
        self.assert_router_text(
            result.review_text,
            "recommended_route=separate_provider_or_platform_boundary_required",
            "provider_posture=provider_model_runtime_platform_not_selected",
        )
        self.assertFalse(result.no_activity_flags["provider_executed"])
        self.assertFalse(result.no_activity_flags["model_executed"])
        self.assertFalse(result.no_activity_flags["runtime_executed"])
        self.assertFalse(result.no_activity_flags["platform_executed"])
        self.assert_no_activity(result)

    def test_production_execution_fixture_remains_blocked(self):
        result = run_named_fixture_review("production_execution_blocked")

        self.assertEqual(result.router_policy_recommendation["recommended_route"], "block")
        self.assertIn("production_execution_blocked", result.blocked_conditions)
        self.assertIn("production_execution_blocked", result.router_policy_recommendation["blocked_conditions"])
        self.assert_router_text(result.review_text, "recommended_route=block")
        self.assert_no_activity(result)

    def test_cli_rendered_text_preserves_router_policy_and_existing_sections(self):
        result = build_manual_review_cli_output(["--fixture", "safe_direct_answer"])

        self.assertEqual(result.exit_code, 0)
        for section in (
            "Assessment",
            "Accepted Facts",
            "Decision",
            "Router Policy",
            "NBM",
            "Deliverable/Command",
            "RESPONSE_METADATA",
        ):
            self.assertIn(section, result.output_text)
        self.assertIn("recommended_route=local_first_answer", result.output_text)
        for forbidden in FORBIDDEN_EXECUTION_CLAIMS:
            self.assertNotIn(forbidden, result.output_text.lower())

    def test_report_non_proofs_include_router_policy_non_proofs(self):
        result = run_named_fixture_review("safe_direct_answer")

        for non_proof in (
            "router_policy_is_not_provider_execution",
            "router_policy_is_not_model_execution",
            "router_policy_is_not_live_router",
            "router_policy_is_not_worker_dispatch",
            "router_policy_is_not_route_execution",
            "router_policy_is_not_rag_lookup",
            "router_policy_is_not_web_lookup",
            "router_policy_is_not_scheduler_execution",
            "router_policy_is_not_production_readiness",
        ):
            self.assertIn(non_proof, result.non_proofs)


if __name__ == "__main__":
    unittest.main()
