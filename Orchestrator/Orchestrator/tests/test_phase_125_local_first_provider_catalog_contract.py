import inspect
import unittest

from orchestrator import model_provider_catalog
from orchestrator.model_provider_catalog import (
    NO_PROVIDER_CATALOG_ACTIVITY_FLAGS,
    PROVIDER_CATALOG_NON_PROOFS,
    REQUIRED_PROVIDER_KEYS,
    get_model_provider_catalog,
    get_model_provider_catalog_entry,
    provider_posture_for_route,
)


class Phase125LocalFirstProviderCatalogContractTests(unittest.TestCase):
    def setUp(self):
        self.catalog = get_model_provider_catalog()

    def assert_no_activity(self, entry):
        self.assertFalse(entry.execution_allowed)
        self.assertFalse(entry.selection_allowed)
        self.assertEqual(entry.activity_flags, NO_PROVIDER_CATALOG_ACTIVITY_FLAGS)
        self.assertTrue(all(flag is False for flag in entry.activity_flags.values()))

    def assert_conservative_non_proofs(self, entry):
        for non_proof in PROVIDER_CATALOG_NON_PROOFS:
            self.assertIn(non_proof, entry.non_proofs)
        for required in (
            "provider_catalog_is_not_provider_execution",
            "provider_catalog_is_not_model_execution",
            "provider_catalog_is_not_runtime_execution",
            "provider_catalog_is_not_platform_execution",
            "provider_catalog_is_not_worker_dispatch",
            "provider_catalog_is_not_route_execution",
            "provider_catalog_is_not_production_readiness",
        ):
            self.assertIn(required, entry.non_proofs)

    def test_catalog_returns_all_required_provider_entries(self):
        self.assertEqual(set(REQUIRED_PROVIDER_KEYS), set(self.catalog))
        for provider_key in REQUIRED_PROVIDER_KEYS:
            self.assertEqual(self.catalog[provider_key].provider_key, provider_key)

    def test_every_catalog_entry_is_non_executing_and_non_selecting(self):
        for entry in self.catalog.values():
            with self.subTest(provider_key=entry.provider_key):
                self.assert_no_activity(entry)
                self.assert_conservative_non_proofs(entry)

    def test_no_activity_flags_claim_runtime_or_boundary_execution(self):
        forbidden_true_flags = (
            "provider_executed",
            "model_executed",
            "runtime_executed",
            "platform_executed",
            "worker_dispatched",
            "codex_dispatched",
            "rag_lookup_performed",
            "web_lookup_performed",
            "scheduler_executed",
            "connector_executed",
            "route_executed",
            "production_executed",
        )
        for entry in self.catalog.values():
            with self.subTest(provider_key=entry.provider_key):
                for flag in forbidden_true_flags:
                    self.assertIs(entry.activity_flags[flag], False)

    def test_local_model_candidate_prefers_local_first_but_requires_future_boundary(self):
        entry = self.catalog["local_model_candidate"]

        self.assertEqual(entry.provider_tier, "local_first_candidate")
        self.assertEqual(entry.provider_posture, "local_first_when_authorized_no_provider_executed")
        self.assertIn("future_provider_model_boundary", entry.required_authority)
        self.assertIn("local_first_preference_is_not_local_model_execution", entry.non_proofs)
        self.assert_no_activity(entry)

    def test_frontier_provider_candidate_requires_explicit_frontier_boundary(self):
        entry = self.catalog["frontier_provider_candidate"]

        self.assertEqual(entry.provider_tier, "frontier_candidate")
        self.assertEqual(entry.allowed_boundary, "frontier_provider_escalation_boundary")
        self.assertEqual(entry.provider_posture, "provider_model_runtime_platform_not_selected")
        self.assertIn("explicit_frontier_provider_escalation_boundary", entry.required_authority)
        self.assert_no_activity(entry)

    def test_worker_codex_entry_requires_boundary_and_does_not_dispatch(self):
        entry = self.catalog["worker_codex_boundary"]

        self.assertEqual(entry.allowed_boundary, "bounded_worker_codex_boundary")
        self.assertEqual(entry.provider_posture, "provider_model_not_selected_for_direct_execution")
        self.assertIn("worker_boundary_required_before_any_dispatch", entry.escalation_posture)
        self.assertFalse(entry.activity_flags["worker_dispatched"])
        self.assertFalse(entry.activity_flags["codex_dispatched"])
        self.assert_no_activity(entry)

    def test_rag_scheduler_and_web_entries_require_own_boundaries_without_execution(self):
        expected = {
            "rag_local_document_boundary": ("rag_local_document_lookup_boundary", "rag_lookup_performed"),
            "scheduler_reminder_boundary": ("scheduler_reminder_boundary", "scheduler_executed"),
            "web_research_boundary": ("web_research_boundary", "web_lookup_performed"),
        }
        for provider_key, (boundary, activity_flag) in expected.items():
            with self.subTest(provider_key=provider_key):
                entry = self.catalog[provider_key]
                self.assertEqual(entry.allowed_boundary, boundary)
                self.assertIn("explicit_", entry.required_authority)
                self.assertFalse(entry.activity_flags[activity_flag])
                self.assert_no_activity(entry)

    def test_route_posture_lookup_matches_existing_router_policy_strings(self):
        self.assertEqual(
            provider_posture_for_route("local_first_answer"),
            "local_first_when_authorized_no_provider_executed",
        )
        self.assertEqual(
            provider_posture_for_route("worker_codex_boundary"),
            "provider_model_not_selected_for_direct_execution",
        )
        self.assertEqual(
            provider_posture_for_route("separate_provider_or_platform_boundary_required"),
            "provider_model_runtime_platform_not_selected",
        )
        self.assertEqual(provider_posture_for_route("unknown"), "no_provider_selected")

    def test_unknown_catalog_entry_falls_back_to_blocked_or_unavailable(self):
        entry = get_model_provider_catalog_entry("unknown_provider")

        self.assertEqual(entry.provider_key, "provider_blocked_or_unavailable")
        self.assertIn("fresh_proof", entry.escalation_posture)
        self.assert_no_activity(entry)

    def test_catalog_module_uses_no_provider_runtime_or_execution_imports(self):
        source = inspect.getsource(model_provider_catalog)

        for forbidden in (
            "import subprocess",
            "import requests",
            "import socket",
            "import urllib",
            "import openai",
            "import ollama",
            "import discord",
            "from providers",
            "import providers",
            "from orchestrator.providers",
            "from orchestrator.provider",
            "from orchestrator.platform",
            "from orchestrator.scheduler",
            "from orchestrator.connector",
            "from orchestrator.openclaw",
            "from orchestrator.hermes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
