# Dossier Case Abstraction Implementation Plan

Boundary: `DOSSIER_CASE_ABSTRACTION_IMPLEMENTATION_PLAN_DOCS_ONLY`

Status: implementation plan only. Docs-only. No source behavior mutation.

Marker: `DOSSIER_CASE_ABSTRACTION_IMPLEMENTATION_PLAN_DOCS_ONLY_REGISTERED=DOCS_ONLY`

## 1. Executive Summary

Roger ratified Option 3: build the neutral dossier/case abstraction first, then
choose the first product domain.

This plan prepares that abstraction-first path without implementing it. The
source inspection shows that `orchestrator/case_packet.py` already contains the
core shared fields needed by a neutral dossier/case substrate. The safest future
implementation path is not an immediate rename or broad refactor. It is a small
wrapper/adaptor boundary that makes neutral dossier/case language explicit while
preserving existing case-packet behavior and tests.

This plan does not select claims/disputes/appeals or game/worldbuilding/design
as the first product domain. It only prepares a future small mutation boundary.

## 2. Accepted Facts From Inspected Source

- `docs/DOSSIER_CASE_ABSTRACTION.md` defines the neutral dossier/case
  abstraction as the current bridge between claims/disputes/appeals and
  game/worldbuilding/design dossier work.
- `docs/FIRST_PRODUCT_WEDGE_RATIFICATION_PACKET.md` records Option C as:
  "Build the neutral dossier/case abstraction first, then choose the first
  domain."
- `docs/FOUNDER_COMPREHENSION_SNAPSHOT_CURRENT.md` records that the first
  product wedge is not ratified and that neutral dossier/case schema or code
  should not be implemented until a future boundary.
- `docs/CAPABILITY_REALITY_MAP.md` identifies the bounded coding-task packet
  path as the strongest current proven capability and classifies the
  case-packet substrate as early product substrate.
- `docs/DOMAIN_LOCK_IN_AUDIT.md` estimates the steering correction as medium,
  not a trivial rename and not a total identity fork.
- `docs/OPERATOR_CODEBASE_MAP.md` identifies `orchestrator/case_packet.py` and
  related case-packet modules as the early product substrate for case-like work.
- `docs/FIRST_PRODUCT_WEDGE_DECISION.md` says the first product wedge is not
  settled for forward implementation.
- `docs/TRACKS_AND_OPEN_THREADS.md`, `docs/STARTUP_BRIEF.md`, and
  `docs/CONTEXT_MAP.md` record Phase 387 as parked and the dossier/case bridge
  as design/control work rather than implementation momentum.
- `docs/PROJECT_VISION.md` says present capability is local-first
  orchestration for bounded AI-assisted work, not full general user-facing
  intake.
- `docs/CURRENT_SUCCESS_CRITERION.md` records the current success bar as
  operator-facing bounded coding-task proof and preserves non-proofs around
  semantic correctness, live provider/model behavior, autonomous coding, and
  production readiness.
- `orchestrator/case_packet.py` defines scalar fields `case_id`, `case_type`,
  `title`, `objective`, `status`, and `next_step`.
- `orchestrator/case_packet.py` defines list fields `source_materials`,
  `extracted_facts`, `timeline_events`, `open_issues`, `missing_evidence`,
  `contradictions`, `drafts`, and `decisions`.
- `orchestrator/case_packet.py` normalizes, validates, summarizes, initializes,
  appends to, and updates orientation fields for case packets.
- `orchestrator/case_packet_persistence.py` builds persisted case packets from
  authorized creation input and initializes the same shared fields.
- `orchestrator/case_packet_task_candidate_review.py` reads persisted case
  packets, summarizes source packets, blocks bundled execution/runtime/model
  requests, and surfaces task-candidate readiness.
- The case-packet task creation, execution authorization, execution candidate,
  execution result review, and response option modules form a guarded workflow
  around case-packet-derived tasks.
- Tests already exist for the case-packet substrate and phases 68 through 76,
  plus phase 96 canonical case-packet execution delegation.

## 3. Current Case-Packet Substrate

The current substrate has two layers:

1. A data container in `orchestrator/case_packet.py`.
2. A guarded task workflow around persisted case packets.

The data container is already close to the neutral dossier/case shape. It has:

