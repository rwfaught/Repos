# PHASE_56.md

## Phase 56: Minimal Service-Level Intake Judgment Surface

---

## Goal

Implement the first bounded intake judgment surface as a small service-level function that accepts a structured intake input and returns one of the already-ratified intake outcomes:

- `proceed`
- `clarify`
- `blocked`

This phase must implement intake judgment only.

It must **not** perform decomposition.
It must **not** create internal tasks.
It must **not** introduce planner behavior.
It must **not** expose HTTP or API transport.

This is a **feature-hardening phase**.

Its purpose is to create the first honest executable front-door judgment layer while preserving the existing bounded execution core and the ratified intake design stack.

---

## Why This Phase Exists

The intake design staircase is now complete enough to support small implementation work:

- `INTAKE_TRIAGE_DESIGN_01_REVISED.md`
  - established constitutional intake meanings
- `INTAKE_TRIAGE_DESIGN_02.md`
  - established machine-readable outcome shapes
- `INTAKE_TRIAGE_DESIGN_03.md`
  - established input shape and evidence-source rules
- `INTAKE_TRIAGE_DESIGN_04.md`
  - established the handoff-to-decomposition boundary

That means the next step is no longer more intake theory.

The next step is to implement the smallest possible intake judgment surface that proves the design can exist in code without collapsing into hidden planning or speculative decomposition.

---

## Problems This Phase Must Solve

### Problem 1: Intake Judgment Is Ratified In Design But Does Not Yet Exist As Executable Logic

The project now has intake rules in documents, but no minimal executable surface that enforces them.

That leaves a gap between ratified principle and actual architecture.

This phase should close that gap with the smallest honest implementation.

---

### Problem 2: The First Intake Implementation Must Not Drift Into Planner Behavior

The biggest danger in first implementation is overreach.

If the first intake surface:
- decomposes work
- creates tasks
- invents plans
- or smuggles hidden workflow commitments across the boundary

then it violates the entire intake design stack.

This phase must stay strictly judgment-only.

---

## Scope Of This Phase

This phase should implement a small service-level intake judgment function and the minimum supporting structures needed for it to return machine-readable intake outcomes.

A minimal acceptable implementation may include:

1. a new small module under `orchestrator/`, such as:
   - `orchestrator/intake.py`
2. one primary function, such as:
   - `judge_intake(...)`
3. one structured input shape
4. one structured output shape matching the ratified intake outcomes
5. focused tests covering:
   - `proceed`
   - `clarify`
   - `blocked`

Choose the smallest implementation that makes intake judgment real without widening into decomposition or transport.

---

## This Phase Is NOT About

- decomposition
- task creation
- planner logic
- automatic task trees
- service/server transport
- HTTP routes
- CLI exposure unless a tiny local inspection hook is strictly necessary
- connector implementation
- full capability modeling
- long-term memory
- multi-turn dialogue policy
- confidence scoring
- downstream role assignment
- recommendation policy changes
- verification changes
- run selection changes

This phase is about one thing only:

**given bounded intake input, return honest intake judgment.**

---

## Required Capability

The system should gain one service-level intake judgment surface.

A conceptual minimal shape is:

```python
judge_intake(intake_input: dict) -> dict
```

This phase does not require those exact names, but it does require the following behavior:

- consume a small structured intake input
- judge only from:
  - explicit request evidence
  - confirmed context/evidence
  - available capabilities
- return one of:
  - `proceed`
  - `clarify`
  - `blocked`
- include:
  - `decomposition_permitted`
  - `human_explanation`
  - `next_action`
  - `clarification_request` when relevant
  - `blocked_reason` when relevant

The returned shape should follow the design logic ratified in Intake Designs 01–04.

---

## Required Input Surface

The intake input should remain small.

A minimal acceptable conceptual shape should include equivalents of:

- `objective_text`
- `provided_artifacts`
- `confirmed_context`
- `available_capabilities`

You may refine exact field names if needed, but keep the input shape minimal and close to the ratified design.

This phase must **not** introduce a large ontology or complex nested capability model.

---

## Required Judgment Rules

This phase must implement only a very small bounded rule set sufficient to prove the intake architecture.

At minimum:

### Rule A: Proceed
Return `proceed` only when:
- `objective_text` is present and non-empty
- no bounded clarification is required by the implemented rule surface
- no confirmed blocked condition is present under the implemented rule surface

