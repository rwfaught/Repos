# Dossier Case Abstraction

Boundary: `DOSSIER_CASE_ABSTRACTION_FOUNDER_RATIFICATION_DESIGN_DOCS_ONLY`

Status: founder-ratification design document. Docs-only. Not implementation.

Marker: `DOSSIER_CASE_ABSTRACTION_FOUNDER_RATIFICATION_DESIGN_DOCS_ONLY_REGISTERED=DOCS_ONLY`

## Executive Summary

The neutral dossier/case abstraction is the current bridge between two live
product directions:

- claims/disputes/appeals casework
- game/worldbuilding/design dossier work

The purpose is not to erase domain differences. The purpose is to name the
shared workflow bones that already appear in the source and design record:
objectives, source materials, extracted facts, chronology, open questions,
missing evidence or canon, contradictions, drafts, decisions, next work items,
review posture, and operator approvals.

This document prepares Roger to ratify the first product wedge without Codex
choosing it by implementation momentum.

## Definition

A dossier/case is a bounded work container for a human objective that depends on
source material, structured interpretation, visible uncertainty, drafts,
decisions, and review.

Plain-English version:

A dossier/case is the folder the system keeps for a complicated matter so Roger
or a future user can see what is known, what is missing, what conflicts, what
has been drafted, what has been decided, and what should happen next.

## Purpose

The abstraction exists to preserve useful case-packet work while preventing
claims/disputes/appeals from remaining the product center by inertia.

It should let the project compare two different first proving domains without
throwing away shared structure:

- consequential admin casework such as claims, disputes, appeals, billing
  disputes, reimbursement packets, or benefits appeals
- creative/design casework such as lore dossiers, setting packets, faction
  briefs, mechanics design files, campaign history, or worldbuilding canon

## Existing Case-Packet Mapping

Accepted source/design record:

- `docs/PRODUCT_DESIGN_02.md` defines a case-state structure around identity,
  source materials, extracted facts, timeline, open issues, missing materials,
  contradictions, drafts, user decisions, and next step.
- `docs/DOMAIN_LOCK_IN_AUDIT.md` records that the case-packet substrate may be
  reusable as a dossier packet.
- `docs/FIRST_PRODUCT_WEDGE_DECISION.md` records a candidate dossier/case
  packet with objective, source materials, extracted facts, chronology, open
  questions, missing evidence or canon, contradictions, drafts, decisions, next
  work items, review posture, and operator approvals.

Mapping:

| Existing case-packet concept | Neutral dossier/case concept | Notes |
| --- | --- | --- |
| Case identity | Dossier/case objective and label | Domain label changes; bounded objective remains. |
| Source materials | Source materials | Evidence in admin work; canon/reference material in creative work. |
| Extracted facts | Extracted facts | Must preserve source linkage and confidence. |
| Timeline / events | Chronology / timeline / history | Claim history or world/campaign/design history. |
| Open issues / claims under dispute | Open questions | Disputed issue in admin work; unresolved design/canon question in creative work. |
| Missing evidence / missing materials | Missing evidence / missing canon | Evidence gap or canon/reference gap. |
| Contradictions / unresolved conflicts | Contradictions | Conflicting invoices, dates, rules, lore, constraints, or design statements. |
| Drafts / prepared outputs | Drafts | Letters, summaries, briefs, design notes, lore pages, or mechanics drafts. |
| Decisions / approvals / user-owned judgments | Decisions and operator approvals | Human-owned judgment must remain explicit. |
| Current case status / next step | Next work items and review posture | Shows what is active, waiting, blocked, or ready for review. |

## Shared Fields

### Objective

The bounded purpose of the dossier/case.

Examples:

- recover a disputed reimbursement
- prepare an appeal packet
- stabilize a faction brief
- reconcile conflicting setting canon
- design a combat subsystem

### Source Materials

The raw materials the work depends on.

Admin casework may include PDFs, invoices, denial letters, receipts, policy
excerpts, forms, screenshots, emails, and user notes.

Creative/design dossier work may include campaign notes, lore documents,
rulebooks, maps, faction notes, character briefs, mechanics drafts, art
references, and user-authored canon.

### Extracted Facts

Structured claims drawn from source materials, with provenance.

This field must not flatten source material into confirmed truth. It should
preserve what was extracted, where it came from, and whether Roger or the user
has confirmed it.

### Chronology / Timeline / History

The ordered sequence of relevant events or developments.

In admin casework, this may be invoice, payment, denial, appeal, response, and
deadline history.

In creative/design work, this may be world history, campaign events, design
iterations, faction chronology, or prior decisions.

### Open Questions

Questions still unresolved.

These may be contested issues in a claim or unresolved design/canon questions
in a dossier.

### Missing Evidence / Missing Canon

Known gaps.

Admin examples: missing receipt, missing policy excerpt, missing email, missing
deadline confirmation.

Creative examples: missing faction motivation, missing map constraint, missing
rule interaction, missing lore source, missing decision record.

### Contradictions

Visible conflicts that should not be buried as generic uncertainty.

Admin examples: two invoice totals, conflicting denial reasons, date mismatch,
policy text that conflicts with a form.

Creative examples: two incompatible lore statements, a mechanic that conflicts
with the design pillar, a timeline inconsistency, or a faction goal that
contradicts prior canon.

