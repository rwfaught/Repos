# INTAKE_TRIAGE_DESIGN_01_REVISED.md

## Intake/Triage Design 01: Proceed / Clarify / Blocked Boundary

---

## Goal

Define the first bounded design artifact for the future intake boundary.

This artifact specifies the minimum honest judgment layer that must exist between:

- raw human objective
- bounded orchestrator-executable work

Its purpose is to prevent future intake work from collapsing into vague planner behavior, agent theater, speculative decomposition, or hidden blocked states.

This is a **design artifact**.

It is not:
- a feature phase
- an implementation packet
- an API design
- a planner expansion phase
- a full product specification

Its job is narrower:

to define the first safe constitutional shape of intake judgment before any implementation work begins.

---

## Why This Artifact Exists

The project now has:

- a functioning bounded execution core
- explicit review and recommendation handling
- materially improved deterministic verification
- a ratified project vision that distinguishes:
  - present bounded execution reality
  - future intake-facing direction
- an explicit governing principle: keep the human in honest contact with what is actually happening

That makes the next missing conceptual capability clearer.

The missing bridge is not more execution power.

It is an honest intake judgment layer that decides whether decomposition may begin at all.

Without that layer, future movement toward broader human-objective handling risks producing:

- a shadow planner
- false confidence on ambiguous requests
- silent conversion of vague goals into bad internal tasks
- hidden blocked states
- interface theater instead of governed execution

This artifact exists to prevent that.

---

## Core Design Question

Before the system decomposes a human objective into bounded internal work, what is the smallest honest judgment it must make?

This artifact answers:

- `proceed`
- `clarify`
- `blocked`

This is the minimum safe intake boundary.

---

## Required Design Outcome

Define the meaning, boundary conditions, and observable consequences of these three intake outcomes:

1. `proceed`
2. `clarify`
3. `blocked`

These outcomes must remain:

- explicit
- non-overlapping
- machine-meaningful
- human-explainable
- architecturally compatible with the current execution core

---

## What This Artifact Is NOT About

This artifact is NOT about:

- implementing a planner
- generating task trees automatically
- building a chat UX
- defining multi-turn conversational policy
- building HTTP or service interfaces
- defining permission connectors in full
- building ambiguity resolution heuristics exhaustively
- creating a full customer-facing product workflow
- adding a broad intake ontology or schema system

This artifact defines the first honest intake gate only.

---

## Intake Outcome Semantics

### 1. Proceed

`proceed` means:

- the objective is bounded enough to translate honestly into internal work
- the system has enough information to begin bounded decomposition
- no critical ambiguity blocks safe execution framing
- no known capability or permission gap makes execution dishonest at the outset

`proceed` does NOT mean:
- success is guaranteed
- all downstream work is already specified
- no later review or recommendations will be needed

It means only:
- bounded internal work can now be created honestly

### 2. Clarify

`clarify` means:

- the objective is plausible and potentially actionable
- but one or more missing distinctions make direct decomposition dishonest or underdetermined
- the system should ask for a narrow clarification rather than pretend the request is already well formed

`clarify` exists to prevent false certainty.

It should be used when the request is:
- materially underspecified
- ambiguous across meaningfully different workflows
- missing a required source/data-form distinction
- missing a key output-form decision
- otherwise not yet safe to decompose truthfully

`clarify` does NOT mean:
- the system is blocked forever
- the system should begin speculative planning anyway

It means:
- a bounded additional input is needed before decomposition

### 3. Blocked

`blocked` means:

- the objective cannot honestly proceed right now because a required condition is not satisfied
- the missing condition is not merely interpretive ambiguity
- execution framing would be dishonest without resolving it

Examples may include:
- missing required permission
- missing connector or data source
- unsupported capability
- policy restriction
- absent required artifact/input
- impossible request under current system boundaries

`blocked` must not collapse into vague failure language.

It should diagnose why progress cannot occur.

---

## Required Blocked-State Taxonomy

`blocked` must not be one undifferentiated status.

At minimum, the design should preserve blocked classes such as:

- `missing_input`
- `missing_permission`
- `missing_connector`
- `unsupported_capability`
- `policy_restricted`
- `insufficient_evidence`

