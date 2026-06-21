# PHASE_12.md

## Phase 12: Regression Tests for Reviewer Recommendation Handling

---

## Goal

Add a small, durable regression test surface for the reviewer recommendation behavior introduced in Phase 11.

This phase should verify that:

- reviewer-role tasks validate recommendation output as JSON only
- valid reviewer recommendations complete successfully and persist records
- invalid reviewer recommendations fail cleanly as `verification_failed`
- execution and verification precedence remain intact
- ordinary non-reviewer task behavior remains unchanged

This phase is about preserving the semantics of the current orchestration core.

It is NOT yet about:
- broad test framework expansion
- end-to-end autonomous workflow testing
- planner-generated task testing
- writeback or repair-loop testing
- performance testing
- multi-provider matrix expansion beyond what is needed for bounded validation

---

## Problems This Phase Must Solve

### Problem 1: Phase 11 Added a New Control Branch Without Durable Regression Guarding

Phase 11 introduced reviewer-role-specific recommendation parsing, validation, and persistence.

That behavior now affects:

- task status outcomes
- persistence side effects
- separation between reviewer and ordinary task flows

Without durable regression tests, later edits to `orchestrator/engine.py` or reviewer-output handling may silently break these semantics.

---

### Problem 2: Reviewer Logic Must Remain Narrow and Must Not Leak Into Ordinary Task Routing

The current design depends on reviewer recommendation handling applying only to reviewer-role tasks.

Ordinary tasks must continue to use:

- execution outcome
- verification outcome
- adequacy assessment
- reviewer-task creation on inadequacy

This phase must lock that distinction in with tests.

---

## Files to Create

Create only the minimal new test files required.

Preferred approach:
- create a small tests surface under an explicit project-root test location

Recommended:
- tests/test_phase_12_reviewer_recommendations.py

If the repo already has an established testing location or shell-driven acceptance style that is clearly better aligned with the existing project, use the smallest consistent option.

Do NOT introduce multiple new test directories unless truly necessary.

---

## Files to Modify

- docs/ACTION_LOG.md
- docs/PHASE_INDEX.md
- optionally existing test runner or test plan files only if strictly needed

If needed for minimal test execution support:
- TEST_PLAN.md

Do NOT modify implementation code unless testability reveals a genuine defect.
If a genuine implementation defect is discovered, STOP and report it rather than silently fixing it in this phase.

---

## Core Behavior

This phase must add reproducible tests for the following Phase 11 behaviors.

### Required Test Surface

#### Test A: Valid Reviewer Recommendation

A reviewer-role task with:
- successful provider execution
- passing verification
- valid JSON recommendation output

Expected:
- final status = `completed`
- recommendation record is persisted
- record contains required recommendation fields only in the recommendation payload

---

#### Test B: Invalid Reviewer Recommendation Structure

A reviewer-role task with:
- successful provider execution
- passing verification
- invalid reviewer output

Examples:
- malformed JSON
- JSON array instead of object
- missing required fields
- invalid `recommendation_type`

Expected:
- final status = `verification_failed`
- no accepted recommendation record is persisted

---

#### Test C: Reviewer Execution Failure Precedence

A reviewer-role task with:
- provider execution error

Expected:
- final status = `execution_failed`
- reviewer recommendation validation does not run
- no recommendation record is persisted

---

#### Test D: Reviewer Verification Failure Precedence

A reviewer-role task with:
- successful execution
- failing normal verification

Expected:
- final status = `verification_failed`
- reviewer recommendation validation does not run
- no recommendation record is persisted

---

#### Test E: Ordinary Task Behavior Unchanged

A non-reviewer task with:
- successful execution
- passing verification
- inadequate output

Expected:
- original task status = `needs_review`
- reviewer task is created
- reviewer recommendation parsing is not applied to the ordinary task
- ordinary adequacy routing remains intact

---

## Test Design Rules

Tests must be:

- deterministic
- minimal
- readable
- bounded to the current architecture

Prefer:

- direct setup of task/run artifacts in test state
- mock-provider-driven execution where possible
- explicit assertions on persisted files and task statuses

Avoid:

- open-ended model behavior tests
- fragile environment assumptions
- broad integration sprawl
- hidden dependencies on conversational context

---

## Implementation Guidance

Use the smallest testing mechanism that matches the repository’s existing style.

Preferred order of options:

1. Existing project test mechanism, if one already exists and is appropriate
2. Simple Python test file(s) with explicit setup/assertions
3. Minimal shell-based test wrapper only if it is already the established style and keeps scope smaller

Do NOT introduce:
- a large new test framework
- fixture-heavy abstraction systems
- coverage tooling
- CI pipeline work
- multi-environment orchestration

This phase is for regression guarding, not test-platform construction.

---

## Test Data and Side Effects

Tests may create temporary:

- runs
- tasks
- verifier results
- artifacts
- reviewer recommendation records

But test behavior must remain bounded and inspectable.

If cleanup is implemented, keep it simple.
If cleanup is not implemented, isolate test data clearly and avoid damaging existing project state.

Do NOT redesign persistence for test isolation in this phase.

---

## Validation Requirements

This phase is complete only if the new tests can be run reproducibly and their outcomes are clear.

At minimum, report:

- which tests were added
- how they are run
- which passed
- whether any implementation defect was discovered during testing

If any required test reveals a real defect:
- STOP
- report the defect clearly
- do NOT silently absorb implementation fixes into this testing phase

That defect should be handled through a bounded fix document.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT redesign implementation layers for ideal testability
- Do NOT expand into broad framework work
- Do NOT add future-phase testing
- Do NOT silently fix implementation defects discovered by tests
- Do NOT broaden provider coverage unnecessarily
- Do NOT alter reviewer recommendation semantics
- Do NOT weaken existing adequacy routing

This phase exists to guard the current behavior, not change it.

---

## Success Criteria

- reproducible regression tests exist for the Phase 11 reviewer recommendation branch
- tests cover valid and invalid reviewer outputs
- tests cover execution-failure and verification-failure precedence
- tests confirm ordinary-task routing remains unchanged
- no implementation code is changed unless a real defect is discovered and explicitly reported
- no testing infrastructure sprawl is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what tests were added
   - which files were created or modified

2. Report:
   - how the tests are run
   - which required cases passed
   - whether any defect was discovered

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further