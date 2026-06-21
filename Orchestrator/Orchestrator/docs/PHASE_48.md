# PHASE_48.md

## Phase 48: Explicit Recommendation Archival / Consumption

---

## Goal

Add an explicit, user-triggered command that archives or marks a persisted reviewer recommendation as consumed, without introducing automatic archival, automatic acceptance, or broad recommendation-state policy.

This phase should provide the first bounded mutation layer for recommendation records now that the system already supports:
- recommendation landing
- visibility
- interpretation
- candidate-action surfacing
- draft proposal surfacing
- explicit creation
- materialization surfacing
- practical resolution surfacing

This is a forward feature phase.

It is NOT about:
- automatic archival
- automatic acceptance workflows
- automatic deduplication
- automatic execution
- batch archival
- queue mutation
- writeback
- UI/dashboard work
- broad schema redesign

---

## Problems This Phase Must Solve

### Problem 1: Recommendation State Is Now Richly Visible but Cannot Yet Be Explicitly Retired

The system can now show recommendation records, their candidate actions, drafts, materialization state, and practical resolution state.

That is good.

But the operator still cannot explicitly tell the system:
- this recommendation has been handled
- this recommendation should no longer remain active operational state

This phase should add that explicit archival / consumption step.

---

### Problem 2: Mutation Must Happen Only After Visibility Is Sufficient

This project’s staircase depends on visibility before mutation.

Now that the system has adequate visibility around recommendation state, the next missing capability is a bounded, explicit operator-triggered mutation layer.

This phase should add only that mutation.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/reviewer_output.py`
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to add explicit recommendation archival / consumption.

---

## Required Feature

Add an explicit CLI command that archives or marks a recommendation record as consumed.

Recommended command shape:

- `python main.py recommendation-archive --reviewer-task <reviewer_task_id>`
- optional:
  - `python main.py recommendation-archive --reviewer-task <reviewer_task_id> --run <run_id>`

You may refine argument naming slightly only if strongly justified, but keep it explicit and minimal.

The command must:

1. load the persisted recommendation record associated with the supplied reviewer task
2. validate that the recommendation record exists in the selected run context
3. update only the minimum recommendation state required to mark it archived / consumed
4. persist the updated recommendation record
5. print a clear archival summary

This command must not:
- archive multiple recommendations at once
- mutate unrelated recommendation records
- create or execute tasks
- infer acceptance policy beyond the explicit archival mark

---

## Archival / Consumption Semantics

Choose the smallest clear representation for archival state.

A minimal acceptable approach is:
- add a small explicit archival / consumed marker to the persisted recommendation record
- optionally include an archived / consumed timestamp

Keep this representation minimal and inspectable.

Do NOT:
- redesign the recommendation schema broadly
- introduce status taxonomies beyond what is needed
- add confidence or policy fields
- add batch/archive history systems

---

## Scope of This Phase

This phase archives recommendation records only.

It does NOT:
- decide whether a recommendation was “correct”
- decide whether an `accept_result` is semantically approved
- archive automatically after creation or materialization
- enforce closure policy elsewhere in the system

Archival here is an explicit operator action only.

---

## Interaction With Existing Read-Only Surfaces

Existing read-only recommendation surfaces should remain intact.

This phase may, if truly necessary and minimally, adjust them so archived recommendations are clearly surfaced as archived or excluded by default.

However, keep that change minimal.

A preferred minimal behavior is:

- existing visibility commands continue to work
- archived recommendations are either:
  - clearly labeled as archived
  - or excluded by default only if the phase can do so without broad read-surface churn

Choose the smallest consistent implementation and explain it.

Do NOT redesign all recommendation surfaces in this phase.

---

## Source of Truth

Recommendation archival must be tied to the persisted recommendation record keyed by reviewer task ID, not reconstructed from task state or prose.

Do NOT invent a parallel archival store unless clearly necessary.
Prefer mutating the existing recommendation record in the smallest inspectable way possible.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy
- Do NOT redesign recommendation persistence broadly
- Do NOT redesign the recommendation schema broadly
- Do NOT bundle in acceptance workflows
- Do NOT bundle in batch archival or deletion semantics

This is explicit recommendation archival only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Archive Existing Recommendation

Expected:
- command finds the correct persisted recommendation record
- command marks it archived / consumed in the minimal explicit way
- update is persisted
- no unrelated records are changed

### Test B: Missing Recommendation Record

Expected:
- clear not-found message
- no crash
- no mutation

### Test C: Wrong Run Scope

Expected:
- if `--run` is provided and the recommendation record does not belong to that run
- command stops cleanly with a clear message
- no mutation occurs

### Test D: No Hidden Behavior Change

Expected:
- no task creation
- no execution
- no queue mutation
- existing recommendation landing / visibility / interpretation / draft / creation / materialization / resolution behavior remains intact except for the bounded archival state change

### Test E: Archived Record Is Inspectable

Expected:
- persisted archival marker can be read back clearly
- the result remains inspectable and minimal

---

## Success Criteria

- a single persisted recommendation can be explicitly archived / consumed from the CLI
- the mutation is minimal, inspectable, and bounded
- no unrelated recommendation records or task state are mutated
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how recommendation archival / consumption works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
