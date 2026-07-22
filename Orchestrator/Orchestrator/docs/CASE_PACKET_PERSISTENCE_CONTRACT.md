# Case-Packet Entry Persistence Contract

## Scope

`save_case_packet` and `load_case_packet` persist one complete case packet at
`data/case_packets/<case_id>.json`.  Save uses the existing record-local atomic
JSON writer; load validates the durable packet before returning a copy.

The contract applies explicit-entry continuity only to `source_materials` and
`extracted_facts`.  Identified entries retain their caller-provided IDs,
values, collection field, and list order.  Anonymous legacy values remain
anonymous and retain their values and order; load never assigns IDs or matches
entries by content.

## Safe Updates

Ordinary whole-packet saves may update other packet state and identified-entry
values, but they may not add, discard, reorder, or rewrite explicit IDs in the
two protected collections.  Such a change fails diagnostically.

Use `save_case_packet_entry_preservation_operation(case_id, operation)` for an
identified create, preserve, edit, replace, or retire transition.  It loads the
packet, delegates to the existing in-memory preservation contract, verifies the
candidate result, and atomically writes it.  This is the sole persistence
adapter; it does not duplicate transition semantics.

## Compatibility And Failure Posture

Legacy anonymous entries and unversioned normalized packet shapes remain
compatible.  No IDs are synthesized or migrated.  There is no global registry,
history ledger, semantic matching, or evidence-link behavior.

Load rejects malformed JSON, a non-object packet, missing required packet
fields, incompatible scalar/list types, invalid or mismatched case IDs, and
malformed identified entries.  Failed atomic replacement leaves the previous
target intact and cleans its temporary file.

## Non-Proofs

This proves controlled local save/load continuity only.  It does not prove
provenance, evidence-link integrity, semantic equivalence, fact correctness,
workflow completion, product value, product-wedge selection, concurrency,
recovery beyond one atomic write, or production readiness.
