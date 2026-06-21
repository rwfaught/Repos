# PHASE_19.md

## Phase 19: Recommendation-Lineage Status + Task Surfacing

---

## Goal

Make recommendation-created tasks visibly traceable through bounded, read-only workflow surfaces.

This phase should allow the operator to:

- identify which tasks in a run originated from explicit recommendation approval
- see the lineage of those tasks back to source task and source artifact
- inspect recommendation-origin task provenance without mutating workflow state
- preserve the distinction between provenance visibility and further executive behavior

This phase is about making recommendation-derived task lineage legible.

It is NOT yet about:
- bulk proposal approval
- automatic task creation
- recommendation-driven routing
- retry loops
- writeback/application logic
- schema redesign
- autonomous prioritization or ranking

---

## Problems This Phase Must Solve

### Problem 1: Recommendation-Created Tasks Exist but Their Origin Is Not Yet Clearly Surfaced

The system can now:
- prepare draft proposal cards from recommendation state
- explicitly create one real queued task from an approved proposal

But once such a task exists, its recommendation-derived origin is still too implicit.

This phase should make that lineage visible.

---

### Problem 2: Executive Workflow Mutation Requires Provenance Visibility

Now that the system can create real tasks from recommendation state, provenance matters more.

The operator should be able to see:
- which tasks were created from recommendation approval
- which source task and source artifact each came from
- what recommendation type led to their creation

This phase must improve visibility without adding more executive force.

---

## Files to Create

Create only the minimum new file(s) needed.

Preferred:
- no new files if existing task/recommendation helpers can be reused cleanly

Optional:
- `orchestrator/recommendation_store.py` may be extended minimally for lineage lookup helpers

Do NOT create a new routing or policy layer.

---

## Files to Modify

- `main.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

If strictly needed:
- `orchestrator/run_manager.py`
- `orchestrator/recommendation_store.py`

Do NOT modify task execution semantics.
Do NOT modify task creation semantics from Phase 18 unless a genuine defect is discovered.
Do NOT redesign traceability schema broadly in this phase.

---

## Core Behavior

Add a bounded read-only CLI surface for recommendation-derived task lineage.

Recommended command:

`python main.py recommendation-lineage`

Optional bounded variant:

`python main.py recommendation-lineage --run <run_id>`

If no run filter is provided:
- use the active run
- if no active run exists, print a clear message and stop

The command should show, at minimum:

- target run ID
- total count of recommendation-created tasks found for that run
- for each lineage-visible task:
  - task ID
  - title
  - role
  - status
  - source task ID
  - source artifact ID
  - originating recommendation type, if available from current traceability representation

If existing traceability stores recommendation type inside `review_reason` or another lightweight representation, it may be surfaced from there.

Keep output:
- explicit
- deterministic
- read-only
- human-readable

---

## Lineage Detection Rules

A task counts as recommendation-created only if current stored task fields clearly indicate that it originated from recommendation approval.

Use only existing persisted task data and traceability fields.

Do NOT:
- infer lineage from vague title patterns alone if stronger fields exist
- inspect unrelated files for hidden clues
- mutate task records to improve lineage
- redesign schema in this phase

A minimal acceptable strategy is:

1. load tasks for the target run
2. select tasks with clear recommendation-origin traceability
3. display bounded lineage summary for those tasks

This is sufficient for this phase.

---

## Output Requirements

CLI output must include at least:

- run ID
- count of recommendation-created tasks
- one readable block per matching task showing:
  - task ID
  - title
  - role
  - status
  - source task ID
  - source artifact ID

Optional:
- recommendation type
- review reason

Only if already present and easy to show without complexity.

Do NOT:
- emit raw JSON
- create a large task browser
- imply automatic action will occur
- modify tasks or recommendation records

If no recommendation-created tasks are found:
- print a clear message

---

## Reuse Guidance

If existing task-loading or recommendation helpers from earlier phases can be reused, prefer that.

Do NOT duplicate persistence-loading logic if reuse keeps the implementation smaller.

Do NOT broaden helpers into a general lineage engine.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce additional task creation behavior
- Do NOT alter existing tasks
- Do NOT redesign persistence or schema broadly
- Do NOT broaden CLI into a full task-management interface
- Do NOT introduce hidden routing behavior
- Do NOT imply that lineage visibility changes workflow state

This phase is provenance visibility only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Run With Recommendation-Created Tasks

Expected:
- lineage command shows recommendation-created task count
- task blocks show task ID, title, role, status, source task ID, and source artifact ID
- recommendation type shown if available from current representation

---

### Test B: Run With No Recommendation-Created Tasks

Expected:
- clear no-lineage-items message
- no crash

---

### Test C: No Active Run and No --run Argument

Expected:
- clear message
- stop without crash

---

### Test D: Read-Only Guarantee

Running the lineage command must not:
- modify state
- modify runs
- modify tasks
- create artifacts
- create recommendation records

---

## Success Criteria

- a bounded recommendation-lineage CLI surface exists
- recommendation-created tasks are visibly identifiable
- source-linked provenance is surfaced clearly
- output remains deterministic and read-only
- no new executive or routing behavior is introduced
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how lineage detection works
   - whether helper reuse was used
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
