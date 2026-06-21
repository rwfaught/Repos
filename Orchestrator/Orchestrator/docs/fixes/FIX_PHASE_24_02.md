# FIX_PHASE_24_02.md

## Fix: Separate Recommendation-Emitter Reviewer Semantics from Manual Follow-Up Review Semantics

---

## Purpose

Correct semantic overloading around reviewer-role tasks.

The current system distinguishes recommendation-derived follow-up work from ordinary task execution, but reviewer-role tasks are now carrying more than one meaning.

This fix must ensure that the system does not treat every reviewer-role task as if it were the same kind of reviewer task.

---

## Problem

The project currently has reviewer-role tasks that are intended to emit bounded recommendation records.

It also has recommendation-derived `manual_followup` tasks that may be created with role `reviewer`.

If engine behavior routes all reviewer-role tasks through the same recommendation-output validation path, then two distinct concepts collapse into one:

- reviewer as recommendation emitter
- reviewer as manual follow-up review worker

That creates hidden role semantics and weakens the project’s explicit-control model.

Roles should frame work clearly.
They should not silently encode multiple incompatible task classes.

---

## Goal

Make reviewer-task handling explicit enough that recommendation-emitter reviewer tasks are no longer conflated with manual follow-up review tasks.

After this fix, the system must be able to distinguish between:

1. reviewer tasks whose intended output is a bounded recommendation record
2. reviewer-role follow-up tasks whose purpose is different

This distinction must be implemented with the smallest necessary change.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/engine.py`
- `orchestrator/task_schema.py` (only if a minimal explicit discriminator is truly needed)
- `orchestrator/run_manager.py` (only if creation logic must be updated)
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to separate the semantics cleanly.

---

## Required Correction

The system must no longer rely on `task.role == "reviewer"` alone as the sole determinant of recommendation-output handling if that collapses distinct reviewer-task meanings.

A minimal acceptable correction may involve one of the following:

- a small explicit discriminator for recommendation-emitter reviewer tasks
- a narrower engine condition based on existing task fields if sufficient
- a small role/task-class distinction for manual follow-up review work

Choose the smallest clear implementation.

Do NOT redesign the entire role model.

---

## Constraints

- Keep this fix tightly scoped
- Do NOT redesign the architecture broadly
- Do NOT reopen adequacy routing generally
- Do NOT add new routing behavior
- Do NOT add automation
- Do NOT introduce broad schema growth
- Do NOT create a second control system through ad hoc special cases

This is a semantic separation fix, not a redesign phase.

---

## Validation Requirements

Validate at least these cases:

### Test A: Recommendation-Emitter Reviewer Task

Expected:
- recommendation-emitter reviewer task still follows recommendation-output validation path correctly

### Test B: Manual Follow-Up Review Task

Expected:
- manual follow-up review task is no longer incorrectly forced through recommendation-emitter semantics if that is not its intended class

### Test C: Ordinary Non-Reviewer Tasks

Expected:
- ordinary task behavior remains unchanged

### Test D: No Hidden Routing Regression

Expected:
- fix does not reintroduce recursive reviewer routing or hidden behavior changes elsewhere

---

## Success Criteria

- reviewer-role overloading is resolved
- recommendation-emitter reviewer behavior remains intact
- manual follow-up review tasks are semantically distinct where needed
- no unrelated workflow changes are introduced
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
