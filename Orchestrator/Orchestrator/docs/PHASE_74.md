# Phase 74 - Authorized Case-Packet Task Execution Boundary

## Purpose

Phase 74 defines the explicit execution boundary after Phase 73 operator case-packet task execution authorization.

Phase 72 surfaces queued Phase 71-created tasks as case-packet task execution candidates.

Phase 73 records explicit operator authorization for later execution of exactly one selected Phase 72 candidate.

Phase 74 defines the later boundary where one Phase 73-authorized case-packet task may actually be executed.

This phase definition does not implement execution.

This phase definition does not execute any task.

## Problem Statement

The product now distinguishes these states:

- a queued case-packet-created task exists
- the task is surfaced as a Phase 72 execution candidate
- the operator selects one candidate
- Phase 73 records explicit operator execution authorization
- a later boundary executes exactly that authorized task

Phase 74 exists to define that later execution boundary without collapsing authorization into execution.

Execution must remain narrower than candidacy and narrower than authorization.

Authorization says: this selected task may be executed later.

Execution says: this selected authorized task was actually run, produced an artifact or outcome, and mutated task/run state according to explicit rules.

Those are different states and must remain inspectable.

## Phase Boundary

Phase 74 is the authorized case-packet task execution boundary.

A future implementation may execute exactly one task only if all of the following are true:

1. A Phase 73 authorization result is provided.
2. The Phase 73 result has `case_packet_task_execution_authorization_gate=true`.
3. The Phase 73 result has `task_execution_authorization=task_execution_authorized`.
4. The Phase 73 result has `task_execution_authorized=true`.
5. The Phase 73 result states `task_executed=false` and `execution_performed=false`.
6. The selected task id is present.
7. The selected task path is present.
8. The selected candidate summary preserves queued task status from the Phase 72 candidate.
9. The selected candidate summary preserves bounded file scope.
10. The selected candidate summary preserves case-packet traceability.
11. The selected candidate summary preserves success criteria and expected output.
12. The execution request does not expand the authorized scope.
13. The execution request does not bundle unrelated platform, OpenClaw, Discord, bridge, adapter, installer, WSL, A18CF, vendoring, cleanup, deletion, archive, oz, or Codex behavior.
14. The boundary is explicitly authorized as an execution boundary.

## Non-Authorizations

This phase definition does not authorize or perform:

- task execution in this docs-only boundary
- runtime execution in this docs-only boundary
- model execution in this docs-only boundary
- provider execution in this docs-only boundary
- planner execution in this docs-only boundary
- reviewer execution in this docs-only boundary
- verifier execution in this docs-only boundary
- platform repo mutation
- OpenClaw integration
- Discord integration
- bridge execution
- adapter execution
- installer execution
- WSL execution
- A18CF
- vendoring
- cleanup
- deletion
- archive
- oz
- Codex

## Intended Future Behavior

A future implementation should accept a Phase 73 authorization result and execute only the selected authorized task.

The implementation should be deterministic and operator-legible.

The implementation should produce a result that preserves:

- run id
- task id
- task path
- task title
- task role
- bounded file scope
- case-packet traceability
- source artifact identity
- Phase 72 candidate identity
- Phase 73 authorization identity
- execution start/end classification
- artifact path or explicit no-artifact outcome
- verifier/reviewer status if applicable and explicitly authorized
- task status transition
- next action

The implementation must not silently select a different task.

The implementation must not execute multiple tasks.

The implementation must not execute from a mere Phase 72 candidate without Phase 73 authorization.

The implementation must not treat ambiguous authorization as authorization.

## Expected Output Shape

A future implementation should return an operator-legible result containing at least:

- `authorized_case_packet_task_execution_boundary`
- `run_id`
- `task_id`
- `task_path`
- `task_execution_status`
- `task_executed`
- `execution_performed`
- `artifact_path`
- `reason`
- `detail`
- `blocked_conditions`
- `missing_requirements`
- `source_authorization_summary`
- `selected_candidate_summary`
- `next_action`

Possible execution classifications:

- `executed`
- `needs_operator_decision`
- `blocked`
- `execution_failed`

## Blocked Conditions

A future implementation should return `blocked` if:

- the Phase 73 authorization result is missing
- the Phase 73 authorization result is malformed
- the Phase 73 authorization result is not authorized
- the Phase 73 authorization result is ambiguous
- the selected task is missing
- the selected task path is missing
- the selected task does not match the authorization result
- the task is no longer queued at execution time
- bounded file scope is missing
- case-packet traceability is missing
- success criteria are missing
- expected output is missing
- the request expands beyond the Phase 73 authorized task
- the request attempts platform/OpenClaw/Discord/bridge/adapter/installer/WSL work
- the request attempts A18CF, vendoring, cleanup, deletion, archive, oz, or Codex behavior
- the request attempts to execute more than one task
- the request attempts to bypass the Phase 73 authorization gate

