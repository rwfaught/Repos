# Dossier Case Mapping Operator Review

Boundary: `DOSSIER_CASE_MAPPING_OPERATOR_REVIEW_DOCS_ONLY`

Status: docs-only operator review of the neutral dossier/case mapping seam.

Marker: `DOSSIER_CASE_MAPPING_OPERATOR_REVIEW_DOCS_ONLY_REGISTERED=DOCS_ONLY`

## 1. Executive Summary

The mapping seam added in `orchestrator/dossier_case_mapping.py` is a small,
deterministic source/test/docs proof that existing case-packet-shaped data can
be viewed through neutral dossier/case vocabulary.

It is sufficient as a first source foothold for Roger's ratified Option 3:
build the neutral dossier/case abstraction first, then choose the product
domain later.

This review does not choose claims/disputes/appeals. It does not choose
game/worldbuilding/design. It does not resume Phase 387. It reviews only the
structural mapping seam that now sits beside the existing case-packet
substrate.

Classification:

- source/test/docs proof
- deterministic structural proof
- not semantic product proof
- not runtime/model/provider proof
- not product wedge selection
- not Phase 387

## 2. Accepted Facts

- `HEAD` and `origin/main` were verified at
  `41d7ba7dcbd6c9413f00df18077dfd290833a59a` before this review boundary.
- `41d7ba7dcbd6c9413f00df18077dfd290833a59a` is the commit titled
  `Add dossier case mapping seam`.
- `orchestrator/dossier_case_mapping.py` defines
  `DossierCaseFieldMapping`, `get_dossier_case_field_mappings`,
  `get_dossier_case_field_map`, and
  `adapt_case_packet_to_dossier_case`.
- `orchestrator/dossier_case_mapping.py` imports only
  `normalize_case_packet` from the existing case-packet substrate.
- `tests/test_dossier_case_mapping.py` contains focused unittest coverage for
  neutral field coverage, case-packet-compatible field targets, missing
  evidence and contradiction preservation, wedge non-selection, domain
  neutrality, adapter extraction, and non-proof posture.
- `orchestrator/case_packet.py` remains the existing dict-shaped substrate with
  scalar fields including `objective`, `status`, and `next_step`, and list
  fields including `source_materials`, `extracted_facts`, `timeline_events`,
  `open_issues`, `missing_evidence`, `contradictions`, `drafts`, and
  `decisions`.
- `docs/DOSSIER_CASE_ABSTRACTION_IMPLEMENTATION_PLAN.md` records that Roger
  ratified Option 3: build the neutral dossier/case abstraction first, then
  choose the first product domain later.
- `docs/FIRST_PRODUCT_WEDGE_RATIFICATION_PACKET.md` says Codex must not infer
  a product wedge, Phase 387 resumption, or semantic product capability from
  the existence of case-packet code.

## 3. What The Mapping Seam Adds

The seam adds a neutral vocabulary layer over existing case-packet fields.

It does not introduce a new persisted dossier packet. It does not rename
existing case-packet storage. It does not alter task creation, task execution,
review, response options, provider behavior, runtime behavior, or platform
behavior.

The seam adds:

- a frozen `DossierCaseFieldMapping` dataclass
- a canonical tuple of neutral-to-case-packet mappings
- a helper returning the mappings as dataclass records
- a helper returning the mappings as a plain dictionary
- a read-only adapter that normalizes a case-packet-shaped dictionary and
  returns a neutral dossier/case view
- explicit constants preserving no-wedge and non-proof posture

## 4. Field Mapping Review

The mapping covers the shared neutral vocabulary required by the dossier/case
bridge.

| Neutral field | Existing case-packet field(s) | Review |
| --- | --- | --- |
| `objective` | `objective` | Direct shared purpose field. |
| `source_materials` | `source_materials` | Direct shared source inventory field. |
| `extracted_facts` | `extracted_facts` | Direct shared interpretation field. |
| `chronology` | `timeline_events` | Neutral alias for timeline/history. |
| `open_questions` | `open_issues` | Neutral alias for unresolved issues. |
| `missing_evidence` | `missing_evidence` | Direct shared gap field. |
| `missing_canon` | `missing_evidence` | Neutral alias that preserves the same storage initially. |
| `contradictions` | `contradictions` | Direct shared conflict field. |
| `drafts` | `drafts` | Direct shared prepared-output field. |
| `decisions` | `decisions` | Direct shared human-judgment field. |
| `next_work_items` | `next_step` | Narrow current next-step signal, not a full work-item model. |
| `review_posture` | `status`, `next_step` | Partial posture from existing orientation fields. |
| `operator_approvals` | `decisions` | Approval signals remain decision records for now. |
| `status` | `status` | Direct current status field. |

