# Phase 71 — Authorized Case-Packet Task Creation Write Gate

## Purpose

Phase 71 defines the first product-side task-creation write gate in the case-packet track.

It follows Phase 70 operator task-creation authorization and creates exactly one bounded task only when an explicit Phase 70 `task_creation_authorized` result is provided.

This phase exists to keep the distinction sharp between:

- a persisted case packet
- a task-candidate review
- operator authorization
- actual task creation
- task execution

Phase 71 may create a task record.

Phase 71 must not execute that task.

## Phase Boundary

This phase defines a write gate.

It may:

- inspect a Phase 70 task-creation authorization result
- verify that the authorization is explicit and valid
- derive a bounded task payload from the authorized candidate summary
- create exactly one queued task record in the product task store
- return a deterministic task-creation result
- preserve source case-packet and authorization traceability

It must not:

- invoke planner behavior
- execute the created task
- run verifier behavior
- run reviewer behavior
- call runtime providers
- call models
- perform platform integration
- touch OpenClaw
- touch Discord
- touch bridge or adapter behavior
- run installer behavior
- use WSL
- perform A18CF work
- vendor dependencies
- clean up, delete, or archive files
- run oz
- use Codex

## Required Input

A valid Phase 71 implementation should accept a Phase 70 result, or an explicit wrapper containing a Phase 70 result.

The Phase 70 result must show:

- `case_packet_task_creation_authorization=true`
- `task_creation_authorization=task_creation_authorized`
- `task_creation_authorized=true`
- `task_created=false`
- `planner_invoked=false`
- `runtime_executed=false`
- `model_executed=false`
- `platform_invoked=false`
- `mutation_performed=false`
- `execution_performed=false`

The Phase 70 result must preserve:

- `case_id`
- `case_packet_path`
- `candidate_summary`
- `source_case_packet_summary`
- `phase69_review_summary`
- explicit operator decision text

## Task Creation Rules

Phase 71 may create exactly one task if all of the following are true:

1. The input is a valid Phase 70 task-creation authorization result.
2. The authorization status is `task_creation_authorized`.
3. The authorization result does not imply a task was already created.
4. The authorization result does not imply planner, runtime, model, platform, bridge, adapter, installer, WSL, OpenClaw, Discord, A18CF, mutation, or execution behavior.
5. The candidate summary contains objective text or a bounded task description.
6. The candidate summary contains a bounded file surface.
7. The source case-packet summary is inspectable.
8. The implementation can create one queued task without inventing operator intent.
9. The output remains explicit that execution has not occurred.

## Expected Created Task Shape

A created task should be a normal product task record compatible with the existing task schema.

A future implementation should prefer existing task primitives unless a narrow helper is required.

The task should include:

- generated task id
- run id or a deliberate case-packet task run binding
- title derived from the authorized case-packet candidate
- role selected by deterministic product rule, not planner behavior
- status `queued`
- dependencies empty unless explicitly supplied by the authorized candidate
- success criteria derived from the authorized candidate or bounded default
- files in scope from the candidate bounded file surface
- expected output derived from the candidate if available
- source case-packet identity
- source authorization traceability
- retry count zero

If the existing task schema cannot preserve all desired traceability, the implementation must choose the smallest compatible traceability surface and document the limitation instead of broadening the schema casually.

## Output Shape

A future implementation should return an operator-legible result containing at least:

- `case_packet_task_creation_write_gate`
- `case_id`
- `case_packet_path`
- `task_creation_status`
- `task_created`
- `task_id`
- `task_path`
- `reason`
- `detail`
- `blocked_conditions`
- `missing_requirements`
- `created_task_summary`
- `source_authorization_summary`
- `next_action`

The output must explicitly state:

- `planner_invoked=false`
- `runtime_executed=false`
- `model_executed=false`
- `platform_invoked=false`
- `openclaw_invoked=false`
- `discord_invoked=false`
- `bridge_invoked=false`
- `adapter_invoked=false`
- `execution_performed=false`

