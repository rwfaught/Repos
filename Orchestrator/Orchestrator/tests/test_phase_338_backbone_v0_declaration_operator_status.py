import unittest

from orchestrator.backbone_code_patching_adapter_mapping import (
    read_code_patching_backbone_operator_readback,
)
from orchestrator.backbone_pkms_note_fixture_mapping import (
    read_pkms_note_fixture_backbone_operator_readback,
)
from orchestrator.backbone_research_claim_fixture_mapping import (
    read_research_claim_fixture_backbone_operator_readback,
)
from orchestrator.backbone_v0_declaration_operator_status import (
    BOUNDARY,
    MARKER,
    read_backbone_v0_declaration_operator_status,
)


class Phase338BackboneV0DeclarationOperatorStatusTests(unittest.TestCase):
    def test_operator_status_is_deterministic(self):
        first = read_backbone_v0_declaration_operator_status()
        second = read_backbone_v0_declaration_operator_status()

        self.assertEqual(first, second)
        self.assertEqual(first["phase"], 338)
        self.assertEqual(first["boundary"], BOUNDARY)
        self.assertEqual(first["marker"], MARKER)

    def test_references_phase_337_declaration_boundary_and_marker(self):
        status = read_backbone_v0_declaration_operator_status()

        self.assertEqual(
            status["declaration_boundary"],
            "PHASE337_BACKBONE_V0_DECLARATION_SOURCE_TEST_DOCS_ONLY",
        )
        self.assertEqual(
            status["declaration_marker"],
            "PHASE337_BACKBONE_V0_DECLARATION_SOURCE_TEST_DOCS_PROVEN=PASS",
        )
        self.assertEqual(
            status["source_of_truth"],
            "orchestrator.backbone_v0_declaration.read_backbone_v0_declaration_status",
        )

    def test_reports_narrow_structural_declaration(self):
        status = read_backbone_v0_declaration_operator_status()

        self.assertTrue(status["backbone_v0_declared"])
        self.assertIn("source/test/docs structural milestone", status["declared_claim"])
        self.assertIn("source/test/docs structural milestone", status["operator_summary"])
        self.assertIn("domain_neutral_backbone_scaffold_exists", status["declaration_scope"])
        self.assertIn("not_production_readiness", status["non_proofs"])

    def test_preserves_phase_335_capsule_proof_exactly(self):
        status = read_backbone_v0_declaration_operator_status()
        capsule = status["official_capsule_proof"]

        self.assertEqual(
            capsule["sha256"],
            "04cb5a2205bedcef767d8cab6344237e9b4ce1f75f19793a56425ab8b197d49d",
        )
        self.assertEqual(capsule["entry_count"], 1001)
        self.assertEqual(capsule["git_entry_count"], 0)
        self.assertEqual(capsule["pycache_pyc_entry_count"], 0)

    def test_preserves_non_proofs_and_forbidden_claims(self):
        status = read_backbone_v0_declaration_operator_status()

        for claim in (
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
        ):
            self.assertIn(claim, status["forbidden_claims"])

        self.assertIn("does_not_resume_general_answer", status["operator_caveats"])
        self.assertIn(
            "does_not_extend_official_capsule_proof_beyond_phase_335_record",
            status["operator_caveats"],
        )

    def test_execution_flags_remain_false(self):
        status = read_backbone_v0_declaration_operator_status()
        flags = status["execution_flags"]

        for flag in (
            "semantic_correctness_claimed",
            "production_readiness_claimed",
            "autonomous_ai_coding_claimed",
            "provider_model_runtime_platform_execution_claimed",
            "service_api_ui_dashboard_auth_deployment_readiness_claimed",
            "adapter_execution_allowed",
            "real_domain_execution_claimed",
            "fixture_mappings_treated_as_live_integrations",
        ):
            self.assertFalse(flags[flag])

    def test_does_not_reinterpret_fixture_readbacks_as_live_integrations(self):
        fixture_readbacks = (
            read_code_patching_backbone_operator_readback(),
            read_research_claim_fixture_backbone_operator_readback(),
            read_pkms_note_fixture_backbone_operator_readback(),
        )

        for readback in fixture_readbacks:
            self.assertFalse(readback["backbone_v0_declared"])
            self.assertFalse(readback["adapter_execution_allowed"])
            self.assertFalse(readback["semantic_correctness_claimed"])
            self.assertFalse(readback["production_readiness_claimed"])
            self.assertFalse(
                readback["provider_model_runtime_platform_execution_claimed"]
            )
            self.assertTrue(readback["non_proofs"])

    def test_git_ref_preservation_status_is_careful(self):
        status = read_backbone_v0_declaration_operator_status()
        refs = status["git_ref_preservation_status"]

        self.assertTrue(refs["local_refs_independently_verified"])
        self.assertEqual(
            refs["local_tag_points_to"],
            "12e70023d638c0f919aa8e00e50ceccfaf36a6de",
        )
        self.assertEqual(
            refs["local_branch_points_to"],
            "12e70023d638c0f919aa8e00e50ceccfaf36a6de",
        )
        self.assertFalse(refs["remote_refs_independently_verified"])
        self.assertEqual(refs["remote_ref_status"], "not_independently_verified")


if __name__ == "__main__":
    unittest.main()
