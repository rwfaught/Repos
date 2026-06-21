# ALPHA_3_0_SNAPSHOT_HANDOFF_ADDENDUM_01.md

## Alpha 3.0 Snapshot Handoff Addendum 01 — Snapshot Reliability Watchlist

---

## Purpose

Add a small restart watchlist item for snapshot handoff reliability.

This is a docs-only addendum to the Alpha 3.0 restart preparation work.

The goal is to make Alpha 3.0 aware that the current snapshot handoff method works but can create avoidable friction when the entire `projects/` folder is archived and uploaded as `projects.tar.gz`.

This addendum does not change the build plan.

It does not authorize Phase 61.

It does not authorize implementation.

---

## Background

The current snapshot handoff method is:

- zip/tar the whole `projects/` folder
- upload it as `projects.tar.gz`
- use that archive as repo truth for Orchestrator/auditor analysis

This method has worked, but recent handoff exposed reliability friction:

- multiple similarly named `projects.tar.gz` uploads or source-refreshes can create canonical-snapshot ambiguity
- full-folder archives may include runtime/test state under `data/`
- archives may include `__pycache__/`, `.pyc`, `Zone.Identifier`, or other filesystem noise
- stale extracted directories or duplicate uploads can confuse which snapshot is current
- tarballs are less directly searchable than individual docs or changed-file bundles

The issue is not necessarily archive size.

The issue is snapshot clarity.

---

## Watchlist Item

Add this watchlist item to Alpha 3.0 restart context:

### SNAPSHOT_HANDOFF_RELIABILITY

Current whole-folder snapshot handoff works, but it should not be treated as frictionless.

Alpha 3.0 should confirm:

1. Which uploaded `projects.tar.gz` is canonical.
2. Whether the archive root structure is correct.
3. Whether accidental nested path artifacts are present.
4. Whether `__pycache__`, `.pyc`, `Zone.Identifier`, or other noise is present.
5. Whether `data/` runtime/test state is needed for the current task.
6. Whether a smaller handoff would be more appropriate.

Alpha 3.0 should not treat stale extracted directories, older uploads, or duplicate filenames as repo truth.

---

## Recommended Future Snapshot Protocols

Depending on task type, prefer the smallest sufficient handoff.

### Full repo audit

Use `projects.tar.gz`, but clean obvious noise first.

Recommended exclusions:

- `__pycache__/`
- `*.pyc`
- `*:Zone.Identifier`
- accidental nested extraction/path artifacts
- temporary files
- stale local archives

Include `data/` only if runtime state is relevant.

### Docs-only review

Use a docs-only archive:

- `docs_snapshot.tar.gz`

This is preferable when the task concerns restart briefs, strategy docs, phase docs, method docs, or handoff prompts.

### Phase audit / changed files review

Use a changed-files archive:

- `changed_files.tar.gz`

Include only:

- new files
- modified files
- relevant phase boundary
- relevant tests
- relevant ledger docs

### Patch-based review

If the repo is under git, consider:

- `git diff --stat`
- `git diff`
- changed files
- test output

A patch is often cleaner than a full snapshot when the task is bounded.

### Manifest-based handoff

For any snapshot type, consider adding:

- `SNAPSHOT_MANIFEST.md`

The manifest should list:

- snapshot date/time
- repo root
- reason for snapshot
- canonical archive name
- changed files since last closure
- current phase state
- whether `data/` is included intentionally
- known exclusions
- known cleanup items
- test commands/results if relevant

---

## Documents To Amend

Amend only as needed:

- `docs/ALPHA_3_0_RESTART_BRIEF.md`
- `docs/NEW_SESSION_PROMPT_ALPHA_3_0.txt`
- `docs/ACTION_LOG.md`

Do not modify:

- code
- tests
- `docs/PHASE_INDEX.md`
- phase docs
- case-packet implementation
- providers
- agents
- verifiers
- runtime state

---

## Required Amendments

### ALPHA_3_0_RESTART_BRIEF.md

Add `SNAPSHOT_HANDOFF_RELIABILITY` to the known watchlist items.

Include the core rule:

- Confirm the canonical snapshot before treating archive contents as repo truth.
- Prefer smaller handoffs when a full repo archive is unnecessary.
- Treat full-folder snapshots as acceptable but noisy.

### NEW_SESSION_PROMPT_ALPHA_3_0.txt

Add a brief instruction to Alpha 3.0:

- If a snapshot is supplied, confirm the canonical archive/source.
- Inspect the archive root structure before relying on it.
- Watch for stale uploads, duplicate filenames, accidental nested path artifacts, `__pycache__`, `.pyc`, and `Zone.Identifier` noise.
- Prefer repo truth from the current canonical snapshot.

Do not make the prompt long or procedural-heavy.

### ACTION_LOG.md

Append a concise entry recording that snapshot handoff reliability was added as an Alpha 3.0 watchlist item.

Mention:

- no code changed
- no tests changed
- `PHASE_INDEX.md` not modified
- no Phase 61 admitted

---

## Non-Goals

Do not:

- implement snapshot tooling
- add scripts
- modify build code
- modify tests
- create a cleanup phase
- create Phase 61
- modify `PHASE_INDEX.md`
- delete runtime data
- rewrite the Alpha 3.0 restart docs broadly

This is a restart-context addendum only.

---

## Success Criteria

This addendum is complete only when:

1. `SNAPSHOT_HANDOFF_RELIABILITY` appears in `docs/ALPHA_3_0_RESTART_BRIEF.md`.
2. `docs/NEW_SESSION_PROMPT_ALPHA_3_0.txt` instructs Alpha 3.0 to confirm canonical snapshot/source and watch for archive noise.
3. `docs/ACTION_LOG.md` records the docs-only addendum.
4. No code files are modified.
5. No test files are modified.
6. `docs/PHASE_INDEX.md` is not modified.
7. No Phase 61 is admitted.

---

## Completion Report Required

At completion, report:

- files modified
- confirmation no code files were modified
- confirmation no test files were modified
- confirmation `docs/PHASE_INDEX.md` was not modified
- confirmation no Phase 61 was admitted
- any assumptions or uncertainties

Then STOP.

Do not propose Phase 61.

---

## Addendum Reminder

This is not a new project direction.

It is a reliability note for how Alpha 3.0 should interpret repo snapshots.

The goal is to reduce confusion at handoff, not create more process.
