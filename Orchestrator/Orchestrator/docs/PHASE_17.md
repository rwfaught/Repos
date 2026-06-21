# PHASE_17.md

## Phase 17: Recommendation-Derived Draft Task Proposals

---

## Goal

Add a bounded, read-only proposal-preparation layer so the operator can see draft follow-up task cards derived from recommendation-linked action candidates.

This phase should allow the system to:

- prepare deterministic draft task proposals from persisted recommendation records
- surface bounded follow-up task-card shapes grouped by recommendation type
- preserve the distinction between draft proposals and actual task creation
- keep all behavior inspectable, deterministic, and read-only

This phase is about preparing draft next-step packets, not modifying workflow state.

It is NOT yet about:
- automatic task creation
- recommendation-driven routing
- retry loops
- writeback/application logic
- task mutation
- planner-generated autonomous follow-up work
- automatic prioritization or ranking

---

## Problems This Phase Must Solve

### Problem 1: Candidate Action Items Exist but Are Not Yet Translated Into Draft Follow-Up Task Shapes

The system can now:
- persist recommendation records
- test reviewer recommendation behavior
- surface recommendation details
- reflect recommendation awareness in status
- summarize recommendation meaning
- show actionable recommendation-linked items

But the operator still has to manually translate those items into draft follow-up task cards.

This phase should close that gap.

---

### Problem 2: The System Needs Proposal Preparation Before It Can Safely Support Task Creation

A later phase may consider explicit operator-triggered task creation from recommendation state.

But before that, the system should first prepare bounded draft follow-up task proposals in a fully read-only way.

This phase must remain non-executing and non-mutating.

---

## Files to Create

Create only the minimum new file(s) needed.

Preferred:
- no new files if existing recommendation helper(s) can be extended minimally

Optional:
- `orchestrator/recommendation_store.py` may be extended with small read-only proposal helpers

Do NOT create a task-creation or routing engine.

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
Do NOT write proposals into `data/tasks/`.

---

## Core Behavior

Add a bounded read-only CLI surface for recommendation-derived draft task proposals.

Recommended command:

`python main.py recommendation-proposals`

Optional bounded variant:

`python main.py recommendation-proposals --run <run_id>`

If no run filter is provided:
- use the active run
- if no active run exists, print a clear message and stop

The command should show, at minimum:

- target run ID
- total recommendation record count
- grouped draft proposal sections for:
  - `repair_candidate`
  - `manual_followup`

For each draft proposal, show at least:

- proposed title
- proposed role
- source task ID
- source artifact ID
- originating recommendation type
- reason

Optional:
- simple proposed `expected_output`
- concise operator note that these are draft proposals only

Keep output:
- explicit
- deterministic
- read-only
- human-readable

---

## Proposal Rules

Draft proposal generation must be based only on persisted recommendation records.

Do NOT:
- create real tasks
- mutate tasks
- mutate runs
- apply recommendations
- inspect source task bodies beyond record-linked IDs and recommendation reasons
- infer hidden priorities
- rank proposals with fuzzy heuristics
- invent complex dependencies

A minimal acceptable strategy is:

1. load recommendation records for the target run
2. select actionable recommendation types:
   - `repair_candidate`
   - `manual_followup`
3. generate one bounded draft proposal per actionable recommendation record
4. display the proposals grouped by recommendation type
5. remain fully read-only

This is sufficient for this phase.

---

## Draft Proposal Shape

Each draft proposal should be deterministic and small.

Recommended proposed fields:

- `title`
- `role`
- `source_task_id`
- `source_artifact_id`
- `recommendation_type`
- `reason`

Recommended defaults:

- For `repair_candidate`:
  - proposed role: `coder`
  - title pattern:
    - `Repair follow-up for <source_task_id>`

- For `manual_followup`:
  - proposed role: `reviewer`
  - title pattern:
    - `Manual follow-up for <source_task_id>`

If `expected_output` is shown, keep it minimal and human-readable.

Do NOT:
- persist these as real Task objects
- generate real task IDs
- assign dependencies
- imply automatic execution

---

## Output Requirements

CLI output must include at least:

- run ID
- total recommendation record count
- grouped proposal sections for actionable recommendation types

Each proposal entry must show:
- proposed title
- proposed role
- source task ID
- source artifact ID
- recommendation type
- reason

Do NOT:
- emit raw JSON
- create a large report surface
- imply that proposals are already real tasks
- let non-actionable accept records dominate the output

If no actionable recommendation records exist:
- print a clear message

---

## Reuse Guidance

If existing recommendation-loading helpers from earlier phases can be reused, prefer that.

Do NOT duplicate recommendation file-reading logic if reuse keeps the implementation smaller.

Do NOT broaden helpers into a task-creation engine.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce recommendation execution
- Do NOT create tasks
- Do NOT alter recommendation records
- Do NOT redesign persistence
- Do NOT broaden CLI into a task-management interface
- Do NOT introduce hidden routing behavior
- Do NOT imply that draft proposals automatically change workflow state

This phase is proposal preparation only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Run With Repair Candidates

Expected:
- repair-candidate proposal section appears
- each proposal shows title, role, source task ID, source artifact ID, recommendation type, and reason

---

### Test B: Run With Manual Follow-Up Candidates

Expected:
- manual-followup proposal section appears
- each proposal shows required fields clearly

---

### Test C: Run With Mixed Recommendation Types

Expected:
- grouped proposal sections are correct
- actionable proposal groups appear clearly
- accept records do not dominate output

---

### Test D: Run With No Actionable Recommendation Records

Expected:
- clear no-proposals message
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
- create draft tasks on disk

---

## Success Criteria

- a bounded recommendation-proposals CLI surface exists
- output is deterministic and read-only
- draft proposals are grouped clearly
- source-linked IDs and reasons are visible
- proposals are clearly distinguishable from real tasks
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
   - how draft proposal generation works
   - whether helper reuse was used
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
