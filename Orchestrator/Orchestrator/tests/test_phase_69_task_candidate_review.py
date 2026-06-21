import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
import orchestrator.case_packet_persistence as persistence
import orchestrator.case_packet_task_candidate_review as review
from orchestrator.case_packet_task_candidate_review import review_persisted_case_packet_task_candidate
from orchestrator.intake import (
    authorize_case_packet_creation_from_seed_review,
    judge_intake,
    review_case_packet_seed_candidate,
)
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase69TaskCandidateReviewTests(unittest.TestCase):
    def _write_temp_input(self, payload: dict) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        with handle:
            json.dump(payload, handle, indent=2)
        return Path(handle.name)

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

    def _snapshot_repo_mutation_surface(self, case_dir: Path) -> dict[str, int | str]:
        return {
            "runs": self._count_json_files(RUNS_DIR),
            "tasks": self._count_json_files(TASKS_DIR),
            "artifacts": self._count_json_files(ARTIFACTS_DIR),
            "verifier_results": self._count_json_files(VERIFIER_RESULTS_DIR),
            "case_packets": self._count_json_files(case_dir),
            "recommendations": self._count_json_files(DATA_DIR / "reviewer_recommendations"),
            "state_text": STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else "",
        }

    def _proceed_input(self) -> dict:
        return {
            "objective_text": "Summarize the provided release notes into a short report.",
            "provided_artifacts": ["release_notes.md"],
            "confirmed_context": {
                "required_artifacts": ["release_notes.md"],
                "source_format": "markdown",
                "output_format": "summary",
            },
            "available_capabilities": ["local_files"],
        }

    def _phase67_authorization(self) -> dict:
        intake_result = judge_intake(self._proceed_input())
        seed_review = review_case_packet_seed_candidate(intake_result)
        return authorize_case_packet_creation_from_seed_review(
            {
                "seed_review_result": seed_review,
                "operator_case_packet_creation_decision": "authorize_case_packet_creation",
            }
        )

    def _persisted_packet_result(self, case_id: str, case_dir: Path) -> dict:
        payload = {
            "phase67_creation_authorization_result": self._phase67_authorization(),
            "operator_case_packet_persistence_decision": "authorize_case_packet_persistence",
            "case_id": case_id,
        }
        with patch.object(persistence, "CASE_PACKETS_DIR", case_dir):
            return persistence.persist_case_packet_from_creation_authorization(payload)

    def test_a_valid_persisted_phase68_case_packet_is_task_candidate_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)
            persist_result = self._persisted_packet_result("phase69_ready_case", case_dir)

            with patch.object(review, "CASE_PACKETS_DIR", case_dir):
                result = review_persisted_case_packet_task_candidate({"case_id": "phase69_ready_case"})

            self.assertEqual(persist_result.get("case_packet_persistence"), "persisted")
            self.assertEqual(result.get("task_candidate_status"), "task_candidate_ready")
            self.assertEqual(result.get("case_id"), "phase69_ready_case")
            self.assertTrue(result.get("case_packet_task_candidate_review"))
            self.assertEqual(result.get("next_action"), "operator_may_choose_explicit_task_creation_authorization_boundary")
            self.assertFalse(result.get("task_created"))
            self.assertFalse(result.get("planner_invoked"))
            self.assertFalse(result.get("runtime_executed"))
            self.assertFalse(result.get("model_executed"))
            self.assertFalse(result.get("platform_invoked"))
            self.assertFalse(result.get("mutation_performed"))
            self.assertFalse(result.get("execution_performed"))
            self.assertEqual(result.get("blocked_conditions"), [])
            self.assertEqual(
                result.get("candidate_summary", {}).get("declared_or_inferred_file_surface", {}).get("files"),
                ["release_notes.md"],
            )

    def test_b_valid_persisted_packet_missing_file_surface_needs_operator_clarification(self):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)
            persist_result = self._persisted_packet_result("phase69_clarify_case", case_dir)
            packet_path = Path(persist_result["path"])
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            packet["source_materials"] = []
            packet_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")

            with patch.object(review, "CASE_PACKETS_DIR", case_dir):
                result = review_persisted_case_packet_task_candidate({"case_id": "phase69_clarify_case"})

            self.assertEqual(result.get("task_candidate_status"), "needs_operator_clarification")
            self.assertIn("source_materials_or_file_surface", result.get("missing_requirements", []))
            self.assertFalse(result.get("task_created"))

    def test_c_missing_case_packet_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(review, "CASE_PACKETS_DIR", Path(directory)):
                result = review_persisted_case_packet_task_candidate({"case_id": "phase69_missing_case"})

        self.assertEqual(result.get("task_candidate_status"), "blocked")
        self.assertIn("case_packet_not_found", result.get("blocked_conditions", []))

    def test_d_invalid_case_packet_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)
            packet_path = case_dir / "phase69_invalid_case.json"
            packet_path.write_text(
                json.dumps(
                    {
                        "case_id": "phase69_invalid_case",
                        "case_type": "orchestrator_intake",
                        "title": "Invalid packet",
                        "objective": "",
                        "status": "created",
                        "next_step": "operator_review_case_packet_before_task_creation",
                        "counterparties": [],
                        "source_materials": ["release_notes.md"],
                        "extracted_facts": [],
                        "timeline_events": [],
                        "open_issues": [],
                        "missing_evidence": [],
                        "contradictions": [],
                        "drafts": [],
                        "decisions": [],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            with patch.object(review, "CASE_PACKETS_DIR", case_dir):
                result = review_persisted_case_packet_task_candidate({"case_id": "phase69_invalid_case"})

        self.assertEqual(result.get("task_candidate_status"), "blocked")
        self.assertIn("objective is required", result.get("blocked_conditions", []))

    def test_e_task_or_planner_implication_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)
            persist_result = self._persisted_packet_result("phase69_task_planner_block", case_dir)
            packet_path = Path(persist_result["path"])
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            packet["task_created"] = True
            packet["planner_invoked"] = True
            packet_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")

            with patch.object(review, "CASE_PACKETS_DIR", case_dir):
                result = review_persisted_case_packet_task_candidate({"case_id": "phase69_task_planner_block"})

        self.assertEqual(result.get("task_candidate_status"), "blocked")
        self.assertIn("case_packet_implies_task_creation", result.get("blocked_conditions", []))
        self.assertIn("case_packet_implies_planner_invocation", result.get("blocked_conditions", []))

    def test_f_runtime_model_platform_request_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)
            self._persisted_packet_result("phase69_runtime_block", case_dir)

            with patch.object(review, "CASE_PACKETS_DIR", case_dir):
                result = review_persisted_case_packet_task_candidate(
                    {
                        "case_id": "phase69_runtime_block",
                        "requested_behavior": "review packet then run model through OpenClaw bridge",
                    }
                )

        self.assertEqual(result.get("task_candidate_status"), "blocked")
        self.assertIn("unsupported_bundled_behavior_request", result.get("blocked_conditions", []))

    def test_g_direct_case_packet_without_product_store_record_is_blocked(self):
        direct_packet = {
            "case_id": "phase69_direct_case",
            "case_type": "orchestrator_intake",
            "title": "Direct packet",
            "objective": "Summarize one file.",
            "status": "created",
            "next_step": "operator_review_case_packet_before_task_creation",
            "counterparties": [],
            "source_materials": ["release_notes.md"],
            "extracted_facts": [],
            "timeline_events": [],
            "open_issues": [],
            "missing_evidence": [],
            "contradictions": [],
            "drafts": [],
            "decisions": [],
        }

        result = review_persisted_case_packet_task_candidate({"case_packet": direct_packet})

        self.assertEqual(result.get("task_candidate_status"), "blocked")
        self.assertIn("case_packet_not_loaded_from_product_case_packet_store", result.get("blocked_conditions", []))

    def test_h_cli_review_is_read_only_and_matches_direct_result(self):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)
            self._persisted_packet_result("phase69_cli_case", case_dir)
            payload = {"case_id": "phase69_cli_case"}
            input_path = self._write_temp_input(payload)

            with patch.object(review, "CASE_PACKETS_DIR", case_dir):
                before = self._snapshot_repo_mutation_surface(case_dir)
                text = self._capture_main(["main.py", "case-packet-task-candidate-review", str(input_path)])
                after = self._snapshot_repo_mutation_surface(case_dir)
                cli_payload = json.loads(text)
                direct = review_persisted_case_packet_task_candidate(payload)

        self.assertEqual(cli_payload, direct)
        self.assertEqual(cli_payload.get("task_candidate_status"), "task_candidate_ready")
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
