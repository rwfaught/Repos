# PHASE_20.md

## Phase 20: Recommendation-Created Task Review + Confirmation Surfacing

---

## Goal

Add a bounded, read-only review surface for tasks that were created from explicit recommendation approval.

This phase should allow the operator to:

- list recommendation-created tasks for a run
- distinguish them from ordinary tasks
- inspect their core task fields together with their recommendation lineage
- treat them as a visible class of newly introduced work requiring human review

This phase is about review/confirmation visibility for recommendation-created tasks.

It is NOT yet about:
- automatic execution of created tasks
- task approval state mutation
- batch approval
- recommendation-driven routing
- retry loops
- writeback/application logic
- schema redesign

---

## Problems This Phase Must Solve

### Problem 1: Recommendation-Created Tasks Exist but Lack a Dedicated Review Surface

The system can now:
- create a real queued task from explicit recommendation approval
- surface lineage for such tasks

But those tasks do not yet have a dedicated bounded review surface as newly introduced workflow objects.

This phase should make them easier to review as a distinct class of tasks.

---

### Problem 2: The First Executive Bridge Needs Stronger Human Oversight Before Any Further Scaling

Now that recommendation-derived tasks can be created, the system should provide a clean operator-facing way to review those created tasks before any future expansion into broader creation or execution behavior.

This phase must improve visibility and reviewability without changing task state.

---

## Files to Create

Create only the minimum new file(s) needed.

Preferred:
- no new files if existing task/recommendation helpers can be reused cleanly

Optional:
- `orchestrator/recommendation_store.py` may be extended minimally if useful for read-only task review formatting

Do NOT create a task-approval engine.

---

## Files to Modify

- `main.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

If strictly needed:
- `orchestrator/run_manager.py`
- `orchestrator/recommendation_store.py`

Do NOT modify task execution semantics.
Do NOT modify task creation semantics from Phase 18.
Do NOT redesign traceability schema in this phase.
Do NOT mutate task state.

---

## Core Behavior

Add a bounded read-only CLI surface for reviewing recommendation-created tasks.

Recommended command:

`python main.py recommendation-created-tasks`

Optional bounded variant:

`python main.py recommendation-created-tasks --run <run_id>`

If no run filter is provided:
- use the active run
- if no active run exists, print a clear message and stop

The command should show, at minimum:

- target run ID
- count of recommendation-created tasks found for that run

For each matching task, show:

- task ID
- title
- role
- status
- success criteria
- source task ID
- source artifact ID
- originating recommendation type, if available from current traceability representation
- review reason, if present

Optional:
- files in scope, only if already present and easy to show without clutter

Keep output:
- explicit
- deterministic
- read-only
- human-readable

---

## Review-Surface Rules

A task should appear in this surface only if current persisted task data clearly indicates that it was created from recommendation approval.

Use only existing persisted task data and current traceability fields.

Do NOT:
- infer inclusion from vague naming alone if stronger traceability exists
- mutate tasks to mark them reviewed
- introduce approval state in this phase
- create any new tasks
- execute any tasks

A minimal acceptable strategy is:

1. load tasks for the target run
2. select tasks with clear recommendation-origin traceability
3. display a richer task-review block than the lineage command
4. remain fully read-only

This is sufficient for this phase.

---

## Output Requirements

CLI output must include at least:

- run ID
- recommendation-created task count
- one readable block per matching task showing:
  - task ID
  - title
  - role
  - status
  - success criteria
  - source task ID
  - source artifact ID

Optional:
- recommendation type
- review reason
- files in scope

Only if already present and easy to surface without complexity.

Do NOT:
- emit raw JSON
- create a large task browser
- imply tasks are approved or executed
- modify tasks or recommendation records

If no recommendation-created tasks are found:
- print a clear message

---

## Reuse Guidance

If existing helpers from earlier phases can be reused, prefer that.

Do NOT duplicate task-loading or recommendation-loading logic if reuse keeps the implementation smaller.

Do NOT broaden helpers into a task-governance engine.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce approval-state mutation
- Do NOT introduce additional task creation behavior
- Do NOT alter existing tasks
- Do NOT redesign persistence or schema broadly
- Do NOT broaden CLI into a full task-management interface
- Do NOT introduce hidden routing behavior
- Do NOT imply that review visibility changes workflow state

This phase is review visibility only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Run With Recommendation-Created Tasks

Expected:
- review command shows task count
- each task block shows task ID, title, role, status, success criteria, source task ID, and source artifact ID
- recommendation type shown if available

---

### Test B: Run With No Recommendation-Created Tasks

Expected:
- clear no-created-tasks message
- no crash

---

### Test C: No Active Run and No --run Argument

Expected:
- clear message
- stop without crash

---

### Test D: Read-Only Guarantee

Running the review command must not:
- modify state
- modify runs
- modify tasks
- create artifacts
- create recommendation records

---

## Success Criteria

- a bounded recommendation-created-task review CLI surface exists
- recommendation-created tasks are distinguishable from ordinary tasks
- core task fields and lineage are surfaced clearly
- output remains deterministic and read-only
- no new executive or approval behavior is introduced
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how recommendation-created task review surfacing works
   - whether helper reuse was used
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
