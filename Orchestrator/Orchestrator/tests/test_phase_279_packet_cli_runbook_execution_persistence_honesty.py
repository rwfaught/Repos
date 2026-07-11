import json
import re
import unittest
from pathlib import Path


class Phase279PacketCliRunbookExecutionPersistenceHonestyTests(unittest.TestCase):
    def setUp(self):
        repo_root = Path(__file__).resolve().parents[1]
        self.runbook_text = (repo_root / "docs" / "OPERATOR_CODING_TASK_PACKET_CLI_RUNBOOK.md").read_text(encoding="utf-8")
        self.runbook_lower = self.runbook_text.lower()
        self.runbook_words = " ".join(self.runbook_lower.split())

    def _extract_first_json_fence(self):
        match = re.search(r"~~~json\s*(\{.*?\})\s*~~~", self.runbook_text, re.DOTALL)
        self.assertIsNotNone(match, "runbook must contain a fenced JSON packet")
        return json.loads(match.group(1))

    def test_runbook_documents_the_canonical_execution_and_persistence_surface(self):
        for phrase in (
            "not a read-only smoke command",
            "--data-root",
            "--trusted-worker-posture trusted_local_unsandboxed",
            "--worker-command",
            "execution_authorizations/",
            "worker_workspaces/",
            "changed_paths",
            "read-only lifecycle reconciliation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.runbook_lower)

    def test_runbook_preserves_trusted_worker_and_non_proof_boundaries(self):
        for phrase in (
            "implicit **local_file** execution is retired",
            "does not select a provider or model",
            "not os sandboxing",
            "untrusted-worker execution is unsupported",
            "does not prove semantic correctness",
            "autonomous coding competence",
            "production readiness",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.runbook_words)

    def test_runbook_packet_json_example_is_parseable_and_requires_subprocess_worker(self):
        packet = self._extract_first_json_fence()
        self.assertEqual(packet["provider_name"], "subprocess_worker")
        self.assertEqual(packet["execution_policy"], "filesystem_mutation")
        self.assertEqual(packet["worker_trust_posture"], "trusted_local_unsandboxed")
        self.assertNotIn("model_name", packet)
        self.assertNotIn("runtime", packet)
        self.assertNotIn("platform", packet)


if __name__ == "__main__":
    unittest.main()
