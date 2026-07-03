import unittest

import orchestrator.product_task_packet_negative_edge as module
from orchestrator.product_task_packet_negative_edge import (
    BOUNDARY,
    MARKER,
    PHASE_349_MARKER,
    read_product_task_packet_negative_edge_contract,
)


class Phase351ProductTaskPacketNegativeEdgeContractTests(unittest.TestCase):
    def test_function_exists_and_returns_deterministic_structure(self):
        first = read_product_task_packet_negative_edge_contract()
        second = read_product_task_packet_negative_edge_contract()

        self.assertEqual(first, second)
        self.assertEqual(first["phase"], 351)
        self.assertEqual(first["boundary"], BOUNDARY)
        self.assertEqual(first["marker"], MARKER)

    def test_phase_349_source_basis_is_preserved(self):
        contract = read_product_task_packet_negative_edge_contract()
        basis = contract["source_basis"]

        self.assertEqual(basis["phase"], 349)
        self.assertEqual(
            basis["source_file"],
            "orchestrator/product_task_packet_operator_report.py",
        )
        self.assertEqual(basis["marker"], PHASE_349_MARKER)

    def test_contract_posture_says_packets_are_not_execution_authority(self):
        contract = read_product_task_packet_negative_edge_contract()

        self.assertIn("planning/report artifacts", contract["contract_posture"])
        self.assertIn("not execution authority", contract["contract_posture"])

    def test_disallowed_packet_claims_are_represented(self):
        contract = read_product_task_packet_negative_edge_contract()

        for claim in (
            "semantic correctness proven",
            "production readiness proven",
            "autonomous AI coding authority granted",
            "runtime/provider/model/platform execution occurred",
            "service/API/UI/dashboard/auth/deployment readiness proven",
            "live Obsidian/PKMS/business-data access occurred",
            "live mutation occurred",
            "adapter execution occurred",
            "real domain execution occurred",
            "fixture mapping is live integration",
            "general_answer resumed",
            "OpenClaw/Hermes/LightRAG/Discord/installer behavior proven",
            "official capsule proof extended beyond Phase 335",
        ):
            self.assertIn(claim, contract["disallowed_packet_claims"])

    def test_disallowed_packet_actions_are_represented(self):
        contract = read_product_task_packet_negative_edge_contract()

        for action in (
            "execute runtime/provider/model/platform paths",
            "run WSL/Ollama/OpenClaw/Hermes/LightRAG/Discord/installer work",
            "resume general_answer",
            "create service/API/UI/dashboard/auth/deployment work",
            "dispatch workers",
            "apply patches",
            "mutate files without exact allowlist",
            "commit without validation",
            "push without separate authorization",
            "refresh capsule/export/package without separate authorization",
            "broaden into unrelated files or cleanup",
        ):
            self.assertIn(action, contract["disallowed_packet_actions"])

    def test_required_stop_conditions_are_represented(self):
        contract = read_product_task_packet_negative_edge_contract()

        for stop_condition in (
            "missing exact boundary",
            "missing allowed-file list for mutation",
            "requested mutation outside allowlist",
            "requested runtime/provider/model/platform execution",
            "requested service/API/UI/dashboard/auth/deployment work",
            "requested general_answer resumption",
            "requested worker dispatch without explicit worker boundary",
            "requested patch application without explicit patch boundary",
            "requested capsule/export/package refresh",
            "claimed proof exceeds inspected evidence",
            "output blurs accepted facts and inference",
        ):
            self.assertIn(stop_condition, contract["required_stop_conditions"])

    def test_all_required_false_flags_exist_and_are_false(self):
        contract = read_product_task_packet_negative_edge_contract()
        flags = contract["required_false_flags"]

        for flag in (
            "runtime_provider_model_platform_executed",
            "service_api_ui_dashboard_auth_deployment_work",
            "general_answer_resumed",
            "live_business_data_access",
            "live_mutation",
            "adapter_execution",
            "real_domain_execution",
            "fixture_as_live_integration",
            "production_readiness_proven",
            "semantic_correctness_proven",
            "autonomous_ai_coding_authority",
            "capsule_export_package_refreshed",
        ):
            self.assertIn(flag, flags)
            self.assertFalse(flags[flag])

    def test_required_report_caveats_are_represented(self):
        contract = read_product_task_packet_negative_edge_contract()

        for caveat in (
            "worker PASS is evidence, not coordinator ratification",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
            "fixture is not live integration",
            "readback/report surface is not runtime behavior",
            "product task packet is not task execution",
            "negative-edge contract is not live enforcement",
            "Git repo truth is distinct from Source Files handoff snapshots",
            "official clean capsule proof remains separate",
        ):
            self.assertIn(caveat, contract["required_report_caveats"])

    def test_next_safe_seam_doctrine_is_represented(self):
        contract = read_product_task_packet_negative_edge_contract()

        for later_seam in (
            "operator decision/readback",
            "routing",
            "patch workflow",
            "worker dispatch",
            "provider policy",
            "domain-general intake",
        ):
            self.assertTrue(
                any(later_seam in item for item in contract["next_safe_seam_doctrine"])
            )

    def test_source_capsule_git_truth_separation_is_represented(self):
        contract = read_product_task_packet_negative_edge_contract()
        caveat = contract["source_capsule_git_truth_separation_caveat"]

        self.assertIn("Git repo truth", caveat)
        self.assertIn("Source Files handoff snapshots", caveat)
        self.assertIn("official clean product capsule proofs", caveat)
        self.assertIn("full Git repo backups including .git", caveat)
        self.assertIn("Phase 335", caveat["official clean product capsule proofs"])

    def test_contract_does_not_claim_forbidden_proofs(self):
        contract = read_product_task_packet_negative_edge_contract()
        flags = contract["required_false_flags"]

        self.assertFalse(flags["runtime_provider_model_platform_executed"])
        self.assertFalse(flags["service_api_ui_dashboard_auth_deployment_work"])
        self.assertFalse(flags["production_readiness_proven"])
        self.assertFalse(flags["semantic_correctness_proven"])
        self.assertFalse(flags["autonomous_ai_coding_authority"])
        self.assertFalse(flags["general_answer_resumed"])
        self.assertFalse(flags["fixture_as_live_integration"])
        self.assertFalse(flags["capsule_export_package_refreshed"])

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
        ):
            self.assertFalse(hasattr(module, forbidden_name))

        contract = read_product_task_packet_negative_edge_contract()
        for caveat in (
            "not_a_validator_parser_dispatcher_runner_cli_service_or_live_task_harness",
            "does_not_parse_live_packets",
            "does_not_validate_live_tasks",
            "does_not_create_or_execute_product_tasks",
            "does_not_dispatch_workers",
            "does_not_apply_patches",
        ):
            self.assertIn(caveat, contract["forbidden_surface_caveats"])


if __name__ == "__main__":
    unittest.main()
