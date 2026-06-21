# INTAKE_TRIAGE_DESIGN_03.md

## Intake/Triage Design 03: Input Shape and Evidence Sources

---

## Goal

Define the minimum input contract and evidence-source rules for the future intake judgment layer.

This artifact should specify what the intake layer is allowed to receive, what evidence it is allowed to use when deciding `proceed`, `clarify`, or `blocked`, and what it must not silently assume.

This is a **design artifact**.

It is not:
- an implementation phase
- a planner phase
- an API design
- a connector implementation plan
- a full capability model
- a transport specification

Its job is narrower:

to define the first honest input boundary for intake judgment before any intake implementation begins.

---

## Why This Artifact Exists

`INTAKE_TRIAGE_DESIGN_01_REVISED.md` established the constitutional intake boundary.

`INTAKE_TRIAGE_DESIGN_02.md` established the machine-readable outcome contract.

But one major ambiguity still remains:

**what evidence is the intake layer actually allowed to judge from?**

Without that boundary, a future implementation could drift into exactly the wrong behaviors:

- invent missing facts from weak context
- silently assume tools or permissions exist
- treat conversational implication as confirmed evidence
- collapse “not provided” into “probably available”
- mix operator request, inferred context, and connected capability into one fuzzy blob

That would destroy the honesty the intake layer is supposed to protect.

This artifact exists to prevent that.

---

## Core Design Question

Before the intake layer emits `proceed`, `clarify`, or `blocked`, what is the minimum structured input it may rely on, and what sources of evidence are legitimate?

This artifact answers that question.

---

## Required Design Outcome

Define:

1. the minimum intake input object
2. the allowed evidence-source classes
3. the distinction between:
   - explicit request content
   - confirmed environment/context
   - inferred but unconfirmed assumptions
4. the rules for how intake judgment may use each class
5. the conditions under which lack of evidence produces:
   - `clarify`
   - `blocked`

The result must remain:

- small
- explicit
- machine-meaningful
- architecturally honest
- compatible with the current bounded execution core

---

## What This Artifact Is NOT About

This artifact is NOT about:

- how decomposition works
- planner logic
- full task schema design
- connector implementation details
- full permission systems
- ranking downstream task options
- long-term memory architecture
- full ontology design
- full product UX flows
- network transport details

This artifact defines the intake input/evidence boundary only.

---

## Required Intake Input Shape

The intake layer should judge from a small structured input object.

A minimum acceptable conceptual shape is:

```json
{
  "objective_text": "...",
  "provided_artifacts": [],
  "confirmed_context": {},
  "available_capabilities": []
}
```

This artifact does not require these exact field names in future implementation, but it does require these conceptual components.

### Required input components

#### 1. `objective_text`
The raw human objective or request.

This is required.

It is the primary thing being judged.

#### 2. `provided_artifacts`
Any concrete artifacts the operator has already supplied or explicitly attached.

Examples:
- uploaded files
- pasted structured data
- linked documents the system can actually access
- explicitly identified repo snapshot
- explicitly provided screenshots

This is distinct from merely mentioned artifacts.

#### 3. `confirmed_context`
Structured facts the system is allowed to treat as actually available and current.

Examples:
- active repo snapshot present
- connected source available
- workspace initialized
- current run exists
- specific file supplied
- specific account/tool permission confirmed

This must contain confirmed facts only.

#### 4. `available_capabilities`
The bounded set of capabilities/tools/connectors the system is actually allowed to assume are usable for this intake attempt.

Examples:
- local repo snapshot inspection available
- Gmail connector available
- calendar connector available
- no note source connected
- no Slack connector available

This is not a wish list.
It is the confirmed capability surface.

---

## Evidence Source Classes

The intake layer must distinguish among three evidence classes.

### Class A: Explicit request evidence

This comes directly from what the human explicitly said or supplied.

Examples:
- the objective text itself
- explicitly stated constraints
- explicitly named output form
- explicitly attached files or pasted data

This evidence is always admissible.

But it does not prove capability availability by itself.

### Class B: Confirmed system/environment evidence

This comes from facts the system has actually verified or already possesses in structured form.

Examples:
- connected tool availability
- current repo snapshot presence
- known file existence from current supplied materials
- confirmed active run or workspace state
- permission confirmed by actual connector availability

This evidence is admissible and may support `proceed` or `blocked`.

### Class C: Inferred but unconfirmed assumptions

This includes guesses based on implication, habit, or conversational probability.

Examples:
- “the user probably has the file”
- “they likely mean CSV”
- “the connector is probably available”
- “the repo probably still looks like it did last week”
- “this request probably means X rather than Y”

This evidence is **not sufficient** for `proceed`.

This evidence may be used only to formulate a clarification or to explain uncertainty, never to silently authorize decomposition.

---

## Governing Evidence Rule

The intake layer must follow this rule:

**Only explicit request evidence and confirmed system/environment evidence may authorize `proceed`.**

Inferred but unconfirmed assumptions may not authorize decomposition.

That is the key protection in this artifact.

Without it, the intake layer becomes a guess engine.

---

## Relationship Between Evidence and Outcomes

