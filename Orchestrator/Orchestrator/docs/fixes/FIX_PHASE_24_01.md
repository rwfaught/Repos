# FIX_PHASE_24_01.md

## Fix: Acceptance Harness Must Propagate Command Failure

---

## Purpose

Correct a validation-trust defect in `run_acceptance_tests.sh`.

The current harness records command exit codes in logs and summaries, but the helper function still returns success even when the underlying command failed.

This fix must ensure that command failure is truthfully reflected in harness behavior.

---

## Problem

The acceptance harness currently captures command failures but does not propagate them as failures at the helper-function level.

This creates a misleading validation surface where:

- a command can fail
- the harness can log that failure
- but the helper still returns success

That weakens trust in acceptance validation.

In this project, validation is part of governance.
So failure propagation must be truthful and explicit.

---

## Goal

Update `run_acceptance_tests.sh` so command failure is no longer normalized into helper success.

After this fix:

- failed commands must remain visibly failed in summaries
- the harness must propagate failure truthfully
- the script may still continue or stop according to its intended design, but it must not misrepresent command success

---

## Files to Modify

- `run_acceptance_tests.sh`
- `docs/ACTION_LOG.md`

If test-plan wording must be adjusted for accuracy, only if strictly necessary:
- `TEST_PLAN.md`

Do NOT modify implementation code.

---

## Required Correction

Revise the harness so that:

- `run_cmd()` does not always return success
- failure truth is preserved in the shell behavior
- command-level failure can be detected reliably by the harness logic

Acceptable approaches include:

- returning the actual exit code from `run_cmd()`
- or clearly separating “record failure and continue” behavior from “pretend success”

Keep the implementation minimal and readable.

Do NOT redesign the harness into a complex test framework.

---

## Constraints

- Keep this fix tightly scoped
- Do NOT broaden the acceptance surface
- Do NOT redesign the test harness architecture
- Do NOT add CI tooling
- Do NOT modify project runtime behavior outside validation truthfulness

This is a trust-restoration fix for the validation layer.

---

## Validation Requirements

Validate at least these cases:

### Test A: Command Success

Expected:
- successful command is logged as pass
- harness behavior remains normal

### Test B: Command Failure

Expected:
- failed command is logged as fail
- helper/harness behavior no longer reports success for that command

### Test C: Summary Integrity

Expected:
- summary still clearly distinguishes pass/fail results
- failure remains visible and truthful

---

## Success Criteria

- acceptance harness no longer masks command failures
- validation output remains readable
- no unrelated harness redesign is introduced
- trust in acceptance results is improved

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
