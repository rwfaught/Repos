import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestrator.artifact_store as artifact_store
import orchestrator.current_success_result_review as result_review
import orchestrator.paths as project_paths
import orchestrator.run_manager as run_manager
from orchestrator import engine
from orchestrator.current_success_result_review import review_current_success_task_result
from orchestrator.task_schema import FILESYSTEM_MUTATION_EXECUTION_POLICY, Task


class Phase272IntegratedCodingTaskCurrentSpineProofTests(unittest.TestCase):
    def test_integrated_coding_task_spine_reaches_current_success_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks_dir = root / "data" / "tasks"
            artifacts_dir = root / "data" / "artifacts"
            verifier_dir = root / "data" / "verifier_results"

            task = Task(
                id="task_phase272_integrated",
                run_id="run_phase272",
                title="Integrated current-spine bounded coding task proof",
                role="coder",
                status="queued",
                dependencies=[],
                success_criteria=[
                    "Write the bounded deterministic Phase 272 output.",
                    "Persist task, artifact, verifier, and review evidence.",
                ],
                files_in_scope=["outputs/phase272.txt"],
                retry_count=0,
                expected_output="PHASE272 integrated current-spine proof\n",
                execution_policy=FILESYSTEM_MUTATION_EXECUTION_POLICY,
                requires_causal_change=False,
            )

            with (
                patch.object(project_paths, "PROJECT_ROOT", root),
                patch.object(run_manager, "TASKS_DIR", tasks_dir),
                patch.object(artifact_store, "ARTIFACTS_DIR", artifacts_dir),
                patch.object(engine, "VERIFIER_RESULTS_DIR", verifier_dir),
                patch.object(result_review, "ARTIFACTS_DIR", artifacts_dir),
                patch.object(result_review, "VERIFIER_RESULTS_DIR", verifier_dir),
            ):
                run_manager.save_task(task)
                engine.process_task_by_id(
                    run_manager.load_task(task.id),
                    provider_name="local_file",
                )

                completed = run_manager.load_task(task.id)
                self.assertEqual(completed.status, "completed")
                self.assertTrue(completed.execution_artifact_id)
                self.assertEqual(
                    completed.execution_policy,
                    FILESYSTEM_MUTATION_EXECUTION_POLICY,
                )
                self.assertTrue(completed.requires_causal_change)
                self.assertEqual(
                    (root / "outputs" / "phase272.txt").read_text(encoding="utf-8"),
                    task.expected_output,
                )

                artifact_files = sorted(artifacts_dir.glob("*.json"))
                self.assertEqual(len(artifact_files), 1)
                artifact = json.loads(artifact_files[0].read_text(encoding="utf-8"))
                self.assertEqual(artifact["artifact_id"], completed.execution_artifact_id)
                self.assertEqual(artifact["task_id"], task.id)
                self.assertEqual(artifact["status"], "success")
                self.assertEqual(
                    artifact["execution_policy"],
                    FILESYSTEM_MUTATION_EXECUTION_POLICY,
                )
                self.assertTrue(artifact["requires_causal_change"])

                verifier_files = sorted(verifier_dir.glob("*.json"))
                self.assertEqual(len(verifier_files), 1)
                verifier_record = json.loads(
                    verifier_files[0].read_text(encoding="utf-8")
                )
                self.assertEqual(verifier_record["task_id"], task.id)
                self.assertEqual(
                    verifier_record["execution_artifact_id"],
                    completed.execution_artifact_id,
                )
                verification = verifier_record["verification_result"]
                self.assertTrue(verification["overall_passed"])
                self.assertTrue(verification["causal_change_passed"])
                self.assertEqual(
                    verification["changed_targets"],
                    ["outputs/phase272.txt"],
                )

                review = review_current_success_task_result({"task_id": task.id})

            self.assertTrue(review["current_success_result_review_surface"])
            self.assertTrue(review["ready_for_operator_review"])
            self.assertEqual(
                review["final_outcome_classification"],
                "completed_current_state_success",
            )
            self.assertEqual(
                review["operator_response_surface"],
                "completed_result_response_options",
            )
            self.assertEqual(
                review["artifact_summary"]["artifact_id"],
                completed.execution_artifact_id,
            )
            self.assertTrue(review["verification_summary"]["overall_passed"])

            option_ids = {
                option["option_id"] for option in review.get("response_options", [])
            }
            self.assertTrue(
                {
                    "inspect_task_state",
                    "inspect_execution_artifact",
                    "inspect_verifier_result",
                    "record_operator_acceptance_later",
                }.issubset(option_ids)
            )
            self.assertFalse(review["task_mutated"])
            self.assertFalse(review["execution_performed"])
            self.assertFalse(review["provider_executed"])
            self.assertFalse(review["runtime_executed"])
            self.assertFalse(review["model_executed"])


if __name__ == "__main__":
    unittest.main()
