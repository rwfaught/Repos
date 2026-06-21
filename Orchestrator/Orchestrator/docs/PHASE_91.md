# Phase 91 - Provider Status Routing And Reviewer Schema Separation

Status: RATIFIED AS LOCALLY SOURCE/TEST-PROVEN; EXPORT/UPLOAD PENDING  
Marker: `PHASE91_CORRECTED_LOCAL_PROOF_RESULT=PASS`  
Documentation ratified: 2026-06-13

## Purpose

Phase 91 repaired provider outcome routing and separated Ollama performer output from reviewer recommendation output.

## Status Routing

The engine now applies these rules:

- a valid Ollama `completed` envelope may become task `completed` only after existing verification and adequacy gates pass;
- valid Ollama `blocked` routes to task `needs_review`, not `completed`;
- valid Ollama `needs_review` routes to task `needs_review`, not `completed`;
- an invalid Ollama contract remains inadequate with a reason beginning `Ollama output contract invalid:`;
- provider execution status other than `success`, including CodexProvider `not_implemented`, routes to `execution_failed`.

Existing artifact and verifier recording behavior remains in place.

## Schema Separation

Ollama performer/task prompts use the six-field task result schema:

- `task_id`
- `status`
- `summary`
- `evidence`
- `files_touched`
- `caveats`

Ollama reviewer prompts use the reviewer recommendation schema:

- `recommendation_type`
- `reason`

Reviewer and performer outputs are no longer forced into one incompatible schema.

## Source And Tests

- `providers/ollama_provider.py`
- `orchestrator/adequacy.py`
- `orchestrator/engine.py`
- `tests/test_phase_89_ollama_output_contract.py`
- `tests/test_phase_91_provider_status_routing.py`

## Corrected Local Proof

Boundary:

`READONLY_PHASE_91_CORRECTED_LOCAL_PROOF_NO_SOURCE_MUTATION_NO_DOC_MUTATION_NO_EXPORT_NO_OZ_NO_TASK_EXECUTION_NO_PROVIDER_EXECUTION_NO_MODEL_EXECUTION_NO_RUNTIME_EXECUTION_NO_WSL_NO_INSTALLER_NO_DISCORD_NO_BRIDGE_NO_ADAPTER_NO_PLATFORM_MUTATION_NO_CODEX_NO_CLEANUP_NO_DELETE_NO_ARCHIVE`

Targeted command recorded by the corrected proof:

`python -m unittest tests.test_phase_84_ollama_provider_contract tests.test_phase_89_ollama_output_contract tests.test_phase_91_provider_status_routing`

Recorded result:

`Ran 24 tests in 0.055s`

`OK`

Phase 91 proof is targeted local unittest proof only. The targeted unittest proof ran 24 tests.

Observed routing proved `blocked` and `needs_review` remain non-completed, `completed` remains gated, and Codex `not_implemented` becomes `execution_failed`.

## Open Caveats

Phase 91 did not prove live model compliance.

Phase 91 does not prove or repair:

- live Ollama compliance;
- semantic correctness of model answers;
- model-backed code mutation or writeback;
- verification provenance or no-op verification semantics;
- Phase 74 authorized case-packet synthetic completion semantics;
- reviewer subtype/contract-selector nuance;
- test isolation beyond the targeted proof;
- path containment;
- atomic persistence or locking;
- service/API, authentication, or multi-user support;
- packaging or CI;
- production readiness;
- product package export or upload.

## Decision

Phase 91 is ratified as locally source/test-proven provider status routing and reviewer/performer schema separation. Export and upload remain pending.

`PHASE91_CORRECTED_LOCAL_PROOF_RESULT=PASS`
