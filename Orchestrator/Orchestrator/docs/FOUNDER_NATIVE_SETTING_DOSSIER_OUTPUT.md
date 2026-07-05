# Founder Native Setting Dossier Output

Boundary: `FOUNDER_NATIVE_SETTING_DOSSIER_OUTPUT_SOURCE_TEST_DOCS`

Status: source/test/docs output seam. Not product wedge selection.

Marker: `FOUNDER_NATIVE_SETTING_DOSSIER_OUTPUT_SOURCE_TEST_DOCS_REGISTERED=SOURCE_TEST_DOCS`

## Purpose

This boundary adds a deterministic visible dossier output over the committed
**The Human Override** founder-native setting fixture.

The output consumes `orchestrator/founder_native_setting_fixture.py` and renders
plain data plus markdown for Roger inspection. It does not recreate the source
notes, call a model, select a product wedge, resume Phase 387, or claim semantic
correctness.

## Source/Test Files

- `orchestrator/founder_native_setting_dossier_output.py`
- `tests/test_founder_native_setting_dossier_output.py`

## Output Shape

The output exposes:

- canon_facts
- contradictions
- missing_canon
- open_questions
- draft_repair_or_recommendation
- next_work_items
- explicit_non_proofs

The markdown renderer uses the same sections so the dossier is visible and
judgeable without runtime/provider/model execution.

## Non-Proofs

This boundary does not prove:

- runtime/provider/model behavior
- semantic correctness
- production readiness
- Phase 387 implementation
- first product wedge selection
- claims/disputes/appeals product implementation
- game/worldbuilding/design wedge selection
- live model generation
- provider calls
- Source Files refresh/export/capsule proof

## Recommended Next Boundary

`FOUNDER_NATIVE_SETTING_DOSSIER_FOUNDER_REVIEW_RECORD_DOCS_ONLY`

This later docs-only boundary should record Roger's founder review of the
visible dossier output without selecting a first product wedge or mutating
source behavior.

## Founder Review Record

The founder review record is:

`docs/FOUNDER_NATIVE_SETTING_DOSSIER_FOUNDER_REVIEW.md`
