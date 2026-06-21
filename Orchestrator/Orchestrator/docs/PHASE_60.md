# PHASE_60.md

## Phase 60 — Controlled Operator Case Packet Creation Helper

---

## Purpose

Add a deterministic operator-controlled helper for creating skeletal case packets from a small seed input.

Phase 58 made the case packet exist.

Phase 59 made the case packet legible.

Phase 60 reduces the friction of starting a case packet without making the system intelligent, autonomous, or intake-driven.

The operator should no longer need to manually construct a full case-packet JSON object with every required field.

Instead, the operator may provide a small seed JSON containing the core identity/objective fields, and the system will create a normalized skeletal packet using the existing Phase 58 substrate.

This phase improves controlled manual creation.

It does not create intake automation.

It does not create case intelligence.

---

## Governing Context

This phase follows directly from:

- docs/PHASE_58.md
- docs/PHASE_59.md
- docs/RERANK_01_RESULT.md
- docs/PRODUCT_STRATEGY_03.md
- docs/PRODUCT_DESIGN_02.md
- docs/INTAKE_TRIAGE_DESIGN_04.md
- docs/PROJECT_VISION.md
- docs/CURRENT_SUCCESS_CRITERION.md

Current repo state:

- Phase 58 created the local case-packet substrate.
- Phase 59 created read-only case-packet inspectability and readiness surfaces.
- Current Phase is `(none — awaiting next phase definition)`.

This phase does not reopen Phase 58 or Phase 59.

It adds a narrow creation convenience layer on top of them.

---

## Active Layer

implementation

---

## Active Decision Membrane

This phase may decide only:

- how to accept a small operator-provided seed input
- how to normalize that seed into a complete skeletal case packet
- how to validate the resulting packet before persistence
- how to expose this behavior through one narrow CLI command
- how to test that the helper mutates only the approved case-packet storage surface

This phase must not decide:

- how intake should connect to case packets
- how tasks should be created from case packets
- how source materials should be ingested
- how facts should be extracted
- how timeline events should be inferred
- how contradictions should be detected
- how case strength should be evaluated
- how legal, medical, insurance, or policy merit should be judged
- how drafts should be generated
- how providers/models should be routed
- how workflow planning should operate

The helper is a controlled input adapter.

It is not intake.

It is not a planner.

It is not a case assistant.

---

## Required Outcome

After this phase, the repo must support creation of a skeletal case packet from a smaller operator seed JSON.

The operator must be able to run:

    python main.py case-packet-init <case_packet_seed_json_path>

The command must:

1. Read a seed JSON file.
2. Normalize the seed into a complete case packet using existing case-packet substrate logic.
3. Validate the normalized packet.
4. If invalid:
   - print JSON validation result or a clear JSON failure object
   - do not persist a packet
5. If valid:
   - persist the packet under data/case_packets/<case_id>.json
   - print JSON containing at minimum:
     - created: true
     - initialized: true
     - case_id
     - path
     - validation
     - summary or readiness information if cheaply available from existing Phase 59 logic

The command may mutate only:

- data/case_packets/

It must not mutate:

- data/runs/
- data/tasks/
- data/artifacts/
- data/verifier_results/
- data/reviewer_recommendations/
- global state file

---

## Seed Input Shape

The seed JSON should be intentionally small.

Required seed fields:

- case_id
- case_type
- title
- objective

Optional seed fields:

- status
- next_step
- counterparties

The implementation may also accept optional simple list fields already supported by the Phase 58 packet shape, but it must not require them.

Recommended minimal seed example:

    {
      "case_id": "billing_dispute_vendor_x",
      "case_type": "billing_dispute",
      "title": "Billing dispute with Vendor X",
      "objective": "Contest an incorrect invoice charge.",
      "status": "active",
      "next_step": "Collect invoice and payment receipt.",
      "counterparties": [
        "Vendor X"
      ]
    }

Missing optional list fields must become empty lists through existing normalization behavior.

Missing optional scalar fields should normalize to strings.

If status is missing, an acceptable default is:

    active

If next_step is missing, an acceptable default is:

    ""

The implementation may choose a conservative default for next_step, but it must not infer substantive case action from the objective.

Acceptable default:

    ""

Also acceptable:

    "Review case packet and add source materials."

The default must be deterministic and tested.

---

## Existing Substrate

Phase 58 created:

    def normalize_case_packet(payload: dict) -> dict:
        ...

    def validate_case_packet(packet: dict) -> dict:
        ...

    def save_case_packet(packet: dict) -> Path:
        ...

    def load_case_packet(case_id: str) -> dict:
        ...

Phase 59 added:

    def assess_case_packet_readiness(packet: dict) -> dict:
        ...

    def summarize_case_packet(packet: dict) -> dict:
        ...

Phase 60 must reuse this substrate.

Do not replace it with a larger framework.

Do not create a second creation path that bypasses normalization or validation.

---

## Required Functions

Add a small deterministic helper function to orchestrator/case_packet.py.

Required function name may be close to:

    def initialize_case_packet_from_seed(seed: dict) -> dict:
        ...

The function must:

1. Accept a seed dictionary.
2. Build a candidate packet dictionary.
3. Fill all required scalar and list fields.
4. Apply existing normalization logic.
5. Return the normalized packet.

It should not save the packet directly unless the existing code style strongly favors that.

Persistence should remain explicit through save_case_packet().

Validation should remain explicit through validate_case_packet().

The helper must not:

- inspect source material files
- read external documents
- call models
- infer facts
- infer timeline events
- infer open issues
- generate drafts
- create decisions
- create tasks
- mutate global state

---

## CLI Surface