## Relationship To Existing Execution Surfaces

Phase 74 concerns tasks created from the case-packet staircase:

case packet -> task candidate -> creation authorization -> task creation -> execution candidacy -> execution authorization -> execution

It does not replace generic `next`.

It does not replace Phase 24 ready-execution candidate surfacing.

It does not replace Phase 25 recommendation-created ready-candidate execution.

It defines a case-packet-specific execution boundary for Phase 71-created tasks that have passed Phase 72 and Phase 73.

## Expected Implementation Surface

A later implementation boundary may add one or more of:

- `orchestrator/authorized_case_packet_task_execution.py`
- a CLI command such as `case-packet-task-execute-authorized`
- tests for executed, blocked, needs-decision, and execution-failed classifications
- tests proving Phase 73 authorization is required
- tests proving Phase 72 candidacy alone is insufficient
- tests proving task identity cannot change between authorization and execution
- tests proving scope expansion is blocked
- tests proving no platform/OpenClaw/Discord/bridge/adapter/installer/WSL behavior occurs

Likely target files for implementation, not authorized by this definition boundary:

- `orchestrator/authorized_case_packet_task_execution.py`
- `main.py`
- `tests/test_phase_74_authorized_case_packet_task_execution.py`
- `docs/PHASE_74.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`

## Acceptance Criteria

A successful future implementation should prove:

1. A valid Phase 73 authorization result can execute exactly one matching queued task.
2. A missing Phase 73 authorization result is blocked.
3. A non-authorized Phase 73 result is blocked.
4. A Phase 72 candidate without Phase 73 authorization is blocked.
5. A selected task mismatch is blocked.
6. A non-queued selected task is blocked.
7. Missing bounded file scope is blocked.
8. Missing case-packet traceability is blocked.
9. Scope expansion is blocked.
10. Multiple-task execution is blocked.
11. Platform/OpenClaw/Discord/bridge/adapter/installer/WSL requests are blocked.
12. A18CF, vendoring, cleanup, deletion, archive, oz, or Codex requests are blocked.
13. Execution result is persisted or explicitly classified as no-artifact/failure.
14. Task status transition is inspectable.
15. The result includes a clear next action for the operator.

## Boundary Discipline

This phase definition is docs-only.

It does not implement execution.

It does not run execution.

It does not run runtime, model, provider, planner, reviewer, verifier, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, A18CF, vendoring, cleanup, deletion, archive, oz, or Codex behavior.

Actual implementation belongs to a later explicit implementation boundary.

Actual live task execution, if ever performed, requires a separately explicit execution/runtime boundary.

## Expected Next Boundary

After Phase 74 definition, export, upload, and verification, the next likely boundary is implementation of the Phase 74 authorized case-packet task execution surface.

That implementation boundary should still avoid live runtime/model/platform execution unless explicitly authorized.

## Definition Status

Phase 74 is defined as the authorized case-packet task execution boundary.

Implementation is implemented and locally verified.

Implemented surface:

- `orchestrator/authorized_case_packet_task_execution.py`
- `python main.py case-packet-task-execute-authorized <phase73_authorization_json_path>`

Implementation preserves Phase 74 as a local authorized case-packet task execution surface. It can execute exactly one matching queued task from a clean Phase 73 authorization result by creating a deterministic local artifact and transitioning the task to completed.

Implementation blocks missing authorization, non-authorized Phase 73 results, Phase 72 candidacy without Phase 73 authorization, selected-task mismatch, non-queued tasks, missing bounded file scope, missing case-packet traceability, scope expansion, multi-task execution, and platform/runtime/model/provider requests.

Implementation does not invoke runtime, model, provider, planner, reviewer, verifier, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, A18CF, vendoring, cleanup, deletion, archive, oz, or Codex behavior.

PHASE_74_DEFINED_AUTHORIZED_CASE_PACKET_TASK_EXECUTION_BOUNDARY

PHASE_74_IMPLEMENTED_AUTHORIZED_CASE_PACKET_TASK_EXECUTION_SURFACE

## Phase 93 Supersession Note

Phase 93 supersedes the synthetic-completion portion of the Phase 74 implementation.

A valid Phase 73 authorization no longer creates a local success artifact, sets `execution_artifact_id`, or transitions a queued task through `in_progress` to `completed` when no real execution occurred. The command now returns `needs_operator_decision`, leaves the task queued, and requires a later explicit real execution boundary.

All Phase 74 blocked-condition behavior remains preserved.
