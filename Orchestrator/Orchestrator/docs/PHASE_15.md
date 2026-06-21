# PHASE_15.md

## Phase 15: Recommendation Interpretation + Operator Decision Support

---

## Goal

Add a bounded, read-only interpretation layer for persisted reviewer recommendation state so the operator can see a concise summary of what the current recommendation set implies.

This phase should allow the system to:

- summarize recommendation types for the active run
- surface a concise operator-facing interpretation of recommendation state
- preserve the distinction between interpretation and execution
- keep recommendation meaning advisory rather than automatic

This phase is about helping the operator understand recommendation state.

It is NOT yet about:
- automatic repair task creation
- recommendation-driven routing
- retry loops
- writeback/application logic
- automatic task mutation
- planner-generated follow-up work

---

## Problems This Phase Must Solve

### Problem 1: Recommendation State Is Visible but Not Yet Interpreted

The system can now:
- persist recommendation records
- test recommendation behavior
- show recommendation details on demand
- surface recommendation-count awareness in status

But the operator still has to manually interpret what those records imply.

This phase should add a small advisory layer so recommendation state becomes more legible.

---

### Problem 2: The System Needs Advisory Meaning Before It Gains Any Executive Behavior

A future phase may introduce bounded recommendation-driven follow-up behavior.

But before that, the system should first be able to say, in a read-only way:

- what recommendation types are present
- whether the active run appears to need manual attention
- whether repair candidates are present
- whether the recommendation set is mixed or clean

This phase must remain advisory only.

---

## Files to Create

Create only the minimum new file(s) needed.

Recommended:
- no new files if existing recommendation helper(s) can be extended minimally

Optional:
- `orchestrator/recommendation_store.py` may be extended with small read-only summary helpers

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

Add a bounded read-only CLI surface for recommendation interpretation.

Recommended command:

`python main.py recommendation-summary`

Optional bounded variant:

`python main.py recommendation-summary --run <run_id>`

If no run filter is provided:
- use the active run
- if no active run exists, print a clear message and stop

The command should summarize, at minimum:

- target run ID
- total recommendation record count
- counts by `recommendation_type`
- concise advisory interpretation

Example interpretation patterns:

- if only `accept` records are present:
  - `Recommendation summary: no outstanding manual or repair signals detected.`

- if one or more `manual_followup` records are present:
  - `Recommendation summary: manual follow-up is recommended for this run.`

- if one or more `repair_candidate` records are present:
  - `Recommendation summary: repair candidates are present for this run.`

- if multiple recommendation types are present:
  - `Recommendation summary: mixed recommendation state; operator review advised.`

Keep interpretation:
- explicit
- deterministic
- advisory
- read-only

---

## Interpretation Rules

Interpretation must be based only on persisted recommendation records.

Do NOT:
- inspect task bodies beyond what is already in the recommendation records
- infer hidden priorities
- generate new tasks
- apply recommendations
- mutate workflow state
- use model-based reasoning

Keep the interpretation logic simple and deterministic.

A minimal acceptable strategy is:

1. count recommendation types for the run
2. generate one concise summary line from those counts

This is sufficient for this phase.

---

## Output Requirements

CLI output must include at least:

- run ID
- total recommendation record count
- count of `accept`
- count of `manual_followup`
- count of `repair_candidate`
- one concise interpretation line

Optional:
- brief note directing operator to use `python main.py recommendations` for detailed record inspection

Do NOT:
- print full recommendation records
- emit raw JSON
- create a large report surface
- imply automatic action will occur

---

## Reuse Guidance

If existing recommendation-loading helpers from Phase 13 or Phase 14 can be reused, prefer that.

Do NOT duplicate file-reading logic if reuse keeps the implementation smaller.

Do NOT broaden helpers into a policy engine.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce recommendation execution
- Do NOT create repair tasks
- Do NOT alter recommendation records
- Do NOT redesign persistence
- Do NOT broaden CLI into a large decision interface
- Do NOT introduce hidden routing behavior
- Do NOT imply that summaries automatically change workflow state

This phase is interpretation only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Run With Only Accept Records

Expected:
- summary shows only accept count
- interpretation indicates no outstanding manual or repair signals

---

### Test B: Run With Manual Follow-Up Records

Expected:
- summary shows manual_followup count
- interpretation indicates manual follow-up is recommended

---

### Test C: Run With Repair Candidate Records

Expected:
- summary shows repair_candidate count
- interpretation indicates repair candidates are present

---

### Test D: Mixed Recommendation Types

Expected:
- summary shows correct per-type counts
- interpretation indicates mixed state and advises operator review

---

### Test E: No Recommendation Records for Target Run

Expected:
- summary shows zero records or clear no-records message
- no crash

---

### Test F: Read-Only Guarantee

Running the summary command must not:
- modify state
- modify runs
- modify tasks
- create artifacts
- create recommendation records

---

## Success Criteria

- a bounded recommendation-summary CLI surface exists
- interpretation is deterministic and read-only
- per-type counts are correct
- advisory summary is concise and useful
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
   - how recommendation interpretation works
   - whether helper reuse was used
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
