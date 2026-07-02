# Phase 304 - Authorized Draft Patch Apply Negative Edge Contract

Boundary:

`PHASE304_AUTHORIZED_DRAFT_PATCH_APPLY_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS`

## Purpose

Harden negative and edge cases around authorized draft patch bounded apply.

This phase does not verify apply results, finalize patch tasks, prove semantic
correctness, prove production readiness, claim autonomous AI coding, invoke
provider/model/runtime/platform behavior, or declare Backbone V0.

## Files Changed

- `orchestrator/authorized_draft_patch_apply.py`
- `tests/test_phase_304_authorized_draft_patch_apply_negative_edge_contract.py`
- `docs/PHASE_304.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Behavior

Phase 304 strengthens the Phase 303 apply-attempt adapter with deterministic
negative-edge handling for latest reject/defer records, mismatched
authorization ids, candidate/task/packet/artifact/current-success references,
missing Phase 296 eligibility, unsupported or ambiguous operations, Windows
separator handling, absolute paths, path traversal, provider/model/runtime/
platform smuggling, semantic-correctness smuggling, autonomous coding
smuggling, production-readiness smuggling, finalization smuggling, verification
smuggling, duplicate apply attempts, and Phase 284 generated-residue reports.

Every blocked or failed attempt preserves exact reason codes plus
`patch_not_verified`, `not_finalized`,
`semantic_correctness_not_proven`, and
`production_readiness_not_proven`.

## Validation Commands

- `python -m py_compile orchestrator/authorized_draft_patch_apply.py tests/test_phase_304_authorized_draft_patch_apply_negative_edge_contract.py`
- `python -m unittest tests.test_phase_304_authorized_draft_patch_apply_negative_edge_contract`
- `python -m unittest tests.test_phase_303_authorized_draft_patch_proposal_bounded_apply_execution`
- relevant regression tests listed in the worker report
- `git diff --check`
- proof marker search
- changed-file allowlist audit
- clean git status

## Proof Scope

This phase proves only source/test/docs negative-edge contract behavior around
authorized draft patch bounded apply attempts. It proves deterministic blocked
or failed shapes for the covered edge cases and preserves no-verification and
no-finalization fields.

## Non-Proofs

This phase does not prove semantic correctness, live provider/model execution,
runtime/platform behavior, autonomous AI coding, model-backed generation,
production readiness, service/API/UI/dashboard/auth/deployment behavior,
scheduler/reminder/connector behavior, `general_answer` resumption,
platform/OpenClaw/Hermes/LightRAG behavior, cleanup/delete/archive authority,
apply-result verification, patch task finalization, integrated production patch
workflow readiness, or Backbone V0.

## Generated Artifact / Residue Posture

Tests patch project and artifact storage to temporary directories. Phase 304
does not delete or clean generated residue; it reports Phase 284 residue guard
input as a block condition before apply execution.

## Capsule / Source ZIP Caveat

Official product capsule proof comes from
`C:\Users\accou\Desktop\Repos\Powershell Scripts\Zip-OrchestratorProductRepo.ps1`.
Source Files ZIPs may include `__pycache__` and `.pyc` entries and should not
be treated as product failure on hash identity alone.

## Backbone V0 Open Thread

Backbone V0 remains an open thread. The loop is closer to reusable control
spine criteria but still lacks apply-result verification, finalization, and
domain separation.

`PHASE304_AUTHORIZED_DRAFT_PATCH_APPLY_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`
