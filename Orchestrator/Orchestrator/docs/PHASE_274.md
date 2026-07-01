# Phase 274 - Operator-Facing Bounded Coding Task Packet

## Boundary

`PRODUCT_PHASE_274_OPERATOR_FACING_BOUNDED_CODING_TASK_PACKET_SOURCE_TEST_DOCS_WORKER`

## Purpose

Phase 274 implements a narrow operator-facing bounded coding-task packet
surface for the next success bar defined by Phase 273.

The packet surface accepts a structured operator-provided bounded coding task
specification, validates named file scope and explicit success criteria, runs
the task through deterministic local `local_file` behavior, and returns
current-success review/readback with operator-visible next action evidence.

## Files Changed

Source:

- `orchestrator/operator_coding_task_packet.py`

Tests:

- `tests/test_phase_274_operator_facing_bounded_coding_task_packet.py`

Docs:

- `docs/PHASE_274.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Behavior

The Phase 274 packet surface:

- requires a JSON-object packet
- requires `packet_id`, `run_id`, `task_id`, `title`, `files_in_scope`,
  `success_criteria`, and `expected_output`
- defaults to `filesystem_mutation` and `local_file`
- allows only deterministic `local_file` behavior
- rejects empty scope, empty success criteria, absolute paths, parent
  traversal, unsupported providers, and provider/model/runtime/platform
  requests before task persistence
- saves a task, executes it through the existing engine, reloads the completed
  task, and calls `review_current_success_task_result`
- returns current-success review, response surface, operator next action,
  caveat flags, and non-proofs

## Validation

Validation passed:

- `python -m py_compile orchestrator/operator_coding_task_packet.py tests/test_phase_274_operator_facing_bounded_coding_task_packet.py`
- `python -m unittest tests.test_phase_274_operator_facing_bounded_coding_task_packet -v`
- `python -m unittest tests.test_phase_78_current_success_result_review tests.test_phase_91_provider_status_routing tests.test_phase_92_verification_provenance tests.test_phase_95_task_execution_policy_classification tests.test_phase_97_model_backed_patch_proposal_protocol tests.test_phase_98_patch_proposal_operator_apply_authorization_gate tests.test_phase_99_bounded_patch_apply_engine_for_operator_authorized_proposals tests.test_phase_100_patch_apply_result_verification_and_task_completion_gate tests.test_phase_101_verified_patch_apply_task_completion_finalization_gate tests.test_phase_272_integrated_coding_task_current_spine_proof tests.test_phase_274_operator_facing_bounded_coding_task_packet -v`
- `git diff --check`

The targeted current-spine regression with Phase 274 ran 102 tests with one
symlink-environment skip and passed.

## Non-Proofs

Phase 274 does not prove or add:

- semantic correctness
- live provider/model behavior
- runtime/platform behavior
- autonomous AI coding behavior
- production readiness
- model-backed generation
- `general_answer` resumption
- service/API/UI behavior
- export/upload
- commit or push

## Marker

`PHASE274_OPERATOR_FACING_BOUNDED_CODING_TASK_PACKET_SOURCE_TEST_DOCS_PROVEN=PASS`
