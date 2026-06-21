# PHASE_59.md

## Phase 59 — Case Packet Readiness and Inspectability Surface

---

## Purpose

Add a minimal read-only inspectability surface for persisted case packets.

Phase 58 created the first local case-packet substrate.

Phase 59 makes that substrate operator-legible without making it intelligent.

The goal is to let an operator quickly answer:

- Is this case packet structurally valid?
- Which case-state categories are populated?
- Which case-state categories are empty?
- What is the packet's current status?
- What is the packet's next step?
- Is the packet ready for further human review, or is it still only a skeletal container?

This phase improves visibility.

It does not create case reasoning.

---

## Governing Context

This phase follows directly from:

- docs/PHASE_58.md
- docs/RERANK_01_RESULT.md
- docs/PRODUCT_STRATEGY_03.md
- docs/PRODUCT_DESIGN_02.md
- docs/INTAKE_TRIAGE_DESIGN_04.md
- docs/PROJECT_VISION.md
- docs/CURRENT_SUCCESS_CRITERION.md

Phase 58 closed with a minimal local case-packet substrate:

- orchestrator/case_packet.py
- tests/test_phase_58_case_packet_substrate.py
- python main.py case-packet-create <case_packet_input_json_path>
- python main.py case-packet-show <case_id>

This phase does not reopen the Phase 58 substrate decision.

It adds a narrow read-only layer on top of it.

---

## Active Layer

implementation

---

## Active Decision Membrane

This phase may decide only:

- how to summarize a persisted case packet deterministically
- how to expose validation/readiness information through read-only CLI commands
- how to report category population and emptiness
- how to test that the inspectability surface does not mutate case or orchestration state

This phase must not decide:

- how to ingest source documents
- how to extract facts
- how to infer timeline events
- how to resolve contradictions
- how to judge case strength
- how to recommend case outcomes
- how to draft appeals or dispute letters
- how to connect intake to case creation
- how to create orchestrator tasks from case packets
- how to route cases to providers or models
- how to implement a workflow engine

The packet remains a substrate.

The inspectability surface is a mirror, not a worker.

---

## Required Outcome

After this phase, the repo must support read-only inspection of an existing case packet.

The operator must be able to run commands that reveal:

1. whether the packet is structurally valid
2. validation errors, if any
3. the case id
4. title
5. case type
6. objective
7. status
8. next step
9. counts for each required list category
10. which categories are populated
11. which categories are empty
12. a deterministic readiness classification

The readiness classification must be simple and non-semantic.

It must not judge the case.

It must not determine legal, insurance, policy, or factual merit.

It may classify only structural readiness.

Acceptable readiness values:

- invalid
- skeletal
- partially_populated
- review_ready

Suggested deterministic meaning:

- invalid: validation fails
- skeletal: valid packet, but all required list categories are empty
- partially_populated: valid packet, at least one required list category is populated, but one or more important categories remain empty
- review_ready: valid packet with enough populated categories to support human review

The exact threshold for review_ready must be explicit in code and tests.

A conservative acceptable threshold:

- packet is valid
- source_materials has at least one item
- open_issues has at least one item
- missing_evidence or contradictions may be empty
- status is non-empty
- next_step is non-empty

This threshold is not a claim that the case is strong.

It means only that the packet has enough structure to be reviewed by a human.

---

## Non-Goals

Do not implement:

- document parsing
- OCR
- PDF extraction
- email ingestion
- connector access
- automated evidence classification
- automated fact extraction
- timeline generation from source materials
- contradiction detection
- legal reasoning
- medical reasoning
- insurance-policy reasoning
- case outcome recommendation
- settlement recommendation
- autonomous drafting
- filing, sending, or submission
- task decomposition
- hidden task creation
- planner behavior
- provider/model calls
- recommendation creation
- intake-to-case-packet creation
- intake-to-decomposition automation
- multi-case search
- GUI
- database migration system
- workflow engine expansion

Do not mutate case packet contents.

Do not mutate runs, tasks, artifacts, verifier results, reviewer recommendations, or global state.

---

## Files To Create

Create:

- tests/test_phase_59_case_packet_inspectability.py

---

## Files To Modify

Modify only as needed:

- orchestrator/case_packet.py
- main.py
- docs/PHASE_INDEX.md
- docs/ACTION_LOG.md

Do not modify unrelated recommendation, intake, provider, verifier, run-manager, task, artifact, or global-state behavior.

---

## Existing Substrate

Phase 58 created these functions in orchestrator/case_packet.py:

    def normalize_case_packet(payload: dict) -> dict:
        ...

    def validate_case_packet(packet: dict) -> dict:
        ...

    def save_case_packet(packet: dict) -> Path:
        ...

    def load_case_packet(case_id: str) -> dict:
        ...

Phase 59 may reuse and extend this module.

Do not replace the Phase 58 substrate with a larger framework.

---

## Required Functions

Add small deterministic helper functions to orchestrator/case_packet.py.

Required function names may be close to:

    def summarize_case_packet(packet: dict) -> dict:
        ...

    def assess_case_packet_readiness(packet: dict) -> dict:
        ...

The implementation may combine these if simpler, but the code must keep the concepts clear:

- validation
- category counts
- empty categories
- populated categories
- readiness classification

