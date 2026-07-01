# Phase 271 - Path Containment POSIX Absolute Repair

## Boundary

`PHASE_271_PATH_CONTAINMENT_POSIX_ABSOLUTE_REPAIR_AND_CURRENT_SPINE_VALIDATION_WORKER`

## Purpose

Phase 271 repairs path-containment error-message contract drift for
POSIX-style absolute declared project paths on Windows.

`resolve_declared_project_path()` now rejects paths such as
`/tmp/outside.txt` as absolute before they can fall through to the broader
project-root containment diagnostic.

## Files Changed

Source:

- `orchestrator/paths.py`

Docs:

- `docs/PHASE_271.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

No tests changed.

## Validation

Phase 271 validation passed:

- `python -m py_compile orchestrator/paths.py orchestrator/current_success_result_review.py`
- `python -m unittest tests.test_phase_97_model_backed_patch_proposal_protocol.Phase97ModelBackedPatchProposalProtocolTests.test_absolute_proposed_change_path_is_rejected tests.test_phase_98_patch_proposal_operator_apply_authorization_gate.Phase98PatchProposalOperatorApplyAuthorizationGateTests.test_absolute_authorized_path_is_rejected tests.test_phase_99_bounded_patch_apply_engine_for_operator_authorized_proposals.Phase99BoundedPatchApplyEngineTests.test_absolute_operation_path_is_rejected tests.test_phase_101_verified_patch_apply_task_completion_finalization_gate.Phase101VerifiedPatchApplyTaskFinalizationTests.test_absolute_file_path_evidence_is_rejected -v`
- `python -m unittest tests.test_phase_78_current_success_result_review tests.test_phase_91_provider_status_routing tests.test_phase_92_verification_provenance tests.test_phase_95_task_execution_policy_classification tests.test_phase_97_model_backed_patch_proposal_protocol tests.test_phase_98_patch_proposal_operator_apply_authorization_gate tests.test_phase_99_bounded_patch_apply_engine_for_operator_authorized_proposals tests.test_phase_100_patch_apply_result_verification_and_task_completion_gate tests.test_phase_101_verified_patch_apply_task_completion_finalization_gate -v`

The targeted coding-spine regression ran 99 tests with one symlink-environment
skip and passed.

## Non-Proofs

Phase 271 does not prove or add:

- semantic correctness beyond the tests run
- live provider/model behavior
- runtime/platform behavior
- autonomous AI coding behavior
- production readiness
- export/upload
- commit or push

## Marker

`PHASE271_PATH_CONTAINMENT_POSIX_ABSOLUTE_REPAIR_SOURCE_TEST_DOCS_PROVEN=PASS`