## Blocked Conditions

The write gate must return `blocked` and create no task if:

- Phase 70 authorization is missing
- input is not a Phase 70 authorization result
- authorization is not `task_creation_authorized`
- authorization implies a task already exists
- authorization implies planner invocation
- authorization implies runtime/model/platform behavior
- authorization implies OpenClaw, Discord, bridge, adapter, installer, WSL, or A18CF behavior
- authorization or operator request bundles task creation with execution
- candidate summary lacks objective text
- candidate summary lacks bounded file surface
- task creation would require inventing missing operator intent
- the requested file surface is unbounded, such as whole repo or wildcard-only scope

## Relationship To Existing Task Creation Surfaces

This phase does not redesign recommendation-derived task creation.

This phase does not change execution routing.

This phase defines the narrow case-packet-backed task creation write gate after Phase 70 only.

A future implementation may reuse existing task schema and task persistence primitives, but must not reuse any behavior that silently executes, plans, verifies, reviews, or mutates beyond the single task record.

## Expected Implementation Surface

A later implementation boundary may add one or more of:

- a narrow source module such as `orchestrator/case_packet_task_creation_write_gate.py`
- a CLI command such as `case-packet-task-create-authorized`
- deterministic tests for created / blocked / duplicate-safe outcomes
- regression tests proving exactly one task is created on valid authorization
- regression tests proving no task is created on blocked inputs
- regression tests proving no planner, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, verifier, reviewer, execution, cleanup, deletion, archive, oz, or Codex behavior occurs

Likely target files for implementation, not authorized by this definition boundary:

- `orchestrator/case_packet_task_creation_write_gate.py`
- `main.py`
- `tests/test_phase_71_task_creation_write_gate.py`
- `docs/PHASE_71.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`

## Acceptance Criteria

A successful implementation of this phase should prove:

1. A valid Phase 70 `task_creation_authorized` result creates exactly one queued task.
2. The created task has bounded files in scope.
3. The created task preserves case-packet and authorization traceability.
4. A missing Phase 70 authorization result is blocked.
5. A non-authorized Phase 70 result is blocked.
6. Inputs implying prior task creation are blocked.
7. Inputs implying planner, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, verifier, reviewer, execution, cleanup, deletion, archive, oz, or Codex behavior are blocked.
8. The implementation does not execute the created task.
9. The implementation does not invoke planner behavior.
10. The implementation does not run runtime or model behavior.
11. The implementation does not mutate platform state.
12. The result is deterministic and operator-legible.

## Boundary Discipline

This phase definition does not itself implement task creation.

This phase definition does not authorize:

- product source mutation beyond this docs-only definition boundary
- task execution
- planner output
- verifier execution
- reviewer execution
- runtime execution
- model execution
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

## Definition Status

Phase 71 is defined as the authorized case-packet task creation write gate.

Implementation is not yet performed.

PHASE_71_DEFINED_AUTHORIZED_CASE_PACKET_TASK_CREATION_WRITE_GATE


## Implementation Status

Status: Implemented / locally tested.

Implementation marker:

PHASE_71_IMPLEMENTED_AUTHORIZED_CASE_PACKET_TASK_CREATION_WRITE_GATE

Implemented surface:

- `orchestrator/case_packet_task_creation_write_gate.py`
- `tests/test_phase_71_task_creation_write_gate.py`
- `main.py` command: `case-packet-task-create-authorized`

Implementation summary:

Phase 71 creates exactly one queued task from an explicit Phase 70 `task_creation_authorized` result. It blocks missing, unauthorized, broad, or bundled inputs. It does not invoke planner, reviewer, verifier, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, cleanup, deletion, archive, oz, Codex, or execution behavior.

Validation:

- `python -m unittest tests.test_phase_71_task_creation_write_gate`
