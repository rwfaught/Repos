# PHASE_30.md

## Phase 30: Post-Execution Semantics for Recommendation-Derived Tasks

---

## Goal

Add a bounded read-only surface that makes post-execution outcomes for explicitly executed recommendation-derived tasks visible and semantically distinct.

This phase should allow the operator to:

- see which recommendation-derived tasks have been explicitly executed
- inspect their resulting execution status and verification/result state
- distinguish those outcomes from ordinary task execution outcomes
- preserve the distinction between semantic surfacing and automatic consequence

This phase is about post-execution visibility and semantics, not automated follow-up behavior.

It is NOT yet about:
- automatic repair task creation
- automatic re-review
- automatic re-execution
- queue changes
- routing based on post-execution result
- status-model redesign
- policy-engine behavior

---

## Problems This Phase Must Solve

### Problem 1: Recommendation-Derived Tasks Can Now Be Explicitly Executed, But Their Downstream Meaning Is Still Generic

The system can now:
- create recommendation-derived tasks
- confirm them
- surface them as ready execution candidates
- explicitly execute one by task ID

But once executed, those tasks still mostly collapse back into generic task-result visibility.

This phase should make their post-execution outcomes visible as a distinct class of recommendation-derived follow-up result.

---

### Problem 2: Downstream Meaning Should Become Visible Before It Becomes Behavioral

Before any future phase considers automatic handling of failed, inadequate, or completed recommendation-derived follow-up work, the system must first surface those outcomes clearly.

This phase must improve semantic visibility without changing execution or routing behavior.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/run_manager.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

If strictly needed:
- a very small helper addition under `orchestrator/`

Do NOT redesign execution flow.
Do NOT redesign status handling broadly.
Do NOT introduce automation.

---

## Core Behavior

Add a bounded read-only CLI surface for post-execution recommendation-derived task outcomes.

Recommended command:

`python main.py recommendation-execution-results`

Optional bounded variant:

`python main.py recommendation-execution-results --run <run_id>`

If no run filter is provided:
- use the active run
- if no active run exists, print a clear message and stop

The command should show only recommendation-derived tasks that:
- were recommendation-created
- have already been executed (i.e. are no longer simply queued candidates)

For the target run, show:

- run ID
- count of executed recommendation-derived tasks

For each matching task, show at minimum:

- task ID
- title
- role
- final task status
- recommendation type
- source task ID
- source artifact ID

Optional if already present and easy to show:
- verification state
- confirmation timestamp
- recommendation reason
- success criteria

Output must clearly indicate:
- these are post-execution results for recommendation-derived follow-up work
- this command does NOT execute or reroute anything
- this command does NOT change queue behavior

---

## Detection Rules

A task counts as a recommendation-derived execution result only if:

- it clearly appears recommendation-created using existing normalized provenance logic
- it has moved beyond the pre-execution candidate state
- it has a post-execution status/result that reflects actual execution flow

Use existing persisted task data and explicit provenance logic.

Do NOT:
- infer inclusion from vague naming alone
- mutate task records to improve surfacing
- introduce new status meanings in this phase

---

## Output Requirements

The command must include:

- run ID
- executed recommendation-derived task count
- one readable block per matching task showing:
  - task ID
  - title
  - role
  - final task status
  - source task ID
  - source artifact ID

Optional:
- recommendation type
- recommendation reason
- verification/result information

Do NOT:
- emit raw JSON
- create a full dashboard
- imply that failed/inadequate results trigger automatic follow-up
- modify task or recommendation state

If no executed recommendation-derived tasks are found:
- print a clear message

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce automatic follow-up behavior
- Do NOT change queue or execution policy
- Do NOT redesign statuses
- Do NOT add new routing logic
- Do NOT alter existing tasks

This phase is post-execution semantic surfacing only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Run With Executed Recommendation-Derived Task

Expected:
- command shows correct count
- task block shows post-execution result fields clearly

### Test B: Run With Recommendation-Derived Tasks That Have Not Been Executed

Expected:
- those tasks are excluded
- clear no-results message if nothing qualifies

### Test C: Run With No Recommendation-Derived Tasks

Expected:
- clear no-results message
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

- executed recommendation-derived tasks are surfaced as a distinct post-execution result class
- output is deterministic and read-only
- downstream semantic visibility is improved without introducing automation
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how executed recommendation-derived results are detected
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
