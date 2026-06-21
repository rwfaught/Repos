from typing import Any

from verifiers.base import VerificationCheckResult, VerificationResult
from verifiers.file_checks import (
    check_directory_exists,
    check_file_contains_text,
    check_file_exists,
    check_json_parses,
)
from verifiers.python_checks import check_python_syntax

CHECKS = {
    "file_exists": check_file_exists,
    "directory_exists": check_directory_exists,
    "python_syntax": check_python_syntax,
    "json_parses": check_json_parses,
}
CHECKS_WITH_TEXT = {"file_contains_text"}


def list_checks() -> list[str]:
    return sorted(set(CHECKS.keys()) | CHECKS_WITH_TEXT)


def run_check(check_name: str, target_path: str, check_options: dict[str, Any] | None = None) -> VerificationResult:
    options = check_options or {}
    if check_name == "file_contains_text":
        check_result = check_file_contains_text(target_path, str(options.get("text", "")))
        return VerificationResult(
            overall_passed=check_result.passed,
            checks=[check_result],
            messages=[check_result.message],
        )

    check_fn = CHECKS.get(check_name)
    if check_fn is None:
        check_result = VerificationCheckResult(
            name=check_name,
            passed=False,
            message="Unknown check name.",
            evidence={"check_name": check_name, "available_checks": list_checks()},
        )
        return VerificationResult(
            overall_passed=False,
            checks=[check_result],
            messages=[check_result.message],
        )

    check_result = check_fn(target_path)
    return VerificationResult(
        overall_passed=check_result.passed,
        checks=[check_result],
        messages=[check_result.message],
    )
