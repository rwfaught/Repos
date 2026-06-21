from pathlib import Path

from verifiers.base import VerificationCheckResult


def check_python_syntax(path: str) -> VerificationCheckResult:
    target = Path(path)

    if not target.exists():
        return VerificationCheckResult(
            name="python_syntax",
            passed=False,
            message="Target does not exist.",
            evidence={"path": path, "error": "missing_path"},
        )

    if not target.is_file():
        return VerificationCheckResult(
            name="python_syntax",
            passed=False,
            message="Target is not a file.",
            evidence={"path": path, "error": "not_a_file"},
        )

    try:
        source = target.read_text(encoding="utf-8")
        compile(source, str(target), "exec")
    except SyntaxError as error:
        return VerificationCheckResult(
            name="python_syntax",
            passed=False,
            message="Python syntax check failed.",
            evidence={
                "path": path,
                "error": str(error),
                "line": error.lineno,
                "offset": error.offset,
            },
        )
    except Exception as error:  # Defensive catch for non-syntax read/compile issues.
        return VerificationCheckResult(
            name="python_syntax",
            passed=False,
            message="Unable to check Python syntax.",
            evidence={"path": path, "error": str(error)},
        )

    return VerificationCheckResult(
        name="python_syntax",
        passed=True,
        message="Python syntax is valid.",
        evidence={"path": path},
    )
