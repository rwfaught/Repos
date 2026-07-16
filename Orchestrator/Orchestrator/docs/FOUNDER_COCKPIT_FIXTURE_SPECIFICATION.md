# Founder Cockpit Fixture Specification Controls

Boundary: `FOUNDER_COCKPIT_TOOL_NEUTRAL_FIXTURE_INFORMATION_MODEL_AND_WIREFRAME_SPEC_DOCS_ONLY`

Status: CTO/coordinator-ratified tool-neutral, read-only, fictional-fixture specification.

Marker: `FOUNDER_COCKPIT_FIXTURE_SPECIFICATION=RATIFIED_DOCS_ONLY`

## Purpose and Non-Authority Posture

The Founder Cockpit is a small, read-only orientation surface: it tells a founder where the project is, what is proven and not proven, what decision remains open, the next bounded move, and whether the source set is safe to rely on. It displays recorded posture; it is not authority for that posture.

It must use fictional fixture data only. It cannot approve, mutate, schedule, assign, comment, notify, execute, reconcile automatically, or ratify. It is neither a project-management surface nor a Dossier Workspace substitute.

| Surface | Question | Scope |
| --- | --- | --- |
| Founder Cockpit | Where are we and what needs founder attention? | Project orientation and one bounded next move. |
| Dossier Workspace | What is in this dossier/case? | Detailed context, evidence, provenance, and working materials. |

The Cockpit may identify a dossier but must not reproduce its workspace. Founder Cockpit-only content is project stage, current pursuit, proof/non-proof, decision tension, next bounded move, source health, and project-level authority inspection. Dossier Workspace-only content is dossier subject matter, evidence materials, case facts, analyses, and work context. Shared concepts such as `Claim`, `Decision`, `Source`, freshness, and provenance mean project-orientation summaries in the Cockpit, but subject-specific working detail in the Dossier Workspace.

The Founder Cockpit must not display client identity, client documents, case facts, recommendations, pricing, opportunity scoring, client deliverables, or case work queues. It may display only an abstract, non-client-specific reference needed to explain a project-level decision.

## Design Rules

1. Orientation precedes inspection; inspection precedes provenance detail.
2. Pair every material proof with its decisive non-proof.
3. Keep proving-use-case and product-wedge postures distinct.
4. Keep status, authority, evidence, freshness, ratification, and durability distinct.
5. Plain English leads; exact canonical values remain inspectable and are explained when opaque.
6. Essential truths remain visible without expansion; permit at most two meaningful disclosure levels.
7. Unknown, stale, unavailable, missing, and conflicting conditions are explicit; no inferred completeness.

## Initial Record Model

Use only these five types. This is a display model, not a universal ontology, global identity registry, persistence schema, or project-management schema.

| Type | Purpose | Minimum fields |
| --- | --- | --- |
| `Snapshot` | Visible project position. | `id`, `stage`, `current_pursuit`, `strongest_proof_claim_id`, `decisive_non_proof_claim_id`, `proving_use_case_posture`, `product_wedge_posture`, `next_move_work_item_id`, `source_health`, `observed_at`, `source_ids` |
| `WorkItem` | Next move, track, open thread, risk, or blocker with lifecycle. | `id`, `type`, `founder_statement`, `canonical_value`, `status`, `authority_class`, `advisory_or_authorized`, `responsible_role`, `source_ids` |
| `Claim` | Supported, limited, stale, or contested statement. | `id`, `founder_statement`, `canonical_value`, `classification`, `support_status`, `authority_class`, `source_ids`, `observed_at`, `reconciliation_state`, `conflict_state` |
| `Decision` | Recorded choice or unresolved question. | `id`, `question`, `posture`, `founder_statement`, `canonical_value`, `ratification_status`, `authority_class`, `source_ids`, `durability` |
| `Source` | Inspectable origin. | `id`, `label`, `source_entity`, `source_basis`, `authority_class`, `revision_or_update_time`, `observed_or_verified_time`, `producing_or_verifying_activity`, `responsible_agent_or_role`, `reconciliation_state`, `durability`, `availability` |

