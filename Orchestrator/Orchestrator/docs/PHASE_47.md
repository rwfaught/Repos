# PHASE_47.md

## Phase 47: Read-Only Recommendation Resolution Surfacing

---

## Goal

Add a read-only operator surface that shows the practical resolution state of persisted reviewer recommendations, without mutating recommendation records or queue state.

This phase should help the operator understand which recommendations remain effectively open, which have already materialized into created tasks, and which are informational-only, while remaining strictly descriptive.

This is a forward feature phase.

It is NOT about:
- automatic archival
- automatic acceptance workflows
- automatic deduplication
- automatic execution
- explicit recommendation consumption
- queue mutation
- writeback
- UI/dashboard work
- broad schema redesign

---

## Problems This Phase Must Solve

### Problem 1: Recommendation Materialization Is Visible, But Practical Resolution Is Still Operationally Thin

The system can now show whether a persisted recommendation has materialized into a created task.

That is good.

But the operator still lacks a compact read-only surface that answers the practical question:
- is this recommendation still open,
- already materialized into a task,
- or informational-only with no task path required?

This phase should create that resolution surface.

---

### Problem 2: Resolution Visibility Should Exist Before Any Later Consumption / Archival Action

This project’s staircase depends on visibility before mutation.

Now that explicit creation and materialization surfacing exist, the next missing capability is not archival.
It is a clear read-only surface that summarizes recommendation resolution state first.

This phase should add only that visibility.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/reviewer_output.py`
- `orchestrator/run_manager.py` (only if a narrow read helper is needed)
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to add a read-only recommendation resolution surface.

---

## Required Feature

Add a read-only CLI command that surfaces recommendation resolution state for a run.

Recommended command shape:

- `python main.py recommendation-resolution`
- optional:
  - `python main.py recommendation-resolution --run <run_id>`

Default behavior if no `--run` is provided:
- use the active run if one exists
- if no active run exists, print a clear message and stop

The command must not mutate state.

---

## Recommendation Resolution Surface

The CLI output should show, for each persisted recommendation record in the selected run:

- reviewer task ID
- recommendation type
- reason
- timestamp
- resolution status text

If directly and cheaply available, you may also include:
- source task ID
- created task ID for materialized recommendations

This surface must remain descriptive only.

Do NOT:
- mark a recommendation resolved
- archive a recommendation
- mutate queue state
- change recommendation records

---

## Resolution Rules

Use the smallest truthful rules available.

A minimal acceptable resolution model is:

- `accept_result`
  - surface as informational / no-creation-path / resolved-in-place

- `manual_followup`
  - if a matching created task is determinable through the existing recommendation-backed materialization logic:
      surface as materialized
    else:
      surface as open

- `repair_candidate`
  - if a matching created task is determinable through the existing recommendation-backed materialization logic:
      surface as materialized
    else:
      surface as open

- unsupported / unknown recommendation type
  - surface as unsupported or unknown in the smallest truthful way

- missing required linkage for determination
  - surface as unknown rather than inferred

Do NOT overclaim closure.
Do NOT infer archival or acceptance that the system has not actually recorded.

---

## Output Requirements

At minimum, each entry should include:

- reviewer task ID
- recommendation type
- reason
- timestamp
- resolution status text

If known and directly available, also include:
- source task ID
- created task ID

Ordering should be deterministic and readable.

A minimal acceptable ordering is:
1. stable recommendation-type order
2. entries within each type ordered by `(timestamp, reviewer_task_id)`

If no matching recommendation records exist:
- print a clear message and stop

---

## Non-Goals

This phase must NOT:

- archive recommendations
- mark recommendations consumed
- auto-create tasks
- auto-run tasks
- redesign recommendation schema
- attach confidence scores
- add policy ranking
- add UI/dashboard layers

This is read-only recommendation resolution surfacing only.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy
- Do NOT redesign recommendation persistence
- Do NOT redesign the recommendation schema
- Do NOT bundle in explicit archival / consumption workflows

This is recommendation-resolution visibility only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Show Resolution Surface For Active Run

Expected:
- when active run exists and persisted recommendations exist for it
- command shows practical resolution state for each recommendation clearly

### Test B: Show Resolution Surface For Explicit Run

Expected:
- `--run <run_id>` scopes output correctly to that run

### Test C: No Matching Recommendations

Expected:
- clear no-results message
- no state mutation

### Test D: No Active Run

Expected:
- clear message
- no crash
- no state mutation

### Test E: No Hidden Behavior Change

Expected:
- resolution surfacing remains read-only
- no task creation
- no routing change
- existing recommendation landing / visibility / interpretation / draft / creation / materialization behavior remains intact

---

## Success Criteria

- persisted reviewer recommendations can be surfaced alongside a practical read-only resolution state from the CLI
- output is clear, minimal, and deterministic
- run-scoped filtering works
- command is read-only
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how recommendation resolution surfacing works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
