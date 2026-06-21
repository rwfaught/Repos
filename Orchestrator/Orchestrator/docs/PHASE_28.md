# PHASE_28.md

## Phase 28: Recommendation Lifecycle Regression Hardening

---

## Goal

Add bounded automated regression coverage for the recommendation-derived task lifecycle from recommendation persistence through explicit ready-candidate execution.

This phase should strengthen confidence in the project’s most delicate later-stage governance logic without expanding product behavior.

This is a testing and hardening phase.

It is NOT about:
- adding new execution features
- redesigning the test architecture broadly
- replacing the shell acceptance harness
- exhaustive repo-wide test coverage
- CLI refactoring
- schema redesign

---

## Problems This Phase Must Solve

### Problem 1: The Recommendation Ladder Is Now Deep Enough to Need Durable Regression Protection

The project now has a long recommendation-derived task lifecycle.

That lifecycle includes:
- provenance
- reviewer semantic separation
- task creation
- confirmation
- readiness
- candidate detection
- explicit candidate execution

This is now a load-bearing control surface.

It should not rely primarily on shell-by-shell manual validation.

---

### Problem 2: Later Semantic Layers Need Better Change Protection Than They Currently Have

The project already has earlier regression coverage, but the later recommendation-created task ladder now contains enough linked semantics that local changes can break behavior in subtle ways.

This phase should add bounded automated protection for those semantics.

---

## Files to Create

Create only the minimum test files needed.

Preferred:
- one new unittest module focused on the recommendation-derived task lifecycle

Possible:
- `tests/test_phase_28_recommendation_lifecycle.py`

If small helper reuse is necessary, keep it minimal and local to the test layer.

---

## Files to Modify

- new test file(s) under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Modify implementation code only if:
- a genuine defect is discovered while adding tests
- and only to the minimum extent necessary

If an implementation defect is found that is clearly a post-phase correction rather than part of intended Phase 28 work, stop and report it rather than silently broadening scope.

---

## Required Coverage

Add automated regression coverage for at least these areas:

### 1. Recommendation Provenance

Tests should verify:
- newly created recommendation-derived tasks persist normalized provenance fields
- bounded fallback still works for older tasks without normalized fields

### 2. Reviewer Semantic Separation

Tests should verify:
- recommendation-emitter reviewer tasks still follow recommendation-output validation behavior
- manual-followup reviewer tasks are not forced through recommendation-emitter semantics

### 3. Confirmation / Readiness / Candidate Detection

Tests should verify:
- recommendation-created task detection works
- confirmation state behaves as expected
- readiness semantics behave as expected
- ready execution candidates require:
  - recommendation-created
  - confirmed / ready
  - `status == "queued"`

### 4. Explicit Ready-Candidate Execution

Tests should verify:
- valid ready candidate executes through normal flow
- non-ready recommendation-created task is rejected
- ordinary queued task is rejected
- provider behavior remains explicit and consistent
- ordinary `next` behavior remains unchanged

---

## Test Design Constraints

- Keep tests deterministic
- Prefer bounded fixture setup over dependence on existing live repo state
- Do NOT build a large test framework
- Do NOT broaden scope into general cleanup
- Do NOT use tests as a pretext for unrelated refactors

This phase should protect the later recommendation lifecycle, not redesign the repo.

---

## Validation Requirements

This phase must validate at least:

### Test A: Normalized Provenance on New Recommendation-Derived Task

Expected:
- explicit provenance fields persist
- later lifecycle logic recognizes the task correctly

### Test B: Legacy Provenance Fallback

Expected:
- older task shape still works where fallback is intended

### Test C: Reviewer Semantic Split

Expected:
- emitter reviewer path remains intact
- manual-followup reviewer path remains distinct

### Test D: Confirmation / Readiness / Candidate Logic

Expected:
- confirmed-task, ready-task, and candidate logic remain correct

### Test E: Explicit Candidate Execution

Expected:
- valid candidate executes
- invalid candidates are rejected cleanly
- `next` behavior remains unchanged

---

## Success Criteria

- bounded automated regression coverage exists for the later recommendation-derived task lifecycle
- the most delicate later-stage semantics now have durable change protection
- no unrelated architectural drift is introduced
- no feature expansion is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what tests were added
   - which files were created or modified

2. Report:
   - what lifecycle areas are now regression-covered
   - whether any implementation defects were discovered
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
