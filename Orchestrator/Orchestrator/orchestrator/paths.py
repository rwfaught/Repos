import re
from pathlib import Path
from pathlib import PurePosixPath, PureWindowsPath

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
DATA_DIR = PROJECT_ROOT / "data"
STATE_DIR = DATA_DIR / "state"
RUNS_DIR = DATA_DIR / "runs"
TASKS_DIR = DATA_DIR / "tasks"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
LOGS_DIR = DATA_DIR / "logs"
VERIFIER_RESULTS_DIR = DATA_DIR / "verifier_results"
AGENTS_PROMPTS_DIR = PROJECT_ROOT / "agents" / "prompts"

_SAFE_RECORD_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def resolve_project_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def validate_record_id(record_id: str, *, label: str = "record id") -> str:
    raw = str(record_id or "")
    normalized = raw.strip()
    if not normalized:
        raise ValueError(f"{label} must not be empty.")
    if normalized != raw:
        raise ValueError(f"{label} must not contain leading or trailing whitespace.")
    if Path(normalized).is_absolute() or PureWindowsPath(normalized).is_absolute():
        raise ValueError(f"{label} must not be an absolute path.")
    if "/" in normalized or "\\" in normalized:
        raise ValueError(f"{label} must not contain path separators.")
    if normalized in {".", ".."} or set(normalized) == {"."}:
        raise ValueError(f"{label} must not be dot-only.")
    if not _SAFE_RECORD_ID_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"{label} must start with a letter or number and contain only "
            "letters, numbers, underscore, hyphen, and dot."
        )
    return normalized


def record_path(
    store_dir: Path,
    record_id: str,
    *,
    suffix: str = ".json",
    label: str = "record id",
) -> Path:
    safe_id = validate_record_id(record_id, label=label)
    root = Path(store_dir).resolve()
    candidate = (root / f"{safe_id}{suffix}").resolve()
    if candidate.parent != root:
        raise ValueError(f"{label} resolved outside the intended store.")
    return candidate


def resolve_declared_project_path(path: str) -> Path:
    target = str(path or "").strip()
    if not target:
        raise ValueError("Declared project path must not be empty.")

    candidate = Path(target)
    if (
        candidate.is_absolute()
        or PureWindowsPath(target).is_absolute()
        or PurePosixPath(target).is_absolute()
    ):
        raise ValueError("Declared project path must be relative.")
    if any(part == ".." for part in candidate.parts) or any(
        part == ".." for part in PureWindowsPath(target).parts
    ):
        raise ValueError("Declared project path must not contain parent traversal.")

    root = PROJECT_ROOT.resolve()
    resolved = (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError("Declared project path resolved outside the project root.")
    return resolved
