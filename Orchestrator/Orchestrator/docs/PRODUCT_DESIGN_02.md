# PRODUCT_DESIGN_02.md

## Product Design 02: Case-State Structure for the First Proving Ground

---

## Goal

Define the minimum case-state structure for Ro’s initial proving ground:

**claims / disputes / appeals-style casework for consequential personal or small-business paperwork problems.**

This artifact should specify what a live case structurally is, what kinds of state must persist locally, and what distinctions Ro must preserve so the case remains resumable, inspectable, and honest across time.

This is a **design artifact**.

It is not:
- a feature phase
- a code implementation packet
- a complete schema spec for every future product domain
- a transport design
- a UI mockup

Its purpose is narrower:

to define the first bounded case-state model that future design and implementation work can build against in the initial proving ground.

---

## Why This Artifact Exists

The proving-ground strategy is now sharp enough to guide product design:

- Ro is the engine
- claims / disputes / appeals-style casework is the first proving ground
- autonomy / interruption thresholds have been defined
- the harness must justify its friction
- internal rigor must remain distinct from external experience

That still leaves one foundational design question open:

**What is the case that Ro is actually carrying?**

Without a clear case-state model, several failures become likely:

- the system stores too little and cannot resume coherently
- the system stores too much in a shapeless blob and loses legibility
- drafts, evidence, contradictions, missing materials, and approval points blur together
- Ro cannot distinguish “what is known” from “what is claimed” or “what is missing”
- later implementation drifts because there is no stable case structure to preserve

This artifact exists to prevent that drift.

---

## Core Design Question

For claims / disputes / appeals-style casework, what minimum local state must exist so that Ro can:

- resume a case after interruption
- explain what has happened
- show what is missing
- preserve what is confirmed versus uncertain
- prepare drafts without pretending they are final
- support approval and clarification thresholds cleanly

This artifact answers that question.

---

## Required Design Outcome

This artifact must define the minimum case-state categories required for the first proving ground.

At minimum, a live case should preserve bounded state for:

1. case identity
2. source materials
3. extracted facts
4. timeline/events
5. open issues / claims under dispute
6. missing evidence / missing materials
7. contradictions / unresolved conflicts
8. drafts / prepared outputs
9. decisions / approvals / user-owned judgments
10. current case status / next step

If the artifact does not explicitly define those categories or their equivalents, it is too vague.

---

## This Artifact Is NOT About

This artifact is NOT about:

- a database implementation
- final JSON schema details
- all future product verticals
- general knowledge graphs
- long-term personal memory for everything
- broad connector design
- UI layout
- final naming for every field

This artifact defines the minimum conceptual case-state structure only.

---

## Governing Case-State Principle

The case state should follow this rule:

**Ro must preserve the structure of the case, not just accumulate artifacts.**

That means the system should not merely store:
- files
- emails
- notes
- drafts

It must preserve the functional distinctions among them.

A live case is not a pile.
It is an organized process state.

That distinction is the whole point.

---

## Minimum Case-State Categories

### 1. Case Identity

This is the bounded identity of the case as a case.

It should minimally answer:
- what kind of case this is
- what the user is trying to achieve
- who or what the counterparties are
- what the current case label or title is

Examples in spirit:
- “Billing dispute with Vendor X”
- “Insurance reimbursement appeal for visit on March 4”
- “Contractor damage claim for kitchen repair”

This matters because Ro should be carrying a named case, not a vague cloud of related materials.

---

### 2. Source Materials

This is the inventory of provided or linked case materials.

Examples:
- PDFs
- receipts
- invoices
- denial letters
- policy excerpts
- claim forms
- screenshots
- email threads
- notes the user adds directly

Important distinction:
Source materials are not yet the same thing as confirmed facts.

They are the evidence pool.

Ro must preserve provenance:
- what material exists
- where it came from
- whether it has been reviewed or extracted from
- whether it is still pending interpretation

---

### 3. Extracted Facts

