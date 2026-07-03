# Phase 345 - Codex Bounded-Autonomy Prompt Surface

Boundary:

`PHASE345_CODEX_BOUNDED_AUTONOMY_PROMPT_SURFACE_DOCS_ONLY`

## Purpose

Phase 345 adds a docs-only reusable Codex bounded-autonomy prompt/report surface
for Orchestrator product-track work after Backbone V0 declaration and
post-declaration consolidation preservation.

This phase records a worker-task contract for longer Codex runs inside fenced
boundaries. It does not expand product scope or grant Codex coordinator
authority.

## Changed Files

- `docs/PHASE_345.md`
- `docs/CODEX_BOUNDED_AUTONOMY_PROMPT_SURFACE.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Accepted Facts

- Phase 344 is the latest local main commit at the start of this phase:
  `72a8c6f8ad801762e8e739421c1ab34f3dd6c313`
- Remote `main` was observed at:
  `72a8c6f8ad801762e8e739421c1ab34f3dd6c313`
- Phase 337 declaration-preservation target:
  `12e70023d638c0f919aa8e00e50ceccfaf36a6de`
- Phase 342 post-declaration consolidation target:
  `bf81ad0c07f40e53c3285da511316679bc763ee9`
- Phase 344 records the post-declaration consolidation preservation refs in
  docs and preserves the Phase 335 official clean capsule proof caveat.

## Implementation Summary

Phase 345 adds `docs/CODEX_BOUNDED_AUTONOMY_PROMPT_SURFACE.md` as an
operator-facing prompt and report template for bounded Codex work. The surface
preserves coordinator/operator authority, allowed-file discipline, proof/
non-proof separation, lockouts, validation reporting, and local-commit/no-push
separation.

## Validation Checklist

- `git status --short --branch`
- Marker search for
  `PHASE345_CODEX_BOUNDED_AUTONOMY_PROMPT_SURFACE_DOCS_ONLY_PROVEN=PASS`
- Prompt-surface search for `SESSION ROLE`, `BOUNDARY`, `LOCKOUTS`, and
  `REPORT FORMAT`
- `git diff --check`
- changed-file allowlist audit

## Marker

`PHASE345_CODEX_BOUNDED_AUTONOMY_PROMPT_SURFACE_DOCS_ONLY_PROVEN=PASS`

## Non-Proofs

- No source/test code changed.
- No runtime/provider/model/platform execution occurred.
- No WSL, Ollama, OpenClaw, Hermes, LightRAG, Discord, installer, service,
  API, UI, dashboard, auth, deployment, scheduler, connector, or production
  behavior occurred.
- No `general_answer` work occurred.
- No Source Files refresh, capsule refresh, export/package refresh, or official
  capsule proof extension occurred.
- No tag or branch was created, moved, deleted, or pushed in this docs-only
  phase.
- No production readiness is implied.
- No semantic correctness is implied.
- No autonomous AI coding is implied.
- No live domain execution is implied.

## Source/Capsule/Git Truth Separation Caveat

Git repo truth remains separate from Source Files handoff snapshots, official
clean capsule proof, and full Git backups. Phase 345 adds a docs-only prompt
surface and does not refresh or supersede the Phase 335 official clean capsule
proof.
