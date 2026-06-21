# PHASE_46.md

## Phase 46: Read-Only Recommendation Materialization Surfacing

---

## Goal

Add a read-only operator surface that shows which persisted reviewer recommendations have already been materialized into explicitly created tasks, without mutating recommendation state or queue state.

This phase should make post-creation recommendation state legible by surfacing whether a recommendation remains informational only or has already produced a created task.

This is a forward feature phase.

It is NOT about:
- automatic archival
- automatic acceptance workflows
- automatic deduplication
- automatic execution
- batch creation
- recommendation closure policies
- writeback
- UI/dashboard work
- broad schema redesign

---

## Problems This Phase Must Solve

### Problem 1: Recommendation-Backed Creation Now Exists, But Post-Creation State Is Not Clearly Surfaced

The system can now:
- persist reviewer recommendations
- show them
- summarize them
- surface candidate actions
- generate drafts
- explicitly create supported tasks

That is good.

But once a recommendation-backed task has been created, the operator still lacks a clean built-in surface showing which recommendation records have already materialized into real tasks.

This phase should create that read-only materialization surface.

---

### Problem 2: Explicit Creation Needs a Visible After-State Before Later Archival or Policy Layers

This project’s staircase depends on keeping state legible after each new executive step.

Now that explicit creation exists, the next missing capability is not more execution.
It is visibility into the consequences of that execution.

This phase should add only that after-state visibility.

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

Do NOT broaden changes beyond what is necessary to add a read-only recommendation materialization surface.

---

## Required Feature

Add a read-only CLI command that surfaces recommendation materialization state for a run.

Recommended command shape:

- `python main.py recommendation-outcomes`
- optional:
  - `python main.py recommendation-outcomes --run <run_id>`

Default behavior if no `--run` is provided:
- use the active run if one exists
- if no active run exists, print a clear message and stop

The command must not mutate state.

---

## Recommendation Materialization Surface

The CLI output should show, for each persisted recommendation record in the selected run:

- reviewer task ID
- recommendation type
- reason
- timestamp
- whether a created task has already been materialized from that recommendation-backed path
- created task ID when present

If source-task linkage is directly and cheaply available, you may also include:
- source task ID

The output must remain descriptive only.

Do NOT:
- archive the recommendation
- mark it consumed
- rank outcomes
- mutate queue state
- change recommendation records

---

## Materialization Detection Rules

This phase must detect whether a persisted recommendation has already produced a created task through the recommendation-backed creation path.

Use the smallest truthful read path available.

A minimal acceptable approach is:
- inspect persisted tasks in the same run
- detect tasks whose lineage/provenance clearly identifies them as having been created from the recommendation-backed path for the relevant reviewer recommendation

Do NOT invent weak heuristics if explicit linkage is unavailable.
Prefer narrow, truthful detection.

If no materialized task can be determined safely:
- surface the recommendation as not-yet-materialized or unknown in the smallest truthful way your implementation supports
- do not overclaim

Choose the smallest clear implementation.

---

## Output Requirements

At minimum, each entry should include:

- reviewer task ID
- recommendation type
- reason
- timestamp
- materialization status text
- created task ID when known

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
- batch-create tasks
- redesign recommendation schema
- attach confidence scores
- add policy ranking
- add UI/dashboard layers

This is read-only recommendation materialization surfacing only.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy
- Do NOT redesign recommendation persistence
- Do NOT redesign the recommendation schema
- Do NOT bundle in recommendation archival or acceptance workflows

This is post-creation visibility only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Show Materialized Recommendation Outcome For Active Run

Expected:
- when active run exists and persisted recommendations exist for it
- command shows whether each recommendation has or has not yet produced a created task
- created task ID is surfaced when known

### Test B: Show Materialized Recommendation Outcome For Explicit Run

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
- outcome surfacing remains read-only
- no task creation
- no routing change
- existing recommendation landing / visibility / interpretation / draft / creation behavior remains intact

---

## Success Criteria

- persisted reviewer recommendations can be surfaced alongside their materialization status from the CLI
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
   - how recommendation materialization surfacing works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
