# PROJECT_VISION.md

## Purpose

This document defines the project’s constitutional direction.

It is not:
- a phase document
- a fix document
- a roadmap
- a present-tense success bar
- a detailed intake/triage specification

Its job is narrower:

to state what this project is ultimately trying to become, in a way that can guide ranking decisions without overstating current capability.

---

## Why This Document Exists

The project now has:
- a functioning bounded execution core
- explicit governance discipline
- a present-tense success criterion
- a growing need to distinguish current capability from intended direction

Without a separate vision artifact, those concerns tend to blur.

That blur creates two equal and opposite risks:

1. overstating what the current system can already do
2. under-defining what the system is being built toward

This document exists to prevent both mistakes.

---

## Present Capability vs Intended Direction

### Present capability

Today, the system is strongest as a local-first orchestration core for bounded AI-assisted work.

Its current strengths include:
- bounded task execution
- persistent task and artifact state
- deterministic verification where possible
- structured review and recommendation handling
- explicit operator-visible control surfaces
- inspectable outcome classification

At the current stage, the system is oriented around well-formed, operator-bounded tasks.

It does **not** yet fully provide a general user-facing intake layer that can reliably interpret vague human objectives and convert them into bounded internal work.

That distinction must remain explicit.

### Intended direction

Over time, the system should extend the same discipline it already applies to execution toward the intake boundary itself.

That means the project should move toward a system that can:
- receive human objectives
- determine whether they are actionable, underdetermined, or unsupported
- convert actionable objectives into bounded supervised work
- explain clearly when it cannot honestly proceed

This is the intended direction.

It is not a claim about the system’s full present capability.

---

## Governing Principle

The governing principle of the project is:

**keep the human in honest contact with what is actually happening.**

That applies across all layers of the system.

At the execution layer, it means:
- no hidden control
- no silent mutation
- no synthetic progress
- no weak result silently treated as success
- no ambiguity about what ran, what was produced, what failed, or why

At the future intake layer, it should mean:
- no pretending ambiguous requests are well understood
- no false confidence about capability or permissions
- no disguised inability
- no vague “blocked” behavior without actionable explanation

This principle matters more than apparent capability.

A system that appears more powerful while making reality less legible is moving in the wrong direction.

---

## What The Project Is

This project is building a **trustworthy governing layer for AI-assisted work**.

Its purpose is not to make AI appear autonomous.

Its purpose is to preserve:
- boundedness
- inspectability
- explicit state
- reviewability
- diagnosable failure
- operator judgment

The project should be understood as a governing layer, not as agent theater.

As new interfaces are added, the system must remain one governing layer.

The CLI, any future API, and any future GUI or automation surface must expose the same underlying orchestration semantics rather than create alternate control systems with different meanings, shortcuts, or mutation paths.

---

## North Star

The north star is this:

**Keep the human in honest contact with AI-assisted work.**

That means turning objectives into supervised, inspectable workflows — and when that is not possible, saying exactly why, in terms the human can act on.

---

## What This Vision Rejects

This vision rejects the following directions:

- “autonomous AI employee” positioning
- hidden control flow presented as intelligence
- broad capability claims not supported by current architecture
- synthetic progress where the system appears active but the operator loses the thread
- ambiguity about whether the system understood the request, lacked permissions, lacked data, or simply failed
- growth in apparent power at the cost of legibility

The project should not optimize for appearances that weaken honest contact.

---

## Architectural Implication

The future path should not be “make the system more agentic” in the vague sense.

The more precise future path is:

1. preserve the current disciplined execution core
2. extend that discipline outward toward intent intake
3. add honest proceed / clarify / blocked judgment at the intake boundary
4. maintain explicit explanation when the system cannot act
5. keep future capability growth subordinate to legibility

This project should become broader only by carrying its current discipline outward, not by abandoning it.

---

## Relationship To Other Documents

This document does not override:

- `CURRENT_SUCCESS_CRITERION.md`
- `BUILD_RULES.md`
- `PHASE_INDEX.md`
- phase documents
- fix documents

Instead, it complements them.

Relationship summary:

- `PROJECT_VISION.md` defines long-range constitutional direction
- `CURRENT_SUCCESS_CRITERION.md` defines the present-tense product bar
- `ORCHESTRATOR_METHOD.md` defines governance and ranking method
- phase and fix documents define bounded execution packets

These layers should remain distinct.

---

## Ranking Guidance

When ranking future work, ask:

1. Does the proposed move improve honest contact between the human and what is actually happening?
2. Does it strengthen boundedness, inspectability, diagnosability, or truthful explanation?
3. Does it extend current discipline outward, or merely increase apparent capability?
4. Does it preserve the distinction between current capability and intended direction?

If a proposal increases apparent power while weakening honest contact, it is the wrong move.

If a proposal makes the system more truthful, more legible, more bounded, or more actionable under real constraints, it is moving in the right direction.

---

## Final Interpretation

This project is not trying to become a black-box intelligence that “just handles things.”

It is trying to become a system that can be trusted to handle bounded work honestly.

Today, that honesty is expressed through disciplined execution.

Over time, it should also be expressed through disciplined intake.

That continuity matters.

The system should not become a different thing as it grows.
It should become the same thing, applied across a wider boundary.
