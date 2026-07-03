import unittest

from orchestrator.backbone_v0_proof_chain_operator_index import (
    BOUNDARY,
    MARKER,
    read_backbone_v0_proof_chain_operator_index,
)


class Phase340BackboneV0ProofChainOperatorIndexTests(unittest.TestCase):
    def test_operator_index_exists_and_is_deterministic(self):
        first = read_backbone_v0_proof_chain_operator_index()
        second = read_backbone_v0_proof_chain_operator_index()

        self.assertEqual(first, second)
        self.assertEqual(first["phase"], 340)
        self.assertEqual(first["boundary"], BOUNDARY)
        self.assertEqual(first["marker"], MARKER)

    def test_phase_337_and_338_facts_are_preserved(self):
        index = read_backbone_v0_proof_chain_operator_index()

        self.assertEqual(
            index["declaration_boundary"],
            "PHASE337_BACKBONE_V0_DECLARATION_SOURCE_TEST_DOCS_ONLY",
        )
        self.assertEqual(
            index["declaration_marker"],
            "PHASE337_BACKBONE_V0_DECLARATION_SOURCE_TEST_DOCS_PROVEN=PASS",
        )
        self.assertEqual(
            index["phase_337_fork_point_commit"],
            "12e70023d638c0f919aa8e00e50ceccfaf36a6de",
        )
        self.assertEqual(
            index["phase_338_boundary"],
            "PHASE338_BACKBONE_V0_DECLARATION_READBACK_OPERATOR_STATUS_SOURCE_TEST_DOCS",
        )
        self.assertEqual(
            index["phase_338_marker"],
            "PHASE338_BACKBONE_V0_DECLARATION_READBACK_OPERATOR_STATUS_SOURCE_TEST_DOCS_PROVEN=PASS",
        )
        self.assertEqual(
            index["phase_338_commit"],
            "3d322fcb7d04ca8655d4234816a990e4ea6d24cb",
        )

    def test_phase_335_capsule_reference_is_present(self):
        index = read_backbone_v0_proof_chain_operator_index()
        capsule = index["phase_335_official_clean_capsule_proof"]

        self.assertEqual(
            capsule["phase"],
            "PHASE335_BACKBONE_V0_OFFICIAL_CLEAN_CAPSULE_PROOF_SOURCE_DOCS",
        )
        self.assertEqual(
            capsule["sha256"],
            "04cb5a2205bedcef767d8cab6344237e9b4ce1f75f19793a56425ab8b197d49d",
        )
        self.assertEqual(capsule["entry_count"], 1001)
        self.assertEqual(capsule["git_entry_count"], 0)
        self.assertEqual(capsule["pycache_pyc_entry_count"], 0)

    def test_ordered_proof_chain_includes_expected_phases(self):
        index = read_backbone_v0_proof_chain_operator_index()
        phases = [entry["phase"] for entry in index["ordered_proof_chain_phases"]]

        self.assertEqual(
            phases,
            [
                316,
                317,
                318,
                319,
                320,
                322,
                323,
                324,
                326,
                327,
                328,
                331,
                332,
                333,
                335,
                337,
                338,
                340,
            ],
        )
        descriptions = {
            entry["phase"]: entry["description"]
            for entry in index["ordered_proof_chain_phases"]
        }
        self.assertEqual(descriptions[316], "neutral Backbone scaffold")
        self.assertEqual(descriptions[335], "official clean capsule proof")
        self.assertEqual(
            descriptions[340], "Backbone V0 proof-chain operator index"
        )

    def test_read_only_assessment_phases_are_separate(self):
        index = read_backbone_v0_proof_chain_operator_index()

        self.assertEqual(
            index["read_only_assessment_phases"],
            [321, 325, 329, 330, 334, 336, 339],
        )
        proof_phases = {
            entry["phase"] for entry in index["ordered_proof_chain_phases"]
        }
        for phase in index["read_only_assessment_phases"]:
            self.assertNotIn(phase, proof_phases)

    def test_non_proofs_preserve_forbidden_scope(self):
        index = read_backbone_v0_proof_chain_operator_index()

        for non_proof in (
            "not_semantic_correctness",
            "not_production_readiness",
            "not_autonomous_ai_coding",
            "not_provider_model_runtime_platform_execution",
            "not_service_api_ui_dashboard_auth_deployment_readiness",
            "not_live_obsidian_pkms_access",
            "not_live_business_data_access",
            "not_real_domain_execution",
            "not_adapter_execution",
            "not_fixture_mappings_as_live_integrations",
            "not_general_answer_resumption",
            "not_openclaw_hermes_lightrag_discord_installer_behavior",
        ):
            self.assertIn(non_proof, index["non_proofs"])

        for forbidden_claim in (
            "semantic_correctness",
            "production_readiness",
            "autonomous_ai_coding",
            "provider_model_runtime_platform_execution",
            "service_api_ui_dashboard_auth_deployment_readiness",
            "live_obsidian_pkms_access",
            "live_business_data_access",
            "real_domain_execution",
            "adapter_execution",
            "fixture_mappings_as_live_integrations",
            "general_answer_resumption",
            "openclaw_hermes_lightrag_discord_installer_behavior",
            "future_phases_already_completed",
            "official_capsule_proof_beyond_phase_335_record",
        ):
            self.assertIn(forbidden_claim, index["forbidden_claims"])

    def test_execution_flags_remain_false(self):
        index = read_backbone_v0_proof_chain_operator_index()

        for flag_value in index["execution_flags"].values():
            self.assertFalse(flag_value)

    def test_forbidden_claims_are_not_converted_to_true_claims(self):
        index = read_backbone_v0_proof_chain_operator_index()

        for forbidden_claim in index["forbidden_claims"]:
            claimed_flag = f"{forbidden_claim}_claimed"
            if claimed_flag in index["execution_flags"]:
                self.assertFalse(index["execution_flags"][claimed_flag])

        self.assertIn("does_not_expand_product_capability", index["operator_caveats"])
        self.assertIn("does_not_resume_general_answer", index["operator_caveats"])
        self.assertIn(
            "does_not_refresh_capsules_exports_or_packages",
            index["operator_caveats"],
        )

    def test_source_capsule_git_truth_separation_caveat_is_present(self):
        index = read_backbone_v0_proof_chain_operator_index()
        caveat = index["source_capsule_separation_caveat"]

        self.assertIn("git_repo_truth", caveat)
        self.assertIn("source_files_handoff_snapshots", caveat)
        self.assertIn("official_clean_product_capsule_proofs", caveat)
        self.assertIn("full_git_repo_backups_including_git", caveat)
        self.assertIn("Git repository", caveat["git_repo_truth"])
        self.assertIn("may lag", caveat["source_files_handoff_snapshots"])
        self.assertIn("Phase 335", caveat["official_clean_product_capsule_proofs"])


if __name__ == "__main__":
    unittest.main()
