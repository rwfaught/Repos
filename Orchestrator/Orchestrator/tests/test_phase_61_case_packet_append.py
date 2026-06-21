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
    append_case_packet_entry,
    initialize_case_packet_from_seed,
    load_case_packet,
    normalize_case_packet,
    save_case_packet,
    summarize_case_packet,
)
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase61CasePacketAppendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_dir = DATA_DIR / "phase61_case_packet_inputs"
        self.fixture_dir.mkdir(parents=True, exist_ok=True)

    def _capture_main(self, argv: list[str]) -> str:
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                main.main()
            return output.getvalue()

    def _write_json(self, payload: dict, prefix: str) -> Path:
        path = self.fixture_dir / f"{prefix}_{uuid4().hex[:8]}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

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
        }

    def _new_case(self, with_seed: bool = False) -> str:
        case_id = f"case61_{uuid4().hex[:8]}"
        if with_seed:
            packet = initialize_case_packet_from_seed(
                {
                    "case_id": case_id,
                    "case_type": "billing_dispute",
                    "title": "Billing dispute",
                    "objective": "Contest charge",
                }
            )
        else:
            packet = normalize_case_packet(
                {
                    "case_id": case_id,
                    "case_type": "billing_dispute",
                    "title": "Billing dispute",
                    "objective": "Contest charge",
                    "status": "active",
                    "next_step": "",
                    "open_issues": [{"text": "initial"}],
                }
            )
        save_case_packet(packet)
        return case_id

    def test_a_append_to_approved_field(self):
        case_id = self._new_case()
        packet = load_case_packet(case_id)

        updated = append_case_packet_entry(packet, "open_issues", {"text": "new issue"})

        self.assertEqual(len(updated["open_issues"]), 2)
        self.assertEqual(updated["open_issues"][1]["text"], "new issue")

    def test_b_append_preserves_existing_entries(self):
        case_id = self._new_case()
        packet = load_case_packet(case_id)
        existing_first = packet["open_issues"][0]

        updated = append_case_packet_entry(packet, "open_issues", {"text": "another"})

        self.assertEqual(updated["open_issues"][0], existing_first)
        self.assertEqual(updated["open_issues"][1]["text"], "another")

    def test_c_unknown_field_rejected(self):
        case_id = self._new_case()
        packet = load_case_packet(case_id)

        with self.assertRaises(ValueError):
            append_case_packet_entry(packet, "unknown_field", {"text": "x"})

    def test_d_scalar_field_rejected(self):
        case_id = self._new_case()
        packet = load_case_packet(case_id)

        with self.assertRaises(ValueError):
            append_case_packet_entry(packet, "title", {"text": "x"})

    def test_e_missing_entry_rejected(self):
        case_id = self._new_case()
        append_payload = {
            "case_id": case_id,
            "field": "open_issues",
        }
        append_path = self._write_json(append_payload, "missing_entry")

        output = self._capture_main(["main.py", "case-packet-append", str(append_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertFalse(payload["appended"])
        self.assertIn("entry is required", payload["errors"])

    def test_f_null_entry_rejected(self):
        case_id = self._new_case()
        append_payload = {
            "case_id": case_id,
            "field": "open_issues",
            "entry": None,
        }
        append_path = self._write_json(append_payload, "null_entry")

        output = self._capture_main(["main.py", "case-packet-append", str(append_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertFalse(payload["appended"])
        self.assertIn("entry must not be null", payload["errors"])

    def test_g_unsafe_case_id_rejected(self):
        append_payload = {
            "case_id": "../escape",
            "field": "open_issues",
            "entry": {"text": "x"},
        }
        append_path = self._write_json(append_payload, "unsafe")

        output = self._capture_main(["main.py", "case-packet-append", str(append_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertFalse(payload["appended"])

    def test_h_missing_case_packet_handled(self):
        append_payload = {
            "case_id": f"missing_{uuid4().hex[:8]}",
            "field": "open_issues",
            "entry": {"text": "x"},
        }
        append_path = self._write_json(append_payload, "missing_case")

        output = self._capture_main(["main.py", "case-packet-append", str(append_path)])
        self.assertIn("Case packet not found", output)

    def test_i_cli_append_success(self):
        case_id = self._new_case()
        append_payload = {
            "case_id": case_id,
            "field": "open_issues",
            "entry": {"text": "operator issue", "source": "operator"},
        }
        append_path = self._write_json(append_payload, "append_success")

        output = self._capture_main(["main.py", "case-packet-append", str(append_path)])
        payload = json.loads(output)

        self.assertTrue(payload["updated"])
        self.assertTrue(payload["appended"])
        self.assertEqual(payload["case_id"], case_id)
        self.assertEqual(payload["field"], "open_issues")
        self.assertEqual(payload["new_count"], 2)

    def test_j_cli_append_failure(self):
        case_id = self._new_case()
        append_payload = {
            "case_id": case_id,
            "field": "status",
            "entry": {"text": "blocked"},
        }
        append_path = self._write_json(append_payload, "append_fail")

        output = self._capture_main(["main.py", "case-packet-append", str(append_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertFalse(payload["appended"])

    def test_k_append_mutates_only_target_case_packet_file(self):
        case_id = self._new_case()
        before_surface = self._snapshot_mutation_surface()
        before_packet = load_case_packet(case_id)

        append_payload = {
            "case_id": case_id,
            "field": "open_issues",
            "entry": {"text": "only this packet"},
        }
        append_path = self._write_json(append_payload, "mutate_target")
        _ = self._capture_main(["main.py", "case-packet-append", str(append_path)])

        after_surface = self._snapshot_mutation_surface()
        after_packet = load_case_packet(case_id)

        self.assertEqual(before_surface, after_surface)
        self.assertEqual(len(after_packet["open_issues"]), len(before_packet["open_issues"]) + 1)

    def test_l_phase58_create_show_regression(self):
        case_id = f"case61_l_{uuid4().hex[:8]}"
        create_payload = {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute",
            "objective": "Contest charge",
            "status": "active",
            "next_step": "",
        }
        create_path = self._write_json(create_payload, "phase58_reg")

        created = json.loads(self._capture_main(["main.py", "case-packet-create", str(create_path)]))
        self.assertTrue(created["created"])

        shown = json.loads(self._capture_main(["main.py", "case-packet-show", case_id]))
        self.assertEqual(shown["case_id"], case_id)

    def test_m_phase59_summary_validate_regression(self):
        case_id = self._new_case()

        summary = json.loads(self._capture_main(["main.py", "case-packet-summary", case_id]))
        validation = json.loads(self._capture_main(["main.py", "case-packet-validate", case_id]))

        self.assertEqual(summary["case_id"], case_id)
        self.assertIn("readiness", summary)
        self.assertTrue(validation["valid"])

    def test_n_phase60_init_regression(self):
        case_id = f"case61_n_{uuid4().hex[:8]}"
        seed_payload = {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute",
            "objective": "Contest charge",
        }
        seed_path = self._write_json(seed_payload, "phase60_reg")

        initialized = json.loads(self._capture_main(["main.py", "case-packet-init", str(seed_path)]))
        self.assertTrue(initialized["created"])
        self.assertTrue(initialized["initialized"])


if __name__ == "__main__":
    unittest.main()
