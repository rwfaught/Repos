# Orchestrator — Local-First Orchestration Framework

## Overview

Orchestrator is a phase-governed, local-first orchestration framework for bounded AI-assisted work.

The project is designed around a simple principle: useful AI systems should not rely on conversational memory or hidden agent behavior. They should operate through explicit tasks, persisted state, bounded execution, deterministic checks where possible, and controlled human approval at important decision points.

The current implementation is **software-first**, but not **software-only**. It is strongest today in software-oriented and code-mediated workflows, while intentionally preserving room to support broader bounded workflows over time.

## Core Characteristics

- **Local-first orchestration**
  - Important state is stored on disk.
  - The system is designed to work with local and explicit execution backends.

- **Phase-governed development**
  - Features are added one bounded phase at a time.
  - Corrections to completed work are handled through fix documents instead of rewriting history casually.

- **Explicit task lifecycle**
  - Tasks are persisted as structured JSON.
  - Execution, verification, adequacy review, recommendation generation, response handling, and follow-up task creation are all inspectable.

- **Human-governed control**
  - Operator-triggered actions are explicit.
  - Automation is intentionally limited.
  - The system prefers visibility before consequence.

## What the System Can Do Today

At its current state, the framework can:

### Core orchestration
- initialize and manage a workspace
- persist runs, tasks, artifacts, verifier results, and reviewer recommendations
- select runnable tasks deterministically
- execute tasks through provider backends
- create artifacts from execution
- run verification and classify results

### Providers
- use a mock provider for bounded local testing
- use an Ollama provider for real local model execution
- reject unknown providers explicitly and predictably

### Review and recommendation flow
- detect inadequate but otherwise successful output
- route such results into reviewer tasks
- validate reviewer output as bounded recommendation records
- persist reviewer recommendations
- inspect, summarize, and surface recommendation state

### Recommendation-to-task ladder
- surface recommendation-created task classes
- confirm recommendation-created tasks explicitly
- surface confirmed tasks as ready
- surface ready tasks as execution candidates
- explicitly execute a selected ready candidate
- surface post-execution recommendation-derived results
- surface bounded operator response options for those results
- explicitly create:
  - follow-up review tasks from eligible `needs_review` results
  - repair tasks from eligible `verification_failed` / `execution_failed` results

### Governance and hardening
- preserve bounded one-step ordinary progression
- normalize recommendation provenance into explicit task fields
- maintain regression coverage for the recommendation lifecycle
- enforce process discipline through documented protocol rules

## What the System Does **Not** Do

The framework is intentionally restrained. It does **not** currently:

- behave like a fully autonomous agent
- automatically create tasks from surfaced options
- automatically repair, retry, or re-execute work
- automatically re-route post-execution results
- broadly optimize queue policy on its own
- provide domain-general real-world automation out of the box

This is deliberate. The current architecture is built to be explicit, inspectable, and governable before becoming more powerful.

## Recommendation Lifecycle (Current Shape)

The current recommendation-derived ladder looks roughly like this:

1. A task executes.
2. Verification and adequacy checks assess the result.
3. Inadequate-but-successful results can produce reviewer work.
4. Reviewer output can persist bounded recommendation records.
5. Recommendations can be surfaced, summarized, and interpreted.
6. Actionable recommendation records can be materialized into real queued tasks by explicit operator action.
7. Those tasks can be confirmed, surfaced as ready, surfaced as execution candidates, and explicitly executed.
8. Post-execution recommendation-derived results can be surfaced and given bounded operator-response options.
9. Eligible results can produce explicit follow-up review tasks or explicit repair tasks.

This gives the project a full recommendation-to-execution-to-response ladder without turning the system into uncontrolled automation.

## Architecture Summary

The project currently revolves around a small set of core concepts:

### Orchestrator
The orchestrator manages runs, selects work, dispatches execution, persists state, and coordinates later lifecycle transitions.

### Tasks
Tasks are the unit of work. They carry bounded objectives, constraints, scope, retry state, and traceability.

### Roles
The current implementation uses roles such as:
- planner
- coder
- reviewer

These are implementation-oriented roles, not permanent constitutional limits on future system shape.

### Providers
Providers abstract execution backends. The current system supports explicit provider handling and is designed to avoid hidden backend behavior.

### Verifier
The verifier framework supports deterministic checks where possible and helps separate:
- execution happened
- result passed verification
- result still needs adequacy review

### Recommendation / response layer
This is the newer, more specialized part of the system. It handles recommendation persistence, recommendation-derived task creation, confirmation/readiness/candidate surfacing, explicit execution, and bounded response-task creation.

## Repository Structure

A simplified view of the repository looks like this:

