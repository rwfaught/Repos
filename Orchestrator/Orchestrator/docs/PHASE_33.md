# PHASE_33.md

## Phase 33: Explicit Repair Task Creation from Failed Recommendation Results

---

## Goal

Add a bounded, explicitly operator-triggered bridge from failed post-execution recommendation-derived results to creation of one new repair task.

This phase should allow the operator to:

- select one eligible failed recommendation-derived result by task ID
- create one bounded repair task from that result
- preserve traceability back to the failed result and its source chain
- keep all behavior explicit, minimal, and inspectable

This phase is about explicit repair-task creation, not automatic failure handling.

It is NOT yet about:
- automatic repair task creation
- automatic retry
- automatic re-execution
- queue changes
- routing based on failure
- bulk repair creation
- broader workflow automation
- status-model redesign

---

## Problems This Phase Must Solve

### Problem 1: Failed Recommendation-Derived Results Are Visible but Cannot Yet Be Acted On Through a Repair Path

The system can now:
- execute recommendation-derived tasks
- surface post-execution recommendation-derived results
- surface bounded operator-response options
- create follow-up review work for `needs_review` results

But the operator still cannot directly tell the system:

- create repair work for this failed recommendation-derived result

This phase should create that explicit bridge.

---

### Problem 2: Failure Response Should Become Operator-Executable Before Any Automatic Handling Is Considered

Before any future phase considers automatic retry or repair behavior, the system should support explicit operator-triggered creation of one repair task from an eligible failed result.

This phase must not change queue behavior or add automation.

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

`python main.py create-repair-task --task <task_id>`

Required behavior:

- operator must explicitly provide:
  - task ID

The command must:

1. load the specified task
2. verify that the task is an eligible post-execution recommendation-derived result:
   - recommendation-created
   - post-execution under existing Phase 30 semantics
   - final task status is exactly one of:
     - `verification_failed`
     - `execution_failed`
3. create one new queued repair task
4. persist that task through normal task persistence
5. print a clear summary of what was created

If the task is not found:
- print a clear message
- do not create anything

If the task is not an eligible failed recommendation-derived result:
- print a clear message
- do not create anything

Do NOT fall back to:
- first matching task
- active run latest result
- any implicit selection behavior

The task ID must be authoritative.

---

## Repair Task Requirements

The created task must be minimal and explicit.

At minimum it should include:

- real task ID
- same run ID as the source failed-result task
- role appropriate for bounded repair work
- status = `queued`
- source task linkage back to the failed recommendation-derived result task
- source artifact linkage where available
- human-readable repair reason or equivalent traceability
- success criteria small and bounded
- files in scope minimal or empty if unknown
- retry count initialized appropriately

Recommended title pattern:

- `Repair for <source_task_id>`

Recommended role:
- `coder`

The created task should be clearly distinguishable as repair work created from a failed post-execution recommendation-derived result.

Do NOT:
- auto-execute the new task
- create multiple tasks
- infer complex dependencies
- create follow-up review tasks in this phase

---

## Traceability Rules

The new repair task should preserve enough traceability to answer:

- which failed recommendation-derived result caused this repair task to exist
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
- note that the task was created from a failed recommendation-derived result

On failure to qualify, print clear messages for:
- task not found
- task not recommendation-derived
- task not post-execution
- task status not eligible for repair-task creation

Do NOT:
- emit raw JSON
- imply that the created repair task has already executed
- modify unrelated tasks

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce automatic failure handling
- Do NOT change queue or execution policy
- Do NOT bulk-create tasks
- Do NOT redesign statuses
- Do NOT alter unrelated tasks

This phase is explicit one-task repair creation only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Create Repair Task from Eligible `verification_failed` Result

Expected:
- one queued repair task is created
- task fields and traceability are persisted
- clear creation summary is printed

### Test B: Create Repair Task from Eligible `execution_failed` Result

Expected:
- one queued repair task is created
- task fields and traceability are persisted
- clear creation summary is printed

### Test C: Reject `needs_review` Result

Expected:
- clear message
- no repair task created

### Test D: Reject Ordinary Task

Expected:
- clear message
- no task created

### Test E: Reject Missing Task ID

Expected:
- clear not-found message
- no task created

### Test F: No Queue / Execution Behavior Change

Expected:
- ordinary `next` behavior remains unchanged
- no automatic execution of created repair task occurs

---

## Success Criteria

- a bounded explicit repair-task creation command exists
- only explicitly selected eligible failed recommendation-derived results can create repair tasks
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
   - how eligible failed source results are detected
   - how repair task creation works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
