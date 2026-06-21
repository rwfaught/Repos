# PHASE_62.md

## Phase 62 — Minimal Operator-Controlled Case Orientation Update Surface

---

## Purpose

Add a minimal deterministic operator-controlled orientation update surface for existing case packets.

Phase 61 made case packets appendable by the operator.
Phase 62 makes case packets orientable by the operator.

This phase allows updating only:
- `status`
- `next_step`

No other scalar or list fields may be changed by this command.

---

## Scope

Add CLI command:

`python main.py case-packet-orient <case_packet_orientation_json_path>`

Allowed orientation fields only:
- `status`
- `next_step`

Forbidden scalar fields:
- `case_id`
- `case_type`
- `title`
- `objective`

Forbidden list fields:
- `counterparties`
- `source_materials`
- `extracted_facts`
- `timeline_events`
- `open_issues`
- `missing_evidence`
- `contradictions`
- `drafts`
- `decisions`

---

## Input Shape

```json
{
  "case_id": "billing_dispute_vendor_x",
  "status": "in_review",
  "next_step": "Collect final invoice and cancellation confirmation."
}
```

At least one of `status` or `next_step` is required.

---

## Required Behavior

1. Read orientation JSON file.
2. Validate JSON object input.
3. Require `case_id`.
4. Require at least one of `status` or `next_step`.
5. Reject unknown fields.
6. Reject forbidden scalar fields.
7. Reject list-field mutation attempts.
8. Reject null orientation values.
9. Reject empty or whitespace-only string orientation values.
10. Reject non-string orientation values.
11. Load existing case packet by `case_id`.
12. Rely on existing case-id safety behavior for traversal rejection.
13. Update only the provided approved orientation fields.
14. Validate updated packet before persistence.
15. If invalid, print JSON failure and do not persist.
16. If valid, persist only `data/case_packets/<case_id>.json`.
17. Print JSON success output.

Successful output includes at minimum:
- `updated: true`
- `oriented: true`
- `case_id`
- `updated_fields`
- `path`
- `validation`

Failure output includes:
- `updated: false`
- `oriented: false`
- `error` or `errors`

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
- lifecycle automation
- status enums or transition rules
- broad case management

---

## Files

Create:
- `tests/test_phase_62_case_packet_orientation.py`

Modify only:
- `orchestrator/case_packet.py`
- `main.py`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`

---

## Validation

Run:
- `python3 -m unittest tests/test_phase_62_case_packet_orientation.py`
- `python3 -m unittest discover -s tests`

---

## Completion

After validation:
- update `docs/ACTION_LOG.md` with concise Phase 62 completion note
- update `docs/PHASE_INDEX.md` with Phase 62 entry and completion tracking
- set Current Phase to `(none — awaiting next phase definition)`
