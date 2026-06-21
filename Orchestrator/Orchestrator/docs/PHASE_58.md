# PHASE_58.md

## Phase 58 — Minimal Proving-Ground Case Packet Substrate

---

## Purpose

Add the first minimal local substrate for claims / disputes / appeals-style casework.

This phase exists to make the selected proving ground operationally real at the smallest useful level:

- a case packet can be represented
- its core state categories are explicit
- the state remains local and inspectable
- the system can validate the packet shape deterministically
- the implementation does not create hidden workflow, routing, policy judgment, or autonomous case handling

This is a feature phase.

It is not a broad product buildout.

---

## Governing Context

This phase is justified by the current repo control state:

- `docs/RERANK_01_RESULT.md` recommends `PHASE_58 — Minimal Proving-Ground Case Packet Substrate`
- `docs/PRODUCT_STRATEGY_03.md` selects claims / disputes / appeals-style casework as the first proving ground
- `docs/PRODUCT_DESIGN_02.md` defines the minimum conceptual case-state categories
- `docs/INTAKE_TRIAGE_DESIGN_04.md` requires that intake may authorize decomposition but must not silently perform decomposition
- `docs/PROJECT_VISION.md` requires honest contact with what is actually happening
- `docs/CURRENT_SUCCESS_CRITERION.md` remains the present-tense success anchor

This phase converts the design stack into a minimal implementation substrate without expanding beyond it.

---

## Active Layer

`implementation`

---

## Active Decision Membrane

This phase may decide only:

- how to represent a minimal local case packet
- how to validate that packet deterministically
- how to expose the packet through a small explicit CLI surface
- how to test that the substrate is inspectable and non-mutating except where explicitly requested

This phase must not decide:

- full case-management workflow
- document ingestion
- evidence extraction
- timeline generation from source materials
- model-based fact analysis
- policy/legal/insurance reasoning
- autonomous drafting
- task decomposition
- routing between models
- connector integration
- GUI/API behavior
- automatic creation of orchestrator tasks from case packets

The packet is a substrate, not a worker.

---

## Required Outcome

After this phase, the repo must support a minimal local case packet with explicit state categories corresponding to the case-state model in `PRODUCT_DESIGN_02.md`.

A valid minimal case packet must preserve these categories:

1. case identity
2. source materials
3. extracted facts
4. timeline / events
5. open issues / claims under dispute
6. missing evidence / missing materials
7. contradictions / unresolved conflicts
8. drafts / prepared outputs
9. decisions / approvals / user-owned judgments
10. current case status / next step

The implementation may use simple names, but these conceptual categories must remain visible in code and tests.

---

## Non-Goals

Do not implement:

- document parsing
- OCR
- email ingestion
- PDF extraction
- connector access
- automated evidence classification
- automated fact extraction
- legal, medical, insurance, or policy judgment
- case outcome recommendation
- autonomous filing, sending, or submission
- background jobs
- hidden task creation
- planner behavior
- recommendation creation
- intake-to-decomposition task creation
- multi-case search
- UI
- database migration system
- schema version negotiation beyond a simple explicit version field if needed

Do not introduce a broad case-management framework.

Do not create a second orchestration system.

Do not make the case packet mutate existing runs, tasks, recommendations, verifier results, or global state.

---

## Files To Create

Create:

- `orchestrator/case_packet.py`
- `tests/test_phase_58_case_packet_substrate.py`

Optionally create only if needed for deterministic fixtures:

- `data/case_packets/.gitkeep`

---

## Files To Modify

Modify only as needed:

- `main.py`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`

Do not modify unrelated recommendation, intake, provider, verifier, or run-manager behavior unless strictly necessary to wire the CLI command.

---

## Data Location

Case packets must be stored locally under:

- `data/case_packets/`

Each persisted packet should be a JSON file.

The file name should be deterministic from the case packet id.

Acceptable pattern:

- `data/case_packets/<case_id>.json`

The implementation must prevent path traversal by normalizing or rejecting unsafe case ids.

---

## Minimal Case Packet Shape

Implement a simple, explicit case packet structure.

The exact internal representation may be a dictionary or simple functions. Do not introduce a heavy class hierarchy.

A minimal valid case packet should contain fields equivalent to:

```json
{
  "case_id": "billing_dispute_vendor_x",
  "case_type": "billing_dispute",
  "title": "Billing dispute with Vendor X",
  "objective": "Contest an incorrect invoice charge.",
  "counterparties": [],
  "source_materials": [],
  "extracted_facts": [],
  "timeline_events": [],
  "open_issues": [],
  "missing_evidence": [],
  "contradictions": [],
  "drafts": [],
  "decisions": [],
  "status": "active",
  "next_step": ""
}
```

The implementation may include a small `schema_version` field if useful.

Required scalar fields:

- `case_id`
- `case_type`
- `title`
- `objective`
- `status`
- `next_step`

Required list fields:

- `counterparties`
- `source_materials`
- `extracted_facts`
- `timeline_events`
- `open_issues`
- `missing_evidence`
- `contradictions`
- `drafts`
- `decisions`

All required list fields must normalize missing or invalid values to empty lists when creating a packet from input.

Required scalar fields must normalize to stripped strings.

A packet with an empty `case_id`, empty `title`, or empty `objective` must be invalid.

---

## Required Functions

In `orchestrator/case_packet.py`, implement minimal functions with names close to these:

```python
def normalize_case_packet(payload: dict) -> dict:
    ...
