# PHASE_37.md

## Phase 37: Bounded Scope Inheritance for Response Tasks

---

## Goal

Harden follow-up review and repair task creation so response tasks inherit a minimal, truthful `files_in_scope` packet when that can be done safely from the source result task.

This phase should preserve explicit operator control while improving boundedness and inspectability of response-task execution packets.

This is a hardening phase.

It is NOT about:
- changing response commands
- queue policy changes
- automation
- redesigning provenance broadly
- broad task-schema redesign
- broad CLI refactoring

---

## Problems This Phase Must Solve

### Problem 1: Response Tasks Are the Loosest Packets in the Ladder

The system now creates follow-up review and repair tasks explicitly and with good provenance.

But these response tasks still commonly enter the queue with empty `files_in_scope`, even when the source result task already had a bounded file scope.

That weakens packet discipline at exactly the point where the ladder creates descendant work.

---

### Problem 2: Response Work Should Inherit Safe Boundaries When Available

If a source result task already has a truthful and bounded `files_in_scope`, the response task should usually inherit that packet rather than discard it.

This phase should improve boundedness without inventing scope, expanding scope, or creating false precision.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `orchestrator/run_manager.py`
- `orchestrator/task_schema.py` (only if strictly necessary; likely not needed)
- `main.py` (only if any creation surface should display inherited scope and only if strictly necessary)
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to improve bounded scope inheritance for response tasks.

---

## Required Hardening

When creating:

- follow-up review tasks from eligible `needs_review` results
- repair tasks from eligible `verification_failed` / `execution_failed` results

the system should inherit `files_in_scope` from the source result task when that source scope is:

- present
- already explicit
- safe to carry forward unchanged

A minimal acceptable rule is:

- if `source_task.files_in_scope` is a non-empty list, copy it directly onto the created response task
- if `source_task.files_in_scope` is empty or absent, preserve the current truthful empty behavior

Do NOT:
- invent new file scope
- merge scope from multiple ancestors
- broaden scope beyond the source result task
- infer scope from prose fields

Choose the smallest clear implementation.

---

## Behavior Requirement

The created response task should remain:

- explicit
- bounded
- truthful
- non-automatic

This phase should only strengthen the task packet by preserving safe scope when it already exists.

It should not create stronger claims than the source task justifies.

---

## Non-Goals

This phase must NOT:

- infer file scope from artifact content
- infer file scope from `review_reason`
- infer file scope from recommendation prose
- introduce scope heuristics
- add scope-policy machinery
- redesign task creation generally

This is simple scope inheritance only.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy broadly
- Do NOT redesign response commands
- Do NOT redesign provenance
- Do NOT bundle in further duplicate-awareness or identity-rule changes

This is response-packet boundedness hardening only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Follow-Up Review Inherits Non-Empty Source Scope

Expected:
- created follow-up review task receives the same `files_in_scope` as the eligible source result task

### Test B: Repair Task Inherits Non-Empty Source Scope

Expected:
- created repair task receives the same `files_in_scope` as the eligible source result task

### Test C: Empty Source Scope Remains Truthfully Empty

Expected:
- if the source result task has empty or missing `files_in_scope`
- created response task keeps empty scope
- no scope is invented

### Test D: No Hidden Behavior Change

Expected:
- no auto-execution
- no queue policy drift
- no provenance drift
- existing recommendation lifecycle regressions still pass

---

## Success Criteria

- follow-up review and repair tasks inherit safe bounded scope when available
- empty scope remains truthful when no source scope exists
- response-task packets become more bounded and inspectable
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was hardened
   - which files were created or modified

2. Report:
   - how response-task scope inheritance now works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
