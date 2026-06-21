import inspect
import unittest

from orchestrator import capability_registry
from orchestrator.capability_registry import (
    CAPABILITY_REGISTRY,
    CapabilityClass,
    CapabilityMaturityStatus,
    CapabilityRegistryEntry,
    assess_required_capabilities,
    get_capability,
    list_capabilities,
)


class Phase109CapabilityRegistryContractTests(unittest.TestCase):
    def test_registry_contains_representative_entry_for_each_required_class(self):
        classes = {entry.capability_class.value for entry in CAPABILITY_REGISTRY.values()}

        self.assertEqual(
            classes,
            {
                "direct_answer",
                "coding_task",
                "file_operation",
                "local_document_lookup",
                "web_research",
                "reminder_scheduler",
                "connector_access",
                "platform_runtime",
                "provider_model",
                "artifact_export_package",
                "production_execution",
                "unsupported_or_blocked",
            },
        )

    def test_registry_entries_include_required_documentation_level_fields(self):
        required_fields = {
            "capability_id",
            "display_name",
            "capability_class",
            "maturity_status",
            "authority_docs",
            "implementation_refs",
            "allowed_route_types",
            "permission_burden",
            "validation_burden",
            "stop_conditions",
            "non_proofs",
            "owner_context",
            "external_track_dependency",
        }

        for entry in CAPABILITY_REGISTRY.values():
            self.assertIsInstance(entry, CapabilityRegistryEntry)
            self.assertTrue(required_fields.issubset(entry.__dataclass_fields__))
            self.assertIsInstance(entry.capability_class, CapabilityClass)
            self.assertIsInstance(entry.maturity_status, CapabilityMaturityStatus)
            self.assertIn("docs/CAPABILITY_REGISTRY.md", entry.authority_docs)
            self.assertIn("registry_lookup_is_not_execution", entry.non_proofs)

    def test_get_capability_returns_known_entry_without_execution_authority(self):
        entry = get_capability("provider_model")

        self.assertIsNotNone(entry)
        self.assertEqual(entry.capability_id, "provider_model")
        self.assertIn("registry_lookup_is_not_provider_model_substrate_selection", entry.non_proofs)
        assessment = assess_required_capabilities(["provider_model"])
        self.assertFalse(assessment["authorized_execution"])

    def test_get_capability_returns_none_for_unknown_id(self):
        self.assertIsNone(get_capability("unknown_future_capability"))

        assessment = assess_required_capabilities(["unknown_future_capability"])
        self.assertEqual(assessment["unknown_capabilities"], ["unknown_future_capability"])
        self.assertIn(
            "unknown_capabilities_require_clarification_or_future_registry_entry",
            assessment["admission_notes"],
        )

    def test_list_capabilities_returns_deterministic_stable_ordering(self):
        first = [entry.capability_id for entry in list_capabilities()]
        second = [entry.capability_id for entry in list_capabilities()]

        self.assertEqual(first, second)
        self.assertEqual(first, sorted(first))

    def test_assess_required_capabilities_separates_known_from_unknown(self):
        assessment = assess_required_capabilities(
            ["source_inspection", "local_document_lookup", "future_unknown"]
        )

        self.assertEqual(
            assessment["requested_capabilities"],
            ["source_inspection", "local_document_lookup", "future_unknown"],
        )
        self.assertEqual(
            assessment["known_capabilities"],
            ["source_inspection", "local_document_lookup"],
        )
        self.assertEqual(assessment["unknown_capabilities"], ["future_unknown"])
        self.assertFalse(assessment["authorized_execution"])

    def test_assessment_reports_blocked_or_external_conservatively(self):
        assessment = assess_required_capabilities(
            ["local_document_lookup", "scheduling_contract", "external_connector"]
        )

        self.assertEqual(
            assessment["blocked_or_external_capabilities"],
            ["local_document_lookup", "scheduling_contract", "external_connector"],
        )
        self.assertIn(
            "blocked_or_external_capabilities_require_separate_boundary",
            assessment["admission_notes"],
        )

    def test_no_current_capability_is_production_ready(self):
        self.assertFalse(
            [
                entry.capability_id
                for entry in CAPABILITY_REGISTRY.values()
                if entry.maturity_status == CapabilityMaturityStatus.PRODUCTION_READY
            ]
        )

        assessment = assess_required_capabilities(list(CAPABILITY_REGISTRY))
        self.assertEqual(assessment["production_ready_capabilities"], [])

    def test_capability_labels_are_not_execution_authority(self):
        assessment = assess_required_capabilities(["filesystem_mutation_authority"])

        self.assertFalse(assessment["authorized_execution"])
        self.assertIn(
            "implemented_capability_is_not_authorized_execution",
            assessment["admission_notes"],
        )
        self.assertIn(
            "capability_label_is_not_execution_authority",
            assessment["non_proofs"],
        )

    def test_provider_model_and_platform_classes_remain_non_executing_and_external(self):
        assessment = assess_required_capabilities(["provider_model", "platform_runtime"])

        self.assertEqual(
            assessment["blocked_or_external_capabilities"],
            ["provider_model", "platform_runtime"],
        )
        self.assertFalse(assessment["authorized_execution"])
        for capability_id in ("provider_model", "platform_runtime"):
            entry = get_capability(capability_id)
            self.assertEqual(entry.maturity_status, CapabilityMaturityStatus.BLOCKED_OR_EXTERNAL)
            self.assertIsNotNone(entry.external_track_dependency)

    def test_phase_103_capability_strings_are_registered_or_conservative(self):
        phase_103_capabilities = [
            "source_inspection",
            "patch_proposal",
            "filesystem_mutation_authority",
            "bounded_file_write",
            "local_document_lookup",
            "scheduling_contract",
            "planning_report",
            "web_research",
            "creative_text_generation",
            "external_connector",
        ]

        assessment = assess_required_capabilities(phase_103_capabilities)

        self.assertEqual(assessment["unknown_capabilities"], [])
        self.assertFalse(assessment["authorized_execution"])
        self.assertIn("local_document_lookup", assessment["blocked_or_external_capabilities"])
        self.assertIn("scheduling_contract", assessment["blocked_or_external_capabilities"])
        self.assertIn("external_connector", assessment["blocked_or_external_capabilities"])

    def test_module_does_not_import_provider_model_runtime_or_platform_libraries(self):
        source = inspect.getsource(capability_registry)

        forbidden_imports = (
            "import requests",
            "import openai",
            "import ollama",
            "import discord",
            "import subprocess",
            "from orchestrator.provider",
            "from orchestrator.platform",
            "from orchestrator.request_routing",
        )
        for forbidden in forbidden_imports:
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
