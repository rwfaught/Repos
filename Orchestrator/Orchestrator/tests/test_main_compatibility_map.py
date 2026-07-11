import ast
import unittest
from pathlib import Path


EXPECTED_COMMANDS = {
    "init",
    "status",
    "new-run",
    "next",
    "verify",
    "intake-judge",
    "intake-handoff-admit",
    "case-packet-seed-review",
    "case-packet-creation-authorize",
    "case-packet-persist-authorized",
    "case-packet-task-candidate-review",
    "case-packet-task-creation-authorize",
    "case-packet-task-create-authorized",
    "case-packet-task-execution-candidates",
    "case-packet-task-execution-authorize",
    "case-packet-task-execute-authorized",
    "case-packet-task-execution-result-review",
    "case-packet-task-execution-result-options",
    "current-success-result-review",
    "current-success-result-accept",
    "packet-result-operator-decide",
    "case-packet-create",
    "case-packet-show",
    "case-packet-summary",
    "case-packet-validate",
    "case-packet-init",
    "case-packet-append",
    "case-packet-orient",
    "recommendations",
    "recommendation-summary",
    "recommendation-actions",
    "recommendation-proposals",
    "recommendation-drafts",
    "recommendation-outcomes",
    "recommendation-resolution",
    "recommendation-archive",
    "recommendation-accept",
    "recommendation-create",
    "recommendation-lineage",
    "recommendation-created-tasks",
    "recommendation-confirm",
    "confirmed-recommendation-tasks",
    "ready-recommendation-tasks",
    "ready-execution-candidates",
    "recommendation-execution-results",
    "recommendation-result-options",
    "create-followup-review",
    "create-repair-task",
    "execute-ready-candidate",
}

CANONICAL_DELEGATES = set()
DEPRECATED_COMMANDS = set()
FUTURE_MIGRATION_REQUIRED = {
    "init",
    "new-run",
    "next",
    "case-packet-persist-authorized",
    "case-packet-task-create-authorized",
    "case-packet-task-execute-authorized",
    "current-success-result-accept",
    "packet-result-operator-decide",
    "case-packet-create",
    "case-packet-init",
    "case-packet-append",
    "case-packet-orient",
    "recommendation-archive",
    "recommendation-accept",
    "recommendation-create",
    "recommendation-confirm",
    "create-followup-review",
    "create-repair-task",
    "execute-ready-candidate",
}
LEGACY_OUTSIDE_CANONICAL_ALPHA = EXPECTED_COMMANDS - FUTURE_MIGRATION_REQUIRED


class MainCompatibilityMapTests(unittest.TestCase):
    def test_exact_49_command_surface_is_classified_without_new_delegation(self):
        main_path = Path(__file__).resolve().parents[1] / "main.py"
        tree = ast.parse(main_path.read_text(encoding="utf-8-sig"))
        discovered = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare) or len(node.ops) != 1:
                continue
            if not isinstance(node.ops[0], ast.Eq) or len(node.comparators) != 1:
                continue
            left = node.left
            right = node.comparators[0]
            if isinstance(left, ast.Name) and left.id == "command" and isinstance(right, ast.Constant):
                if isinstance(right.value, str):
                    discovered.add(right.value)

        self.assertEqual(len(discovered), 49)
        self.assertEqual(discovered, EXPECTED_COMMANDS)
        self.assertEqual(CANONICAL_DELEGATES, set())
        self.assertEqual(DEPRECATED_COMMANDS, set())
        self.assertEqual(
            LEGACY_OUTSIDE_CANONICAL_ALPHA | FUTURE_MIGRATION_REQUIRED,
            EXPECTED_COMMANDS,
        )
        self.assertFalse(LEGACY_OUTSIDE_CANONICAL_ALPHA & FUTURE_MIGRATION_REQUIRED)


if __name__ == "__main__":
    unittest.main()
