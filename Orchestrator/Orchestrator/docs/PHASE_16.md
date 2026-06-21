# PHASE_16.md

## Phase 16: Recommendation Action Preparation + Candidate Surfacing

---

## Goal

Add a bounded, read-only action-preparation layer so the operator can see which recommendation-linked items appear to need attention next.

This phase should allow the system to:

- prepare a concise candidate action view from persisted recommendation records
- surface source-linked items grouped by recommendation type
- preserve the distinction between action preparation and action execution
- keep all behavior deterministic, inspectable, and read-only

This phase is about preparing operator attention, not performing workflow mutation.

It is NOT yet about:
- automatic repair task creation
- recommendation-driven routing
- retry loops
- writeback/application logic
- task mutation
- planner-generated follow-up work
- automatic prioritization or ranking

---

## Problems This Phase Must Solve

### Problem 1: Recommendation State Can Be Interpreted but Not Yet Turned Into a Concrete Attention Set

The system can now:
- persist recommendation records
- test reviewer recommendation behavior
- show recommendations directly
- surface recommendation awareness in status
- summarize recommendation meaning for the operator

But the operator still has to manually translate those summaries into:
- which specific items need attention
- which source tasks and artifacts those recommendations refer to

This phase should close that gap.

---

### Problem 2: The System Needs a Manual Action Bridge Before Any Executive Behavior

A later phase may consider bounded follow-up behavior based on recommendation records.

But before that, the system should first provide a structured, read-only candidate action view for the operator.

This phase must remain non-executing and non-mutating.

---

## Files to Create

Create only the minimum new file(s) needed.

Preferred:
- no new files if existing recommendation helper(s) can be extended minimally

Optional:
- `orchestrator/recommendation_store.py` may be extended with small read-only action-preparation helpers

Do NOT create a routing or policy engine.

---

## Files to Modify

- `main.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

If strictly needed:
- `orchestrator/recommendation_store.py`

Do NOT modify task execution semantics.
Do NOT modify reviewer recommendation semantics.
Do NOT modify recommendation record structure.

---

## Core Behavior

Add a bounded read-only CLI surface for recommendation-linked action preparation.

Recommended command:

`python main.py recommendation-actions`

Optional bounded variant:

`python main.py recommendation-actions --run <run_id>`

If no run filter is provided:
- use the active run
- if no active run exists, print a clear message and stop

The command should show, at minimum:

- target run ID
- total recommendation record count
- grouped candidate sections for:
  - `repair_candidate`
  - `manual_followup`
- for each candidate item:
  - `source_task_id`
  - `source_artifact_id`
  - `recommendation_type`
  - `reason`

Optional:
- concise summary of `accept` records, but do not let accepted items dominate the output

If no actionable recommendation records exist:
- print a clear message

Keep output:
- explicit
- deterministic
- read-only
- human-readable

---

## Action-Preparation Rules

The candidate action view must be based only on persisted recommendation records.

Do NOT:
- create tasks
- mutate tasks
- mutate runs
- apply recommendations
- inspect source task bodies beyond record-linked IDs
- infer hidden priorities
- rank items using fuzzy heuristics
- deduplicate aggressively unless exact duplicates are trivial and obvious

A minimal acceptable strategy is:

1. load recommendation records for the target run
2. group them by `recommendation_type`
3. print grouped candidate entries for actionable types
4. remain fully read-only

This is sufficient for this phase.

---

## Output Requirements

CLI output must include at least:

- run ID
- total recommendation record count
- actionable candidate sections for:
  - `repair_candidate`
  - `manual_followup`

Each candidate entry must show:
- source task ID
- source artifact ID
- reason

You may also show:
- reviewer task ID
- timestamp

Only if already stored and easy to surface without complexity.

Do NOT:
- emit raw JSON
- create a large report surface
- imply automatic action will occur
- print full recommendation-record internals unnecessarily

---

## Reuse Guidance

If existing recommendation-loading helpers from Phases 13–15 can be reused, prefer that.

Do NOT duplicate recommendation file-reading logic if reuse keeps the implementation smaller.

Do NOT broaden helpers into a policy engine.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce recommendation execution
- Do NOT create repair tasks
- Do NOT alter recommendation records
- Do NOT redesign persistence
- Do NOT broaden CLI into a large action-management interface
- Do NOT introduce hidden routing behavior
- Do NOT imply that candidate actions automatically change workflow state

This phase is preparation only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Run With Repair Candidates

Expected:
- repair candidate section appears
- source task and artifact IDs are shown
- reasons are shown clearly

---

### Test B: Run With Manual Follow-Up Candidates

Expected:
- manual follow-up section appears
- source task and artifact IDs are shown
- reasons are shown clearly

---

### Test C: Run With Mixed Recommendation Types

Expected:
- actionable sections are grouped correctly
- non-actionable accept records do not dominate the output

---

### Test D: Run With No Actionable Recommendation Records

Expected:
- clear no-actionable-items message
- no crash

---

### Test E: No Active Run and No --run Argument

Expected:
- clear message
- stop without crash

---

### Test F: Read-Only Guarantee

Running the command must not:
- modify state
- modify runs
- modify tasks
- create artifacts
- create recommendation records

---

## Success Criteria

- a bounded recommendation-actions CLI surface exists
- output is deterministic and read-only
- actionable items are grouped clearly
- source-linked IDs and reasons are visible
- no routing or execution behavior is introduced
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how candidate action preparation works
   - whether helper reuse was used
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
