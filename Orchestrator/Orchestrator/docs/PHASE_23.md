# PHASE_23.md

## Phase 23: Confirmed Recommendation-Task Readiness Semantics

---

## Goal

Add a bounded semantic distinction for confirmed recommendation-created tasks so the system can explicitly surface them as ready for ordinary workflow consideration.

This phase should allow the operator to:

- see which recommendation-created tasks are considered ready
- understand readiness as a consequence of existing confirmation state
- distinguish readiness from execution
- preserve the separation between semantic readiness and actual task processing

This phase is about readiness semantics and visibility, not execution behavior.

It is NOT yet about:
- automatic execution of ready tasks
- task selection changes in `next`
- queue reordering
- routing based on readiness
- automatic confirmation
- schema redesign beyond the smallest necessary extension
- batch operations

---

## Problems This Phase Must Solve

### Problem 1: Confirmation Exists but Its Workflow Meaning Is Still Too Implicit

The system can now:
- create recommendation-derived tasks
- surface their lineage
- review them as a distinct class
- explicitly confirm them
- surface confirmed vs unconfirmed counts

But it still does not clearly express the next semantic step:

- confirmed recommendation-created task = ready for ordinary workflow consideration

This phase should make that meaning explicit.

---

### Problem 2: Readiness Must Become Visible Before It Becomes Consequential

Before any future phase considers changing execution or selection behavior based on confirmation, the system must first surface readiness as a bounded, inspectable concept.

This phase must improve semantic visibility without changing workflow execution rules.

---

## Files to Create

Create only the minimum new file(s) needed.

Preferred:
- no new files if existing task-loading and review-surface helpers can be reused cleanly

Optional:
- no helper files unless a very small read-only helper clearly improves clarity

Do NOT create a queue-policy layer.

---

## Files to Modify

- `main.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

If strictly needed:
- `orchestrator/run_manager.py`
- `orchestrator/task_schema.py` (only if persistence proves necessary, which should be avoided if readiness can be derived)

Do NOT modify task execution semantics.
Do NOT modify confirmation semantics from Phase 21.
Do NOT redesign traceability schema in this phase.
Do NOT mutate task state unless absolutely necessary.

---

## Core Behavior

### 1. Readiness Semantics

A recommendation-created task should be considered **ready** only if:

- it clearly appears recommendation-created using existing strict traceability logic
- `recommendation_confirmed == True`

Prefer deriving readiness from existing persisted data.

Do NOT persist a new readiness field unless implementation proves that derivation is insufficient.

---

### 2. Status Surfacing

Extend `python main.py status` so that, when an active run exists, it now includes:

- ready recommendation-created task count

The existing recommendation-created summary should remain concise.

Example shape:

- Recommendation-created tasks: `<total>`
- Confirmed recommendation-created tasks: `<count>`
- Unconfirmed recommendation-created tasks: `<count>`
- Ready recommendation-created tasks: `<count>`

If readiness is equivalent to confirmed recommendation-created tasks in the current model, that is acceptable.
The value of this phase is making that meaning explicit.

---

### 3. Dedicated Readiness Surface

Add a bounded read-only CLI command:

`python main.py ready-recommendation-tasks`

Optional bounded variant:

`python main.py ready-recommendation-tasks --run <run_id>`

If no run filter is provided:
- use the active run
- if no active run exists, print a clear message and stop

The command must show:

- target run ID
- ready recommendation-created task count

For each ready task, show at minimum:

- task ID
- title
- role
- status
- recommendation confirmation state
- source task ID
- source artifact ID

Optional if already present and easy to show:
- recommendation type
- confirmation timestamp
- success criteria

Keep output:
- explicit
- deterministic
- read-only
- human-readable

---

## Readiness Rules

Readiness must be:

- derived or minimally represented
- read-only in this phase
- separate from task selection
- separate from execution

Do NOT:
- modify `next`
- auto-run ready tasks
- prefer ready tasks in queue logic
- hide unconfirmed tasks
- imply that ready tasks will execute automatically

This phase is semantic surfacing only.

---

## Output Requirements

### Status output

Must include a concise ready-task count when an active run exists.

Do NOT let this dominate the status surface.

### Ready-task command output

Must include at least:

- run ID
- ready task count
- one readable block per ready task showing:
  - task ID
  - title
  - role
  - status
  - recommendation confirmation state
  - source task ID
  - source artifact ID

Do NOT:
- emit raw JSON
- create a full workflow dashboard
- imply execution behavior
- modify task or recommendation state

If no ready recommendation-created tasks are found:
- print a clear message

---

## Reuse Guidance

If existing helpers from earlier phases can be reused, prefer that.

Do NOT duplicate recommendation-created-task detection logic if reuse keeps the implementation smaller.

Do NOT broaden helpers into a queue-governance engine.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce execution behavior
- Do NOT change task selection semantics
- Do NOT reorder queue behavior
- Do NOT alter existing tasks unless persistence is absolutely necessary
- Do NOT redesign persistence or schema broadly
- Do NOT introduce hidden routing behavior

This phase is readiness semantics only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Active Run With Mixed Confirmed and Unconfirmed Recommendation-Created Tasks

Expected:
- `status` shows ready count correctly
- ready-task command shows only confirmed recommendation-created tasks

---

### Test B: Run With Recommendation-Created Tasks but None Ready

Expected:
- ready count = 0
- ready-task command prints clear no-ready-tasks message

---

### Test C: Run With No Recommendation-Created Tasks

Expected:
- ready count = 0
- ready-task command prints clear no-ready-tasks message
- no crash

---

### Test D: No Active Run and No --run Argument

Expected:
- clear message
- stop without crash

---

### Test E: Read-Only Guarantee

Running `status` and `ready-recommendation-tasks` must not:
- modify state
- modify runs
- modify tasks
- create artifacts
- create recommendation records

---

## Success Criteria

- readiness is explicitly surfaced as a bounded concept for confirmed recommendation-created tasks
- `status` includes ready-task count
- dedicated ready-task command exists and is read-only
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
   - how readiness detection works
   - how status and ready-task surfacing work
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
