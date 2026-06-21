# PHASE_55.md

## Phase 55: Current-Success Validation for Declared Content Verification

---

## Goal

Update the current-success validation surface so it proves the post-Phase-54 system on a real bounded task.

This phase is not about adding new verifier capabilities.

It is about showing that the richer declared verification model now lands correctly in an end-to-end bounded run and remains legible to the operator.

The system should demonstrate that:

- a real bounded task can be executed
- declared `verification_checks` are used as part of the task definition
- content-level deterministic verification can participate in success/failure evaluation
- persisted task, artifact, verifier, and recommendation state remain self-explaining

---

## Why This Phase Exists

Phase 51 validated the current success bar before the verifier surface expanded.

Since then:

- Phase 53 introduced declared deterministic verification checks
- Phase 54 added bounded content-level verification checks including:
  - `file_contains_text`
  - `json_parses`

That means the current end-to-end success validation is no longer anchored to the latest verification model.

This phase closes that gap.

---

## This Phase Is About

This phase is about refreshing the current-success validation path so it exercises the declared post-Phase-54 verification model on a real bounded task.

The target is a narrow end-to-end validation proving that:

- the task declares `verification_checks`
- the verifier evaluates those checks
- the resulting persisted state is legible
- recommendation behavior remains bounded and coherent if verification fails

---

## This Phase Is NOT About

This phase is NOT about:

- adding new verification check types
- redesigning verifier schema
- broadening recommendation policy
- changing task lifecycle semantics
- changing run selection behavior
- building API/service-layer infrastructure
- broadening into generalized verifier refactors
- creating multiple new validation scenarios when one bounded scenario is enough

This is a validation-refresh phase only.

---

## Files to Create

- `tests/test_phase_55_declared_content_verification_success.py`

---

## Files to Modify

- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Optional only if strictly necessary:

- validation fixtures or tiny supporting test helpers already used by adjacent tests

Do not modify product code unless a narrowly confirmed defect is discovered while implementing the validation.
If a defect is discovered, stop and report it rather than silently broadening the phase.

---

## Core Requirement

Create one bounded current-success validation test module that proves the post-Phase-54 verification path in an end-to-end scenario.

The scenario must:

1. create or simulate a real bounded task
2. use declared `verification_checks`
3. include at least one content-level deterministic check
4. prove success or controlled failure legibly through persisted state

Preferred default:
- use the smallest realistic scenario that exercises `file_contains_text`

Optional:
- include `json_parses` only if it remains small and materially improves confidence without widening the phase

Default stance:
- one content-level check is sufficient if it proves the post-Phase-54 success path cleanly

---

## Scenario Requirements

The validation should prove a real bounded task rather than a synthetic verifier-only unit behavior.

At minimum, the scenario should demonstrate:

- task creation with declared verification checks
- task execution producing an artifact or output
- verification evaluation against that output
- persisted verification result
- bounded final task state
- recommendation state only if the scenario is intentionally structured as a controlled failure case

The phase may use either:

- a success-path scenario only
or
- a tightly paired success/failure scenario

Preferred default:
- success-path primary validation

Add failure-path coverage only if it stays small and clearly strengthens confidence.

---

## Verification Requirements

The validation must prove that declared verification checks are the active path.

That means the scenario should not rely only on legacy `files_in_scope`-style presence checks.

The test should make clear that:

- verification truth comes from `verification_checks`
- content-level evaluation is actually consulted
- the result is persisted legibly

If helpful, the test may explicitly distinguish:
- file existence truth
from
- content verification truth

But do not turn this into a broad verifier taxonomy exercise.

---

## Content-Level Check Selection

### Preferred baseline

Use:

- `file_contains_text`

Reason:
- smallest meaningful proof that the verifier can check not just file presence, but semantic content anchors in a bounded deterministic way

### Optional secondary check

Use:

- `json_parses`

Only if:
- it can be included with very small additional complexity
- it strengthens confidence materially
- it does not turn the phase into a multi-check framework exercise

Default:
- defer `json_parses` if including it broadens the phase

---

## Success Criteria

This phase is successful when:

- a new bounded current-success validation module exists
- the validation proves declared `verification_checks` are used
- at least one post-Phase-54 content-level deterministic check participates in end-to-end validation
- persisted state remains legible and bounded
- no product-code changes were required
- docs are updated to reflect the new completed validation phase

---

## Validation Requirements

Required validation:

### Test A: compile validation

Run:

`python3 -m py_compile tests/test_phase_55_declared_content_verification_success.py`

Expected:
- passes cleanly

---

### Test B: new Phase 55 validation

Run:

`python3 -m unittest tests.test_phase_55_declared_content_verification_success`

Expected:
- passes cleanly

---

### Test C: adjacent regression validation

Run the smallest adjacent regression surface needed to prove no drift in the existing current-success/recommendation-validation staircase.

Minimum expected adjacent coverage should include:

- `tests.test_phase_51_current_success_validation`

Optionally include adjacent phases if needed, but keep the regression set bounded.

---

## Design Rules

This phase must preserve the following rules:

### 1. proof, not expansion

Do not add verifier capability.
Prove the capability that already exists.

### 2. one bounded scenario first

Prefer one strong bounded scenario over multiple decorative scenarios.

### 3. no hidden product-code mutation

If product code appears to need changes, stop and report the defect rather than silently broadening scope.

### 4. keep operator legibility central

The purpose is not merely green tests.
The purpose is showing that post-Phase-54 verification truth lands in persisted state a human can inspect and trust.

---

## Implementation Notes

The safest implementation style is:

- mirror the structure of existing current-success validation tests where appropriate
- add the minimum new fixture/setup needed
- keep the scenario realistic but small
- prefer `file_contains_text` as the first proof check
- treat `json_parses` as optional, not mandatory

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - which verification check path was exercised
   - whether only `file_contains_text` was used or whether `json_parses` was also included
   - what validation was performed
   - whether any product-code defect was discovered

3. Append concise entries to:
   - `docs/ACTION_LOG.md`
   - `docs/PHASE_INDEX.md`

4. Do NOT proceed further
