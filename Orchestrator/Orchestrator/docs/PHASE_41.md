# PHASE_41.md

## Phase 41: Read-Only Recommendation Visibility

---

## Goal

Add a read-only operator surface for persisted reviewer recommendations so recommendation state can be inspected clearly from the CLI.

This phase should make recommendation records visible and usable as information without making them actionable yet.

This is a forward feature phase.

It is NOT about:
- automatic routing
- automatic repair creation
- automatic follow-up creation
- recommendation interpretation logic
- candidate-action generation
- draft proposal generation
- writeback
- UI/dashboard work
- broad schema redesign

---

## Problems This Phase Must Solve

### Problem 1: Recommendation State Exists but Lacks an Explicit Operator Surface

The system can now persist reviewer recommendation records.

That is good.

But recommendation state still mostly lives on disk as latent JSON. The operator does not yet have a clean built-in surface for inspecting those records through the CLI.

This phase should create that visibility surface.

---

### Problem 2: State Should Be Visible Before It Becomes Actionable

This project’s control model depends on staircase ordering:

- land state
- make it visible
- make it interpretable
- only later make it actionable

This phase should implement only the visibility step.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/reviewer_output.py`
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to add a read-only recommendation visibility surface.

---

## Required Feature

Add a read-only CLI command that lists persisted reviewer recommendations.

Recommended command shape:

- `python main.py recommendations`
- optional:
  - `python main.py recommendations --run <run_id>`

Default behavior if no `--run` is provided:
- use the active run if one exists
- if no active run exists, print a clear message and stop

The command must not mutate state.

---

## Recommendation Visibility Surface

The CLI output should present recommendation records clearly and minimally.

At minimum, each surfaced recommendation should include:

- reviewer task ID
- run ID
- recommendation type
- reason
- timestamp

If source-task linkage is already directly and cheaply available from the stored record or associated reviewer task, you may also surface:
- source task ID

Do NOT broaden into rich interpretation or action hints yet.

The purpose is visibility, not recommendation policy.

---

## Ordering / Filtering Rules

The command should show only persisted reviewer recommendation records.

If `--run <run_id>` is supplied:
- show only recommendations for that run

If no run is supplied and an active run exists:
- show only recommendations for the active run

Ordering should be deterministic and readable.
A simple timestamp-based ordering is acceptable.

If no matching recommendations exist:
- print a clear message and stop

---

## Non-Goals

This phase must NOT:

- interpret recommendations
- rank recommendations
- derive action candidates
- create tasks
- mutate recommendation records
- broaden recommendation schema
- add a UI
- add dashboard layers

This is read-only visibility only.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy
- Do NOT redesign recommendation persistence
- Do NOT redesign the recommendation schema
- Do NOT bundle in candidate-action surfacing or recommendation interpretation

This is recommendation visibility only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Show Recommendations for Active Run

Expected:
- when active run exists and persisted recommendations exist for it
- command shows those recommendations clearly

### Test B: Show Recommendations for Explicit Run

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
- recommendation visibility remains read-only
- no task creation
- no routing change
- existing recommendation persistence behavior remains intact

---

## Success Criteria

- persisted reviewer recommendations can be inspected from the CLI
- output is clear and minimal
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
   - how recommendation visibility works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
