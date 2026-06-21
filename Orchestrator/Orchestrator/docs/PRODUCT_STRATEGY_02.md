# PRODUCT_STRATEGY_02.md

## Product Strategy 02: Engine Identity vs First Proving Ground

---

## Goal

Turn the current product-strategy work into a sharper ranking instrument by separating:

- what **Ro is**
- where **Ro should first prove itself**

This artifact exists because the project now needs a cleaner distinction between:

- the general engine identity
- the first product-entry wedge
- the broader family of workflows the engine may eventually support

Without that distinction, the project risks one of two mistakes:

1. becoming too vague at the product layer
2. collapsing the engine into one narrow use case and underselling what it actually is

This artifact should prevent both mistakes.

---

## Why This Artifact Exists

The strategy work has already established several things:

- the harness must justify its friction
- repeated use matters more than one-time impressiveness
- internal rigor is not the user experience
- raw AI is already sufficient for many easy tasks
- the project needs an obvious win zone rather than broad generality

That is good.

But one ambiguity remains:

If the project names one strong proving-ground use case too strongly, it may accidentally redefine Ro as a single-purpose tool.

If it stays too general, it becomes an impressive engine in search of a human reason to exist.

This artifact exists to make the distinction explicit:

**Ro can be general at the engine layer and narrow at the product-entry layer.**

---

## Core Strategic Distinction

This artifact adopts the following distinction:

### Engine identity
What Ro fundamentally is.

### First proving ground
The first use-case family where Ro’s value should become obvious enough to justify the harness.

### Eventual expansion family
Other workflow categories that may later fit the same engine if the first proving ground succeeds.

This distinction should guide both language and ranking.

---

## What Ro Is

Ro should be understood as:

**a local bounded-trust orchestration engine for messy, consequential, resumable workflows where raw AI is useful but operationally unreliable.**

Key features of that identity:

- work unfolds over time
- continuity matters
- partial correctness can create downstream mess
- local state creates real value
- inspectability matters
- resumability matters
- human judgment must remain available without turning the human into a process scheduler
- models should see only bounded slices of work rather than owning the whole situation

This is the engine identity.

It is broader than any one use case.
It is narrower than “AI for everything.”

---

## What Ro Is NOT

Ro should not currently be framed as:

- a universal AI operating system
- a better general assistant for everyday low-stakes tasks
- a one-shot writing machine
- a coding agent product only
- a single-purpose dispute tool
- a broad workflow automation layer for everything

Those framings are either too broad, too narrow, or strategically weak.

---

## First Proving Ground Selection Rule

The first proving ground should not be chosen because it is flashy.

It should be chosen because it makes the engine’s advantages immediately legible to a normal person.

A good first proving ground should prove all or most of these at once:

- local state is an advantage, not a fetish
- bounded model exposure creates real peace of mind
- tracked autonomy reduces burden without surrendering control
- resumability matters because the workflow spans time
- inspectability matters because the task is consequential
- cost-aware routing is practically useful
- the system is better than “paste everything into one powerful model and hope”

If a candidate use case does not make those advantages legible, it is a weak proving ground even if it is technically compatible.

---

## Current Strongest First Proving Ground

The current strongest first proving-ground family is:

**consequential document-and-admin casework**

More concretely:
- disputes
- claims
- appeals
- reimbursement packets
- benefits or compliance paperwork
- other messy document-heavy workflows where the user must carry a case across time

This is strong not because the system is “for paperwork.”
It is strong because this kind of work naturally exposes the value of:

- local continuity
- evidence tracking
- bounded trust
- resumable progress
- human approval only when needed
- stateful recovery after interruption

This is a proving ground, not the total identity.

---

## Why This Proving Ground Is Strong

### 1. It makes the architecture matter
Raw AI can already draft a letter.
The value here is not one generated output.
The value is carrying a multi-step consequential case without losing coherence.

### 2. It makes bounded trust emotionally legible
In messy personal or business-admin cases, users immediately understand why they may not want one remote model to see the whole situation.

### 3. It naturally supports selective routing
A lot of the work is cheaper/lower-stakes:
- extraction
- classification
- chunking
- checklist generation
- timeline assembly
- first drafting passes

Only narrower higher-stakes steps need stronger models.

### 4. It has repeated-use potential
If someone uses the system once for a messy consequential case and it truly reduces burden, they are likely to want it again for the next one.

