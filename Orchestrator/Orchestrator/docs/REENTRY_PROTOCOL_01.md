# REENTRY_PROTOCOL_01.md

## Re-entry Protocol 01: Repo-Based Restart Discipline

---

## Goal

Define the minimum continuity protocol required to restart orchestration cleanly after interruption, subscription lapse, session loss, or worker/context drift.

This artifact should make it possible for a new or returning Orchestrator to regain orientation from the repo and a small targeted snapshot, rather than depending on whole-repo rereads or fragile conversational memory.

This is a **docs/operating-protocol artifact**.

It is not:
- a feature phase
- a product strategy artifact
- a code implementation phase
- a transport design
- a substitute for truthful docs

Its purpose is narrower:

to define how the project should recover its working state from the repo itself.

---

## Why This Artifact Exists

Recent recovery work exposed three realities:

1. the repo can advance faster than its top-level docs
2. conversational continuity can make project state feel cleaner than the active repo actually is
3. reading an entire growing repo into every new session is inefficient and eventually unrealistic

That means continuity must become deliberate.

The project needs a compact restart discipline so that a future session can answer, quickly and truthfully:

- what this project is
- what state it is in
- what phase history is trustworthy
- what the current strategic layer is
- what active implementation work, if any, should lead next
- what fresh code evidence is required before making new judgments

This artifact exists to define that discipline.

---

## Core Principle

**The repo must become the primary re-entry surface.**

Conversational memory is useful.
It is not the source of truth.

A clean restart should come from:
- the governance stack
- the phase ledger
- the action log
- current strategy/design anchors
- targeted fresh code evidence only where needed

Not from replaying the entire project history informally.

---

## Required Re-entry Stack

A returning Orchestrator should orient from a small fixed document set first.

### Required startup read set

The minimum re-entry set should be:

- `docs/PROJECT_VISION.md`
- `docs/CURRENT_SUCCESS_CRITERION.md`
- `docs/ORCHESTRATOR_METHOD.md`
- `docs/STARTUP_BRIEF.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`

### Conditional read set

Read these only when they are currently load-bearing:

- active product strategy artifacts
  - for example: `docs/PRODUCT_STRATEGY_*.md`
- active intake design artifacts
  - for example: `docs/INTAKE_TRIAGE_DESIGN_*.md`
- active recovery artifacts
  - for example: `docs/DOCS_RECOVERY_*.md`
- currently open or most recent approved boundary docs
  - phase / fix / alignment docs not yet fully metabolized into repo truth

This keeps the restart surface small while still allowing strategic context to remain current.

---

## Required Re-entry Questions

A returning Orchestrator should explicitly answer these questions before resuming forward work:

1. What is the current product/strategy layer?
2. What is the latest trustworthy phase/governance state?
3. Are there active recovery notes or partial-support classifications that constrain claims?
4. Is implementation currently paused, active, or blocked?
5. What is the current highest-priority open thread?
6. Does the next judgment depend on fresh code state?

If these cannot be answered from the docs stack, the docs stack is not doing its job.

---

## Snapshot Discipline

The project should stop treating “load the whole repo” as the default continuity mechanism.

Instead:

### Use a fresh full snapshot when:
- ranking depends on current code architecture broadly
- the repo may have changed significantly
- recovery/classification depends on distributed code evidence
- a new session needs to inspect multiple interacting surfaces

### Use targeted files when:
- the question is narrow
- the likely touched surfaces are known
- the risk of stale assumptions is localized

Examples:
- `main.py`
- a specific module under `orchestrator/`
- one test file
- one verifier module
- one docs file


### Archive access rule (`projects.tar.gz`)

When a `projects.tar.gz` handoff is used:

- confirm the canonical snapshot path first
- inspect archive root structure with a small listing before broader access
- prefer targeted archive reads for required files before broad extraction
- only extract broader paths when targeted reads are insufficient

### Do not assume freshness when:
- code or docs may have changed since the last verified snapshot
- acceptance depends on exact present file state
- ranking depends on whether a seam still exists

In those cases, ask for:
- a fresh snapshot
or
- the minimum relevant files

This rule is mandatory.

---

## Repo Truth Rule

When repo truth and conversational momentum diverge, **repo truth wins**.

That means:
- do not claim a phase is implemented unless active repo evidence supports it
- do not let prior conversation smooth over missing files
- do not repair continuity by narrative alone
- use recovery artifacts when docs, code, and claims diverge

This rule exists because smooth false continuity is more dangerous than explicit incompleteness.

---

## Partial-Support Rule

If the active repo contains mixed support for prior work, re-entry must preserve that explicitly.

Allowed states include:
- supported
- partially supported
- unsupported / missing

These states should not be flattened during restart.

A returning Orchestrator must inherit those distinctions and avoid speaking as though partially supported work were fully intact.

---

## Startup Sequence

The preferred restart sequence is:

1. read the required startup docs
2. read any currently load-bearing strategy/design/recovery artifacts
3. inspect `PHASE_INDEX.md` and `ACTION_LOG.md` together
4. identify whether any repo-truth caveat or partial-support note is active
5. decide whether a fresh snapshot is needed before further judgment
6. only then resume ranking, review, or drafting

This sequence should become the normal restart path.

---

## Required Repo Maintenance Consequence

This protocol implies a maintenance responsibility:

The project’s docs stack must remain strong enough that a fresh session can recover from it.

That means:
- `PHASE_INDEX.md` must remain truthful
- `ACTION_LOG.md` must remain current enough to explain recent moves
- strategy/design artifacts that materially outrank implementation should be present in `docs/`
- partially supported or recovered state must be visible, not hidden in chat history

If those conditions fail, the next move should often be documentation recovery before new feature work.

---

## Restart Output Requirement

After re-entry, the Orchestrator should produce a short state summary before resuming normal work.

That summary should make visible:

- current response type
- current state
- what is known from repo truth
- what remains uncertain
- whether a fresh snapshot is still required
- next best move

This keeps the restart explicit instead of implicit.

---

## What This Protocol Is NOT For

This protocol is not an excuse to avoid inspecting code.

It is also not a promise that docs alone can answer every question.

Its purpose is to reduce unnecessary repo-wide rereads and make restarts efficient, not magical.

The rule is:
- docs first for orientation
- fresh code evidence where judgment depends on reality

---

## Failure Modes This Protocol Prevents

This protocol is meant to reduce:

- phase claims drifting beyond active repo evidence
- new sessions over-trusting prior conversation
- whole-repo rereads becoming the default recovery mechanism
- implementation work resuming while docs continuity is dirty
- strategic context being lost because it never made it into repo docs
- unsupported history being treated as intact

---

## Deliverable Shape

This protocol should establish:

1. the canonical startup read set
2. the conditional load-bearing read set
3. the required re-entry questions
4. the snapshot discipline rule
5. the repo truth rule
6. the partial-support rule
7. the preferred restart sequence
8. the restart output requirement

---

## Validation Standard

This artifact is acceptable only if it:

- reduces dependence on conversational memory
- avoids whole-repo rereads as the default continuity method
- keeps repo truth above narrative smoothness
- makes partial-support states survivable across sessions
- gives a returning Orchestrator a clear way to restart without pretending certainty

---

## Expected Next Step After This Artifact

If this artifact is ratified, the likely next move would be either:

- a small alignment pass to ensure the re-entry set docs are actually current and sufficient
- or a return to strategic/product work using the cleaned continuity protocol

No feature work should use continuity confusion as an excuse again once this protocol is in place.
