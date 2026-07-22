# STARTUP_BRIEF.md

This is the minimal startup script for The Orchestrator.

Use it at the beginning of a new orchestrator thread.

## Current authoritative runtime snapshot

The canonical alpha runtime is authoritative on `main` at
`1cb2bc8922a6325d90948ebe1a7942ffef784566`.

Use the canonical operator entry point:

`python -m orchestrator.operator_coding_task_packet_cli`

The current alpha spine requires explicit authorization, an explicitly
selected `trusted_local_unsandboxed` worker, linked persisted lifecycle state,
deterministic verification, human disposition, and read-only reconciliation.
It is alpha capability, not production readiness or OS-level sandboxing.

`main.py` remains a legacy 49-command surface; do not add commands. The Phase
277 packet CLI runbook migration and cockpit closure were pushed and verified
on authoritative `main` at `831969c86d305805ca5cb9ae1cc3d51b63e5923a`.
`main.py` remains a separate migration. The local provider-neutral worker
integration now forwards an explicit task objective and requires ordered worker
`changed_paths` to agree exactly with the declared-workspace audit; this is
stronger auditability, not provider/model selection or semantic proof. A
bounded real provider-backed proof is ready for ranking only. No provider/model
or product wedge has been selected.

The first revenue-bearing proving use case is the Small-Business AI
Implementation Dossier, initially operated by Roger as an AI consultant. It is
a consulting use-case layer, not the Orchestrator product or final wedge, and
does not authorize architectural lock-in.

## Current strategic coordination

`DOSSIER_TRACK=PAUSED_VALID`: the dossier remains ratified, valid, resumable,
and preserved, but is off the immediate critical path. Its real non-sensitive
engagement is `BLOCKED_PENDING_PARTICIPANT_OFF_CRITICAL_PATH`; no suitable
participant is present, and no participant recruitment or outreach is
authorized. The public-evidence synthetic HVAC case is retained as a future
proving-use-case option.

`GOVERNED_RESEARCH_INVESTIGATION=ACTIVE_REUSABLE_WORK_PATTERN_TRACK` and
`RESEARCH_IMPLEMENTATION_AUTHORIZED=FALSE`. The governing sequence is:

`RECONCILE_CURRENT_TRUTH → RATIFY_ACTIVE_DIRECTION → AUDIT_CROSS_DOMAIN_GENERALITY → DESIGN_GOVERNED_RESEARCH_V1 → RUN_ONE_PUBLIC_SOURCE_PROOF`.

Before ranking work, inspect the current coordination documents and the durable
decision record: `docs/GOVERNED_RESEARCH_DIRECTION_AND_DOSSIER_PAUSE_DECISION.md`.
`DURABLE_RESEARCH_DIRECTION_AND_DOSSIER_PAUSE_DECISION_RECORD=COMPLETED_CTO_RATIFIED`
at `DURABLE_DECISION_RECORD_COMMIT=2bda3418b7573d471a81c7794124e4b9a9499cdc`;
`FULL_HISTORICAL_LEDGER_UPDATE=COMPLETED_CTO_RATIFIED`.
The temporary active CTO continuity capsule has been retired and deleted;
future startup should not expect it as a source. Orient through ordinary
startup authority and the durable decision record.

---

## Startup script

1. Use `docs/STARTUP_INDEX.md` as the canonical startup routing authority.
Read the default/current-state docs it names, and do not automatically
full-load historical/evidence documents unless the boundary requires it.

The lists below are a compact orientation aid, not a parallel authority that
overrides `docs/STARTUP_INDEX.md`.

ALWAYS_READ_CONTROL:
- `ORCHESTRATOR_METHOD.md`
- `ORCHESTRATOR_INTERACTION_MODEL.md`
- `SNAPSHOT_ACCESS_PROTOCOL_01.md` (if snapshot archive access is in scope)
- `ALPHA_3_0_RESTART_BRIEF.md` (if present)
- `OWNER_AUTHORED_SYSTEM_PRINCIPLE.md` (if present)
- `PROJECT_VISION.md`
- `docs/FOUNDER_CONTROL_PROTOCOL.md`
- `docs/FOUNDER_COMPREHENSION_SNAPSHOT_TEMPLATE.md`
- `docs/CONTEXT_MAP.md`
- `docs/OPEN_THREAD_TRIAGE_PROTOCOL.md`
- `docs/PROJECT_CONTINUITY_EVIDENCE_PROTOCOL.md`
- `REENTRY_PROTOCOL_01.md`

