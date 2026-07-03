import unittest

from orchestrator.product_task_packet_operator_report import (
    BOUNDARY,
    MARKER,
    PHASE_347_MARKER,
    PHASE_348_BOUNDARY,
    read_product_task_packet_operator_report,
)


class Phase349ProductTaskPacketOperatorReportSurfaceTests(unittest.TestCase):
    def test_function_exists_and_returns_deterministic_structure(self):
        first = read_product_task_packet_operator_report()
        second = read_product_task_packet_operator_report()

        self.assertEqual(first, second)
        self.assertEqual(first["phase"], 349)
        self.assertEqual(first["boundary"], BOUNDARY)
        self.assertEqual(first["marker"], MARKER)

    def test_phase_347_and_phase_348_source_basis_is_preserved(self):
        report = read_product_task_packet_operator_report()
        basis = report["source_basis"]

        self.assertEqual(basis["phase_347_marker"], PHASE_347_MARKER)
        self.assertEqual(basis["phase_348_boundary"], PHASE_348_BOUNDARY)
        self.assertIn(
            "Phase 347 bounded Codex worker packet operator readback",
            basis["dependencies"],
        )
        self.assertIn(
            "Phase 348 post-Backbone V0 read-only seam selection",
            basis["dependencies"],
        )

    def test_product_task_packet_fields_are_operator_legible(self):
        report = read_product_task_packet_operator_report()

        for field_name in (
            "task_packet_id",
            "boundary",
            "mode",
            "operator_intent",
            "accepted_facts",
            "inference",
            "allowed_files",
            "lockouts",
            "validation_plan",
            "stop_conditions",
            "report_metadata",
            "non_proofs_to_preserve",
        ):
            self.assertIn(field_name, report["product_task_packet_fields"])

    def test_required_response_shape_is_preserved(self):
        report = read_product_task_packet_operator_report()

        for section in (
            "Assessment",
            "Accepted Facts",
            "Decision",
            "NBM",
            "Deliverable/Command",
            "RESPONSE_METADATA",
        ):
            self.assertIn(section, report["report_sections"])

    def test_accepted_fact_and_inference_separation_is_explicit(self):
        report = read_product_task_packet_operator_report()
        separation = report["accepted_fact_inference_separation"]

        self.assertTrue(separation["accepted_facts_required"])
        self.assertTrue(separation["inference_must_be_marked"])
        self.assertTrue(separation["worker_report_is_not_coordinator_acceptance"])
        self.assertTrue(separation["test_pass_is_not_semantic_correctness"])

    def test_operator_legibility_requirements_are_explicit(self):
        report = read_product_task_packet_operator_report()
        legibility = report["operator_legibility"]

        self.assertTrue(legibility["nbm_required"])
        self.assertTrue(legibility["decision_required"])
        self.assertTrue(legibility["deliverable_or_command_required"])
        self.assertTrue(legibility["response_metadata_required"])
        self.assertTrue(legibility["changed_files_must_match_allowed_files"])

    def test_standing_lockouts_are_preserved(self):
        report = read_product_task_packet_operator_report()

        for lockout in (
            "No runtime/provider/model/platform execution.",
            "No WSL/Ollama/OpenClaw/Hermes/LightRAG/Discord/installer execution.",
            "No service/API/UI/dashboard/auth/deployment work.",
            "No general_answer resumption.",
            "No Source Files refresh, capsule refresh, export/package refresh, or official capsule proof extension.",
            "No semantic-correctness, autonomous-AI-coding, live-domain-execution, or production-readiness claims.",
            "No unrelated files.",
        ):
            self.assertIn(lockout, report["standing_lockouts"])

    def test_validation_expectations_are_targeted(self):
        report = read_product_task_packet_operator_report()

        for expectation in (
            "git status --short --branch",
            "python -m py_compile orchestrator/product_task_packet_operator_report.py",
            "python -m unittest tests.test_phase_349_product_task_packet_operator_report_surface",
            "marker search",
            "non-proof and lockout text search",
            "git diff --check",
            "changed-file allowlist audit",
        ):
            self.assertIn(expectation, report["validation_expectations"])

    def test_false_activity_flags_remain_false(self):
        report = read_product_task_packet_operator_report()

        for value in report["false_activity_flags"].values():
            self.assertFalse(value)

    def test_non_proofs_include_current_lockout_claims(self):
        report = read_product_task_packet_operator_report()

        for non_proof in (
            "not_semantic_correctness",
            "not_production_readiness",
            "not_autonomous_ai_coding",
            "not_provider_model_runtime_platform_execution",
            "not_service_api_ui_dashboard_auth_deployment_readiness",
            "not_general_answer_resumption",
            "not_official_capsule_proof_beyond_phase_335",
        ):
            self.assertIn(non_proof, report["non_proofs"])

    def test_source_capsule_git_truth_separation_is_preserved(self):
        report = read_product_task_packet_operator_report()
        caveat = report["source_capsule_git_truth_separation_caveat"]

        self.assertIn("Git repo truth", caveat)
        self.assertIn("Source Files handoff snapshots", caveat)
        self.assertIn("official clean product capsule proofs", caveat)
        self.assertIn("full Git repo backups including .git", caveat)
        self.assertIn("Phase 335", caveat["official clean product capsule proofs"])

    def test_surface_does_not_claim_execution_or_dispatch(self):
        report = read_product_task_packet_operator_report()
        flags = report["false_activity_flags"]

        for forbidden_flag in (
            "task_created",
            "task_mutated",
            "task_executed",
            "worker_dispatched",
            "codex_agent_executed",
            "provider_model_runtime_platform_execution",
            "service_api_ui_dashboard_auth_deployment_behavior",
            "general_answer_resumed",
            "source_files_capsule_export_package_refreshed",
            "semantic_correctness_claimed",
            "production_readiness_claimed",
            "autonomous_ai_coding_claimed",
            "live_domain_execution_claimed",
        ):
            self.assertFalse(flags[forbidden_flag])

        for caveat in (
            "operator_report_surface_only",
            "not_a_parser_runner_dispatcher_cli_service_or_live_worker_harness",
            "does_not_create_or_execute_product_tasks",
        ):
            self.assertIn(caveat, report["next_operator_caveats"])


if __name__ == "__main__":
    unittest.main()
