# PHASE_69.md

## Title

Persisted Case-Packet Task Candidate Review Surface

## Purpose

Phase 69 defines the product-side read-only review surface after Phase 68 authorized case-packet persistence.

Phase 68 may persist a case packet.

Phase 69 does not create a task.

Phase 69 reviews whether a persisted case packet is sufficiently bounded, inspectable, and operator-legible to become a candidate for a later explicit task-creation authorization boundary.

This phase is the membrane between durable case-packet state and any later task surface.

## Problem Statement

A persisted case packet is not a task.

A persisted case packet may contain enough structured intent to support a bounded task candidate, but persistence alone must not imply:

- task creation
- planner invocation
- runtime execution
- model execution
- platform integration
- OpenClaw behavior
- bridge or adapter behavior

Without a separate review surface, the system would blur these states:

- case packet exists
- case packet is usable
- task candidate is ready
- task creation is authorized
- task is created
- task is executed

That blur would turn inspectable state into action pressure.

Phase 69 exists to prevent that.

## Phase Boundary

This phase defines a read-only case-packet task-candidate review surface only.

It may inspect a persisted case packet and classify whether the packet is eligible for a later operator-controlled task-creation authorization boundary.

This phase does not authorize:

- task creation
- planner output
- execution runs
- verifier runs
- reviewer runs
- runtime calls
- model calls
- platform integration
- OpenClaw integration
- bridge behavior
- adapter behavior
- installer work
- WSL work
- Discord work
- A18CF
- vendoring
- cleanup
- deletion
- archive
- export
- oz
- Codex

## Intended Behavior

A future implementation of this phase should accept a persisted case packet, or an explicit reference to one, and produce a deterministic review result.

The review result should classify the packet as one of:

- `task_candidate_ready`
- `needs_operator_clarification`
- `blocked`

The review should be conservative.

A case packet should be `task_candidate_ready` only when the system can identify a bounded, operator-legible task candidate without inventing missing scope.

## Readiness Requirements

A persisted case packet may be classified as `task_candidate_ready` only if all of the following are true:

1. The case packet exists in the product case-packet store.
2. The case packet validates under current case-packet rules.
3. The case packet has objective text.
4. The case packet has source intake linkage.
5. The case packet has inspectable Phase 65, Phase 66, Phase 67, and Phase 68 provenance where available.
6. The case packet does not claim that a task already exists.
7. The case packet does not claim that planner behavior has already occurred.
8. The case packet does not require runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, A18CF, vendoring, cleanup, deletion, archive, oz, or Codex behavior.
9. The candidate task surface can be described without broad repo-scale mutation.
10. The next action remains operator authorization, not automatic task creation.

## Needs-Clarification Conditions

The review should classify the result as `needs_operator_clarification` if:

- the objective is understandable but not yet bounded enough for a task candidate
- the likely files in scope are missing or ambiguous
- success criteria are missing or ambiguous
- the operator must choose between multiple plausible bounded task candidates
- the case packet is valid but its next action is unclear
- the packet needs human narrowing before any task-creation authorization boundary

## Blocked Conditions

The review should classify the result as `blocked` if:

- the case packet does not exist
- the case packet is invalid
- the input is not a persisted Phase 68 case packet or equivalent valid product case-packet record
- the packet implies task creation already happened
- the packet implies planner invocation already happened
- the packet implies runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, or A18CF behavior
- the requested next move bundles candidate review with task creation or execution
- the requested next move expands into vendoring, cleanup, deletion, archive, oz, Codex, or platform mutation
- the packet cannot be narrowed without inventing operator intent

## Output Shape

A future implementation should return an operator-legible result containing at least:

- `case_packet_task_candidate_review`
- `case_id`
- `case_packet_path`
- `task_candidate_status`
- `reason`
- `detail`
- `missing_requirements`
- `blocked_conditions`
- `candidate_summary`
- `source_case_packet_summary`
- `next_action`

If ready, the candidate summary may include:

