# Narrow Evidence-Linked Synthesis Transformation Contract

Boundary: `ORCHESTRATOR_NARROW_EVIDENCE_LINKED_SYNTHESIS_TRANSFORMATION_SOURCE_TEST_DOCS_IMPLEMENTATION`

## Purpose

`orchestrator.evidence_linked_synthesis` deterministically validates and presents one caller-supplied structured dossier packet as a reviewable recommendation package. It is a transformation seam, not recommendation generation: the caller supplies source records, classifications, candidate assessments, prioritization judgment, authorization state, and disposition.

## Input and validation

The packet includes a bounded case frame; source and statement registers (a statement may supply `text` or `value`); constraint, contradiction, and missing-information registers; a problem frame; candidates and extensible assessments (a rating may be supplied as `rating` or `classification`); explicit prioritization; recommendation claims; `NeutralEvidenceLink` records; gates; authorizations and non-authorizations; non-proofs; disposition; and optional revision relationships.

`NeutralEvidenceLink` remains an asserted typed-subject-to-source association. The transformation validates its existing shape and verifies that its supplied source and subject references are local to the packet. It does not change the link's non-proof semantics, infer associations, repair references, or create a global relationship graph.

The validator returns stable machine-readable errors and a blocked result when a required case frame or source inventory is absent, references are unresolved, a material recommendation claim has no registered statement basis and direct evidence link, a hard constraint is violated, a critical unresolved gap blocks work, an authorization is absent, a retired identity is selected, or a revision overwrites rather than references a prior recommendation.

Missing-information statuses are explicit: `unknown`, `not_collected`, `unavailable`, `not_applicable`, and `resolved`. Absence is never treated as `not_applicable`.

## Output

On success, the package exposes the case frame, problem statement, evidence summary and classifications, qualifications, contradictions, gaps, constraints, candidate comparison, caller-judged selection, recommendation claims, evidence associations, assessments, gates, authorization surfaces, non-proofs, next bounded action, disposition, and revision relationships. Every output section has an explicit transformation posture from `copied`, `selected`, `grouped`, `derived`, `inferred`, `judged`, or `presentation_only`.

Each material recommendation claim separately exposes supporting statement references, qualifications, contradicting basis, unresolved gaps, and caller-supplied judgment posture. Repeating a statement does not create independent confirmation, and no prose certainty is evaluated.

## Boundaries and non-proofs

This module is packet-local and non-persistent. It does not extract raw prose, discover links, resolve contradictions, infer gaps, score candidates, select recommendations, decide authorization, rewrite disposition, call a model or provider, implement Phase 5 provenance, implement Phase 6 workflow, or encode consulting/HVAC rules. Passing focused tests proves deterministic structural validation and presentation only; it does not prove evidence truth, quality, sufficiency, recommendation correctness, real-client value, product-wedge suitability, security, privacy compliance, or production readiness.
