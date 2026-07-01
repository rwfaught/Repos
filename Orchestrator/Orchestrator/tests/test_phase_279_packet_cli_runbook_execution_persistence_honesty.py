import json
import re
import unittest
from pathlib import Path


class Phase279PacketCliRunbookExecutionPersistenceHonestyTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.runbook_path = (
            self.repo_root / "docs" / "OPERATOR_CODING_TASK_PACKET_CLI_RUNBOOK.md"
        )
        self.runbook_text = self.runbook_path.read_text(encoding="utf-8")
        self.runbook_lower = self.runbook_text.lower()
        self.runbook_words = " ".join(self.runbook_lower.split())

    def _extract_first_json_fence(self):
        match = re.search(r"```json\s*(\{.*?\})\s*```", self.runbook_text, re.DOTALL)
        self.assertIsNotNone(match, "runbook must contain a fenced JSON packet")
        return json.loads(match.group(1))

    def test_runbook_no_longer_presents_packet_cli_as_repo_read_only(self):
        self.assertIn("not a read-only repo smoke", self.runbook_lower)
        self.assertIn("do not frame this command as a repo-read-only smoke", self.runbook_lower)
        self.assertNotIn("repo-read-only operator smoke", self.runbook_lower)
        self.assertNotIn("git status will remain clean", self.runbook_lower)

    def test_runbook_explicitly_documents_execution_and_persistence_surface(self):
        required_phrases = (
            "execution and persistence surface",
            "repo-local durable",
            "task, artifact, verifier, and output records",
            "successful run can leave `git status` dirty",
            "explicit persistence or mutation boundary",
            "expected, inspected, accepted, or cleaned under a later explicit boundary",
        )
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.runbook_words)

    def test_runbook_names_generated_repo_local_paths(self):
        for path_text in (
            "outputs/",
            "data/tasks/",
            "data/artifacts/",
            "data/verifier_results/",
            "GeneratedRepoPathsToInspect",
        ):
            with self.subTest(path_text=path_text):
                self.assertIn(path_text, self.runbook_text)

    def test_runbook_preserves_non_proofs_and_local_file_caveat(self):
        required_phrases = (
            "no_semantic_correctness_proof",
            "no_live_provider_model_proof",
            "no_runtime_platform_proof",
            "no_autonomous_ai_coding_proof",
            "no_production_readiness_proof",
            "deterministic `local_file` behavior",
            "not model-backed coding",
            "not semantic task adequacy proof",
        )
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.runbook_words)

    def test_runbook_includes_no_exit_operator_script_discipline(self):
        self.assertIn("must not use `exit`", self.runbook_lower)
        self.assertIn("especially not `exit 1`", self.runbook_lower)
        self.assertIn("prefer accumulated", self.runbook_lower)
        self.assertIn("natural script completion", self.runbook_lower)

        powershell_blocks = re.findall(
            r"```powershell\s*(.*?)\s*```",
            self.runbook_text,
            re.DOTALL,
        )
        self.assertGreaterEqual(len(powershell_blocks), 2)
        execution_block = powershell_blocks[-1]
        self.assertNotRegex(execution_block, r"(?im)^\s*exit\b")
        self.assertNotRegex(execution_block, r"(?im)^\s*throw\b")
        self.assertIn("PASS", execution_block)
        self.assertIn("FAIL", execution_block)
        self.assertIn("StartedAt", execution_block)
        self.assertIn("FinishedAt", execution_block)
        self.assertIn("ElapsedMs", execution_block)

    def test_runbook_packet_json_example_remains_parseable_and_local_file_only(self):
        packet = self._extract_first_json_fence()
        self.assertEqual(packet["provider_name"], "local_file")
        self.assertEqual(packet["execution_policy"], "filesystem_mutation")
        self.assertEqual(packet["files_in_scope"], ["outputs/phase277_golden_smoke.txt"])
        self.assertNotIn("model_name", packet)
        self.assertNotIn("runtime", packet)
        self.assertNotIn("platform", packet)


if __name__ == "__main__":
    unittest.main()
