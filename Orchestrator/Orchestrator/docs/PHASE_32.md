# PHASE_32.md

## Phase 32: Explicit Follow-Up Review Creation from `needs_review` Recommendation Results

---

## Goal

Add a bounded, explicitly operator-triggered bridge from post-execution recommendation-derived results in `needs_review` state to creation of a new follow-up review task.

This phase should allow the operator to:

- select one post-execution recommendation-derived result in `needs_review`
- create one bounded follow-up review task from that result
- preserve traceability back to the originating recommendation-derived task and source chain
- keep all behavior explicit, minimal, and inspectable

This phase is about explicit follow-up review creation, not automatic response handling.

It is NOT yet about:
- automatic follow-up task creation
- automatic re-review
- automatic repair creation
- automatic re-execution
- queue policy changes
- bulk response execution
- broader workflow automation
- status-model redesign

---

## Problems This Phase Must Solve

### Problem 1: `needs_review` Recommendation-Derived Results Now Expose Response Options but Cannot Yet Be Acted On Explicitly

The system can now:
- execute recommendation-derived tasks
- surface their post-execution results
- show bounded operator-response options for those results

But the operator still cannot directly tell the system:

- create follow-up review work for this `needs_review` result

This phase should create that explicit bridge.

---

### Problem 2: Response Options Should Become Operator-Executable Before Any Automatic Handling Is Considered

Before any future phase considers automatic response behavior, the system should support explicit operator-triggered creation of a single bounded follow-up review task from an eligible `needs_review` recommendation-derived result.

This phase must not change queue behavior or add automatic routing.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/run_manager.py`
- `orchestrator/task_schema.py` (only if a minimal traceability extension is clearly necessary)
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT redesign execution flow broadly.
Do NOT redesign recommendation semantics broadly.
Do NOT add automation.

---

## Core Behavior

Add a bounded CLI command:

`python main.py create-followup-review --task <task_id>`

Required behavior:

- operator must explicitly provide:
  - task ID

The command must:

1. load the specified task
2. verify that the task is an eligible post-execution recommendation-derived result:
   - recommendation-created
   - post-execution under existing Phase 30 semantics
   - final task status is exactly `needs_review`
3. create one new queued follow-up review task
4. persist that task through normal task persistence
5. print a clear summary of what was created

If the task is not found:
- print a clear message
- do not create anything

If the task is not an eligible `needs_review` recommendation-derived result:
- print a clear message
- do not create anything

Do NOT fall back to:
- first matching task
- active run latest result
- any implicit selection behavior

The task ID must be authoritative.

---

## Follow-Up Review Task Requirements

The created task must be minimal and explicit.

At minimum it should include:

- real task ID
- same run ID as the source result task
- role appropriate for bounded review follow-up work
- status = `queued`
- source task linkage back to the executed recommendation-derived result task
- source artifact linkage where available
- human-readable review reason or equivalent traceability
- success criteria small and bounded
- files in scope minimal or empty if unknown
- retry count initialized appropriately

Recommended title pattern:

- `Follow-up review for <source_task_id>`

Recommended role:
- `reviewer`

The created task should be clearly distinguishable as follow-up review work created from a `needs_review` post-execution result.

Do NOT:
- auto-execute the new task
- create multiple tasks
- infer complex dependencies
- create repair tasks in this phase

---

## Traceability Rules

The new follow-up review task should preserve enough traceability to answer:

- which executed recommendation-derived result caused this follow-up review task to exist
- what original source chain it belongs to

Use existing normalized provenance patterns where possible.
Add the smallest necessary extension only if existing fields are insufficient.

Do NOT introduce a large provenance object.

---

## Output Requirements

On successful creation, print at least:

- created task ID
- run ID
- title
- role
- status
- source task ID
- source artifact ID (if available)
- note that the task was created from a `needs_review` recommendation-derived result

On failure to qualify, print clear messages for:
- task not found
- task not recommendation-derived
- task not post-execution
- task status not `needs_review`

Do NOT:
- emit raw JSON
- imply that the created follow-up review task has already executed
- modify unrelated tasks

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce automatic follow-up behavior
- Do NOT change queue or execution policy
- Do NOT create repair tasks
- Do NOT bulk-create tasks
- Do NOT redesign statuses
- Do NOT alter unrelated tasks

This phase is explicit one-task follow-up review creation only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Create Follow-Up Review from Eligible `needs_review` Recommendation-Derived Result

Expected:
- one queued follow-up review task is created
- task fields and traceability are persisted
- clear creation summary is printed

---

### Test B: Reject Recommendation-Derived Result With Non-`needs_review` Status

Expected:
- clear message
- no task created

---

### Test C: Reject Ordinary Task

Expected:
- clear message
- no task created

---

### Test D: Reject Missing Task ID

Expected:
- clear not-found message
- no task created

---

### Test E: No Queue / Execution Behavior Change

Expected:
- ordinary `next` behavior remains unchanged
- no automatic execution of created follow-up review task occurs

---

## Success Criteria

- a bounded explicit follow-up review creation command exists
- only explicitly selected eligible `needs_review` recommendation-derived results can create follow-up review tasks
- traceability is preserved in a small explicit way
- no automatic or hidden behavior is introduced
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how eligible source results are detected
   - how follow-up review task creation works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