### Rule B: Clarify
Return `clarify` when:
- the objective is plausibly actionable
- but a required interpretive distinction is missing
- and the issue is request-side ambiguity, not environmental blockage

### Rule C: Blocked
Return `blocked` when:
- the obstacle is environmental/capability/evidence-based
- and decomposition would be dishonest until that condition changes

### Rule D: No inferred assumptions may authorize proceed
Unconfirmed inference may support clarification wording.
It may not authorize decomposition.

### Rule E: No non-proceed outcome may create hidden internal work
This phase must not create tasks, plans, drafts, or task-like internal structures.

---

## Preferred Bounded Rule Surface

To keep the first implementation honest and small, use a narrow rule surface.

A good minimal shape would be:

### Proceed baseline
- objective present
- no required source-form ambiguity under current implemented rule set
- no explicit blocked condition in confirmed context/capabilities

### Clarify baseline
Return `clarify` when the request clearly depends on a missing source/input distinction, for example:
- source data form not specified
- requested output form not specified where it materially changes downstream work

### Blocked baseline
Return `blocked` when confirmed context or available capabilities explicitly show absence of a required condition, for example:
- required connector unavailable
- required permission unavailable
- required provided artifact absent despite being necessary under the bounded implemented rule set

Keep these rule families small.
Do NOT try to solve general intake intelligence in this phase.

---

## Files To Modify

Modify only the minimum files required.

Likely candidates:
- create `orchestrator/intake.py`
- possibly a very small supporting type/helper module if truly needed
- targeted tests under `tests/`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Modify additional files only if clearly necessary.

Avoid touching:
- `orchestrator/engine.py`
- `main.py`
unless a very small local inspection hook is strictly necessary and clearly justified.

Do NOT thread intake into execution yet.

---

## Design Rules

1. Keep the intake judgment surface service-level and importable.
2. Keep the input shape small.
3. Keep the output shape aligned with the ratified intake artifacts.
4. Keep the implemented rule set intentionally narrow.
5. Preserve explicit separation between:
   - judgment
   - decomposition
   - execution
6. Prefer exact explicit conditions over heuristic ambition.
7. Do not let the first implementation become a shadow planner.

This phase should prove the architecture can exist in code, not attempt to complete the product.

---

## Source Of Truth

Judgment must be grounded only in:
- explicit request input
- confirmed context
- available capabilities

This phase must not silently treat:
- implication as confirmation
- mentioned artifacts as provided artifacts
- theoretical capability as current availability
- stale context as current evidence

That discipline is essential.

---

## Validation Requirements

This phase must validate at least these cases:

### Test A: Proceed
Use a small intake input where:
- objective is present
- required current evidence is present
- no blocked condition exists
- no clarification rule is triggered

Expected:
- `outcome = proceed`
- `decomposition_permitted = true`
- `next_action = begin_decomposition`

### Test B: Clarify
Use a small intake input where:
- objective is plausibly actionable
- but a required interpretive distinction is missing under the implemented rule set

Expected:
- `outcome = clarify`
- `decomposition_permitted = false`
- `clarification_request` present
- no task/decomposition artifact created

### Test C: Blocked
Use a small intake input where:
- objective is understandable enough
- but confirmed context/capabilities show a real environmental obstacle

Expected:
- `outcome = blocked`
- `decomposition_permitted = false`
- `blocked_reason` present
- no task/decomposition artifact created

### Test D: Inference cannot authorize proceed
Use a case where:
- objective could be guessed into a workflow
- but required current evidence is not confirmed

Expected:
- not `proceed`
- likely `clarify` or `blocked` depending on the bounded rule family
- explanation reflects uncertainty honestly

### Test E: Non-proceed outcomes do not create hidden internal work
Confirm:
- no task records created
- no decomposition artifacts created
- no run/task state mutated

This phase must remain judgment-only.

---

## Success Criteria

- the repo gains one importable intake judgment surface
- it returns structured `proceed` / `clarify` / `blocked` results
- it follows the ratified intake design stack closely
- it remains service-level, not transport-level
- it performs no decomposition
- it creates no internal tasks
- targeted tests prove honest behavior across the bounded outcome set
- docs reflect the completed phase

---

## End Of Phase

STOP after completion.

Then:

1. Summarize:
   - what intake judgment surface was added
   - which files were created or modified

2. Report:
   - what bounded rule set was implemented
   - how the output shape aligns with the intake design artifacts
   - how non-proceed outcomes were prevented from creating hidden work
   - what validation was performed
   - any assumptions or uncertainties

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
