# PHASE_49.md

## Phase 49: Archival-Aware Recommendation Read Surfaces

---

## Goal

Make the existing read-only recommendation surfaces archival-aware so persisted recommendation records that have been explicitly archived are clearly surfaced as archived, without redesigning the recommendation subsystem or adding new mutation behavior.

This phase should ensure the operator can distinguish between:
- active recommendation state
- archived recommendation state

across the existing recommendation read surfaces, while preserving boundedness and inspectability.

This is a forward feature phase.

It is NOT about:
- additional recommendation mutation commands
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

### Problem 1: Archival Now Exists, But Read Surfaces May Not Reflect It Clearly

The system can now explicitly archive a persisted recommendation record.

That is good.

But the read-only recommendation surfaces were intentionally left mostly unchanged. That means the system now contains archival truth on disk that may not yet be clearly legible through the operator-facing surfaces.

This phase should correct that.

---

### Problem 2: Read-State Coherence Must Catch Up After Mutation Is Introduced

The project’s staircase has now crossed into explicit recommendation-state mutation.

Once mutation exists, the read surfaces should not remain blind to it. Otherwise the operator is forced to inspect raw JSON to understand whether a recommendation is still active.

This phase should make the existing read surfaces archival-aware, and nothing more.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/reviewer_output.py`
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to make existing recommendation read surfaces archival-aware.

---

## Required Feature

Update the existing recommendation read-only CLI surfaces so archived recommendation records are clearly surfaced as archived.

At minimum, review and update the existing read surfaces that show recommendation records directly, such as:

- `recommendations`
- `recommendation-summary`
- `recommendation-actions`
- `recommendation-drafts`
- `recommendation-outcomes`
- `recommendation-resolution`

You do NOT need to redesign each command.
You do need to ensure archived recommendation state is legible and consistent across them.

---

## Archival-Aware Surface Rules

Choose the smallest consistent implementation.

A minimal acceptable approach is:

- archived recommendation records remain readable
- archived recommendation records are clearly labeled as archived in output
- where a command groups or summarizes recommendation state, archived recommendations are either:
  - included but clearly marked
  - or excluded by default only if the command also clearly reports that archival filtering occurred

Prefer the smallest change that preserves continuity and inspectability.

Strong preference:
- do NOT hide archived records silently
- do NOT create multiple filtering modes unless truly necessary

---

## Output Expectations

For per-record surfaces, archived recommendation records should clearly show archival state, for example by including:

- archival status text
- archived timestamp if directly available and cheap to show

For summary/grouped surfaces, archived records should remain understandable in the summary output in the smallest coherent way possible.

Do NOT:
- redesign output formats broadly
- add policy language
- add ranking or decision hints
- add new archival commands

---

## Non-Goals

This phase must NOT:

- add new archival mutation behavior
- add unarchive behavior
- add acceptance-specific state
- redesign recommendation schema broadly
- archive or mutate records implicitly
- introduce batch filtering systems
- add UI/dashboard layers

This is archival-aware read-surface coherence only.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add automation
- Do NOT change queue policy
- Do NOT redesign recommendation persistence broadly
- Do NOT redesign the recommendation schema broadly
- Do NOT bundle in acceptance-specific semantics

This is read-surface coherence only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Archived Recommendation Appears Clearly In Direct Listing

Expected:
- `recommendations` (or equivalent direct record surface) clearly shows archival state for archived records

### Test B: Archived Recommendation Remains Legible In Summary / Grouped Surfaces

Expected:
- archival state is not silently lost in grouped or interpreted recommendation surfaces

### Test C: Non-Archived Recommendation Behavior Remains Intact

Expected:
- active recommendation records still appear normally
- no unrelated behavior regression occurs

### Test D: No Hidden Behavior Change

Expected:
- no task creation
- no queue mutation
- no additional recommendation mutation
- existing recommendation archival and creation behavior remains intact

### Test E: Regression Surfaces Still Pass

Expected:
- existing recommendation visibility, interpretation, action, draft, outcome, resolution, and archive tests still pass

---

## Success Criteria

- archived recommendation state is clearly legible across the existing recommendation read surfaces
- the implementation is minimal and consistent
- archived records are not silently hidden unless explicitly and clearly reported
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how archival-aware recommendation read surfaces now work
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
