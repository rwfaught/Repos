# FIX_PHASE_33_02.md

## Fix: Align `recommendation-result-options` With Actual Available Response Paths

---

## Purpose

Correct stale operator-response wording in the read-only `recommendation-result-options` surface.

The system now supports explicit operator-triggered follow-up review creation and explicit operator-triggered repair-task creation for eligible recommendation-derived post-execution results.

The response-options surface must reflect that accurately.

---

## Problem

The current read-only response-option surface still includes wording equivalent to:

- "create follow-up review work later (not in this phase)"
- "consider repair/follow-up later (not in this phase)"
- "consider retry/repair later (not in this phase)"

That wording is now stale after the implementation of:

- explicit follow-up review creation for eligible `needs_review` results
- explicit repair-task creation for eligible `verification_failed` / `execution_failed` results

This creates a control-surface inconsistency:
the read-only operator guidance no longer matches the actual bounded response actions available in the system.

---

## Goal

Update the `recommendation-result-options` surface so it truthfully describes the currently available bounded operator-triggered response paths.

After this fix:

- the response surface must no longer imply that existing response paths are unavailable
- the surface must remain read-only
- the surface must remain bounded and non-automatic
- wording must stay concrete and small

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to correct the stale wording.

---

## Required Correction

Update the bounded response-option mapping used by `recommendation-result-options` so it accurately reflects the system’s current capabilities.

A minimal acceptable correction is:

- for `completed`:
  - keep a bounded note equivalent to:
    - no immediate follow-up required
    - review result if desired

- for `needs_review`:
  - surface bounded response options equivalent to:
    - inspect result
    - create follow-up review task explicitly if needed

- for `verification_failed`:
  - surface bounded response options equivalent to:
    - inspect failure details
    - create repair task explicitly if needed

- for `execution_failed`:
  - surface bounded response options equivalent to:
    - inspect execution failure
    - create repair task explicitly if needed

The wording may vary slightly, but it must remain:
- truthful
- read-only
- non-automatic
- bounded

Do NOT imply that the command performs those actions.
Do NOT add action execution to this surface.

---

## Constraints

- Keep this fix tightly scoped
- Do NOT redesign the response ladder
- Do NOT add new commands
- Do NOT change queue or execution policy
- Do NOT introduce automatic handling
- Do NOT bundle in artifact-traceability fixes

This is a control-surface wording fix only.

---

## Validation Requirements

Validate at least these cases:

### Test A: `needs_review` Response Surfacing

Expected:
- surface now truthfully indicates explicit follow-up review creation is available
- surface remains read-only

### Test B: `verification_failed` / `execution_failed` Response Surfacing

Expected:
- surface now truthfully indicates explicit repair-task creation is available
- surface remains read-only

### Test C: No Behavior Change

Expected:
- the command still only surfaces options
- no tasks are created
- no queue or execution behavior changes

---

## Success Criteria

- `recommendation-result-options` now matches the actual post-Phase-33 system
- stale “not in this phase” wording is removed where no longer true
- the surface remains bounded and non-automatic
- no unrelated architectural drift is introduced

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
