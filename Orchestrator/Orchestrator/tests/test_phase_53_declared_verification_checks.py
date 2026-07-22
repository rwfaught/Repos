import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import main
from orchestrator import engine
from orchestrator.paths import DATA_DIR, VERIFIER_RESULTS_DIR
from orchestrator.recommendation_store import load_recommendation_records_for_run
from orchestrator.run_manager import create_run, load_task, load_tasks_for_run, save_task
from orchestrator.task_schema import create_task


class Phase53DeclaredVerificationChecksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_dir = DATA_DIR / "phase53_fixtures"
        self.fixture_dir.mkdir(parents=True, exist_ok=True)

    def _task_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:8]}"

    def _create_task(
        self,
        run_id: str,
        task_id: str,
        *,
        role: str = "coder",
        files_in_scope: list[str] | None = None,
        verification_checks: list[dict[str, str]] | None = None,
        expected_output: str | None = None,
        source_task_id: str | None = None,
        source_artifact_id: str | None = None,
    ):
        task = create_task(
            {
                "id": task_id,
                "run_id": run_id,
                "title": f"Phase53 task {task_id}",
                "role": role,
                "status": "queued",
                "dependencies": [],
                "success_criteria": ["phase53 validation"],
                "files_in_scope": files_in_scope or [],
                "retry_count": 0,
                "expected_output": expected_output,
                "source_task_id": source_task_id,
                "source_artifact_id": source_artifact_id,
                "verification_checks": verification_checks,
            }
        )
        save_task(task)
        return task

    def _write_fixture_file(self, name: str, content: str) -> str:
        path = self.fixture_dir / name
        path.write_text(content, encoding="utf-8")
        try:
            return str(path.relative_to(Path.cwd()))
        except ValueError:
            return str(Path("data") / path.relative_to(DATA_DIR))

    def _verifier_results_for_task(self, task_id: str) -> list[dict]:
        if not VERIFIER_RESULTS_DIR.exists():
            return []

        records: list[dict] = []
        for path in VERIFIER_RESULTS_DIR.glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if str(payload.get("task_id")) == task_id:
                records.append(payload)
        return records

    def _capture_main(self, argv: list[str]) -> str:
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                main.main()
            return output.getvalue()

    def test_a_declared_python_syntax_check_passes_and_persists(self):
        run = create_run("phase53 test A")
        valid_python = self._write_fixture_file(
            f"valid_{uuid4().hex[:8]}.py",
            "def ok() -> int:\n    return 1\n",
        )
        task_id = self._task_id("task_phase53_a")
        self._create_task(
            run["id"],
            task_id,
            verification_checks=[{"check": "python_syntax", "target": valid_python}],
        )

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "Implemented bounded change with clear deterministic validation evidence.",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(task_id), provider_name="mock")

        updated = load_task(task_id)
        self.assertEqual(updated.status, "completed")

        verifier_records = self._verifier_results_for_task(task_id)
        self.assertEqual(len(verifier_records), 1)
        verification = verifier_records[0].get("verification_result", {})
        self.assertTrue(verification.get("overall_passed"))
        checks = verification.get("checks", [])
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0].get("name"), "python_syntax")
        self.assertTrue(checks[0].get("passed"))

    def test_b_declared_python_syntax_check_failure_sets_verification_failed(self):
        run = create_run("phase53 test B")
        invalid_python = self._write_fixture_file(
            f"invalid_{uuid4().hex[:8]}.py",
            "def broken(:\n    return 1\n",
        )
        task_id = self._task_id("task_phase53_b")
        self._create_task(
            run["id"],
            task_id,
            verification_checks=[{"check": "python_syntax", "target": invalid_python}],
        )

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "Execution completed but syntax should fail deterministically.",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(task_id), provider_name="mock")

        updated = load_task(task_id)
        self.assertEqual(updated.status, "verification_failed")

        verifier_records = self._verifier_results_for_task(task_id)
        self.assertEqual(len(verifier_records), 1)
        verification = verifier_records[0].get("verification_result", {})
        self.assertFalse(verification.get("overall_passed"))
        checks = verification.get("checks", [])
        self.assertEqual(checks[0].get("name"), "python_syntax")
        self.assertFalse(checks[0].get("passed"))

    def test_c_mixed_declared_checks_run_and_persist_combined_truth(self):
        run = create_run("phase53 test C")
        valid_python = self._write_fixture_file(
            f"mixed_valid_{uuid4().hex[:8]}.py",
            "x = 1\n",
        )
        task_id = self._task_id("task_phase53_c")
        self._create_task(
            run["id"],
            task_id,
            verification_checks=[
                {"check": "file_exists", "target": "main.py"},
                {"check": "directory_exists", "target": "data"},
                {"check": "python_syntax", "target": valid_python},
            ],
        )

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "Execution completed with deterministic mixed-check verification targets.",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(task_id), provider_name="mock")

        updated = load_task(task_id)
        self.assertEqual(updated.status, "completed")

        verifier_records = self._verifier_results_for_task(task_id)
        self.assertEqual(len(verifier_records), 1)
        verification = verifier_records[0].get("verification_result", {})
        self.assertTrue(verification.get("overall_passed"))
        names = [check.get("name") for check in verification.get("checks", [])]
        self.assertEqual(names, ["file_exists", "directory_exists", "python_syntax"])

    def test_d_legacy_fallback_without_declared_checks_still_uses_file_exists(self):
        run = create_run("phase53 test D")
        task_id = self._task_id("task_phase53_d")
        self._create_task(run["id"], task_id, files_in_scope=["main.py"])

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "Legacy fallback path remains intact and deterministic.",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(task_id), provider_name="mock")

        updated = load_task(task_id)
        self.assertEqual(updated.status, "completed")

        verifier_records = self._verifier_results_for_task(task_id)
        self.assertEqual(len(verifier_records), 1)
        verification = verifier_records[0].get("verification_result", {})
        checks = verification.get("checks", [])
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0].get("name"), "file_exists")

    def test_e_outcome_precedence_unchanged(self):
        run_exec_fail = create_run("phase53 test E execution failure precedence")
        valid_python = self._write_fixture_file(
            f"exec_fail_{uuid4().hex[:8]}.py",
            "x = 1\n",
        )
        exec_fail_task_id = self._task_id("task_phase53_e_exec_fail")
        self._create_task(
            run_exec_fail["id"],
            exec_fail_task_id,
            verification_checks=[{"check": "python_syntax", "target": valid_python}],
        )

        engine.process_task_by_id(load_task(exec_fail_task_id), provider_name="no_such_provider")
        exec_failed = load_task(exec_fail_task_id)
        self.assertEqual(exec_failed.status, "execution_failed")

        run_review_gate = create_run("phase53 test E verification gate before adequacy/review")
        missing_python_target = f"data/phase53_fixtures/missing_{uuid4().hex[:8]}.py"
        review_gate_task_id = self._task_id("task_phase53_e_review_gate")
        self._create_task(
            run_review_gate["id"],
            review_gate_task_id,
            role="coder",
            verification_checks=[{"check": "python_syntax", "target": missing_python_target}],
            expected_output="must_include_expected_phrase",
        )

        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "This output is long enough but intentionally misses expected phrase.",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(review_gate_task_id), provider_name="mock")

        review_gated = load_task(review_gate_task_id)
        self.assertEqual(review_gated.status, "verification_failed")
        tasks_for_run = load_tasks_for_run(run_review_gate["id"])
        reviewer_tasks = [task for task in tasks_for_run if task.role == "reviewer"]
        self.assertEqual(reviewer_tasks, [])

        recommendations = load_recommendation_records_for_run(run_review_gate["id"])
        self.assertEqual(recommendations, [])

    def test_f_standalone_verifier_cli_behavior_remains_intact(self):
        valid_python = self._write_fixture_file(
            f"cli_valid_{uuid4().hex[:8]}.py",
            "y = 2\n",
        )

        file_exists_text = self._capture_main(["main.py", "verify", "file_exists", "main.py"])
        file_exists_payload = json.loads(file_exists_text)
        self.assertTrue(file_exists_payload["overall_passed"])
        self.assertEqual(file_exists_payload["checks"][0]["name"], "file_exists")

        directory_exists_text = self._capture_main(["main.py", "verify", "directory_exists", "data"])
        directory_exists_payload = json.loads(directory_exists_text)
        self.assertTrue(directory_exists_payload["overall_passed"])
        self.assertEqual(directory_exists_payload["checks"][0]["name"], "directory_exists")

        python_syntax_text = self._capture_main(["main.py", "verify", "python_syntax", valid_python])
        python_syntax_payload = json.loads(python_syntax_text)
        self.assertTrue(python_syntax_payload["overall_passed"])
        self.assertEqual(python_syntax_payload["checks"][0]["name"], "python_syntax")


if __name__ == "__main__":
    unittest.main()
