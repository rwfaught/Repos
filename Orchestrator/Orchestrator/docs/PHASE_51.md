# PHASE_51.md

## Phase 51: Current Success Criterion Validation on a Real Bounded Task

---

## Goal

Validate the current system against `CURRENT_SUCCESS_CRITERION.md` by adding a bounded, repeatable, inspectable end-to-end validation path that demonstrates whether the system can successfully execute a real small coding task under current architecture and control rules.

This phase is a **validation-first hardening / product-anchor phase**.

It is not primarily about adding new recommendation features.

It is about forcing the project to answer, with repo-level evidence, whether the current system actually satisfies its present-tense success bar.

---

## Why This Phase Exists

The project now has:

- strong governance documents
- a deep recommendation lifecycle
- explicit mutation/read surfaces
- passing regression coverage for many recommendation behaviors

That is good.

But governance-health is not the same thing as product-health.

The project’s current method now explicitly requires forward ranking to be anchored to the present-tense success criterion, not merely to the most recently active subsystem.

This phase creates that anchor in executable form.

---

## Problems This Phase Must Solve

### Problem 1: The Current Success Bar Exists in Prose But Is Not Yet Proved in a Focused Repo-Level Validation Path

`CURRENT_SUCCESS_CRITERION.md` now defines what a successful run means today.

That is useful.

But unless the repo contains a bounded, repeatable way to validate that bar on a real small task, the success criterion risks becoming advisory prose rather than an operational checkpoint.

This phase should create that checkpoint.

---

### Problem 2: Future Ranking Should Be Driven By Observed Product Bottlenecks

If the current system fails this validation, the failure should inform the next move.

For example:
- thin deterministic verification may emerge as the real bottleneck
- outcome clarity may be insufficient in some path
- CLI/control-surface density may hinder understandable operation
- recommendation handling may prove adequate already

This phase should not pre-decide that answer.
It should create the bounded evidence path that reveals it.

---

## Scope Of This Phase

This phase should add the smallest clear validation surface needed to test the current success criterion honestly.

Likely acceptable outcomes include one or more of:

1. a focused acceptance-style test module
2. a deterministic fixture-based end-to-end validation path
3. a small validation command or script only if clearly justified
4. minimal supporting fixture/task setup required to exercise the real workflow

Choose the smallest implementation that makes the current success bar concretely testable.

---

## This Phase Is NOT About

- adding new recommendation mutations
- adding `recommendation-restore`
- adding `unaccept`
- broad verifier redesign
- planner autonomy
- automatic repair chains
- writeback
- dashboard/UI work
- broad CLI refactoring
- broad test-framework redesign
- synthetic demos that bypass the real orchestration flow

This phase must stay tightly anchored to validating the existing system as it is.

---

## Files To Modify

Modify only the minimum files required.

Likely candidates:
- targeted files under `tests/`
- `run_acceptance_tests.sh` only if strictly necessary
- possibly a narrow helper under `orchestrator/` only if a validation seam is genuinely missing
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Use the smallest modification surface possible.

Do NOT broaden the change into a product feature phase.

---

## Required Validation Target

The implemented validation path must exercise a **real bounded task flow** through the current system such that the operator can determine whether the following current-state bar is met:

1. persisted task state is clear
2. execution artifact is persisted
3. deterministic verification result is persisted
4. final outcome classification is clear and truthful
5. if review occurs, recommendation landing is structured and inspectable
6. operator-visible next-step surfaces are legible under current rules

The validation path may use one or more small fixture scenarios.

Keep them bounded and inspectable.

---

## Preferred Validation Scenarios

At minimum, validate a small set of current-state scenarios such as:

### Scenario A: Clean bounded success
A small coding-style task or bounded file-target task that:
- executes successfully
- verifies successfully
- persists artifact and verifier result
- ends with a truthful successful outcome classification

### Scenario B: Verification failure
A bounded task that:
- executes
- fails deterministic verification
- persists artifact and verifier result
- lands in the correct non-success status

### Scenario C: Review landing path
A bounded task path that:
- routes to reviewer handling under current rules
- persists structured recommendation output correctly
- makes the recommendation inspectable via current control surfaces

Use the smallest set of scenarios that honestly covers the current success criterion.

Do NOT expand into broad combinatorial testing.

---

## Implementation Rules

1. Prefer exercising existing commands and existing persistence behavior over inventing a parallel test-only system.
2. Prefer deterministic fixtures over broad live-provider dependence.
3. Prefer mock-provider or otherwise stable bounded execution unless a real provider is absolutely required.
4. Keep the validation readable enough that it can function as a product-health checkpoint, not just as test machinery.
5. Do not overbuild a new acceptance framework if targeted validation is sufficient.

---

## Source Of Truth

The validation must judge the real persisted outputs of the existing orchestration system:

- task records
- artifact records
- verifier results
- recommendation records where applicable

Do NOT substitute prose claims for persisted evidence.

Do NOT treat conversational expectation as proof.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT add new recommendation mutation commands
- Do NOT redesign the recommendation state model
- Do NOT broaden verifier semantics beyond what is needed to validate the current system honestly
- Do NOT refactor `main.py` broadly in this phase
- Do NOT create a second control path just for validation
- Do NOT overclaim success if the validation reveals shortfalls

This phase is about truthful current-state validation.

---

## Validation Requirements

The phase itself must validate at least these cases:

### Test A: Successful bounded run
Expected:
- task state persists correctly
- artifact persists
- verifier result persists
- final status is truthful and inspectable

### Test B: Verification-failed bounded run
Expected:
- failure is persisted clearly
- verifier result is inspectable
- no ambiguous success semantics appear

### Test C: Reviewer recommendation landing
Expected:
- reviewer output is persisted in the currently supported recommendation structure
- recommendation record is inspectable
- operator-visible recommendation surfaces remain coherent

### Test D: No hidden behavior change
Expected:
- no queue-policy drift
- no automatic repair/creation escalation
- no automatic recommendation resolution
- no hidden mutation outside the current system rules

---

## Success Criteria

- the repo gains a bounded, repeatable validation path that tests the current success criterion on real persisted system behavior
- the result makes current product-health easier to judge honestly
- the implementation stays small and does not mutate the architecture unnecessarily
- the phase produces evidence that can inform the next ranking decision

---

## End Of Phase

STOP after completion.

Then:

1. Summarize:
   - what validation path was added
   - which files were created or modified

2. Report:
   - which current-success scenarios were validated
   - what the validation showed
   - whether any current-success gap was revealed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
