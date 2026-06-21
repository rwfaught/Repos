# PHASE_65.md

## Title

Intake Handoff Admission Gate

## Purpose

Phase 65 defines the smallest product-side admission gate between a Phase 64 `decomposition_handoff` and any deeper Orchestrator work surface.

Phase 64 established that an intake `proceed` result can emit a deterministic handoff object.

Phase 65 does not execute that handoff.

Phase 65 defines what must be checked before the system may treat that handoff as admissible input for a later bounded case-packet, task, planner, or execution surface.

The goal is to preserve honest contact at the membrane where user intent begins to become system work.

## Problem Statement

After Phase 64, the system can say:

- intake judged the objective as `proceed`
- a deterministic `decomposition_handoff` exists
- the handoff is authorization context only

That is useful, but it creates the next control problem.

A proceed handoff must not silently become:

- a task
- a case packet
- planner output
- runtime execution
- model execution
- platform work
- OpenClaw work
- bridge or adapter activity

The system needs an explicit admission gate that can inspect the handoff and classify whether it is ready for later bounded work.

Without this gate, the handoff risks becoming a hidden conveyor belt.

## Phase Boundary

This phase is product-side only.

This phase defines admission semantics only.

It does not create:

- tasks
- case packets
- planner output
- execution runs
- verifier runs
- reviewer runs
- runtime calls
- model calls
- platform integration
- OpenClaw integration
- bridge behavior
- adapter behavior

## Intended Behavior

A future implementation of this phase should expose a deterministic admission judgment for a `decomposition_handoff`.

The admission judgment should classify the handoff as one of:

- `admissible`
- `needs_operator_clarification`
- `blocked`

The judgment should preserve a clear reason.

The judgment should not mutate deeper work state.

The judgment should not create a task or case packet.

The judgment should not execute anything.

## Minimum Admission Requirements

A `decomposition_handoff` should only be considered admissible if it preserves:

1. Source intake linkage

   The handoff must identify the intake judgment or source objective it came from.

2. Proceed-only lineage

   The handoff must originate from an intake outcome classified as `proceed`.

3. Bounded objective text

   The handoff must carry a bounded objective or a bounded summary of the objective.

4. Explicit non-execution status

   The handoff must remain authorization context only.

5. Operator-legible reason

   The handoff must include enough explanation for the operator to understand why it is eligible for later bounded work.

6. No hidden mutation

   The admission check must not create or update case packets, tasks, artifacts, runtime state, or platform state.

## Rejection Conditions

A handoff should be classified as `needs_operator_clarification` if:

- the objective is too vague to bound
- the required files or scope are not named clearly enough
- the intended next work surface is ambiguous
- the handoff reason is not operator-legible

A handoff should be classified as `blocked` if:

- it comes from a non-proceed intake result
- it requests unsupported platform/runtime/model/Discord/OpenClaw behavior
- it attempts to bypass operator authorization
- it implies hidden mutation or unattended execution
- it lacks required lineage

## Operator Control Principle

The admission gate is not an autonomy layer.

It is a membrane.

Its job is to prevent the system from smuggling intent into action.

The system may classify the handoff.

The system may explain what is missing.

The system may identify the next bounded work surface.

The system must not silently create that work.

## Expected Implementation Surface

A later implementation boundary may add one or more of:

- a pure function for evaluating `decomposition_handoff` admission
- a CLI read surface for inspecting admission judgment
- deterministic tests proving proceed, clarify, and blocked classifications
- persisted or printed admission output if explicitly bounded

That later boundary must stay product-side unless separately authorized.

## Acceptance Criteria

A successful implementation of this phase should prove:

1. A valid proceed-derived `decomposition_handoff` can be classified as `admissible`.
2. A clarify-derived or blocked-derived input cannot be classified as admissible.
3. A malformed handoff is classified as `needs_operator_clarification` or `blocked`.
4. The admission check does not create tasks.
5. The admission check does not create case packets.
6. The admission check does not invoke planner behavior.
7. The admission check does not execute runtime, models, WSL, installer, Discord, OpenClaw, bridge, or adapter behavior.
8. The result is deterministic and operator-legible.

## Boundary Discipline

This phase does not authorize:

- platform repo mutation
- installer execution
- WSL execution
- model pull
- model run
- Discord execution
- OpenClaw integration
- bridge execution
- adapter execution
- A18CF
- vendoring
- cleanup/delete/archive
- export
- `oz`
- Codex

## Expected Next Boundary

After Phase 65 implementation is ratified, the next likely boundary is product-side Phase 66: a read-only/operator-controlled case-packet seed candidate review surface.

That boundary should inspect an admissible handoff's seed candidate and classify whether it is ready for explicit operator-controlled case-packet creation.

It must not create a case packet, create a task, invoke planner behavior, execute runtime/model behavior, or touch platform/OpenClaw/bridge/adapter surfaces.