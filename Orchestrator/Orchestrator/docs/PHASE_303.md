# Phase 303 - Authorized Draft Patch Proposal Bounded Apply Execution

Boundary:

`PHASE303_AUTHORIZED_DRAFT_PATCH_PROPOSAL_BOUNDED_APPLY_EXECUTION_SOURCE_TEST_DOCS`

## Purpose

Add deterministic bounded patch apply execution from an explicit Phase 299/301
apply-authorization record.

This phase may invoke the existing Phase 99 bounded patch apply engine only
after the latest authorization readback is active and the draft proposal
evidence chain remains linked. It does not verify apply results, finalize patch
tasks, prove semantic correctness, prove production readiness, claim autonomous
AI coding, or declare Backbone V0.

## Files Changed

- `orchestrator/authorized_draft_patch_apply.py`
- `tests/test_phase_303_authorized_draft_patch_proposal_bounded_apply_execution.py`
- `docs/PHASE_303.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Behavior

Phase 303 adds `execute_authorized_draft_patch_apply`. The function loads or
accepts an explicit Phase 299 apply-authorization record, uses Phase 301
latest-status semantics to require an active `authorize_apply` decision, checks
that the authorization links to a `draft_only` and `not_applied` draft proposal,
requires Phase 296 `authorization_eligible` evidence, rejects stale or
mismatched links, rejects provider/model/runtime/platform and readiness
smuggling, normalizes bounded operations, creates narrow Phase 99-compatible
bridge artifacts, invokes the existing bounded patch apply engine, and persists
an apply-attempt artifact.

The apply-attempt artifact reports the source authorization id, draft proposal
id, linked evidence chain, bounded target information, files attempted, apply
status, reason code, timestamp, caveats, and non-proofs. It explicitly carries
`patch_not_verified`, `not_finalized`,
`semantic_correctness_not_proven`, and
`production_readiness_not_proven`.

## Validation Commands

- `python -m py_compile orchestrator/authorized_draft_patch_apply.py tests/test_phase_303_authorized_draft_patch_proposal_bounded_apply_execution.py`
- `python -m unittest tests.test_phase_303_authorized_draft_patch_proposal_bounded_apply_execution`
- relevant regression tests listed in the worker report
- `git diff --check`
- proof marker search
- changed-file allowlist audit
- clean git status

## Proof Scope

This phase proves only source/test/docs behavior for a bounded apply-attempt
adapter from explicit Phase 299/301 authorization records to the existing Phase
99 apply engine. It proves deterministic blocking for missing, rejected,
deferred, stale, mismatched, malformed, unbounded, and smuggled inputs covered
by the Phase 303 tests.

## Non-Proofs

This phase does not prove semantic correctness, live provider/model execution,
runtime/platform behavior, autonomous AI coding, model-backed generation,
production readiness, service/API/UI/dashboard/auth/deployment behavior,
scheduler/reminder/connector behavior, `general_answer` resumption,
platform/OpenClaw/Hermes/LightRAG behavior, cleanup/delete/archive authority,
apply-result verification, patch task finalization, integrated production patch
workflow readiness, or Backbone V0.

## Generated Artifact / Residue Posture

Tests patch project and artifact storage to temporary directories. The phase
does not perform broad cleanup, deletion, archive, provider/model/runtime
execution, apply-result verification, or finalization behavior.

## Capsule / Source ZIP Caveat

Official product capsule proof comes from
`C:\Users\accou\Desktop\Repos\Powershell Scripts\Zip-OrchestratorProductRepo.ps1`.
Source Files ZIPs may include `__pycache__` and `.pyc` entries and should not
be treated as product failure on hash identity alone.

## Backbone V0 Open Thread

Backbone V0 remains an open thread. The control loop is closer to the packet /
result / candidate / proposal / authorization / apply / verification /
finalization model, but it still lacks apply-result verification, finalization,
and domain separation.

`PHASE303_AUTHORIZED_DRAFT_PATCH_PROPOSAL_BOUNDED_APPLY_EXECUTION_SOURCE_TEST_DOCS_PROVEN=PASS`
