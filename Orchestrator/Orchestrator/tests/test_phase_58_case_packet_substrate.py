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
    load_case_packet,
    normalize_case_packet,
    save_case_packet,
    validate_case_packet,
)
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase58CasePacketSubstrateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_dir = DATA_DIR / "phase58_case_packet_inputs"
        self.fixture_dir.mkdir(parents=True, exist_ok=True)

    def _input_path(self, prefix: str) -> Path:
        return self.fixture_dir / f"{prefix}_{uuid4().hex[:8]}.json"

    def _write_input(self, prefix: str, payload: dict) -> Path:
        path = self._input_path(prefix)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def _capture_main(self, argv: list[str]) -> str:
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                main.main()
            return output.getvalue()

    def _count_json_files(self, directory: Path) -> int:
        if not directory.exists():
            return 0
        return len(list(directory.glob("*.json")))

    def _snapshot_mutation_surface(self) -> dict[str, int | str]:
        return {
            "runs": self._count_json_files(RUNS_DIR),
            "tasks": self._count_json_files(TASKS_DIR),
            "artifacts": self._count_json_files(ARTIFACTS_DIR),
            "verifier_results": self._count_json_files(VERIFIER_RESULTS_DIR),
            "recommendations": self._count_json_files(DATA_DIR / "reviewer_recommendations"),
            "state_text": STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else "",
            "case_packets": self._count_json_files(CASE_PACKETS_DIR),
        }

    def _valid_payload(self, case_id: str) -> dict:
        return {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute with vendor",
            "objective": "Contest incorrect invoice",
            "counterparties": ["Vendor A"],
            "source_materials": ["invoice.pdf"],
            "extracted_facts": ["invoice total mismatch"],
            "timeline_events": ["2026-01-01 invoice received"],
            "open_issues": ["line item not contracted"],
            "missing_evidence": ["signed contract"],
            "contradictions": [],
            "drafts": [],
            "decisions": [],
            "status": "active",
            "next_step": "request corrected invoice",
        }

    def test_a_valid_normalization_and_validation(self):
        payload = {
            "case_id": "  case_58_a  ",
            "case_type": " dispute ",
            "title": "  Title  ",
            "objective": "  Objective  ",
            "counterparties": "invalid",
            "status": " active ",
            "next_step": " next ",
        }
        packet = normalize_case_packet(payload)
        validation = validate_case_packet(packet)

        self.assertEqual(packet["case_id"], "case_58_a")
        self.assertEqual(packet["title"], "Title")
        self.assertEqual(packet["objective"], "Objective")
        self.assertEqual(packet["counterparties"], [])
        self.assertEqual(packet["missing_evidence"], [])
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["errors"], [])

    def test_b_invalid_packet_rejection(self):
        packet = normalize_case_packet(
            {
                "case_id": "  ",
                "case_type": "x",
                "title": "",
                "objective": "",
                "status": "active",
                "next_step": "",
            }
        )
        validation = validate_case_packet(packet)

        self.assertFalse(validation["valid"])
        self.assertIn("case_id is required", validation["errors"])
        self.assertIn("title is required", validation["errors"])
        self.assertIn("objective is required", validation["errors"])

    def test_c_persistence_load_round_trip(self):
        case_id = f"case58_roundtrip_{uuid4().hex[:8]}"
        packet = normalize_case_packet(self._valid_payload(case_id))
        validation = validate_case_packet(packet)
        self.assertTrue(validation["valid"])

        path = save_case_packet(packet)
        loaded = load_case_packet(case_id)

        self.assertTrue(path.exists())
        self.assertEqual(loaded, packet)

    def test_d_cli_create(self):
        case_id = f"case58_cli_create_{uuid4().hex[:8]}"
        input_path = self._write_input("create", self._valid_payload(case_id))

        output = self._capture_main(["main.py", "case-packet-create", str(input_path)])
        payload = json.loads(output)

        self.assertTrue(payload.get("created"))
        self.assertEqual(payload.get("case_id"), case_id)
        self.assertTrue(payload.get("validation", {}).get("valid"))

        packet_path = Path(payload["path"])
        self.assertTrue(packet_path.exists())

    def test_e_cli_show(self):
        case_id = f"case58_cli_show_{uuid4().hex[:8]}"
        packet = normalize_case_packet(self._valid_payload(case_id))
        save_case_packet(packet)

        output = self._capture_main(["main.py", "case-packet-show", case_id])
        shown = json.loads(output)
        self.assertEqual(shown["case_id"], case_id)
        self.assertEqual(shown, packet)

    def test_f_no_hidden_orchestration_mutation(self):
        case_id = f"case58_no_mut_{uuid4().hex[:8]}"
        input_path = self._write_input("no_mut", self._valid_payload(case_id))

        before = self._snapshot_mutation_surface()
        _ = self._capture_main(["main.py", "case-packet-create", str(input_path)])
        _ = self._capture_main(["main.py", "case-packet-show", case_id])
        after = self._snapshot_mutation_surface()

        self.assertEqual(before["runs"], after["runs"])
        self.assertEqual(before["tasks"], after["tasks"])
        self.assertEqual(before["artifacts"], after["artifacts"])
        self.assertEqual(before["verifier_results"], after["verifier_results"])
        self.assertEqual(before["recommendations"], after["recommendations"])
        self.assertEqual(before["state_text"], after["state_text"])
        self.assertEqual(after["case_packets"], before["case_packets"] + 1)

    def test_g_path_traversal_protection(self):
        payload = self._valid_payload("../escape")
        normalized = normalize_case_packet(payload)
        validation = validate_case_packet(normalized)

        self.assertFalse(validation["valid"])
        self.assertIn("case_id contains unsafe characters", validation["errors"])

        input_path = self._write_input("traversal", payload)
        output = self._capture_main(["main.py", "case-packet-create", str(input_path)])
        result = json.loads(output)

        self.assertFalse(result["valid"])
        self.assertIn("case_id contains unsafe characters", result["errors"])

        outside_path = (CASE_PACKETS_DIR / ".." / "escape.json").resolve()
        self.assertFalse(outside_path.exists())


if __name__ == "__main__":
    unittest.main()