### Proceed

`proceed` is valid only when:

- the objective is bounded enough from explicit request evidence
- and all required environmental/capability assumptions are confirmed rather than guessed

If a required condition depends on an unconfirmed assumption, `proceed` is not allowed.

### Clarify

`clarify` is appropriate when:

- the missing piece is interpretive
- the ambiguity lives in the request framing itself
- one bounded additional input would resolve it

Typical evidence pattern:
- explicit request evidence is present
- confirmed environment may be sufficient
- but the objective remains materially underdetermined

### Blocked

`blocked` is appropriate when:

- the obstacle is environmental, capability-based, permission-based, or evidence-based
- the problem is not just interpretation
- the system cannot honestly proceed even if it guessed the intended workflow

Typical evidence pattern:
- the request may be understandable enough
- but confirmed context or capability evidence shows a real obstacle

---

## Admissible vs Inadmissible Assumptions

The intake layer must stay honest about what it knows.

### Admissible

- “A repo snapshot was explicitly provided.”
- “The user explicitly said the source format is CSV.”
- “The Gmail connector is currently available.”
- “No note source is connected.”
- “A required file is present in the provided artifacts.”

### Inadmissible as grounds for proceed

- “The user probably meant CSV.”
- “They mentioned a spreadsheet once, so a current spreadsheet is probably available.”
- “The connector might be enabled.”
- “This repo is probably unchanged since the last snapshot.”
- “This request sounds like a standard workflow, so decomposition can start.”

These may justify:
- a clarification question
- or an explanation of uncertainty

They may not justify `proceed`.

---

## Required Missing-Evidence Rule

This artifact should explicitly define:

**absence of confirmed evidence is not the same as evidence of absence, but it is also not permission to proceed.**

That means:

- if the system lacks confirmation of a required interpretive distinction:
  - use `clarify`

- if the system lacks confirmation of a required capability, permission, connector, or artifact:
  - use `blocked` when the missing condition is environmental
  - use `clarify` only when the missing condition is truly a request-side ambiguity

This rule matters because otherwise “not confirmed” becomes a loophole for speculative progress.

---

## Input Boundary Rules

### Rule 1: Intake must judge from current evidence, not stale assumptions

If the system does not have a current snapshot, current file, or current connector state, it must not silently rely on older state as if it were current.

### Rule 2: Mentioned is not provided

A human referencing a file, dataset, connector, or repo is not the same as supplying or confirming it.

### Rule 3: Possible is not available

A capability the system could theoretically support is not the same as a capability currently available for this intake attempt.

### Rule 4: Familiar is not confirmed

Prior project history may help frame a clarification, but it does not by itself authorize `proceed` when current evidence is missing.

---

## Human-Facing Explanation Requirement

The intake result should remain explainable in terms of evidence.

Examples in spirit:

- `clarify`:
  “I can help, but I still need to know whether your input will be screenshots, CSV exports, or manual entries.”

- `blocked`:
  “I understand the request, but I cannot proceed yet because no accessible note source is currently available.”

- `proceed`:
  “I have both the request and the required current context to frame this into bounded work.”

This artifact does not require final UX wording.
It requires that explanations remain grounded in the actual evidence state.

---

## Relationship To Current Architecture

This artifact is especially important because the current project already depends on current evidence boundaries in practice.

For example:
- fresh repo snapshots matter
- current files matter
- current connector/tool availability matters
- stale assumptions are already known to be risky

This design should preserve that discipline at the future intake boundary.

The intake layer should become broader by using confirmed evidence cleanly, not by becoming more willing to guess.

---

## Protected Non-Goals

This design rejects the following premature moves:

- allowing inferred assumptions to authorize `proceed`
- treating old snapshots as current by default
- treating mentioned artifacts as provided artifacts
- treating theoretical capability as confirmed availability
- merging request text, environment state, and inferred context into one undifferentiated input blob
- building a large ontology of evidence types at this stage

The goal is to define a minimum honest evidence boundary, not a total world model.

---

## Deliverable Shape

This artifact should establish:

1. the minimum intake input components
2. the allowed evidence-source classes
3. the governing evidence rule
4. the relationship between evidence classes and the three intake outcomes
5. the missing-evidence rule
6. the protected input-boundary rules

No implementation plan is required yet.

No intake phase should begin until this input/evidence boundary is judged coherent.

---

## Validation Standard

This artifact is acceptable only if it:

- clearly distinguishes explicit evidence from confirmed context and unconfirmed inference
- prevents guessed context from authorizing decomposition
- keeps `clarify` and `blocked` grounded in different kinds of missing evidence
- remains compatible with the current architecture’s emphasis on fresh, confirmed state
- does not drift into ontology or transport sprawl

---

## Expected Next Step After This Artifact

If this artifact is ratified, the likely next move would be either:

- a bounded implementation phase for a minimal service-level intake judgment function
- or one final design artifact for how intake judgment hands off into bounded decomposition without planner drift

Either way, the system would now have:
- constitutional intake meanings
- machine-readable intake outcomes
- honest intake evidence boundaries

That would be enough to begin very small implementation work safely.
