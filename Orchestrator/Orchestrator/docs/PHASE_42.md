# PHASE_42.md

## Phase 42: Read-Only Recommendation Interpretation

---

## Goal

Add a read-only interpretation surface for persisted reviewer recommendations so the operator can understand recommendation state at a higher level than raw record listing, without creating action yet.

This phase should build on recommendation visibility by summarizing what recommendation records mean at the run level while remaining strictly advisory.

This is a forward feature phase.

It is NOT about:
- automatic routing
- automatic repair creation
- automatic follow-up creation
- task creation
- candidate-action execution
- draft proposal generation
- writeback
- UI/dashboard work
- broad schema redesign

---

## Problems This Phase Must Solve

### Problem 1: Recommendation Records Are Visible but Still Operationally Thin

The system can now list persisted reviewer recommendation records.

That is good.

But raw record listing still leaves the operator to mentally interpret recommendation state record-by-record. The system does not yet provide a read-only run-level view of what kinds of recommendations are present.

This phase should create that interpretation surface.

---

### Problem 2: Interpretation Must Happen Before Action Surfacing

This project’s staircase depends on keeping layers ordered:

- land state
- make it visible
- make it interpretable
- only later surface candidate actions
- only later allow explicit action creation

This phase should implement only the interpretation step.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/reviewer_output.py`
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to add a read-only recommendation interpretation surface.

---

## Required Feature

Add a read-only CLI command that interprets persisted reviewer recommendations for a run.

Recommended command shape:

- `python main.py recommendation-summary`
- optional:
  - `python main.py recommendation-summary --run <run_id>`

Default behavior if no `--run` is provided:
- use the active run if one exists
- if no active run exists, print a clear message and stop

The command must not mutate state.

---

## Recommendation Interpretation Surface

The CLI output should summarize recommendation state clearly and minimally.

At minimum, the surface should include:

- run ID
- total recommendation count
- count by recommendation type
- per-type grouped entries showing:
  - reviewer task ID
  - reason
  - timestamp

If source-task linkage is already directly and cheaply available from stored records or associated reviewer tasks, you may also include:
- source task ID

The command should remain descriptive only.
Do NOT add action hints such as:
- “create repair task now”
- “run follow-up”
- “accept this result”

That belongs to a later phase.

---

## Ordering / Grouping Rules

The command should show only persisted reviewer recommendation records.

If `--run <run_id>` is supplied:
- show only recommendations for that run

If no run is supplied and an active run exists:
- show only recommendations for the active run

Grouping should be deterministic and readable.

A minimal acceptable ordering is:
1. recommendation type in a stable order
2. records within each type ordered by timestamp, then reviewer task ID

If no matching recommendations exist:
- print a clear message and stop

---

## Non-Goals

This phase must NOT:

- rank recommendations
- generate candidate actions
- create tasks
- mutate recommendation records
- broaden recommendation schema
- attach confidence scores
- add policy language
- add a UI or dashboard

This is read-only interpretation only.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy
- Do NOT redesign recommendation persistence
- Do NOT redesign the recommendation schema
- Do NOT bundle in candidate-action surfacing or draft generation

This is recommendation interpretation only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Show Interpreted Summary For Active Run

Expected:
- when active run exists and persisted recommendations exist for it
- command shows grouped summary and per-type entries clearly

### Test B: Show Interpreted Summary For Explicit Run

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
- interpretation remains read-only
- no task creation
- no routing change
- existing recommendation visibility/persistence behavior remains intact

---

## Success Criteria

- persisted reviewer recommendations can be interpreted at a run level from the CLI
- output is grouped, clear, and minimal
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
   - how recommendation interpretation works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
