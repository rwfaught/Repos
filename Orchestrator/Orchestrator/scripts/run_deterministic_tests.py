"""Run the repository's deterministic unittest suite in a disposable data root."""

from __future__ import annotations

import shutil
import tempfile
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESTS_ROOT = PROJECT_ROOT / "tests"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from orchestrator.alpha_runtime import isolated_data_root


def discover_suite() -> unittest.TestSuite:
    """Discover every checked-in deterministic test module, including worker tests."""
    return unittest.defaultTestLoader.discover(
        start_dir=str(TESTS_ROOT),
        pattern="test_*.py",
    )


def main() -> int:
    suite = discover_suite()
    with tempfile.TemporaryDirectory(prefix="orchestrator-deterministic-tests-") as directory:
        sandbox_root = Path(directory) / "project"
        sandbox_root.mkdir()
        shutil.copy2(PROJECT_ROOT / "main.py", sandbox_root / "main.py")
        with isolated_data_root(sandbox_root / "data"):
            result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
