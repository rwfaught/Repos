# Phase 89 - Strict Ollama Task Output Contract

Status: RATIFIED AS SOURCE/TEST-PROVEN WITH PHASE 91 LIFECYCLE DEPENDENCY  
Marker: `PHASE89_STRICT_OLLAMA_JSON_TASK_OUTPUT_CONTRACT_SOURCE_TEST_PROVEN`  
Documentation ratified: 2026-06-13

## Purpose

Phase 89 hardened the Ollama task/performer prompt and output contract so model output can be checked as an exact, bounded, machine-reviewable envelope before ordinary adequacy assessment.

## Implemented Contract

The Ollama task prompt requires one raw JSON object string:

- no Markdown fences;
- no prose before or after the object;
- no example output;
- exactly `task_id`, `status`, `summary`, `evidence`, `files_touched`, and `caveats`;
- status limited to `completed`, `blocked`, or `needs_review`.

The parser and validator reject invalid or non-object JSON, missing or extra fields, task-id mismatch, invalid status, empty summary or evidence, invalid list fields, Markdown fences, prose wrappers, and prospective language in summary, evidence, or caveats.

Ollama contract failures enter adequacy with a reason beginning:

`Ollama output contract invalid:`

## Source And Tests

- `providers/ollama_provider.py`
- `orchestrator/adequacy.py`
- `tests/test_phase_84_ollama_provider_contract.py`
- `tests/test_phase_89_ollama_output_contract.py`

## Lifecycle Dependency

Phase 89 established envelope validity but did not independently complete semantic lifecycle routing. A valid envelope declaring `blocked` or `needs_review` could still be flattened into task completion by the engine.

Phase 91 repaired that status-routing gap. Phase 89 must therefore be read together with Phase 91 when describing current task-outcome behavior.

## Non-Proofs

Phase 89 did not prove live model compliance.

Phase 89 does not prove:

- live Ollama compliance with the contract;
- semantic correctness of model answers;
- autonomous code mutation or writeback;
- verification provenance;
- production readiness;
- service, API, authentication, or multi-user support;
- package export or upload.

## Decision

Phase 89 is ratified as strict Ollama task-output contract source/test hardening. Its semantic lifecycle dependency is closed only by the separately ratified Phase 91 source/test repair.

`PHASE89_STRICT_OLLAMA_JSON_TASK_OUTPUT_CONTRACT_SOURCE_TEST_PROVEN`
