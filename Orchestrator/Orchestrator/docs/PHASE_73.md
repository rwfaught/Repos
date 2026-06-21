# Phase 73 - Operator Case-Packet Task Execution Authorization Gate

## Purpose

Phase 73 defines the explicit operator authorization gate after Phase 72 case-packet task execution-candidate surfacing.

Phase 71 may create a queued bounded task from an authorized case-packet task-creation decision.

Phase 72 may surface that queued task as an execution candidate.

Phase 73 does not execute the task.

Phase 73 records whether the operator has explicitly authorized execution of one selected Phase 72 case-packet task execution candidate.

This phase is the consent membrane between execution candidacy and any later actual execution boundary.

## Problem Statement

An execution candidate is not an executed task.

A Phase 72 candidate means the task is visible, queued, bounded, traceable to a case packet, and eligible for operator execution consideration.

It does not mean:

- the task should run automatically
- a provider should be selected automatically
- verifier or reviewer behavior should run
- runtime or model execution is authorized
- platform, OpenClaw, Discord, bridge, adapter, installer, WSL, A18CF, vendoring, cleanup, deletion, archive, oz, or Codex behavior is authorized

Without a separate operator execution authorization gate, the product would blur these states:

- queued case-packet-created task exists
- queued task is surfaced as an execution candidate
- operator selects a candidate
- operator authorizes execution
- task is executed

That blur would turn visibility into action pressure.

Phase 73 exists to prevent that.

## Phase Boundary

This phase defines authorization semantics only.

It may inspect a Phase 72 execution-candidate surface and classify whether explicit operator task-execution authorization has been given for one selected candidate.

This phase does not authorize or perform:

- task execution
- task mutation
- execution artifact creation
- planner output
- verifier runs
- reviewer runs
- runtime calls
- model calls
- provider calls
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

A future implementation of this phase should accept a Phase 72 candidate surface, or an equivalent explicit candidate object, plus an operator decision.

The authorization result should classify the decision as one of:

- `task_execution_authorized`
- `needs_operator_decision`
- `blocked`

The authorization result should preserve:

- run id
- selected task id
- selected task path
- selected task title
- selected task status
- selected task role
- bounded file scope
- success criteria
- expected output
- source artifact identity
- source case-packet identity
- Phase 72 execution-candidate status
- explicit operator decision text
- non-execution status until a later execution boundary actually runs the task

This phase should not itself execute the task unless a later boundary explicitly authorizes that implementation.

## Authorization Requirements

A selected candidate may only become execution-authorized if all of the following are true:

1. The input derives from a Phase 72 case-packet task execution-candidate surface.
2. The Phase 72 surface has `case_packet_task_execution_candidate_surface=true`.
3. The selected task appears exactly once in the Phase 72 `candidates` list.
4. The selected candidate has `execution_candidate_status=case_packet_task_execution_candidate`.
5. The selected candidate status is `queued`.
6. The selected candidate preserves bounded file scope.
7. The selected candidate preserves case-packet traceability.
8. The selected candidate preserves objective or success-criteria text.
9. The Phase 72 result confirms:
   - `task_created=false`
   - `task_mutated=false`
   - `task_executed=false`
   - `planner_invoked=false`
   - `runtime_executed=false`
   - `model_executed=false`
   - `platform_invoked=false`
   - `openclaw_invoked=false`
   - `discord_invoked=false`
   - `bridge_invoked=false`
   - `adapter_invoked=false`
   - `verifier_invoked=false`
   - `reviewer_invoked=false`
   - `execution_performed=false`
10. The operator explicitly authorizes execution of that selected candidate.
11. The authorization request does not bundle authorization with execution.
12. The authorization output still states that execution has not occurred in this phase.

## Needs-Decision Conditions

A selected candidate should be classified as `needs_operator_decision` if:

- the Phase 72 candidate is valid, but no explicit operator execution decision is provided
- the operator decision text is ambiguous
- the operator asks for more inspection before execution
- the operator selects no task
- the operator selection is unclear but appears repairable by a narrower selection

## Blocked Conditions

A selected candidate should be classified as `blocked` if:

- the input is not a Phase 72 candidate surface
- the Phase 72 surface is missing
- the selected task is absent from the Phase 72 candidate list
- more than one selected task is provided
- the selected task is not queued
- the selected task lacks bounded file scope
- the selected task lacks case-packet traceability
- the selected task lacks objective or success-criteria text
- the Phase 72 result implies task creation, task mutation, task execution, planner invocation, verifier execution, reviewer execution, runtime/model/platform execution, OpenClaw, Discord, bridge, adapter, installer, WSL, cleanup, deletion, archive, oz, Codex, or other execution behavior
- the operator request attempts to bypass the explicit execution authorization gate
- the operator request bundles authorization with execution
- the operator request expands into unrelated platform/OpenClaw/bridge/adapter/installer/WSL behavior

## Output Shape

A future implementation should return an operator-legible result containing at least:

