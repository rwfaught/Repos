import unittest
from pathlib import Path

import orchestrator.product_task_packet_operator_decision_readback as module
from orchestrator.product_task_packet_operator_decision_readback import (
    BOUNDARY,
    MARKER,
    PHASE_349_MARKER,
    PHASE_351_MARKER,
    read_product_task_packet_operator_decision_readback,
)


PHASE_352_MARKER_TEXT = (
    "PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
)


class Phase352ProductTaskPacketOperatorDecisionReadbackTests(unittest.TestCase):
    def test_function_exists_and_returns_deterministic_equal_structures(self):
        first = read_product_task_packet_operator_decision_readback()
        second = read_product_task_packet_operator_decision_readback()

        self.assertEqual(first, second)
        self.assertEqual(first["phase"], 352)
        self.assertEqual(first["boundary"], BOUNDARY)
        self.assertEqual(first["marker"], MARKER)

    def test_phase_349_and_phase_351_source_basis_is_preserved(self):
        readback = read_product_task_packet_operator_decision_readback()
        basis = readback["source_basis"]

        self.assertEqual(basis["phase_349"]["phase"], 349)
        self.assertEqual(
            basis["phase_349"]["source_file"],
            "orchestrator/product_task_packet_operator_report.py",
        )
        self.assertEqual(basis["phase_349"]["marker"], PHASE_349_MARKER)
        self.assertEqual(basis["phase_351"]["phase"], 351)
        self.assertEqual(
            basis["phase_351"]["source_file"],
            "orchestrator/product_task_packet_negative_edge.py",
        )
        self.assertEqual(basis["phase_351"]["marker"], PHASE_351_MARKER)

    def test_allowed_operator_decisions_include_required_states(self):
        readback = read_product_task_packet_operator_decision_readback()

        for decision in (
            "proceed_to_bounded_mutation",
            "request_read_only_seam_selection",
            "stop_missing_boundary",
            "stop_missing_allowlist",
            "stop_runtime_provider_model_platform_lockout",
            "stop_service_api_ui_dashboard_auth_deployment_lockout",
            "stop_general_answer_lockout",
            "stop_worker_dispatch_boundary_missing",
            "stop_patch_application_boundary_missing",
            "stop_proof_overclaim",
            "stop_source_capsule_git_truth_conflation",
            "stop_context_saturation_handoff_needed",
        ):
            self.assertIn(decision, readback["allowed_operator_decisions"])

    def test_decision_requirements_include_boundary_authorization_and_handoff(self):
        readback = read_product_task_packet_operator_decision_readback()

        for requirement in (
            "exact boundary required",
            "allowed file list required before mutation",
            "validation plan required before commit",
            "push requires separate authorization",
            "capsule/export/package refresh requires separate authorization",
            "runtime/provider/model/platform work requires separate authorization",
            "service/API/UI/dashboard/auth/deployment work requires separate authorization",
            "worker dispatch requires separate explicit worker boundary",
            "patch application requires separate explicit patch boundary",
            "context saturation requires handoff rather than scope expansion",
        ):
            self.assertIn(requirement, readback["decision_requirements"])

    def test_stop_conditions_include_lockouts_and_overclaim_states(self):
        readback = read_product_task_packet_operator_decision_readback()

        for stop_condition in (
            "missing boundary",
            "missing allowlist",
            "requested out-of-allowlist mutation",
            "requested runtime/provider/model/platform execution",
            "requested service/API/UI/dashboard/auth/deployment work",
            "requested general_answer resumption",
            "requested worker dispatch without worker boundary",
            "requested patch application without patch boundary",
            "proof overclaim",
            "source/capsule/Git truth conflation",
            "context saturation/handoff needed",
        ):
            self.assertIn(stop_condition, readback["stop_conditions"])

    def test_all_false_activity_flags_exist_and_are_false(self):
        readback = read_product_task_packet_operator_decision_readback()
        flags = readback["false_activity_flags"]

        for flag in (
            "runtime_provider_model_platform_executed",
            "service_api_ui_dashboard_auth_deployment_work",
            "general_answer_resumed",
            "worker_dispatched",
            "patch_applied",
            "live_task_created",
            "live_task_executed",
            "live_mutation",
            "live_business_data_access",
            "adapter_execution",
            "real_domain_execution",
            "source_files_refreshed",
            "capsule_export_package_refreshed",
            "semantic_correctness_proven",
            "production_readiness_proven",
            "autonomous_ai_coding_authority",
        ):
            self.assertIn(flag, flags)
            self.assertFalse(flags[flag])

    def test_required_report_caveats_preserve_non_proof_doctrine(self):
        readback = read_product_task_packet_operator_decision_readback()

        for caveat in (
            "operator decision readback is not task execution",
            "decision state is not live enforcement",
            "worker PASS is evidence, not coordinator ratification",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
            "Git repo truth is distinct from Source Files handoff snapshots",
            "official clean capsule proof remains separate",
            "Phase 335 remains accepted capsule proof unless explicitly superseded",
        ):
            self.assertIn(caveat, readback["required_report_caveats"])

    def test_source_capsule_git_truth_separation_is_explicit(self):
        readback = read_product_task_packet_operator_decision_readback()
        separation = readback["source_capsule_git_truth_separation"]

        self.assertIn("Git repo truth", separation)
        self.assertIn("Source Files handoff snapshots", separation)
        self.assertIn("official clean product capsule proofs", separation)
        self.assertIn("full Git repo backups including .git", separation)
        self.assertIn("Phase 335", separation["official clean product capsule proofs"])

    def test_surface_does_not_claim_forbidden_behavior_or_proofs(self):
        readback = read_product_task_packet_operator_decision_readback()
        flags = readback["false_activity_flags"]

        self.assertFalse(flags["runtime_provider_model_platform_executed"])
        self.assertFalse(flags["service_api_ui_dashboard_auth_deployment_work"])
        self.assertFalse(flags["worker_dispatched"])
        self.assertFalse(flags["patch_applied"])
        self.assertFalse(flags["live_mutation"])
        self.assertFalse(flags["semantic_correctness_proven"])
        self.assertFalse(flags["production_readiness_proven"])
        self.assertFalse(flags["capsule_export_package_refreshed"])

        for caveat in (
            "does_not_create_cli_parser_runner_dispatcher_behavior",
            "does_not_create_service_api_ui_dashboard_auth_deployment_behavior",
            "does_not_parse_live_packets",
            "does_not_execute_live_tasks",
            "does_not_dispatch_workers",
            "does_not_apply_patches",
            "does_not_resume_general_answer",
            "does_not_extend_official_capsule_proof_beyond_phase_335",
        ):
            self.assertIn(caveat, readback["forbidden_surface_caveats"])

    def test_module_does_not_expose_live_behavior_surfaces(self):
        for forbidden_name in (
            "main",
            "parse",
            "parse_packet",
            "dispatch",
            "dispatch_worker",
            "run",
            "runner",
            "validate_live_task",
            "validate_live_packet",
            "cli",
            "apply_patch",
            "execute",
        ):
            self.assertFalse(hasattr(module, forbidden_name))

    def test_next_safe_seam_doctrine_proves_no_later_surface(self):
        readback = read_product_task_packet_operator_decision_readback()

        for later_seam in (
            "routing",
            "patch workflow",
            "worker dispatch",
            "provider policy",
            "domain-general intake",
        ):
            self.assertTrue(
                any(later_seam in item for item in readback["next_safe_seam_doctrine"])
            )
            self.assertTrue(
                any("proves no" in item for item in readback["next_safe_seam_doctrine"])
            )

    def test_marker_appears_in_source_test_and_docs(self):
        repo_root = Path(__file__).resolve().parents[1]

        for relative_path in (
            "orchestrator/product_task_packet_operator_decision_readback.py",
            "tests/test_phase_352_product_task_packet_operator_decision_readback.py",
            "docs/PHASE_352.md",
        ):
            text = (repo_root / relative_path).read_text(encoding="utf-8")
            self.assertIn(MARKER, text)


if __name__ == "__main__":
    unittest.main()