### 5. It keeps the human-first principle honest
The human remains sovereign:
- approves outgoing communications
- confirms sensitive facts
- decides on escalation
- provides missing materials

But the human is not dragged into every internal step.

---

## First Proving Ground Example Shapes

This artifact does not force one exact vertical yet, but the current strongest shapes include:

- insurance claims
- billing disputes
- reimbursement packets
- benefits appeals
- contractor/home-issue casework
- compliance or documentation disputes
- small-business admin disputes with document trails

These are not all separate products.
They are variations of the same proving-ground family.

---

## Why Ro Should Not Be Defined By That Family Alone

Even if consequential document-and-admin casework is the first proving ground, Ro should not be reduced to “the claims/disputes tool.”

That would undersell the engine.

If the engine is real, the same bounded-trust orchestration pattern should later support adjacent workflow families such as:

- resumable research pipelines
- bounded coding/repo workflows
- personal life-admin transitions
- small-business back-office casework
- other local multi-step workflows where continuity, inspectability, and recovery matter

So the product-entry wedge should be narrow.
The engine identity should remain broader.

---

## Eventual Expansion Family

If the first proving ground succeeds, likely adjacent expansion zones include:

### 1. Resumable research-and-synthesis workflows
Where sources accumulate over time and the burden is maintaining continuity, evidence, unresolved questions, and drafts.

### 2. Local coding and repo work
Where bounded changes, verification, recovery, and compartmentalized model exposure remain valuable.

### 3. Personal life-admin transitions
Such as moving, caregiving logistics, or household/contractor issue management.

### 4. Small-business back-office workflows
Where invoices, vendors, reimbursements, compliance, and issue-resolution all benefit from local state and bounded trust.

These are expansion candidates, not current primary product claims.

---

## Strategic Language Rule

The project should now use this language discipline:

### Acceptable engine-layer language
- local bounded-trust orchestration engine
- resumable workflow engine
- local governing layer for consequential workflows
- bounded AI-assisted casework engine

### Acceptable proving-ground language
- first proving ground
- first obvious win zone
- product-entry wedge
- initial use-case family

### Avoid
- universal assistant framing
- single-vertical identity collapse
- “AI OS” rhetoric
- product claims broader than the current proving-ground evidence

This matters because language can quietly distort ranking.

---

## Ranking Consequence

This artifact changes ranking behavior in a specific way.

Future work should now be judged against two linked questions:

### Engine question
Does this strengthen Ro as a local bounded-trust orchestration engine for messy, consequential, resumable workflows?

### Proving-ground question
Does this improve Ro’s ability to win in consequential document-and-admin casework as the first obvious wedge?

If a proposal helps neither, it should fall in priority.

If it helps the engine abstractly but not the proving ground, it should be treated with caution.

If it helps the proving ground but at the cost of collapsing Ro into a single-purpose tool, it should also be treated with caution.

This artifact is meant to preserve the balance.

---

## What This Artifact Must Produce

This strategy artifact must produce explicit answers to:

1. what Ro is at the engine level
2. what Ro is not
3. what the first proving-ground family is
4. why that proving ground makes the engine’s advantages legible
5. what adjacent expansion families exist if the first wedge succeeds
6. how future ranking should distinguish engine-strengthening from wedge-strengthening work

If it does not produce those answers, it is still too vague.

---

## Deliverable Shape

This artifact should end in:

1. a stable engine identity
2. a named first proving-ground family
3. a warning against collapsing the engine into the wedge
4. a shortlist of coherent expansion families
5. a ranking rule tying future work to both engine strength and wedge strength

It does not yet need to pick one final vertical forever.

---

## Validation Standard

This artifact is acceptable only if it:

- keeps Ro broad enough to remain an engine
- keeps the product-entry layer narrow enough to matter
- makes the first proving ground emotionally and practically legible
- avoids universal-assistant vagueness
- avoids single-purpose identity collapse
- materially changes future ranking behavior

---

## Expected Next Step After This Artifact

If this artifact is ratified, the likely next move would be one of:

- a third strategy artifact narrowing the first proving ground further into one initial subdomain
- a re-ranking pass using the engine-vs-proving-ground distinction
- a design artifact for autonomy/interruption thresholds specifically shaped by the proving ground

But normal implementation work should remain paused until the engine identity and proving-ground wedge are both clear enough to guide selection.
