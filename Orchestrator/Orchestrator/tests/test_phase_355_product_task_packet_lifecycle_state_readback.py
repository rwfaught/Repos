import unittest
from pathlib import Path

from orchestrator.product_task_packet_lifecycle_state_readback import (
    BOUNDARY,
    MARKER,
    RECOMMENDED_NEXT_BOUNDARY,
    read_product_task_packet_lifecycle_state_readback,
)


PHASE_355_MARKER_TEXT = (
    "PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
)


class Phase355ProductTaskPacketLifecycleStateReadbackTests(unittest.TestCase):
    def test_function_exists_and_returns_deterministic_equal_structures(self):
        first = read_product_task_packet_lifecycle_state_readback()
        second = read_product_task_packet_lifecycle_state_readback()

        self.assertEqual(first, second)
        self.assertEqual(first["phase"], 355)
        self.assertEqual(first["boundary"], BOUNDARY)
        self.assertEqual(first["marker"], MARKER)

    def test_source_basis_preserves_prior_packet_spine_phases(self):
        readback = read_product_task_packet_lifecycle_state_readback()
        basis = readback["source_basis"]

        expected = {
            "phase_349": "orchestrator/product_task_packet_operator_report.py",
            "phase_351": "orchestrator/product_task_packet_negative_edge.py",
            "phase_352": "orchestrator/product_task_packet_operator_decision_readback.py",
            "phase_354": "orchestrator/product_task_packet_next_seam_selection_readback.py",
        }
        for phase_key, source_file in expected.items():
            self.assertIn("boundary", basis[phase_key])
            self.assertIn("marker", basis[phase_key])
            self.assertEqual(basis[phase_key]["source_file"], source_file)

    def test_completed_packet_spine_includes_required_phases(self):
        readback = read_product_task_packet_lifecycle_state_readback()

        for spine_item in (
            "report_surface_phase_349",
            "negative_edge_contract_phase_351",
            "operator_decision_readback_phase_352",
            "next_seam_selection_readback_phase_354",
        ):
            self.assertIn(spine_item, readback["completed_packet_spine"])

    def test_lifecycle_states_include_all_required_states_and_fields(self):
        readback = read_product_task_packet_lifecycle_state_readback()
        states = {state["state_id"]: state for state in readback["lifecycle_states"]}

        for state_id in (
            "packet_unformed",
            "boundary_declared",
            "allowlist_declared",
            "source_basis_declared",
            "read_only_review_pending",
            "mutation_authorized",
            "mutation_in_progress",
            "validation_pending",
            "local_commit_authorized",
            "local_commit_created",
            "coordinator_review_pending",
            "push_ref_verify_authorized",
            "remote_ref_verified",
            "handoff_required",
            "blocked_by_missing_boundary",
            "blocked_by_missing_allowlist",
            "blocked_by_lockout",
            "blocked_by_proof_overclaim",
            "blocked_by_source_capsule_git_truth_conflation",
            "blocked_by_context_saturation",
            "complete_for_current_boundary",
        ):
            self.assertIn(state_id, states)

        for state in states.values():
            for field in (
                "state_id",
                "description",
                "allowed_next_states",
                "blocked_next_states",
                "required_evidence",
                "non_proofs",
                "allowed_operations",
                "excluded_operations",
            ):
                self.assertIn(field, state)

    def test_transition_doctrine_preserves_ordering_and_authorization(self):
        readback = read_product_task_packet_lifecycle_state_readback()

        for doctrine in (
            "boundary_declared requires allowlist before mutation",
            "allowlist_declared requires source basis before implementation",
            "validation_pending must precede local_commit_authorized",
            "coordinator_review_pending must precede push_ref_verify_authorized",
            "remote-ref verification does not prove production readiness",
            "context saturation must route to handoff_required",
            "Source Files refresh requires separate authorization",
            "capsule/export/package proof requires separate authorization",
            "runtime/provider/model/platform work requires separate authorization",
        ):
            self.assertIn(doctrine, readback["transition_doctrine"])

    def test_invalid_transitions_include_non_proof_doctrine(self):
        readback = read_product_task_packet_lifecycle_state_readback()

        for invalid_transition in (
            "worker_pass_as_coordinator_ratification",
            "test_pass_as_semantic_correctness",
            "source_files_refresh_as_capsule_proof",
            "push_without_coordinator_review",
            "validation_pending_to_push",
            "remote_ref_verified_to_production_ready",
        ):
            self.assertIn(invalid_transition, readback["invalid_transitions"])

    def test_lifecycle_gates_include_required_gates(self):
        readback = read_product_task_packet_lifecycle_state_readback()

        for gate in (
            "exact boundary",
            "file allowlist",
            "validation",
            "marker search",
            "changed-file audit",
            "coordinator review",
            "push/ref verification",
            "handoff",
            "capsule-proof separation",
        ):
            self.assertIn(gate, readback["lifecycle_gates"])

    def test_stop_conditions_include_lockouts_and_dirty_tree_states(self):
        readback = read_product_task_packet_lifecycle_state_readback()

        for stop_condition in (
            "runtime/provider/model/platform request",
            "service/API/UI/dashboard/auth/deployment request",
            "general_answer resumption request",
            "dirty working tree",
            "remote-before mismatch",
            "source/capsule/Git truth conflation",
            "proof overclaim",
            "context saturation/handoff needed",
        ):
            self.assertIn(stop_condition, readback["stop_conditions"])

    def test_all_false_activity_flags_exist_and_are_false(self):
        readback = read_product_task_packet_lifecycle_state_readback()
        flags = readback["false_activity_flags"]

        for flag in (
            "runtime_provider_model_platform_executed",
            "service_api_ui_dashboard_auth_deployment_work",
            "general_answer_resumed",
            "worker_dispatched",
            "patch_applied",
            "routing_implemented",
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
        readback = read_product_task_packet_lifecycle_state_readback()

        for caveat in (
            "lifecycle state readback is not transition execution",
            "lifecycle eligibility is not implementation",
            "transition doctrine is not runtime enforcement",
            "worker PASS is evidence, not coordinator ratification",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
            "Git repo truth is distinct from Source Files handoff snapshots",
            "official clean capsule proof remains separate",
            "Phase 335 remains accepted capsule proof unless explicitly superseded",
        ):
            self.assertIn(caveat, readback["required_report_caveats"])

    def test_source_capsule_git_truth_separation_is_explicit(self):
        readback = read_product_task_packet_lifecycle_state_readback()
        separation = readback["source_capsule_git_truth_separation"]

        self.assertIn("Git repo truth", separation)
        self.assertIn("Source Files handoff snapshots", separation)
        self.assertIn("official clean product capsule proofs", separation)
        self.assertIn("full Git repo backups including .git", separation)
        self.assertIn("Phase 335", separation["official clean product capsule proofs"])

    def test_recommended_next_boundary_is_routing_contract_readback(self):
        readback = read_product_task_packet_lifecycle_state_readback()

        self.assertEqual(
            readback["recommended_next_boundary"],
            "PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS",
        )
        self.assertEqual(readback["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)

    def test_marker_appears_in_source_test_and_docs(self):
        repo_root = Path(__file__).resolve().parents[1]

        for relative_path in (
            "orchestrator/product_task_packet_lifecycle_state_readback.py",
            "tests/test_phase_355_product_task_packet_lifecycle_state_readback.py",
            "docs/PHASE_355.md",
        ):
            text = (repo_root / relative_path).read_text(encoding="utf-8")
            self.assertIn(PHASE_355_MARKER_TEXT, text)


if __name__ == "__main__":
    unittest.main()