This is the set of facts Ro believes are extractable from the source materials.

Examples:
- dates
- amounts
- invoice numbers
- policy numbers
- names
- addresses
- deadlines
- identifiers
- claimed amounts
- stated denial reasons

This state must preserve an important distinction:

- extracted fact
- confidence / support basis
- source linkage

Ro should not flatten “a date found in a PDF” into the same category as “a user-confirmed decisive fact” without trace.

The system should remain able to say:
- what it believes
- why it believes it
- where that came from

---

### 4. Timeline / Events

This is the ordered sequence of what has happened in the case.

Examples:
- invoice issued
- payment made
- denial letter received
- appeal deadline stated
- follow-up email sent
- contradictory statement introduced
- supporting receipt uploaded
- draft letter prepared
- user approved final appeal text

This is not just a list of facts.
It is a temporal structure.

The timeline matters because these workflows unfold over time, and resumability depends heavily on being able to reconstruct sequence without rebuilding it manually.

---

### 5. Open Issues / Claims Under Dispute

This is the set of live contested or unresolved questions in the case.

Examples:
- “Was this charge valid?”
- “Was the payment received?”
- “Does the denial reason match the policy text?”
- “Is the late fee contestable?”
- “Is the revised invoice part of the same dispute?”

This category matters because not every case is about one single question.

Ro should be able to carry:
- the primary issue
- sub-issues
- whether each one is open, narrowed, or resolved

This is one of the main structures that keeps the case coherent.

---

### 6. Missing Evidence / Missing Materials

This is the inventory of what the case still lacks.

Examples:
- missing receipt
- missing payment confirmation
- missing revised invoice
- missing date of service
- missing denial letter page
- missing approval from the user for sending a draft

Important distinction:
Missing materials are not the same as contradictions.
They are absent prerequisites.

Ro should preserve them explicitly so that the case can advance without pretending the evidence pool is already complete.

---

### 7. Contradictions / Unresolved Conflicts

This is the set of places where the current materials or extracted facts conflict materially.

Examples:
- invoice total in email differs from PDF
- denial reason conflicts with submitted claim form
- two dates for the same event appear in different sources
- user note conflicts with document evidence
- timeline sequence is inconsistent across sources

Contradictions should not be hidden inside generic uncertainty.

They are special because they often determine whether Ro should:
- continue quietly
- clarify
- block
- or request approval on a cautious draft

This category must remain visible.

---

### 8. Drafts / Prepared Outputs

This is the set of work Ro has prepared but which is not yet equivalent to committed external action.

Examples:
- draft dispute letter
- appeal outline
- evidence summary
- reimbursement packet checklist
- counterparty response draft
- case summary memo
- timeline summary for user review

This category must preserve distinctions such as:
- internal draft
- ready for user review
- approved for external use
- superseded / obsolete

Without this, Ro will blur “prepared” with “sent” or “suggested” with “adopted.”

That would be dangerous.

---

### 9. Decisions / Approvals / User-Owned Judgments

This is the part of the case state where the user’s actual choices live.

Examples:
- approved sending the appeal
- chose neutral rather than aggressive tone
- confirmed that receipt is proof of payment
- decided not to escalate further
- chose to treat revised invoice as separate issue
- accepted or rejected a drafted summary

This matters because Ro must not quietly absorb user judgment into its own internal summary.

The case should preserve what the user actually decided.

That is both operationally important and trust-preserving.

---

### 10. Current Case Status / Next Step

This is the concise present-tense state of the case.

It should answer:
- where the case currently stands
- what Ro is waiting on, if anything
- what the next bounded move is
- whether the case is active, waiting, blocked, pending user approval, or materially complete for now

This is the category most directly tied to user relief.

A good case system should let the user quickly grasp:
- what is going on
- what has already happened
- what matters next

without rereading the whole case.

---

## Required Distinctions

This artifact must preserve several distinctions that cannot be collapsed.

