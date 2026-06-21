# Phase 95 - Task Execution Policy Classification

Status: LOCALLY SOURCE/TEST/DOCS-PROVEN; EXPORT/UPLOAD NOT PERFORMED

Marker: `PHASE95_TASK_EXECUTION_POLICY_CLASSIFICATION_LOCAL_SOURCE_TEST_PROVEN=PASS`

## Purpose

Phase 95 makes task execution intent explicit and prevents filesystem-mutation work from completing through report-only or state-only verification semantics.

## Implemented Behavior

- Tasks have an `execution_policy` field.
- Missing policy defaults to `report_only` for backward compatibility.
- Known policies are `report_only` and `filesystem_mutation`.
- Unknown policies are rejected deterministically before provider dispatch.
- `report_only` preserves existing provider, adequacy, deterministic verification, and no-scope skipped-verification behavior.
- `filesystem_mutation` enforces `requires_causal_change=True`.
- Mutation tasks require at least one declared file target before dispatch.
- Mutation targets use the Phase 94 shared project-relative path policy before dispatch.
- Empty-scope mutation tasks persist a failed policy-precondition verifier record and do not dispatch a provider.
- Mutation tasks cannot complete without a created or hash-changed declared target.
- Execution policy and causal requirement are visible in serialized tasks, execution artifacts, and verifier records.
- `LocalFileProvider` remains the deterministic bounded mutation demonstration provider.

## Source And Tests

- `orchestrator/task_schema.py`
- `orchestrator/engine.py`
- `orchestrator/artifact_store.py`
- `tests/test_phase_95_task_execution_policy_classification.py`

## Validation

`python3 -m py_compile orchestrator/task_schema.py orchestrator/engine.py orchestrator/artifact_store.py tests/test_phase_95_task_execution_policy_classification.py`

`python3 -m unittest tests.test_phase_95_task_execution_policy_classification tests.test_phase_94_path_and_record_identity_containment tests.test_phase_92_verification_provenance tests.test_phase_91_provider_status_routing tests.test_phase_74_authorized_case_packet_task_execution`

Recorded result:

`Ran 40 tests in 2.841s`

`OK`

## Phase 94 External Verification Reconciliation

Coordinator-side uploaded verification accepted the Phase 94 product ZIP:

- `PHASE94_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS`
- SHA-256 `614282E4884F901F07F96487F1D0D71E563A875E881E4E7DCD4BDDBC44AAB88E`

That final artifact hash proof is external to the source files later exported. Phase 95 does not claim that source files prove their own final exported hash.

## Explicit Non-Proofs

Phase 95 does not add or prove live runtime, provider, model, WSL, installer, Discord, bridge, adapter, platform, OpenClaw, oz, export, package, cleanup, deletion, archive, autonomous writeback, real Phase 74 execution, semantic correctness, or production readiness.

`PHASE95_TASK_EXECUTION_POLICY_CLASSIFICATION_LOCAL_SOURCE_TEST_PROVEN=PASS`
