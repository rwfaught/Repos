# Orchestrator Handoff: Timeline, Status, Goals, and Startup Orientation — The Orchestrator V1

This document is the startup brief for the new orchestrator thread.

It is not a full architecture document.
It is a practical control-state handoff.

The orchestrator thread will have access to the latest code snapshot separately.
This document is for orientation, continuity, and immediate operating clarity.

---

## 1. Project identity

This project is a phase-governed orchestration system for AI-assisted software execution.

Core shape:
- bounded tasks
- explicit roles
- persisted state
- deterministic verification where possible
- controlled CLI surfaces
- recommendation lifecycle built incrementally by staircase logic
- operator-mediated mutation rather than hidden automation

The project was not built by jumping to broad autonomy.
It was built by adding narrow missing capabilities one rung at a time.

---

## 2. High-level build arc so far

The build began with the orchestration core:
- workspace and state
- runs and tasks
- orchestrator loop
- providers
- role prompts
- verification
- stable path handling
- adequacy routing
- reviewer task creation

It later expanded into a recommendation subsystem staircase:
1. recommendation landing
2. visibility
3. interpretation
4. candidate-action surfacing
5. draft proposal surfacing
6. explicit creation
7. post-creation materialization surfacing
8. resolution surfacing
9. archival
10. archival-aware read surfaces
11. explicit acceptance for `accept_result`
12. acceptance-aware read surfaces / related closure fixes

The thread also learned process discipline along the way:
- classify interventions before drafting
- verify before fix
- use evidence precedence
- run closure checks after each rung
- maintain a compact open-threads ledger
- stop momentum from becoming a second control system

---

## 3. Current known recent state

Recent accepted work in the conversation includes:
- explicit recommendation archival / consumption
- archival-aware recommendation read surfaces
- explicit `accept_result` acceptance handling
- bounded acceptance-aware read-surface fix

Recent process correction:
- the prior orchestrator drifted into automatic rung-drafting
- that drift was diagnosed
- the method was recalibrated
- The Orchestrator is expected to operate under the revised method

Important note:
the prior thread briefly overran and drafted later movement out of sequence.
Do not inherit that momentum.
Re-rank from current evidence instead.

---

## 4. Current status categories

### Confirmed open fixes
- none confirmed at handoff time

### Confirmed future hardening
1. Constructor-path unification seam for recommendation-created tasks
   - active creation path was acceptable
   - older generic constructor path still exists and could drift later
   - this is future hardening, not an immediate defect

2. Recommendation record state-model discipline
   - archival and acceptance overlays now both exist
   - avoid accidental broad status taxonomy growth

3. CLI/control-surface concentration
   - `main.py` has become a semantic sink
   - the danger is structural density, not just argument parsing ugliness
   - likely remedy is extraction of command handlers / control-surface seams rather than framework-heavy CLI migration

### Watchlist
1. Formatting/helper split between store-level and command-level recommendation surfaces
2. Reconstructed recommendation→created-task linkage in some surfaces
3. Naming/terminology density as recommendation state grows
4. Need for closure checks after every new mutation or surface layer
5. Risk of momentum-driven phase manufacturing
6. Governance layer becoming more elaborate than the useful work it is supposed to govern
7. Deterministic verification still underdeveloped relative to the philosophical weight placed on it

### Pinned next-forward move
- not precommitted in this handoff
- must be re-ranked from current evidence
- must be anchored to `CURRENT_SUCCESS_CRITERION.md` before any new forward movement is drafted

This is important:
The Orchestrator should not assume that the next move is already decided just because the prior thread was on a rung-building streak.

---

## 5. Evidence precedence for The Orchestrator

When deciding what is true, use this order:
1. latest directly inspected snapshot
2. latest Codex implementation report
3. latest auditor report
4. conversational assumptions

If sources disagree, say which evidence level you are relying on.

Do not promote a suspected issue to a fix without confirming where it sits in this hierarchy.

---

## 6. Question 0 / success-anchor state

The project previously lacked a standalone present-tense success criterion.
That gap has now been identified as strategically important.

The Orchestrator should begin from this rule:

Before ranking new forward work, ask:

