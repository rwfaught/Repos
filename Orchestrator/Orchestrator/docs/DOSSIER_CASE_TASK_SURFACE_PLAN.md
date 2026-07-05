# Dossier Case Task Surface Plan

Boundary: `DOSSIER_CASE_TASK_SURFACE_PLAN_DOCS_ONLY`

Status: docs-only implementation plan. No source behavior mutation.

Marker: `DOSSIER_CASE_TASK_SURFACE_PLAN_DOCS_ONLY_REGISTERED=DOCS_ONLY`

## 1. Executive Summary

This plan defines the smallest neutral dossier/case task surface that can be
implemented after the current mapping, readback, fixture, and operator-decision
work. It does not select a first product wedge, resume Phase 387, or implement
any domain-specific workflow.

The recommended first task is exactly:
`neutral_task_readiness_report`.

That task should remain deterministic and structural. It should report whether a
dossier/case-shaped dictionary or existing fixture has the neutral fields needed
for later domain-specific work, while explicitly preserving that no product
wedge has been selected and Phase 387 remains unimplemented.

## 2. Accepted Facts From Current Source

- `docs/FIRST_PRODUCT_WEDGE_OPERATOR_DECISION_RECORD.md` records that no first
  product wedge has been selected.
- `docs/FIRST_PRODUCT_WEDGE_RATIFICATION_PACKET.md` preserves Option C:
  continue abstraction-first and choose the product domain later.
- `docs/FOUNDER_COMPREHENSION_SNAPSHOT_CURRENT.md` records Phase 387 as parked
  and the first product wedge as not ratified.
- `docs/DOSSIER_CASE_ABSTRACTION.md` defines a neutral dossier/case vocabulary,
  not a product-domain workflow.
- `docs/DOSSIER_CASE_ABSTRACTION_IMPLEMENTATION_PLAN.md` recommends small,
  bounded mapping/readback/task surfaces before domain selection.
- `docs/DOSSIER_CASE_MAPPING_OPERATOR_REVIEW.md` treats the mapping seam as
  deterministic structural compatibility, not semantic correctness.
- `orchestrator/dossier_case_mapping.py` maps existing case-packet-shaped data
  into neutral dossier/case fields and preserves `NO_FIRST_PRODUCT_WEDGE_SELECTED`.
- `orchestrator/dossier_case_mapping_readback.py` exposes required neutral
  fields, required-field coverage, no-wedge state, Phase 387 false state, and
  explicit non-proofs.
- `orchestrator/dossier_case_minimal_fixture.py` exposes `admin_case_shape` and
  `creative_dossier_shape` as structural examples only.
- Existing tests prove mapping, readback, and fixture posture. They do not prove
  production readiness, semantic reasoning, or domain-specific task execution.

## 3. Purpose Of A Neutral Task Surface

The neutral task surface should convert the existing dossier/case substrate into
a small deterministic work-readiness report. Its job is to make the current
structure easier for a future operator or source boundary to inspect without
forcing a product-domain choice.

It should distinguish:

- neutral task surface: deterministic reporting over neutral dossier/case fields
- product-domain workflow: claims/disputes/appeals, game/worldbuilding/design,
  or any other selected wedge-specific flow
- semantic reasoning: meaning-level judgment that requires interpretation
- deterministic structural readback: direct inspection of fields and flags
- fixture proof: proof that example shapes preserve expected structural posture
- production proof: proof of real workflow execution, persistence, runtime
  behavior, or user-facing readiness

## 4. What The Task Surface Must Not Become

The task surface must not become:

- product wedge selection
- Phase 387 implementation or resume
- claims/disputes/appeals implementation
- game/worldbuilding/design implementation
- legal, policy, canon, game-design, or semantic scoring logic
- runtime/provider/model execution
- persistence migration
- CLI, UI, installer, Discord, OpenClaw, Hermes, platform, WSL, or Ollama work
- Source Files refresh/export/capsule/package work
- production task execution
- broad refactor or cleanup/archive/delete operation

## 5. Minimal Candidate Task Types

Candidate neutral task types are:

- summarize neutral dossier/case field coverage
- list missing required fields
- list open questions
- list contradictions
- list pending decisions
- produce next-operator-action recommendation from structural fields only
- produce neutral task-readiness report

## 6. Recommended First Neutral Task

Recommend exactly one smallest first task:
`neutral_task_readiness_report`.

Given a dossier/case-shaped dictionary or existing fixture, the task should
produce a deterministic report showing:

