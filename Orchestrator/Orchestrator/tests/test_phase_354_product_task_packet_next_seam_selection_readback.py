import unittest
from pathlib import Path

from orchestrator.product_task_packet_next_seam_selection_readback import (
    BOUNDARY,
    MARKER,
    RECOMMENDED_NEXT_BOUNDARY,
    read_product_task_packet_next_seam_selection_readback,
)


PHASE_354_MARKER_TEXT = (
    "PHASE354_PRODUCT_TASK_PACKET_NEXT_SEAM_SELECTION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS"
)


class Phase354ProductTaskPacketNextSeamSelectionReadbackTests(unittest.TestCase):
    def test_function_exists_and_returns_deterministic_equal_structures(self):
        first = read_product_task_packet_next_seam_selection_readback()
        second = read_product_task_packet_next_seam_selection_readback()

        self.assertEqual(first, second)
        self.assertEqual(first["phase"], 354)
        self.assertEqual(first["boundary"], BOUNDARY)
        self.assertEqual(first["marker"], MARKER)

    def test_phase_349_phase_351_and_phase_352_source_basis_is_preserved(self):
        readback = read_product_task_packet_next_seam_selection_readback()
        basis = readback["source_basis"]

        expected = {
            "phase_349": (
                "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS",
                "PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS_PROVEN=PASS",
                "orchestrator/product_task_packet_operator_report.py",
            ),
            "phase_351": (
                "PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS",
                "PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS",
                "orchestrator/product_task_packet_negative_edge.py",
            ),
            "phase_352": (
                "PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS",
                "PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS",
                "orchestrator/product_task_packet_operator_decision_readback.py",
            ),
        }
        for key, (boundary, marker, source_file) in expected.items():
            self.assertEqual(basis[key]["boundary"], boundary)
            self.assertEqual(basis[key]["marker"], marker)
            self.assertEqual(basis[key]["source_file"], source_file)

    def test_completed_packet_spine_includes_phases_349_351_and_352(self):
        readback = read_product_task_packet_next_seam_selection_readback()

        for spine_item in (
            "report_surface_phase_349",
            "negative_edge_contract_phase_351",
            "operator_decision_readback_phase_352",
        ):
            self.assertIn(spine_item, readback["completed_packet_spine"])

    def test_eligible_next_seams_include_required_candidates(self):
        readback = read_product_task_packet_next_seam_selection_readback()
        seam_ids = {seam["seam_id"] for seam in readback["eligible_next_seams"]}

        for seam_id in (
            "packet_lifecycle_state_readback",
            "routing_contract_readback",
            "patch_workflow_contract_readback",
            "worker_dispatch_contract_readback",
            "provider_policy_readback",
            "domain_general_intake_readback",
            "handoff_packet_readback",
        ):
            self.assertIn(seam_id, seam_ids)

        for seam in readback["eligible_next_seams"]:
            for field in (
                "seam_id",
                "posture",
                "allowed_operations",
                "excluded_operations",
                "required_preconditions",
                "proof_required",
                "non_proofs",
                "recommended_order",
            ):
                self.assertIn(field, seam)

    def test_blocked_or_deferred_seams_include_required_lockouts(self):
        readback = read_product_task_packet_next_seam_selection_readback()

        for blocked in (
            "runtime/provider/model/platform execution",
            "service/API/UI/dashboard/auth/deployment",
            "live business-data access",
            "live mutation",
            "adapter execution",
            "general_answer resumption",
            "Source Files refresh",
            "capsule/export/package refresh",
            "production execution",
        ):
            self.assertIn(blocked, readback["blocked_or_deferred_seams"])

    def test_recommended_next_boundary_is_lifecycle_state_readback(self):
        readback = read_product_task_packet_next_seam_selection_readback()

        self.assertEqual(
            readback["recommended_next_boundary"],
            "PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS",
        )
        self.assertEqual(readback["recommended_next_boundary"], RECOMMENDED_NEXT_BOUNDARY)

    def test_selection_rules_preserve_ordering_and_separate_authorization(self):
        readback = read_product_task_packet_next_seam_selection_readback()

        for rule in (
            "choose lifecycle before routing",
            "choose routing contract before routing implementation",
            "choose provider policy before provider/model execution",
            "choose handoff when context saturation appears",
            "require separate push/ref verification after local commit",
            "require separate capsule-proof boundary for official capsule claims",
        ):
            self.assertIn(rule, readback["selection_rules"])

    def test_stop_conditions_include_lockouts_and_overclaim_states(self):
        readback = read_product_task_packet_next_seam_selection_readback()

        for stop_condition in (
            "runtime/provider/model/platform request",
            "service/API/UI/dashboard/auth/deployment request",
            "general_answer resumption request",
            "worker dispatch request without worker boundary",
            "patch application request without patch boundary",
            "provider execution request without provider boundary",
            "source/capsule/Git truth conflation",
            "proof overclaim",
            "context saturation/handoff needed",
        ):
            self.assertIn(stop_condition, readback["stop_conditions"])

    def test_all_false_activity_flags_exist_and_are_false(self):
        readback = read_product_task_packet_next_seam_selection_readback()
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
        readback = read_product_task_packet_next_seam_selection_readback()

        for caveat in (
            "seam selection readback is not execution",
            "candidate seam eligibility is not implementation",
            "recommended next boundary is not authorization for later seams",
            "worker PASS is evidence, not coordinator ratification",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
            "Git repo truth is distinct from Source Files handoff snapshots",
            "official clean capsule proof remains separate",
            "Phase 335 remains accepted capsule proof unless explicitly superseded",
        ):
            self.assertIn(caveat, readback["required_report_caveats"])

    def test_source_capsule_git_truth_separation_is_explicit(self):
        readback = read_product_task_packet_next_seam_selection_readback()
        separation = readback["source_capsule_git_truth_separation"]

        self.assertIn("Git repo truth", separation)
        self.assertIn("Source Files handoff snapshots", separation)
        self.assertIn("official clean product capsule proofs", separation)
        self.assertIn("full Git repo backups including .git", separation)
        self.assertIn("Phase 335", separation["official clean product capsule proofs"])

    def test_marker_appears_in_source_test_and_docs(self):
        repo_root = Path(__file__).resolve().parents[1]

        for relative_path in (
            "orchestrator/product_task_packet_next_seam_selection_readback.py",
            "tests/test_phase_354_product_task_packet_next_seam_selection_readback.py",
            "docs/PHASE_354.md",
        ):
            text = (repo_root / relative_path).read_text(encoding="utf-8")
            self.assertIn(PHASE_354_MARKER_TEXT, text)


if __name__ == "__main__":
    unittest.main()
