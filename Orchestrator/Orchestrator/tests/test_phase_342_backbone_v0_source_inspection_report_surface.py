import unittest

from orchestrator.backbone_v0_source_inspection_report import (
    BOUNDARY,
    MARKER,
    read_backbone_v0_source_inspection_report,
)


class Phase342BackboneV0SourceInspectionReportSurfaceTests(unittest.TestCase):
    def test_report_surface_exists_and_is_deterministic(self):
        first = read_backbone_v0_source_inspection_report()
        second = read_backbone_v0_source_inspection_report()

        self.assertEqual(first, second)
        self.assertEqual(first["phase"], 342)
        self.assertEqual(first["boundary"], BOUNDARY)
        self.assertEqual(first["marker"], MARKER)

    def test_report_references_three_source_surfaces(self):
        report = read_backbone_v0_source_inspection_report()
        surfaces = report["source_surfaces_inspected"]
        names = {surface["name"] for surface in surfaces}

        self.assertEqual(len(surfaces), 3)
        self.assertIn("Backbone V0 declaration", names)
        self.assertIn("Backbone V0 declaration operator status", names)
        self.assertIn("Backbone V0 proof-chain operator index", names)

        for surface in surfaces:
            self.assertTrue(surface["present"])
            self.assertTrue(surface["expected_marker_preserved"])
            self.assertTrue(surface["expected_non_proofs_preserved"])
            self.assertTrue(surface["execution_flags_remain_false"])

    def test_commit_reference_facts_are_preserved(self):
        report = read_backbone_v0_source_inspection_report()
        refs = report["accepted_commit_reference_facts"]

        self.assertEqual(
            refs["phase_337_fork_point_commit"],
            "12e70023d638c0f919aa8e00e50ceccfaf36a6de",
        )
        self.assertEqual(
            refs["phase_338_commit"],
            "3d322fcb7d04ca8655d4234816a990e4ea6d24cb",
        )
        self.assertEqual(
            refs["phase_340_commit"],
            "e629a49920d6933dba5c95c952e353955fc71e4f",
        )

    def test_phase_335_capsule_reference_is_present_and_caveated(self):
        report = read_backbone_v0_source_inspection_report()
        capsule = report["phase_335_capsule_proof_reference"]

        self.assertEqual(
            capsule["reference"]["phase"],
            "PHASE335_BACKBONE_V0_OFFICIAL_CLEAN_CAPSULE_PROOF_SOURCE_DOCS",
        )
        self.assertEqual(
            capsule["reference"]["sha256"],
            "04cb5a2205bedcef767d8cab6344237e9b4ce1f75f19793a56425ab8b197d49d",
        )
        self.assertEqual(capsule["reference"]["entry_count"], 1001)
        self.assertIn("only the accepted Phase 335", capsule["caveat"])
        self.assertIn("does not refresh capsules", capsule["caveat"])

    def test_phase_337_338_and_340_markers_are_preserved(self):
        report = read_backbone_v0_source_inspection_report()
        markers = report["preserved_markers"]

        self.assertEqual(
            markers["phase_337_marker"],
            "PHASE337_BACKBONE_V0_DECLARATION_SOURCE_TEST_DOCS_PROVEN=PASS",
        )
        self.assertEqual(
            markers["phase_338_marker"],
            "PHASE338_BACKBONE_V0_DECLARATION_READBACK_OPERATOR_STATUS_SOURCE_TEST_DOCS_PROVEN=PASS",
        )
        self.assertEqual(
            markers["phase_340_marker"],
            "PHASE340_BACKBONE_V0_PROOF_CHAIN_OPERATOR_INDEX_SOURCE_TEST_DOCS_PROVEN=PASS",
        )

    def test_ordered_proof_chain_and_assessment_phases_are_preserved(self):
        report = read_backbone_v0_source_inspection_report()
        phases = [
            entry["phase"]
            for entry in report["ordered_proof_chain_phase_summary"]
        ]

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
        self.assertEqual(
            report["read_only_assessment_phase_summary"],
            [321, 325, 329, 330, 334, 336, 339],
        )

    def test_non_proofs_preserve_forbidden_scope(self):
        report = read_backbone_v0_source_inspection_report()

        for non_proof in (
            "not_semantic_correctness",
            "not_production_readiness",
            "not_autonomous_ai_coding",
            "not_provider_model_runtime_platform_execution",
            "not_service_api_ui_dashboard_auth_deployment_readiness",
            "not_live_obsidian_pkms_access",
            "not_live_business_data_access",
            "not_adapter_execution",
            "not_real_domain_execution",
            "not_general_answer_resumption",
            "not_openclaw_hermes_lightrag_discord_installer_behavior",
        ):
            self.assertIn(non_proof, report["non_proofs"])

        for forbidden_claim in (
            "future_phases_already_completed",
            "official_capsule_proof_beyond_phase_335_record",
        ):
            self.assertIn(forbidden_claim, report["forbidden_claims"])

    def test_execution_flags_remain_false(self):
        report = read_backbone_v0_source_inspection_report()

        for flag_value in report["execution_flags"].values():
            self.assertFalse(flag_value)

    def test_forbidden_claims_are_not_converted_to_true_claims(self):
        report = read_backbone_v0_source_inspection_report()

        for forbidden_claim in report["forbidden_claims"]:
            claimed_flag = f"{forbidden_claim}_claimed"
            if claimed_flag in report["execution_flags"]:
                self.assertFalse(report["execution_flags"][claimed_flag])

        self.assertIn(
            "does_not_expand_product_capability",
            report["next_operator_caveats"],
        )
        self.assertIn(
            "does_not_replace_phase_340_operator_index",
            report["next_operator_caveats"],
        )

    def test_source_capsule_git_truth_separation_caveat_is_present(self):
        report = read_backbone_v0_source_inspection_report()
        caveat = report["source_capsule_git_truth_separation_caveat"]

        self.assertIn("git_repo_truth", caveat)
        self.assertIn("source_files_handoff_snapshots", caveat)
        self.assertIn("official_clean_product_capsule_proofs", caveat)
        self.assertIn("full_git_repo_backups_including_git", caveat)

    def test_report_does_not_claim_execution_or_product_surface_work(self):
        report = read_backbone_v0_source_inspection_report()
        scope = report["report_surface_scope"]

        self.assertTrue(scope["report_surface_only"])
        for key in (
            "second_declaration",
            "phase_340_replacement",
            "runtime_execution",
            "provider_execution",
            "model_execution",
            "platform_execution",
            "git_execution",
            "file_read_execution",
            "subprocess_execution",
            "service_api_ui_dashboard_auth_deployment_behavior",
            "general_answer_resumption",
        ):
            self.assertFalse(scope[key])


if __name__ == "__main__":
    unittest.main()
