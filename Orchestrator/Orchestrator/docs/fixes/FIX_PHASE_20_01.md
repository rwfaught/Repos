# FIX_PHASE_20_01.md

## Fix: PHASE_INDEX Completion Rule Consistency After Final Defined Phase

---

## Purpose

Correct an internal governance inconsistency in `docs/PHASE_INDEX.md`.

The file’s current live control state correctly supports the case where all currently defined phases are complete and no next phase has yet been authored.

However, the `Completion Update Rule` still contains older wording that assumes the next phase always exists and should always become the new `Current Phase`.

This fix must align that rule with the already-adopted control-state model.

---

## Problem

`docs/PHASE_INDEX.md` currently contains logic equivalent to:

- mark the completed phase as done
- set the next phase as the Current Phase

That wording is no longer universally correct.

After the final currently defined phase is completed and no next phase document exists, the correct control state is:

- completed phases remain marked complete
- `Current Phase` becomes:
  - `(none — awaiting next phase definition)`

So the rule text and the live control model are now out of sync.

This is a governance inconsistency.

---

## Goal

Update `docs/PHASE_INDEX.md` so its `Completion Update Rule` explicitly supports both cases:

1. a next phase is defined
2. no next phase is defined yet

After this fix, the file must be internally consistent with the control-state behavior already in use.

---

## Files to Modify

- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`

---

## Required Correction

Revise the `Completion Update Rule` in `docs/PHASE_INDEX.md` so it clearly states:

- if a next phase is defined, set that phase as `Current Phase`
- if no next phase is defined, set `Current Phase` to:
  - `(none — awaiting next phase definition)`

Keep the wording concise and explicit.

Do NOT change the broader meaning of the document.
Do NOT alter phase order.
Do NOT alter fix tracking behavior.
Do NOT introduce placeholder future phases.

---

## Constraints

- Keep this fix tightly scoped
- Do NOT modify implementation code
- Do NOT redesign the broader governance model
- Do NOT add a new phase
- Do NOT alter any runtime behavior outside the docs

This is a docs-only constitutional correction.

---

## Validation Requirements

Validate at least these cases:

### Test A: Normal Case With Next Phase Defined

Expected:
- rule text still supports normal forward progression

### Test B: Final Defined Phase Completed With No Next Phase Defined

Expected:
- rule text now explicitly supports:
  - `(none — awaiting next phase definition)`

### Test C: No Other Control Semantics Disturbed

Expected:
- phase order unchanged
- fix tracking unchanged
- continue behavior remains coherent

---

## Success Criteria

- `PHASE_INDEX.md` no longer contains contradictory completion-rule language
- the rule text matches the current control-state model
- no unrelated governance or implementation changes are introduced

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