- `case_packet_task_execution_authorization_gate`
- `run_id`
- `task_id`
- `task_path`
- `task_execution_authorization`
- `task_execution_authorized`
- `reason`
- `detail`
- `blocked_conditions`
- `missing_requirements`
- `selected_candidate_summary`
- `source_candidate_surface_summary`
- `operator_decision`
- `next_action`

The output must explicitly state:

- `task_created=false`
- `task_mutated=false`
- `task_executed=false`
- `planner_invoked=false`
- `runtime_executed=false`
- `model_executed=false`
- `platform_invoked=false`
- `openclaw_invoked=false`
- `discord_invoked=false`
- `bridge_invoked=false`
- `adapter_invoked=false`
- `verifier_invoked=false`
- `reviewer_invoked=false`
- `execution_performed=false`

## Relationship To Existing Execution Surfaces

This phase does not change generic `next` behavior.

This phase does not change recommendation-derived execution candidate behavior.

This phase does not replace Phase 24 or Phase 25.

Phase 24 and Phase 25 concern recommendation-created ready tasks.

Phase 73 concerns tasks created from the Phase 71 case-packet task creation write gate and surfaced by Phase 72.

A later phase may define explicit execution for a selected Phase 73-authorized case-packet task, but Phase 73 itself is read-only and authorization-only.

## Expected Implementation Surface

A later implementation boundary may add one or more of:

- `orchestrator/case_packet_task_execution_authorization.py`
- a CLI command such as `case-packet-task-execution-authorize`
- tests for authorized, needs-decision, and blocked classifications
- tests proving a valid Phase 72 selected candidate can become execution-authorized
- tests proving missing, ambiguous, non-queued, non-traceable, and bundled execution requests are blocked
- regression tests proving no task creation, task mutation, task execution, planner, reviewer, verifier, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, cleanup, deletion, archive, oz, or Codex behavior occurs

Likely target files for implementation, not authorized by this definition boundary:

- `orchestrator/case_packet_task_execution_authorization.py`
- `main.py`
- `tests/test_phase_73_case_packet_task_execution_authorization.py`
- `docs/PHASE_73.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`

## Acceptance Criteria

A successful implementation of this phase should prove:

1. A valid Phase 72 candidate plus explicit operator approval can be classified as `task_execution_authorized`.
2. A valid Phase 72 candidate without explicit operator approval is classified as `needs_operator_decision`.
3. A missing Phase 72 candidate surface is classified as `blocked`.
4. An absent selected candidate is classified as `blocked`.
5. A non-queued selected task is classified as `blocked`.
6. A selected task lacking bounded file scope is classified as `blocked`.
7. A selected task lacking case-packet traceability is classified as `blocked`.
8. Any input implying task creation, task mutation, task execution, planner invocation, verifier execution, reviewer execution, runtime, model, platform, Discord, OpenClaw, bridge, adapter, installer, WSL, cleanup, deletion, archive, oz, or Codex behavior is classified as `blocked`.
9. Any request bundling authorization with execution is classified as `blocked`.
10. The authorization check does not create a task.
11. The authorization check does not mutate a task.
12. The authorization check does not execute a task.
13. The authorization result is deterministic and operator-legible.
14. The authorization result points to a later explicit case-packet task execution boundary, not automatic task execution.

## Boundary Discipline

This phase definition does not itself implement task execution authorization.

This phase definition does not authorize:

- product source mutation beyond this docs-only definition boundary
- task execution
- task mutation
- execution artifact creation
- planner output
- verifier execution
- reviewer execution
- runtime execution
- model execution
- provider execution
- platform repo mutation
- installer execution
- WSL execution
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

After Phase 73 definition, export, upload, and verification, the next product boundary should implement the Phase 73 operator case-packet task execution authorization gate.

That implementation boundary should remain read-only and authorization-only.

It should not execute tasks.

Actual execution of a selected Phase 73-authorized task belongs to a later explicit execution boundary.

## Definition Status

Phase 73 is defined as the operator case-packet task execution authorization gate.

Implementation is implemented and locally verified.

Implemented surface:

- `orchestrator/case_packet_task_execution_authorization.py`
- `python main.py case-packet-task-execution-authorize <phase72_candidate_surface_or_authorization_json_path>`

Implementation preserves Phase 73 as authorization-only. It can classify one selected Phase 72 candidate as `task_execution_authorized`, `needs_operator_decision`, or `blocked`.

Implementation does not create tasks, mutate tasks, execute tasks, create execution artifacts, invoke planner, reviewer, verifier, runtime, model, provider, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, cleanup, deletion, archive, oz, or Codex behavior.

PHASE_73_DEFINED_OPERATOR_CASE_PACKET_TASK_EXECUTION_AUTHORIZATION_GATE

PHASE_73_IMPLEMENTED_OPERATOR_CASE_PACKET_TASK_EXECUTION_AUTHORIZATION_GATE