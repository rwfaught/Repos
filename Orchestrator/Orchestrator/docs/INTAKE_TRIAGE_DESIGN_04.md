# INTAKE_TRIAGE_DESIGN_04.md

## Intake/Triage Design 04: Handoff-to-Decomposition Boundary

---

## Goal

Define the minimum rules governing how a ratified intake judgment may hand off into bounded internal decomposition.

This artifact should specify:

- what a `proceed` outcome is allowed to authorize
- what it is not allowed to smuggle in
- how `clarify` and `blocked` are prevented from creating hidden internal work
- how the system preserves bounded decomposition instead of silently drifting into planner behavior

This is a **design artifact**.

It is not:
- an implementation phase
- a planner expansion phase
- a task-schema redesign
- an API design
- a transport specification
- a full decomposition ontology

Its job is narrower:

to define the first honest handoff boundary between intake judgment and bounded internal work.

---

## Why This Artifact Exists

The intake design stack now has three ratified layers:

1. constitutional intake meanings
2. machine-readable intake outcome shapes
3. input shape and evidence-source rules

That stack defines:
- what the intake layer may decide
- how it must represent that decision
- what evidence it may rely on

But one major architectural danger still remains:

**what happens immediately after `proceed`?**

If that handoff is left fuzzy, the system can still rot in a new way:

- intake becomes de facto planning
- `proceed` becomes a license for unbounded decomposition
- hidden internal tasks are created before the boundary is explicit
- `clarify` and `blocked` leak into speculative background work
- the system starts looking disciplined at intake while drifting behind the scenes

This artifact exists to prevent that.

---

## Core Design Question

Once intake returns `proceed`, what exactly is handed off into the execution side of the system, and what constraints must govern that handoff so decomposition remains bounded, inspectable, and non-speculative?

This artifact answers that question.

---

## Required Design Outcome

Define:

1. what a `proceed` outcome may authorize
2. what a `proceed` outcome must not authorize
3. what the minimum handoff object should contain
4. what is prohibited for `clarify` and `blocked`
5. what decomposition must still determine for itself after intake
6. what protections are required against planner drift

The result must remain:

- explicit
- bounded
- machine-meaningful
- architecturally compatible with the current execution core
- faithful to the project’s governing principle of honest contact

---

## What This Artifact Is NOT About

This artifact is NOT about:

- implementing a planner
- generating full task trees
- defining the final task schema in full
- deciding role counts or role sequencing
- deciding UI behavior
- defining API transport
- defining long-term autonomous execution
- building multi-turn orchestration policy
- defining ranking between multiple decomposition plans
- creating a large decomposition ontology

This artifact defines the handoff boundary only.

---

## Governing Handoff Rule

The handoff from intake to decomposition must follow this rule:

**Intake may authorize decomposition. It may not silently perform decomposition.**

That means:

- intake can decide that bounded decomposition is now permitted
- intake can pass forward the bounded objective and confirmed context needed for decomposition
- intake cannot itself smuggle in a hidden task tree, hidden plan, or hidden workflow commitments unless those are explicitly part of the next bounded layer

This is the central protection in the artifact.

Without it, `proceed` becomes planner behavior wearing intake clothing.

---

## Proceed Authorization Semantics

A `proceed` outcome should authorize exactly this:

- the system may begin bounded internal decomposition
- decomposition may rely on the confirmed evidence bundle used by intake
- decomposition may create internal work only within the bounded rules of the decomposition layer
- downstream execution may begin only after decomposition has produced bounded internal work in an inspectable form

A `proceed` outcome should NOT by itself imply:

- that a full task tree already exists
- that the workflow shape is already fixed beyond what intake actually judged
- that the system may skip bounded decomposition and jump directly to execution
- that ambiguous downstream choices have already been resolved if intake did not resolve them

`proceed` is authorization to begin bounded decomposition.
It is not hidden decomposition in completed form.

---

## Non-Proceed Prohibition Rule

This artifact must explicitly protect the opposite side too:

**No intake outcome other than `proceed` may create internal tasks, internal plans, or hidden workflow commitments.**

That means:

- `clarify` may not queue speculative tasks
- `clarify` may not create draft decomposition artifacts disguised as “helpful preparation”
- `blocked` may not create internal tasks
- `blocked` may not create fallback workflows as if the block were already resolved

This matters because hidden progress is still dishonest even when framed as helpfulness.

---

## Minimum Handoff Object

Once intake returns `proceed`, the handoff into decomposition should be represented by a small explicit object.

A minimum acceptable conceptual shape is:

```json
{
  "authorized_objective": "...",
  "confirmed_evidence_bundle": {},
  "decomposition_authorized": true,
  "handoff_constraints": []
}
```

This artifact does not require those exact names in implementation, but it does require these conceptual parts.

### Required handoff components

#### 1. Authorized objective

A bounded representation of what decomposition is now allowed to work on.

This should be derived from:
- the original objective text
- any clarification that has already been resolved
- confirmed context only

It must not silently include unconfirmed assumptions.

#### 2. Confirmed evidence bundle

The subset of evidence that decomposition is explicitly allowed to rely on.

This should come only from:
- explicit request evidence
- confirmed environment/context evidence

It must not include inferred but unconfirmed assumptions.

#### 3. Decomposition authorization flag