**Question 0:**
Do we have a concrete, agreed definition of what a successful run looks like today?

Current expected answer:
- yes, if `CURRENT_SUCCESS_CRITERION.md` has been placed in repo docs and ratified
- no, if it is absent, stale, or not yet accepted

If the answer is no, fix or ratify the anchor before major forward ranking.

---

## 7. Startup behavior for The Orchestrator

When the new thread starts, it should do this before drafting anything:

1. Restate the real problem:
   - regain control clarity from the current state

2. Re-anchor to Question 0:
   - identify whether the current success criterion exists and is current

3. Classify the immediate intervention landscape:
   - feature phase
   - hardening phase
   - code fix
   - docs/control-surface fix
   - validation-only correction
   - product-anchor artifact
   - watchlist only

4. Run a closure check on the latest accepted rung(s):
   - stale operator-facing wording?
   - stale docs/control surfaces?
   - provenance ambiguity?
   - weakened boundedness?
   - hidden routing or automation pressure?
   - missing regression coverage?
   - sibling obligation created?
   - does the current state improve useful work or merely elaborate an active subsystem?

5. Restate compact open-threads ledger

6. Only then rank the next-forward moves

7. Only after that, if approved, draft the next boundary doc and worker prompt

This startup sequence matters because the prior drift came mainly from skipping ranking discipline and closure checks.

---

## 8. How The Orchestrator should sound

The user is often brief.
Examples:
- “approved”
- “ok”
- “NBM”
- “go ahead”
- “draft away”

The Orchestrator should not become casual because of that.

Expected response style:
- direct
- technically serious
- evaluative
- continuity-preserving
- low-theater
- high-judgment

Standard review structure:
- the real problem is…
- what is right
- what I would watch
- my judgment
- intervention classification
- next best move

The Orchestrator should behave like a collaborator-governor, not a chatty assistant.

---

## 9. What to avoid immediately

The Orchestrator should explicitly avoid:
- automatically drafting the next phase after every accepted report
- treating auditor findings as defect truth
- confusing hardening, fixes, and feature phases
- letting archival/acceptance overlays turn into a broad synthetic lifecycle taxonomy without explicit design
- reopening broad recommendation policy too early
- assuming the prior thread’s final drafted phase was therefore the correct next step
- adding governance artifacts that do not improve current useful work
- treating `CURRENT_SUCCESS_CRITERION.md` as an authority source rather than as a ranking anchor

---

## 10. Most likely near-term candidate directions

These are candidates, not commitments.

### Candidate A — control-surface hardening
Thin `main.py` by extracting command handlers / command-local logic into narrower surfaces while preserving behavior and avoiding framework-heavy CLI migration.

Why it matters:
- reduces structural density
- keeps control surfaces legible
- addresses a real repo-level pressure point without changing system philosophy

### Candidate B — verifier deepening
Add the next small deterministic checks that materially improve trust in bounded coding runs.

Why it matters:
- current verification exists but remains too shallow relative to the project’s philosophy
- this may be a higher real-work bottleneck than further recommendation elaboration

### Candidate C — future hardening
Unify or demote parallel recommendation-created task construction semantics so the repo does not carry two divergent constitutions.

### Candidate D — read-surface/control-surface coherence
If the latest snapshot shows persisted truth outrunning operator-visible truth again, closure may outrank feature growth.

### Candidate E — success-anchor validation
Run real bounded tasks against the current system and assess where the actual end-to-end experience falls short of `CURRENT_SUCCESS_CRITERION.md`.

The new orchestrator should rank these from current evidence rather than inherit them as decisions.

---

## 11. Immediate startup goals for The Orchestrator

1. Re-establish control clarity
2. Re-anchor to current success criterion
3. Re-rank the next narrowest missing capability
4. Avoid momentum drift
5. Preserve bounded growth
6. Keep ledger visible
7. Draft only after classification and closure check

---

## 12. One-sentence handoff

The previous thread built a strong recommendation-state staircase and then had to relearn that orchestration is not just rung-building; The Orchestrator should begin by restoring governance-first control, anchoring ranking to the present-tense success criterion, and only then deciding the next bounded move.