Add one command to main.py:

    python main.py case-packet-init <case_packet_seed_json_path>

### case-packet-init

Behavior:

1. Read the seed JSON file.
2. Initialize a skeletal case packet from the seed.
3. Validate the initialized packet.
4. If validation fails:
   - print JSON failure/validation output
   - do not save
5. If validation passes:
   - save the packet
   - print JSON success output
6. Do not mutate any state outside data/case_packets/.

Successful output must be JSON.

Invalid seed output should be JSON where practical.

Not-found seed file errors may print a clear normal-use error, consistent with existing CLI patterns.

Unsafe case ids must be rejected before write by existing path safety behavior.

---

## Output Requirements

All successful outputs must be JSON.

The success object must include at minimum:

- created: true
- initialized: true
- case_id
- path
- validation

It may include:

- summary
- readiness

If summary/readiness is included, it must use existing Phase 59 logic and must not trigger any new reasoning behavior.

Do not introduce:

- colored output
- interactive prompts
- background work
- non-deterministic fields
- timestamps unless already standard in this codebase for similar records

---

## Non-Goals

Do not implement:

- intake-to-case-packet creation
- intake-to-decomposition automation
- task creation
- hidden task creation
- planner behavior
- document parsing
- OCR
- PDF extraction
- email ingestion
- connector access
- automated evidence classification
- automated fact extraction
- timeline generation
- contradiction detection
- case merit scoring
- legal reasoning
- medical reasoning
- insurance-policy reasoning
- case outcome recommendation
- settlement recommendation
- autonomous drafting
- filing, sending, or submission
- provider/model calls
- recommendation creation
- multi-case search
- GUI
- database migration system
- workflow engine expansion

Do not create a broad case-management framework.

Do not mutate existing runs, tasks, artifacts, verifier results, reviewer recommendations, or global state.

---

## Files To Create

Create:

- tests/test_phase_60_case_packet_init.py

---

## Files To Modify

Modify only as needed:

- orchestrator/case_packet.py
- main.py
- docs/PHASE_INDEX.md
- docs/ACTION_LOG.md

Do not modify unrelated recommendation, intake, provider, verifier, run-manager, task, artifact, or global-state behavior.

---

## Required Tests

Create tests/test_phase_60_case_packet_init.py.

Tests must cover at least:

### 1. Minimal seed initializes complete packet

Given a seed with:

- case_id
- case_type
- title
- objective

The initialized packet must include all required Phase 58 scalar and list fields.

Expected:

- required scalar fields exist
- required list fields exist
- list fields default to empty lists
- status defaults deterministically
- next_step defaults deterministically

### 2. Optional seed fields are preserved

Given a seed with optional fields:

- status
- next_step
- counterparties

The initialized packet must preserve normalized versions of those fields.

### 3. Validation occurs before persistence

Given an invalid seed missing case_id, title, or objective:

- validation fails
- no packet is saved

### 4. CLI init success

Calling:

    python main.py case-packet-init <seed_path>

with a valid seed must print JSON containing at minimum:

- created: true
- initialized: true
- case_id
- path
- validation

### 5. CLI init invalid seed

Calling:

    python main.py case-packet-init <seed_path>

with an invalid seed must not persist a packet and must print validation/failure JSON.

### 6. Path traversal remains blocked

A seed with unsafe case_id such as:

    ../escape

must not write outside data/case_packets/.

Rejecting unsafe ids is acceptable and preferred.

### 7. Init mutates only case-packet storage

The init command must not mutate:

- data/runs/
- data/tasks/
- data/artifacts/
- data/verifier_results/
- data/reviewer_recommendations/
- global state file

The only allowed mutation is the initialized packet file under data/case_packets/.

### 8. Existing Phase 58 behavior remains intact

Existing tests for:

- case-packet-create
- case-packet-show

must continue to pass.

### 9. Existing Phase 59 behavior remains intact

Existing tests for:

- case-packet-summary
- case-packet-validate
- readiness classification

must continue to pass.

---

## Implementation Constraints

Keep the implementation small.

Prefer plain functions.

Do not introduce:

- new class hierarchy
- pydantic or external schema libraries
- database abstractions
- async behavior
- background workers
- connector logic
- model calls
- provider calls
- generalized workflow utilities

The helper should be visibly boring.

That is the point.

It should reduce manual JSON burden, not increase system autonomy.

---

## Success Criteria

This phase is complete only when:

1. initialize_case_packet_from_seed() or equivalent exists.
2. case-packet-init CLI command exists.
3. minimal seed input creates a complete normalized packet.
4. validation occurs before persistence.
5. invalid seeds do not persist packets.
6. unsafe case ids cannot write outside data/case_packets/.
7. the init command mutates only data/case_packets/.
8. Phase 58 tests continue to pass.
9. Phase 59 tests continue to pass.
10. new Phase 60 tests pass.
11. broader existing tests continue to pass.
12. docs/ACTION_LOG.md is updated with a concise Phase 60 completion entry.
13. docs/PHASE_INDEX.md is updated only after completion:
    - add 60. PHASE_60.md — Controlled Operator Case Packet Creation Helper
    - mark PHASE_60.md complete in optional completion tracking if the file uses such tracking
    - set Current Phase back to (none — awaiting next phase definition)

---

## Completion Report Required

At completion, report:

- files created
- files modified
- exact CLI command added
- test commands run
- test results
- whether init mutated any state outside data/case_packets/
- any assumptions or uncertainties

Then STOP.

Do not propose or implement Phase 61.

---

## Phase Boundary Reminder

Phase 58 made the case packet exist.

Phase 59 made the case packet legible.

Phase 60 makes the case packet easier to start.

It does not make the case packet autonomous.
