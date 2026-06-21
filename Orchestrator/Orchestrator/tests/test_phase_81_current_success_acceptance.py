import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.current_success_acceptance as acceptance
import orchestrator.current_success_result_review as result_review
import orchestrator.run_manager as run_manager
from orchestrator.current_success_acceptance import record_current_success_result_acceptance
from orchestrator.current_success_result_review import review_current_success_task_result
from orchestrator.task_schema import Task


class Phase81CurrentSuccessAcceptanceTests(unittest.TestCase):
    def _task(self, status="completed"):
        return Task(
            id="task_phase81",
            run_id="run_phase81",
            title="Phase 81 eligible completed task",
            role="coder",
            status=status,
            dependencies=[],
            success_criteria=["Write bounded output."],
            files_in_scope=["demo/phase81.py"],
            retry_count=0,
            expected_output="PHASE81_ACCEPTANCE",
            execution_artifact_id="artifact_phase81",
            verification_checks=[{"check": "file_contains_text", "target": "demo/phase81.py", "text": "PHASE81_ACCEPTANCE"}],
        )

    def _acceptance_input(self, **overrides):
        payload = {
            "task_id": "task_phase81",
            "accepted": True,
            "operator_note": "Accepted as bounded current-state success under the deterministic-provider caveat.",
            "verification_caveat_acknowledged": True,
            "provider_caveat_acknowledged": True,
        }
        payload.update(overrides)
        return payload

    def _write_supporting_records(self, tasks: Path, artifacts: Path, verifiers: Path, status="completed", overall_passed=True):
        run_manager.save_task(self._task(status=status))
        (artifacts / "artifact_phase81.json").write_text(
            json.dumps(
                {
                    "artifact_id": "artifact_phase81",
                    "task_id": "task_phase81",
                    "run_id": "run_phase81",
                    "role": "coder",
                    "status": "success",
                    "output": "PHASE81_ACCEPTANCE",
                }
            ),
            encoding="utf-8",
        )
        (verifiers / "task_phase81_20260612T000000000000Z.json").write_text(
            json.dumps(
                {
                    "task_id": "task_phase81",
                    "run_id": "run_phase81",
                    "verification_result": {
                        "overall_passed": overall_passed,
                        "checks": [
                            {
                                "name": "file_contains_text",
                                "passed": overall_passed,
                                "message": "bounded verification",
                                "evidence": {},
                            }
                        ],
                        "messages": ["bounded verification"],
                    },
                }
            ),
            encoding="utf-8",
        )

    def test_acceptance_record_is_persisted_without_execution_or_mutation_flags(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = root / "tasks"
            artifacts = root / "artifacts"
            verifiers = root / "verifier_results"
            records = root / "acceptance_records"
            tasks.mkdir()
            artifacts.mkdir()
            verifiers.mkdir()

            with patch.object(run_manager, "TASKS_DIR", tasks), \
                 patch.object(result_review, "ARTIFACTS_DIR", artifacts), \
                 patch.object(result_review, "VERIFIER_RESULTS_DIR", verifiers), \
                 patch.object(result_review, "ACCEPTANCE_RECORDS_DIR", records), \
                 patch.object(acceptance, "ACCEPTANCE_RECORDS_DIR", records):
                self._write_supporting_records(tasks, artifacts, verifiers)
                result = record_current_success_result_acceptance(self._acceptance_input())
                followup_review = review_current_success_task_result({"task_id": "task_phase81"})

            self.assertTrue(result.get("current_success_acceptance_record_surface"))
            self.assertTrue(result.get("acceptance_record_created"))
            self.assertTrue(result.get("accepted"))
            self.assertEqual(result.get("result_classification_accepted"), "completed_current_state_success")
            self.assertFalse(result.get("task_executed"))
            self.assertFalse(result.get("provider_executed"))
            self.assertFalse(result.get("model_executed"))
            self.assertFalse(result.get("runtime_executed"))
            self.assertTrue(Path(result["acceptance_record_path"]).exists())
            self.assertTrue(followup_review.get("acceptance_summary", {}).get("acceptance_record_present"))
            self.assertTrue(followup_review.get("acceptance_summary", {}).get("accepted"))

            persisted = json.loads(Path(result["acceptance_record_path"]).read_text(encoding="utf-8"))
            self.assertTrue(persisted.get("accepted"))
            self.assertEqual(persisted.get("task_id"), "task_phase81")
            self.assertEqual(persisted.get("execution_artifact_id"), "artifact_phase81")
            self.assertTrue(persisted.get("verification_caveat_acknowledged"))
            self.assertTrue(persisted.get("provider_caveat_acknowledged"))
            self.assertFalse(persisted.get("no_execution_flags", {}).get("provider_executed"))

    def test_acceptance_requires_explicit_operator_acknowledgements(self):
        result = record_current_success_result_acceptance(
            self._acceptance_input(
                accepted=False,
                operator_note="",
                verification_caveat_acknowledged=False,
                provider_caveat_acknowledged=False,
            )
        )

        self.assertFalse(result.get("acceptance_record_created"))
        self.assertIn("explicit_acceptance_required", result.get("blocked_conditions", []))
        self.assertIn("operator_note_required", result.get("blocked_conditions", []))
        self.assertIn("verification_caveat_acknowledgement_required", result.get("blocked_conditions", []))
        self.assertIn("provider_caveat_acknowledgement_required", result.get("blocked_conditions", []))

    def test_acceptance_blocks_when_current_success_review_is_not_completed_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = root / "tasks"
            artifacts = root / "artifacts"
            verifiers = root / "verifier_results"
            records = root / "acceptance_records"
            tasks.mkdir()
            artifacts.mkdir()
            verifiers.mkdir()

            with patch.object(run_manager, "TASKS_DIR", tasks), \
                 patch.object(result_review, "ARTIFACTS_DIR", artifacts), \
                 patch.object(result_review, "VERIFIER_RESULTS_DIR", verifiers), \
                 patch.object(result_review, "ACCEPTANCE_RECORDS_DIR", records), \
                 patch.object(acceptance, "ACCEPTANCE_RECORDS_DIR", records):
                self._write_supporting_records(tasks, artifacts, verifiers, status="verification_failed", overall_passed=False)
                result = record_current_success_result_acceptance(self._acceptance_input())

            self.assertFalse(result.get("acceptance_record_created"))
            self.assertIn("completed_current_state_success_required", result.get("blocked_conditions", []))
            self.assertIn("deterministic_verification_pass_required", result.get("blocked_conditions", []))
            self.assertFalse(records.exists())

    def test_acceptance_cli_dispatch_reaches_acceptance_input_reader(self):
        import subprocess
        import sys

        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing_acceptance_input.json"
            result = subprocess.run(
                [sys.executable, "-B", "main.py", "current-success-result-accept", str(missing)],
                cwd=Path(__file__).resolve().parent.parent,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Current success result acceptance input file not found", result.stdout)
        self.assertNotIn("Usage: python main.py <init|status|new-run|next|verify", result.stdout)


if __name__ == "__main__":
    unittest.main()

