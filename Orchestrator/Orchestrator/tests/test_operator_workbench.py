from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from orchestrator.operator_workbench import Workbench, packet_from_form


class OperatorWorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.app = Workbench(self.root, self.root / "data")
        self.form = {"title": "Exact fixture", "objective": "Write the exact expected line.", "path": "workbench_fixtures/proof.txt", "expected_output": "Expected Workbench proof line.\n", "validation": "Exact expected output.", "worker": "fixture", "timeout": "10"}

    def tearDown(self): self.temp.cleanup()

    def test_preview_never_authorizes_execution(self):
        packet = packet_from_form(self.form)
        self.assertEqual("preview_only", packet["authorization_decision"])
        self.assertFalse((self.root / "data").exists())

    def test_paths_outside_dedicated_fixture_are_rejected(self):
        with self.assertRaises(ValueError): packet_from_form({**self.form, "path": "../outside.txt"})
        with self.assertRaises(ValueError): packet_from_form({**self.form, "path": "source.py"})

    def test_fixture_run_persists_canonical_evidence_then_accepts(self):
        self.app.start(self.form)
        for _ in range(100):
            state = self.app.status()
            if state["state"] != "executing": break
            time.sleep(.05)
        self.assertEqual("awaiting_review", state["state"])
        self.assertTrue(state["evidence"]["task"])
        self.assertTrue(state["evidence"]["artifact"])
        self.assertTrue(state["evidence"]["verifier"])
        self.app.disposition("accept", "Accepted after inspecting the exact fixture output.")
        self.assertEqual("accepted", self.app.status()["state"])
        self.assertTrue(self.app.status()["disposition"]["acceptance_record_created"])

    def test_one_active_run_posture_is_enforced(self):
        self.app.active = {"state": "executing"}
        with self.assertRaises(ValueError): self.app.start(self.form)

    def test_codex_selection_uses_the_fixed_protocol_adapter(self):
        command = self.app.worker_command("codex")
        self.assertEqual(["-m", "orchestrator.operator_workbench_codex_worker"], command[1:])


if __name__ == "__main__": unittest.main()