`WorkItem.type` may be `next_move`, `track`, `open_thread`, `risk`, or `blocker`. A risk/blocker without independent lifecycle is a typed `Claim`. Durability is metadata on `Source`, `Decision`, or `Snapshot`, not an entity.

Detailed durability values are `fixture_only`, `draft_local`, `working_tree_observed`, `committed_local`, `pushed_remote`, `remote_ref_verified`, `current_main_ancestry_verified`, `operator_evidence_only`, and `unknown`. A first-screen summary may compress these values, but inspection must preserve the precise value. Broad repository/external labels are not sufficiently precise terminal states.

## Display Vocabulary

Every significant classification renders a tuple: (1) a founder statement in plain English, (2) an exact canonical repository value available on inspection, and (3) a short explanation when that value is not self-explanatory.

Example: “The project is paused at a founder decision gate.” / `FOUNDER_RATIFICATION_GATE_STOP` / “No product-direction implementation is authorized until founder ratification.”

| Meaning | Founder label | Canonical examples |
| --- | --- | --- |
| Evidence | Proof / non-proof | `deterministic_source_test_docs_proof`; `not_semantic_proof` |
| Authority | Who can establish it | `founder_decision_authority`; `technical_source_test_evidence` |
| Ratification | Is the choice authorized? | `ratified`; `pending_founder`; `historical_not_currently_ratified` |
| Freshness | Is source state reconciled? | `reconciled`; `stale`; `unknown`; `conflicting` |
| Move posture | Can it be acted on? | `advisory_only`; `authorized_bounded_move`; `blocked` |
| Durability | How is it recorded? | `draft_local`; `remote_ref_verified`; `operator_evidence_only` |

## First-Screen Hierarchy

The reading order is `Position`, `Decision Tension`, then `Next Move and Source Health`, with no more than six initial semantic statements in Fixture V0. This initial ceiling is a V0 hypothesis, not universal doctrine: Roger comprehension testing may justify a smaller or larger number when evidence shows improved comprehension without loss of hierarchy.

### Position

- Project stage, with plain-English wording and inspectable canonical value.
- Current pursuit.
- Strongest proof, including its bounded scope.
- Decisive non-proof.

### Decision Tension

- Proving-use-case posture.
- Product-wedge posture, including whether it is ratified.
- Open strategic decision only when it explains the tension.

The wording must not allow a proving use case or historical direction to be read as the selected wedge.

### Next Move and Source Health

- Next bounded move, its boundary, and its advisory/authorized/blocked posture.
- Source health: reconciled, stale, unavailable, missing provenance, or conflicting, with textual warning.

Stage, pursuit, proof/non-proof, use-case/wedge posture, next move, and stale/conflicting warning must remain visible without expansion.

## Secondary Inspection and PROV-Lite

One contextual disclosure may show canonical value and explanation, evidence scope/non-proof, authority, source basis, observation time, ratification history, provenance, reconciliation target, and technical source detail. Detailed tracks/open threads are inspection detail, not first-screen regions. No third meaningful level is permitted.

Each material displayed `Claim`, `Decision`, or `Snapshot` records or renders: source entity; producing/verifying activity; responsible role; source basis; observed/verified time; authority class; freshness/reconciliation state; and a derivation note when more than one source is synthesized. “Direct rendering of source record” is valid for one direct source. No W3C PROV-O, RDF, graph store, or ontology engine is required.

## Tool-Neutral Wireframe

Desktop reading order is left-to-right and then top-to-bottom; the fixture/non-authority label persists above the three macro-regions. The contextual evidence-inspection entry point is the labelled `Inspect evidence and authority` control attached to each material statement. It opens that statement's single secondary inspection disclosure.

