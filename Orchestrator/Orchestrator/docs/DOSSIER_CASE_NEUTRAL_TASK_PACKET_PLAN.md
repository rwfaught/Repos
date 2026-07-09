# Dossier/Case Neutral Task Packet Plan

Boundary: `DOSSIER_CASE_NEUTRAL_TASK_PACKET_PLAN_DOCS_ONLY`

Status: docs-only planning artifact. This is planning, not implementation.

## Plain-English Operator Purpose

This document defines a tiny neutral task packet shape for Roger/CTO review.
It turns the ratified neutral dossier/case task-readiness review into the next
smallest inspectable product-shaped planning artifact without selecting a first
product wedge.

The packet shape is domain-neutral. It is meant to make future work easier to
review before any source/test/docs implementation boundary is written.

Worker/Codex is not selecting a product wedge.

## Current Posture Preserved

- no first product wedge selected
- Phase 387 remains parked
- this plan is not runtime/provider/model proof
- this plan is not production readiness
- this plan does not commit to claims/disputes/appeals as the first product
  wedge
- this plan does not commit to game/worldbuilding/design as the first product
  wedge
- this plan does not authorize runtime, provider, model, platform, bridge,
  installer, Discord, production, cleanup, export, archive, or package work

## Proposed Neutral Task Packet Fields

A later neutral task packet should be small enough for Roger/CTO to inspect in
one pass. Proposed fields:

- `packet_id`: stable neutral identifier for the packet.
- `boundary_name`: proposed future boundary name, not authorization by itself.
- `operator_goal`: plain-English outcome the operator wants to inspect.
- `neutral_subject`: domain-neutral object being examined, such as a dossier,
  case, packet, record, or request.
- `inputs_available`: named source materials, records, notes, fixtures, or
  operator-provided facts available to the packet.
- `required_neutral_fields`: structural fields expected by the neutral
  dossier/case readiness seam.
- `open_questions`: unresolved questions that must stay visible.
- `contradictions_or_tensions`: known conflicts, mismatches, or uncertainties.
- `decisions_needed`: choices Roger/CTO must make before implementation can
  narrow the work.
- `next_work_items`: smallest proposed source/test/docs tasks after review.
- `blocked_until`: decisions or evidence required before the packet can become
  a domain-specific implementation boundary.
- `success_shape`: what a later implementation boundary would need to show at
  source/test/docs level.
- `explicit_non_proofs`: what the packet and any later source/test/docs pass
  would still not prove.
- `runtime_provider_model_posture`: explicit statement that runtime,
  provider, and model execution remain excluded unless a later boundary
  authorizes them.
- `phase_387_posture`: explicit statement that Phase 387 remains parked unless
  Roger or CTO/coordinator separately authorizes it.
- `wedge_posture`: explicit statement that no first product wedge selected is
  preserved.

## Example Neutral Packet Outline

```text
packet_id: neutral-task-packet-001
boundary_name: FUTURE_NEUTRAL_TASK_PACKET_SOURCE_TEST_DOCS
operator_goal: Inspect whether a neutral dossier/case-shaped packet is ready
  for a later bounded implementation boundary.
neutral_subject: A domain-neutral dossier/case candidate.
inputs_available:
  - current neutral readiness review
  - operator-provided neutral packet notes
  - existing source/test/docs seam names, if a future boundary names them
required_neutral_fields:
  - packet identity
  - available inputs
  - open questions
  - contradictions or tensions
  - decisions needed
  - next work items
open_questions:
  - What domain, if any, should later become the first proving domain?
  - Should the project continue abstraction-first before selecting a wedge?
contradictions_or_tensions:
  - Product-shaped planning is useful, but implementation inertia must not
    select a wedge.
decisions_needed:
  - Roger/CTO must choose a domain or explicitly continue abstraction-first
    before domain-specific implementation.
next_work_items:
  - Draft a source/test/docs boundary only after Roger/CTO reviews this packet
    shape.
blocked_until:
  - Roger chooses a domain, or Roger/CTO explicitly continues abstraction-first.
success_shape:
  - A later source/test/docs boundary would need to prove that the neutral
    packet fields can be represented, read back, and checked without domain
    claims.
explicit_non_proofs:
  - not runtime/provider/model proof
  - not production readiness
  - not semantic correctness
  - not first product wedge selection
runtime_provider_model_posture: Excluded unless separately authorized later.
phase_387_posture: Phase 387 remains parked.
wedge_posture: no first product wedge selected.
```

