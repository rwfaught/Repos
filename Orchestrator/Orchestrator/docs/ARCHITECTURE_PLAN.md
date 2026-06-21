# ARCHITECTURE_PLAN.md

## Purpose

This document defines the technical architecture of the orchestration system.

It describes:
- system structure
- data flow
- component responsibilities
- execution model

It is the authoritative technical reference for how the system is designed to function.

This document does NOT define execution scope.  
Phase documents define what is built at any given time.

---

## System Model

The system is a **sequential orchestration engine**.

It coordinates:

- tasks
- roles
- execution providers
- verification steps
- persistent state

The system does not rely on model memory.  
All important state is stored on disk.

---

## Core Components

### 1. Orchestrator

The orchestrator is the control spine.

Responsibilities:
- manage runs
- select next task
- enforce dependencies
- dispatch tasks
- track state transitions
- store artifacts
- coordinate verification
- apply routing decisions

The orchestrator is **code-driven**, not model-driven.

---

### 2. Task System

Tasks are the unit of execution.

Each task defines:
- objective
- role
- dependencies
- constraints
- success criteria
- files in scope
- retry state

Tasks are persisted as JSON.

---

### 3. Role Layer

Roles define *how* work is executed.

Core roles:
- planner
- coder
- reviewer

Each role:
- has a dedicated module
- has a dedicated prompt file
- operates only within task scope

Roles do NOT control system flow.

---

### 4. Provider Layer

Providers abstract execution backends.

Each provider:
- receives role + task + context
- executes work
- returns structured output

Providers include:
- mock provider (local testing)
- ollama provider (future local models)
- codex provider (external model)

Providers do NOT control workflow.

---

### 5. Verifier Layer

Verifiers perform deterministic checks.

Examples:
- file exists
- directory exists
- Python syntax valid

Verifiers return structured results:
- pass/fail
- messages
- evidence

Verifiers have higher authority than model opinions.

---

### 6. Artifact System

Artifacts represent outputs of task execution.

Each artifact includes:
- artifact_id
- task_id
- role
- timestamp
- output data or reference
- status

Artifacts are persisted to disk.

---

### 7. Persistence Layer

The system stores:

- workspace state
- run data
- task files
- artifact metadata
- verifier results
- logs

All persistence uses JSON.

---

### 8. CLI Interface

The CLI provides human control.

Core commands:
- init
- new-run
- next
- status
- verify

The CLI is intentionally minimal and explicit.

---

## Execution Flow

A typical execution cycle:

1. Load workspace state
2. Identify active run
3. Select next runnable task
4. Mark task as in_progress
5. Dispatch task via provider
6. Receive result
7. Create artifact
8. Mark task as completed
9. Persist all changes
10. Stop

Later phases will insert:
- verification between steps
- routing decisions after verification

---

## Task Lifecycle

Tasks move through states:

- queued
- ready
- in_progress
- completed
- failed (future)
- under_review (future)

State transitions must be explicit and persisted.

---

## Data Flow

Input:
- user request
- stored tasks

Flow:
task → role → provider → result → artifact → verifier → state update

Output:
- updated state
- artifact records
- logs

---

## System Constraints

- sequential execution only
- no hidden state
- no reliance on model memory
- no concurrent task execution
- no implicit routing decisions

## Scope Discipline

This architecture is currently implemented with software-oriented workflows as the primary target.
That implementation emphasis should remain explicit.

However, the architectural model (bounded tasks, explicit roles, persisted state, deterministic verification where possible) is intended to remain applicable to broader bounded workflows when practical.
Future phases should avoid unnecessary software-only narrowing in role semantics, artifact concepts, task semantics, and verification assumptions unless a phase explicitly requires software-specific behavior.

This is not a claim that the current system is already fully domain-general in practical capability.

---

## Design Rules

The system must:

- be inspectable
- be resumable
- be deterministic where possible
- be minimal in early phases
- avoid premature abstraction

---

## Extension Points

Future capabilities may include:

- richer verification (tests, linting)
- smarter routing logic
- real model integration
- UI/dashboard layer
- multi-run management

These must be added without breaking existing structure.

---

## Relationship to Phase Documents

This document defines the full system.

Phase documents define:
- what portion of this system is built now

If a conflict exists:
- follow the phase document for implementation
- preserve this document as architectural truth

---

## Guiding Principle

The system is not built to be clever.

It is built to be:
- controlled
- predictable
- extensible

The architecture must support that at every level.
