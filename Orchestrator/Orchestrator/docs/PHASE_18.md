# PHASE_18.md

## Phase 18: Explicit Proposal Approval + Controlled Task Creation

---

## Goal

Add a bounded, explicitly user-triggered bridge from draft recommendation-derived proposals into real queued tasks.

This phase should allow the operator to:

- select a specific draft proposal
- materialize it as a real queued task
- preserve traceability to the originating recommendation, source task, and source artifact
- keep task creation deterministic, explicit, and minimal

This phase is about controlled task creation by explicit operator approval.

It is NOT yet about:
- automatic task creation
- recommendation-driven routing
- retry loops
- automatic execution of created tasks
- writeback/application logic
- task mutation beyond creating the new queued task
- autonomous prioritization or ranking

---

## Problems This Phase Must Solve

### Problem 1: Draft Proposals Exist but Cannot Yet Become Real Tasks

The system can now:
- surface recommendation records
- interpret recommendation state
- show actionable recommendation-linked items
- prepare draft follow-up task proposals

But those proposals are still read-only output.

There is no explicit, controlled bridge from approved proposal to real task record.

This phase should create that bridge.

---

### Problem 2: The First Executive Step Must Be Explicitly Human-Triggered

The system is now close to the boundary where recommendation state could influence workflow state.

That step must not happen implicitly.

This phase must ensure that:
- task creation happens only through explicit CLI approval
- one proposal is materialized deliberately
- no hidden routing or automatic creation is introduced

---

## Files to Create

Create only the minimum new file(s) needed.

Preferred:
- no new files if existing task persistence and recommendation helpers can be reused cleanly

Optional:
- `orchestrator/recommendation_store.py` may be extended minimally for proposal lookup helpers

Do NOT create an autonomous routing or approval engine.

---

## Files to Modify

- `main.py`
- `orchestrator/run_manager.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

If strictly needed:
- `orchestrator/recommendation_store.py`
- `orchestrator/task_schema.py` (minimal extension only if clearly necessary)

Do NOT redesign task persistence.
Do NOT modify reviewer recommendation semantics.
Do NOT modify recommendation record structure.

---

## Core Behavior

Add a bounded CLI command for explicit proposal approval and task creation.

Recommended command:

`python main.py recommendation-create --run <run_id> --source-task <source_task_id> --type <recommendation_type>`

Required behavior:

- operator must explicitly provide:
  - target run ID
  - source task ID
  - recommendation type

The command must:

1. load recommendation records for the target run
2. locate the matching actionable recommendation record
3. deterministically derive the corresponding draft proposal shape
4. create one real queued task from that proposal
5. save the new task into normal task persistence
6. print a clear summary of what was created

If no matching actionable proposal exists:
- print a clear message
- create nothing

Keep behavior:
- explicit
- deterministic
- minimal
- operator-triggered

---

## Actionable Recommendation Types

This phase should support creation only from:

- `repair_candidate`
- `manual_followup`

Do NOT create tasks from:
- `accept`

If `accept` is requested:
- print a clear message
- create nothing

---

## Created Task Requirements

The created task must be a normal persisted task record.

At minimum it should include:

- real task ID
- run ID
- title
- role
- status = `queued`
- dependencies (minimal, explicit)
- success criteria
- files in scope (minimal or empty if unknown)
- retry count
- traceability back to:
  - source task ID
  - source artifact ID
  - originating recommendation type

If `expected_output` is already part of the task schema and is useful here, it may be set minimally.

Do NOT create elaborate schema additions unless truly necessary.

---

## Deterministic Proposal-to-Task Mapping

Task creation must be deterministic.

Recommended mapping:

### From `repair_candidate`
- role: `coder`
- title: `Repair follow-up for <source_task_id>`

### From `manual_followup`
- role: `reviewer`
- title: `Manual follow-up for <source_task_id>`

Recommended status:
- `queued`

Recommended dependencies:
- minimal and explicit only if clearly justified
- otherwise keep empty rather than inventing complex dependency logic

Recommended success criteria:
- small, human-readable, bounded

Do NOT:
- infer complex dependency graphs
- generate multiple tasks from one command
- create planner tasks automatically
- assign hidden routing metadata

---

## Proposal Matching Rules

Matching logic must be simple and explicit.

A valid match requires:
- same run ID
- same source task ID
- same recommendation type
- actionable recommendation record exists

If multiple exact matches exist:
- use a simple deterministic rule, such as the most recent matching record
- document the rule clearly in output or summary

Keep matching minimal.
Do NOT introduce fuzzy matching.

---

## Output Requirements

On successful creation, print at least:

- created task ID
- run ID
- title
- role
- originating recommendation type
- source task ID
- source artifact ID
- status

On no match:
- print a clear no-match message

On unsupported type:
- print a clear unsupported-type message

Do NOT:
- create a large approval UI
- imply that the created task has executed
- auto-run the created task

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce automatic task creation
- Do NOT execute the created task automatically
- Do NOT alter existing tasks
- Do NOT redesign persistence
- Do NOT broaden CLI into a full proposal-management interface
- Do NOT introduce hidden routing behavior
- Do NOT create tasks from `accept`
- Do NOT imply approval beyond the explicit CLI command

This phase is explicit creation only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Create Task From Repair Candidate

Expected:
- matching repair-candidate recommendation found
- one new queued task created
- task fields match deterministic mapping
- traceability fields preserved

---

### Test B: Create Task From Manual Follow-Up

Expected:
- matching manual-followup recommendation found
- one new queued task created
- task fields match deterministic mapping
- traceability fields preserved

---

### Test C: Reject Accept Recommendation

Expected:
- clear message
- no task created

---

### Test D: No Matching Recommendation

Expected:
- clear no-match message
- no task created

---

### Test E: Explicit Creation Only

Running unrelated commands must not create tasks.

The creation command must only create a task when explicit CLI approval is given with matching inputs.

---

## Success Criteria

- a bounded explicit-approval CLI surface exists
- actionable recommendation records can be materialized into real queued tasks
- task creation is deterministic and minimal
- traceability is preserved
- unsupported or missing matches create nothing
- no automatic routing or execution behavior is introduced
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how proposal matching works
   - how task creation mapping works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
