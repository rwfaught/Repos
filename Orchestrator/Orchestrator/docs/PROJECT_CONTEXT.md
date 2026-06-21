# PROJECT_CONTEXT.md

## Purpose

This document provides high-signal context about why this project exists, what constraints it operates under, and how decisions should be made during implementation.

It is not a full architecture document.  
It is a compressed orientation layer for effective execution.

---

## Why This Project Exists

Local and mid-tier AI models are capable of producing useful work, but they are unreliable when asked to:

- plan large systems
- implement multiple components at once
- review their own work accurately
- maintain consistency across long workflows
- operate without external structure

This project exists to solve that problem by introducing:

- explicit workflow control
- bounded task execution
- persistent system state
- deterministic verification
- structured iteration

---

## Core Strategy

The system is designed around the following principles:

- Break work into small, bounded tasks  
- Execute tasks sequentially  
- Assign tasks to explicit roles  
- Store all important state on disk  
- Verify outputs using deterministic checks where possible  
- Log meaningful actions for continuity  

The goal is not raw intelligence.  
The goal is **reliability through structure**.

---

## Key Constraints

### 1. Limited Codex Usage

Codex is a constrained resource.

Therefore:
- minimize the number of interactions
- maximize useful output per interaction
- avoid unnecessary back-and-forth
- prefer complete, well-scoped execution per phase

---

### 2. Context Window Limits

The model does not retain full project awareness.

Therefore:
- keep prompts small and focused
- avoid loading unnecessary documents
- rely on phase-specific context
- do not assume global awareness

---

### 3. Sequential Execution Model

The system is intentionally sequential.

Therefore:
- only one role operates at a time
- no concurrent multi-agent execution
- no parallel workflows
- all state transitions are explicit

---

### 4. Externalized Memory

The model does not remember past work reliably.

Therefore:
- all state must be written to disk
- runs, tasks, artifacts, and logs must persist
- no reliance on conversational memory

---

## Design Philosophy

AI is not the system.

AI is a tool used within the system.

The system:
- defines structure
- controls execution
- manages state
- enforces rules

AI:
- performs bounded tasks
- does not control workflow
- does not define architecture

## Scope Position

The current build is software-first in implementation emphasis.
That is an execution reality, not a permanent software-only constitutional limit.

When future phases evolve roles, task semantics, artifact concepts, or verification assumptions, avoid unnecessary software-only narrowing unless the phase explicitly requires it.
At the same time, do not overclaim current capability: today the system is strongest in software-oriented workflows.

---

## Decision Heuristics

When faced with ambiguity, prefer:

- simpler over more complex  
- explicit over implicit  
- deterministic over probabilistic  
- readable over abstract  
- minimal over generalized  

If something is not required for the current phase:
- do not implement it

---

## Operational Behavior

At all times:

- operate within the current phase only  
- do not expand scope  
- stop cleanly after completing a phase  
- produce clear summaries of work  
- maintain consistency with prior phases  

---

## What Success Looks Like

A successful system:

- can execute tasks step-by-step without confusion  
- can resume after interruption  
- stores its state externally and clearly  
- produces traceable outputs  
- remains understandable to a human  

---

## What Failure Looks Like

Failure modes include:

- uncontrolled expansion of scope  
- hidden assumptions about system state  
- reliance on model memory instead of persisted data  
- overly complex abstractions early in the build  
- breaking prior phase outputs while implementing new phases  

---

## Guiding Principle

The objective is not to build the most advanced system.

The objective is to build a system that works **reliably, predictably, and incrementally** under real constraints.

## Process Discipline

This project now requires explicit process discipline in addition to bounded implementation discipline.

That means:

- suspected issues should be confirmed before becoming fixes
- audit findings should be treated as triage input, not automatic truth
- source disagreement should be resolved by evidence precedence
- every completed phase or fix should receive a closure check for stale wording, provenance ambiguity, boundedness drift, hidden routing, hidden automation, and missing regression protection

See:
- `docs/PROCESS_PROTOCOL.md`

## Orchestrator Interaction Model

During development, Orchestrator currently exists in two coupled forms:
- conversational governance mode used in-thread
- emerging local-first framework behavior

The conversational form is being used to discover and stabilize the control semantics the framework should eventually embody.
See:
- `docs/ORCHESTRATOR_INTERACTION_MODEL.md`

## Re-entry Discipline

Restart/orientation is governed by:
- the governance stack (`BUILD_RULES`, process/method/startup docs)
- the phase ledger (`PHASE_INDEX.md`, `ACTION_LOG.md`)
- targeted fresh code evidence when current state is load-bearing

Use docs-first re-entry, then request focused fresh snapshots/files as needed.
Preserve the distinction between repo truth (authoritative) and conversational continuity (helpful but non-authoritative).

## Vision Anchor

The project now has a ratified long-range vision artifact:
- `docs/PROJECT_VISION.md`

Use it as constitutional direction for ranking and strategic coherence.
Keep it distinct from present-tense product truth:
- `docs/CURRENT_SUCCESS_CRITERION.md` remains the current capability bar
- `docs/PROJECT_VISION.md` remains the future-direction anchor

This preserves the intended split:
- current reality: software-first bounded execution with explicit control
- future direction: broader honest-contact orchestration, without overclaiming current intake capability

## Alpha 3.0 Strategic Note

Orchestrator remains the bounded-trust kernel.
Channel/app access is a future transport concern, not the kernel itself.

The system should remain personally sovereign while preserving owner-authored workflow seams for future adopters.
Current product-proof pressure remains the golden-path local casework workflow.