- required neutral fields present and missing
- open questions
- contradictions
- decisions
- next work items
- whether the structure is ready for domain-specific work
- `product_wedge_selected` expected false
- `phase_387_implemented` expected false
- what the report does not prove

## 7. Inputs And Outputs

Inputs:

- a dossier/case-shaped dictionary
- a dictionary produced through the existing mapping seam
- the current admin or creative minimal fixtures

The task must not require model reasoning, runtime execution, semantic scoring,
legal/policy reasoning, canon reasoning, game-design reasoning, doc generation,
or external files.

Outputs should be plain deterministic data, likely a dictionary with fields such
as:

- `task_name`
- `required_neutral_fields_present`
- `missing_required_neutral_fields`
- `open_questions`
- `contradictions`
- `decisions`
- `next_work_items`
- `structurally_ready_for_domain_specific_work`
- `product_wedge_selected`
- `phase_387_implemented`
- `non_proofs`

## 8. Mapping / Readback / Fixture Dependencies

The future source boundary should reuse the current structural spine:

- mapping: `orchestrator/dossier_case_mapping.py`
- readback: `orchestrator/dossier_case_mapping_readback.py`
- fixtures: `orchestrator/dossier_case_minimal_fixture.py`

The task should depend on required neutral field names and existing readback
posture rather than duplicating domain-specific assumptions. The admin fixture
must remain only an administrative structural example, not
claims/disputes/appeals proof. The creative fixture must remain only a creative
structural example, not game/worldbuilding/design proof.

## 9. Domain Neutrality Requirements

The task should use neutral terms such as required fields, missing fields, open
questions, contradictions, pending decisions, next work items, and readiness.

It must not encode a privileged product domain. Any reference to administrative
or creative fixtures must be described as structural coverage, not domain
workflow correctness.

## 10. Non-Proof Requirements

The report must state that it does not prove:

- first product wedge selection
- Phase 387 implementation
- claims/disputes/appeals product readiness
- game/worldbuilding/design product readiness
- semantic correctness
- legal, policy, canon, or game-design correctness
- runtime/provider/model behavior
- production readiness
- persistence migration
- Source Files refresh/export/capsule/package proof

## 11. Candidate Future Source Files

Candidate future source files for the next source/test/docs boundary:

- `orchestrator/dossier_case_task_readiness.py`

The future boundary should avoid changing existing mapping, readback, or fixture
source unless a narrow import or constant reuse is required.

## 12. Candidate Future Tests

Candidate future tests:

- `tests/test_dossier_case_task_readiness.py`

Expected test coverage:

- reports present/missing required neutral fields
- reports open questions, contradictions, decisions, and next work items
- preserves no-wedge state as false for product-wedge selection
- preserves Phase 387 implementation as false
- accepts admin and creative structural fixtures without treating either as
  product proof
- emits explicit non-proofs
- does not require provider/model/runtime execution or external files

## 13. Minimal Future Implementation Sequence

1. Add a pure source module for `neutral_task_readiness_report`.
2. Reuse existing mapping/readback constants and fixture data where practical.
3. Return deterministic plain data only.
4. Add narrow unit tests for dictionary, admin fixture, and creative fixture
   paths.
5. Update docs and ledgers for the source/test/docs boundary only after tests
   pass.

## 14. Stop Conditions

Stop if the next boundary would require:

- selecting the first product wedge
- resuming or implementing Phase 387
- semantic reasoning or scoring
- legal, policy, canon, or game-design interpretation
- runtime/provider/model execution
- source changes outside the named future task module and its tests
- persistence, CLI, UI, installer, platform, WSL, Ollama, Discord, OpenClaw, or
  Hermes work
- Source Files refresh/export/capsule/package work
- production task execution

## 15. Next Boundary Options

1. `DOSSIER_CASE_TASK_READINESS_SOURCE_TEST_DOCS`
2. `FIRST_PRODUCT_WEDGE_RATIFICATION_RECORD_DOCS_ONLY`
3. `PHASE_387_RESUME_DECISION_DOCS_ONLY`
4. `SOURCE_FILES_REFRESH_EXPORT_AFTER_TASK_SURFACE_PLAN`

## 16. Recommended Next Move

Recommended next boundary:
`DOSSIER_CASE_TASK_READINESS_SOURCE_TEST_DOCS`.

That boundary should implement the pure deterministic
`neutral_task_readiness_report` task with focused tests and documentation. It
should not select a product wedge, resume Phase 387, or claim production proof.
