# PHASE_43.md

## Phase 43: Read-Only Candidate-Action Surfacing

---

## Goal

Add a read-only operator surface that shows what explicit candidate actions are available from persisted reviewer recommendations, without creating tasks or mutating system state.

This phase should build on recommendation landing, visibility, and interpretation by surfacing bounded possible next moves while remaining strictly advisory.

This is a forward feature phase.

It is NOT about:
- automatic routing
- automatic repair creation
- automatic follow-up creation
- task creation
- draft proposal generation
- writeback
- queue mutation
- UI/dashboard work
- broad schema redesign

---

## Problems This Phase Must Solve

### Problem 1: Recommendation State Is Now Interpretable but Still Not Operationally Surfaced

The system can now:
- persist reviewer recommendations
- list them
- summarize them by type at the run level

That is good.

But the operator still has to manually translate recommendation state into possible next steps. The system does not yet provide a read-only surface showing which explicit actions are currently available.

This phase should create that surface.

---

### Problem 2: Candidate Actions Must Be Surfaced Before They Are Drafted or Created

This project’s staircase depends on ordered capability growth:

- land state
- make it visible
- make it interpretable
- surface candidate actions
- later draft proposals
- only later allow explicit creation

This phase should implement only the candidate-action surfacing step.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/reviewer_output.py`
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to add a read-only candidate-action surface.

---

## Required Feature

Add a read-only CLI command that surfaces candidate actions implied by persisted reviewer recommendations for a run.

Recommended command shape:

- `python main.py recommendation-actions`
- optional:
  - `python main.py recommendation-actions --run <run_id>`

Default behavior if no `--run` is provided:
- use the active run if one exists
- if no active run exists, print a clear message and stop

The command must not mutate state.

---

## Candidate-Action Surface

The CLI output should show candidate actions clearly and minimally.

At minimum, the surface should map recommendation types to explicit possible actions:

- `accept_result`
  - surface as: result may be accepted / no immediate follow-up action required
- `manual_followup`
  - surface as: follow-up review task could be created explicitly
- `repair_candidate`
  - surface as: repair task could be created explicitly

This surface must remain descriptive only.

Do NOT:
- create the task
- draft the task yet
- rank or score actions
- choose actions automatically
- merge or collapse distinct recommendations into one policy decision

---

## Output Requirements

At minimum, each surfaced candidate-action entry should include:

- reviewer task ID
- recommendation type
- reason
- candidate action text
- timestamp

If source-task linkage is directly and cheaply available, you may also include:
- source task ID

Ordering should be deterministic and readable.

A minimal acceptable ordering is:
1. stable recommendation-type order
2. entries within each type ordered by `(timestamp, reviewer_task_id)`

If no matching recommendations exist:
- print a clear message and stop

---

## Non-Goals

This phase must NOT:

- create tasks
- generate task drafts
- mutate recommendation records
- broaden recommendation schema
- attach confidence scores
- introduce policy ranking
- add UI/dashboard layers
- add automatic decision logic

This is read-only candidate-action surfacing only.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy
- Do NOT redesign recommendation persistence
- Do NOT redesign the recommendation schema
- Do NOT bundle in draft proposal generation or explicit task creation

This is recommendation-action surfacing only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Show Candidate Actions For Active Run

Expected:
- when active run exists and persisted recommendations exist for it
- command shows candidate actions clearly for those recommendations

### Test B: Show Candidate Actions For Explicit Run

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
- candidate-action surfacing remains read-only
- no task creation
- no routing change
- existing recommendation landing / visibility / interpretation behavior remains intact

---

## Success Criteria

- persisted reviewer recommendations can be surfaced as explicit candidate actions from the CLI
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
   - how candidate-action surfacing works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
