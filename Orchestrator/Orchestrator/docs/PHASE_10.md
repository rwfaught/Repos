# PHASE_10.md

## Phase 10: Output Adequacy Assessment + Reviewer Routing

---

## Goal

Introduce a minimal output adequacy layer so the system can distinguish between:

- successful execution
- successful verification
- meaningful task fulfillment

This phase must allow the system to detect when a provider returned output that is structurally present but not adequate for the task.

When output is clearly inadequate, the system should:

- mark the original task as `needs_review`
- create a separate reviewer task
- preserve traceable links between the original task, its artifact, and the reviewer task

This phase is about controlled semantic gating, not deep intelligence.

---

## Problems This Phase Must Solve

### Problem 1: Output Can Be Technically Successful but Practically Inadequate

Current behavior allows this outcome:

- provider execution returns `status = "success"`
- verification passes
- output is weak, deflective, or not meaningfully responsive
- task is marked `completed`

This is insufficient.

The system must be able to say:
- execution succeeded
- verification succeeded
- output still needs review

---

### Problem 2: Reviewer Role Exists but Is Not Yet Used as a Routing Target

The system already has:
- reviewer role modules
- reviewer prompt assets

But it does not yet create reviewer tasks when a result is inadequate.

This phase should make reviewer routing operational in a minimal, explicit way.

---

## Files to Modify

- orchestrator/task_schema.py
- orchestrator/run_manager.py
- orchestrator/engine.py
- orchestrator/artifact_store.py (only if needed for traceability metadata)
- docs/ACTION_LOG.md

---

## Optional New File (Recommended)

- orchestrator/adequacy.py

If created, this file should contain the output adequacy evaluator and related helper logic.

This is recommended because it keeps adequacy logic separate from the main execution loop.

---

## Task Schema Change

Extend the task schema with one optional field:

- `expected_output`

This should be a plain string.

Examples:
- `"concise review"`
- `"bounded implementation response"`
- `"patch suggestion"`

Do NOT introduce:
- enums
- output taxonomies
- schema registries
- large nested output specifications

Keep this field small and human-readable.

---

## New Task Status

Add one new task status:

- `needs_review`

Use this only when:
- execution succeeded
- verification passed
- output adequacy failed

Do NOT use it for:
- provider failures
- verification failures

---

## Core Behavior Change

After provider execution and verification succeed, the system must evaluate output adequacy.

### Rule 1: Execution Failure Still Wins

If provider result has:
- `status == "error"`

Then:
- task status = `execution_failed`

Do NOT perform adequacy routing for execution errors.

---

### Rule 2: Verification Failure Still Wins After Successful Execution

If provider result has:
- `status == "success"`

and verification fails, then:
- task status = `verification_failed`

Do NOT perform adequacy routing when verification already failed.

---

### Rule 3: Adequacy Check Runs Only After Successful Execution and Successful Verification

Only if:
- execution status = `success`
- verification passed

Then:
- evaluate output adequacy

If output is adequate:
- task status = `completed`

If output is inadequate:
- task status = `needs_review`
- create a reviewer task

---

## Adequacy Evaluation Rules

The adequacy evaluator must be deterministic and conservative.

It should check for clear signs of inadequacy only.

### Required checks

The evaluator should mark output inadequate if one or more of the following are true:

1. Output is missing
   - `None`
   - empty string
   - whitespace only

2. Output is clearly deflective
   Examples:
   - asks the user to provide files or context that should already be available
   - says it cannot proceed without basic information the task already includes

3. Output is trivially short relative to the expected task
   Use a simple conservative heuristic only.
   Do NOT overfit this.

4. Output obviously does not match the `expected_output` field, if provided

The evaluator must return:
- `is_adequate`
- `reason`

Keep this simple and explicit.

---

## Reviewer Task Creation

If adequacy fails, the system must create a separate reviewer task.

Do NOT mutate the original task into a reviewer task.

The reviewer task should include at least:

- new task ID
- same run ID
- role = `reviewer`
- status = `queued`
- title indicating it is a review of the original task
- dependency on the original task
- reference to the original task ID
- reference to the source artifact ID
- short reason for review routing
- `expected_output` appropriate for reviewer behavior

The original task should remain as the historical execution attempt.

This traceability is important.

---

## Reviewer Task Scope

The reviewer task is not a repair task yet.

Its purpose is to:
- inspect the output artifact
- assess why adequacy failed
- recommend next action

Do NOT implement:
- automatic repair
- retry loops
- recursive reviewer routing
- file writeback

Reviewer routing in this phase is single-step only.

---

## orchestrator/adequacy.py (pseudocode)

If created, this module may include:

function assess_output_adequacy(task, provider_result):
    output = provider_result["output"]
    expected_output = task.expected_output

    apply simple deterministic checks

    return {
        "is_adequate": bool,
        "reason": str
    }

Keep this module:
- small
- explicit
- testable

Do NOT add scoring systems.

---

## orchestrator/engine.py Changes

Update the execution flow so that after:
- dispatch
- artifact creation
- verification

the engine performs adequacy assessment only if:
- execution succeeded
- verification passed

Then:

- adequate output => `completed`
- inadequate output => `needs_review` + reviewer task created

Summary output should clearly show:
- provider
- execution status
- verification result
- adequacy result
- final task status
- reviewer task ID if created

---

## run_manager.py Changes

Add whatever minimal helper is needed to save reviewer tasks cleanly.

Do NOT redesign run/task persistence.

---

## task_schema.py Changes

Add optional `expected_output`.

If needed, also add optional traceability fields for reviewer routing, such as:
- `source_task_id`
- `source_artifact_id`
- `review_reason`

Only add fields that are clearly needed.

Do NOT over-expand the schema.

---

## Constraints

- Keep this phase tightly scoped
- Do NOT redesign provider abstraction
- Do NOT redesign verification logic
- Do NOT add retries
- Do NOT add repair loops
- Do NOT add writeback
- Do NOT add recursive reviewer routing
- Do NOT add fuzzy scoring or confidence systems
- Do NOT add complex expected-output schemas

This phase is about minimal semantic adequacy routing.

---

## Validation Requirements

This phase must be validated with at least these cases:

### Test A: Adequate Output
Use mock provider or a bounded provider output that clearly satisfies the task.

Expected:
- execution success
- verification pass
- adequacy pass
- final status = `completed`

### Test B: Inadequate Output
Use a task/provider combination that returns weak or deflective output.

Expected:
- execution success
- verification pass
- adequacy fail
- original task status = `needs_review`
- reviewer task created

### Test C: Execution Failure Still Bypasses Adequacy
Use unknown provider or forced provider error.

Expected:
- final status = `execution_failed`
- no reviewer task created from adequacy logic

### Test D: Verification Failure Still Bypasses Adequacy
Use mock provider with missing file in scope.

Expected:
- final status = `verification_failed`
- no reviewer task created from adequacy logic

---

## Success Criteria

- `expected_output` is added cleanly
- adequacy evaluator exists and is deterministic
- `needs_review` status is used correctly
- reviewer task is created when adequacy fails
- original task remains preserved
- reviewer task links back to original task and artifact
- execution and verification failure semantics remain intact
- no architectural drift is introduced

---

## End of Phase

STOP after completion.

Then:

1. Summarize:
   - what was implemented
   - which files were modified

2. Report:
   - how adequacy is determined
   - how reviewer tasks are created
   - what validation was performed

3. Append a concise entry to:
   docs/ACTION_LOG.md

4. Do NOT proceed further