import contextlib
import io
import unittest
from pathlib import Path

from orchestrator import operator_coding_task_packet_cli


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = PROJECT_ROOT / "docs" / "SUPPORTED_EXECUTABLE_SURFACES.md"


class SupportedExecutableSurfacesContractTests(unittest.TestCase):
    def test_contract_preserves_the_canonical_command_and_noncanonical_markers(self):
        text = CONTRACT_PATH.read_text(encoding="utf-8")

        self.assertIn(
            ".venv\\Scripts\\python.exe -m orchestrator.operator_coding_task_packet_cli",
            text,
        )
        self.assertIn(
            ".venv\\Scripts\\python.exe -B scripts\\run_deterministic_tests.py",
            text,
        )
        for marker in (
            "CANONICAL_SUPPORTED",
            "LEGACY_RETAINED",
            "DIAGNOSTIC_DIRECT_ENTRY",
            "TEST_OR_REFERENCE_ONLY",
            "RETIRED_DO_NOT_RUN",
            "main.py",
            "run_acceptance_tests.sh",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_canonical_cli_no_argument_path_is_blocked_without_activity(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = operator_coding_task_packet_cli.main([])

        rendered = output.getvalue()
        self.assertEqual(exit_code, 2)
        self.assertIn('"blocked": true', rendered)
        self.assertIn('"live_provider_invoked": false', rendered)
        self.assertIn('"runtime_executed": false', rendered)