```

```python
def validate_case_packet(packet: dict) -> dict:
    ...
```

```python
def save_case_packet(packet: dict) -> Path:
    ...
```

```python
def load_case_packet(case_id: str) -> dict:
    ...
```

Validation must return a structured result rather than raising for ordinary invalid packet content.

Acceptable validation result shape:

```json
{
  "valid": true,
  "errors": []
}
```

For invalid packets:

```json
{
  "valid": false,
  "errors": ["case_id is required"]
}
```

Path or JSON read/write errors may raise normal Python exceptions.

Keep all logic deterministic.

No model calls.

No provider calls.

No verifier registry changes.

---

## CLI Surface

Add two minimal CLI commands to `main.py`:

```bash
python main.py case-packet-create <case_packet_input_json_path>
```

```bash
python main.py case-packet-show <case_id>
```

### `case-packet-create`

Behavior:

1. Read the input JSON file.
2. Normalize the payload into a case packet.
3. Validate the normalized packet.
4. If invalid:
   - print JSON validation result
   - do not persist the packet
5. If valid:
   - persist the packet to `data/case_packets/<case_id>.json`
   - print JSON containing at minimum:
     - `created: true`
     - `case_id`
     - `path`
     - `validation`

This command may mutate only `data/case_packets/`.

It must not create tasks, runs, recommendations, artifacts, verifier results, or global state.

### `case-packet-show`

Behavior:

1. Load the case packet by id.
2. Print the packet JSON.
3. Do not mutate any state.

If the packet does not exist, the command should print a clear error message and not crash with a traceback during normal use.

---

## Required Tests

Create `tests/test_phase_58_case_packet_substrate.py`.

Tests must cover at least:

### 1. Valid packet normalization and validation

Given a minimal payload with required scalar fields, normalization should produce all required case-state categories.

Expected:

- validation returns `valid: true`
- required list fields exist
- missing list fields become empty lists

### 2. Invalid packet rejection

Given a payload missing `case_id`, `title`, or `objective`, validation should return `valid: false`.

Expected:

- validation includes a useful error
- no packet is saved when using the CLI create path

### 3. Persistence and load round trip

A valid packet should save to `data/case_packets/<case_id>.json`.

Loading by `case_id` should return the same core packet fields.

### 4. CLI create surface

Calling:

```bash
python main.py case-packet-create <input_path>
```

with a valid packet should print JSON with:

- `created: true`
- matching `case_id`
- validation result

### 5. CLI show surface

Calling:

```bash
python main.py case-packet-show <case_id>
```

should print the persisted packet JSON.

### 6. No hidden orchestration mutation

The case packet create/show commands must not mutate:

- `data/runs/`
- `data/tasks/`
- `data/artifacts/`
- `data/verifier_results/`
- `data/reviewer_recommendations/`
- global state file

The only allowed mutation is the case packet JSON file under `data/case_packets/`.

### 7. Path traversal protection

A case id containing unsafe path traversal, such as `../escape`, must not write outside `data/case_packets/`.

The implementation may reject unsafe ids or sanitize them deterministically, but the behavior must be tested.

---

## Implementation Constraints

Keep the implementation small.

Prefer simple functions.

Do not introduce:

- dataclass hierarchy unless truly simpler
- pydantic or external schema libraries
- database abstractions
- async behavior
- background workers
- connector logic
- model calls
- generalized workflow engines

The goal is inspectable local substrate, not framework expansion.

---

## Success Criteria

This phase is complete only when:

1. `orchestrator/case_packet.py` exists.
2. Minimal case packet normalization exists.
3. Minimal case packet validation exists.
4. Valid packets can be saved under `data/case_packets/`.
5. Saved packets can be loaded by `case_id`.
6. `main.py` exposes:
   - `case-packet-create`
   - `case-packet-show`
7. Invalid packets are rejected without persistence.
8. Tests cover valid, invalid, persistence, CLI create, CLI show, no hidden mutation, and path traversal protection.
9. Existing tests continue to pass.
10. `docs/ACTION_LOG.md` is updated with a concise Phase 58 completion entry.
11. `docs/PHASE_INDEX.md` is updated only after completion:
    - add `58. PHASE_58.md — Minimal Proving-Ground Case Packet Substrate`
    - mark `PHASE_58.md` complete in optional completion tracking
    - set Current Phase back to `(none — awaiting next phase definition)`

---

## Completion Report Required

At completion, report:

- files created
- files modified
- exact CLI commands added
- test command run
- test result
- whether any state surfaces besides `data/case_packets/` were mutated during tests
- any assumptions or uncertainties

Then STOP.

Do not propose or implement Phase 59.

---

## Phase Boundary Reminder

This phase creates the first case packet substrate.

It does not create case intelligence.

The point is to make the case legible before making it powerful.