- objective text
- likely bounded task description
- declared or inferred file surface, with inference clearly labeled
- success criteria if present
- explicit non-authorizations

The output must not include a created task id.

## Operator Control Principle

The case packet is a ledger entry.

The Phase 69 review result is a candidate judgment.

Neither is authorization to create a task.

The next boundary after this phase, if justified, should be an explicit operator task-creation authorization gate.

## Expected Implementation Surface

A later implementation boundary may add one or more of:

- a pure function for persisted case-packet task-candidate review
- a CLI command such as `case-packet-task-candidate-review`
- regression tests for ready / needs-clarification / blocked outcomes
- regression tests proving no task, planner, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, or WSL behavior occurs
- regression tests proving the review is read-only

That later implementation boundary must identify exact target files before mutation.

## Acceptance Criteria

A successful implementation of this phase should prove:

1. A valid persisted Phase 68 case packet can be reviewed without mutation.
2. A sufficiently bounded valid case packet can be classified as `task_candidate_ready`.
3. An under-specified valid case packet is classified as `needs_operator_clarification`.
4. An invalid or missing case packet is classified as `blocked`.
5. Any input implying task creation is classified as `blocked`.
6. Any input implying planner invocation is classified as `blocked`.
7. Any input implying runtime, model, platform, Discord, OpenClaw, bridge, adapter, installer, or WSL behavior is classified as `blocked`.
8. The review does not create tasks.
9. The review does not invoke planner behavior.
10. The review does not execute runtime or model behavior.
11. The review result is deterministic and operator-legible.
12. The review result points to operator authorization as the next action, not automatic task creation.

## Boundary Discipline

This phase does not authorize:

- task creation
- planner output
- platform repo mutation
- installer execution
- WSL execution
- model pull
- model run
- Discord execution
- OpenClaw integration
- bridge execution
- adapter execution
- A18CF
- vendoring
- cleanup
- deletion
- archive
- oz
- Codex

## Expected Next Boundary

After this phase is defined and ratified, the next likely boundary is product implementation of the persisted case-packet task-candidate review surface.

That implementation boundary should be read-only except for product source/test/doc edits required to add the review function, CLI surface, and tests.

No task creation should be implemented until a later explicit operator task-creation authorization phase is defined and ratified.

## Definition Status

Phase 69 is defined as the read-only persisted case-packet task-candidate review surface.

Implementation is implemented, locally tested, exported, uploaded, and coordinator-verified.

PHASE_69_DEFINED_PERSISTED_CASE_PACKET_TASK_CANDIDATE_REVIEW_SURFACE


PHASE_69_IMPLEMENTED_PERSISTED_CASE_PACKET_TASK_CANDIDATE_REVIEW_SURFACE


PHASE_69_REPAIRED_AFTER_ABORTED_SOURCE_PATCH_AND_FALSE_DOC_LEDGER

A prior Phase 69 implementation attempt aborted before source/test creation because the patch script incorrectly required the new test file to pre-exist. A docs-only continuation then prematurely recorded implementation/local-test status. This marker supersedes that premature ledger state. Current Phase 69 implementation status is valid only after the repaired source/test/main patch and Phase 64-69 unit tests pass in this repair boundary.


PHASE_69_UPLOADED_ARTIFACT_VERIFIED

- Timestamp: 2026-06-11T19:47:11-05:00
- Verified implementation artifact SHA256: ab48f7b74bc7314fc14d0c4233d8c2795c1ccce80770ed8a24c6d77ac285efc3
- Verified implementation artifact size bytes: 673687
- Verified implementation artifact entry count: 643
- Verification result: uploaded product ZIP matched the locally exported Phase 69 implementation artifact and preserved required Phase 69 source/test/doc entries.
- Hygiene result: generated workspace JSON = 0; real log payload = 0; pyc/pyo/cache = 0; host metadata = 0.
- Caveat: the artifact verified here recorded export/upload verification as pending because coordinator upload verification occurred after that export. This docs-ratification boundary closes that ledger loop.
