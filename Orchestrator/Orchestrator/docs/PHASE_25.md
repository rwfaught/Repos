# PHASE_25.md

## Phase 25: Explicit Ready-Candidate Execution

---

## Goal

Add a bounded, explicitly operator-triggered bridge from ready execution-candidate surfacing to actual task execution.

This phase should allow the operator to:

- select one ready execution candidate by task ID
- execute that task through the existing execution flow
- preserve the distinction between explicit execution and ordinary queue behavior
- keep all behavior deterministic, minimal, and inspectable

This phase is about explicit execution of a selected ready candidate, not automatic execution.

It is NOT yet about:
- changes to `next`
- queue reordering
- automatic selection of ready tasks
- batch execution
- routing based on readiness
- automatic execution after confirmation
- broader scheduler redesign

---

## Problems This Phase Must Solve

### Problem 1: Ready Execution Candidates Exist but Cannot Yet Be Explicitly Acted On

The system can now surface ready execution candidates, but the operator still cannot directly tell the system:

- execute this ready candidate now

This phase should create that explicit bridge.

---

### Problem 2: Execution Must Remain Human-Triggered Before It Becomes Policy-Driven

Before any future phase considers queue-policy changes or execution behavior tied to readiness, the system must first support explicit one-task execution of a selected ready candidate.

This phase must not change ordinary queue behavior.

---

## Files to Modify

- `main.py`
- `orchestrator/engine.py` (only if a minimal explicit single-task execution entrypoint is needed)
- `orchestrator/run_manager.py` (only if candidate validation helper reuse is needed)
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`

Do NOT redesign task execution flow broadly.
Do NOT redesign provider or verifier behavior.
Do NOT redesign readiness semantics.

---

## Core Behavior

Add a bounded CLI command:

`python main.py execute-ready-candidate --task <task_id>`

Required behavior:

- operator must explicitly provide:
  - task ID

The command must:

1. load the specified task
2. verify that the task is a valid ready execution candidate:
   - recommendation-created
   - ready under existing Phase 23 semantics
   - `status == "queued"`
3. execute that specific task through the existing execution path
4. persist all normal execution results
5. print a clear summary

If the task is not found:
- print a clear message
- do not execute anything

If the task is not a valid ready execution candidate:
- print a clear message
- do not execute anything

Do NOT fall back to:
- first ready task
- active run next task
- any implicit selection behavior

The task ID must be authoritative.

---

## Execution Rules

Execution must:

- reuse the existing execution machinery as much as possible
- preserve artifact creation
- preserve verification behavior
- preserve outcome classification behavior
- preserve recommendation-created task traceability fields unless the normal execution flow changes them explicitly

Do NOT:
- auto-confirm tasks
- auto-create tasks
- auto-run multiple tasks
- change task selection semantics for `next`
- introduce special execution rules beyond explicit eligibility validation

---

## Output Requirements

On successful execution, print at least:

- task ID
- title
- role
- provider used
- execution status
- verification status
- final task status

On failure to qualify, print clear messages for:
- task not found
- task not ready
- task not recommendation-created
- task not queued

Do NOT:
- emit raw JSON
- imply that other ready candidates were considered
- modify unrelated tasks

---

## Constraints

- Keep this phase tightly scoped
- Do NOT change ordinary `next` behavior
- Do NOT introduce queue prioritization
- Do NOT execute multiple tasks
- Do NOT introduce hidden routing behavior
- Do NOT redesign persistence or schema broadly

This phase is explicit one-task execution only.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Execute Valid Ready Candidate

Expected:
- specified task executes through normal flow
- artifact and verification behavior remain intact
- final status reflects actual execution outcome

---

### Test B: Reject Non-Ready Recommendation-Created Task

Expected:
- clear message
- no execution occurs

---

### Test C: Reject Ordinary Queued Task

Expected:
- clear message
- no execution occurs

---

### Test D: Reject Missing Task ID

Expected:
- clear not-found message
- no execution occurs

---

### Test E: No Ordinary Queue Behavior Change

Expected:
- `next` behavior remains unchanged
- no implicit ready-candidate selection is introduced

---

## Success Criteria

- a bounded explicit-ready-candidate execution command exists
- only explicitly selected valid ready queued recommendation-created tasks can be executed through this path
- ordinary `next` behavior remains unchanged
- no automatic or hidden execution behavior is introduced
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were created or modified

2. Report:
   - how ready-candidate validation works
   - how explicit execution works
   - what validation was performed

3. Append a concise entry to:
   `docs/ACTION_LOG.md`

4. Update:
   `docs/PHASE_INDEX.md`

5. Do NOT proceed further
