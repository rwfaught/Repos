# PHASE_57.md

## Phase 57: Local Intake Judgment Control Surface

---

## Goal

Expose the new service-level intake judgment surface through one minimal local control surface so the operator can exercise and inspect intake outcomes outside the test suite.

This phase must expose `judge_intake(...)` for real local use.

It must **not** add HTTP transport.
It must **not** add planner behavior.
It must **not** perform decomposition.
It must **not** create internal tasks.

This is a **feature-hardening phase**.

Its purpose is to make the new intake judgment layer operationally usable while preserving its current bounded role as judgment-only architecture.

---

## Why This Phase Exists

Phase 56 added the first executable intake judgment surface.

That was the correct first implementation step.

But right now that surface exists only as importable code plus tests.

That leaves a practical gap:
- the operator cannot yet exercise intake judgment through a normal control surface
- the system cannot yet demonstrate intake outcomes in the same visible way it demonstrates other bounded behaviors
- the project still lacks a real inspection path for the new front-door layer

This phase closes that gap in the smallest possible way.

---

## Problems This Phase Must Solve

### Problem 1: Intake Judgment Exists But Is Not Yet Operationally Exposed

A service function and tests are not enough.

If intake judgment is going to become part of the real governing layer, the operator needs a bounded way to invoke it and inspect its output.

This phase should add that surface.

---

### Problem 2: The First Exposure Must Not Smuggle In More Than Judgment

The danger here is obvious:
once intake becomes user-invocable, the implementation may be tempted to:
- decompose work
- enqueue tasks
- infer plans
- mutate run/task state
- or quietly turn a judgment surface into an orchestration surface

This phase must not allow that.

It should expose judgment only.

---

## Scope Of This Phase

This phase should add one minimal local invocation surface for intake judgment.

A minimal acceptable implementation may include:

1. one new CLI command such as:
   - `intake-judge`
2. one small wrapper around the existing `judge_intake(...)` service
3. simple operator-readable output of the structured intake outcome
4. small tests validating:
   - correct invocation
   - correct output shape
   - no hidden state mutation

Choose the smallest implementation that makes intake judgment operationally usable without widening into decomposition or transport.

---

## This Phase Is NOT About

- decomposition
- task creation
- planner behavior
- task tree generation
- HTTP or REST endpoints
- API server work
- GUI work
- automatic run creation
- recommendation changes
- verification changes
- connector implementation
- multi-turn intake policy
- input persistence
- storing intake history
- background jobs

This phase is about one thing only:

**make intake judgment callable and inspectable through a local control surface.**

---

## Required Capability

The system should gain one bounded local control surface for the existing intake judgment function.

Preferred direction:
- a new CLI command

Conceptual shape:

```bash
python main.py intake-judge <input>
```

This phase does not require that exact argument style, but it does require a small operator-usable invocation path.

A good minimal shape would accept either:
- a JSON file path
or
- a JSON payload string

Prefer the smallest clear approach.

If supporting both broadens the phase, choose one.

Preferred default:
- input via JSON file path

That keeps the surface explicit and easy to inspect.

---

## Required Behavior

The control surface must:

1. invoke the existing service-level intake judgment surface
2. return the structured outcome faithfully
3. avoid mutating runs, tasks, artifacts, verifier results, or recommendations
4. remain local-only
5. preserve the ratified intake outcome semantics

The output should make visible:
- `outcome`
- `decomposition_permitted`
- `human_explanation`
- `next_action`
- `clarification_request` when present
- `blocked_reason` when present

Do not collapse the output into vague prose only.

The operator should be able to inspect the real structured judgment result.

---

## Files To Modify

Modify only the minimum files required.

Likely candidates:
- `main.py`
- `orchestrator/intake.py` only if a tiny interface helper is truly needed
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Modify additional files only if clearly necessary.

Do NOT thread the intake result into execution or decomposition yet.

---

## Design Rules

1. Keep `judge_intake(...)` as the real source of judgment.
2. Make the new control surface a thin adapter, not a second implementation.
3. Keep the input format explicit and inspectable.
4. Keep the output structured and operator-legible.
5. Do not mutate orchestration state.
6. Do not let the CLI exposure become a hidden orchestration surface.
7. Preserve one governing semantics between service function and control surface.

This phase should prove operational exposure, not expand intake scope.

---

## Preferred Input Shape

If using file-based input, a minimal invocation could look conceptually like:

```json
{
  "objective_text": "...",
  "provided_artifacts": [],
  "confirmed_context": {},
  "available_capabilities": []
}
```

This should align with the bounded intake input shape established in the ratified intake design artifacts and implemented in Phase 56.

Do not broaden this into a large intake schema.

---

## Required Output Preservation

The CLI/control surface must preserve the service result faithfully.

That means:
- no remapping of outcome meanings
- no hidden defaults that change control semantics
- no extra inferred fields that make the result look more certain than it is
- no interface-specific alternate meaning for `proceed`, `clarify`, or `blocked`

This phase must reinforce the one-governing-layer principle.

---

## Validation Requirements

This phase must validate at least these cases:

### Test A: Proceed through local control surface
Use a small valid intake input.

Expected:
- command succeeds
- structured output shows:
  - `outcome = proceed`
  - `decomposition_permitted = true`
  - `next_action = begin_decomposition`

### Test B: Clarify through local control surface
Use a small intake input that triggers the bounded clarify rule family.

Expected:
- command succeeds
- structured output shows:
  - `outcome = clarify`
  - `decomposition_permitted = false`
  - `clarification_request` present

### Test C: Blocked through local control surface
Use a small intake input that triggers a bounded blocked rule family.

Expected:
- command succeeds
- structured output shows:
  - `outcome = blocked`
  - `decomposition_permitted = false`
  - `blocked_reason` present

### Test D: No hidden state mutation
Confirm that invoking the local control surface:
- creates no tasks
- creates no runs
- creates no artifacts
- creates no verifier results
- creates no recommendations
- does not mutate workspace/run state

### Test E: Service/control-surface semantic parity
Confirm that the CLI/local control surface returns the same core semantics as direct `judge_intake(...)` invocation for the same input.

This matters because the control surface must remain a thin adapter.

---

## Success Criteria

- the repo gains one minimal local control surface for intake judgment
- the surface is a thin adapter over the existing service function
- the operator can inspect structured intake outcomes outside tests
- no decomposition occurs
- no internal tasks are created
- no run/task/artifact/recommendation state is mutated
- intake semantics remain identical between service layer and local control surface
- docs reflect the completed phase

---

## End Of Phase

STOP after completion.

Then:

1. Summarize:
   - what local intake control surface was added
   - which files were created or modified

2. Report:
   - how input is supplied
   - how output is rendered/preserved
   - how semantic parity with `judge_intake(...)` was validated
   - how hidden state mutation was ruled out
   - what validation was performed
   - any assumptions or uncertainties

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
