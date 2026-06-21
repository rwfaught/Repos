# PHASE_44.md

## Phase 44: Draft Proposal Generation From Recommendation State

---

## Goal

Add a read-only operator surface that generates bounded draft proposals from persisted reviewer recommendations, without creating tasks or mutating system state.

This phase should build on recommendation landing, visibility, interpretation, and candidate-action surfacing by turning recommendation state into explicit draft task proposals that the operator can inspect before any later creation step exists.

This is a forward feature phase.

It is NOT about:
- automatic routing
- automatic repair creation
- automatic follow-up creation
- task creation
- queue mutation
- writeback
- policy ranking
- UI/dashboard work
- broad schema redesign

---

## Problems This Phase Must Solve

### Problem 1: Candidate Actions Exist but Still Lack Concrete Draft Form

The system can now surface candidate actions implied by reviewer recommendations.

That is good.

But the operator still has to mentally translate those candidate actions into bounded task proposals. The system does not yet provide draft proposal packets that show what would likely be created later.

This phase should create that draft surface.

---

### Problem 2: Drafts Must Exist Before Explicit Creation

This project’s staircase depends on ordered capability growth:

- land state
- make it visible
- make it interpretable
- surface candidate actions
- generate drafts
- only later allow explicit creation

This phase should implement only the draft generation step.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/reviewer_output.py`
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to add a read-only draft proposal surface.

---

## Required Feature

Add a read-only CLI command that generates bounded draft proposals from persisted reviewer recommendations for a run.

Recommended command shape:

- `python main.py recommendation-drafts`
- optional:
  - `python main.py recommendation-drafts --run <run_id>`

Default behavior if no `--run` is provided:
- use the active run if one exists
- if no active run exists, print a clear message and stop

The command must not mutate state.

---

## Draft Proposal Surface

The CLI output should generate explicit, bounded draft proposals from recommendation records.

At minimum, draft generation should support:

- `manual_followup`
  - generate a draft follow-up review proposal
- `repair_candidate`
  - generate a draft repair-task proposal
- `accept_result`
  - do not generate a creation draft; instead surface that no draft task is needed

Each surfaced draft proposal should remain descriptive only.

Do NOT:
- create the task
- reserve IDs
- modify queue state
- infer broad scope beyond already-available data
- invent unsupported recommendation types

---

## Draft Fields

For each generated draft proposal, include at minimum:

- recommendation source reviewer task ID
- recommendation type
- proposed task role
- proposed task title
- proposed source task linkage if directly and cheaply available
- proposed source artifact linkage if directly and cheaply available
- draft rationale / reason
- timestamp of the recommendation record

For `accept_result`, surface a clear no-draft-needed entry instead of a proposed task packet.

Keep proposals minimal and inspectable.
Do NOT attach policy language like “should definitely” or “must”.

---

## Draft Mapping Rules

A minimal acceptable mapping is:

- `manual_followup`
  - proposed role: `reviewer`
  - proposed title pattern: bounded follow-up review title derived from source linkage when available

- `repair_candidate`
  - proposed role: `coder`
  - proposed title pattern: bounded repair title derived from source linkage when available

- `accept_result`
  - no creation draft
  - explicit informational entry only

If a recommendation record lacks optional linkage fields:
- keep the draft truthful and minimal
- do not invent missing source data

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
- mutate recommendation records
- broaden recommendation schema
- attach confidence scores
- rank proposals
- choose proposals automatically
- add UI/dashboard layers
- add automatic decision logic

This is draft proposal generation only.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy
- Do NOT redesign recommendation persistence
- Do NOT redesign the recommendation schema
- Do NOT bundle in explicit task creation

This is recommendation-draft surfacing only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Show Draft Proposals For Active Run

Expected:
- when active run exists and persisted recommendations exist for it
- command shows draft proposals clearly for actionable recommendations
- `accept_result` appears as no-draft-needed informational output

### Test B: Show Draft Proposals For Explicit Run

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
- draft generation remains read-only
- no task creation
- no routing change
- existing recommendation landing / visibility / interpretation / candidate-action behavior remains intact

---

## Success Criteria

- persisted reviewer recommendations can be surfaced as bounded draft proposals from the CLI
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
   - how draft proposal generation works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
