# PHASE_22.md

## Phase 22: Confirmed Recommendation-Task Workflow Surfacing

---

## Goal

Add a bounded, read-only workflow surface that makes confirmed recommendation-created tasks visible as a distinct class of work.

This phase should allow the operator to:

- see how many recommendation-created tasks exist for a run
- distinguish between confirmed and unconfirmed recommendation-created tasks
- inspect confirmed recommendation-created tasks as queued, review-complete workflow items
- preserve the distinction between visibility and execution

This phase is about surfacing confirmed state in the ordinary workflow view.

It is NOT yet about:
- automatic execution of confirmed tasks
- queue reordering based on confirmation
- routing based on confirmation state
- batch confirmation
- task mutation beyond existing confirmation behavior
- schema redesign
- autonomous prioritization or ranking

---

## Problems This Phase Must Solve

### Problem 1: Confirmation State Exists but Is Not Yet Clearly Surfaced in Normal Workflow View

The system can now:
- create recommendation-derived queued tasks
- surface their lineage
- review them as a distinct class
- explicitly confirm them

But the ordinary workflow surface still does not clearly distinguish:

- recommendation-created tasks that are unconfirmed
- recommendation-created tasks that are confirmed
- ordinary queued tasks

This phase should make that distinction visible.

---

### Problem 2: Governance Markers Should Become Legible Before They Become Consequential

Confirmation is now a meaningful governance marker.

Before any future phase considers execution gating or workflow behavior tied to confirmation, the system must first surface that marker clearly in operator-facing workflow visibility.

This phase must improve visibility without changing execution rules.

---

## Files to Create

Create only the minimum new file(s) needed.

Preferred:
- no new files if existing task-loading and status/reporting helpers can be reused cleanly

Optional:
- no helper files unless implementation clearly benefits from a very small read-only helper

Do NOT create a queue-management or policy layer.

---

## Files to Modify

- `main.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

If strictly needed:
- `orchestrator/run_manager.py`

Do NOT modify task execution semantics.
Do NOT modify confirmation semantics from Phase 21.
Do NOT redesign traceability schema in this phase.
Do NOT mutate task state.

---

## Core Behavior

Add bounded workflow visibility for confirmed recommendation-created tasks.

Recommended minimum behavior:

### 1. Extend `python main.py status`

If an active run exists, status output should now include a concise recommendation-created-task summary:

- total recommendation-created tasks for active run
- confirmed recommendation-created task count
- unconfirmed recommendation-created task count

This summary must remain concise and read-only.

### 2. Add a dedicated read-only command

Recommended command:

`python main.py confirmed-recommendation-tasks`

Optional bounded variant:

`python main.py confirmed-recommendation-tasks --run <run_id>`

If no run filter is provided:
- use the active run
- if no active run exists, print a clear message and stop

The command should show, at minimum:

- target run ID
- count of confirmed recommendation-created tasks

For each matching task, show:

- task ID
- title
- role
- status
- recommendation confirmation state
- source task ID
- source artifact ID
- recommendation type, if available from current traceability representation

Optional:
- success criteria
- confirmation timestamp, if already present and easy to show without clutter

Keep output:
- explicit
- deterministic
- read-only
- human-readable

---

## Confirmed-Task Detection Rules

A task counts as a confirmed recommendation-created task only if:

- it clearly appears to be recommendation-created using existing strict traceability rules
- `recommendation_confirmed == True`

Use only existing persisted task data and current traceability fields.

Do NOT:
- infer recommendation origin from vague titles alone
- infer confirmation from anything other than the explicit stored confirmation field
- mutate tasks to improve surfacing

A minimal acceptable strategy is:

1. load tasks for the target run
2. identify recommendation-created tasks using existing strict detection
3. split them into confirmed vs unconfirmed using persisted confirmation state
4. surface summary in `status`
5. surface confirmed task blocks in the dedicated command

This is sufficient for this phase.

---

## Output Requirements

### Status output

If an active run exists, include concise lines such as:

- Recommendation-created tasks: `<count>`
- Confirmed recommendation-created tasks: `<count>`
- Unconfirmed recommendation-created tasks: `<count>`

Do NOT let this summary dominate status output.

### Dedicated confirmed-task command output

Must include at least:

- run ID
- confirmed task count
- one readable block per confirmed task showing:
  - task ID
  - title
  - role
  - status
  - recommendation confirmation state
  - source task ID
  - source artifact ID

Optional:
- recommendation type
- success criteria
- confirmation timestamp

Only if already present and easy to show without complexity.

Do NOT:
- emit raw JSON
- create a full task browser
- imply that confirmed tasks will execute automatically
- modify task or recommendation state

If no confirmed recommendation-created tasks are found:
- print a clear message

---

## Reuse Guidance

If existing helpers from earlier phases can be reused, prefer that.

Do NOT duplicate task-loading logic or recommendation-created-task detection logic if reuse keeps the implementation smaller.

Do NOT broaden helpers into a queue-governance engine.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce execution behavior
- Do NOT change task selection semantics
- Do NOT reorder queue behavior
- Do NOT alter existing tasks
- Do NOT redesign persistence or schema broadly
- Do NOT broaden CLI into a full workflow dashboard
- Do NOT introduce hidden routing behavior

This phase is workflow visibility only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Active Run With Mixed Confirmed and Unconfirmed Recommendation-Created Tasks

Expected:
- `status` shows total / confirmed / unconfirmed counts correctly
- dedicated command shows only confirmed recommendation-created tasks

---

### Test B: Run With No Recommendation-Created Tasks

Expected:
- status summary shows zero counts
- dedicated command prints clear no-confirmed-tasks message
- no crash

---

### Test C: Run With Recommendation-Created Tasks but None Confirmed

Expected:
- status distinguishes confirmed = 0, unconfirmed > 0
- dedicated command prints clear no-confirmed-tasks message

---

### Test D: No Active Run and No --run Argument

Expected:
- clear message
- stop without crash

---

### Test E: Read-Only Guarantee

Running the status command and confirmed-task command must not:
- modify state
- modify runs
- modify tasks
- create artifacts
- create recommendation records

---

## Success Criteria

- confirmed recommendation-created tasks are surfaced distinctly in ordinary workflow visibility
- status shows total / confirmed / unconfirmed recommendation-created task counts
- dedicated confirmed-task command exists and is read-only
- output is deterministic and clear
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
   - how confirmed-task detection works
   - how status surfacing works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
