# PHASE_31.md

## Phase 31: Operator Response Surfacing for Post-Execution Recommendation Results

---

## Goal

Add a bounded, read-only operator-response surface for post-execution recommendation-derived task results.

This phase should allow the operator to:

- see which response paths are relevant for a post-execution recommendation-derived result
- distinguish between visible outcome categories without triggering automatic behavior
- treat post-execution recommendation-derived results as decision points rather than dead-end status records
- preserve the distinction between response surfacing and response execution

This phase is about operator-response visibility and bounded decision surfacing, not automatic handling.

It is NOT yet about:
- automatic repair task creation
- automatic re-review
- automatic re-execution
- queue changes
- routing based on post-execution result
- policy-engine behavior
- status-model redesign
- bulk action execution

---

## Problems This Phase Must Solve

### Problem 1: Post-Execution Recommendation-Derived Results Are Now Visible but Not Yet Action-Legible

The system can now:
- execute a ready recommendation-derived candidate
- surface the resulting post-execution task outcome as a distinct class

But the operator still does not get a bounded surface answering the next practical question:

- what kinds of response are relevant to this result?

This phase should make that response space visible without executing any response.

---

### Problem 2: Decision Surfaces Should Become Explicit Before They Become Behavioral

Before any future phase considers operator-triggered follow-up actions for post-execution recommendation-derived results, the system should first surface the relevant response options explicitly.

This phase must improve semantic/action visibility without changing execution or routing behavior.

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

Add a bounded read-only CLI surface for operator-response visibility on post-execution recommendation-derived task results.

Recommended command:

`python main.py recommendation-result-options`

Optional bounded variants:

- `python main.py recommendation-result-options --run <run_id>`
- `python main.py recommendation-result-options --task <task_id>`

At minimum, support either run-scoped or task-scoped behavior cleanly. If both are easy and behavior-preserving, that is acceptable.

If no selector is provided:
- use the active run
- if no active run exists, print a clear message and stop

The command should show only recommendation-derived tasks that already qualify as post-execution results under existing semantics.

For the selected scope, show:

- run ID or task ID context
- count of matching post-execution recommendation-derived tasks
- one readable block per matching task showing:
  - task ID
  - title
  - role
  - final task status
  - recommendation type
  - source task ID
  - source artifact ID
  - bounded operator-response options relevant to that result

---

## Response-Surfacing Rules

This phase must remain read-only.

It should not perform responses.
It should only surface the bounded operator-response categories that are relevant.

A minimal acceptable response-option mapping is:

- if final task status is `completed`:
  - surface a bounded note equivalent to:
    - no immediate follow-up required
    - review result if desired

- if final task status is `needs_review`:
  - surface bounded response options equivalent to:
    - inspect result
    - create follow-up review work later (not in this phase)

- if final task status is `verification_failed`:
  - surface bounded response options equivalent to:
    - inspect failure details
    - consider repair/follow-up later (not in this phase)

- if final task status is `execution_failed`:
  - surface bounded response options equivalent to:
    - inspect execution failure
    - consider retry/repair later (not in this phase)

Keep wording concrete and small.
Do NOT imply that these options are being executed now.

---

## Detection Rules

Use existing post-execution recommendation-derived task detection logic.

Do NOT:
- infer inclusion from vague naming alone
- mutate task records
- introduce new statuses
- trigger any follow-up actions
- create new tasks

This phase is surfacing only.

---

## Output Requirements

The command must include:

- scope context (run or task)
- matching post-execution recommendation-derived result count
- one readable block per matching task showing:
  - task ID
  - title
  - role
  - final task status
  - source task ID
  - source artifact ID
  - bounded operator-response options

Optional:
- recommendation type
- recommendation reason
- success criteria
- confirmation timestamp

Do NOT:
- emit raw JSON
- create a dashboard
- imply that surfaced options are being performed
- modify task or recommendation state

If no matching post-execution recommendation-derived results are found:
- print a clear message

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce automatic follow-up behavior
- Do NOT change queue or execution policy
- Do NOT redesign statuses
- Do NOT add new routing logic
- Do NOT alter existing tasks

This phase is operator-response surfacing only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Run With Post-Execution Recommendation-Derived Result

Expected:
- command shows correct count
- result block shows bounded operator-response options appropriate to the final status

### Test B: Run With Recommendation-Derived Tasks That Have Not Been Executed

Expected:
- those tasks are excluded
- clear no-results message if nothing qualifies

### Test C: Different Result Types

Expected:
- at least two different final statuses map to distinct bounded response-option sets

### Test D: No Active Run and No Selector

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

- post-execution recommendation-derived results now expose bounded operator-response options
- output is deterministic and read-only
- downstream decision visibility is improved without introducing automation
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how matching post-execution recommendation-derived results are detected
   - how response options are surfaced
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
