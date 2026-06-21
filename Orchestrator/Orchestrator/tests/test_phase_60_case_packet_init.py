import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import main
from orchestrator.case_packet import (
    CASE_PACKETS_DIR,
    initialize_case_packet_from_seed,
    load_case_packet,
    summarize_case_packet,
    validate_case_packet,
)
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase60CasePacketInitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_dir = DATA_DIR / "phase60_case_packet_seeds"
        self.fixture_dir.mkdir(parents=True, exist_ok=True)

    def _capture_main(self, argv: list[str]) -> str:
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                main.main()
            return output.getvalue()

    def _write_seed(self, payload: dict) -> Path:
        path = self.fixture_dir / f"seed_{uuid4().hex[:8]}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def _count_json_files(self, directory: Path) -> int:
        if not directory.exists():
            return 0
        return len(list(directory.glob("*.json")))

    def _snapshot_mutation_surface(self) -> dict[str, int | str]:
        return {
            "case_packets": self._count_json_files(CASE_PACKETS_DIR),
            "runs": self._count_json_files(RUNS_DIR),
            "tasks": self._count_json_files(TASKS_DIR),
            "artifacts": self._count_json_files(ARTIFACTS_DIR),
            "verifier_results": self._count_json_files(VERIFIER_RESULTS_DIR),
            "recommendations": self._count_json_files(DATA_DIR / "reviewer_recommendations"),
            "state_text": STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else "",
        }

    def test_a_minimal_seed_initializes_complete_packet(self):
        case_id = f"case60_a_{uuid4().hex[:8]}"
        seed = {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute with vendor",
            "objective": "Contest incorrect invoice charge.",
        }

        packet = initialize_case_packet_from_seed(seed)

        self.assertEqual(packet["case_id"], case_id)
        self.assertEqual(packet["status"], "active")
        self.assertEqual(packet["next_step"], "")
        self.assertIn("counterparties", packet)
        self.assertIsInstance(packet["counterparties"], list)
        self.assertTrue(validate_case_packet(packet)["valid"])

    def test_b_optional_seed_fields_are_preserved(self):
        case_id = f"case60_b_{uuid4().hex[:8]}"
        seed = {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute with vendor",
            "objective": "Contest incorrect invoice charge.",
            "status": "active",
            "next_step": "Collect evidence",
            "counterparties": ["Vendor X"],
            "source_materials": ["invoice.pdf"],
        }

        packet = initialize_case_packet_from_seed(seed)

        self.assertEqual(packet["status"], "active")
        self.assertEqual(packet["next_step"], "Collect evidence")
        self.assertEqual(packet["counterparties"], ["Vendor X"])
        self.assertEqual(packet["source_materials"], ["invoice.pdf"])

    def test_c_validation_occurs_before_persistence(self):
        before = self._count_json_files(CASE_PACKETS_DIR)
        seed = {
            "case_id": "",
            "case_type": "billing_dispute",
            "title": "",
            "objective": "",
        }
        seed_path = self._write_seed(seed)

        output = self._capture_main(["main.py", "case-packet-init", str(seed_path)])
        payload = json.loads(output)

        self.assertFalse(payload["created"])
        self.assertFalse(payload["validation"]["valid"])
        after = self._count_json_files(CASE_PACKETS_DIR)
        self.assertEqual(before, after)

    def test_d_cli_init_success(self):
        case_id = f"case60_d_{uuid4().hex[:8]}"
        seed = {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute with vendor",
            "objective": "Contest incorrect invoice charge.",
        }
        seed_path = self._write_seed(seed)

        output = self._capture_main(["main.py", "case-packet-init", str(seed_path)])
        payload = json.loads(output)

        self.assertTrue(payload["created"])
        self.assertTrue(payload["initialized"])
        self.assertEqual(payload["case_id"], case_id)
        self.assertTrue(payload["validation"]["valid"])
        self.assertTrue(Path(payload["path"]).exists())

    def test_e_cli_init_invalid_seed(self):
        seed = {
            "case_id": "",
            "case_type": "billing_dispute",
            "title": "",
            "objective": "",
        }
        seed_path = self._write_seed(seed)

        output = self._capture_main(["main.py", "case-packet-init", str(seed_path)])
        payload = json.loads(output)

        self.assertFalse(payload["created"])
        self.assertTrue(payload["initialized"])
        self.assertFalse(payload["validation"]["valid"])

    def test_f_path_traversal_remains_blocked(self):
        seed = {
            "case_id": "../escape",
            "case_type": "billing_dispute",
            "title": "Billing dispute",
            "objective": "Contest charge.",
        }
        seed_path = self._write_seed(seed)

        output = self._capture_main(["main.py", "case-packet-init", str(seed_path)])
        payload = json.loads(output)

        self.assertFalse(payload["created"])
        self.assertIn("case_id contains unsafe characters", payload["validation"]["errors"])
        self.assertFalse(((CASE_PACKETS_DIR / ".." / "escape.json").resolve()).exists())

    def test_g_init_mutates_only_case_packet_storage(self):
        case_id = f"case60_g_{uuid4().hex[:8]}"
        seed = {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute",
            "objective": "Contest charge.",
        }
        seed_path = self._write_seed(seed)

        before = self._snapshot_mutation_surface()
        _ = self._capture_main(["main.py", "case-packet-init", str(seed_path)])
        after = self._snapshot_mutation_surface()

        self.assertEqual(after["case_packets"], before["case_packets"] + 1)
        self.assertEqual(before["runs"], after["runs"])
        self.assertEqual(before["tasks"], after["tasks"])
        self.assertEqual(before["artifacts"], after["artifacts"])
        self.assertEqual(before["verifier_results"], after["verifier_results"])
        self.assertEqual(before["recommendations"], after["recommendations"])
        self.assertEqual(before["state_text"], after["state_text"])

    def test_h_phase58_behavior_remains_intact(self):
        case_id = f"case60_h_{uuid4().hex[:8]}"
        packet_input = {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute",
            "objective": "Contest charge.",
            "status": "active",
            "next_step": "",
        }
        packet_path = self._write_seed(packet_input)

        create_output = self._capture_main(["main.py", "case-packet-create", str(packet_path)])
        create_payload = json.loads(create_output)
        self.assertTrue(create_payload["created"])

        show_output = self._capture_main(["main.py", "case-packet-show", case_id])
        shown = json.loads(show_output)
        self.assertEqual(shown["case_id"], case_id)

    def test_i_phase59_behavior_remains_intact(self):
        case_id = f"case60_i_{uuid4().hex[:8]}"
        seed = {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute",
            "objective": "Contest charge.",
            "source_materials": ["invoice.pdf"],
            "open_issues": ["wrong amount"],
            "status": "active",
            "next_step": "Request correction",
        }
        seed_path = self._write_seed(seed)
        _ = self._capture_main(["main.py", "case-packet-init", str(seed_path)])

        summary_output = self._capture_main(["main.py", "case-packet-summary", case_id])
        summary = json.loads(summary_output)
        self.assertEqual(summary["case_id"], case_id)
        self.assertIn("readiness", summary)

        validate_output = self._capture_main(["main.py", "case-packet-validate", case_id])
        validation = json.loads(validate_output)
        self.assertTrue(validation["valid"])

        loaded = load_case_packet(case_id)
        self.assertEqual(summarize_case_packet(loaded)["case_id"], case_id)


if __name__ == "__main__":
    unittest.main()
