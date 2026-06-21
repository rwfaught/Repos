# PHASE_36.md

## Phase 36: Duplicate-Awareness for Response Task Creation

---

## Goal

Add bounded duplicate-awareness to explicit response-task creation so repeated operator invocation against the same eligible source result does not silently create redundant queued descendants.

This phase should preserve explicit operator control while preventing unnecessary lineage clutter in the recommendation-to-response ladder.

This is a hardening phase.

It is NOT about:
- automatic deduplication across the whole system
- queue policy changes
- automation
- blocking all repeated actions forever
- redesigning provenance broadly
- broad CLI refactoring

---

## Problems This Phase Must Solve

### Problem 1: Explicit Response Commands Can Create Redundant Descendants From the Same Source Result

The system currently allows repeated explicit invocation of:

- `create-followup-review --task <source_task_id>`
- `create-repair-task --task <source_task_id>`

against the same eligible source result.

That remains explicit and operator-triggered, which is good.

But it also means the ladder can accumulate redundant queued response tasks that:
- point to the same source task
- represent the same response intent
- clutter later surfaces

This phase should reduce that clutter without introducing hidden automation or broad policy behavior.

---

### Problem 2: Explicitness Should Not Become Repetition-Driven Sprawl

This project’s control model depends on explicit bounded packets.

Repeated creation of materially equivalent response tasks from the same source result weakens inspectability even when no hidden routing exists.

This phase should add bounded duplicate-awareness while preserving operator-triggered control.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/run_manager.py`
- `main.py`
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to add bounded duplicate-awareness to response-task creation.

---

## Required Hardening

The system must detect when an equivalent response task already exists for the same source result and response type.

At minimum, duplicate-awareness should apply to:

- follow-up review creation from eligible `needs_review` results
- repair-task creation from eligible `verification_failed` / `execution_failed` results

A minimal acceptable equivalence rule is:

A response task should be treated as an existing equivalent if it has:
- the same `source_task_id`
- the same `recommendation_type`
- and a live task state that still makes the duplicate operationally redundant

Recommended live states to consider duplicate-blocking:
- `queued`
- `in_progress`

You may include `needs_review` or other states only if clearly justified, but do not broaden casually.

Choose the smallest clear implementation.

---

## Behavior Requirement

When an equivalent response task already exists, the explicit creation command should:

- print a clear message
- avoid creating a new redundant task
- preserve full read-only clarity about what existing task caused the block

At minimum the message should identify:
- existing task ID
- title
- status

This phase should not silently succeed.
It should explicitly surface why no new task was created.

---

## Non-Blocking Cases

This phase should not overreach.

It should NOT automatically block creation when:
- the earlier equivalent task is already completed
- the earlier equivalent task is clearly no longer a live redundant descendant
- equivalence is ambiguous

Do not design a broad policy engine here.

The goal is bounded duplicate-awareness, not universal deduplication.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy broadly
- Do NOT redesign response commands
- Do NOT redesign provenance
- Do NOT introduce a global deduplication subsystem
- Do NOT bundle in bounded-scope inheritance work or broader identity cleanup

This is duplicate-awareness hardening only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Duplicate Follow-Up Review Attempt While Existing Equivalent Task Is Queued

Expected:
- no new task is created
- clear duplicate message is printed
- existing task identity is surfaced

### Test B: Duplicate Repair Attempt While Existing Equivalent Task Is Queued

Expected:
- no new task is created
- clear duplicate message is printed
- existing task identity is surfaced

### Test C: Re-Creation Allowed After Prior Equivalent Task Is No Longer Live

Expected:
- if prior equivalent task is completed or otherwise no longer duplicate-blocking
- new explicit response-task creation is allowed

### Test D: No Hidden Behavior Change

Expected:
- no auto-execution
- no queue policy drift
- no hidden routing
- existing recommendation lifecycle regressions still pass

---

## Success Criteria

- explicit response-task creation no longer silently proliferates redundant live descendants from the same source result
- operator control remains explicit
- duplicate blocking is bounded and understandable
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was hardened
   - which files were created or modified

2. Report:
   - how duplicate-awareness now works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
