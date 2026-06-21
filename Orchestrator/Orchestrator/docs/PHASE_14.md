# PHASE_14.md

## Phase 14: Recommendation-Aware Status Surfacing

---

## Goal

Make persisted reviewer recommendation state visible through the system’s ordinary status surface, not only through the dedicated recommendations command.

This phase should allow the system to:

- detect whether the active run has persisted reviewer recommendation records
- surface concise recommendation-state summaries through normal status reporting
- preserve the distinction between visibility and action
- keep recommendation state inspectable without turning it into routing behavior

This phase is about orchestrator awareness of reviewer recommendation state.

It is NOT yet about:
- automatic repair task creation
- recommendation-driven routing
- retry loops
- writeback/application logic
- planner-generated follow-up work
- automatic task mutation based on recommendations

---

## Problems This Phase Must Solve

### Problem 1: Recommendation State Exists but Is Not Yet Part of Normal Workflow Status

Phase 11 introduced recommendation persistence.
Phase 12 added regression coverage.
Phase 13 added explicit CLI visibility through `recommendations`.

But the ordinary status surface still does not reflect whether recommendation records exist for the active run.

This means recommendation state is visible only when specifically queried, not as part of the normal orchestrator-facing system summary.

---

### Problem 2: The Orchestrator Needs Awareness Before It Can Safely Support Interpretation

A later phase may introduce bounded interpretation or operator decision support around reviewer recommendations.

But before that, the system should first be able to say, in its standard status flow:

- whether recommendation records exist
- how many exist for the active run
- what recommendation types are present

This phase must improve awareness without introducing automatic action.

---

## Files to Create

Create only the minimum new file(s) needed.

Preferred:
- no new files if existing recommendation visibility helpers can be reused cleanly

Optional:
- `orchestrator/recommendation_store.py` may be extended minimally if needed

Do NOT create a new routing or policy layer.

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

The ordinary status surface must become recommendation-aware.

Recommended target:

`python main.py status`

In addition to existing status behavior, the command should now surface concise recommendation state for the active run.

If an active run exists, status output should include at least:

- active run ID
- whether reviewer recommendation records exist for that run
- count of recommendation records for that run

Optional but acceptable if easy and minimal:
- counts by `recommendation_type`

Example shape:

- Active run: `<run_id>`
- Recommendation records for active run: `2`
- Recommendation types present:
  - `manual_followup`: 1
  - `repair_candidate`: 1

If no active run exists:
- preserve current no-active-run behavior
- do not infer recommendation meaning globally

If an active run exists but no recommendation records exist for it:
- show a clear zero-record message

Keep status output:
- concise
- explicit
- read-only
- deterministic

---

## Recommendation Status Rules

Recommendation-aware status must:

1. Read persisted recommendation records safely
2. Filter them to the active run only
3. Surface summary information only
4. Remain read-only

Do NOT:
- print full recommendation details in the standard status command
- mutate tasks or runs
- create tasks
- apply recommendations
- infer next actions

Detailed recommendation inspection should remain the job of:

`python main.py recommendations`

This phase adds awareness to status, not duplication of the full recommendations view.

---

## Reuse Guidance

If Phase 13 introduced a reusable recommendation-loading helper, prefer reusing it.

Do NOT duplicate file-reading logic if existing helper reuse is simple and keeps the implementation smaller.

Do NOT broaden the helper into a policy engine.

---

## Output Rules

Status output must clearly distinguish:

- system/workspace state
- active run state
- recommendation state for the active run

Recommendation status should be brief and summary-oriented.

Preferred fields:
- recommendation count
- optional type counts

Do NOT emit raw JSON.
Do NOT list every recommendation record in the status output.
Do NOT add broad formatting complexity.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce recommendation execution
- Do NOT create repair tasks
- Do NOT alter existing status semantics beyond adding bounded recommendation awareness
- Do NOT redesign persistence
- Do NOT broaden CLI behavior beyond the status command
- Do NOT introduce hidden routing behavior
- Do NOT alter recommendation record contents

This phase is awareness only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Active Run with Recommendation Records

Given an active run that has one or more persisted recommendation records,
running:

`python main.py status`

Expected:
- status output includes recommendation summary for the active run
- recommendation count is correct

---

### Test B: Active Run with No Recommendation Records

Given an active run with no matching recommendation records,
running:

`python main.py status`

Expected:
- clear zero-record recommendation summary
- no crash

---

### Test C: No Active Run

Given no active run,
running:

`python main.py status`

Expected:
- preserve existing no-active-run behavior
- no recommendation summary incorrectly inferred

---

### Test D: Read-Only Guarantee

Running the status command must not:
- modify tasks
- modify runs
- modify state
- create artifacts
- create recommendation records

---

## Success Criteria

- ordinary status output becomes recommendation-aware for the active run
- recommendation summary is concise and correct
- detailed recommendation inspection remains separate
- status behavior remains read-only
- no routing or action behavior is introduced
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how recommendation awareness is surfaced in status
   - whether any helper reuse was used
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
