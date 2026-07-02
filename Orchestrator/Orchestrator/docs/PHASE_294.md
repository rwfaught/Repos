# Phase 294 - Promoted Candidate To Draft Patch Proposal Artifact

Boundary:

`PHASE294_PROMOTED_CANDIDATE_TO_DRAFT_PATCH_PROPOSAL_ARTIFACT_SOURCE_TEST_DOCS`

## Purpose

Create a deterministic local standard-library-only draft patch proposal artifact
from a promoted packet-derived candidate. The artifact is draft-only evidence.
It does not apply a patch, authorize apply, call apply code, or treat candidate
promotion as authorization.

## Phase 293 Read-Only Assessment

Phase 293 found a safe artifact-only seam only if Phase 294 uses a new
draft-only artifact surface. The existing `orchestrator/patch_proposal.py`
schema is useful as a proposal-shaped reference, but its native
`proposal_status` is `awaiting_operator_apply` and its `requires_operator_apply`
field is intentionally for later authorization flow. Therefore Phase 294 does
not write native Phase 97 patch proposals and does not call the Phase 98-101
authorization/apply/finalization spine.

Relevant modules and tests:

- `orchestrator/packet_result_patch_proposal_eligibility.py`
- `orchestrator/packet_result_patch_proposal_candidate.py`
- `orchestrator/patch_proposal_candidate_promotion.py`
- `orchestrator/patch_proposal.py`
- `orchestrator/patch_apply_authorization.py`
- `orchestrator/patch_apply_engine.py`
- `orchestrator/patch_apply_result_review.py`
- `orchestrator/patch_apply_task_finalization.py`
- `tests/test_phase_97_model_backed_patch_proposal_protocol.py`
- `tests/test_phase_98_patch_proposal_operator_apply_authorization_gate.py`
- `tests/test_phase_99_bounded_patch_apply_engine_for_operator_authorized_proposals.py`
- `tests/test_phase_100_patch_apply_result_verification_and_task_completion_gate.py`
- `tests/test_phase_101_verified_patch_apply_task_completion_finalization_gate.py`
- Phase 288-291 packet-to-patch bridge tests.

## Files Changed

- `orchestrator/promoted_candidate_draft_patch_proposal.py`
- `tests/test_phase_294_promoted_candidate_to_draft_patch_proposal_artifact.py`
- `docs/PHASE_294.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Behavior

`create_promoted_candidate_draft_patch_proposal` accepts a promoted candidate
and promotion record, requires a non-empty draft note/reason, verifies the
candidate is `candidate_only`, verifies the promotion status is
`candidate_ready_for_later_patch_proposal_boundary`, verifies source evidence
links match, and requires structured patch payload fields:
`proposed_changes`, `unified_diff`, and `rationale`.

Successful output persists `artifact_type=draft_patch_proposal` with
`draft_proposal_status=draft_only`, `not_authorized_for_apply=true`, and
`not_applied=true`.

Blocked output is deterministic and includes exact reason codes plus missing
requirements for unpromoted, rejected, deferred, stale, mismatched, missing
note, unsafe id, missing payload, claim-smuggling, and apply-smuggling cases.

## Validation Commands

- `python -m py_compile orchestrator/promoted_candidate_draft_patch_proposal.py`
- `python -m unittest tests.test_phase_294_promoted_candidate_to_draft_patch_proposal_artifact`
- focused Phase 288/289/290/291 regressions
- relevant patch proposal/apply spine regressions for Phases 97/98/99/100/101
- requested packet/current-success regressions that are available in this
  checkout
- `git diff --check`
- proof marker search
- changed-file allowlist audit
- clean git status

## Proof Scope

This phase proves only source/test/docs behavior for creating a deterministic
draft-only patch proposal artifact from a promoted candidate with sufficient
structured evidence. It proves the draft preserves packet, run, task, execution
artifact, verifier, current-success, operator decision, eligibility, candidate,
promotion, note/reason, caveat, and non-proof links.

## Non-Proofs

This phase does not prove semantic correctness, live provider/model execution,
runtime/platform behavior, autonomous AI coding, model-backed generation,
production readiness, service/API/UI/dashboard/auth/deployment behavior,
scheduler/reminder/connector behavior, `general_answer` resumption,
platform/OpenClaw/Hermes/LightRAG behavior, cleanup/delete/archive authority,
actual apply authorization, patch apply execution, integrated production patch
workflow readiness, or Backbone V0.

## Generated Artifact / Residue Posture

The source function writes only caller-requested draft proposal artifacts under
the product data draft directory or a test-patched directory. Tests use
temporary directories and do not clean or delete product artifacts.

## Capsule / Source ZIP Caveat

The Source Files upload ZIP may include `__pycache__` and `.pyc` entries when
created by `srczip`. Product capsule proof should come from the official
product capsule refresh output, not source upload hash identity alone.

## Backbone V0 Open Thread

The packet/result/candidate/promotion/draft shape is approaching reusable
control-loop criteria, but Backbone V0 is not declared. Actual apply
authorization, bounded apply, apply-result verification, finalization, and
domain separation remain separate future work.

`PHASE294_PROMOTED_CANDIDATE_TO_DRAFT_PATCH_PROPOSAL_ARTIFACT_SOURCE_TEST_DOCS_PROVEN=PASS`