The field map is intentionally explicit and conservative. The two fields that
need later caution are `next_work_items` and `operator_approvals`, because the
existing substrate stores them as partial signals rather than a full neutral
workflow model.

## 5. Adapter Behavior Review

`adapt_case_packet_to_dossier_case` accepts a case-packet-shaped dictionary,
normalizes it through `normalize_case_packet`, and returns a neutral view.

The adapter copies list values into new lists for the neutral view. It maps
`timeline_events` to `chronology`, `open_issues` to `open_questions`, and
`missing_evidence` to both `missing_evidence` and `missing_canon`.

The adapter also returns:

- `product_wedge_selection: no_first_product_wedge_selected`
- `non_proof_posture` with false values for runtime proof, provider/model
  proof, semantic correctness proof, production readiness proof, Phase 387
  implementation, and first product wedge selection

This is appropriate for the first seam because it proves read-only structural
compatibility without creating a new behavior branch.

## 6. Test Coverage Review

`tests/test_dossier_case_mapping.py` proves the following deterministic
contract points:

- required neutral fields are exposed
- mapped case-packet fields stay within the existing case-packet-compatible
  field set
- missing-evidence and missing-canon concepts both remain visible
- contradictions remain visible as a separate concept
- the adapter does not select a first product wedge
- the mapping surface avoids claims/disputes/appeals and
  game/worldbuilding/design terminology
- the adapter extracts expected neutral values from a minimal case-packet
  fixture
- non-proof posture is exported

The tests are pure unittest coverage. They do not execute providers, models,
runtime surfaces, persistence writes, platform behavior, or product-domain
workflows.

## 7. What This Proves

This proves that the existing case-packet substrate has enough structural
overlap to support a neutral dossier/case vocabulary layer.

Specifically, it proves:

- a deterministic neutral field map can be expressed in source
- required neutral categories can map to existing case-packet-compatible fields
- missing evidence / missing canon and contradictions remain visible
- a normalized case-packet-shaped dictionary can be adapted into a neutral view
- no first product wedge is selected by the adapter
- the seam can preserve explicit non-proof posture in data

This is source/test/docs proof and deterministic structural proof only.

## 8. What This Does Not Prove

This does not prove:

- runtime behavior
- provider/model behavior
- semantic correctness
- production readiness
- Phase 387 implementation
- first product wedge selection
- claims/disputes/appeals product implementation
- game/worldbuilding/design product implementation
- persistence migration
- Source Files refresh/export/capsule proof
- end-to-end dossier or case usefulness
- real document analysis
- legal, policy, insurance, reimbursement, or benefits competence
- canon, lore, mechanics, or creative-design workflow competence

The mapping seam is not product proof. It is a first structural foothold.

## 9. Founder/Operator Interpretation

Roger ratified Option 3 only: build neutral dossier/case abstraction first,
then choose the product domain later.

The seam is a good first implementation move for that ratification because it
keeps the existing case-packet investment visible while stopping short of a
domain commitment. It shows that the shared workflow bones named in the design
docs can be represented over current source without a rename or persistence
migration.

The correct operator read is:

- the abstraction-first path now has a small source foothold
- claims/disputes/appeals remains historically relevant but unchosen
- game/worldbuilding/design remains a live candidate but unchosen
- a later boundary can make the seam easier to inspect or test with examples
- Roger still owns the product-domain decision

## 10. Risks / Watchpoints

- `missing_canon` currently aliases `missing_evidence`; that is acceptable for
  the first seam, but a later domain-specific branch may need clearer storage
  or labeling.
- `next_work_items` is derived from one `next_step` string. It should not be
  treated as a complete work-item list.
- `operator_approvals` is derived from `decisions`. Later approval surfaces may
  need stronger separation between decision records, authorization records, and
  final approvals.
- The mapping names are neutral, but future examples could still accidentally
  bias toward one product wedge.
- Repeated ledger growth can feel like product progress. This seam should be
  treated as structural groundwork only.
- Any persistence, CLI, report surface, or fixture examples should remain
  explicitly bounded and should preserve no-wedge posture unless Roger chooses
  a domain.

## 11. Next Safe Boundaries

1. `DOSSIER_CASE_MAPPING_READBACK_SOURCE_TEST_DOCS`

Purpose: add deterministic readback/reporting for the mapping seam.

This would make the neutral map easier for Roger to inspect from source without
changing persistence or product behavior.

