# PRODUCT_DESIGN_01.md

## Product Design 01: Autonomy and Interruption Thresholds for the First Proving Ground

---

## Goal

Define the first bounded autonomy/interruption model for Ro’s initial proving ground:

**claims / disputes / appeals-style casework for consequential personal or small-business paperwork problems.**

This artifact should specify:

- what Ro may do silently
- when Ro must ask for clarification
- when Ro must request approval
- when Ro must stop and explain that it is blocked
- how to preserve the human-first principle without turning the human into the process scheduler

This is a **design artifact**.

It is not:
- a feature phase
- a code implementation packet
- a complete product spec
- a transport design
- a UX copy deck

Its purpose is narrower:

to define how autonomy should feel and where interruption thresholds should sit in the first proving ground.

---

## Why This Artifact Exists

The strategy stack now says:

- Ro is the engine
- claims / disputes / appeals-style casework is the first proving ground
- the harness must justify its friction
- internal rigor is not the user experience
- repeated use matters more than one-time impressiveness

That means one design question now becomes central:

**When should Ro act quietly, and when should it interrupt the user?**

This matters because the proving ground is exactly the kind of work where both extremes fail.

If Ro interrupts constantly:
- the user becomes the process scheduler
- the burden is not reduced
- the harness feels bureaucratic

If Ro acts too freely:
- it risks overstepping on consequential casework
- it may send, assume, or escalate too much
- trust collapses

So the project needs a threshold model.

This artifact exists to define that model before implementation drifts into either human-burden-first or reckless autonomy.

---

## Core Design Question

In claims / disputes / appeals-style casework, what kinds of actions should Ro:

- perform silently
- perform only after clarification
- perform only after approval
- refuse or block pending missing conditions

This is the practical form of the autonomy question.

---

## Required Design Outcome

This artifact must define four operational modes:

1. **silent bounded autonomy**
2. **clarify-first**
3. **approval-required**
4. **blocked-with-explanation**

These modes must be tied to action categories, not just abstract principles.

If the artifact does not identify what kinds of actions belong in each mode, it is too vague.

---

## This Artifact Is NOT About

This artifact is NOT about:

- implementing the workflow engine
- final UI wording
- broad conversational policy
- general assistant behavior
- all future product domains
- connector-specific behavior in full detail
- legal advice policy
- building a full permissions framework

It is about threshold-setting for the first proving ground only.

---

## Governing Principle

The autonomy rule for the proving ground should be:

**Ro should carry the burden of process, but never quietly take over the burden of judgment.**

That means Ro should absorb:
- organization
- extraction
- state maintenance
- drafting preparation
- evidence tracking
- timeline maintenance
- bounded recommendations

But Ro should not quietly make:
- factual commitments on uncertain material
- external communications on the user’s behalf
- escalation decisions
- legal/financial judgment calls
- irreversible case-state changes that depend on the user’s intent

This is the backbone of the threshold model.

---

## Mode 1: Silent Bounded Autonomy

### Definition
Ro may act without interrupting the user when the action is:
- reversible or low-risk
- internally scoped
- organizational rather than judgmental
- supported by available materials
- not an external commitment

### In this proving ground, silent bounded autonomy should include:
- ingesting provided files
- extracting dates, amounts, names, invoice numbers, policy numbers, claim references, and similar facts
- assembling draft timelines from provided materials
- tracking document inventory
- noticing contradictions or missing materials
- grouping artifacts by relevance
- producing internal summaries
- preparing draft checklists
- routing low-stakes extraction or classification subtasks to weaker/cheaper models
- maintaining local case state

### Why
These actions reduce burden without requiring the user to supervise process minutiae.

They are exactly the kind of work the user should not have to micromanage.

---

## Mode 2: Clarify-First

### Definition
Ro must ask a bounded question when it lacks an interpretive distinction required to proceed honestly.

Clarify-first is not for environmental failure.
It is for ambiguous intent, scope, or framing.

### In this proving ground, clarify-first should include:
- uncertain desired outcome
  - “Do you want to dispute the fee, request an explanation, or request reimbursement?”
- uncertain case boundary
  - “Should this revised invoice be treated as part of the same dispute?”
- uncertain document role
  - “Is this receipt intended as proof of payment for the disputed charge?”
- uncertain communication posture
  - “Do you want a firm challenge, a neutral information request, or a conciliatory draft?”
- uncertain priority when multiple open issues exist

### Why
These are not places where Ro should guess.
They are places where one short clarification prevents downstream distortion.

---

## Mode 3: Approval-Required

### Definition
Ro must request explicit user approval before taking actions that create an external commitment, formalize a consequential interpretation, or lock in a move that the user may reasonably want to own.

### In this proving ground, approval-required should include:
- sending or finalizing outgoing dispute letters
- sending or finalizing claim submissions
- submitting appeals
- sending accusatory or escalatory communications
- choosing an escalation path when multiple paths exist
- freezing a timeline or case summary as a formal version for external use
- using a draft that makes factual assertions the user has not yet confirmed
- any action that could materially affect money, liability, deadline posture, or relationship posture