```text
+--------------------------------------------------------------------------------+
| FICTIONAL FIXTURE · NON-AUTHORITATIVE PROJECTION · READ ONLY                  |
+--------------------------------------------------------------------------------+
| POSITION                         | DECISION TENSION                            |
| Stage                            | Proving-use-case posture                    |
| Current pursuit                  | Product-wedge posture                       |
| Strongest proof  <-> decisive    | Open strategic decision                     |
| non-proof                        | [Inspect evidence and authority]            |
+----------------------------------+---------------------------------------------+
| NEXT BOUNDED MOVE                | SOURCE HEALTH                               |
| Plain-English move + posture     | Reconciled / stale / conflicting text       |
| [Inspect evidence and authority] | [Inspect evidence and authority]            |
+--------------------------------------------------------------------------------+
```

At narrow widths, stack in this order: persistent fixture label; `Position`; `Decision Tension`; `Next Bounded Move`; `Source Health`. The proof/non-proof pair changes from side-by-side to sequential, with strongest proof immediately followed by decisive non-proof. A stale or conflicting warning interrupts normal presentation: place its textual warning directly before the affected statement and preserve the source-health warning in its normal region. This is a textual layout requirement only; it selects no HTML, CSS, platform, or component library.

## Source Authority, Freshness, and Conflicts

Authority establishes fitness for a conclusion; it does not establish freshness, truth, semantic correctness, or execution authority. Detailed inspection uses these distinct classes: `constitutional_strategic_authority`, `current_project_state_authority`, `founder_decision_authority`, `cto_coordination_authority`, `technical_source_test_evidence`, `operator_runtime_evidence`, `historical_reference`, `specialist_worker_advisory_evidence`, and `fictional_fixture_data`.

| Display field | Primary authority | Supporting authority | Must not be inferred |
| --- | --- | --- | --- |
| Project stage | `current_project_state_authority` | `constitutional_strategic_authority` | Roadmap synthesis is not live Git/source/test/runtime proof. |
| Success anchor | `constitutional_strategic_authority` | `cto_coordination_authority` | A strategic aim is not current capability proof. |
| Current pursuit | `current_project_state_authority` | `cto_coordination_authority` | Current-state summary must be reconciled against live source. |
| Active decision membrane | `cto_coordination_authority` | `founder_decision_authority` | A pending review is not founder ratification. |
| Proving-use-case posture | `current_project_state_authority` | `constitutional_strategic_authority` | Activity is not product-wedge selection. |
| Product-wedge posture | `founder_decision_authority` | `historical_reference` | Historical direction is not current ratification. |
| Tracks/open threads | `current_project_state_authority` | `cto_coordination_authority` | A current-track summary is not live-source proof until reconciled. |
| Next bounded move | `cto_coordination_authority` | `current_project_state_authority` | A recommendation is not authorization unless explicitly recorded. |
| Capability proof | `technical_source_test_evidence` | `operator_runtime_evidence` | Documentation existence is not implementation proof; Git durability is not semantic proof. |
| Founder ratification | `founder_decision_authority` | `cto_coordination_authority` | Worker/Specialist reports are evidence, not CTO or founder ratification. |
| CTO ratification | `cto_coordination_authority` | `specialist_worker_advisory_evidence` | Advisory evidence is not CTO acceptance. |
| Durability | Source/Decision durability metadata | `operator_runtime_evidence` | A commit, push, or remote ref is not semantic proof. |
| Freshness/conflict | Reconciled source set under `current_project_state_authority` | `operator_runtime_evidence` | A recent document timestamp is not current merely by age. |

`fictional_fixture_data` is a source-scope classification for illustrative records. It is not the fixture's data mode, authority posture, or a claim of authority over the real project. Keep source revision/update time, observation/verification time, reconciliation state, reconciliation target, and conflict state separate. A recent timestamp alone is not “current.” Source health values: `reconciled`, `stale`, `unknown`, `unavailable`, `missing_provenance`, and `conflicting`.

If claims conflict, show the claims, source(s) for each, authority classes, source basis and observed time, whether one authority outranks another, whether automatic resolution is valid, who must resolve it, and the conclusion unsafe in the meantime. If automatic resolution is invalid, say “No automatic resolution is valid.”

## Empty and Degraded States

