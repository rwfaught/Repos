import ast
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS = REPO_ROOT / "tools" / "phase85_ollama_live_smoke.py"


class Phase85OllamaLiveSmokeGuardTests(unittest.TestCase):
    def test_harness_source_has_no_utf8_bom(self):
        data = HARNESS.read_bytes()
        self.assertFalse(data.startswith(b"\xef\xbb\xbf"))

    def test_live_smoke_harness_blocks_without_explicit_env_flag(self):
        env = dict(os.environ)
        env.pop("ORCH_PHASE85_ALLOW_LIVE_OLLAMA", None)

        result = subprocess.run(
            [sys.executable, "-B", str(HARNESS)],
            cwd=str(REPO_ROOT),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2, msg=f"stdout={result.stdout}\nstderr={result.stderr}")

        payload = json.loads(result.stdout)

        self.assertEqual(payload.get("phase"), 85)
        self.assertEqual(payload.get("status"), "blocked")
        self.assertIn("ORCH_PHASE85_ALLOW_LIVE_OLLAMA=YES", payload.get("reason", ""))
        self.assertFalse(payload.get("live_provider_execution"))
        self.assertFalse(payload.get("model_execution"))
        self.assertFalse(payload.get("runtime_execution"))
        self.assertFalse(payload.get("task_persistence"))
        self.assertEqual(result.stderr.strip(), "")

    def test_harness_has_no_top_level_live_project_imports(self):
        text = HARNESS.read_text(encoding="utf-8")
        tree = ast.parse(text)

        forbidden_top_level_imports = []

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".", 1)[0]
                    if root_name in {"orchestrator", "providers"}:
                        forbidden_top_level_imports.append(alias.name)

            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                root_name = module.split(".", 1)[0]
                if root_name in {"orchestrator", "providers"}:
                    forbidden_top_level_imports.append(module)

        self.assertEqual(forbidden_top_level_imports, [])

    def test_live_project_imports_are_deferred_inside_live_path(self):
        text = HARNESS.read_text(encoding="utf-8")

        self.assertIn('ALLOW_ENV = "ORCH_PHASE85_ALLOW_LIVE_OLLAMA"', text)
        self.assertIn("def _live_allowed", text)
        self.assertIn("if not _live_allowed()", text)
        self.assertIn("def _ensure_repo_root_on_path", text)
        self.assertIn("def run_live_smoke", text)
        self.assertIn("from providers.ollama_provider import OllamaProvider", text)
        self.assertIn("from orchestrator.task_schema import Task", text)
        self.assertIn("task_persistence", text)

        tree = ast.parse(text)
        function_imports = {}

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                imports = []
                for child in ast.walk(node):
                    if isinstance(child, ast.Import):
                        imports.extend(alias.name for alias in child.names)
                    if isinstance(child, ast.ImportFrom):
                        imports.append(child.module or "")
                function_imports[node.name] = imports

        self.assertIn("providers.ollama_provider", function_imports.get("run_live_smoke", []))
        self.assertIn("orchestrator.task_schema", function_imports.get("_build_task", []))


if __name__ == "__main__":
    unittest.main()