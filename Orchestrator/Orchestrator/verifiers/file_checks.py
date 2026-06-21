import json
from pathlib import Path

from verifiers.base import VerificationCheckResult


def check_file_exists(path: str) -> VerificationCheckResult:
    target = Path(path)
    exists = target.exists() and target.is_file()
    message = "File exists." if exists else "File does not exist."
    return VerificationCheckResult(
        name="file_exists",
        passed=exists,
        message=message,
        evidence={"path": path, "exists": exists},
    )


def check_directory_exists(path: str) -> VerificationCheckResult:
    target = Path(path)
    exists = target.exists() and target.is_dir()
    message = "Directory exists." if exists else "Directory does not exist."
    return VerificationCheckResult(
        name="directory_exists",
        passed=exists,
        message=message,
        evidence={"path": path, "exists": exists},
    )


def check_file_contains_text(path: str, text: str | None) -> VerificationCheckResult:
    target = Path(path)

    if not target.exists():
        return VerificationCheckResult(
            name="file_contains_text",
            passed=False,
            message="Target does not exist.",
            evidence={"path": path, "error": "missing_path"},
        )

    if not target.is_file():
        return VerificationCheckResult(
            name="file_contains_text",
            passed=False,
            message="Target is not a file.",
            evidence={"path": path, "error": "not_a_file"},
        )

    expected_text = (text or "").strip()
    if not expected_text:
        return VerificationCheckResult(
            name="file_contains_text",
            passed=False,
            message="Required text is missing.",
            evidence={"path": path, "error": "missing_text"},
        )

    try:
        content = target.read_text(encoding="utf-8")
    except Exception as error:
        return VerificationCheckResult(
            name="file_contains_text",
            passed=False,
            message="Unable to read target file.",
            evidence={"path": path, "error": str(error)},
        )

    contains_text = expected_text in content
    message = "Required text is present." if contains_text else "Required text is not present."
    return VerificationCheckResult(
        name="file_contains_text",
        passed=contains_text,
        message=message,
        evidence={"path": path, "contains_text": contains_text, "text": expected_text},
    )


def check_json_parses(path: str) -> VerificationCheckResult:
    target = Path(path)

    if not target.exists():
        return VerificationCheckResult(
            name="json_parses",
            passed=False,
            message="Target does not exist.",
            evidence={"path": path, "error": "missing_path"},
        )

    if not target.is_file():
        return VerificationCheckResult(
            name="json_parses",
            passed=False,
            message="Target is not a file.",
            evidence={"path": path, "error": "not_a_file"},
        )

    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return VerificationCheckResult(
            name="json_parses",
            passed=False,
            message="JSON parse failed.",
            evidence={
                "path": path,
                "error": str(error),
                "line": error.lineno,
                "column": error.colno,
            },
        )
    except Exception as error:
        return VerificationCheckResult(
            name="json_parses",
            passed=False,
            message="Unable to parse JSON.",
            evidence={"path": path, "error": str(error)},
        )

    return VerificationCheckResult(
        name="json_parses",
        passed=True,
        message="JSON parses successfully.",
        evidence={"path": path, "json_type": type(payload).__name__},
    )