- identity: `case_id`, `case_type`, `title`
- purpose: `objective`
- posture: `status`, `next_step`
- materials: `source_materials`
- interpretation: `extracted_facts`
- history: `timeline_events`
- unresolved questions: `open_issues`
- gaps: `missing_evidence`
- conflicts: `contradictions`
- prepared outputs: `drafts`
- human/operator judgment: `decisions`

The guarded workflow currently assumes case-packet language. It includes
persistence, task-candidate review, task-creation authorization, write gate,
execution-candidate surfacing, execution authorization, authorized execution,
execution-result review, response options, and canonical delegation.

## 4. Proposed Neutral Dossier/Case Abstraction

The neutral abstraction should be a vocabulary and compatibility layer over the
existing case-packet substrate before it becomes a new behavior branch.

Future implementation should start with a small module that:

- defines neutral field names and their case-packet equivalents
- exposes a read-only mapping from case-packet fields to dossier/case fields
- classifies which fields are shared, domain-specific, or workflow-control
  fields
- preserves existing case-packet behavior unchanged
- avoids choosing claims/disputes/appeals or game/worldbuilding/design

The first mutation should prove that neutral dossier/case language can sit
beside existing case-packet code without breaking current case-packet tests.

## 5. Field Mapping

| Neutral field | Current case-packet field | Implementation note |
| --- | --- | --- |
| objective | `objective` | Reuse unchanged. |
| source materials | `source_materials` | Reuse unchanged; domain examples differ. |
| extracted facts | `extracted_facts` | Reuse unchanged; preserve provenance expectations later. |
| chronology/timeline/history | `timeline_events` | Wrapper should expose neutral alias without renaming storage first. |
| open questions | `open_issues` | Wrapper should expose neutral alias; domain language can vary. |
| missing evidence / missing canon | `missing_evidence` | Reuse as storage initially; wrapper should document evidence/canon meaning. |
| contradictions | `contradictions` | Reuse unchanged. |
| drafts | `drafts` | Reuse unchanged. |
| decisions | `decisions` | Reuse unchanged; keep human-owned judgment explicit. |
| next work items | `next_step` initially, later possibly task candidates | Wrapper should avoid pretending one string is a complete work-item list. |
| review posture | `status`, readiness summaries, review result surfaces | Needs adaptor treatment because posture is spread across modules. |
| operator approvals | `decisions`, authorization modules, response options | Needs adaptor treatment because approvals are workflow records, not one field. |

## 6. What Can Be Reused Unchanged

- `orchestrator/case_packet.py` field storage for the core shared categories.
- Normalization and validation for existing case-packet records.
- Safe ID/path handling around case packet persistence.
- Appendable field handling for source materials, facts, timeline events, open
  issues, missing evidence, contradictions, drafts, and decisions.
- Orientation handling for `status` and `next_step`.
- Existing negative-edge posture that blocks bundled runtime/model/platform
  execution requests.
- Existing tests for current case-packet behavior, as regression coverage.

## 7. What Likely Needs Wrapper/Adaptor Treatment

- Neutral naming should be introduced through a new mapping/adaptor module
  rather than by renaming existing fields in place.
- `timeline_events` should map to chronology/timeline/history.
- `open_issues` should map to open questions.
- `missing_evidence` should map to missing evidence / missing canon without
  changing current storage semantics.
- `status` and `next_step` should be treated as partial review posture / next
  work item signals, not as a full neutral workflow model.
- Operator approvals should remain tied to existing decision and authorization
  surfaces until a later boundary proves a cleaner abstraction.
- Case-packet task workflow modules should remain case-specific until the
  neutral data mapping is proven and regression-tested.

## 8. What Must Remain Domain-Specific

Claims/disputes/appeals-specific material must remain outside the neutral core:

- policy, insurance, reimbursement, benefits, billing, counterparty, deadline,
  external communication, legal/policy risk, and evidence-submission language

Game/worldbuilding/design-specific material must remain outside the neutral
core:

- canon hierarchy, lore, factions, mechanics, campaign history, design pillars,
  playtest criteria, creative alternatives, and theme/tone language

The neutral layer should not turn domain-specific judgment into generic fields.

## 9. Minimal Future Implementation Sequence

1. Add a small neutral mapping module, likely
   `orchestrator/dossier_case_abstraction.py`.
2. Add tests that prove the neutral field map exactly covers the required
   shared fields and maps to existing case-packet fields without mutation.
3. Add a read-only summary/adaptor function that accepts a normalized
   case-packet dict and returns a neutral dossier/case view.
