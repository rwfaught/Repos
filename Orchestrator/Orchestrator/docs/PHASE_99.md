# Phase 99 - Bounded Patch Apply Engine For Operator-Authorized Proposals

Status: LOCALLY SOURCE/TEST/DOCS-PROVEN; EXPORT/UPLOAD NOT PERFORMED

Marker: `PHASE99_BOUNDED_PATCH_APPLY_ENGINE_FOR_OPERATOR_AUTHORIZED_PROPOSALS_LOCAL_SOURCE_TEST_PROVEN=PASS`

## Purpose

Phase 99 adds the first deterministic bounded patch-application capability behind
the Phase 98 operator authorization gate. Application is an explicit standalone
boundary, not normal-engine, provider, or model execution.

## Changed Behavior

- Valid Phase 98 `authorize_apply` artifacts can authorize an explicit apply
  request for their referenced Phase 97 proposals.
- Operations use `operation_id`, `file_path`, `expected_before`,
  `replacement_after`, and an optional description.
- `expected_before` must occur exactly once. Zero or multiple matches fail
  without writing.
- All operations are validated and staged before any target file is written.
- Proposal and authorization identity, linkage, filesystem-mutation policy,
  unapplied state, and operator/apply-boundary gates are revalidated.
- Paths must pass Phase 94 containment and appear in both proposal
  `files_in_scope` and authorization `files_authorized`.
- Successful application persists a separate `patch_apply_result` with changed
  files, operations, and per-file before/after SHA-256 evidence.
- Apply results set `applied=true`, `requires_verification=true`, and
  `causal_change_observed=true` only after successful writes and hash changes.
- Proposal and authorization artifacts remain immutable.
- Task state and execution artifact identity remain unchanged.
- Apply results do not satisfy task verification or completion.
- No normal-engine automatic application or provider/model/runtime integration
  was added.

## Source Files

- `orchestrator/patch_apply_engine.py`

## Tests

- `tests/test_phase_99_bounded_patch_apply_engine_for_operator_authorized_proposals.py`
- `tests/test_phase_98_patch_proposal_operator_apply_authorization_gate.py`
- `tests/test_phase_97_model_backed_patch_proposal_protocol.py`
- `tests/test_phase_96_canonical_case_packet_execution_delegation.py`
- `tests/test_phase_95_task_execution_policy_classification.py`
- `tests/test_phase_94_path_and_record_identity_containment.py`
- `tests/test_phase_92_verification_provenance.py`
- `tests/test_phase_91_provider_status_routing.py`

## Proof Commands

`python3 -m py_compile orchestrator/patch_apply_engine.py tests/test_phase_99_bounded_patch_apply_engine_for_operator_authorized_proposals.py`

`python3 -m unittest tests.test_phase_99_bounded_patch_apply_engine_for_operator_authorized_proposals tests.test_phase_98_patch_proposal_operator_apply_authorization_gate tests.test_phase_97_model_backed_patch_proposal_protocol tests.test_phase_96_canonical_case_packet_execution_delegation tests.test_phase_95_task_execution_policy_classification tests.test_phase_94_path_and_record_identity_containment tests.test_phase_92_verification_provenance tests.test_phase_91_provider_status_routing`

Recorded result:

`Ran 72 tests in 8.554s`

`OK`

## Phase 98 External Verification Reconciliation

- `PHASE98_PRODUCT_ZIP_EXPORT_VERIFY_RESULT=PASS`
- `PHASE98_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS`
- SHA-256 `354BC287532E3429EF056ABAD850431303139843954710EA1454EE44FBE24A09`

That final artifact hash proof is external to source files later exported.

## Caveats

- The format is exact text replacement, not unified-diff or fuzzy patching.
- Operations are prevalidated before writes, but multi-file writes are not a
  transactional filesystem commit if an external I/O failure interrupts writes.
- Causal hashes support a later verification boundary; they are not full task
  verification.
- Immutable proposal and authorization records remain unapplied; the separate
  apply-result artifact records application.

## Explicit Non-Proofs

Phase 99 does not prove semantic correctness, test adequacy, full verification,
task completion, production readiness, live provider/model/runtime behavior, or
general patch compatibility. It does not invoke the normal task engine,
provider, model, Ollama, verifier, reviewer, planner, platform, OpenClaw,
Discord, bridge, adapter, installer, WSL, or oz, or export, package, clean up,
delete, or archive.

`PHASE99_BOUNDED_PATCH_APPLY_ENGINE_FOR_OPERATOR_AUTHORIZED_PROPOSALS_LOCAL_SOURCE_TEST_PROVEN=PASS`
