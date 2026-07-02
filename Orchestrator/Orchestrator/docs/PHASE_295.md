# Phase 295 - Draft Patch Proposal Negative Edge Contract

Boundary:

`PHASE295_DRAFT_PATCH_PROPOSAL_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS`

## Purpose

Harden negative and edge cases around promoted-candidate draft patch proposal
creation. This phase keeps the bridge draft-only. It does not apply patches,
authorize apply, call provider/model/runtime/platform behavior, or treat draft
creation as production patch workflow readiness.

## Files Changed

- `orchestrator/promoted_candidate_draft_patch_proposal.py`
- `tests/test_phase_295_draft_patch_proposal_negative_edge_contract.py`
- `docs/PHASE_295.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Behavior

Phase 295 adds deterministic blocked/readback coverage for missing candidate
evidence, rejected/deferred promotion evidence, promoted candidates with missing
promotion notes, stale or mismatched source links, latest rejected/deferred
promotion records, mismatched task/artifact/verifier/current-success/operator
decision references, missing eligibility/operator/current-success references,
missing or ambiguous structured patch payloads, unsafe proposed patch paths,
and claim smuggling.

Unsafe proposed patch paths now block before draft artifact creation. The
contract rejects parent traversal, POSIX absolute paths, Windows absolute
paths, and Windows separator paths in proposed patch evidence.

Claim smuggling blocks provider/model/runtime/platform claims, semantic
correctness claims, autonomous coding claims, production-readiness claims,
apply-authorization claims, and attempted apply claims. Text smuggling in patch
evidence rationale is also rejected.

Blocked outputs remain deterministic and preserve exact reason codes,
`draft_proposal_status=blocked`, `not_authorized_for_apply=true`,
`not_applied=true`, no provider/model/runtime/platform flags, no semantic
correctness proof, no autonomous coding proof, no production-readiness proof,
and no cleanup/delete/archive/apply behavior.

Successful draft creation remains `draft_only` and
`not_authorized_for_apply`.

## Validation Commands

- `python -m py_compile orchestrator/promoted_candidate_draft_patch_proposal.py`
- `python -m unittest tests.test_phase_295_draft_patch_proposal_negative_edge_contract`
- `python -m unittest tests.test_phase_294_promoted_candidate_to_draft_patch_proposal_artifact`
- focused Phase 288/289/290/291 regressions
- relevant patch proposal/apply spine regressions for Phases 97/98/99/100/101
- `git diff --check`
- proof marker search
- changed-file allowlist audit
- clean git status

## Proof Scope

This phase proves only source/test/docs negative-edge behavior for draft patch
proposal creation. It proves deterministic blocking and exact reason-code
readback for the Phase 295 edge cases while preserving the existing draft-only
success shape.

## Non-Proofs

This phase does not prove semantic correctness, live provider/model execution,
runtime/platform behavior, autonomous AI coding, model-backed generation,
production readiness, service/API/UI/dashboard/auth/deployment behavior,
scheduler/reminder/connector behavior, `general_answer` resumption,
platform/OpenClaw/Hermes/LightRAG behavior, cleanup/delete/archive authority,
actual apply authorization, patch apply execution, integrated production patch
workflow readiness, or Backbone V0.

## Generated Artifact / Residue Posture

Tests patch draft artifact storage to temporary directories. Generated residue
guard coverage reports generated paths without cleanup, deletion, archive, or
apply behavior.

`PHASE295_DRAFT_PATCH_PROPOSAL_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`