This outline is intentionally neutral. It makes no claims/disputes/appeals
product commitment and no game/worldbuilding/design product commitment.

## Structural Acceptance Criteria

Roger/CTO can accept this planning artifact structurally if it:

- names the boundary
  `DOSSIER_CASE_NEUTRAL_TASK_PACKET_PLAN_DOCS_ONLY`
- defines a tiny neutral task packet shape
- keeps the packet domain-neutral
- preserves no first product wedge selected
- states that Worker/Codex is not selecting a product wedge
- preserves that Phase 387 remains parked
- states that it is planning, not implementation
- states that it is not runtime/provider/model proof
- states that it is not production readiness
- avoids claims/disputes/appeals product commitment
- avoids game/worldbuilding/design product commitment
- identifies what a later source/test/docs implementation boundary would need
  to prove
- identifies what remains blocked until Roger chooses a domain or explicitly
  continues abstraction-first

## What A Later Source/Test/Docs Boundary Would Need To Prove

A future implementation boundary, if authorized, would need to prove only the
bounded structural claims it names. Likely proof targets:

- the neutral packet fields can be represented in source
- required fields can be read back or reported
- missing fields can be detected without domain-specific assumptions
- open questions, contradictions, decisions, and next work items remain visible
- no first product wedge selected remains explicit unless Roger has selected
  one in a separate boundary
- Phase 387 remains parked unless separately authorized
- runtime/provider/model execution remains excluded unless separately
  authorized
- fixtures or examples remain structural and do not become product-domain proof

That later boundary would still not prove semantic correctness, product
usefulness, runtime/provider/model behavior, production readiness, or Roger's
acceptance unless those are separately authorized and evidenced.

## What Remains Blocked

The following remain blocked until Roger chooses a domain or Roger/CTO
explicitly continues abstraction-first:

- domain-specific implementation planning
- product workflow optimization for claims/disputes/appeals
- product workflow optimization for game/worldbuilding/design
- Phase 387 implementation or resume work
- runtime/provider/model proof work
- production-readiness claims
- Source Files refresh, export, capsule, archive, cleanup, or package work

## Next Possible Boundaries After This Plan

Possible future boundaries, without selecting one:

1. `NEUTRAL_TASK_PACKET_SOURCE_TEST_DOCS`

   Implement a tiny neutral packet representation and readback/check surface at
   source/test/docs level, still without selecting a product wedge.

2. `FIRST_PRODUCT_WEDGE_SELECTION_RECORD_DOCS_ONLY`

   Record Roger's explicit product-wedge choice if he makes one.

3. `CONTINUE_ABSTRACTION_FIRST_RATIFICATION_RECORD_DOCS_ONLY`

   Record an explicit Roger/CTO decision to continue abstraction-first without
   selecting a first product wedge.

4. `PHASE_387_RESUME_DECISION_DOCS_ONLY`

   Decide whether Phase 387 should remain parked or be separately resumed.

5. `SOURCE_FILES_REFRESH_EXPORT_AFTER_TASK_READINESS`

   Refresh external Source Files or export/capsule material only if Roger/CTO
   explicitly wants a portable snapshot.

## Non-Proofs And Caveats

This plan is not runtime/provider/model proof.

This plan is not production readiness.

This plan is not semantic correctness proof.

This plan is not source/test behavior proof.

This plan is not Phase 387 implementation.

This plan is not first product wedge selection.

This plan is not claims/disputes/appeals product commitment.

This plan is not game/worldbuilding/design product commitment.

Worker/Codex is not selecting a product wedge.
