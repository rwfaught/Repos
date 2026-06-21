# PHASE_27.md

## Phase 27: Recommendation Provenance Normalization

---

## Goal

Replace the project’s growing reliance on semi-structured `review_reason` parsing with a small, explicit provenance representation for recommendation-derived tasks.

This phase should allow the system to:

- preserve recommendation provenance in explicit task fields rather than string conventions
- reduce dependence on parsing `review_reason` for recommendation type and recommendation-origin identity
- keep existing recommendation-created task behavior intact
- improve the stability of later lineage, confirmation, readiness, and execution-candidate logic

This phase is about provenance hardening, not behavior expansion.

It is NOT yet about:
- changing recommendation semantics
- changing confirmation semantics
- changing readiness semantics
- changing execution-candidate semantics
- redesigning the whole task schema
- broad CLI refactoring
- general metadata expansion

---

## Problems This Phase Must Solve

### Problem 1: `review_reason` Has Become a Shadow Schema

The current build uses `review_reason` for both:
- human-readable explanation
- semi-structured machine-readable provenance such as `recommendation_type=...`

That was a reasonable bridge earlier, but it is now load-bearing across multiple later features.

This phase should stop treating `review_reason` as the primary carrier of recommendation provenance.

---

### Problem 2: Later Workflow Layers Depend on Stable Recommendation-Origin Semantics

The project now has multiple surfaces that depend on recommendation-created task provenance, including:

- lineage surfacing
- created-task review surfaces
- confirmation
- readiness
- ready-candidate surfacing
- explicit ready-candidate execution

These features should depend on explicit narrow provenance fields, not string parsing conventions.

---

## Files to Modify

- `orchestrator/task_schema.py`
- `orchestrator/run_manager.py`
- `orchestrator/engine.py` (only if needed for creation/update plumbing)
- `main.py`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

If strictly needed:
- `orchestrator/recommendation_store.py`

Do NOT broaden modifications beyond what is necessary to normalize provenance cleanly.

---

## Required Normalization

Introduce the smallest explicit provenance fields needed for recommendation-derived tasks.

Recommended minimal additions:

- `recommendation_type` (optional string)
- `recommendation_reason` (optional string)

These fields should be used for recommendation-created tasks and any other workflow surfaces where explicit recommendation provenance is required.

The existing `review_reason` field may remain for backward compatibility and human-readable context, but later logic should no longer depend primarily on parsing it for recommendation provenance.

---

## Core Behavior

### 1. Task Creation / Persistence

When the system creates a recommendation-derived task, it should persist explicit recommendation provenance in the normalized fields.

This applies at minimum to:
- recommendation-created follow-up tasks
- any created tasks whose later lifecycle depends on recommendation provenance

### 2. Read Logic

Later workflow logic that currently depends on parsing `review_reason` for recommendation provenance should be updated to prefer the explicit normalized fields.

Examples include logic for:
- recommendation-created task detection
- recommendation-emitter vs manual-followup reviewer separation if provenance is relevant
- confirmation/readiness/candidate detection
- lineage and review surfacing

### 3. Backward Compatibility

If older persisted tasks exist that still rely on `review_reason` parsing, the system may support a bounded fallback for compatibility.

If fallback is used:
- prefer explicit normalized fields first
- fall back to old `review_reason` parsing only when explicit fields are absent

This phase should improve the default path without breaking existing persisted state unnecessarily.

---

## Normalization Rules

Keep the normalization small and explicit.

Do:
- introduce the minimum provenance fields required
- preserve current behavior wherever possible
- migrate logic to explicit fields gradually but decisively
- support backward compatibility in a bounded way if needed

Do NOT:
- redesign the entire task schema
- add large nested provenance objects
- add generic metadata blobs
- add new routing behavior
- change user-facing semantics unrelated to provenance

---

## Output / CLI Expectations

User-facing command behavior should remain functionally the same where possible.

The important change is internal correctness and robustness:
- provenance-driven surfaces should still work
- but should now rely on explicit fields when available

Any user-visible changes should be limited to:
- improved stability/clarity
- no regression in existing commands

Do NOT introduce new CLI commands in this phase unless strictly necessary.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT redesign the recommendation system
- Do NOT redesign queue behavior
- Do NOT redesign confirmation/readiness semantics
- Do NOT perform broad CLI cleanup here
- Do NOT add unrelated schema fields

This is provenance normalization only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Newly Created Recommendation-Derived Task

Expected:
- explicit normalized provenance fields are persisted
- later workflow surfaces still recognize the task correctly

---

### Test B: Existing Older Recommendation-Derived Task

Expected:
- backward compatibility works if normalized fields are absent
- existing behavior does not regress unexpectedly

---

### Test C: Reviewer Semantic Separation Still Works

Expected:
- recommendation-emitter reviewer tasks remain distinct where required
- manual-followup reviewer tasks are not conflated again

---

### Test D: Confirmation / Readiness / Candidate Surfaces Still Work

Expected:
- confirmed-task, ready-task, and execution-candidate surfaces still identify tasks correctly using normalized provenance when available

---

### Test E: No Unrelated Behavior Change

Expected:
- ordinary non-recommendation task behavior remains unchanged
- `next` behavior remains unchanged
- explicit ready-candidate execution remains unchanged except for provenance robustness

---

## Success Criteria

- explicit recommendation provenance fields exist and are used
- `review_reason` is no longer the primary provenance carrier for current behavior
- backward compatibility is preserved in a bounded way if needed
- later recommendation-derived task surfaces remain intact
- no unrelated architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was normalized
   - which files were modified

2. Report:
   - how explicit provenance is now stored
   - how backward compatibility is handled
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
