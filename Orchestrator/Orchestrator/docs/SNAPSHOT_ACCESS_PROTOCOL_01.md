# Snapshot Access Protocol 01 — Targeted Archive Re-entry

## 1. Status

This is a re-entry/workflow reliability document, not a phase boundary and not implementation authorization.

## 2. Problem

Canonical snapshots may be large and noisy. Full extraction or broad archive scanning can time out or waste effort when only a small set of files is needed for orientation or verification.

## 3. Canonical Snapshot Rule

- Use the user-supplied refreshed snapshot as canonical when identified.
- Confirm the snapshot path before reading from it.
- Confirm archive root structure before relying on archive paths.
- Prefer repo truth from the canonical snapshot over conversation memory.
- Watch for stale uploads and duplicate filenames.

## 4. Targeted Access Rule

- Do not default to extracting the entire archive.
- First inspect root structure with a small list command.
- Read specific required files directly from the archive where possible.
- Extract only needed files/paths when direct read is insufficient.

Examples:

    tar -tzf /mnt/data/projects.tar.gz | head -50
    tar -xOzf /mnt/data/projects.tar.gz projects/docs/STARTUP_BRIEF.md
    tar -xOzf /mnt/data/projects.tar.gz projects/docs/PHASE_INDEX.md
    tar -xOzf /mnt/data/projects.tar.gz projects/docs/ACTION_LOG.md
    tar -xOzf /mnt/data/projects.tar.gz projects/orchestrator/case_packet.py

## 5. Suggested Re-entry Read Pattern

- Confirm archive exists.
- Inspect root with `tar -tzf ... | head`.
- Read startup/re-entry docs with `tar -xOzf`.
- Read only relevant phase/source/test files.
- Avoid extracting runtime directories unless directly needed.
- If extraction is needed, extract to a temp directory and target specific paths.

## 6. Noise Recognition

Common snapshot noise:

- `__pycache__/`
- `*.pyc`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `*.Zone.Identifier`
- runtime `data/`
- `test_logs/`
- duplicate/stale-looking snapshot filenames

Clarification:

Do not treat runtime `data/` or `test_logs/` as disposable unless a task explicitly authorizes cleanup. They may contain audit-like or fixture-like state.

## 7. Failure Handling

- If a full extraction or broad scan times out, retry with targeted archive reads.
- Do not declare the snapshot unusable merely because full extraction failed.
- Report precisely which file/path could or could not be read.
- If paths differ from expected root, adapt based on archive listing rather than guessing.

## 8. Operating Principle

Read the minimum necessary repo truth from the canonical snapshot before acting; prefer targeted archive access over broad extraction.
