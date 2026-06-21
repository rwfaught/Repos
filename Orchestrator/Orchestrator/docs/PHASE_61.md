# PHASE_61.md

## Phase 61 — Minimal Operator-Controlled Case Packet Amendment Surface

---

## Purpose

Add a minimal deterministic operator-controlled append-only amendment surface for existing case packets.

This phase allows exactly one explicit operator-provided entry to be appended to one approved list field on an existing case packet.

This phase does not add intelligence, automation, routing, task creation, or scalar patching.

---

## Scope

Add CLI command:

`python main.py case-packet-append <case_packet_append_json_path>`

Approved append fields only:

- counterparties
- source_materials
- extracted_facts
- timeline_events
- open_issues
- missing_evidence
- contradictions
- drafts
- decisions

Forbidden scalar mutation fields:

- case_id
- case_type
- title
- objective
- status
- next_step

---

## Input Shape

```json
{
  "case_id": "billing_dispute_vendor_x",
  "field": "open_issues",
  "entry": {
    "text": "Vendor charged for a service period after cancellation.",
    "source": "operator",
    "note": "Entered manually from owner review."
  }
}
```

---

## Required Behavior

1. Read append JSON file.
2. Validate JSON object input.
3. Require `case_id`, `field`, and `entry`.
4. Reject missing or null `entry`.
5. Load existing case packet by `case_id`.
6. Rely on existing case-id safety behavior for traversal rejection.
7. Reject unknown fields and scalar fields.
8. Append exactly one entry to selected approved list field.
9. Validate updated packet before persistence.
10. If invalid, print JSON failure and do not persist.
11. If valid, persist only `data/case_packets/<case_id>.json`.
12. Print JSON success output.

Successful output includes at minimum:

- updated: true
- appended: true
- case_id
- field
- new_count
- path
- validation

Failure output includes:

- updated: false
- appended: false
- error or errors

---

## Non-Goals

Do not add:

- channel access
- OpenClaw integration
- document/source parsing
- model/provider calls
- planner behavior
- intake-to-case behavior
- task or recommendation creation
- arbitrary JSON patching
- scalar status/next_step mutation
- broad case management

---

## Files

Create:

- `tests/test_phase_61_case_packet_append.py`

Modify only:

- `orchestrator/case_packet.py`
- `main.py`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`

---

## Validation

Run:

- `python3 -m unittest tests/test_phase_61_case_packet_append.py`
- `python3 -m unittest discover -s tests`

---

## Completion

After validation:

- update `docs/ACTION_LOG.md` with concise Phase 61 completion note
- update `docs/PHASE_INDEX.md` with Phase 61 entry and completion tracking
- set Current Phase to `(none — awaiting next phase definition)`
