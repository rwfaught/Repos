import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from orchestrator.operator_coding_task_packet_cli import main


class Phase277PacketCliOperatorRunbookGoldenSmokeTests(unittest.TestCase):
    def _extract_first_json_fence(self, runbook_text):
        match = re.search(r"~~~json\s*(\{.*?\})\s*~~~", runbook_text, re.DOTALL)
        self.assertIsNotNone(match, "runbook must contain a fenced JSON packet")
        return json.loads(match.group(1))

    def test_migrated_runbook_requires_explicit_canonical_worker_wiring(self):
        repo_root = Path(__file__).resolve().parents[1]
        runbook_path = repo_root / "docs" / "OPERATOR_CODING_TASK_PACKET_CLI_RUNBOOK.md"
        self.assertTrue(runbook_path.exists())
        runbook_text = runbook_path.read_text(encoding="utf-8")
        self.assertIn(
            "python -m orchestrator.operator_coding_task_packet_cli --packet-json <packet-path>",
            runbook_text,
        )
        self.assertIn("subprocess_worker", runbook_text)
        self.assertIn("Implicit **local_file** execution is retired", runbook_text)

        packet = self._extract_first_json_fence(runbook_text)
        self.assertEqual(packet["provider_name"], "subprocess_worker")
        self.assertEqual(packet["worker_trust_posture"], "trusted_local_unsandboxed")
        self.assertNotIn("model_name", packet)
        self.assertNotIn("runtime", packet)
        self.assertNotIn("platform", packet)

        with tempfile.TemporaryDirectory() as directory:
            packet_path = Path(directory) / "packet.json"
            packet_path.write_text(json.dumps(packet), encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--packet-json", str(packet_path)])
            result = json.loads(stdout.getvalue())

            self.assertEqual(exit_code, 1)
            self.assertTrue(result["operator_coding_task_packet_surface"])
            self.assertFalse(result["accepted"])
            self.assertTrue(result["blocked"])
            self.assertIn("explicit_worker_provider_required", result["blocked_conditions"])


if __name__ == "__main__":
    unittest.main()
