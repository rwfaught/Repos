# Phase 77 - Current Success Criterion Demonstration Plan

## Purpose

Phase 77 defines the demonstration plan for proving the current success criterion on one small bounded operator-provided coding task.

This phase is a planning and definition boundary only.

It does not execute the demonstration.

It does not mutate tasks.

It does not invoke providers.

It does not run models.

It does not run verifiers.

It does not run reviewers.

It does not call runtime, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, A18CF, vendoring, cleanup, deletion, archive, oz, or Codex behavior.

The purpose is to define exactly what a later explicit demonstration boundary must prove.

## Source Context

The current success criterion states that the system should demonstrate:

a bounded operator-provided coding task executed through the orchestration system such that the run produces a persisted, inspectable, minimally verified result with clear outcome classification and no ambiguity about what happened.

The Phase 64-76 milestone review recorded that the case-packet governance staircase is substantially built, but the current success criterion is not yet live-proven by a real bounded task run.

## Phase 77 Boundary

Phase 77 may define:

- the demonstration task shape
- acceptable file scope
- required preconditions
- required proof artifacts
- expected persisted task state
- expected persisted execution artifact
- expected deterministic verifier result
- expected outcome classification
- expected operator-visible next-step surface
- disallowed shortcuts
- later boundary requirements

Phase 77 may not perform:

- live task execution
- task mutation
- artifact creation
- provider execution
- model execution
- verifier execution
- reviewer execution
- runtime calls
- platform calls
- OpenClaw calls
- Discord calls
- bridge behavior
- adapter behavior
- installer work
- WSL work
- A18CF
- vendoring
- cleanup
- deletion
- archive
- oz
- Codex

## Demonstration Task Shape

The later demonstration should use a small bounded coding task that is easy to inspect.

The task should be operator-provided and should include:

- one clear objective
- one file or a very small related file surface
- explicit success criteria
- expected output
- named files in scope before execution
- no broad repository mutation
- no autonomous decomposition
- no unattended multi-step loop

Recommended demonstration task class:

- add or modify one tiny pure-Python function
- add or adjust one tiny deterministic unit test
- avoid external services
- avoid runtime/model/platform integrations
- avoid broad refactors
- avoid installer behavior
- avoid cleanup/deletion/archive behavior

## Required Demonstration Proof

A later demonstration boundary should prove all of the following.

### 1. Operator-Provided Task Framing

The input should show that the operator provided the bounded coding task.

Required proof:

- task objective
- files in scope
- success criteria
- expected output
- explicit boundary authorization

### 2. Persisted Task State

The system should persist task state before and after execution.

Required proof:

- task id
- task path
- initial status
- final status
- status transition reason
- source traceability

### 3. Persisted Execution Artifact

The system should emit a persisted execution artifact.

Required proof:

- artifact id
- artifact path
- artifact content summary
- link from task state to artifact id
- no ambiguity about what was produced

### 4. Deterministic Verification Result

The system should run and persist deterministic verification.

Required proof:

- verifier result path or artifact id
- exact deterministic checks run
- pass/fail status
- no overclaim that deterministic checks prove semantic correctness
- clear caveat if verification is syntax/tripwire only

### 5. Clear Outcome Classification

The final state should classify the result.

Required classification should distinguish at least:

- completed / acceptable current-state success
- execution failure
- verification failure
- review/recommendation state, if review is involved

### 6. Operator-Visible Next-Step Surface

The result should expose what the operator can do next.

Required proof:

- result review or response-option surface
- clear distinction between suggested next action and authorized next action
- no hidden follow-up creation
- no automatic repair chain

## Demonstration Success Criteria

The later demonstration succeeds only if the operator can answer these questions from the produced records without reconstructing scattered internals manually:

1. What task was run?
2. What file or files were in scope?
3. What changed or what output was produced?
4. Where is the persisted task state?
5. Where is the persisted execution artifact?
6. What deterministic verification ran?
7. What did verification prove and not prove?
8. What is the final outcome classification?
9. What is the next operator-visible option?
10. What was not authorized or not performed?

## Demonstration Failure Conditions

The later demonstration fails if:

- task state is missing
- artifact state is missing
- deterministic verification is missing
- final outcome classification is ambiguous
- provider/runtime/model behavior is implied but not explicitly authorized
- the task mutates files outside scope
- the result requires manual reconstruction from scattered implementation details
- recommendation or response surfaces blur suggestion, authorization, and execution
- verification overclaims semantic correctness
- any hidden autonomous follow-up occurs

## Relationship To Phase 64-76

Phase 64-76 built the governance staircase.

Phase 77 defines how to test whether that staircase can satisfy the current success criterion on one real bounded task.

Phase 77 is not another governance membrane for its own sake.

It is a preparation boundary for a concrete demonstration.

## Expected Later Boundary

After Phase 77 is uploaded and verified, the next likely boundary is a read-only preflight for the demonstration task.

That preflight should identify:

- the exact demonstration task
- the exact file scope
- whether provider execution is authorized
- whether verifier execution is authorized
- whether reviewer behavior is authorized
- what mutations are allowed
- what artifacts must be collected
- what proof must be pasted back by the operator

The actual demonstration must not begin without a separate explicit runtime/provider/verifier/mutation authorization boundary.

## Definition Status

Phase 77 is defined as the current success criterion demonstration plan.

Implementation is not applicable in this phase because Phase 77 is a plan-definition boundary, not a source-code behavior boundary.

PHASE_77_DEFINED_CURRENT_SUCCESS_CRITERION_DEMONSTRATION_PLAN