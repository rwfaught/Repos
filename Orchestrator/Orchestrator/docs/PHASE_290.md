# Phase 290 - Patch Proposal Candidate Operator Promotion Gate

## Boundary

`PHASE290_PATCH_PROPOSAL_CANDIDATE_OPERATOR_PROMOTION_GATE_SOURCE_TEST_DOCS`

## Purpose

Phase 290 adds an explicit operator promotion gate for packet-derived patch
proposal candidates. It persists promotion, rejection, and defer records for
valid `candidate_only` artifacts.

This phase conservatively stops at promotion records. It does not create a
draft patch proposal, does not authorize patch apply, and does not apply a
patch.

## Files Changed

- `orchestrator/patch_proposal_candidate_promotion.py`
- `tests/test_phase_290_patch_proposal_candidate_operator_promotion_gate.py`
- `docs/PHASE_290.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Validation Commands

- `python -m py_compile orchestrator\patch_proposal_candidate_promotion.py tests\test_phase_290_patch_proposal_candidate_operator_promotion_gate.py`
- `python -m unittest tests.test_phase_290_patch_proposal_candidate_operator_promotion_gate`
- `python -m unittest tests.test_phase_288_packet_result_to_patch_proposal_eligibility_contract`
- `python -m unittest tests.test_phase_289_packet_result_patch_proposal_candidate_artifact`
- Relevant packet/current-success and patch-spine regressions listed in the
  worker validation report.
- `git diff --check`
- Search proof marker:
  `PHASE290_PATCH_PROPOSAL_CANDIDATE_OPERATOR_PROMOTION_GATE_SOURCE_TEST_DOCS_PROVEN=PASS`
- Changed-file allowlist audit.

## Proof Marker

`PHASE290_PATCH_PROPOSAL_CANDIDATE_OPERATOR_PROMOTION_GATE_SOURCE_TEST_DOCS_PROVEN=PASS`

## Proof Scope

Phase 290 proves only a deterministic operator gate that persists promotion
records with decisions `promote_to_patch_proposal_candidate_ready`,
`reject_candidate`, and `defer_candidate` for valid `candidate_only` artifacts
with non-empty operator notes/reasons. The record preserves candidate, packet,
run, task, execution artifact, verifier, operator decision, and eligibility
evidence while explicitly marking no patch proposal creation, no apply
authorization, and no patch application.

## Non-Proofs

Phase 290 does not prove semantic correctness, live provider/model execution,
runtime/platform behavior, autonomous AI coding, model-backed generation,
production readiness, service/API/UI/dashboard/auth/deployment behavior,
scheduler/reminder behavior, connector behavior, `general_answer` resumption,
platform/OpenClaw/Hermes/LightRAG behavior, cleanup/delete/archive authority,
draft patch proposal creation, authorized patch proposal creation, patch apply
authorization from packet acceptance, patch apply authorization from candidate
creation, patch apply authorization from candidate promotion, patch
application, or integrated production patch workflow readiness.

## Caveats

- Accepted packet decisions alone cannot promote candidates.
- Candidate promotion means ready for a later explicit patch proposal boundary,
  not authorized for apply.
- The existing patch proposal spine remains adjacent but not integrated by this
  phase.
- Source ZIP uploads may include generated `__pycache__` or `.pyc` entries
  depending on operator packaging; product capsule proof should come from the
  official product capsule refresh output, not source upload hash alone.

## Generated Artifact / Residue Posture

Phase 290 adds a promotion record writer under product data only when called by
an explicit caller. The phase tests use temporary promotion directories. The
phase does not clean, delete, archive, accept packet residue, invoke providers,
or touch patch apply code.
