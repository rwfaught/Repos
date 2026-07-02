import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.current_success_result_review as result_review
import orchestrator.operator_packet_result_decision as decision
import orchestrator.run_manager as run_manager
from orchestrator.current_success_result_review import review_current_success_task_result
from orchestrator.operator_packet_result_decision import record_packet_result_operator_decision
from orchestrator.task_schema import Task


class Phase283PacketCliOperatorAcceptanceRecordTests(unittest.TestCase):
    def _task(self, status="completed", task_id="task_phase283"):
        return Task(
            id=task_id,
            run_id="run_phase283",
            title="Phase 283 packet result decision task",
            role="coder",
            status=status,
            dependencies=[],
            success_criteria=["Produce bounded packet output."],
            files_in_scope=["outputs/phase283.txt"],
            retry_count=0,
            expected_output="PHASE283_PACKET_DECISION",
            execution_artifact_id="artifact_phase283",
            verification_checks=[
                {
                    "check": "file_contains_text",
                    "target": "outputs/phase283.txt",
                    "text": "PHASE283_PACKET_DECISION",
                }
            ],
        )

    def _decision_input(self, **overrides):
        payload = {
            "operator_decision": "accepted",
            "packet_id": "packet_phase283",
            "task_id": "task_phase283",
            "operator_note": "Accepted as a bounded packet CLI result under recorded caveats.",
        }
        payload.update(overrides)
        return payload

    def _write_supporting_records(self, artifacts: Path, verifiers: Path, status="completed", overall_passed=True):
        run_manager.save_task(self._task(status=status))
        (artifacts / "artifact_phase283.json").write_text(
            json.dumps(
                {
                    "artifact_id": "artifact_phase283",
                    "task_id": "task_phase283",
                    "run_id": "run_phase283",
                    "role": "coder",
                    "status": "success",
                    "output": "PHASE283_PACKET_DECISION",
                }
            ),
            encoding="utf-8",
        )
        (verifiers / "task_phase283_20260701T000000000000Z.json").write_text(
            json.dumps(
                {
                    "task_id": "task_phase283",
                    "run_id": "run_phase283",
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

    def _patched_stores(self):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        tasks = root / "tasks"
        artifacts = root / "artifacts"
        verifiers = root / "verifier_results"
        decisions = root / "packet_operator_decision_records"
        for path in (tasks, artifacts, verifiers):
            path.mkdir()
        patchers = [
            patch.object(run_manager, "TASKS_DIR", tasks),
            patch.object(result_review, "ARTIFACTS_DIR", artifacts),
            patch.object(result_review, "VERIFIER_RESULTS_DIR", verifiers),
            patch.object(result_review, "PACKET_OPERATOR_DECISION_RECORDS_DIR", decisions),
            patch.object(decision, "PACKET_OPERATOR_DECISION_RECORDS_DIR", decisions),
        ]
        return directory, tasks, artifacts, verifiers, decisions, patchers

    def test_successful_acceptance_record_persistence_links_evidence_and_non_proofs(self):
        directory, _tasks, artifacts, verifiers, decisions, patchers = self._patched_stores()
        with directory:
            with patchers[0], patchers[1], patchers[2], patchers[3], patchers[4]:
                self._write_supporting_records(artifacts, verifiers)
                result = record_packet_result_operator_decision(self._decision_input())
                followup_review = review_current_success_task_result({"task_id": "task_phase283"})

            self.assertTrue(result["packet_result_operator_decision_surface"])
            self.assertTrue(result["operator_decision_record_created"])
            self.assertEqual(result["operator_decision"], "accepted")
            self.assertEqual(result["packet_id"], "packet_phase283")
            self.assertEqual(result["task_id"], "task_phase283")
            self.assertEqual(result["run_id"], "run_phase283")
            self.assertEqual(result["execution_artifact_id"], "artifact_phase283")
            self.assertIn("task_phase283_", result["verifier_result_path"])
            self.assertEqual(result["current_success_review_classification"], "completed_current_state_success")
            self.assertFalse(result["provider_executed"])
            self.assertFalse(result["model_executed"])
            self.assertFalse(result["runtime_executed"])
            self.assertFalse(result["platform_invoked"])
            self.assertIn("no_semantic_correctness_proof", result["non_proofs"])
            self.assertIn("no_autonomous_ai_coding_proof", result["non_proofs"])
            self.assertIn("no_live_provider_model_proof", result["non_proofs"])
            self.assertTrue(Path(result["operator_decision_record_path"]).exists())
            self.assertTrue(decisions.exists())

            persisted = json.loads(Path(result["operator_decision_record_path"]).read_text(encoding="utf-8"))
            self.assertEqual(persisted["operator_decision"], "accepted")
            self.assertFalse(persisted["no_activity_flags"]["provider_executed"])
            self.assertIn("does not prove semantic correctness", " ".join(persisted["caveats"]))
            self.assertIn("model-backed generation", " ".join(persisted["caveats"]))

            summary = followup_review["operator_decision_summary"]
            self.assertTrue(summary["operator_decision_record_present"])
            self.assertEqual(summary["operator_decision"], "accepted")
            self.assertTrue(summary["accepted"])

    def test_successful_rejection_record_preserved_without_product_failure_mutation(self):
        directory, _tasks, artifacts, verifiers, _decisions, patchers = self._patched_stores()
        with directory:
            with patchers[0], patchers[1], patchers[2], patchers[3], patchers[4]:
                self._write_supporting_records(artifacts, verifiers)
                result = record_packet_result_operator_decision(
                    self._decision_input(
                        operator_decision="rejected",
                        operator_note="Rejected because the operator wants a later bounded follow-up.",
                    )
                )
                followup_review = review_current_success_task_result({"task_id": "task_phase283"})
                task = run_manager.load_task("task_phase283")

            self.assertTrue(result["operator_decision_record_created"])
            self.assertEqual(result["operator_decision"], "rejected")
            self.assertTrue(result["rejected"])
            self.assertTrue(result["rejection_is_not_automatic_product_failure"])
            self.assertEqual(task.status, "completed")
            self.assertEqual(followup_review["final_outcome_classification"], "completed_current_state_success")
            self.assertEqual(followup_review["operator_decision_summary"]["operator_decision"], "rejected")
            self.assertTrue(followup_review["operator_decision_summary"]["rejected"])

    def test_missing_operator_note_blocks(self):
        result = record_packet_result_operator_decision(self._decision_input(operator_note=""))

        self.assertFalse(result["operator_decision_record_created"])
        self.assertIn("operator_note_required", result["blocked_conditions"])

    def test_missing_or_invalid_task_id_blocks(self):
        missing = record_packet_result_operator_decision(self._decision_input(task_id=""))
        invalid = record_packet_result_operator_decision(self._decision_input(task_id="../task_phase283"))

        self.assertFalse(missing["operator_decision_record_created"])
        self.assertIn("task_id_required", missing["blocked_conditions"])
        self.assertFalse(invalid["operator_decision_record_created"])
        self.assertIn("task_id_invalid", invalid["blocked_conditions"])

    def test_not_ready_current_success_result_blocks(self):
        directory, _tasks, artifacts, verifiers, decisions, patchers = self._patched_stores()
        with directory:
            with patchers[0], patchers[1], patchers[2], patchers[3], patchers[4]:
                self._write_supporting_records(artifacts, verifiers, status="queued")
                result = record_packet_result_operator_decision(self._decision_input())

            self.assertFalse(result["operator_decision_record_created"])
            self.assertIn("current_success_result_not_ready_for_operator_review", result["blocked_conditions"])
            self.assertIn("completed_current_state_success_required", result["blocked_conditions"])
            self.assertFalse(decisions.exists())

    def test_missing_required_artifact_or_verifier_evidence_blocks(self):
        directory, _tasks, _artifacts, _verifiers, decisions, patchers = self._patched_stores()
        with directory:
            with patchers[0], patchers[1], patchers[2], patchers[3], patchers[4]:
                run_manager.save_task(self._task())
                result = record_packet_result_operator_decision(self._decision_input())

            self.assertFalse(result["operator_decision_record_created"])
            self.assertIn("current_success_result_not_ready_for_operator_review", result["blocked_conditions"])
            self.assertFalse(decisions.exists())

    def test_unsupported_decision_and_provider_runtime_smuggling_block(self):
        result = record_packet_result_operator_decision(
            self._decision_input(operator_decision="approved", model_name="qwen")
        )

        self.assertFalse(result["operator_decision_record_created"])
        self.assertIn("unsupported_operator_decision", result["blocked_conditions"])
        self.assertIn("provider_model_runtime_platform_smuggling_rejected", result["blocked_conditions"])
        self.assertIn("model_name", result["missing_requirements"])

    def test_latest_readback_surfaces_latest_operator_decision(self):
        directory, _tasks, artifacts, verifiers, _decisions, patchers = self._patched_stores()
        with directory:
            with patchers[0], patchers[1], patchers[2], patchers[3], patchers[4]:
                self._write_supporting_records(artifacts, verifiers)
                record_packet_result_operator_decision(self._decision_input())
                record_packet_result_operator_decision(
                    self._decision_input(
                        operator_decision="rejected",
                        operator_note="Latest operator decision rejects the packet result.",
                    )
                )
                followup_review = review_current_success_task_result({"task_id": "task_phase283"})

            summary = followup_review["operator_decision_summary"]
            self.assertTrue(summary["operator_decision_record_present"])
            self.assertEqual(summary["operator_decision"], "rejected")
            self.assertFalse(summary["accepted"])
            self.assertTrue(summary["rejected"])


if __name__ == "__main__":
    unittest.main()
