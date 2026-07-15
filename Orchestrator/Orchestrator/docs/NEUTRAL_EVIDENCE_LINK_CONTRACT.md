# Neutral Evidence-Link Contract

Boundary: `NEUTRAL_EVIDENCE_LINK_CONTRACT_SOURCE_TEST_DOCS_IMPLEMENTATION`

Status: additive source/test/docs contract. It is not a persistence migration,
workflow implementation, or authorization surface.

## Purpose

`NeutralEvidenceLink` records one asserted association between a typed subject
record and an existing source reference. It makes provenance expressible without
requiring current case-packet facts, coding records, or other existing payloads
to change shape.

## Neutral Data Shape

Each link serializes as:

```json
{
  "evidence_link_id": "evidence_link_001",
  "subject_reference": {
    "subject_type": "fact",
    "subject_id": "fact_001"
  },
  "source_reference": "source_note_001",
  "source_locator": "section: findings"
}
```

`subject_reference` is deliberately typed and uses the stable shape
`subject_type` plus `subject_id`. The contract does not impose a closed list of
domains or subject categories; `subject_type` must instead be a non-empty,
lowercase identifier. This permits fact-like subjects and other neutral subjects
such as chronology items, contradictions, recommendations, or review records.

`source_reference` is a required non-empty string that names an existing source
under the caller's own workflow conventions. `source_locator` is optional. When
present, it is a concise string locating the asserted association within that
source; it is not resolved, fetched, or persisted by this contract.

## Validation And Cardinality

Validation requires a stable link identity, a mapping-shaped typed subject
reference, non-empty subject type and identity, and a non-empty source
reference. A supplied locator must be a string or `null`. Normalization and
serialization copy caller data rather than mutating it.

Each association is one independent link record. Therefore one subject may have
multiple links to different sources, and one source may support multiple
subjects, without adding mandatory source fields to existing arbitrary fact
payloads.

## Relationship To Existing Records

Case packets continue to own their flexible `source_materials` and
`extracted_facts` fields unchanged. Coding task, artifact, authorization,
recommendation, and patch-evidence records likewise keep their current
lifecycle-specific links. `NeutralEvidenceLink` is a separate reusable semantic
record, not a replacement for those records and not a new case-packet schema.

## Readback And Non-Proofs

The deterministic readback states whether a link passed structural validation
and preserves explicit non-proofs. A valid link records an asserted association
only. It does not establish:

- truth;
- source quality;
- evidentiary sufficiency;
- recommendation correctness; or
- authorization to act.

It also does not perform persistence, source resolution, provider/model/runtime
execution, worker dispatch, product execution, or product-wedge selection.

## Deferred Adoption And Migration

Existing producers are not required to emit evidence links. A later explicitly
authorized boundary may decide whether an adapter, readback, or particular
workflow should adopt this contract. No migration, database change, external
storage work, or operator-constraint semantics are included here.