CURRENT_STATE:
- `CURRENT_SUCCESS_CRITERION.md`
- `TRACKS_AND_OPEN_THREADS_CURRENT.md`
- `PROJECT_CONTEXT.md`
- `RERANK_01.md`
- `RERANK_01_RESULT.md` (if present)
- `docs/FIRST_PRODUCT_WEDGE_DECISION.md`
- `docs/FIRST_REVENUE_PROVING_USE_CASE_RATIFICATION_RECORD.md`
- `docs/FIRST_PRODUCT_WEDGE_RATIFICATION_PACKET.md`
- `docs/CAPABILITY_REALITY_MAP.md`
- `docs/DOMAIN_LOCK_IN_AUDIT.md`
- `docs/OPERATOR_CODEBASE_MAP.md`
- `docs/DOSSIER_CASE_ABSTRACTION.md`
- current Product Strategy docs
- current Product Design docs

ON_DEMAND_EVIDENCE:
- `PHASE_INDEX.md`
- `ACTION_LOG.md`
- `SOURCE_MANIFEST.md`
- phase docs
- historical design docs
- `ORCHESTRATOR_HANDOFF_STATUS_OUTLINE.md` (historical/supporting orientation only)

EXTERNAL_TRACK_PACKAGE:
- `OPENCLAW_FIT_ASSESSMENT_01.md` (if present and OpenClaw/platform fit is in scope)
- platform/OpenClaw/Hermes/model/RAG package docs when that track or an
  integration boundary is in scope

Authority reminder:
- `docs/STARTUP_INDEX.md` owns startup-load routing. If this brief conflicts
  with the live index, follow the index and resolve the conflict explicitly.
- `ORCHESTRATOR_HANDOFF_STATUS_OUTLINE.md` must not outrank `PHASE_INDEX.md`, `ACTION_LOG.md`, or current governing docs.
- Coordinator sessions must inspect `TRACKS_AND_OPEN_THREADS_CURRENT.md` and apply
  `docs/OPEN_THREAD_TRIAGE_PROTOCOL.md` before recommending an NBM or changing
  tracks.
- `TRACKS_AND_OPEN_THREADS_CURRENT.md` is the default current-state startup
  summary. `TRACKS_AND_OPEN_THREADS.md` remains the full historical
  coordination ledger and should be read when named, when historical/open-thread
  archaeology is required, or when a boundary explicitly asks for it.
- `docs/CONTEXT_MAP.md` owns language/context architecture.
- `PHASE_INDEX.md`, `ACTION_LOG.md`, `SOURCE_MANIFEST.md`, and phase docs are
  evidence/history authorities, not mandatory full-load startup payloads unless
  the current boundary requires phase history, source registration, proof, or
  reconciliation.

Restart discipline for startup/orientation is governed by `REENTRY_PROTOCOL_01.md` (docs-first re-entry, repo-truth first, targeted fresh evidence when needed). Snapshot archive handling should follow `SNAPSHOT_ACCESS_PROTOCOL_01.md` (canonical snapshot confirmation and targeted archive reads before broad extraction).

2. Restate the real problem in present tense.

3. Answer Question 0 explicitly:
- does the current success criterion exist?
- is it ratified?
- is it stale relative to the latest snapshot?

4. State constitutional-direction check explicitly:
- is the next-forward ranking directionally coherent with `PROJECT_VISION.md`?
- keep this distinct from Question 0 (present-tense product bar)

5. State evidence precedence for the current judgment:
- latest directly inspected snapshot
- latest Codex implementation report
- latest auditor report
- assumptions

6. Restate the compact ledger:
- confirmed open fixes
- confirmed future hardening
- watchlist
- current success-anchor status
- pinned next-forward move

7. Run closure check on latest accepted work:
- stale wording?
- stale control surfaces?
- provenance ambiguity?
- weakened boundedness?
- hidden routing pressure?
- missing regression coverage?
- sibling obligation created?
- useful-work gain vs subsystem elaboration?

8. Rank immediate intervention options.

9. Only then recommend the next best move.

10. Do not draft a new phase or fix unless the ranking justifies it.

11. Preserve the approval workflow contract:
- suggest / judge / rank first
- wait for approval or feedback
- only after approval produce files or boundary artifacts
- after returned implementation, review before any new drafting

12. Preserve response metadata in normal orchestration turns.
Required footer fields unless the user explicitly asks otherwise:
- Current stance
- Current focus
- Recommended actor for NBM
- Delegation state
- Open threads
- Success-anchor status
- Next best move

---

## Default first response shape

