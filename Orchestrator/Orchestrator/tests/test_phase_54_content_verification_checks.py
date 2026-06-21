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
from orchestrator.run_manager import create_run, load_task, save_task
from orchestrator.task_schema import create_task


class Phase54ContentVerificationChecksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_dir = DATA_DIR / "phase54_fixtures"
        self.fixture_dir.mkdir(parents=True, exist_ok=True)

    def _task_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:8]}"

    def _create_task(
        self,
        run_id: str,
        task_id: str,
        *,
        files_in_scope: list[str] | None = None,
        verification_checks: list[dict[str, str]] | None = None,
    ):
        task = create_task(
            {
                "id": task_id,
                "run_id": run_id,
                "title": f"Phase54 task {task_id}",
                "role": "coder",
                "status": "queued",
                "dependencies": [],
                "success_criteria": ["phase54 validation"],
                "files_in_scope": files_in_scope or [],
                "retry_count": 0,
                "verification_checks": verification_checks,
            }
        )
        save_task(task)
        return task

    def _write_fixture_file(self, name: str, content: str) -> str:
        path = self.fixture_dir / name
        path.write_text(content, encoding="utf-8")
        return str(path.relative_to(Path.cwd()))

    def _verifier_result_for_task(self, task_id: str) -> dict:
        matches: list[dict] = []
        for path in VERIFIER_RESULTS_DIR.glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if str(payload.get("task_id")) == task_id:
                matches.append(payload)
        self.assertEqual(len(matches), 1)
        return matches[0]

    def _run_successful_execution(self, task_id: str) -> None:
        with patch(
            "orchestrator.engine.dispatch_task",
            return_value={
                "status": "success",
                "output": "Execution completed with deterministic verification evidence.",
                "provider": "mock",
                "metadata": {},
                "error": None,
            },
        ):
            engine.process_task_by_id(load_task(task_id), provider_name="mock")

    def _capture_main(self, argv: list[str]) -> str:
        with patch.object(sys, "argv", argv):
            output = io.StringIO()
            with redirect_stdout(output):
                main.main()
            return output.getvalue()

    def test_a_file_contains_text_passes(self):
        run = create_run("phase54 test A")
        target = self._write_fixture_file(
            f"contains_pass_{uuid4().hex[:8]}.txt",
            "alpha\nbeta\ngamma\n",
        )
        task_id = self._task_id("task_phase54_a")
        self._create_task(
            run["id"],
            task_id,
            verification_checks=[
                {"check": "file_contains_text", "target": target, "text": "beta"}
            ],
        )

        self._run_successful_execution(task_id)

        updated = load_task(task_id)
        self.assertEqual(updated.status, "completed")

        verification = self._verifier_result_for_task(task_id).get("verification_result", {})
        self.assertTrue(verification.get("overall_passed"))
        check = verification.get("checks", [])[0]
        self.assertEqual(check.get("name"), "file_contains_text")
        self.assertTrue(check.get("passed"))
        self.assertTrue(check.get("evidence", {}).get("contains_text"))

    def test_b_file_contains_text_fails_when_text_missing(self):
        run = create_run("phase54 test B")
        target = self._write_fixture_file(
            f"contains_fail_{uuid4().hex[:8]}.txt",
            "line one\nline two\n",
        )
        task_id = self._task_id("task_phase54_b")
        self._create_task(
            run["id"],
            task_id,
            verification_checks=[
                {"check": "file_contains_text", "target": target, "text": "not-present"}
            ],
        )

        self._run_successful_execution(task_id)

        updated = load_task(task_id)
        self.assertEqual(updated.status, "verification_failed")

        verification = self._verifier_result_for_task(task_id).get("verification_result", {})
        self.assertFalse(verification.get("overall_passed"))
        check = verification.get("checks", [])[0]
        self.assertEqual(check.get("name"), "file_contains_text")
        self.assertFalse(check.get("passed"))
        self.assertFalse(check.get("evidence", {}).get("contains_text"))

    def test_c_json_parses_passes(self):
        run = create_run("phase54 test C")
        target = self._write_fixture_file(
            f"json_pass_{uuid4().hex[:8]}.json",
            '{"ok": true, "count": 2}',
        )
        task_id = self._task_id("task_phase54_c")
        self._create_task(
            run["id"],
            task_id,
            verification_checks=[{"check": "json_parses", "target": target}],
        )

        self._run_successful_execution(task_id)

        updated = load_task(task_id)
        self.assertEqual(updated.status, "completed")

        verification = self._verifier_result_for_task(task_id).get("verification_result", {})
        self.assertTrue(verification.get("overall_passed"))
        check = verification.get("checks", [])[0]
        self.assertEqual(check.get("name"), "json_parses")
        self.assertTrue(check.get("passed"))

    def test_d_json_parses_fails_and_captures_parse_error(self):
        run = create_run("phase54 test D")
        target = self._write_fixture_file(
            f"json_fail_{uuid4().hex[:8]}.json",
            '{"ok": true,,}',
        )
        task_id = self._task_id("task_phase54_d")
        self._create_task(
            run["id"],
            task_id,
            verification_checks=[{"check": "json_parses", "target": target}],
        )

        self._run_successful_execution(task_id)

        updated = load_task(task_id)
        self.assertEqual(updated.status, "verification_failed")

        verification = self._verifier_result_for_task(task_id).get("verification_result", {})
        self.assertFalse(verification.get("overall_passed"))
        check = verification.get("checks", [])[0]
        self.assertEqual(check.get("name"), "json_parses")
        self.assertFalse(check.get("passed"))
        self.assertTrue(str(check.get("evidence", {}).get("error", "")).strip())

    def test_e_mixed_declared_checks_with_new_and_existing_checks(self):
        run = create_run("phase54 test E")
        text_target = self._write_fixture_file(
            f"mixed_text_{uuid4().hex[:8]}.txt",
            "needle in haystack",
        )
        json_target = self._write_fixture_file(
            f"mixed_json_{uuid4().hex[:8]}.json",
            '{"value": 1}',
        )
        task_id = self._task_id("task_phase54_e")
        self._create_task(
            run["id"],
            task_id,
            verification_checks=[
                {"check": "file_exists", "target": "main.py"},
                {"check": "directory_exists", "target": "data"},
                {"check": "file_contains_text", "target": text_target, "text": "needle"},
                {"check": "json_parses", "target": json_target},
            ],
        )

        self._run_successful_execution(task_id)

        verification = self._verifier_result_for_task(task_id).get("verification_result", {})
        self.assertTrue(verification.get("overall_passed"))
        names = [item.get("name") for item in verification.get("checks", [])]
        self.assertEqual(
            names,
            ["file_exists", "directory_exists", "file_contains_text", "json_parses"],
        )

    def test_f_legacy_fallback_still_runs_file_exists(self):
        run = create_run("phase54 test F")
        task_id = self._task_id("task_phase54_f")
        self._create_task(run["id"], task_id, files_in_scope=["main.py"])

        self._run_successful_execution(task_id)

        verification = self._verifier_result_for_task(task_id).get("verification_result", {})
        self.assertTrue(verification.get("overall_passed"))
        checks = verification.get("checks", [])
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0].get("name"), "file_exists")

    def test_g_verifier_cli_old_and_new_checks_work(self):
        text_target = self._write_fixture_file(
            f"cli_text_{uuid4().hex[:8]}.txt",
            "hello-world",
        )
        json_target = self._write_fixture_file(
            f"cli_json_{uuid4().hex[:8]}.json",
            '{"k": "v"}',
        )

        file_exists_payload = json.loads(
            self._capture_main(["main.py", "verify", "file_exists", "main.py"])
        )
        self.assertTrue(file_exists_payload.get("overall_passed"))

        python_payload = json.loads(
            self._capture_main(["main.py", "verify", "python_syntax", "main.py"])
        )
        self.assertTrue(python_payload.get("overall_passed"))

        contains_payload = json.loads(
            self._capture_main(
                ["main.py", "verify", "file_contains_text", text_target, "hello-world"]
            )
        )
        self.assertTrue(contains_payload.get("overall_passed"))
        self.assertEqual(contains_payload.get("checks", [])[0].get("name"), "file_contains_text")

        json_payload = json.loads(
            self._capture_main(["main.py", "verify", "json_parses", json_target])
        )
        self.assertTrue(json_payload.get("overall_passed"))
        self.assertEqual(json_payload.get("checks", [])[0].get("name"), "json_parses")


if __name__ == "__main__":
    unittest.main()
