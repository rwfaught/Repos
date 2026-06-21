# PHASE_24.md

## Phase 24: Ready-Task Execution Candidate Surfacing

---

## Goal

Add a bounded, read-only workflow surface that makes ready recommendation-created tasks visible as explicit execution candidates.

This phase should allow the operator to:

- see which ready recommendation-created tasks are currently eligible for explicit execution consideration
- inspect those tasks as a distinct class of queued work
- preserve the distinction between execution candidacy and actual execution
- keep all behavior deterministic, explicit, and read-only

This phase is about execution-candidate surfacing, not execution behavior.

It is NOT yet about:
- automatic execution of ready tasks
- changes to `next`
- queue reordering
- routing based on readiness
- automatic prioritization
- batch execution
- schema redesign

---

## Problems This Phase Must Solve

### Problem 1: Ready Recommendation-Created Tasks Exist but Their Operational Meaning Is Still Too Implicit

The system can now:
- create recommendation-derived tasks
- confirm them
- surface them as ready

But it still does not provide a bounded workflow surface that says:

- these ready tasks are now eligible for explicit execution consideration

This phase should make that operational meaning visible.

---

### Problem 2: Readiness Must Become Operationally Legible Before It Affects Queue Behavior

Before any future phase considers changing queue handling or execution rules based on readiness, the system must first surface ready tasks as execution candidates in a read-only way.

This phase must improve operational visibility without changing execution semantics.

---

## Files to Create

Create only the minimum new file(s) needed.

Preferred:
- no new files if existing task-loading and readiness helpers can be reused cleanly

Optional:
- no helper files unless a very small read-only helper clearly improves clarity

Do NOT create an execution-policy layer.

---

## Files to Modify

- `main.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

If strictly needed:
- `orchestrator/run_manager.py`

Do NOT modify task execution semantics.
Do NOT modify readiness semantics from Phase 23.
Do NOT mutate task state.

---

## Core Behavior

Add a bounded read-only CLI command:

`python main.py ready-execution-candidates`

Optional bounded variant:

`python main.py ready-execution-candidates --run <run_id>`

If no run filter is provided:
- use the active run
- if no active run exists, print a clear message and stop

The command should show only tasks that are:

- recommendation-created
- confirmed / ready
- `status == "queued"`

For the target run, show:

- run ID
- ready execution-candidate count

For each candidate task, show at minimum:

- task ID
- title
- role
- status
- source task ID
- source artifact ID

Optional if already present and easy to show:
- recommendation type
- confirmation timestamp
- success criteria

Output must clearly indicate:
- these tasks are eligible for explicit operator-chosen execution consideration
- this command does NOT execute them
- this command does NOT change queue behavior

---

## Candidate Detection Rules

A task counts as a ready execution candidate only if:

- it clearly appears recommendation-created using existing strict traceability logic
- it is ready under existing Phase 23 semantics
- `status == "queued"`

Use only existing persisted task data and current readiness logic.

Do NOT:
- infer candidacy from vague titles alone
- include non-queued tasks
- include unconfirmed tasks
- mutate tasks to improve surfacing

---

## Output Requirements

The command must include:

- run ID
- execution-candidate count
- one readable block per matching task showing:
  - task ID
  - title
  - role
  - status
  - source task ID
  - source artifact ID

Optional:
- recommendation type
- confirmation timestamp
- success criteria

Do NOT:
- emit raw JSON
- create a full workflow dashboard
- imply the tasks will run automatically
- modify task or recommendation state

If no ready execution candidates are found:
- print a clear message

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce execution behavior
- Do NOT change `next`
- Do NOT reorder queue behavior
- Do NOT alter existing tasks
- Do NOT redesign persistence or schema broadly
- Do NOT introduce hidden routing behavior

This phase is execution-candidate visibility only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Run With Ready Queued Recommendation-Created Tasks

Expected:
- command shows correct candidate count
- only ready queued recommendation-created tasks are listed

### Test B: Run With Ready Recommendation-Created Tasks That Are Not Queued

Expected:
- non-queued tasks are excluded

### Test C: Run With Recommendation-Created Tasks But None Ready

Expected:
- clear no-candidates message
- no crash

### Test D: No Active Run and No --run Argument

Expected:
- clear message
- stop without crash

### Test E: Read-Only Guarantee

Running the command must not:
- modify state
- modify runs
- modify tasks
- create artifacts
- create recommendation records

---

## Success Criteria

- a bounded ready-execution-candidates CLI surface exists
- ready queued recommendation-created tasks are surfaced clearly
- output is deterministic and read-only
- no execution or queue behavior changes are introduced
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how execution-candidate detection works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