4. Add tests proving the adaptor preserves existing values and does not infer a
   product domain.
5. Run existing case-packet substrate tests as regression coverage.
6. Only after the mapping/adaptor is proven, consider whether a later boundary
   should add persistence, CLI, or workflow surfaces for neutral dossier/case
   records.

## 10. Candidate Files For Future Mutation

Small first implementation boundary:

- `orchestrator/dossier_case_abstraction.py`
- `tests/test_dossier_case_abstraction_mapping.py`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

Possible later boundaries, not first:

- `orchestrator/case_packet.py`
- `orchestrator/case_packet_persistence.py`
- `orchestrator/case_packet_task_candidate_review.py`
- `orchestrator/case_packet_task_creation_authorization.py`
- `orchestrator/case_packet_task_creation_write_gate.py`
- `orchestrator/case_packet_task_execution_authorization.py`
- `orchestrator/case_packet_task_execution_candidate_surface.py`
- `orchestrator/authorized_case_packet_task_execution.py`
- `orchestrator/case_packet_task_execution_result_review.py`
- `orchestrator/case_packet_task_execution_result_response_options.py`

The first mutating boundary should avoid changing existing case-packet modules
unless source inspection proves a tiny import or registry hook is strictly
necessary.

## 11. Candidate Tests For Future Mutation

New test:

- `tests/test_dossier_case_abstraction_mapping.py`

Likely regression tests:

- `tests/test_phase_58_case_packet_substrate.py`
- `tests/test_phase_59_case_packet_inspectability.py`
- `tests/test_phase_60_case_packet_init.py`
- `tests/test_phase_61_case_packet_append.py`
- `tests/test_phase_62_case_packet_orientation.py`
- `tests/test_phase_68_authorized_persistence.py`
- `tests/test_phase_69_task_candidate_review.py`
- `tests/test_phase_70_task_creation_authorization.py`
- `tests/test_phase_71_task_creation_write_gate.py`
- `tests/test_phase_72_case_packet_task_execution_candidate_surface.py`
- `tests/test_phase_73_case_packet_task_execution_authorization.py`
- `tests/test_phase_74_authorized_case_packet_task_execution.py`
- `tests/test_phase_75_case_packet_task_execution_result_review.py`
- `tests/test_phase_76_case_packet_task_execution_result_response_options.py`
- `tests/test_phase_96_canonical_case_packet_execution_delegation.py`

If the first mutation only adds a pure mapping module, the minimum validation
should be the new mapping test plus Phase 58 through Phase 62 substrate tests.
Broader workflow regressions should be added if any workflow module changes.

## 12. Stop Conditions

A future mutating boundary should stop if:

- the working tree is dirty before edits
- the planned mutation would require source files outside the allowed list
- implementation pressure starts selecting the first product domain
- Phase 387 becomes implicated by sequence momentum
- existing case-packet storage would need a migration
- existing case-packet tests fail
- the mapping cannot preserve current field values without semantic inference
- runtime/provider/model/platform execution is needed
- Source Files refresh/export/capsule work is requested
- the change would require renaming existing modules rather than adding a small
  neutral layer

## 13. Non-Proofs

This plan does not implement source behavior.

It does not prove runtime behavior, provider/model behavior, semantic
correctness, production readiness, Phase 387 implementation, end-to-end
claims/disputes/appeals competence, end-to-end game/worldbuilding/design
workflow, first product wedge selection, Source Files refresh/export/capsule
proof, or product-market fit.

It does not prove that the future implementation should rename `case_packet` or
that a separate persisted `dossier_packet` store is required.

## 14. Recommended Next Boundary

Recommended next boundary:

`DOSSIER_CASE_ABSTRACTION_MAPPING_SOURCE_TEST_DOCS`

Purpose:

Add a small pure source/test/docs mapping layer that exposes neutral
dossier/case field vocabulary over the existing case-packet substrate without
changing existing case-packet behavior.

Allowed first-boundary mutation should be limited to:

- `orchestrator/dossier_case_abstraction.py`
- `tests/test_dossier_case_abstraction_mapping.py`
- minimal docs/ledger registrations

Excluded:

- no Phase 387
- no product wedge selection
- no case-packet module rename
- no persistence migration
- no runtime/provider/model execution
- no Source Files refresh/export/capsule
- no claims/disputes/appeals implementation
- no game/worldbuilding/design implementation
