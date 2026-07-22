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
    save_case_packet,
    summarize_case_packet,
    update_case_packet_orientation,
    validate_case_packet,
)
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase62CasePacketOrientationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_dir = DATA_DIR / "phase62_case_packet_inputs"
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
            "case_packets": self._count_json_files(CASE_PACKETS_DIR),
        }

    def _seed(self, case_id: str) -> dict:
        return {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute",
            "objective": "Contest invoice",
            "status": "active",
            "next_step": "Collect documents",
            "counterparties": ["Vendor X"],
        }

    def _create_case_packet(self, case_id: str) -> dict:
        packet = initialize_case_packet_from_seed(self._seed(case_id))
        save_case_packet(packet)
        return packet

    def test_01_update_status_only(self):
        case_id = f"case62_status_{uuid4().hex[:8]}"
        packet = self._create_case_packet(case_id)

        updated = update_case_packet_orientation(packet, {"status": "in_review"})

        self.assertEqual(updated["status"], "in_review")
        self.assertEqual(updated["next_step"], packet["next_step"])

    def test_02_update_next_step_only(self):
        case_id = f"case62_next_{uuid4().hex[:8]}"
        packet = self._create_case_packet(case_id)

        updated = update_case_packet_orientation(packet, {"next_step": "Send dispute letter"})

        self.assertEqual(updated["next_step"], "Send dispute letter")
        self.assertEqual(updated["status"], packet["status"])

    def test_03_update_both_status_and_next_step(self):
        case_id = f"case62_both_{uuid4().hex[:8]}"
        packet = self._create_case_packet(case_id)

        updated = update_case_packet_orientation(packet, {"status": "paused", "next_step": "Await vendor response"})

        self.assertEqual(updated["status"], "paused")
        self.assertEqual(updated["next_step"], "Await vendor response")

    def test_04_unknown_field_rejected(self):
        case_id = f"case62_unknown_{uuid4().hex[:8]}"
        packet = self._create_case_packet(case_id)

        with self.assertRaisesRegex(ValueError, "field is not orientation-updatable"):
            update_case_packet_orientation(packet, {"priority": "high"})

    def test_05_forbidden_scalar_field_rejected(self):
        case_id = f"case62_forbidden_scalar_{uuid4().hex[:8]}"
        self._create_case_packet(case_id)
        input_path = self._write_json({"case_id": case_id, "title": "changed", "status": "active"}, "forbidden_scalar")

        output = self._capture_main(["main.py", "case-packet-orient", str(input_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertIn("field is not orientation-updatable: title", payload["errors"])

    def test_06_list_field_rejected(self):
        case_id = f"case62_forbidden_list_{uuid4().hex[:8]}"
        self._create_case_packet(case_id)
        input_path = self._write_json(
            {"case_id": case_id, "source_materials": ["x"], "status": "active"}, "forbidden_list"
        )

        output = self._capture_main(["main.py", "case-packet-orient", str(input_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertIn("field is list-based and not orientation-updatable: source_materials", payload["errors"])

    def test_07_missing_orientation_fields_rejected(self):
        input_path = self._write_json({"case_id": f"case62_missing_{uuid4().hex[:8]}"}, "missing_orientation")

        output = self._capture_main(["main.py", "case-packet-orient", str(input_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertIn("at least one of status or next_step is required", payload["errors"])

    def test_08_null_orientation_value_rejected(self):
        case_id = f"case62_null_{uuid4().hex[:8]}"
        self._create_case_packet(case_id)
        input_path = self._write_json({"case_id": case_id, "status": None}, "null_value")

        output = self._capture_main(["main.py", "case-packet-orient", str(input_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertEqual(payload["error"], "status must not be null")

    def test_09_empty_or_whitespace_orientation_value_rejected(self):
        case_id = f"case62_empty_{uuid4().hex[:8]}"
        self._create_case_packet(case_id)
        input_path = self._write_json({"case_id": case_id, "next_step": "   "}, "empty_value")

        output = self._capture_main(["main.py", "case-packet-orient", str(input_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertEqual(payload["error"], "next_step must not be empty")

    def test_10_non_string_orientation_value_rejected(self):
        case_id = f"case62_nonstring_{uuid4().hex[:8]}"
        self._create_case_packet(case_id)
        input_path = self._write_json({"case_id": case_id, "status": 123}, "non_string")

        output = self._capture_main(["main.py", "case-packet-orient", str(input_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertEqual(payload["error"], "status must be a string")

    def test_11_unsafe_case_id_rejected(self):
        input_path = self._write_json({"case_id": "../escape", "status": "active"}, "unsafe_case_id")

        output = self._capture_main(["main.py", "case-packet-orient", str(input_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertEqual(payload["error"], "Unsafe case_id")

    def test_12_missing_case_packet_handled(self):
        case_id = f"case62_missing_packet_{uuid4().hex[:8]}"
        input_path = self._write_json({"case_id": case_id, "status": "active"}, "missing_packet")

        output = self._capture_main(["main.py", "case-packet-orient", str(input_path)])
        self.assertIn(f"Case packet not found: {case_id}", output)

    def test_13_cli_orientation_success(self):
        case_id = f"case62_cli_success_{uuid4().hex[:8]}"
        self._create_case_packet(case_id)
        input_path = self._write_json(
            {"case_id": case_id, "status": "in_review", "next_step": "Wait for documents"}, "cli_success"
        )

        output = self._capture_main(["main.py", "case-packet-orient", str(input_path)])
        payload = json.loads(output)

        self.assertTrue(payload["updated"])
        self.assertTrue(payload["oriented"])
        self.assertEqual(payload["case_id"], case_id)
        self.assertEqual(payload["updated_fields"], ["status", "next_step"])
        self.assertTrue(payload["validation"]["valid"])

        loaded = load_case_packet(case_id)
        self.assertEqual(loaded["status"], "in_review")
        self.assertEqual(loaded["next_step"], "Wait for documents")

    def test_14_cli_orientation_failure(self):
        case_id = f"case62_cli_failure_{uuid4().hex[:8]}"
        self._create_case_packet(case_id)
        input_path = self._write_json({"case_id": case_id, "status": "active", "bad": "x"}, "cli_failure")

        output = self._capture_main(["main.py", "case-packet-orient", str(input_path)])
        payload = json.loads(output)

        self.assertFalse(payload["updated"])
        self.assertIn("unknown field: bad", payload["errors"])

    def test_15_orientation_mutates_only_target_case_packet_file(self):
        target_case_id = f"case62_target_{uuid4().hex[:8]}"
        other_case_id = f"case62_other_{uuid4().hex[:8]}"
        self._create_case_packet(target_case_id)
        other_before = self._create_case_packet(other_case_id)

        input_path = self._write_json(
            {"case_id": target_case_id, "status": "resolved", "next_step": "Archive packet"}, "mutation_target"
        )

        before = self._snapshot_mutation_surface()
        output = self._capture_main(["main.py", "case-packet-orient", str(input_path)])
        after = self._snapshot_mutation_surface()

        payload = json.loads(output)
        self.assertTrue(payload["updated"])

        self.assertEqual(before["runs"], after["runs"])
        self.assertEqual(before["tasks"], after["tasks"])
        self.assertEqual(before["artifacts"], after["artifacts"])
        self.assertEqual(before["verifier_results"], after["verifier_results"])
        self.assertEqual(before["recommendations"], after["recommendations"])
        self.assertEqual(before["state_text"], after["state_text"])
        self.assertEqual(before["case_packets"], after["case_packets"])

        target_after = load_case_packet(target_case_id)
        self.assertEqual(target_after["status"], "resolved")
        self.assertEqual(target_after["next_step"], "Archive packet")

        other_after = load_case_packet(other_case_id)
        self.assertEqual(other_before, other_after)

    def test_16_phase58_create_show_behavior_still_passes(self):
        case_id = f"case62_reg58_{uuid4().hex[:8]}"
        payload = {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute",
            "objective": "Contest invoice",
            "status": "active",
            "next_step": "Collect documents",
        }
        create_input = self._write_json(payload, "reg58_create")

        create_output = self._capture_main(["main.py", "case-packet-create", str(create_input)])
        create_result = json.loads(create_output)
        self.assertTrue(create_result["created"])

        show_output = self._capture_main(["main.py", "case-packet-show", case_id])
        show_result = json.loads(show_output)
        self.assertEqual(show_result["case_id"], case_id)

    def test_17_phase59_summary_validate_readiness_still_passes(self):
        case_id = f"case62_reg59_{uuid4().hex[:8]}"
        packet = initialize_case_packet_from_seed(self._seed(case_id))
        packet["source_materials"] = ["invoice.pdf"]
        packet["open_issues"] = ["wrong charge"]
        packet["next_step"] = "Send dispute"
        save_case_packet(packet)

        summary = summarize_case_packet(load_case_packet(case_id))
        self.assertEqual(summary["readiness"]["readiness"], "review_ready")

        validation = validate_case_packet(load_case_packet(case_id))
        self.assertTrue(validation["valid"])

    def test_18_phase60_init_behavior_still_passes(self):
        case_id = f"case62_reg60_{uuid4().hex[:8]}"
        seed_path = self._write_json(
            {
                "case_id": case_id,
                "case_type": "billing_dispute",
                "title": "Billing dispute",
                "objective": "Contest invoice",
            },
            "reg60_seed",
        )

        output = self._capture_main(["main.py", "case-packet-init", str(seed_path)])
        result = json.loads(output)
        self.assertTrue(result["created"])
        self.assertTrue(result["initialized"])

    def test_19_phase61_append_behavior_still_passes(self):
        case_id = f"case62_reg61_{uuid4().hex[:8]}"
        self._create_case_packet(case_id)
        append_input = self._write_json(
            {
                "case_id": case_id,
                "field": "open_issues",
                "entry": {"text": "Charge date mismatch", "source": "operator"},
            },
            "reg61_append",
        )

        output = self._capture_main(["main.py", "case-packet-append", str(append_input)])
        result = json.loads(output)
        self.assertTrue(result["updated"])
        self.assertTrue(result["appended"])

        packet = load_case_packet(case_id)
        self.assertTrue(packet["open_issues"])


if __name__ == "__main__":
    unittest.main()
