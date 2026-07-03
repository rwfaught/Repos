# Backbone V0 Preservation Semantics

This document separates Backbone V0 preservation concepts that can otherwise
look similar in handoff prompts, source snapshots, Git refs, and capsule
records.

## Declaration-preservation fork

A declaration-preservation fork is a historical preservation point for the
moment Backbone V0 was declared.

Current instance:

- Phase 337
- Commit: `12e70023d638c0f919aa8e00e50ceccfaf36a6de`
- Tag: `backbone-v0-structural-declaration`
- Branch: `fork/backbone-v0-structural-declaration`

This remains valid and must not be moved. It preserves the declaration moment.
It was not wrong. It does not include later Phase 338, Phase 340, or Phase 342
orientation surfaces.

## Post-declaration build-off preservation candidate

A post-declaration build-off preservation candidate is a stronger practical
preservation point for future users/future Roger because it includes the
declaration plus post-declaration orientation/governance surfaces.

Current candidate:

- Phase 342
- Commit: `bf81ad0c07f40e53c3285da511316679bc763ee9`
- Marker name: `backbone-v0-post-declaration-consolidation`

Treating Phase 337 as the best build-off point is too strong after Phase 342
because Phase 338 added declaration readback/status, Phase 340 added the
proof-chain operator index, and Phase 342 added the source inspection report
surface. Phase 342 is therefore a better practical orientation candidate for
future work, while Phase 337 remains the correct historical declaration fork.

Phase 343 documented this candidate without creating refs. A later ref-only
boundary created and verified the second preservation marker:

- Boundary:
  `PHASE343_BACKBONE_V0_POST_DECLARATION_CONSOLIDATION_REF_PRESERVE_AND_VERIFY`
- Result marker:
  `PHASE343_BACKBONE_V0_POST_DECLARATION_CONSOLIDATION_REF_PRESERVE_AND_VERIFY_RESULT=PASS`
- Branch: `fork/backbone-v0-post-declaration-consolidation`
- Annotated tag: `backbone-v0-post-declaration-consolidation`
- Target commit: `bf81ad0c07f40e53c3285da511316679bc763ee9`
- Annotated tag object:
  `ed0ce5ef5c4540af1a3e9ea973896360ae94e734`

This second marker does not replace or move the Phase 337 declaration-
preservation refs.

## Official clean capsule proof

An official clean capsule proof is a separately recorded official clean product
capsule proof.

Current accepted proof:

- Phase 335 only
- SHA256:
  `04cb5a2205bedcef767d8cab6344237e9b4ce1f75f19793a56425ab8b197d49d`

Phase 337, Phase 338, Phase 340, Phase 342, and Phase 343 do not extend this
official clean capsule proof.

## Source Files handoff snapshot

A Source Files handoff snapshot is an orientation artifact for ChatGPT/source
file handoffs.

It may lag Git truth and may contain `__pycache__` or `.pyc` entries. This is
not product failure by itself. It is not official capsule proof.

## Why the Phase 337 fork remains untouched

The existing Phase 337 tag and branch preserve the declaration moment. Moving
them would blur historical declaration preservation with later practical
build-off orientation. The useful separation is to leave
`backbone-v0-structural-declaration` and
`fork/backbone-v0-structural-declaration` on Phase 337 while documenting a
separate post-declaration candidate.

## Why a second marker may be useful

A second marker helps future users/future Roger build from a point that
includes declaration readback, proof-chain indexing, and source inspection
orientation. The created and verified second marker name is:

`backbone-v0-post-declaration-consolidation`

The corresponding branch is:

`fork/backbone-v0-post-declaration-consolidation`

Both target Phase 342 commit:

`bf81ad0c07f40e53c3285da511316679bc763ee9`

The annotated tag object observed for this marker is:

`ed0ce5ef5c4540af1a3e9ea973896360ae94e734`

Phase 344 records this prior ref-only result; it does not create, move,
delete, or push tags or branches.

## Non-Proofs

This preservation semantics document does not imply production readiness,
semantic correctness, runtime/provider/model/platform execution, live domain
execution, adapter execution, service/API/UI/dashboard/auth/deployment
readiness, capsule/export/package refresh, or official capsule proof beyond
the Phase 335 record.

Marker:

`PHASE343_BACKBONE_V0_POST_DECLARATION_PRESERVATION_SEMANTICS_DOCS_ONLY_PROVEN=PASS`

Phase 344 record marker:

`PHASE344_BACKBONE_V0_POST_DECLARATION_CONSOLIDATION_REF_RECORD_DOCS_ONLY_PROVEN=PASS`