### Why
This is where “helpful process support” becomes “representation of the user.”
Ro should not cross that boundary quietly.

---

## Mode 4: Blocked-With-Explanation

### Definition
Ro must stop and explain when a required condition is absent and proceeding would be dishonest.

Blocked is not “I need a preference.”
Blocked is “I cannot honestly continue because something necessary is missing.”

### In this proving ground, blocked-with-explanation should include:
- required documents not provided
- inaccessible supporting evidence
- missing connector/source when the next step depends on it
- absent dates or identifiers needed for the next bounded move
- unsupported workflow step outside current capability
- policy-boundary limitations
- unresolved contradictions severe enough that drafting would misstate the case

### Why
A good system does not bluff its way past missing prerequisites.

Blocked should feel like clean diagnosis, not vague helplessness.

---

## Action-to-Mode Rule

The artifact should adopt the following practical rule:

### Silent bounded autonomy
For:
- internal organization
- low-risk extraction
- evidence and state maintenance
- internal drafting preparation

### Clarify-first
For:
- ambiguous intent
- ambiguous scope
- ambiguous user preference
- unresolved interpretive forks

### Approval-required
For:
- external communications
- consequential factual positioning
- escalation
- user-facing finalization of material that speaks for the user

### Blocked-with-explanation
For:
- missing prerequisites
- unsupported capability
- absent evidence
- missing access or material

This mapping should guide future design and implementation.

---

## Hidden vs Unavoidable Friction

This proving ground should also distinguish hidden friction from unavoidable friction.

### Hidden friction
Ro should absorb this silently:
- case-state maintenance
- evidence grouping
- timeline upkeep
- contradiction tracking
- missing-material detection
- low-stakes drafting prep
- model-routing choices for bounded internal work

### Unavoidable friction
Ro may surface this only when necessary:
- clarification questions
- approval requests
- blocked-condition explanations
- high-stakes contradiction alerts
- deadline warnings when user judgment is required

This is where the friction-budget principle becomes operational.

---

## Interruption Threshold Rule

Ro should interrupt only when one of these is true:

1. **judgment is required**
2. **a commitment is about to be made**
3. **the case cannot proceed honestly without user input**
4. **a contradiction materially threatens correctness**
5. **a deadline or consequence changes the user’s choice space**

If none of these is true, Ro should usually keep carrying the case quietly.

This rule should become the proving-ground default.

---

## Negative Design Rule

This artifact should explicitly reject two bad modes.

### Bad mode 1: Human-burden-first
Ro asks about everything:
- “Should I classify this?”
- “Should I update the timeline?”
- “Should I mark this file as relevant?”
- “Should I generate a checklist?”

This defeats the point.

### Bad mode 2: Quiet overreach
Ro silently:
- chooses escalation posture
- decides what the user “must mean”
- sends or finalizes consequential communication
- fills factual holes with confident inference
- treats uncertainty as resolved

This also defeats the point.

The proving-ground threshold model exists to avoid both.

---

## Example Flow In Plain Terms

A healthy proving-ground experience should feel like this:

Ro quietly:
- reads the uploaded claim packet
- extracts dates and amounts
- builds a case timeline
- notices the denial letter and missing reimbursement receipt
- drafts a checklist of missing evidence

Ro then interrupts once:
- “I can draft the appeal, but I still need to know whether this receipt is the proof of payment you want included.”

After clarification, Ro quietly:
- updates the timeline
- drafts the appeal packet
- highlights one contradiction between the denial letter and billing statement

Ro interrupts again:
- “This appeal draft is ready. Please approve before I finalize it for submission.”

That is the target feeling:
- quiet burden-carrying
- bounded interruption
- no fake omniscience
- no process babysitting

---

## What This Artifact Must Produce

This design artifact must produce:

1. a four-mode autonomy/interruption model
2. action categories mapped to those modes
3. a hidden-vs-unavoidable friction split
4. an interruption-threshold rule
5. a rejection of both human-burden-first and quiet-overreach behavior
6. a proving-ground-specific design standard for how Ro should feel in use

If it does not produce those, it is too abstract.

---

## Deliverable Shape

This artifact should end in:

1. named autonomy modes
2. a concrete action-to-mode mapping
3. an interruption threshold rule
4. a hidden/unavoidable friction split
5. a short plain-language experience target

It does not yet need to authorize implementation.

---

## Validation Standard

This artifact is acceptable only if it:

- reduces the risk of both micromanagement and overreach
- makes the human-first principle operational rather than rhetorical
- fits the chosen proving ground specifically
- gives future ranking and implementation a clearer threshold model
- makes Ro’s value easier to imagine in lived use

---

## Expected Next Step After This Artifact

If this artifact is ratified, the likely next move would be one of:

- a design artifact for case-state structure aligned to the proving ground
- a strategic re-ranking pass using the proving ground plus threshold model
- a bounded implementation phase for a minimal proving-ground intake/classification surface

But normal implementation work should still remain paused until the threshold model is accepted clearly enough to guide behavior.
