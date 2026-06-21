# Phase 97 - Model-Backed Patch Proposal Protocol

Status: LOCALLY SOURCE/TEST/DOCS-PROVEN; EXPORT/UPLOAD NOT PERFORMED

Marker: `PHASE97_MODEL_BACKED_PATCH_PROPOSAL_PROTOCOL_LOCAL_SOURCE_TEST_PROVEN=PASS`

## Purpose

Phase 97 defines a non-executing patch proposal artifact and persistence protocol for bounded filesystem-mutation tasks.

This is the bridge design between report-only model output and a future mutation-capable workflow. It is not the mutation bridge itself: Phase 97 does not invoke a model, apply a patch, mutate a task target, or authorize autonomous writeback.

## Changed Behavior

- A filesystem-mutation task can produce a stored `patch_proposal` artifact without entering the engine execution lifecycle.
- Proposal records preserve proposal, task, optional run, execution-policy, bounded file-scope, proposed-change, unified-diff, rationale, risk, validation, source, and creation-time fields.
- Proposal records explicitly set `requires_operator_apply=true`, `applied=false`, `completion_proof=false`, and `causal_change_satisfied=false`.
- Proposal records state that execution, provider, model, and runtime activity did not occur.
- Task-declared scope, proposed-change paths, and paths named by unified-diff headers use the Phase 94 bounded relative-path policy.
- Absolute paths, parent traversal, paths outside `PROJECT_ROOT`, and proposal paths outside task `files_in_scope` are rejected.
- Proposal creation does not persist or mutate the task, attach an execution artifact, or change task status.
- Completed tasks cannot receive a new proposal through this protocol.
- `report_only` tasks are deterministically rejected as policy-incompatible.
- No engine or provider integration was added. The normal engine cannot treat this standalone proposal artifact as execution or completion proof.

## Source Files

- `orchestrator/patch_proposal.py`

## Tests

- `tests/test_phase_97_model_backed_patch_proposal_protocol.py`
- `tests/test_phase_96_canonical_case_packet_execution_delegation.py`
- `tests/test_phase_95_task_execution_policy_classification.py`
- `tests/test_phase_94_path_and_record_identity_containment.py`
- `tests/test_phase_92_verification_provenance.py`
- `tests/test_phase_91_provider_status_routing.py`

## Proof Commands

`python3 -m py_compile orchestrator/patch_proposal.py tests/test_phase_97_model_backed_patch_proposal_protocol.py`

`python3 -m unittest tests.test_phase_97_model_backed_patch_proposal_protocol tests.test_phase_96_canonical_case_packet_execution_delegation tests.test_phase_95_task_execution_policy_classification tests.test_phase_94_path_and_record_identity_containment tests.test_phase_92_verification_provenance tests.test_phase_91_provider_status_routing`

Recorded result:

`Ran 42 tests in 3.580s`

`OK`

## Phase 96 External Verification Reconciliation

Coordinator-side export and uploaded verification accepted the Phase 96 product ZIP:

- `PHASE96_PRODUCT_ZIP_EXPORT_VERIFY_RESULT=PASS`
- `PHASE96_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS`
- SHA-256 `15366CE13B66471EA9C4C4860169D85A75729498260B77584A8B958E75A1C728`

That final artifact hash proof is external to the source files later exported. Phase 97 does not claim that source files prove their own final exported hash.

## Caveats

- The source field can identify a manual or future model proposal, but Phase 97 does not prove a live model produced any proposal.
- Unified-diff text is stored and path-bounded; it is not applied or semantically validated as a complete patch.
- A later explicit operator apply or separately authorized execution boundary is still required.
- Proposal evidence cannot satisfy Phase 92 causal-change proof.

## Explicit Non-Proofs

Phase 97 does not execute a task, provider, model, runtime, verifier, reviewer, planner, platform, OpenClaw, Discord, bridge, adapter, installer, WSL, or Ollama. It does not apply patches, mutate source targets, complete tasks, add autonomous writeback, export, package, clean up, delete, archive, prove semantic correctness, or establish production readiness.

`PHASE97_MODEL_BACKED_PATCH_PROPOSAL_PROTOCOL_LOCAL_SOURCE_TEST_PROVEN=PASS`
