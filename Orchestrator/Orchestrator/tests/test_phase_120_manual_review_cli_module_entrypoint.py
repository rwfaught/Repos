import subprocess
import sys
import unittest


REQUIRED_SECTIONS = (
    "Assessment",
    "Accepted Facts",
    "Decision",
    "NBM",
    "Deliverable/Command",
    "RESPONSE_METADATA",
    "Router Policy",
)

FORBIDDEN_EXECUTION_CLAIMS = (
    "provider_executed=true",
    "model_executed=true",
    "worker_dispatched=true",
    "codex_dispatched=true",
    "route_execution=true",
    "production_readiness=true",
)


class Phase120ManualReviewCliModuleEntrypointTests(unittest.TestCase):
    def test_module_entrypoint_safe_direct_answer_smoke(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "orchestrator.manual_review_cli",
                "--fixture",
                "safe_direct_answer",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        for section in REQUIRED_SECTIONS:
            self.assertIn(section, completed.stdout)
        self.assertIn("recommended_route=local_first_answer", completed.stdout)
        self.assertIn("provider_posture=local_first_when_authorized_no_provider_executed", completed.stdout)

        rendered = completed.stdout.lower()
        for forbidden in FORBIDDEN_EXECUTION_CLAIMS:
            self.assertNotIn(forbidden, rendered)


if __name__ == "__main__":
    unittest.main()
