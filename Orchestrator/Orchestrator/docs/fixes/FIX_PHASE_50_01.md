# FIX_PHASE_50_01.md

## Fix: Acceptance-Aware Recommendation Read Surfaces

---

## Purpose

Correct the control-surface lag introduced by Phase 50 so persisted acceptance state for `accept_result` recommendations is clearly surfaced across the existing recommendation read surfaces.

This fix must preserve the good part of Phase 50:
- explicit `accept_result` acceptance
- minimal persisted acceptance markers
- no hidden queue mutation
- no task creation or execution

But it must restore read/write coherence so acceptance truth on disk is legible through the operator-facing surfaces.

---

## Problem

Phase 50 added explicit acceptance handling for `accept_result` recommendations.

That created new persisted truth on recommendation records:

- `accepted: true`
- `accepted_at: <timestamp>`

But acceptance visibility was only added minimally in direct recommendation summaries.

This creates a control-surface lag:

- the persisted record knows acceptance state
- the broader recommendation read surfaces may not show it consistently

That is not a new feature gap.
It is a bounded control-surface coherence issue.

---

## Goal

Make the existing recommendation read surfaces acceptance-aware.

After this fix:

- accepted recommendation records must remain readable
- accepted recommendation records must be clearly labeled as accepted
- grouped/interpreted recommendation surfaces must not silently drop acceptance state
- acceptance and archival must remain distinguishable if both are present

This fix must not introduce new mutation behavior.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/reviewer_output.py`
- `orchestrator/recommendation_store.py`
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to restore acceptance-aware read-surface coherence.

---

## Required Correction

Update the existing recommendation read-only CLI surfaces so accepted recommendation records are clearly surfaced as accepted.

At minimum, review and update the existing read surfaces that show recommendation records directly, such as:

- `recommendations`
- `recommendation-summary`
- `recommendation-actions`
- `recommendation-drafts`
- `recommendation-outcomes`
- `recommendation-resolution`

You do NOT need to redesign each command.
You do need to ensure accepted recommendation state is legible and consistent across them.

A minimal acceptable correction is:

- accepted records remain visible
- accepted state is clearly labeled in direct and grouped surfaces
- accepted timestamp is surfaced where directly available and cheap to show
- accepted + archived records show both states clearly rather than collapsing into one synthetic status

Prefer the smallest consistent implementation.

Strong preference:
- do NOT hide accepted records silently
- do NOT add new filter modes unless truly necessary
- do NOT let acceptance wording blur into broad closure policy

---

## Behavior Preservation Requirement

This fix must preserve:

- explicit `accept_result` acceptance behavior
- explicit archival behavior
- read-only nature of existing recommendation surfaces
- no task creation
- no execution
- no queue mutation
- no additional recommendation mutation behavior

This fix should only restore the missing read-surface coherence.

---

## Constraints

- Keep this fix tightly scoped
- Do NOT add automation
- Do NOT redesign recommendation persistence broadly
- Do NOT redesign the recommendation schema broadly
- Do NOT add new acceptance commands
- Do NOT add unaccept behavior
- Do NOT bundle in broader closure semantics

This is acceptance-aware read-surface coherence only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Accepted Recommendation Appears Clearly In Direct Listing

Expected:
- `recommendations` (or equivalent direct record surface) clearly shows acceptance state for accepted records

### Test B: Accepted Recommendation Remains Legible In Summary / Grouped Surfaces

Expected:
- acceptance state is not silently lost in grouped or interpreted recommendation surfaces

### Test C: Accepted + Archived Record Remains Truthful

Expected:
- if a record is both accepted and archived, both states remain visible without being collapsed into one synthetic status

### Test D: Non-Accepted Recommendation Behavior Remains Intact

Expected:
- records without acceptance markers still appear normally
- no unrelated behavior regression occurs

### Test E: No Hidden Behavior Change

Expected:
- no task creation
- no queue mutation
- no additional recommendation mutation
- existing recommendation acceptance, archival, and creation behavior remains intact

### Test F: Regression Surfaces Still Pass

Expected:
- existing recommendation visibility, interpretation, action, draft, outcome, resolution, archive, and accept tests still pass

---

## Success Criteria

- accepted recommendation state is clearly legible across the existing recommendation read surfaces
- the implementation is minimal and consistent
- accepted records are not silently hidden
- accepted and archived state remain distinguishable when both exist
- no unrelated architectural drift is introduced

---

## End Of Fix

STOP after completion.

Then:

1. Summarize:
   - what was corrected
   - which files were modified

2. Report:
   - how acceptance-aware recommendation read surfaces now work
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update fix tracking in:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
