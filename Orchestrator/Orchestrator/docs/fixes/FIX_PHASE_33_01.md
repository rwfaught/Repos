# FIX_PHASE_33_01.md

## Fix: Restore Single-Step `next` Behavior

---

## Purpose

Correct a bounded-execution violation in the `next` command.

The project’s progression model depends on `next` meaning one explicit step of ordinary task progression.

If `next` currently processes more than one task per invocation, that violates the system’s bounded-execution discipline.

This fix must restore single-step `next` behavior.

---

## Problem

The `next` command is intended to process one runnable task per invocation.

If the current implementation calls the per-task execution path twice during one `next` command, then ordinary progression is no longer:

- explicit
- single-step
- easily inspectable

That creates hidden execution behavior and weakens the project’s core governance model.

This is a control-surface defect, not just a UX issue.

---

## Goal

Ensure that `python main.py next` processes at most one task per invocation.

After this fix:

- `next` must not execute two tasks in one call
- queue progression must remain single-step and explicit
- provider behavior and ordinary selection semantics must remain otherwise unchanged

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

If strictly needed:
- `orchestrator/engine.py`

Do NOT broaden changes beyond what is necessary to restore single-step behavior.

---

## Required Correction

The `next` command must:

- resolve the provider exactly as it currently should
- invoke ordinary next-task execution exactly once
- stop after that single invocation

Do NOT:
- change task selection logic
- change provider semantics
- change queue ordering
- add convenience looping
- add automation
- bundle in unrelated fixes

This is a bounded execution-restoration fix only.

---

## Constraints

- Keep this fix tightly scoped
- Do NOT redesign execution flow broadly
- Do NOT change ordinary provider behavior
- Do NOT change queue semantics beyond restoring one-step progression
- Do NOT mix in result-option wording fixes
- Do NOT mix in artifact-traceability fixes

This fix restores single-step `next` behavior only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Single Runnable Task

Expected:
- `next` processes that one task
- no second execution attempt occurs

### Test B: Multiple Runnable Tasks

Expected:
- `next` processes only one task
- remaining runnable tasks stay queued

### Test C: Provider Behavior Unchanged

Expected:
- provider selection/default behavior remains the same as before

### Test D: No Hidden Regression

Expected:
- explicit ready-candidate execution behavior remains unchanged
- no unrelated queue policy change is introduced

---

## Success Criteria

- `next` now performs at most one task execution per invocation
- bounded single-step progression is restored
- no unrelated workflow behavior is changed
- no architectural drift is introduced

---

## End of Fix

STOP after completion.

Then:

1. Summarize:
   - what was corrected
   - which files were modified

2. Append a concise entry to:
   `docs/ACTION_LOG.md`

3. Update fix tracking in:
   `docs/PHASE_INDEX.md`

4. Do NOT proceed further
