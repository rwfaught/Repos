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
from orchestrator.backbone_v0_declaration import (
    BACKBONE_V0_DECLARED,
    BACKBONE_V0_DECLARATION_MARKER,
    BACKBONE_V0_OFFICIAL_CAPSULE_PROOF,
    read_backbone_v0_declaration_status,
)


class Phase337BackboneV0DeclarationTests(unittest.TestCase):
    def test_declaration_status_exists_and_is_deterministic(self):
        first = read_backbone_v0_declaration_status()
        second = read_backbone_v0_declaration_status()

        self.assertEqual(first, second)
        self.assertTrue(BACKBONE_V0_DECLARED)
        self.assertTrue(first["backbone_v0_declared"])
        self.assertEqual(first["marker"], BACKBONE_V0_DECLARATION_MARKER)

    def test_declaration_scope_is_narrow_source_test_docs_structural_status(self):
        status = read_backbone_v0_declaration_status()

        self.assertIn("source/test/docs structural milestone", status["declared_claim"])
        self.assertIn("domain_neutral_backbone_scaffold_exists", status["declaration_scope"])
        self.assertIn("official_clean_capsule_proof_recorded", status["declaration_scope"])
        self.assertIn("adapter_execution_disabled", status["declaration_scope"])
        self.assertIn("real_domain_execution_not_implied", status["declaration_scope"])

    def test_required_prior_markers_and_capsule_proof_are_referenced(self):
        status = read_backbone_v0_declaration_status()

        for marker in (
            "PHASE320_BACKBONE_MAPPING_OPERATOR_DECISION_BOUNDARY_ASSESSMENT_SOURCE_TEST_DOCS_PROVEN=PASS",
            "PHASE324_BACKBONE_NON_PATCH_FIXTURE_READBACK_DECISION_BOUNDARY_SOURCE_TEST_DOCS_PROVEN=PASS",
            "PHASE328_BACKBONE_PKMS_NOTE_OPERATION_FIXTURE_READBACK_DECISION_BOUNDARY_SOURCE_TEST_DOCS_PROVEN=PASS",
            "PHASE333_BACKBONE_V0_CRITERIA_READBACK_OPERATOR_DECISION_BOUNDARY_SOURCE_TEST_DOCS_PROVEN=PASS",
            "PHASE335_BACKBONE_V0_OFFICIAL_CLEAN_CAPSULE_PROOF_SOURCE_DOCS_PROVEN=PASS",
        ):
            self.assertIn(marker, status["accepted_proof_markers"])

        capsule = status["official_capsule_proof"]
        self.assertEqual(capsule, BACKBONE_V0_OFFICIAL_CAPSULE_PROOF)
        self.assertEqual(
            capsule["sha256"],
            "04cb5a2205bedcef767d8cab6344237e9b4ce1f75f19793a56425ab8b197d49d",
        )
        self.assertEqual(capsule["entry_count"], 1001)
        self.assertEqual(capsule["git_entry_count"], 0)
        self.assertEqual(capsule["pycache_pyc_entry_count"], 0)

    def test_non_proofs_and_forbidden_claims_are_preserved(self):
        status = read_backbone_v0_declaration_status()

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

        self.assertIn("not_semantic_correctness", status["non_proofs"])
        self.assertIn("not_production_readiness", status["non_proofs"])
        self.assertFalse(status["execution_flags"]["semantic_correctness_claimed"])
        self.assertFalse(status["execution_flags"]["production_readiness_claimed"])
        self.assertFalse(
            status["execution_flags"][
                "provider_model_runtime_platform_execution_claimed"
            ]
        )

    def test_adapter_and_real_domain_execution_remain_unclaimed(self):
        status = read_backbone_v0_declaration_status()

        self.assertFalse(status["execution_flags"]["adapter_execution_allowed"])
        self.assertFalse(status["execution_flags"]["real_domain_execution_claimed"])
        self.assertFalse(
            status["execution_flags"]["fixture_mappings_treated_as_live_integrations"]
        )

    def test_declaration_does_not_retroactively_alter_fixture_claims(self):
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


if __name__ == "__main__":
    unittest.main()
