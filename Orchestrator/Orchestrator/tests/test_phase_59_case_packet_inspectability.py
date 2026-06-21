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
    assess_case_packet_readiness,
    load_case_packet,
    normalize_case_packet,
    save_case_packet,
    summarize_case_packet,
    validate_case_packet,
)
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase59CasePacketInspectabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_dir = DATA_DIR / "phase59_case_packet_inputs"
        self.fixture_dir.mkdir(parents=True, exist_ok=True)

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
            "case_packets": self._count_json_files(CASE_PACKETS_DIR),
            "runs": self._count_json_files(RUNS_DIR),
            "tasks": self._count_json_files(TASKS_DIR),
            "artifacts": self._count_json_files(ARTIFACTS_DIR),
            "verifier_results": self._count_json_files(VERIFIER_RESULTS_DIR),
            "recommendations": self._count_json_files(DATA_DIR / "reviewer_recommendations"),
            "state_text": STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else "",
        }

    def _valid_payload(self, case_id: str) -> dict:
        return {
            "case_id": case_id,
            "case_type": "billing_dispute",
            "title": "Billing dispute",
            "objective": "Contest a charge",
            "counterparties": [],
            "source_materials": [],
            "extracted_facts": [],
            "timeline_events": [],
            "open_issues": [],
            "missing_evidence": [],
            "contradictions": [],
            "drafts": [],
            "decisions": [],
            "status": "active",
            "next_step": "",
        }

    def _persist(self, payload: dict) -> dict:
        packet = normalize_case_packet(payload)
        save_case_packet(packet)
        return packet

    def test_a_summary_includes_required_identity_and_state_fields(self):
        case_id = f"case59_a_{uuid4().hex[:8]}"
        packet = self._persist(self._valid_payload(case_id))

        summary = summarize_case_packet(packet)

        self.assertEqual(summary["case_id"], case_id)
        self.assertEqual(summary["case_type"], "billing_dispute")
        self.assertEqual(summary["title"], "Billing dispute")
        self.assertEqual(summary["objective"], "Contest a charge")
        self.assertEqual(summary["status"], "active")
        self.assertEqual(summary["next_step"], "")
        self.assertIn("validation", summary)
        self.assertIn("category_counts", summary)
        self.assertIn("populated_categories", summary)
        self.assertIn("empty_categories", summary)
        self.assertIn("readiness", summary)

    def test_b_category_counts_are_deterministic(self):
        case_id = f"case59_b_{uuid4().hex[:8]}"
        payload = self._valid_payload(case_id)
        payload["source_materials"] = ["invoice.pdf", "email.txt"]
        payload["open_issues"] = ["wrong amount"]
        packet = self._persist(payload)

        summary = summarize_case_packet(packet)
        counts = summary["category_counts"]

        self.assertEqual(counts["source_materials"], 2)
        self.assertEqual(counts["open_issues"], 1)
        self.assertEqual(counts["counterparties"], 0)

    def test_c_empty_and_populated_categories_are_deterministic(self):
        case_id = f"case59_c_{uuid4().hex[:8]}"
        payload = self._valid_payload(case_id)
        payload["source_materials"] = ["invoice.pdf"]
        payload["open_issues"] = ["wrong amount"]
        packet = self._persist(payload)

        summary = summarize_case_packet(packet)

        self.assertIn("source_materials", summary["populated_categories"])
        self.assertIn("open_issues", summary["populated_categories"])
        self.assertIn("counterparties", summary["empty_categories"])
        self.assertNotIn("source_materials", summary["empty_categories"])

    def test_d_invalid_packet_readiness_is_invalid(self):
        packet = normalize_case_packet(
            {
                "case_id": "",
                "case_type": "billing_dispute",
                "title": "",
                "objective": "",
                "status": "active",
                "next_step": "",
            }
        )

        readiness = assess_case_packet_readiness(packet)
        self.assertEqual(readiness["readiness"], "invalid")

    def test_e_skeletal_packet_readiness_is_skeletal(self):
        case_id = f"case59_e_{uuid4().hex[:8]}"
        packet = normalize_case_packet(self._valid_payload(case_id))

        readiness = assess_case_packet_readiness(packet)
        self.assertEqual(readiness["readiness"], "skeletal")

    def test_f_partially_populated_readiness(self):
        case_id = f"case59_f_{uuid4().hex[:8]}"
        payload = self._valid_payload(case_id)
        payload["source_materials"] = ["invoice.pdf"]
        packet = normalize_case_packet(payload)

        readiness = assess_case_packet_readiness(packet)
        self.assertEqual(readiness["readiness"], "partially_populated")

    def test_g_review_ready_readiness(self):
        case_id = f"case59_g_{uuid4().hex[:8]}"
        payload = self._valid_payload(case_id)
        payload["source_materials"] = ["invoice.pdf"]
        payload["open_issues"] = ["wrong amount"]
        payload["next_step"] = "request correction"
        packet = normalize_case_packet(payload)

        readiness = assess_case_packet_readiness(packet)
        self.assertEqual(readiness["readiness"], "review_ready")

    def test_h_cli_summary_prints_expected_json(self):
        case_id = f"case59_h_{uuid4().hex[:8]}"
        payload = self._valid_payload(case_id)
        payload["source_materials"] = ["invoice.pdf"]
        payload["open_issues"] = ["wrong amount"]
        payload["next_step"] = "request correction"
        self._persist(payload)

        output = self._capture_main(["main.py", "case-packet-summary", case_id])
        summary = json.loads(output)

        self.assertEqual(summary["case_id"], case_id)
        self.assertEqual(summary["readiness"]["readiness"], "review_ready")
        self.assertTrue(summary["validation"]["valid"])

    def test_i_cli_validate_prints_expected_json(self):
        case_id = f"case59_i_{uuid4().hex[:8]}"
        packet = self._persist(self._valid_payload(case_id))

        output = self._capture_main(["main.py", "case-packet-validate", case_id])
        validation = json.loads(output)

        self.assertEqual(validation, validate_case_packet(packet))

    def test_j_summary_and_validate_are_read_only(self):
        case_id = f"case59_j_{uuid4().hex[:8]}"
        self._persist(self._valid_payload(case_id))

        before = self._snapshot_mutation_surface()
        _ = self._capture_main(["main.py", "case-packet-summary", case_id])
        _ = self._capture_main(["main.py", "case-packet-validate", case_id])
        after = self._snapshot_mutation_surface()

        self.assertEqual(before, after)

    def test_k_phase58_create_show_behavior_remains_intact(self):
        case_id = f"case59_k_{uuid4().hex[:8]}"
        input_path = self.fixture_dir / f"case59_k_{uuid4().hex[:8]}.json"
        input_path.write_text(json.dumps(self._valid_payload(case_id), indent=2), encoding="utf-8")

        create_output = self._capture_main(["main.py", "case-packet-create", str(input_path)])
        create_payload = json.loads(create_output)
        self.assertTrue(create_payload["created"])
        self.assertEqual(create_payload["case_id"], case_id)

        show_output = self._capture_main(["main.py", "case-packet-show", case_id])
        show_payload = json.loads(show_output)
        self.assertEqual(show_payload["case_id"], case_id)


if __name__ == "__main__":
    unittest.main()