| Condition | Required founder-facing text |
| --- | --- |
| No active boundary | “No active bounded move is recorded.” |
| No next bounded move | “A next bounded move has not been defined.” |
| No current proof | “No current proof is recorded for this position.” |
| No pending decision | “No material decision is currently recorded as pending.” |
| Stale source set | “The source set may be stale; do not treat this view as current.” |
| Source unavailable | “A supporting source could not be inspected.” |
| Missing provenance | “This statement lacks enough provenance to rely on.” |
| Conflicting authority | “Supporting authorities conflict; the conclusion is unresolved.” |
| Pending CTO review | “The evidence is awaiting CTO/coordinator review.” |
| No product wedge | “No product wedge is currently ratified.” |
| Fixture unverified | “This is fictional fixture data, not current project verification.” |

Inspection detail names missing fields, source/authority, resolver, or unsafe conclusion. None of these states may rely only on empty space, color, icon, shape, location, or hover.

## Accessibility

Later static HTML or visual mockups must target WCAG 2.2 AA: semantic headings/landmarks, logical reading order, keyboard-operable disclosures, visible focus, responsive reflow and zoom, compliant text/non-text contrast, accessible table/list semantics, text equivalents for all status/conflict meanings, and reduced-motion compatibility if movement is introduced.

## Fictional Fixture-Data Contract

Every fixture is read-only and fictional and says so visibly. Root `Snapshot` records must carry `data_mode = fictional_fixture` and `authority_posture = non_authoritative_projection`; neither field is an authority class. Represented records may illustrate any real authority class, but those values remain fictional examples and cannot claim current project evidence. Generation time is labelled fixture generation, not source verification. Fixtures include a proof/non-proof pair, distinct use-case/wedge posture, advisory and authorized-move scenarios, and stale, unavailable, missing-provenance, and conflict scenarios. Suggested illustrative names are `unratified_wedge`, `stale_sources`, `conflicting_authority`, and `no_next_move`.

## Founder-Comprehension Test

With Roger, without coaching, ask: (1) stage; (2) current pursuit; (3) genuine proof; (4) important non-proof; (5) whether proving use case is selected wedge; (6) open strategic decision; (7) next bounded move; (8) advisory or authorized; (9) whether source state is current; and (10) where supporting authority can be inspected.

Record answers, orientation time, disclosure use, and confusion. Questions 1–8 must be answerable on the primary screen; 9–10 with no more than one disclosure. Pass requires no confusion between proof/non-proof, use case/wedge, or recommendation/authorization, and no memorization of internal classifications. Roughly ten seconds targets orientation, not complete provenance comprehension.

## Acceptance Tests

A fixture is ready for CTO/coordinator review only if it uses the five initial record types, renders the three macro-regions in order, begins with no more than six initial semantic statements for Fixture V0 unless recorded Roger comprehension testing demonstrates that a smaller or larger count improves comprehension without weakening hierarchy, pairs proof/non-proof, separates use case/wedge, labels move posture, renders textual source health, exposes PROV-Lite in at most one disclosure, separates freshness fields, renders complete conflicts, supplies every degraded state, supports accessibility, declares fictional non-authoritative data, and passes the comprehension test.

## Explicit Non-Implications

This ratification does not authorize fixture implementation, HTML/UI work, hosting/platform selection, Codex Sites, live repository integration, automatic reconciliation, persistence/API design, Dossier Workspace design, project-management functions, approval/mutation/scheduling/assignment/comment/notification/execution controls, wedge/provider/model selection, Phase 387 resumption, runtime/project-script execution, commit, push, export, or capsule work.

## Ratification Record

Classification: `PASS_FOUNDER_COCKPIT_TOOL_NEUTRAL_FIXTURE_INFORMATION_MODEL_AND_WIREFRAME_SPEC_RATIFIED`.

Accepted: the five-record fixture display model; tool-neutral wireframe semantics; fictional fixture-data contract; source-authority mapping; durability semantics; Founder Cockpit/Dossier Workspace separation; PROV-lite; degraded and conflict states; WCAG 2.2 AA target; and the Roger comprehension-test protocol.

The next likely boundary is fictional fixture-data and static wireframe construction under separate authorization.
