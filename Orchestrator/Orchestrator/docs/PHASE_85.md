# Phase 85 - Guarded Live Ollama Smoke Harness and Guard Tests

## Purpose

Phase 85 stages the first live Ollama proof boundary without performing live model execution.

It adds a guarded live smoke harness that refuses to call the Ollama provider unless the explicit environment variable ORCH_PHASE85_ALLOW_LIVE_OLLAMA=YES is set.

This creates a narrow airlock between mocked HTTP provider proof and a later explicitly authorized live model/provider proof.

## Boundary

MUTATE_PRODUCT_PHASE85_GUARDED_LIVE_OLLAMA_SMOKE_HARNESS_AND_GUARD_TESTS_EXPORT_NO_LIVE_TASK_EXECUTION_NO_LIVE_PROVIDER_EXECUTION_NO_MODEL_EXECUTION_NO_RUNTIME_EXECUTION_NO_WSL_NO_INSTALLER_NO_DISCORD_NO_BRIDGE_NO_ADAPTER_NO_PLATFORM_MUTATION_NO_A18CF_NO_VENDOR_NO_CLEANUP_NO_DELETE_NO_ARCHIVE_NO_OZ_NO_CODEX

## Changed Files

- tools/phase85_ollama_live_smoke.py
- tests/test_phase_85_ollama_live_smoke_guard.py
- docs/PHASE_85.md
- docs/ACTION_LOG.md
- docs/PHASE_INDEX.md
- docs/SOURCE_MANIFEST.md
- docs/CURRENT_SUCCESS_CRITERION.md

## Proof

Expected proof for this phase:

- starting product ZIP hash matches 1a8da8b5c392f127ed1868b0c0a12ab4b42135a1a251662ba781caef4812d13e
- guard unit tests pass
- harness exits blocked without ORCH_PHASE85_ALLOW_LIVE_OLLAMA=YES
- blocked harness reports no live provider execution, no model execution, no runtime execution, and no task persistence
- product ZIP exports required Phase 85 source files
- generated acceptance JSON payloads remain excluded

## Caveat

Phase 85 does not prove live model-backed generation.

It proves only that the future live Ollama smoke path exists and is guarded against accidental execution.

PHASE85_GUARDED_LIVE_OLLAMA_SMOKE_HARNESS_AND_GUARD_TESTS

## Repair - Guarded Smoke Import Path and False-Pass Proof

PHASE85_REPAIR_GUARDED_SMOKE_IMPORT_PATH_AND_FALSE_PASS_PROOF

Timestamp: 2026-06-12T14:54:11-05:00

Boundary: REPAIR_PRODUCT_PHASE85_GUARDED_LIVE_OLLAMA_SMOKE_IMPORT_PATH_AND_FALSE_PASS_PROOF_EXPORT_NO_LIVE_TASK_EXECUTION_NO_LIVE_PROVIDER_EXECUTION_NO_MODEL_EXECUTION_NO_RUNTIME_EXECUTION_NO_WSL_NO_INSTALLER_NO_DISCORD_NO_BRIDGE_NO_ADAPTER_NO_PLATFORM_MUTATION_NO_A18CF_NO_VENDOR_NO_CLEANUP_NO_DELETE_NO_ARCHIVE_NO_OZ_NO_CODEX

The initial Phase 85 run was not ratified because the guard unit test failed before export.

Failure observed:

- test_live_smoke_harness_blocks_without_explicit_env_flag expected return code 2
- observed return code 1
- Phase 85 guard unit tests failed with exit code 1

The later PHASE85_GUARD_UNIT_TESTS=PASS and PHASE85_RESULT=PASS lines from that run are invalid proof because they occurred after the test failure.

Repair:

- ensured the harness can emit the blocked payload before importing live provider/task modules
- added repo-root sys.path handling for script execution from tools/
- strengthened the guard test to show stdout/stderr if blocked execution fails
- proved live provider/model/runtime execution remains blocked unless ORCH_PHASE85_ALLOW_LIVE_OLLAMA=YES is set

This repair still does not authorize or prove live model-backed generation.

PHASE85_REPAIR_GUARDED_SMOKE_IMPORT_PATH_AND_FALSE_PASS_PROOF

## Repair - Static Analysis False Failure

PHASE85_REPAIR_STATIC_ANALYSIS_FALSE_FAILURE

Timestamp: 2026-06-12T14:56:27-05:00

Boundary: REPAIR_PRODUCT_PHASE85_GUARD_TEST_STATIC_ANALYSIS_FALSE_FAILURE_EXPORT_NO_LIVE_TASK_EXECUTION_NO_LIVE_PROVIDER_EXECUTION_NO_MODEL_EXECUTION_NO_RUNTIME_EXECUTION_NO_WSL_NO_INSTALLER_NO_DISCORD_NO_BRIDGE_NO_ADAPTER_NO_PLATFORM_MUTATION_NO_A18CF_NO_VENDOR_NO_CLEANUP_NO_DELETE_NO_ARCHIVE_NO_OZ_NO_CODEX

The prior Phase 85 repair run was not ratified because the guard unit test failed before export.

Failure observed:

- test_harness_source_contains_explicit_live_guard_before_live_imports failed
- assertion compared raw text positions
- observed: guard_index=3730, provider_import_index=1963
- this was an over-strict static test because Python function bodies may be defined textually before main guard evaluation without executing their imports

Repair:

- replaced brittle raw text-index ordering check with AST-based top-level import inspection
- preserved direct blocked harness execution proof
- confirmed no top-level imports from providers or orchestrator
- confirmed live provider/task imports remain deferred inside live-path functions
- preserved the ORCH_PHASE85_ALLOW_LIVE_OLLAMA=YES guard

This repair still does not authorize or prove live model-backed generation.

PHASE85_REPAIR_STATIC_ANALYSIS_FALSE_FAILURE

## Repair - UTF-8 No-BOM Guard Test Repair

PHASE85_REPAIR_UTF8_NO_BOM_GUARD_TEST

Timestamp: 2026-06-12T14:59:46-05:00

Boundary: REPAIR_PRODUCT_PHASE85_UTF8_NO_BOM_GUARD_TEST_AND_EXPORT_NO_LIVE_TASK_EXECUTION_NO_LIVE_PROVIDER_EXECUTION_NO_MODEL_EXECUTION_NO_RUNTIME_EXECUTION_NO_WSL_NO_INSTALLER_NO_DISCORD_NO_BRIDGE_NO_ADAPTER_NO_PLATFORM_MUTATION_NO_A18CF_NO_VENDOR_NO_CLEANUP_NO_DELETE_NO_ARCHIVE_NO_OZ_NO_CODEX

The prior Phase 85 static-analysis repair run was not ratified because AST parsing failed on a UTF-8 BOM at the start of tools/phase85_ollama_live_smoke.py.

Failure observed:

- SyntaxError: invalid non-printable character U+FEFF
- ast.parse(text) failed before completing the guard tests

Repair:

- rewrote tools/phase85_ollama_live_smoke.py as UTF-8 without BOM
- rewrote tests/test_phase_85_ollama_live_smoke_guard.py as UTF-8 without BOM
- added an explicit no-BOM guard test
- preserved blocked harness proof
- preserved AST-based no-top-level-live-project-import proof
- preserved deferred live import proof

This repair still does not authorize or prove live model-backed generation.

PHASE85_REPAIR_UTF8_NO_BOM_GUARD_TEST