Labels may be refined slightly later, but the principle must hold:

**blocked states should name the real obstacle, not merely announce stoppage.**

Different blocked causes imply different operator actions.
That is why the taxonomy matters.

---

## Boundary Rules

### Clarify vs Blocked

This is the most important distinction.

- `clarify` = the system could proceed if the human answers a bounded interpretive question
- `blocked` = the system cannot proceed because some capability, permission, evidence, or required input condition is absent

The system must not:
- ask the user to “clarify” environmental failures
- declare “blocked” when it merely failed to ask a precise question

That would weaken honest contact.

### Proceed vs Clarify

The second important distinction is:

- `proceed` = decomposition is already honest
- `clarify` = decomposition would currently be a guess

A plausible guess is not enough.

The system should not silently choose among materially different interpretations and call that decomposition.

---

## Observable Consequences

This artifact also defines what each intake outcome permits.

### Proceed permits
- bounded internal task decomposition
- normal downstream orchestrator flow
- later verification, review, and recommendation behavior as needed

### Clarify permits
- a narrow clarification request
- no bounded decomposition yet
- no speculative internal task creation masked as progress

### Blocked permits
- a precise explanation of the blocking condition
- no decomposition
- no speculative planning presented as actionable progress

This matters because the intake judgment must control behavior, not merely label it.

---

## Human-Facing Explanation Requirement

All three outcomes must be explainable in normal language.

The machine meaning may be structured.
The human-facing explanation must remain legible and actionable.

Illustrative examples:

- `proceed`: “I have enough to frame this into bounded work.”
- `clarify`: “I can help, but I still need to know whether your source data will be screenshots, CSV exports, or manual entries.”
- `blocked`: “I cannot do this yet because no note source is connected.”

This artifact does not define final UX copy.
It preserves the requirement that explanation remain human-usable.

---

## Relationship To Current Architecture

This intake artifact must sit before the current execution machinery.

The current execution core already handles:

- bounded task execution
- verification
- review and recommendation landing
- explicit control surfaces
- inspectable state

This artifact should not collapse intake into the existing planner/coder/reviewer role model prematurely.

It must explicitly protect against:

- making the reviewer a pseudo-intake layer
- turning the planner into a vague human-objective interpreter
- bypassing bounded task creation with speculative orchestration

The current execution core remains below the intake gate.

---

## Recommended Future Layering

This artifact defines the future layering model in principle:

1. human objective
2. intake judgment (`proceed` / `clarify` / `blocked`)
3. bounded internal task decomposition
4. normal orchestrator execution
5. verification / review / recommendation surfaces
6. explicit next-step visibility

This ordering matters.

The system should become broader only by carrying current discipline outward, not by loosening it.

---

## Protected Non-Goals

This design rejects the following premature moves:

- speculative decomposition before intake judgment
- planner-led intake interpretation without explicit boundary rules
- vague “needs more info” states that hide whether the problem is ambiguity or blockage
- blocked states with no actionable diagnosis
- conversational fluency standing in for intake truth
- multiple intake meanings across different interfaces

The intake boundary should preserve one governing semantics, just as the wider system is expected to do across future interfaces.

---

## Deliverable Shape

This design artifact should establish:

1. crisp definitions of `proceed`, `clarify`, and `blocked`
2. a minimum blocked-state taxonomy
3. boundary rules distinguishing:
   - proceed vs clarify
   - clarify vs blocked
4. observable consequences for each outcome
5. a human-facing explanation requirement
6. protected architectural boundaries and non-goals

No implementation plan is required yet.

No phase packet should be opened until this conceptual boundary is coherent.

---

## Validation Standard

This artifact is acceptable only if it:

- makes the intake boundary more honest, not more ambitious
- reduces room for speculative decomposition
- protects the distinction between interpretive ambiguity and true blockage
- keeps outcome labels tied to behavior, not just prose
- remains compatible with the current bounded execution architecture
- does not drift into product theater or premature implementation detail

---

## Expected Next Step After This Artifact

If this artifact is ratified, the likely next move would be either:

- a second design artifact for machine-readable intake outcome shapes and return structures
- or a bounded implementation phase for a service-level intake judgment surface

Neither should begin until this first conceptual boundary is judged sound.
