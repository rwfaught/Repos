# PHASE_50.md

## Phase 50: Explicit Acceptance Handling For `accept_result`

---

## Goal

Add an explicit, user-triggered command that marks an `accept_result` recommendation as affirmatively accepted, without introducing automatic acceptance workflows, broad recommendation policy, or hidden queue mutation.

This phase should distinguish:
- archival / retirement of a recommendation record
from
- affirmative operator acceptance of an `accept_result` recommendation

This is a forward feature phase.

It is NOT about:
- automatic acceptance
- automatic archival
- broad recommendation-state policy
- queue mutation
- task creation
- execution
- batch acceptance
- writeback
- UI/dashboard work
- broad schema redesign

---

## Problems This Phase Must Solve

### Problem 1: `accept_result` Currently Lacks Its Own Explicit Operator Outcome

The system can now:
- persist reviewer recommendations
- surface them across multiple read-only views
- create supported tasks for actionable recommendation types
- archive recommendation records explicitly

That is good.

But `accept_result` still does not have its own explicit operator action. Right now, archival risks carrying too much semantic weight:
- handled
- dismissed
- informational only
- affirmatively accepted

Those are not the same thing.

This phase should add the missing explicit acceptance action for `accept_result`.

---

### Problem 2: Acceptance Must Be Kept Narrow and Explicit

This project’s discipline depends on mutation being:
- visible first
- explicit second
- narrow always

Acceptance should therefore be:
- user-triggered
- recommendation-record based
- limited to `accept_result`
- minimally persisted
- clearly inspectable

This phase should add only that bounded acceptance layer.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/reviewer_output.py`
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to add explicit acceptance handling for `accept_result`.

---

## Required Feature

Add an explicit CLI command that marks an `accept_result` recommendation as accepted.

Recommended command shape:

- `python main.py recommendation-accept --reviewer-task <reviewer_task_id>`
- optional:
  - `python main.py recommendation-accept --reviewer-task <reviewer_task_id> --run <run_id>`

You may refine argument naming slightly only if strongly justified, but keep it explicit and minimal.

The command must:

1. resolve the selected run context (`--run` or active run)
2. load the persisted recommendation record associated with the supplied reviewer task
3. validate that exactly one matching recommendation record exists in the selected run
4. validate that the recommendation type is exactly `accept_result`
5. persist a minimal explicit acceptance marker on that recommendation record
6. print a clear acceptance summary

This command must not:
- accept multiple recommendations at once
- mutate unrelated recommendation records
- archive automatically
- create or execute tasks
- infer broader closure policy

---

## Acceptance Semantics

Choose the smallest clear representation for acceptance state.

A minimal acceptable approach is:
- add a small explicit acceptance marker to the persisted recommendation record
- optionally include an acceptance timestamp

Example minimal fields:
- `accepted: true`
- `accepted_at: <utc iso timestamp>`

Keep this representation minimal and inspectable.

Do NOT:
- redesign the recommendation schema broadly
- introduce recommendation status taxonomies
- add confidence or policy fields
- add acceptance history systems

---

## Scope Of This Phase

This phase handles explicit acceptance for `accept_result` only.

It does NOT:
- accept `manual_followup`
- accept `repair_candidate`
- auto-archive accepted recommendations
- auto-close recommendations generally
- enforce downstream policy elsewhere in the system

Acceptance here is an explicit operator action only.

---

## Interaction With Existing Read Surfaces

Existing read-only recommendation surfaces should remain intact.

This phase may, if truly necessary and minimally, adjust them so accepted `accept_result` records are clearly surfaced as accepted.

However, keep that change minimal.

A preferred minimal behavior is:
- acceptance state is persisted and inspectable on the recommendation record
- existing read surfaces continue to work
- any acceptance-aware surfacing added in this phase should be minimal and directly relevant

Do NOT redesign all recommendation surfaces in this phase.

---

## Source Of Truth

Acceptance must be tied to the persisted recommendation record keyed by reviewer task ID, not reconstructed from task state, archival state, or prose.

Do NOT invent a parallel acceptance store unless clearly necessary.
Prefer mutating the existing recommendation record in the smallest inspectable way possible.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy
- Do NOT redesign recommendation persistence broadly
- Do NOT redesign the recommendation schema broadly
- Do NOT bundle in unarchive behavior
- Do NOT bundle in broad closure semantics

This is explicit `accept_result` acceptance only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Accept Existing `accept_result` Recommendation

Expected:
- command finds the correct persisted recommendation record
- command validates recommendation type is `accept_result`
- command marks it accepted in the minimal explicit way
- update is persisted
- no unrelated records are changed

### Test B: Wrong Recommendation Type

Expected:
- `manual_followup` or `repair_candidate` cannot be accepted through this command
- clear message
- no mutation

### Test C: Missing Recommendation Record

Expected:
- clear not-found message
- no crash
- no mutation

### Test D: Wrong Run Scope

Expected:
- if `--run` is provided and the recommendation record does not belong to that run
- command stops cleanly with a clear message
- no mutation occurs

### Test E: No Hidden Behavior Change

Expected:
- no task creation
- no execution
- no queue mutation
- existing recommendation landing / visibility / interpretation / draft / creation / materialization / resolution / archival behavior remains intact except for the bounded acceptance state change

### Test F: Accepted Record Is Inspectable

Expected:
- persisted acceptance marker can be read back clearly
- the result remains inspectable and minimal

---

## Success Criteria

- a single persisted `accept_result` recommendation can be explicitly accepted from the CLI
- the mutation is minimal, inspectable, and bounded
- unsupported recommendation types are rejected cleanly
- no unrelated recommendation records or task state are mutated
- no unrelated architectural drift is introduced

---

## End Of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how explicit `accept_result` acceptance works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
