# Phase 296 - Draft Patch Proposal Apply Authorization Eligibility Readback

Boundary:

`PHASE296_DRAFT_PATCH_PROPOSAL_APPLY_AUTHORIZATION_ELIGIBILITY_READBACK_SOURCE_TEST_DOCS`

## Purpose

Add a deterministic local standard-library-only readback contract that checks
whether a Phase 294 draft patch proposal has enough structured evidence to be
eligible for a later explicit operator apply-authorization decision.

This phase determines authorization eligibility only. It does not create apply
authorization, does not apply patches, does not call apply functions, and does
not execute provider/model/runtime/platform behavior.

## Files Changed

- `orchestrator/draft_patch_proposal_apply_authorization_eligibility.py`
- `tests/test_phase_296_draft_patch_proposal_apply_authorization_eligibility_readback.py`
- `docs/PHASE_296.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Behavior

Phase 296 adds `evaluate_draft_patch_proposal_apply_authorization_eligibility`.
The readback accepts an embedded draft proposal or a draft proposal id, then
checks the draft-only status, no-authorization/no-apply flags, Phase 289
candidate reference, Phase 290 promotion reference, Phase 288 eligibility
reference, current-success reference, accepted-packet decision posture,
structured patch payload, path/id safety, and smuggled provider/model/runtime/
platform, semantic, autonomous, production-readiness, apply-authorization, and
apply claims.

Successful readback returns `authorization_eligible` with the draft proposal
id, reason code, empty missing-evidence list, linked evidence, caveats,
non-proofs, explicit no-authorization statement, explicit no-apply statement,
and timestamp.

Blocked readback returns `authorization_blocked` with deterministic reason
codes, exact missing evidence, linked evidence when available, caveats,
non-proofs, explicit no-authorization statement, explicit no-apply statement,
and no provider/model/runtime/platform/apply activity flags.

## Validation Commands

- `python -m py_compile orchestrator/draft_patch_proposal_apply_authorization_eligibility.py`
- `python -m unittest tests.test_phase_296_draft_patch_proposal_apply_authorization_eligibility_readback`
- `python -m unittest tests.test_phase_288_packet_result_to_patch_proposal_eligibility_contract tests.test_phase_289_packet_result_patch_proposal_candidate_artifact tests.test_phase_290_patch_proposal_candidate_operator_promotion_gate tests.test_phase_291_packet_to_patch_bridge_negative_edge_contract tests.test_phase_294_promoted_candidate_to_draft_patch_proposal_artifact tests.test_phase_295_draft_patch_proposal_negative_edge_contract`
- `python -m unittest tests.test_phase_97_model_backed_patch_proposal_protocol tests.test_phase_98_patch_proposal_operator_apply_authorization_gate tests.test_phase_99_bounded_patch_apply_engine_for_operator_authorized_proposals tests.test_phase_100_patch_apply_result_verification_and_task_completion_gate tests.test_phase_101_verified_patch_apply_task_completion_finalization_gate`
- `git diff --check`
- proof marker search
- changed-file allowlist audit
- clean git status

## Proof Scope

This phase proves only source/test/docs readback behavior for authorization
eligibility over a draft patch proposal evidence chain. It proves deterministic
eligibility/blocking output shape, evidence consistency checks, exact
no-authorization/no-apply statements, and non-proof preservation.

## Non-Proofs

This phase does not prove semantic correctness, live provider/model execution,
runtime/platform behavior, autonomous AI coding, model-backed generation,
production readiness, service/API/UI/dashboard/auth/deployment behavior,
scheduler/reminder/connector behavior, `general_answer` resumption,
platform/OpenClaw/Hermes/LightRAG behavior, cleanup/delete/archive authority,
actual apply authorization, patch apply execution, integrated production patch
workflow readiness, or Backbone V0.

`PHASE296_DRAFT_PATCH_PROPOSAL_APPLY_AUTHORIZATION_ELIGIBILITY_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS`