```text
docs/
  SYSTEM_OVERVIEW.md
  PROJECT_CONTEXT.md
  ARCHITECTURE_PLAN.md
  BUILD_RULES.md
  PROCESS_PROTOCOL.md
  PHASE_INDEX.md
  ACTION_LOG.md
  PHASE_*.md
  fixes/FIX_*.md

orchestrator/
  engine.py
  run_manager.py
  task_schema.py
  artifact_store.py
  recommendation_store.py
  reviewer_output.py
  adequacy.py
  providers/
  roles/

tests/
  test_phase_12_reviewer_recommendations.py
  test_phase_28_recommendation_lifecycle.py
  test_phase_30_recommendation_execution_results.py
  test_phase_31_recommendation_result_options.py
  test_phase_32_create_followup_review.py
  test_phase_33_create_repair_task.py

data/
  state/
  runs/
  tasks/
  artifacts/
  verifier_results/
  reviewer_recommendations/
```

Exact file layout may continue to evolve, but the overall shape is stable.

## Process Model

This project is not only code-governed; it is also process-governed.

Important process documents include:

- `BUILD_RULES.md` — execution discipline and constraints
- `PHASE_INDEX.md` — active control state for phases and fixes
- `PROCESS_PROTOCOL.md` — verify-before-fix discipline, evidence precedence, intervention classification, closure checks, and snapshot freshness rules
- `ACTION_LOG.md` — compact historical change log
- `PHASE_XX.md` — bounded implementation packets
- `FIX_PHASE_XX_YY.md` — bounded post-phase corrections

### Development philosophy
- Build in bounded increments.
- Prefer explicitness over convenience.
- Confirm defects before opening fixes.
- Treat auditor findings as triage input, not automatic truth.
- Check each new feature for stale wording, provenance ambiguity, hidden routing, hidden automation, and missing regression coverage.

## Running the System

The exact commands available continue to grow, but the framework currently includes command surfaces for:

- ordinary next-task progression
- provider-bounded execution
- recommendation inspection and summaries
- recommendation-created task surfacing
- confirmation and readiness surfacing
- ready execution-candidate surfacing
- explicit candidate execution
- post-execution result surfacing
- explicit follow-up review creation
- explicit repair-task creation

Because the CLI continues to evolve, use the repo's current `main.py` command parsing and docs as the immediate source of truth for exact command syntax.

## Current Status

The project is no longer just a scaffold. It is now a governed orchestration core with:

- persistent state
- bounded execution
- verifier integration
- recommendation persistence
- a recommendation-to-task ladder
- explicit response-task creation paths
- regression coverage around the later recommendation lifecycle
- hardened process rules for future development

In practical terms, it is already useful as a backbone for structured AI-assisted workflows, especially software-oriented ones.

## Current Limitations

The project is strong, but not finished.

Current limitations include:

- still software-first in implementation emphasis
- CLI surface area is growing and must be kept disciplined
- some provenance and response-layer details may need continued hardening
- end-to-end acceptance confidence still grows phase by phase rather than through one giant system-level test harness
- broader non-software domains would still require deliberate verifier, artifact, and role generalization

## Intended Direction

The current implementation is software-first because software work has been the best early domain for explicit bounded control.

But the framework is intended to remain applicable to broader bounded, inspectable, code-mediated workflows over time. That means future work should avoid unnecessary narrowing in:

- role semantics
- artifact semantics
- task semantics
- verification assumptions

unless a given phase explicitly requires that narrowing.

## Why This Project Exists

Most “agent” systems become hard to trust because they blur together:
- memory
- execution
- routing
- judgment
- and action

This project exists to do the opposite.

It is an attempt to build a system where:
- work is explicit
- state is persisted
- results are inspectable
- follow-up paths are bounded
- and increasing power comes only after increasing clarity

## Contributing / Working Style

If you continue building on this project:

- treat phase docs as bounded execution packets
- treat fix docs as bounded corrections
- do not casually refactor across layers without evidence
- preserve one-step explicit progression where that is part of the control model
- prefer small, inspectable changes over clever broad rewrites
- harden semantics before adding force

## Recommended Next Areas of Attention

Depending on the current repo state, likely future work areas include:

- response-layer coherence and provenance hardening
- additional regression coverage as the ladder expands
- bounded CLI consolidation when needed
- broader framework generalization beyond the software-first starting point

## License / Ownership

Add the actual license and ownership terms appropriate for your project here.

If this repository is private or personal, replace this section with the intended usage statement.

---

Orchestrator is best understood not as a chatbot project, and not merely as a code runner, but as a **governed orchestration framework for bounded AI-assisted work**.
