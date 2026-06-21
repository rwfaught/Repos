# BUILD_RULES.md

## Purpose

This document defines how the coding agent (Codex) must behave while building and modifying the system.

These rules are not suggestions. They are constraints that ensure the system is built correctly, incrementally, and without uncontrolled expansion.

---

## Core Execution Rules

1. Only work on the current phase.

2. Do NOT implement future phases, even if you understand them.

3. Follow the pseudocode and instructions in the current phase document exactly.

4. Do NOT expand scope beyond what is explicitly required.

5. Keep implementations minimal, explicit, and readable.

6. Prefer simple, inspectable code over abstraction-heavy designs.

7. Persist all important state to disk. Do not rely on in-memory-only state.

8. Do not assume hidden context. Only use what is provided in the current prompt and referenced documents.

---

## Phase Control Rules

1. Each phase is a strict execution boundary.

2. At the end of a phase:
   - STOP immediately
   - Do not begin the next phase
   - Do not suggest or implement future work unless explicitly asked

3. A phase is considered complete only when its success criteria are met.

---

## File and Structure Rules

1. All project files must follow the root-level structure:

   - main.py  
   - orchestrator/  
   - providers/  
   - verifiers/  
   - agents/  
   - docs/  
   - data/

2. Do NOT introduce a `src/` directory.

3. Do NOT create alternative or duplicate directory structures.

4. When modifying existing files:
   - preserve compatibility with previous phases
   - do not break imports or file paths

---

## Conflict Resolution Rules

If you encounter conflicting instructions between files:

1. Phase document overrides all other documents.

2. If two phase instructions conflict:
   - prefer the current phase
   - do NOT attempt to reconcile future phases

3. If existing files conflict with the current phase:
   - adjust the files to match the current phase requirements
   - do NOT preserve incorrect prior structure

4. If uncertain:
   - choose the simplest implementation that satisfies the current phase
   - do NOT expand scope to resolve ambiguity

---

## Modification Rules

1. Only modify files listed in the current phase unless modification is strictly necessary.

2. If modifying an existing file:
   - make the smallest possible change
   - preserve existing behavior unless explicitly required to change it

3. Do NOT refactor unrelated code.

4. Do NOT optimize prematurely.

---

## Implementation Style Rules

1. Code must be:
   - explicit
   - readable
   - minimally abstracted

2. Avoid:
   - unnecessary classes
   - deep inheritance
   - complex configuration systems
   - premature generalization

3. Prefer:
   - simple functions
   - clear data structures
   - direct logic flow

---

## CLI Behavior Rules

1. CLI commands must be:
   - explicit
   - minimal
   - predictable

2. Do NOT introduce complex CLI frameworks.

3. Keep command parsing simple and readable.

---

## Verification of Work

Before completing a phase, ensure:

- code runs without crashing
- file paths are correct
- imports resolve
- required files exist
- success criteria in the phase document are satisfied

---

## Completion Rules

At the end of each phase:

1. STOP execution.

2. Provide a summary including:
   - what was implemented
   - which files were created or modified
   - any assumptions made
   - any uncertainties

3. Append a concise entry to:
   - docs/ACTION_LOG.md

---

## Prohibited Behavior

Do NOT:

- implement features from future phases
- redesign system architecture mid-phase
- introduce hidden state or implicit behavior
- assume missing components exist
- replace deterministic logic with model-based logic
- create parallel systems that duplicate functionality

---

## Guiding Principle

Your role is not to build everything at once.

Your role is to build the system correctly, one phase at a time, without deviation.

## Process Protocol Rules

Codex must also follow `docs/PROCESS_PROTOCOL.md` as governing process behavior.

Additional required rules:

1. Do not open or implement a fix from an audit claim alone.
   First confirm whether the issue is:
   - confirmed in the latest inspected snapshot
   - confirmed in the latest Codex implementation report
   - not confirmed
   - future hardening
   - watchlist

2. Before drafting work, classify the intervention explicitly as one of:
   - feature phase
   - hardening phase
   - code fix
   - docs/control-surface fix
   - validation-only correction

3. Treat auditor findings as triage input, not as automatic defect truth.

4. After every completed phase or fix, perform a closure check for:
   - stale operator-facing wording
   - stale docs/control surfaces
   - provenance ambiguity
   - weakened boundedness
   - hidden routing behavior
   - hidden automation creep
   - missing regression coverage
   - newly implied sibling obligations

5. When evidence sources disagree, prefer:
   1. latest inspected snapshot
   2. latest Codex implementation report
   3. latest auditor report
   4. conversational memory
