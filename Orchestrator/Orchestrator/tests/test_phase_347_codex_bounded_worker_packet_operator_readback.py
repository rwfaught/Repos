import unittest

from orchestrator.codex_bounded_worker_packet_readback import (
    BOUNDARY,
    MARKER,
    PHASE_345_MARKER,
    read_codex_bounded_worker_packet_operator_readback,
)


class Phase347CodexBoundedWorkerPacketOperatorReadbackTests(unittest.TestCase):
    def test_function_exists_and_returns_deterministic_structure(self):
        first = read_codex_bounded_worker_packet_operator_readback()
        second = read_codex_bounded_worker_packet_operator_readback()

        self.assertEqual(first, second)
        self.assertEqual(first["phase"], 347)
        self.assertEqual(first["boundary"], BOUNDARY)
        self.assertEqual(first["marker"], MARKER)

    def test_phase_345_source_basis_is_preserved(self):
        readback = read_codex_bounded_worker_packet_operator_readback()

        self.assertEqual(readback["source_basis"]["phase"], 345)
        self.assertEqual(readback["source_basis"]["marker"], PHASE_345_MARKER)
        self.assertEqual(
            readback["source_basis"]["document"],
            "docs/CODEX_BOUNDED_AUTONOMY_PROMPT_SURFACE.md",
        )

    def test_required_packet_fields_are_represented(self):
        readback = read_codex_bounded_worker_packet_operator_readback()

        for field in (
            "SESSION ROLE",
            "BOUNDARY",
            "PURPOSE",
            "ACTIVE CONTEXT",
            "AUTHORITY",
            "ALLOWED FILES",
            "LOCKOUTS",
            "REQUIRED DESIGN",
            "TEST/DOC REQUIREMENTS",
            "VALIDATION COMMAND BATCH REQUIREMENT",
            "CHANGED-FILE ALLOWLIST AUDIT",
            "COMMIT AUTHORIZATION",
            "PUSH AUTHORIZATION",
            "STOP CONDITIONS",
            "REPORT FORMAT",
        ):
            self.assertIn(field, readback["required_packet_fields"])

    def test_role_separation_is_represented(self):
        readback = read_codex_bounded_worker_packet_operator_readback()
        roles = readback["role_separation"]

        self.assertIn("roger_owner_operator", roles)
        self.assertIn("cto_coordinator_protocol_keeper", roles)
        self.assertIn("codex_bounded_worker", roles)
        self.assertIn("relay_operator_command_batches", roles)
        self.assertIn("ratifies", roles["cto_coordinator_protocol_keeper"])
        self.assertIn("authorized packet boundary", roles["codex_bounded_worker"])

    def test_boundary_modes_are_represented(self):
        readback = read_codex_bounded_worker_packet_operator_readback()

        for mode in (
            "read-only",
            "docs-only mutation",
            "source/test/docs mutation",
            "ref-only preservation",
            "push/ref verification",
        ):
            self.assertIn(mode, readback["boundary_modes"])

    def test_mutation_authority_rules_are_represented(self):
        readback = read_codex_bounded_worker_packet_operator_readback()

        for value in readback["mutation_authority_rules"].values():
            self.assertTrue(value)

    def test_timestamp_rule_is_represented(self):
        readback = read_codex_bounded_worker_packet_operator_readback()
        rule = readback["timestamp_rule"]

        self.assertTrue(rule["command_script_batches_require_start_timestamp"])
        self.assertTrue(rule["command_script_batches_require_end_timestamp"])
        self.assertTrue(rule["command_script_batches_require_elapsed_time"])

    def test_validation_expectations_are_represented(self):
        readback = read_codex_bounded_worker_packet_operator_readback()
        expectations = readback["validation_expectations"]

        for expected in (
            "targeted compile/check commands when source changes are authorized",
            "targeted unit tests when test/source changes are authorized",
            "marker search",
            "changed-file allowlist audit",
            "git diff --check",
            "git status --short --branch",
        ):
            self.assertIn(expected, expectations)

    def test_report_shapes_are_represented(self):
        readback = read_codex_bounded_worker_packet_operator_readback()
        shapes = readback["report_shapes"]

        self.assertIn("mutation_report_fields", shapes)
        self.assertIn("read_only_assessment_report_fields", shapes)
        self.assertIn("push_ref_verification_report_fields", shapes)
        self.assertIn("CHANGED FILES", shapes["mutation_report_fields"])
        self.assertIn(
            "NO CHANGES MADE CONFIRMATION",
            shapes["read_only_assessment_report_fields"],
        )
        self.assertIn("REMOTE STATUS", shapes["push_ref_verification_report_fields"])

    def test_standing_lockouts_and_non_proof_doctrine_are_represented(self):
        readback = read_codex_bounded_worker_packet_operator_readback()

        self.assertIn(
            "No runtime/provider/model/platform execution.",
            readback["standing_lockouts"],
        )
        self.assertIn("No general_answer resumption.", readback["standing_lockouts"])

        for doctrine in (
            "worker PASS is evidence, not coordinator ratification",
            "test PASS is not semantic correctness",
            "pushed commit is not production readiness",
            "fixture is not live integration",
            "readback/report surface is not runtime behavior",
            "Codex bounded work is not autonomous AI coding",
        ):
            self.assertIn(doctrine, readback["non_proof_doctrine"])

    def test_false_execution_flags_remain_false(self):
        readback = read_codex_bounded_worker_packet_operator_readback()

        for value in readback["false_execution_flags"].values():
            self.assertFalse(value)

    def test_source_capsule_git_truth_separation_caveat_is_present(self):
        readback = read_codex_bounded_worker_packet_operator_readback()
        caveat = readback["source_capsule_git_truth_separation_caveat"]

        self.assertIn("Git repo truth", caveat)
        self.assertIn("Source Files handoff snapshots", caveat)
        self.assertIn("official clean product capsule proofs", caveat)
        self.assertIn("full Git repo backups including .git", caveat)

    def test_no_forbidden_claims_are_made(self):
        readback = read_codex_bounded_worker_packet_operator_readback()
        flags = readback["false_execution_flags"]

        for forbidden_flag in (
            "runtime_provider_model_platform_execution",
            "service_api_ui_dashboard_auth_deployment",
            "production_readiness",
            "semantic_correctness",
            "autonomous_coding_authority",
            "general_answer_resumed",
            "live_integration",
        ):
            self.assertFalse(flags[forbidden_flag])

        for caveat in (
            "not_a_parser_runner_dispatcher_cli_service_or_live_worker_harness",
            "does_not_execute_codex_or_worker_agents",
        ):
            self.assertIn(caveat, readback["next_operator_caveats"])


if __name__ == "__main__":
    unittest.main()