2. `DOSSIER_CASE_MINIMAL_FIXTURE_SOURCE_TEST_DOCS`

Purpose: add a small neutral fixture/example showing how a dossier/case packet
can represent both admin-case and creative-dossier shapes without choosing
either as product wedge.

This would test whether the bridge can stay balanced across both candidate
directions.

3. `FIRST_PRODUCT_WEDGE_RATIFICATION_OPERATOR_DECISION_DOCS_ONLY`

Purpose: stop and ask Roger whether to choose a domain yet or continue
abstraction-first.

This keeps founder ratification explicit.

4. `SOURCE_FILES_REFRESH_EXPORT_AFTER_FOUNDER_REALIGNMENT`

Purpose: refresh external Source Files/capsule only if Roger wants a portable
snapshot.

This should remain optional and should not be bundled with product behavior.

## 12. Recommended Next Move

Recommended next boundary:

`DOSSIER_CASE_MAPPING_READBACK_SOURCE_TEST_DOCS`

Reason:

The safest next move is a deterministic readback/reporting surface for the
mapping seam. It would let Roger inspect the neutral field map and adapter
output directly while preserving the same non-runtime, non-provider,
non-wedge-selection posture.

Do not move to persistence, domain fixtures, Source Files refresh, or product
wedge ratification unless Roger explicitly chooses that next.

## 13. Readback Boundary Record

Boundary:

`DOSSIER_CASE_MAPPING_READBACK_SOURCE_TEST_DOCS`

Status:

Implemented as a small deterministic source/test/docs readback seam in
`orchestrator/dossier_case_mapping_readback.py`, with focused coverage in
`tests/test_dossier_case_mapping_readback.py`.

Readback posture:

The readback reports neutral fields, neutral-to-case-packet mappings, required
field coverage, missing required fields, preserved missing-evidence and
contradiction concepts, domain-neutrality posture, no-wedge status, Phase 387
non-implementation, explicit non-proofs, and safe next options.

Recommended next boundary:

`DOSSIER_CASE_MINIMAL_FIXTURE_SOURCE_TEST_DOCS`

## 14. Minimal Fixture Boundary Record

Boundary:

`DOSSIER_CASE_MINIMAL_FIXTURE_SOURCE_TEST_DOCS`

Status:

Implemented as a small deterministic fixture seam in
`orchestrator/dossier_case_minimal_fixture.py`, with focused coverage in
`tests/test_dossier_case_minimal_fixture.py`.

Fixture posture:

The seam exposes one `admin_case_shape` fixture and one
`creative_dossier_shape` fixture. Both are case-packet-shaped dictionaries
adapted through the existing mapping seam and represented through the existing
readback seam. They preserve required neutral field coverage,
missing-evidence / missing-canon concepts, contradiction concepts, no-wedge
status, Phase 387 non-implementation, and explicit non-proofs.

Recommended next boundary:

`FIRST_PRODUCT_WEDGE_RATIFICATION_OPERATOR_DECISION_DOCS_ONLY`

## 15. Task Readiness Boundary Record

Boundary:

`DOSSIER_CASE_TASK_READINESS_SOURCE_TEST_DOCS`

Status:

Implemented as a deterministic neutral task-readiness source/test/docs seam in
`orchestrator/dossier_case_task_readiness.py`, with focused coverage in
`tests/test_dossier_case_task_readiness.py`.

Readiness posture:

The report inspects structural fields only. It reports required neutral fields,
present/missing fields, open questions, contradictions, decisions, next work
items, structural readiness blockers, no-wedge status, Phase 387
non-implementation, runtime/provider/model non-requirement, and explicit
non-proofs.

Recommended next boundary:

`FIRST_PRODUCT_WEDGE_RATIFICATION_RECORD_DOCS_ONLY`

`DOSSIER_CASE_TASK_READINESS_SOURCE_TEST_DOCS_PROVEN=PASS`

## 16. First Product Wedge Ratification Record

Boundary:

`FIRST_PRODUCT_WEDGE_RATIFICATION_RECORD_DOCS_ONLY`

Status:

Recorded in `docs/FIRST_PRODUCT_WEDGE_RATIFICATION_RECORD.md`.

Decision posture:

No first product wedge is selected. The mapping, readback, fixture, and
readiness seams remain structural source/test/docs proof only.

Recommended next boundary:

`DOSSIER_CASE_TASK_READINESS_OPERATOR_REVIEW_DOCS_ONLY`

`FIRST_PRODUCT_WEDGE_RATIFICATION_RECORD_DOCS_ONLY_REGISTERED=DOCS_ONLY`
