# PHASE_29.md

## Phase 29: CLI Semantic Consolidation for Recommendation Lifecycle

---

## Goal

Reduce semantic duplication in `main.py` by consolidating recommendation-derived task lifecycle logic into a small explicit reusable helper surface.

This phase should allow the project to:

- keep recommendation lifecycle semantics centralized
- reduce the risk of CLI-specific policy drift
- preserve current user-facing behavior
- keep `main.py` closer to a command-dispatch surface rather than a parallel policy layer

This is a hardening/refinement phase.

It is NOT about:
- adding new features
- changing command behavior
- redesigning the CLI broadly
- queue behavior changes
- schema redesign
- general refactoring for style alone

---

## Problems This Phase Must Solve

### Problem 1: Recommendation Lifecycle Semantics Are Becoming Too Scattered in `main.py`

The project now contains multiple CLI commands related to:

- recommendation-created tasks
- confirmed tasks
- ready tasks
- ready execution candidates
- explicit ready-candidate execution

Much of the filtering and eligibility logic for these surfaces currently lives in or near `main.py`.

This increases the risk that semantic rules begin to drift across commands.

---

### Problem 2: The CLI Should Not Become a Parallel Policy Surface

The project’s control semantics should live in one explicit place where possible.

When lifecycle meaning is repeated in multiple command paths, the CLI layer starts to act like a second control system.

This phase should reduce that risk without changing behavior.

---

## Files to Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/run_manager.py`
- optionally a small new helper module under `orchestrator/` only if clearly justified
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT broaden changes beyond what is necessary to consolidate lifecycle semantics cleanly.

---

## Required Consolidation

Centralize the semantic logic for recommendation lifecycle task classes so `main.py` reuses explicit helpers rather than repeating local filtering rules.

At minimum, consolidate reusable logic for:

- recommendation-created tasks
- confirmed recommendation-created tasks
- ready recommendation-created tasks
- ready execution candidates

The exact helper shape is up to implementation, but it must remain:

- small
- explicit
- readable
- behavior-preserving

---

## Behavior Preservation Requirement

This phase must preserve existing user-facing behavior for current commands.

That includes, where applicable:

- recommendation-created task surfaces
- confirmed recommendation task surfaces
- ready recommendation task surfaces
- ready execution candidate surfaces
- explicit ready-candidate execution eligibility checks

Do NOT change semantics unless a genuine defect is discovered.
If a defect is discovered that clearly exceeds Phase 29 scope, stop and report it rather than silently broadening the phase.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT introduce new commands unless strictly necessary
- Do NOT redesign the CLI broadly
- Do NOT change queue behavior
- Do NOT change execution semantics
- Do NOT refactor unrelated code for style reasons
- Do NOT create a large policy abstraction layer

This phase is semantic consolidation only.

---

## Validation Requirements

Validate at least these cases:

### Test A: Recommendation-Created Task Surfaces

Expected:
- existing recommendation-created task commands still behave the same

### Test B: Confirmed / Ready / Candidate Surfaces

Expected:
- confirmed-task, ready-task, and candidate commands still identify the same task classes correctly

### Test C: Explicit Ready-Candidate Execution Eligibility

Expected:
- explicit ready-candidate execution still accepts and rejects the same task classes correctly

### Test D: No Ordinary Queue Behavior Change

Expected:
- `next` behavior remains unchanged

### Test E: Regression Coverage Still Passes

Expected:
- existing regression modules for recommendation lifecycle continue to pass

---

## Success Criteria

- recommendation lifecycle semantics are more centralized and less duplicated
- `main.py` becomes less semantically authoritative
- user-facing behavior remains unchanged
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was consolidated
   - which files were created or modified

2. Report:
   - where lifecycle semantics now live
   - how behavior preservation was validated
   - whether any defects were discovered

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
