# PHASE_45.md

## Phase 45: Explicit Task Creation From Recommendation Drafts

---

## Goal

Add an explicit, user-triggered creation surface that turns supported recommendation-backed draft proposals into real tasks, without introducing automatic routing or hidden task creation.

This phase should convert the recommendation staircase from fully advisory to explicitly actionable, while preserving operator control and boundedness.

This is a forward feature phase.

It is NOT about:
- automatic routing
- automatic repair creation
- automatic follow-up creation
- batch execution
- queue mutation beyond the one explicitly created task
- writeback
- UI/dashboard work
- broad schema redesign
- policy ranking

---

## Problems This Phase Must Solve

### Problem 1: Draft Proposals Exist but Cannot Yet Become Real Tasks Through the Recommendation Surface

The system can now:
- persist reviewer recommendations
- show them
- summarize them
- surface candidate actions
- generate bounded draft proposals

That is good.

But the operator still cannot create the corresponding task through the recommendation-backed path itself. Creation still lives elsewhere and is not yet exposed as the next step in this staircase.

This phase should create that explicit creation surface.

---

### Problem 2: Creation Must Be Explicit and Aligned With the Existing Draft Layer

If task creation is added carelessly, the system could develop:
- a second creation path that ignores draft semantics
- hidden policy decisions
- implicit routing from recommendation state

This phase should ensure creation is:
- explicit
- bounded
- aligned with the already surfaced draft forms
- limited to supported recommendation types only

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/run_manager.py`
- `orchestrator/reviewer_output.py` (only if a narrow loader/helper is needed)
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to add explicit task creation from recommendation-backed drafts.

---

## Required Feature

Add explicit CLI creation commands that create real tasks from supported recommendation-backed draft proposals.

Recommended command shape:

- `python main.py recommendation-create --reviewer-task <reviewer_task_id>`
- optional:
  - `python main.py recommendation-create --reviewer-task <reviewer_task_id> --run <run_id>`

You may refine argument naming slightly only if strongly justified, but keep it explicit and minimal.

The command must:

1. load the persisted recommendation record associated with the supplied reviewer task
2. validate that the recommendation type is one that supports task creation
3. create exactly one bounded task using the existing bounded creation logic where possible
4. persist that task normally
5. print a clear creation summary

This command must not:
- auto-run the created task
- create multiple tasks
- silently choose among multiple recommendations
- mutate unrelated state

---

## Supported Recommendation Types

Creation support in this phase must be limited to:

- `manual_followup`
- `repair_candidate`

Behavior:

- `manual_followup`
  - create a follow-up review task

- `repair_candidate`
  - create a repair task

- `accept_result`
  - do NOT create a task
  - print a clear message that no task creation is applicable

If an unknown recommendation type is encountered:
- do not create a task
- print a clear unsupported-type message
- stop cleanly

---

## Alignment With Existing Task Constructors

Where possible, this phase should reuse the existing bounded task creation helpers already present in the system, rather than duplicating task-construction logic.

This is strongly preferred because it preserves:
- lineage consistency
- status consistency
- traceability consistency
- response-task semantics already hardened earlier

If reuse is impossible, keep any new logic extremely narrow and explain why it was necessary.

---

## Source and Linkage Rules

Creation should remain truthful and bounded.

If source task / artifact linkage is directly available from:
- the recommendation record
- or the associated reviewer task

then carry forward the existing linkage semantics correctly.

Do NOT invent missing linkage.
Do NOT infer linkage from prose if explicit data is absent.

---

## Draft / Creation Consistency Requirement

The task created by this phase should be consistent with the already surfaced draft semantics.

That means:
- `manual_followup` recommendations should create reviewer follow-up tasks
- `repair_candidate` recommendations should create coder repair tasks
- `accept_result` should remain non-creative

This phase must not create a new interpretation layer that disagrees with the recommendation-draft surface.

---

## Non-Goals

This phase must NOT:

- auto-create tasks from all recommendations
- batch-create multiple tasks
- execute the created task automatically
- mutate recommendation records
- redesign recommendation persistence
- broaden recommendation taxonomy
- add draft ranking
- add UI/dashboard layers

This is explicit single-task creation only.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy broadly
- Do NOT redesign recommendation persistence
- Do NOT redesign the recommendation schema
- Do NOT bundle in recommendation archival or acceptance workflows

This is recommendation-backed explicit creation only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Create Follow-Up Task From `manual_followup`

Expected:
- command creates exactly one follow-up review task
- task is persisted normally
- lineage remains truthful
- no auto-execution occurs

### Test B: Create Repair Task From `repair_candidate`

Expected:
- command creates exactly one repair task
- task is persisted normally
- lineage remains truthful
- no auto-execution occurs

### Test C: `accept_result` Does Not Create a Task

Expected:
- command prints clear message
- no task is created
- no mutation beyond normal read path occurs

### Test D: Unsupported Recommendation Type

Expected:
- clear unsupported-type message
- no task creation
- no crash

### Test E: No Matching Recommendation Record

Expected:
- clear not-found message
- no task creation
- no crash

### Test F: No Hidden Behavior Change

Expected:
- creation remains explicit
- no auto-run
- no routing change outside the requested task creation
- existing recommendation landing / visibility / interpretation / draft behavior remains intact

---

## Success Criteria

- supported recommendation-backed drafts can be turned into real tasks explicitly from the CLI
- creation is single-task, explicit, and bounded
- lineage and task semantics remain truthful
- unsupported/non-creative recommendation types are handled clearly
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how explicit creation from recommendation-backed drafts works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