### Drafts

Prepared outputs not yet equivalent to approved action or final canon.

Admin examples: appeal letter, evidence summary, reimbursement checklist.

Creative examples: lore brief, design proposal, encounter outline, faction
memo, rule rewrite.

### Decisions

Human-owned judgments.

The system may preserve, prepare, and recommend. It must not quietly convert
its own interpretation into Roger's decision.

### Next Work Items

The concrete next steps that would advance the dossier/case.

These should stay bounded enough to become future task packets if Roger
authorizes implementation.

### Review Posture

The current trust/readiness status of the dossier/case.

Examples: draft only, needs source review, needs Roger decision, blocked on
missing material, ready for narrow implementation planning, or ready for
domain-specific branch design.

### Operator Approvals

Explicit approvals and non-approvals.

This preserves the distinction between prepared, reviewed, approved, sent,
accepted, canonized, or implemented.

## Domain Differences

### Claims / Disputes / Appeals

This domain is consequential, evidence-heavy, and risk-sensitive. It may involve
money, deadlines, policies, third parties, and external communication.

It needs stronger caution around:

- provenance
- missing evidence
- contradiction visibility
- draft vs sent communication
- user approval before external action
- legal/policy non-advice boundaries
- privacy and selective exposure

### Game / Worldbuilding / Design

This domain is creative, founder-native, and lower external risk. It may still
need rigor because canon drift, contradictory design constraints, and hidden
decisions can make a world or game system incoherent.

It needs stronger support around:

- canon/source separation
- creative alternatives
- design rationale
- thematic consistency
- rule and lore contradictions
- decision history
- iteration without premature closure

## Shared Workflow Bones

Both domains need:

- bounded objective
- source inventory
- extracted facts or canon points
- chronology/history
- unresolved questions
- missing materials
- contradiction tracking
- draft preparation
- explicit decisions
- next work items
- review gates
- operator approvals

This is the justification for using a neutral bridge before selecting the final
first product wedge.

## What Remains Domain-Specific

Domain-specific material should remain outside the neutral core:

- legal, policy, insurance, reimbursement, or benefits vocabulary
- counterparty and external communication rules
- deadlines and procedural risk
- game setting, lore, mechanics, factions, and campaign vocabulary
- design pillars, creative tone, canon hierarchy, and playtest criteria

The neutral abstraction should not become a bland universal schema that hides
what actually matters in each domain.

## Minimal Structural Fixture Check

The `DOSSIER_CASE_MINIMAL_FIXTURE_SOURCE_TEST_DOCS` boundary adds two
deterministic structural examples over the neutral mapping/readback seam:
`admin_case_shape` and `creative_dossier_shape`.

These examples are not domain implementations. They exist only to show that two
different example shapes can be represented through the same neutral
dossier/case fields while preserving missing material, contradiction,
draft/decision, next-work, review-posture, no-wedge, and non-proof posture.

## What Remains Domain-Neutral

The following can remain shared:

- state container shape
- source/fact distinction
- contradiction visibility
- missing-material tracking
- draft/approval distinction
- review posture
- next bounded work item
- operator decision readback
- non-proof language

## Implications For Future Source Changes

No source changes are authorized by this document.

If Roger ratifies the bridge, a later implementation-planning boundary should
inspect existing `case_packet` modules and decide whether to:

- leave `case_packet` as the claims/disputes/appeals branch
- add a separate neutral `dossier_packet` layer
- wrap the existing case-packet substrate without renaming it
- rename only after tests and migration risks are explicit

Any mutating boundary must name allowed files, excluded files, tests, proof
requirements, rollback/stopping conditions, and non-proofs.

## Accepted Facts

- Phase 387 is parked and not authorized by sequence momentum.
- Claims/disputes/appeals is historically documented and source-relevant.
- Claims/disputes/appeals is not current forward ratification by itself.
- Option C is the current bridge.
- The case-packet substrate exists as early product substrate.
- Game/worldbuilding/design dossier work is not yet present as a named source
  surface.

## Inference

The shared fields are strong enough to justify a neutral design bridge.

This does not prove that a single implementation should serve both domains, or
that either domain should be selected as the first proving wedge.

## Neutral Task Readiness Check

The `DOSSIER_CASE_TASK_READINESS_SOURCE_TEST_DOCS` boundary adds a deterministic
neutral task-readiness report over the existing mapping, readback, and fixture
seams.

The report is a structural readiness check only. It does not choose
claims/disputes/appeals, does not choose game/worldbuilding/design, does not
resume Phase 387, and does not prove semantic or production readiness.

## Recommendation

Use this abstraction as a ratification bridge only. Roger should next choose
whether to keep claims/disputes/appeals, pivot to game/worldbuilding/design
dossier work, or authorize implementation planning for the neutral bridge
before choosing the final first proving domain.

## Non-Proofs

This document is design only.

It does not implement a schema, add code, run tests, execute runtime/provider/
model behavior, prove semantic correctness, prove production readiness, prove
claims/disputes/appeals competence, prove a game/worldbuilding/design workflow,
refresh Source Files, create capsule/export/package proof, resume Phase 387,
authorize wedge implementation, or select the first product wedge. In short:
no wedge selection.
