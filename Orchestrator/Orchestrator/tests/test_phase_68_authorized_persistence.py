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
from orchestrator.case_packet import CASE_PACKETS_DIR
from orchestrator.case_packet_persistence import persist_case_packet_from_creation_authorization
from orchestrator.intake import (
    authorize_case_packet_creation_from_seed_review,
    judge_intake,
    review_case_packet_seed_candidate,
)
from orchestrator.paths import ARTIFACTS_DIR, DATA_DIR, RUNS_DIR, TASKS_DIR, VERIFIER_RESULTS_DIR
from orchestrator.state import STATE_PATH


class Phase68AuthorizedPersistenceTests(unittest.TestCase):
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

    def _snapshot_repo_mutation_surface(self) -> dict[str, int | str]:
        return {
            "runs": self._count_json_files(RUNS_DIR),
            "tasks": self._count_json_files(TASKS_DIR),
            "artifacts": self._count_json_files(ARTIFACTS_DIR),
            "verifier_results": self._count_json_files(VERIFIER_RESULTS_DIR),
            "case_packets": self._count_json_files(CASE_PACKETS_DIR),
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

    def _valid_persistence_input(self, case_id: str) -> dict:
        return {
            "phase67_creation_authorization_result": self._phase67_authorization(),
            "operator_case_packet_persistence_decision": "authorize_case_packet_persistence",
            "case_id": case_id,
        }

    def test_a_valid_phase67_authorization_plus_explicit_persistence_approval_persists_one_case_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)
            payload = self._valid_persistence_input("phase68_valid_case")

            with patch.object(persistence, "CASE_PACKETS_DIR", case_dir):
                result = persist_case_packet_from_creation_authorization(payload)

            self.assertEqual(result.get("case_packet_persistence"), "persisted")
            self.assertTrue(result.get("case_packet_persisted"))
            self.assertTrue(result.get("case_packet_created"))
            self.assertEqual(result.get("case_id"), "phase68_valid_case")
            self.assertEqual(len(list(case_dir.glob("*.json"))), 1)

            packet = json.loads(Path(result["path"]).read_text(encoding="utf-8"))
            self.assertEqual(packet["case_id"], "phase68_valid_case")
            self.assertEqual(packet["objective"], "Summarize the provided release notes into a short report.")
            self.assertEqual(packet["source_materials"], ["release_notes.md"])
            self.assertEqual(packet["source_intake_linkage"], "judge_intake.proceed")
            self.assertEqual(packet["persistence_status"], "persisted")
            self.assertIn("phase66_seed_review_summary", packet)
            self.assertIn("phase67_authorization_summary", packet)

            self.assertFalse(result.get("task_created"))
            self.assertFalse(result.get("planner_invoked"))
            self.assertFalse(result.get("runtime_executed"))
            self.assertFalse(result.get("model_executed"))
            self.assertFalse(result.get("platform_invoked"))

    def test_b_valid_phase67_authorization_without_persistence_approval_needs_operator_decision(self):
        payload = {
            "phase67_creation_authorization_result": self._phase67_authorization(),
            "case_id": "phase68_needs_decision",
        }

        result = persist_case_packet_from_creation_authorization(payload)

        self.assertEqual(result.get("case_packet_persistence"), "needs_operator_decision")
        self.assertFalse(result.get("case_packet_persisted"))
        self.assertIn("operator_case_packet_persistence_decision", result.get("missing_requirements", []))

    def test_c_non_authorized_phase67_result_is_blocked(self):
        authorization = dict(self._phase67_authorization())
        authorization["creation_authorization"] = "needs_operator_decision"
        authorization["case_packet_creation_authorized"] = False

        result = persist_case_packet_from_creation_authorization(
            {
                "phase67_creation_authorization_result": authorization,
                "operator_case_packet_persistence_decision": "authorize_case_packet_persistence",
                "case_id": "phase68_blocked_non_authorized",
            }
        )

        self.assertEqual(result.get("case_packet_persistence"), "blocked")
        self.assertIn("phase67_creation_authorization_not_authorized", result.get("blocked_conditions", []))
        self.assertFalse(result.get("case_packet_persisted"))

    def test_d_input_implying_prior_case_packet_persistence_is_blocked(self):
        authorization = dict(self._phase67_authorization())
        authorization["case_packet_persisted"] = True

        result = persist_case_packet_from_creation_authorization(
            {
                "phase67_creation_authorization_result": authorization,
                "operator_case_packet_persistence_decision": "authorize_case_packet_persistence",
                "case_id": "phase68_prior_persistence",
            }
        )

        self.assertEqual(result.get("case_packet_persistence"), "blocked")
        self.assertIn("authorization_implies_case_packet_persistence", result.get("blocked_conditions", []))

    def test_e_task_or_planner_implication_is_blocked(self):
        authorization = dict(self._phase67_authorization())
        authorization["task_created"] = True
        authorization["planner_invoked"] = True

        result = persist_case_packet_from_creation_authorization(
            {
                "phase67_creation_authorization_result": authorization,
                "operator_case_packet_persistence_decision": "authorize_case_packet_persistence",
                "case_id": "phase68_task_planner_block",
            }
        )

        self.assertEqual(result.get("case_packet_persistence"), "blocked")
        self.assertIn("authorization_implies_task_creation", result.get("blocked_conditions", []))
        self.assertIn("authorization_implies_planner_invocation", result.get("blocked_conditions", []))

    def test_f_runtime_model_platform_request_is_blocked(self):
        result = persist_case_packet_from_creation_authorization(
            {
                "phase67_creation_authorization_result": self._phase67_authorization(),
                "operator_case_packet_persistence_decision": "authorize_case_packet_persistence",
                "case_id": "phase68_runtime_block",
                "requested_behavior": "persist case packet and run model through OpenClaw bridge",
            }
        )

        self.assertEqual(result.get("case_packet_persistence"), "blocked")
        self.assertIn("unsupported_bundled_behavior_request", result.get("blocked_conditions", []))

    def test_g_unsafe_case_id_is_blocked(self):
        result = persist_case_packet_from_creation_authorization(
            {
                "phase67_creation_authorization_result": self._phase67_authorization(),
                "operator_case_packet_persistence_decision": "authorize_case_packet_persistence",
                "case_id": "../escape",
            }
        )

        self.assertEqual(result.get("case_packet_persistence"), "blocked")
        self.assertIn("unsafe_case_id", result.get("blocked_conditions", []))

    def test_h_existing_case_packet_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)
            existing = case_dir / "phase68_existing.json"
            existing.write_text(json.dumps({"case_id": "phase68_existing"}), encoding="utf-8")

            with patch.object(persistence, "CASE_PACKETS_DIR", case_dir):
                result = persist_case_packet_from_creation_authorization(
                    self._valid_persistence_input("phase68_existing")
                )

            self.assertEqual(result.get("case_packet_persistence"), "blocked")
            self.assertIn("case_packet_already_exists", result.get("blocked_conditions", []))
            self.assertEqual(json.loads(existing.read_text(encoding="utf-8")), {"case_id": "phase68_existing"})

    def test_i_cli_persistence_is_narrow_and_writes_only_to_patched_case_packet_store(self):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)
            payload = self._valid_persistence_input("phase68_cli_valid")
            input_path = self._write_temp_input(payload)

            before = self._snapshot_repo_mutation_surface()
            with patch.object(persistence, "CASE_PACKETS_DIR", case_dir):
                text = self._capture_main(["main.py", "case-packet-persist-authorized", str(input_path)])
            after = self._snapshot_repo_mutation_surface()

            cli_payload = json.loads(text)
            self.assertEqual(cli_payload["case_packet_persistence"], "persisted")
            self.assertTrue(cli_payload["case_packet_persisted"])
            self.assertEqual(len(list(case_dir.glob("*.json"))), 1)
            self.assertEqual(before, after)
            self.assertFalse(cli_payload["task_created"])
            self.assertFalse(cli_payload["planner_invoked"])
            self.assertFalse(cli_payload["runtime_executed"])
            self.assertFalse(cli_payload["model_executed"])
            self.assertFalse(cli_payload["platform_invoked"])


if __name__ == "__main__":
    unittest.main()
