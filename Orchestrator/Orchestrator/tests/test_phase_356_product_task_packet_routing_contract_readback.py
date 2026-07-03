import unittest
from pathlib import Path

from orchestrator.product_task_packet_routing_contract_readback import (
    BOUNDARY,
    MARKER,
    RECOMMENDED_NEXT_BOUNDARY,
    read_product_task_packet_routing_contract_readback,
)


PHASE_356_MARKER_TEXT = (
    "PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
)


class Phase356ProductTaskPacketRoutingContractReadbackTests(unittest.TestCase):
    def test_function_exists_and_returns_deterministic_equal_structures(self):
        first = read_product_task_packet_routing_contract_readback()
        second = read_product_task_packet_routing_contract_readback()

        self.assertEqual(first, second)
        self.assertEqual(first["phase"], 356)
        self.assertEqual(first["boundary"], BOUNDARY)
        self.assertEqual(first["marker"], MARKER)

    def test_source_basis_preserves_prior_packet_spine_phases(self):
        readback = read_product_task_packet_routing_contract_readback()
        basis = readback["source_basis"]

        expected = {
            "phase_349": "orchestrator/product_task_packet_operator_report.py",
            "phase_351": "orchestrator/product_task_packet_negative_edge.py",
            "phase_352": "orchestrator/product_task_packet_operator_decision_readback.py",
            "phase_354": "orchestrator/product_task_packet_next_seam_selection_readback.py",
            "phase_355": "orchestrator/product_task_packet_lifecycle_state_readback.py",
        }
        for phase_key, source_file in expected.items():
            self.assertIn("boundary", basis[phase_key])
            self.assertIn("marker", basis[phase_key])
            self.assertEqual(basis[phase_key]["source_file"], source_file)

    def test_completed_packet_spine_includes_required_phases(self):
        readback = read_product_task_packet_routing_contract_readback()

        for spine_item in (
            "report_surface_phase_349",
            "negative_edge_contract_phase_351",
            "operator_decision_readback_phase_352",
            "next_seam_selection_readback_phase_354",
            "lifecycle_state_readback_phase_355",
        ):
            self.assertIn(spine_item, readback["completed_packet_spine"])

    def test_route_contracts_include_required_ids_and_fields(self):
        readback = read_product_task_packet_routing_contract_readback()
        routes = {route["route_id"]: route for route in readback["route_contracts"]}

        for route_id in (
            "route_to_read_only_review",
            "route_to_bounded_source_test_docs_mutation",
            "route_to_coordinator_review",
            "route_to_push_ref_verification",
            "route_to_handoff",
            "route_to_stop_missing_boundary",
            "route_to_stop_missing_allowlist",
            "route_to_stop_lockout",
            "route_to_stop_proof_overclaim",
            "route_to_stop_source_capsule_git_truth_conflation",
            "route_to_stop_context_saturation",
            "route_to_deferred_patch_workflow_contract",
            "route_to_deferred_worker_dispatch_contract",
            "route_to_deferred_provider_policy_contract",
            "route_to_deferred_domain_general_intake_contract",
            "route_to_deferred_runtime_provider_execution",
        ):
            self.assertIn(route_id, routes)

        for route in routes.values():
            for field in (
                "route_id",
                "description",
                "eligible_from_lifecycle_states",
                "required_preconditions",
                "required_evidence",
                "allowed_operations",
                "excluded_operations",
                "stop_conditions",
                "non_proofs",
            ):
                self.assertIn(field, route)

    def test_routing_gates_include_required_boundaries(self):
        readback = read_product_task_packet_routing_contract_readback()

        for gate in (
            "exact boundary declared",
            "file allowlist declared",
            "source basis preserved",
            "lifecycle state known",
            "validation plan present",
            "changed-file audit available",
            "coordinator review before push",
            "remote-before check before push",
            "handoff when context saturation appears",
            "separate boundary for patch workflow",
            "separate boundary for worker dispatch",
            "separate boundary for provider policy",
            "separate boundary for provider/model execution",
            "separate boundary for Source Files refresh",
            "separate boundary for official capsule proof",
        ):
            self.assertIn(gate, readback["routing_gates"])

    def test_blocked_routes_include_required_lockouts(self):
        readback = read_product_task_packet_routing_contract_readback()

        for route_id in (
            "route_to_runtime_provider_model_platform_execution",
            "route_to_service_api_ui_dashboard_auth_deployment",
            "route_to_live_business_data_access",
            "route_to_live_obsidian_pkms_access",
            "route_to_live_mutation",
            "route_to_adapter_execution",
            "route_to_real_domain_execution",
            "route_to_general_answer_resumption",
            "route_to_worker_dispatch_without_boundary",
            "route_to_patch_application_without_boundary",
            "route_to_provider_execution_without_boundary",
            "route_to_source_files_refresh_as_capsule_proof",
            "route_to_capsule_export_package_without_boundary",
            "route_to_production_execution",
        ):
            self.assertIn(route_id, readback["blocked_routes"])

    def test_routing_doctrine_preserves_non_proof_ordering(self):
        readback = read_product_task_packet_routing_contract_readback()

        for doctrine in (
            "readback precedes route execution",
            "lifecycle state precedes route eligibility",
            "routing contract precedes routing implementation",
            "coordinator review precedes push/ref verification",
            "remote-before check precedes push",
            "pushed commit does not prove production readiness",
            "test PASS does not prove semantic correctness",
            "worker PASS is evidence, not coordinator ratification",
            "Source Files refresh is not official capsule proof",
            "Phase 335 remains accepted capsule proof unless explicitly superseded",
            "context saturation routes to handoff, not scope expansion",
        ):
            self.assertIn(doctrine, readback["routing_doctrine"])

    def test_invalid_route_claims_reject_overclaims(self):
        readback = read_product_task_packet_routing_contract_readback()

        for claim in (
            "route contract means routing implementation exists",
            "route eligibility means route execution occurred",
            "route to worker means worker dispatch occurred",
            "route to patch means patch application occurred",
            "route to provider means provider/model execution occurred",
            "route to review means coordinator ratified",
            "route to push means push was performed",
            "route to Source Files means capsule proof",
            "test PASS means semantic correctness",
            "pushed commit means production readiness",
            "source snapshot means Git truth",
            "capsule snapshot means live system readiness",
        ):
            self.assertIn(claim, readback["invalid_route_claims"])

    def test_stop_conditions_include_required_states(self):
        readback = read_product_task_packet_routing_contract_readback()

        for stop_condition in (
            "unknown lifecycle state",
            "dirty working tree",
            "remote-before mismatch",
            "proof overclaim",
            "source/capsule/Git truth conflation",
        ):
            self.assertIn(stop_condition, readback["stop_conditions"])

    def test_all_false_activity_flags_exist_and_are_false(self):
        readback = read_product_task_packet_routing_contract_readback()
        flags = readback["false_activity_flags"]

        for flag in (
            "runtime_provider_model_platform_executed",
            "service_api_ui_dashboard_auth_deployment_work",
            "general_answer_resumed",
            "worker_dispatched",
            "patch_applied",
            "routing_implemented",
            "route_selection_executed",
            "provider_policy_implemented",
            "domain_general_intake_implemented",
            "lifecycle_transition_executed",
            "live_task_created",
            "live_task_executed",
            "live_mutation",
            "live_business_data_access",
            "live_obsidian_pkms_access",
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
        readback = read_product_task_packet_routing_contract_readback()

        for caveat in (
            "routing contract readback is not route execution",
            "route eligibility is not routing implementation",
            "route contract is not runtime enforcement",
            "worker PASS is evidence, not coordinator ratification",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
            "Git repo truth is distinct from Source Files handoff snapshots",
            "official clean capsule proof remains separate",
            "Phase 335 remains accepted capsule proof unless explicitly superseded",
        ):
            self.assertIn(caveat, readback["required_report_caveats"])

    def test_source_capsule_git_truth_separation_is_explicit(self):
        readback = read_product_task_packet_routing_contract_readback()
        separation = readback["source_capsule_git_truth_separation"]

        self.assertIn("Git repo truth", separation)
        self.assertIn("Source Files handoff snapshots", separation)
        self.assertIn("official clean product capsule proofs", separation)
        self.assertIn("full Git repo backups including .git", separation)
        self.assertIn("Phase 335", separation["official clean product capsule proofs"])

    def test_recommended_next_boundary_is_patch_workflow_contract_readback(self):
        readback = read_product_task_packet_routing_contract_readback()

        self.assertEqual(
            readback["recommended_next_boundary"],
            "PHASE357_PRODUCT_TASK_PACKET_PATCH_WORKFLOW_CONTRACT_READBACK_SOURCE_TEST_DOCS",
        )
        self.assertEqual(readback["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)

    def test_marker_appears_in_source_test_and_docs(self):
        repo_root = Path(__file__).resolve().parents[1]

        for relative_path in (
            "orchestrator/product_task_packet_routing_contract_readback.py",
            "tests/test_phase_356_product_task_packet_routing_contract_readback.py",
            "docs/PHASE_356.md",
        ):
            text = (repo_root / relative_path).read_text(encoding="utf-8")
            self.assertIn(PHASE_356_MARKER_TEXT, text)


if __name__ == "__main__":
    unittest.main()
