# FIX_PHASE_10_01.md

## Target

Phase 10

This fix applies to the implementation produced for:

- `PHASE_10.md`

---

## Issue Summary

Reviewer tasks created after output inadequacy are currently blocked from running.

The current implementation creates a reviewer task with:

- `dependencies = [original_task.id]`

But the scheduler only considers a dependency satisfied when the dependency task has:

- `status == "completed"`

In the inadequacy-routing path, the original task is set to:

- `needs_review`

Therefore, the reviewer task remains permanently blocked and never becomes runnable.

---

## Why This Matters

This breaks the main new behavior introduced by Phase 10.

The system can detect inadequate output and create a reviewer task, but the reviewer task cannot execute.

As a result, the adequacy-routing path is incomplete.

---

## Required Correction

Update reviewer task creation so that the reviewer task is runnable after the original task is marked `needs_review`.

The simplest correct fix is:

- reviewer tasks created through adequacy routing must NOT depend on the original task for scheduler eligibility

Preserve traceability using:
- `source_task_id`
- `source_artifact_id`
- `review_reason`

Do NOT rely on dependency status for reviewer routing in this fix.

---

## Files to Modify

- `orchestrator/run_manager.py`

---

## Files to Leave Unchanged Unless Strictly Necessary

- `orchestrator/task_schema.py`
- `orchestrator/engine.py`
- scheduler logic in `get_next_task(...)`
- provider logic
- verification logic

Do NOT redesign dependency resolution in this fix.

---

## Implementation Rule

In `create_reviewer_task(...)`, remove the blocking dependency on the original task.

The reviewer task should still contain:
- original task linkage
- source artifact linkage
- review reason

But it should be schedulable without requiring the original task to become `completed`.

---

## Constraints

- Keep this fix minimal
- Do NOT redesign scheduler behavior
- Do NOT redesign adequacy routing
- Do NOT add retries
- Do NOT add reviewer recursion
- Do NOT change task status semantics

This fix is only about making reviewer routing operational.

---

## Validation Requirements

Validate with an inadequate-output case.

Expected behavior:

1. original task executes successfully
2. verification passes
3. adequacy fails
4. original task becomes `needs_review`
5. reviewer task is created
6. reviewer task is `queued`
7. reviewer task is runnable by the scheduler

Confirm that the reviewer task no longer remains blocked.

---

## Success Criteria

- reviewer task is created successfully
- reviewer task preserves traceability fields
- reviewer task is runnable after creation
- no unrelated architecture changes are introduced

---

## End of Fix

STOP after completion.

Then:

1. summarize:
   - what was corrected
   - which files were modified
   - what validation was performed

2. append a concise entry to:
   - `docs/ACTION_LOG.md`

3. update `PHASE_INDEX.md` so this fix is no longer active

4. do NOT proceed to a new phase automatically