A machine-readable field making clear that decomposition is now allowed.

This is important because decomposition permission should remain explicit all the way down, not assumed from prose.

#### 4. Handoff constraints

A small structured list of any bounded constraints intake has already established that decomposition must preserve.

Examples in spirit:
- required source form is CSV
- output must be summary, not code patch
- no connector available beyond supplied files
- current scope limited to provided repo snapshot

This field should remain small and explicit.
It is not a place to hide a giant planning object.

---

## What Intake May Hand Off

Intake may hand off:

- the authorized objective
- resolved clarification answers
- confirmed current evidence
- explicit known constraints
- decomposition permission state

Intake may also hand off:
- why the objective is now considered bounded enough
but only as explanation, not as hidden decomposition content

---

## What Intake Must NOT Hand Off

Intake must not hand off:

- a hidden multi-step plan presented as if decomposition has not yet happened
- implicit role assignments unless those are part of the next bounded layer’s own rules
- speculative missing facts
- guessed capabilities
- stale context treated as current
- pre-created internal tasks for non-`proceed` outcomes
- workflow commitments that exceed what intake actually judged

This is the anti-drift section.
It exists because systems often smuggle planning across boundaries under innocent names like “prepared context.”

---

## Decomposition’s Remaining Responsibility

This artifact must preserve that decomposition still has real work to do after intake.

Once handoff occurs, decomposition is still responsible for:

- deciding the bounded internal work shape
- deciding how many task cards are actually needed
- deciding dependencies
- deciding task-level success criteria
- deciding role assignment within the bounded orchestration model

Those are not intake responsibilities.

Intake decides whether decomposition may honestly begin.
Decomposition decides how bounded internal work is actually formed.

That distinction must remain sharp.

---

## Allowed vs Forbidden Handoff Examples

### Allowed

- “Proceed. The objective is to summarize the supplied CSV export into a bounded findings memo. Confirmed evidence: CSV file provided, output audience specified, no external connectors required.”
- “Proceed. The objective is to inspect the supplied repo snapshot for current verifier behavior. Confirmed evidence: fresh repo snapshot attached.”

These authorize bounded decomposition while staying close to confirmed evidence.

### Forbidden

- “Proceed. Here is a likely five-step task tree and a fallback alternate path if the connector is missing.”
- “Clarify, but meanwhile generate the likely initial task cards.”
- “Blocked, but queue a prep task in case the user later provides access.”
- “Proceed based on the last known snapshot because it is probably still current.”

These all cross the boundary dishonestly.

---

## Relationship To Current Architecture

This artifact must fit the current architectural staircase.

Current execution core already expects:

- explicit bounded tasks
- explicit state transitions
- explicit verification
- explicit review/recommendation surfaces

That means the handoff boundary should terminate before internal tasks exist, unless and until the next bounded layer explicitly creates them.

This artifact therefore protects against:

- intake becoming a shadow planner
- decomposition becoming invisible
- execution being authorized from prose instead of bounded structures
- non-`proceed` outcomes leaking into background orchestration

The current core remains below the handoff boundary.

---

## Protected Non-Goals

This design rejects the following premature moves:

- treating `proceed` as equivalent to “task tree already generated”
- allowing `clarify` to create speculative internal drafts
- allowing `blocked` to spawn hidden remediation tasks
- letting handoff objects become disguised planner payloads
- letting confirmed evidence bundles absorb unconfirmed inference
- skipping decomposition because intake sounds confident enough

The point is to keep authorization, evidence, and decomposition separate.

---

## Required Behavioral Consequences

This artifact should establish these consequences:

### If intake outcome = `proceed`
- decomposition may begin
- only the authorized objective and confirmed evidence bundle may be used
- bounded internal work still must be created explicitly

### If intake outcome = `clarify`
- only clarification behavior is allowed
- no internal task creation
- no hidden decomposition artifacts

### If intake outcome = `blocked`
- only blocked explanation/surfacing behavior is allowed
- no internal task creation
- no hidden workaround planning

These consequences matter because the handoff boundary must govern behavior, not merely describe it.

---

## Deliverable Shape

This artifact should establish:

1. the governing handoff rule
2. the non-`proceed` prohibition rule
3. the minimum handoff object
4. the distinction between what intake may and may not hand off
5. decomposition’s remaining responsibilities
6. behavioral consequences for each intake outcome at the handoff boundary

No implementation plan is required yet.

No intake implementation phase should begin until this handoff boundary is judged coherent.

---

## Validation Standard

This artifact is acceptable only if it:

- prevents intake from collapsing into hidden planning
- keeps `proceed` as authorization rather than completed decomposition
- prevents `clarify` and `blocked` from generating hidden internal work
- keeps confirmed evidence separate from speculative plan content
- remains compatible with the project’s current explicit-task architecture
- does not drift into planner or API implementation detail

---

## Expected Next Step After This Artifact

If this artifact is ratified, the project will likely have enough intake design structure to justify one of two next moves:

- a bounded implementation phase for a minimal service-level intake judgment function
- or a very small follow-on design artifact only if one last unresolved implementation-critical ambiguity remains

At that point the intake design stack would cover:
- meaning
- outcome shape
- evidence boundary
- handoff boundary

That is likely sufficient to begin very small implementation safely.