### Distinction 1: Source material vs extracted fact
A PDF is not the same thing as the fact inferred from it.

### Distinction 2: Extracted fact vs user-confirmed fact
Something Ro pulled from a document is not automatically the same as something the user has confirmed as decisive.

### Distinction 3: Draft vs approved communication
Prepared text is not the same as user-authorized outward communication.

### Distinction 4: Missing evidence vs contradiction
Absence and conflict are different problems and should be tracked differently.

### Distinction 5: Open issue vs resolved issue
Ro must preserve what remains genuinely under dispute.

### Distinction 6: Internal next step vs user-owned decision
Ro may carry process, but it must not silently absorb judgment.

If these distinctions are blurred, the case-state model will not protect the proving ground properly.

---

## Relationship To The Threshold Model

The case-state model should support the autonomy/interruption model already defined.

That means:

- missing materials should support `blocked-with-explanation`
- contradictions should support either `clarify-first`, `approval-required`, or `blocked`, depending on severity
- drafts should support `approval-required`
- extracted facts and source materials should support `silent bounded autonomy`
- user-owned decisions should remain explicit and separate from Ro’s process state

The threshold model and case-state model must fit each other.

---

## Hidden vs Visible Structure

This artifact should also preserve the distinction between internal structure and user-visible simplification.

Internally, the case may need all ten categories.

Externally, the user should usually experience something much simpler, more like:

- what happened
- what matters
- what is missing
- what needs my decision
- what happens next

This means the case model can be rigorous without forcing governance-shaped clutter onto the user.

---

## Negative Design Rule

This artifact should explicitly reject two bad case-state models.

### Bad model 1: Everything is a blob
All files, notes, drafts, facts, and decisions live in one undifferentiated heap.
This destroys resumability and trust.

### Bad model 2: Premature enterprise schema sprawl
The system introduces a giant ontology with too many categories before the proving ground is even validated.
This creates internal ceremony without product proof.

The right model is:
- enough structure to preserve the case truthfully
- no more structure than the proving ground actually needs

---

## Example Case In Plain Terms

A healthy case-state experience should feel like this internally:

- case: “Billing dispute with provider”
- source materials: invoice PDF, payment receipt, denial email, notes from phone call
- extracted facts: invoice amount, payment date, denial date, case reference number
- timeline: invoice issued -> payment made -> denial email received -> draft response prepared
- open issues: whether payment was credited, whether late fee is valid
- missing materials: missing revised statement from provider
- contradictions: email says one amount, invoice says another
- drafts: response letter ready for review
- decisions: user chose neutral tone and approved inclusion of receipt
- current status: waiting for provider’s revised statement before final dispute submission

That is the level of order this artifact is meant to enable.

---

## What This Artifact Must Produce

This design artifact must produce:

1. a minimum case-state model for the proving ground
2. clearly named state categories
3. required distinctions between evidence, facts, drafts, contradictions, missing materials, and decisions
4. alignment with the existing threshold model
5. a rule for keeping internal rigor distinct from external simplicity

If it does not produce those, it is too vague.

---

## Deliverable Shape

This artifact should end in:

1. a named set of minimum case-state categories
2. a short list of non-collapsible distinctions
3. a threshold-model alignment section
4. a negative design rule
5. a plain-language example of a healthy case-state experience

It does not yet need to authorize implementation.

---

## Validation Standard

This artifact is acceptable only if it:

- makes the proving-ground workflow more structurally legible
- preserves resumability and inspectability
- avoids both shapeless blob storage and premature schema sprawl
- keeps user judgment distinct from process handling
- gives future implementation work a clear case-state backbone

---

## Expected Next Step After This Artifact

If this artifact is ratified, the likely next move would be one of:

- a strategic re-ranking pass using the proving ground plus case-state model
- a bounded implementation phase for a minimal proving-ground case intake/classification surface
- a design artifact for case progression / lifecycle states

But normal implementation work should still remain paused until the case-state model is accepted clearly enough to guide structure.
