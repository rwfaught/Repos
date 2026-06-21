# SYSTEM_OVERVIEW.md

## Purpose

This project is a local-first, code-driven orchestration system for structured AI-assisted software work.

Its purpose is to replace unreliable one-shot AI generation with a controlled workflow that:
- breaks work into bounded tasks
- assigns those tasks to explicit roles
- verifies outputs deterministically where possible
- stores state externally on disk
- preserves inspectability and control across phases

This system is intended for software-oriented workflows first, especially scaffolding, implementation, review, verification, and repair.
That is the current implementation center of gravity, not a constitutional software-only boundary.

## Core Idea

AI is treated as a worker inside a controlled system, not as the system itself.

The system:
- controls workflow in code
- stores state explicitly
- uses AI only for bounded role-specific work
- verifies outputs through deterministic checks where possible
- logs meaningful actions for continuity and traceability

## System Shape

At a high level, the system is built around:
- an orchestrator
- bounded task cards
- specialized roles such as planner, coder, and reviewer
- provider abstractions for execution backends
- verifiers for deterministic checks
- persistent run, task, and artifact records

The orchestrator is the control spine.
The roles are workers inside the workflow.
The verifiers are inspection tools.
The persistent files are the system memory.

## Non-Goals

This is NOT:
- a chatbot
- a multi-agent swarm demo
- an unconstrained autonomous AI system
- a system that relies on hidden prompt memory
- a system where one model plans, builds, reviews, and approves everything in one pass

## Operating Philosophy

The project favors:
- explicitness over magic
- bounded tasks over broad requests
- sequential execution over concurrent sprawl
- code-owned control over model-owned control
- persistent state over conversational memory
- verification over self-trust

## Build Philosophy

The project itself should be built using the same discipline it is designed to enforce.

That means:
- work in phases
- keep each phase bounded
- avoid expanding beyond the current phase
- stop cleanly after each phase
- maintain a readable action log
- preserve coherence across files and subsystems

## Scope Clarification

Current practical strength is software-first execution.
Future phases should preserve architecture-level flexibility for other bounded, inspectable workflows when that can be done without harming current software reliability.

This does not mean the current system is already a domain-general executor.
It means future work should avoid unnecessary software-only narrowing in:
- role semantics
- artifact concepts
- task semantics
- verification assumptions
unless a phase explicitly requires software-specific constraints.
