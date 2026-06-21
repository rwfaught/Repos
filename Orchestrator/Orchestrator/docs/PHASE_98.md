# Phase 98 - Patch Proposal Operator Apply Authorization Gate

Status: LOCALLY SOURCE/TEST/DOCS-PROVEN; EXPORT/UPLOAD NOT PERFORMED

Marker: `PHASE98_PATCH_PROPOSAL_OPERATOR_APPLY_AUTHORIZATION_GATE_LOCAL_SOURCE_TEST_PROVEN=PASS`

## Purpose

Phase 98 adds the explicit operator decision artifact between a Phase 97 patch
proposal and a future patch-application boundary.

The artifact records that a bounded filesystem-mutation proposal is authorized
for a future apply boundary, or rejected, without applying the patch or entering
the engine execution lifecycle.

## Changed Behavior

- A stored valid Phase 97 patch proposal can receive a stored
  `patch_apply_authorization` artifact.
- Authorization records preserve proposal, task, optional run, execution policy,
  bounded authorized files, operator decision, operator label, decision reason,
  source, and creation time.
- Supported decisions are `authorize_apply` and `reject_apply`.
- Authorized proposals record `authorized_for_future_apply_boundary`; rejected
  proposals record `apply_rejected`.
- Every authorization records `requires_separate_apply_boundary=true` and
  `applied=false`.
- Proposal lookup, artifact identity, operator-gate state, unapplied state,
  filesystem-mutation policy, and bounded proposal scope are revalidated.
- Absolute paths, parent traversal, paths outside `PROJECT_ROOT`, and paths
  outside proposal `files_in_scope` are rejected.
- Missing proposals, report-only proposals, already-applied proposals, and
  proposals that do not require operator apply are rejected.
- Authorization creation does not mutate the proposal, target files, task
  status, or task execution artifact identity.
- Authorization artifacts explicitly record no execution, provider, model,
  runtime, completion, verification, or causal-change proof.
- No engine or provider integration was added.

## Source Files

- `orchestrator/patch_apply_authorization.py`

## Tests

- `tests/test_phase_98_patch_proposal_operator_apply_authorization_gate.py`
- `tests/test_phase_97_model_backed_patch_proposal_protocol.py`
- `tests/test_phase_96_canonical_case_packet_execution_delegation.py`
- `tests/test_phase_95_task_execution_policy_classification.py`
- `tests/test_phase_94_path_and_record_identity_containment.py`
- `tests/test_phase_92_verification_provenance.py`
- `tests/test_phase_91_provider_status_routing.py`

## Proof Commands

`python3 -m py_compile orchestrator/patch_apply_authorization.py tests/test_phase_98_patch_proposal_operator_apply_authorization_gate.py`

`python3 -m unittest tests.test_phase_98_patch_proposal_operator_apply_authorization_gate tests.test_phase_97_model_backed_patch_proposal_protocol tests.test_phase_96_canonical_case_packet_execution_delegation tests.test_phase_95_task_execution_policy_classification tests.test_phase_94_path_and_record_identity_containment tests.test_phase_92_verification_provenance tests.test_phase_91_provider_status_routing`

Recorded result:

`Ran 55 tests in 4.944s`

`OK`

## Phase 97 External Verification Reconciliation

Coordinator-side export and uploaded verification accepted the Phase 97 product
ZIP:

- `PHASE97_PRODUCT_ZIP_EXPORT_VERIFY_RESULT=PASS`
- `PHASE97_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS`
- SHA-256 `4F8F0FFE180CA94945F39677319D4578991F25A7654B17C1D1DABEAC01733561`

That final artifact hash proof is external to the source files later exported.
Phase 98 does not claim that source files prove their own final exported hash.

## Caveats

- Phase 98 records operator judgment but does not prove that the proposed diff is
  applicable, complete, semantically correct, or safe to apply.
- `authorize_apply` means authorized for a future apply boundary, not yet
  applied.
- The future apply boundary must independently preserve bounded scope, execute
  the mutation, and produce causal-change and verification evidence.
- Authorization artifacts are standalone governance artifacts, not engine
  execution artifacts.

## Explicit Non-Proofs

Phase 98 does not apply a patch, mutate source targets, mark a proposal applied,
complete a task, satisfy verification or causal-change proof, invoke a task,
provider, model, runtime, verifier, reviewer, planner, platform, OpenClaw,
Discord, bridge, adapter, installer, WSL, Ollama, or oz, or export, package,
clean up, delete, archive, or add autonomous writeback.

`PHASE98_PATCH_PROPOSAL_OPERATOR_APPLY_AUTHORIZATION_GATE_LOCAL_SOURCE_TEST_PROVEN=PASS`
