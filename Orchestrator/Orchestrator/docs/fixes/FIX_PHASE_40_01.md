# FIX_PHASE_40_01.md

## Fix: Restore Reviewer Semantic Separation in Recommendation Landing

---

## Purpose

Correct the semantic conflation introduced by Phase 40 so reviewer recommendation landing applies only to recommendation-emitter reviewer tasks, not automatically to all reviewer-role tasks.

This fix must preserve the good part of Phase 40:
- strict JSON-only recommendation landing
- minimal recommendation persistence
- reviewer-output validation after execution/verification precedence

But it must restore the earlier architectural distinction between:
- recommendation-emitter reviewer tasks
- manual-followup reviewer tasks created from response flow

---

## Problem

Phase 40 broadened reviewer recommendation landing to all reviewer-role tasks.

That created a behavioral contradiction:

- the codebase still preserves the semantic distinction between emitter reviewers and manual-followup reviewers in helper logic and tests
- but execution handling now forces both through the same recommendation-landing path

This means manual-followup reviewer tasks are effectively treated as recommendation emitters in execution behavior even though the architecture still names them as a distinct semantic class.

That is reviewer-role conflation.

---

## Goal

Restore reviewer semantic separation in execution handling.

After this fix:

- recommendation landing must apply only to recommendation-emitter reviewer tasks
- manual-followup reviewer tasks must not be forced through reviewer recommendation JSON landing automatically
- the earlier semantic split must again be coherent in both naming and behavior
- no hidden routing, recursion, or broad redesign should be introduced

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/engine.py`
- `orchestrator/run_manager.py` (only if helper usage/import adjustment is needed)
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to restore execution-time reviewer semantic separation.

---

## Required Correction

Execution handling must no longer gate reviewer recommendation landing on `task.role == "reviewer"` alone.

Instead, recommendation landing must apply only to the explicit emitter-reviewer boundary already present in the codebase.

A minimal acceptable correction is:

- use `is_recommendation_emitter_reviewer_task(task)` in execution routing for recommendation landing
- ensure manual-followup reviewer tasks are handled through the ordinary non-emitter path instead of the JSON recommendation landing path

The exact implementation is up to the worker, but it must restore alignment between:
- helper semantics
- tests
- execution behavior

---

## Behavior Preservation Requirement

This fix must preserve:

- strict JSON-only landing for recommendation-emitter reviewer tasks
- minimal recommendation persistence
- execution failure precedence
- verification failure precedence
- no auto-followup creation
- no auto-repair creation
- no hidden recursion
- no queue policy changes

This fix should only restore the missing execution boundary.

---

## Constraints

- Keep this fix tightly scoped
- Do NOT redesign reviewer routing broadly
- Do NOT redesign the recommendation schema
- Do NOT add automation
- Do NOT change queue or execution policy broadly
- Do NOT abolish the emitter/manual-followup distinction everywhere
- Do NOT bundle in unrelated hardening

This is reviewer-semantic-separation restoration only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Recommendation-Emitter Reviewer Task

Expected:
- strict JSON recommendation landing still applies
- valid JSON persists recommendation record
- invalid JSON fails in the existing bounded way

### Test B: Manual-Followup Reviewer Task

Expected:
- task is not forced through reviewer recommendation landing
- task follows the non-emitter reviewer behavior path
- no recommendation record is persisted merely because the task role is reviewer

### Test C: No Hidden Behavior Change

Expected:
- no auto-creation of new tasks
- no recursion introduced
- no queue policy drift
- no routing drift outside the intended boundary

### Test D: Existing Relevant Regressions Still Pass

Expected:
- reviewer recommendation tests still pass where appropriate
- lifecycle tests covering the manual-followup distinction still pass

---

## Success Criteria

- reviewer recommendation landing is again limited to recommendation-emitter reviewer tasks
- manual-followup reviewer tasks are no longer behaviorally conflated with emitters
- the codebase’s semantic split is restored coherently
- no unrelated architectural drift is introduced

---

## End of Fix

STOP after completion.

Then:

1. Summarize:
   - what was corrected
   - which files were modified

2. Report:
   - how reviewer semantic separation is now restored in execution handling
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update fix tracking in:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
