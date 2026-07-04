# Domain Lock-In Audit

Boundary: `FOUNDER_CONTROL_AND_SOURCE_REALITY_DOCS_ONLY`

Status: source-reality audit and strategic bridge record.

Marker: `DOMAIN_LOCK_IN_AUDIT_REGISTERED=DOCS_ONLY`

## Executive Summary

The repo has meaningful claims/disputes/appeals lock-in at the strategy/design
and early case-packet layer. The core orchestration machinery is less locked in.
A shift toward game/worldbuilding/design dossier work would not be a trivial
rename, but it would also not require throwing away the core project.

Current estimate: medium steering correction.

The recommended bridge is Option C: preserve case-packet work while generalizing
the first-product surface into a neutral dossier/case abstraction until Roger
explicitly ratifies the first proving domain.

## Categories

### Claims / Disputes / Appeals-Specific

These surfaces currently pull the project toward consequential paperwork,
administrative casework, claims, disputes, appeals, reimbursements, benefits,
or similar document-heavy work.

Representative docs:

- `docs/PRODUCT_STRATEGY_03.md`
- `docs/PRODUCT_DESIGN_01.md`
- `docs/PRODUCT_DESIGN_02.md`
- `docs/RERANK_01.md`
- `docs/RERANK_01_RESULT.md`
- `docs/PHASE_58.md`
- `docs/PHASE_59.md`
- `docs/PHASE_60.md`

Interpretation:

This is the strongest current product-wedge lock-in. It is real historical
strategy/design record. It is not current founder ratification by itself.

### General Casework-Specific

These surfaces are case-shaped but not necessarily claims/disputes/appeals-only.

Representative source family:

- `orchestrator/case_packet.py`
- `orchestrator/case_packet_persistence.py`
- `orchestrator/case_packet_task_candidate_review.py`
- `orchestrator/case_packet_task_creation_authorization.py`
- `orchestrator/case_packet_task_creation_write_gate.py`
- `orchestrator/case_packet_task_execution_authorization.py`
- `orchestrator/case_packet_task_execution_candidate_surface.py`
- `orchestrator/case_packet_task_execution_result_review.py`
- `orchestrator/case_packet_task_execution_result_response_options.py`

Interpretation:

This layer may be reusable. A case packet is structurally close to a dossier
packet: objective, source material, facts, timeline, missing pieces,
contradictions, drafts, and decisions.

### Domain-Neutral Orchestration Machinery

These surfaces are not inherently tied to any first product wedge.

Representative source family:

- `orchestrator/engine.py`
- `orchestrator/run_manager.py`
- `orchestrator/state.py`
- `orchestrator/artifact_store.py`
- `orchestrator/task_schema.py`
- `orchestrator/paths.py`
- `orchestrator/intake_admission_pipeline.py`
- `orchestrator/boundary_packet.py`
- `orchestrator/capability_registry.py`
- `orchestrator/route_proposal.py`
- `orchestrator/route_selection_readiness.py`
- `orchestrator/manual_review_runner.py`
- `orchestrator/manual_review_cli.py`
- `orchestrator/recommendation_store.py`
- `orchestrator/reviewer_output.py`

Interpretation:

This is the chassis. It can carry more than one payload if the product language
and packet shapes remain disciplined.

### Product-Task / Coding-Task-Specific

These surfaces mostly concern building Orchestrator itself through bounded
coding/product task packets.

Representative source family:

- `orchestrator/operator_coding_task_packet.py`
- `orchestrator/operator_coding_task_packet_cli.py`
- `orchestrator/operator_packet_result_decision.py`
- `orchestrator/packet_cli_residue_guard.py`
- `orchestrator/patch_proposal.py`
- `orchestrator/patch_apply_engine.py`
- `orchestrator/patch_apply_authorization.py`
- `orchestrator/authorized_draft_patch_apply.py`
- `orchestrator/product_task_packet_*`

Interpretation:

This is builder machinery. It is useful and often well-governed, but it should
not be mistaken for the first user-facing product wedge.

### Potentially Reusable for Game / Worldbuilding / Design

Potentially reusable surfaces:

- artifact persistence
- review/readback records
- case-packet state categories
- backbone fixture mapping concepts
- source-material and extracted-fact vocabulary
- contradiction / open-issue / missing-evidence fields
- draft and decision records
- operator-visible next-step surfaces

Interpretation:

A worldbuilding/design dossier has many of the same structural needs as a case
packet:

- objective
- canon/source material
- extracted facts
- timeline/history
- contradictions
- open questions
- drafts
- decisions
- next work items

The emotional and strategic domain is different. The data shape is not alien.

### Unclear / Needs Deeper Inspection

The following require later targeted inspection before any refactor:

- how deeply case-packet tests assert claims/dispute examples
- whether `case` should remain the general abstraction or be split from
  `dossier`
- whether product strategy docs should be superseded or amended
- whether existing case-packet modules should be renamed, wrapped, or left as a
  specialized branch
- whether a neutral `dossier_packet` substrate should be added beside
  `case_packet`

## Option C Strategic Bridge

Option C is adopted as the current interim bridge:

Preserve the case-packet work, but stop allowing claims/disputes/appeals to act
as the gravitational center until Roger explicitly ratifies that domain again.

Option C keeps three truths visible:

1. The existing case-packet work has value and should not be discarded.
2. The first product wedge remains unratified in the current founder context.
3. A neutral dossier/case abstraction can preserve technical continuity while
   giving Roger room to choose the proving domain with founder-level judgment.

## Pivot Severity Estimate

Light correction would mean only changing labels. That is not accurate.

Major identity fork would mean the core engine is specialized around
claims/disputes/appeals. That is also not accurate.

The best estimate is medium steering correction.

Why medium:

- strategy/design docs point strongly at claims/disputes/appeals
- early case-packet docs and examples reinforce that direction
- core engine and governance machinery remain domain-neutral enough to reuse
- dossier-style work is structurally compatible with the case-packet idea
- founder-facing docs need to stop treating old product strategy as automatic
  current ratification

## Non-Proofs

This audit does not prove that a game/worldbuilding/design product path exists.
It does not prove that claims/disputes/appeals is wrong. It does not perform a
refactor, rename modules, run tests, or select the first product wedge.

It only records the current lock-in posture and the authorized bridge.