A suggested summary shape:

    {
      "case_id": "billing_dispute_vendor_x",
      "case_type": "billing_dispute",
      "title": "Billing dispute with Vendor X",
      "objective": "Contest an incorrect invoice charge.",
      "status": "active",
      "next_step": "Collect invoice and payment receipt.",
      "validation": {
        "valid": true,
        "errors": []
      },
      "category_counts": {
        "counterparties": 1,
        "source_materials": 2,
        "extracted_facts": 0,
        "timeline_events": 0,
        "open_issues": 1,
        "missing_evidence": 1,
        "contradictions": 0,
        "drafts": 0,
        "decisions": 0
      },
      "populated_categories": [
        "counterparties",
        "source_materials",
        "open_issues",
        "missing_evidence"
      ],
      "empty_categories": [
        "extracted_facts",
        "timeline_events",
        "contradictions",
        "drafts",
        "decisions"
      ],
      "readiness": {
        "level": "partially_populated",
        "reasons": [
          "packet is valid",
          "some case categories are populated",
          "review_ready threshold not met"
        ]
      }
    }

Readiness must be derived only from packet structure.

Do not inspect file contents.

Do not call models.

Do not infer facts.

---

## CLI Surface

Add two minimal read-only CLI commands to main.py:

    python main.py case-packet-summary <case_id>

    python main.py case-packet-validate <case_id>

### case-packet-summary

Behavior:

1. Load the persisted case packet by case_id.
2. Produce the deterministic summary/readiness object.
3. Print JSON.
4. Do not mutate state.

If the packet does not exist, print a clear error message and avoid a normal-use traceback.

### case-packet-validate

Behavior:

1. Load the persisted case packet by case_id.
2. Validate it with the existing validation logic.
3. Print the validation result as JSON.
4. Do not mutate state.

If the packet does not exist, print a clear error message and avoid a normal-use traceback.

---

## Output Requirements

All new CLI command outputs must be JSON for successful reads.

Error handling for not-found or unsafe case ids may print a clear plain-text error, consistent with the existing case-packet-show behavior.

Do not introduce colored output.

Do not introduce interactive prompts.

Do not introduce background work.

---

## Required Tests

Create tests/test_phase_59_case_packet_inspectability.py.

Tests must cover at least:

### 1. Summary includes required identity and state fields

Given a valid packet, summary output must include:

- case_id
- case_type
- title
- objective
- status
- next_step
- validation
- category_counts
- populated_categories
- empty_categories
- readiness

### 2. Category counts are deterministic

Given known list-field values, category_counts must report the correct count for each required list category.

### 3. Empty and populated categories are deterministic

Given a packet with some populated list categories and some empty categories:

- populated_categories must include the populated list fields
- empty_categories must include the empty list fields

### 4. Invalid packet readiness

Given an invalid packet, readiness level must be:

- invalid

The readiness reasons must identify that validation failed.

### 5. Skeletal packet readiness

Given a valid packet with all required list categories empty, readiness level must be:

- skeletal

### 6. Partially populated packet readiness

Given a valid packet with some populated required list categories but not enough for review_ready, readiness level must be:

- partially_populated

### 7. Review-ready packet readiness

Given a valid packet that meets the explicit review_ready threshold, readiness level must be:

- review_ready

### 8. CLI summary surface

Calling:

    python main.py case-packet-summary <case_id>

must print JSON containing the expected summary fields.

### 9. CLI validate surface

Calling:

    python main.py case-packet-validate <case_id>

must print JSON validation output.

### 10. Read-only behavior

The case-packet-summary and case-packet-validate commands must not mutate:

- data/case_packets/
- data/runs/
- data/tasks/
- data/artifacts/
- data/verifier_results/
- data/reviewer_recommendations/
- global state file

These commands are read-only.

### 11. Existing Phase 58 commands remain intact

Existing tests for:

- case-packet-create
- case-packet-show

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

The summary/readiness output should be deterministic and explainable from the packet alone.

---

## Success Criteria

This phase is complete only when:

1. case packet summary logic exists.
2. case packet readiness assessment exists.
3. readiness classification is deterministic and tested.
4. category counts are deterministic and tested.
5. populated and empty category lists are deterministic and tested.
6. main.py exposes:
   - case-packet-summary
   - case-packet-validate
7. both new CLI commands are read-only.
8. invalid, skeletal, partially_populated, and review_ready readiness states are tested.
9. no hidden mutation occurs outside permitted surfaces.
10. Phase 58 tests continue to pass.
11. broader existing tests continue to pass.
12. docs/ACTION_LOG.md is updated with a concise Phase 59 completion entry.
13. docs/PHASE_INDEX.md is updated only after completion:
    - add 59. PHASE_59.md — Case Packet Readiness and Inspectability Surface
    - mark PHASE_59.md complete in optional completion tracking if the file uses such tracking
    - set Current Phase back to (none — awaiting next phase definition)

---

## Completion Report Required

At completion, report:

- files created
- files modified
- exact CLI commands added
- test commands run
- test results
- whether read-only commands mutated any state
- any assumptions or uncertainties

Then STOP.

Do not propose or implement Phase 60.

---

## Phase Boundary Reminder

Phase 58 made the case packet exist.

Phase 59 makes the case packet legible.

It does not make the case packet smart.