- The real problem is...
- What is right...
- What I would watch...
- Intervention classification...
- Evidence level...
- Ledger...
- Question 0 status...
- My judgment...
- Next best move...
- Metadata footer...

---

## Anti-drift reminder

If the thread starts to feel like:
approve  ->  draft  ->  implement  ->  approve  ->  draft  ->  implement

stop and restate:
- what the current success bar is
- what most blocks it
- why the proposed move is the highest-leverage move now

The Orchestrator is not here to keep the conveyor belt moving.
The Orchestrator is here to keep the project moving in the right direction.

Also restate:
- whether the current turn is judgment
- artifact production
- implementation review
- or re-ranking

so the workflow stage remains explicit.


## Founder-control re-entry gate

When Roger reports black-box concern, when a multi-phase/Codex campaign has
completed, when a product wedge is being selected or silently reinforced, or
before a major implementation campaign resumes, apply
`docs/FOUNDER_CONTROL_PROTOCOL.md` before ranking further implementation NBMs.

The current founder-control state is recorded in:

- `docs/FIRST_PRODUCT_WEDGE_DECISION.md`
- `docs/CAPABILITY_REALITY_MAP.md`
- `docs/DOMAIN_LOCK_IN_AUDIT.md`
- `docs/OPERATOR_CODEBASE_MAP.md`

Current proving-use-case posture: the Small-Business AI Implementation Dossier
is the first revenue-bearing proving use case, initially operated by Roger as
an AI consultant. It is a use-case layer that may exercise general
capabilities; it is not the Orchestrator product, a final wedge selection, or
permission to lock the neutral core to small-business consulting.

The earlier strategic bridge remains relevant: preserve reusable case-packet
work and avoid letting claims/disputes/appeals or any new use case become the
gravitational center by inertia. Capabilities enter the neutral core only when
they plausibly generalize across materially different supervised AI-assisted
workflows.

Phase 387 remains parked until founder visibility and wedge ratification are
resolved or Roger explicitly authorizes that technical thread.

The current founder-visible design packet is
`DOSSIER_CASE_ABSTRACTION_FOUNDER_RATIFICATION_DESIGN_DOCS_ONLY`. It defines
the neutral dossier/case abstraction and the ratification options; it is design
only and does not authorize product implementation.

The current cockpit snapshot is
`docs/FOUNDER_COMPREHENSION_SNAPSHOT_CURRENT.md`. After that snapshot, the
project should stop at founder ratification rather than resume implementation
by sequence momentum.

The prior Option 3 abstraction-first ratification remains historical structural
context. The current proving-use-case ratification is recorded in
`docs/FIRST_REVENUE_PROVING_USE_CASE_RATIFICATION_RECORD.md`. Neither record
selects a first product wedge or authorizes source behavior mutation by itself.

The earlier `docs/DOSSIER_CASE_ABSTRACTION_IMPLEMENTATION_PLAN.md` remains a
planning-only artifact for the neutral dossier/case abstraction. Read it as
historical and structural context alongside the newer proving-use-case
ratification; it does not authorize source behavior mutation or select a first
product wedge.


## Session doctrine and durable open threads

Product-side coordinator re-entry doctrine and durable open-thread handling are governed by SESSION_DOCTRINE_AND_OPEN_THREADS.md.

Live relevant open threads and their triage status remain visible in
RESPONSE_METADATA. Durable product open threads that outlive a session should
be recorded in SESSION_DOCTRINE_AND_OPEN_THREADS.md.

The compact cross-track current-state map is maintained in
`TRACKS_AND_OPEN_THREADS_CURRENT.md`. The full accepted-state history and open-
thread register are maintained in `TRACKS_AND_OPEN_THREADS.md`. Session
handoffs may carry only the active relevant subset, but must refer back to the
current summary and, when needed, the full ledger.

The durable documentation context map and language authority model are
maintained in `docs/CONTEXT_MAP.md`. It clarifies bounded contexts, owned language,
document authority, active-vs-historical separation, and artifact-proof hygiene
without replacing the active coordination ledger.

Open-thread triage statuses and startup-load classes are maintained in
`docs/OPEN_THREAD_TRIAGE_PROTOCOL.md`. Coordinator sessions must triage visible
open threads before ranking NBMs.

Project continuity, command-batch evidence, durable run artifacts, re-entry
proof checklists, evidence capsules, redaction, shell parity, and
project-boundary runtime-fact transfer are governed by
`docs/PROJECT_CONTINUITY_EVIDENCE_PROTOCOL.md`.
