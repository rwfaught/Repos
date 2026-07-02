# Phase 297 - Draft Patch Proposal Authorization Bridge Operator Runbook

Boundary:

`PHASE297_DRAFT_PATCH_PROPOSAL_AUTHORIZATION_BRIDGE_OPERATOR_RUNBOOK_DOCS_ONLY`

## Purpose

Create operator-facing docs for the promoted-candidate-to-draft-proposal-to-
authorization-eligibility bridge.

This phase is docs-only. It does not mutate source behavior, create apply
authorization, apply patches, call provider/model/runtime/platform behavior, or
claim production patch workflow readiness.

## Files Changed

- `docs/PACKET_TO_PATCH_BRIDGE_OPERATOR_RUNBOOK.md`
- `docs/PHASE_297.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Behavior

No product behavior changed.

The runbook now explains promoted candidates, draft patch proposal artifacts,
`draft_only`, `not_authorized_for_apply`, `not_applied`, authorization
eligibility readback, why eligibility is not authorization, why draft creation
is not authorization, why candidate promotion is not authorization, why packet
acceptance is not authorization, required evidence fields, timestamps, shell
context, non-proofs, no actual apply authorization in this campaign, no actual
patch apply in this campaign, source ZIP hygiene caveats, and the Backbone V0
open thread.

## Validation Commands

- `git diff --check`
- proof marker search
- changed-file allowlist audit
- clean git status

## Proof Scope

This phase proves only docs/control registration of operator-facing bridge
language. It documents how to read the evidence chain and preserves the
authorization eligibility versus authorization boundary.

## Non-Proofs

This phase does not prove source behavior, test behavior, semantic correctness,
autonomous AI coding, model-backed generation, provider/model/runtime
execution, runtime/platform behavior, production readiness, service/API/UI/
dashboard/auth/deployment behavior, scheduler/reminder/connector behavior,
`general_answer` resumption, platform/OpenClaw/Hermes/LightRAG behavior,
cleanup/delete/archive authority, actual apply authorization, patch apply
execution, integrated production patch workflow readiness, or Backbone V0.

`PHASE297_DRAFT_PATCH_PROPOSAL_AUTHORIZATION_BRIDGE_OPERATOR_RUNBOOK_DOCS_ONLY_PROVEN=PASS`
