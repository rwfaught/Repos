# Phase 72 - Case-Packet Created Task Execution Candidate Surfacing

## Purpose

Phase 72 defines the read-only execution-candidate surface for tasks created by the Phase 71 case-packet task creation write gate.

It follows Phase 71 task creation and comes before any later case-packet task execution boundary.

This phase exists to keep these states separate:

- persisted case packet
- task-candidate review
- task-creation authorization
- task creation
- execution candidacy
- task execution

Phase 72 may surface a Phase 71-created queued task as an execution candidate.

Phase 72 must not execute that task.

## Phase Boundary

This phase defines a read-only visibility and eligibility surface.

It may:

- inspect persisted product tasks
- identify tasks created by Phase 71
- verify that candidate tasks are queued
- verify that candidate tasks preserve bounded file scope
- verify that candidate tasks preserve case-packet traceability
- return an operator-legible candidate list
- explain why no candidate is available

It must not:

- create tasks
- mutate tasks
- confirm tasks
- execute tasks
- invoke planner behavior
- invoke verifier behavior
- invoke reviewer behavior
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

## Candidate Detection Rules

A task may be surfaced as a Phase 72 candidate only if all of the following are true:

1. The task exists in the product task store.
2. The task status is `queued`.
3. The task role is compatible with normal product task execution.
4. The task was created by Phase 71 or preserves an equivalent narrow case-packet trace.
5. The task has a source artifact identity that points to a case packet path or case identity.
6. The task has bounded files in scope.
7. The task has objective or success-criteria text.
8. The task has no execution artifact.
9. The task is not recommendation-created work.
10. The task does not imply planner, reviewer, verifier, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, cleanup, deletion, archive, oz, Codex, or execution behavior.

A conservative implementation should prefer excluding uncertain tasks over surfacing ambiguous tasks.

## Output Shape

A future implementation should return an operator-legible result containing at least:

- `case_packet_task_execution_candidate_surface`
- `run_id`
- `candidate_count`
- `candidates`
- `excluded_count`
- `reason`
- `detail`
- `next_action`

Each candidate should include at least:

- `task_id`
- `task_path`
- `run_id`
- `title`
- `status`
- `role`
- `files_in_scope`
- `success_criteria`
- `expected_output`
- `source_artifact_id`
- `source_case_packet_identity`
- `execution_candidate_status`

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

## Empty And Blocked Conditions

The surface should return zero candidates without mutation if:

- no Phase 71-created queued task exists
- the requested run has no Phase 71-created queued task
- candidate tasks are already executed or in progress
- candidate tasks lack bounded file scope
- candidate tasks lack case-packet traceability
- candidate tasks appear recommendation-created rather than case-packet-created
- candidate tasks imply broad or ambiguous file scope
- candidate tasks imply bundled execution or platform behavior

## Relationship To Existing Execution Surfaces

This phase does not change generic `next` behavior.

This phase does not change recommendation-derived execution candidate behavior.

This phase does not replace Phase 24 or Phase 25.

Phase 24 and Phase 25 concern recommendation-created ready tasks.

Phase 72 concerns tasks created from the Phase 71 case-packet task creation write gate.

A later phase may define explicit execution for a selected Phase 72 candidate, but Phase 72 itself is read-only.

## Expected Implementation Surface

A later implementation boundary may add one or more of:

- `orchestrator/case_packet_task_execution_candidate_surface.py`
- a CLI command such as `case-packet-task-execution-candidates`
- tests for valid Phase 71 candidate surfacing
- tests proving recommendation-created tasks are excluded
- tests proving non-queued tasks are excluded
- tests proving ambiguous or broad file surfaces are excluded
- regression tests proving no planner, reviewer, verifier, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, execution, cleanup, deletion, archive, oz, or Codex behavior occurs

Likely target files for implementation, not authorized by this definition boundary:

- `orchestrator/case_packet_task_execution_candidate_surface.py`
- `main.py`
- `tests/test_phase_72_case_packet_task_execution_candidate_surface.py`
- `docs/PHASE_72.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`

## Acceptance Criteria

A successful implementation of this phase should prove:

1. A valid Phase 71-created queued task is surfaced as a case-packet execution candidate.
2. The surfaced candidate preserves case-packet traceability.
3. The surfaced candidate preserves bounded file scope.
4. A non-queued Phase 71 task is excluded.
5. A recommendation-created task is excluded.
6. A generic queued task without Phase 71 or case-packet traceability is excluded.
7. A candidate with broad or ambiguous file scope is excluded.
8. The output is deterministic and operator-legible.
9. The implementation does not create or mutate tasks.
10. The implementation does not execute tasks.
11. The implementation does not invoke planner, reviewer, verifier, runtime, model, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, cleanup, deletion, archive, oz, or Codex behavior.

## Boundary Discipline

This phase definition does not itself implement execution-candidate surfacing.

This phase definition does not authorize:

- product source mutation beyond this docs-only definition boundary
- task creation
- task mutation
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

Phase 72 is defined as the case-packet created task execution candidate surfacing phase.

Implementation has been performed, locally tested, exported, uploaded, and ZIP-verified under the Phase 72 implementation artifact.

PHASE_72_DEFINED_CASE_PACKET_CREATED_TASK_EXECUTION_CANDIDATE_SURFACING
## Implementation Status

Phase 72 is implemented by:

- `orchestrator/case_packet_task_execution_candidate_surface.py`
- `tests/test_phase_72_case_packet_task_execution_candidate_surface.py`
- `python main.py case-packet-task-execution-candidates [--run <run_id>]`

The implementation surfaces queued Phase 71 case-packet-created tasks as explicit execution candidates.

It remains read-only. It does not create tasks, mutate tasks, execute tasks, invoke planner/reviewer/verifier/runtime/model/platform behavior, touch OpenClaw, Discord, bridge, adapter, installer, WSL, A18CF, vendoring, cleanup, deletion, archive, oz, or Codex.

Marker:

PHASE_72_IMPLEMENTED_CASE_PACKET_CREATED_TASK_EXECUTION_CANDIDATE_SURFACING
## Upload Verification

Phase 72 implementation was uploaded and verified from the product ZIP artifact.

Verified uploaded artifact:

- SHA256: e6d0569d5dadd1af860fba5a7cce0c9a4747bb49366167e9ae861f51c1a82959
- Required Phase 72 source entry: present exactly once.
- Required Phase 72 test entry: present exactly once.
- Required Phase 72 doc and ledger entries: present exactly once.
- Phase 72 unit test: passed.
- Phase 64-72 regression: passed.
- ZIP hygiene: passed.
- Text integrity: passed.

Marker:

PHASE_72_UPLOADED_VERIFIED_CASE_PACKET_CREATED_TASK_EXECUTION_CANDIDATE_SURFACING
