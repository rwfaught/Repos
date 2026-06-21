# PROCESS_PROTOCOL.md

## Purpose

This document defines the operating protocol for phase-governed execution, defect handling, audit handling, and process closure.

It exists to keep the build process explicit, synchronized, and bounded as the project becomes more capable.

This document is about **how work is governed**, not about adding product behavior.

---

## Core Process Rules

### 1. Verify Before Fix

A suspected defect must not become a fix document solely because it appears in:
- an audit report
- a conversational suspicion
- a stale snapshot

Before opening a fix, classify the issue as one of:

- confirmed in latest inspected snapshot
- confirmed in latest Codex implementation report
- not confirmed
- downgraded to future hardening
- downgraded to watchlist

A fix should be opened only for a **confirmed defect** or a **confirmed control-surface inconsistency**.

---

### 2. Evidence Precedence

When sources disagree, resolve them in this order:

1. latest directly inspected snapshot
2. latest Codex implementation report
3. latest auditor report
4. conversational memory / assumptions

This precedence should be used explicitly when deciding whether an issue is real, stale, or already resolved.

---

### 3. Intervention Classification

Before drafting work, classify the proposed intervention as one of:

- feature phase
- hardening phase
- code fix
- docs/control-surface fix
- validation-only correction
- watchlist only (no immediate action)

Do not draft a phase or fix until the intended intervention class is clear.

---

### 4. Audit Handling

Auditor output is triage input, not defect truth.

Auditor findings should be used to:
- sharpen attention
- rank pressure points
- distinguish likely fix-now vs hardening vs watchlist

Auditor findings should not automatically create new fixes or phases without confirmation.

---

### 5. Closure Check After Every Phase or Fix

After every implemented phase or fix, check whether the change introduced any of the following:

- stale operator-facing wording
- stale docs/control surfaces
- provenance ambiguity
- weakened boundedness
- hidden routing behavior
- hidden automation creep
- missing regression coverage for the new ladder rung
- newly implied sibling response path or sibling hardening obligation

This closure check should happen before resuming forward growth.

---

### 6. Open-Threads Discipline

The project should maintain a compact live understanding of:

- confirmed open fixes
- confirmed future hardening items
- watchlist items
- pinned next-forward move

This state may be mirrored in conversation, but repo governance should not rely on conversation memory alone.

---

### 7. Snapshot Freshness Discipline

If there has been a meaningful series of changes, prefer:
- a fresh snapshot
- or a fresh Codex implementation report

over older assumptions or older audit conclusions.

Do not let stale evidence drive current decisions.

---

## Issue State Categories

When discussing findings, prefer these categories explicitly:

- suspected issue
- confirmed defect
- docs/control-surface inconsistency
- future hardening candidate
- watchlist item
- resolved / closed

This keeps urgency proportional and reduces accidental overreaction.

---

## Process Principle

The project should harden its process in the same way it hardens its code:

- explicit over implicit
- confirmed over assumed
- bounded over sprawling
- synchronized over stale
- inspectable over conversationally improvised
