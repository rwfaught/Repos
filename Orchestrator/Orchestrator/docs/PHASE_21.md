# PHASE_21.md

## Phase 21: Recommendation-Created Task Confirmation State

---

## Goal

Add a bounded, explicit confirmation mechanism for tasks that were created from recommendation approval.

This phase should allow the operator to:

- explicitly confirm an individual recommendation-created task
- persist that confirmation in the task record
- distinguish between recommendation-created tasks that merely exist and those that have been consciously accepted into normal workflow attention
- keep confirmation separate from execution

This phase is about human-triggered confirmation state, not execution.

It is NOT yet about:
- automatic execution of confirmed tasks
- routing based on confirmation state
- rejection workflows
- batch confirmation
- approval notes or complex approval metadata
- schema redesign beyond the smallest necessary extension

---

## Problems This Phase Must Solve

### Problem 1: Recommendation-Created Tasks Exist Without a Formal Confirmation Step

The system can now:
- create recommendation-derived queued tasks
- surface their lineage
- show them in a dedicated review surface

But it still does not distinguish between:
- recommendation-created tasks that simply exist
- recommendation-created tasks the operator has explicitly reviewed and accepted

This phase should create that distinction.

---

### Problem 2: The First Executive Bridge Needs a Minimal Governance Marker

Now that recommendation-derived task creation exists, the system needs a small explicit governance marker that says:
- this created task has been consciously accepted by the operator

This phase must add that marker without turning confirmation into execution.

---

## Files to Create

Create only the minimum new file(s) needed.

Preferred:
- no new files if existing task persistence and CLI flow can be extended minimally

Optional:
- no helper files unless implementation clearly benefits from a very small explicit helper

Do NOT create a full approval engine.

---

## Files to Modify

- `main.py`
- `orchestrator/task_schema.py` (minimal extension only)
- `orchestrator/run_manager.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

If strictly needed:
- `orchestrator/recommendation_store.py`

Do NOT redesign task persistence.
Do NOT modify task execution semantics.
Do NOT redesign broader traceability schema in this phase.

---

## Core Behavior

Add a bounded CLI command for explicit confirmation of a recommendation-created task.

Recommended command:

`python main.py recommendation-confirm --task <task_id>`

Required behavior:

- operator must explicitly provide:
  - task ID

The command must:

1. load the specified task
2. verify that the task clearly appears to be recommendation-created using existing traceability fields
3. set a minimal confirmation marker on the task
4. persist the updated task
5. print a clear summary of the confirmation result

If the task is not recommendation-created:
- print a clear message
- do not confirm it

If the task does not exist:
- print a clear message
- do not create or mutate anything

---

## Minimal Confirmation State

The smallest acceptable extension is:

- `recommendation_confirmed` (boolean)

Optional if clearly useful and minimal:
- `recommendation_confirmed_at` (timestamp string)

Do NOT add:
- approval taxonomies
- reviewer note systems
- rejection states
- workflow-state enums for confirmation
- batch state fields

Keep this phase minimal.

---

## Recommendation-Created Task Detection

A task may be confirmed only if existing persisted task data clearly indicates recommendation origin.

Use the same kind of strict traceability logic already used for lineage/review surfacing.

Do NOT:
- infer recommendation origin from vague titles alone
- allow arbitrary queued tasks to be confirmed through this command
- mutate unrelated tasks

---

## Confirmation Rules

Confirmation must be:

- explicit
- human-triggered
- idempotent or clearly handled if repeated
- separate from execution

If a task is already confirmed:
- print a clear message
- do not duplicate confirmation state changes unnecessarily

Do NOT:
- auto-run the task after confirmation
- move the task to `in_progress`
- change dependencies
- alter recommendation records

---

## Output Requirements

On successful confirmation, print at least:

- task ID
- title
- role
- status
- recommendation confirmation state

Optional:
- confirmation timestamp, if implemented

On failure cases, print clear messages for:
- task not found
- task not recommendation-created
- task already confirmed

Do NOT:
- emit raw JSON
- create a large approval UI
- imply that confirmation causes execution

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce execution behavior
- Do NOT introduce batch confirmation
- Do NOT introduce rejection workflows
- Do NOT redesign persistence broadly
- Do NOT alter unrelated tasks
- Do NOT introduce hidden routing behavior

This phase is explicit confirmation only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Confirm Recommendation-Created Task

Expected:
- target recommendation-created task is found
- confirmation state is persisted
- command prints clear success summary

---

### Test B: Confirm Already Confirmed Task

Expected:
- clear already-confirmed message
- no duplicate or unnecessary mutation

---

### Test C: Reject Ordinary Task

Expected:
- clear message that task is not recommendation-created
- no confirmation applied

---

### Test D: Missing Task ID

Expected:
- clear not-found message
- no mutation

---

### Test E: Confirmation Does Not Trigger Execution

Expected:
- task remains queued
- no automatic run begins
- no artifacts or recommendation records created

---

## Success Criteria

- a bounded explicit-confirmation CLI surface exists
- recommendation-created tasks can be individually confirmed
- confirmation state is persisted minimally
- ordinary tasks cannot be confirmed through this path
- confirmation remains separate from execution
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how recommendation-created task detection works
   - how confirmation state is stored
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
