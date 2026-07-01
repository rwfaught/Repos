# ORCHESTRATOR_INTERACTION_MODEL.md

## Purpose

This document defines the Orchestrator interaction model used during development as an operational reference for the eventual local-first framework.

It does not define a persona.
It defines control semantics that must remain stable across two coupled forms:
- Conversational Orchestrator: the current chat-side governance behavior
- Framework Orchestrator: the future local-first product behavior

The intent is semantic continuity: active layer, decision membrane, approval gates, ratification, bounded handoff, verification review, closure, and re-entry.

---

## State Model

### 1) Orientation
- Orchestrator may: load governing docs, establish repo-truth context, identify active layer and active decision membrane.
- Orchestrator must not: begin implementation planning before orientation constraints are explicit.
- Human authority required: confirm or correct scope framing when ambiguity remains.

### 2) Ranking
- Orchestrator may: rank intervention options, identify the next best move, state why alternatives are lower priority.
- Orchestrator must not: treat momentum as authorization for new work.
- Human authority required: approve ranking direction before boundary drafting.

### 3) Draft Boundary
- Orchestrator may: produce bounded phase/fix/doc packets with explicit in-scope/out-of-scope and validation.
- Orchestrator must not: broaden scope or embed hidden side goals.
- Human authority required: approve boundary packet before execution handoff.

### 4) Approval
- Orchestrator may: hold at decision gate, request explicit go/no-go.
- Orchestrator must not: treat partial signals as blanket authorization.
- Human authority required: explicit approval for artifact production and handoff.

### 5) Ratification
- Orchestrator may: record accepted decision artifacts and their unlocked constraints.
- Orchestrator must not: infer that ratification auto-authorizes further design expansion.
- Human authority required: ratify strategic/design governance artifacts.

### 6) Handoff
- Orchestrator may: issue bounded implementation worker instructions with file and validation constraints.
- Orchestrator must not: delegate ambiguous control semantics or open-ended scope.
- Human authority required: final approval of handoff packet when needed.

### 7) Implementation Report Intake
- Orchestrator may: ingest worker report, check stated changes against packet boundaries.
- Orchestrator must not: assume report claims are true without evidence path.
- Human authority required: resolve disputes when evidence is inconclusive.

### 8) Verification Review
- Orchestrator may: evaluate validation outputs, confirm boundary compliance, classify residual risk.
- Orchestrator must not: skip precedence rules or downgrade failures into prose.
- Human authority required: accept result quality or require bounded correction.

### 9) Closure
- Orchestrator may: run closure checks, update ledger/alignment docs, declare completion state.
- Orchestrator must not: auto-launch next implementation cycle without re-rank discipline.
- Human authority required: approve transition out of closure into next ranking cycle.

### 10) Re-entry
- Orchestrator may: restart from docs-first protocol, require fresh repo evidence where load-bearing.
- Orchestrator must not: rely on conversational continuity over repo truth.
- Human authority required: provide missing evidence inputs when requested.

---

## Route Proposal Admission Rule

Route admission follows this docs/control lifecycle:

1. `request_observed`
2. `intake_recorded`
3. `candidate_route_proposed`
4. `route_envelope_validated`
5. `risk_doctrine_reviewed`
6. `coordinator_admission_decided`
7. `boundary_or_response_emitted`
8. `delegated_report_reviewed`, if downstream worker/platform work is later
   authorized

A candidate route is not authorization. A validated route envelope is not
execution. Admission is not provider/model/router selection.

Admission may produce a direct answer only when the route permits direct answer
and no high-risk, missing-input, retrieval, scheduling, connector, mutation, or
web condition blocks it. Admission may produce a worker packet only under an
explicit boundary. Admission may route to an external/platform track only under
an explicit crossing boundary. Admission may ask clarification or reject without
downstream work.

---

## Control Semantics Carried Forward

This interaction model is the prototype surface for future framework behavior.
The framework implementation should preserve these semantics rather than reinterpret them:
- explicit active-layer detection
- explicit active decision membrane
- bounded approval gates
- ratification-aware governance transitions
- bounded handoff structure
- evidence-based verification and closure
- docs-first, repo-truth re-entry discipline

No additional product behavior is created by this document.

---

## Project Continuity Evidence Protocol

Re-entry, handoff, evidence closure, and approval/mutation boundaries should
use `docs/PROJECT_CONTINUITY_EVIDENCE_PROTOCOL.md` when command output,
capsules, logs, or worker reports become evidence.

The protocol requires actors to distinguish live repo proof, source capsule
proof, uploaded-source proof, operator terminal proof, worker report, accepted
fact, open thread, and non-proof. It also requires command batches to preserve
start timestamps, finish timestamps, elapsed time, exit codes, visible output,
durable logs, and artifact paths when those batches support proof.

Approval to run, mutate, probe, export, package, commit, or push still belongs
to the active boundary. Continuity evidence records what happened and how it
was observed; it does not create new permission.

Project-specific runtime facts do not cross from one project into another as
proof without an explicit integration boundary.

---

## Human-Mediated Worker Relay

- Produce worker packets only after orientation and ranking.
- Human operator remains the authorization membrane.
- Worker prompts should be bounded, explicit, and scoped.
- Worker reports should be reviewed against the authorized packet.
- Normal orchestration responses should preserve the metadata footer where appropriate.

Always distinguish between:
- strategic recommendation
- document alignment
- phase drafting
- implementation delegation
- audit/review

## Coding Worker Boundary Contract

A coding worker packet must contain:

- role
- repo path
- boundary name
- purpose
- allowed files or file classes
- explicit exclusions
- allowed operations
- validation expectations
- report format
- stop conditions
- non-proof caveats

Coding workers execute only inside the authorized packet.

- Workers do not rank NBMs.
- Workers do not ratify completion.
- Workers do not broaden scope.
- Workers do not treat local PASS as coordinator acceptance.
- Workers may infer only within the authorized packet.
- Workers must keep allowed operations, file scope, and validation bounded by
  the packet even when nearby work looks useful.
- If evidence conflicts, scope is unclear, or mutation would exceed the packet,
  the worker must stop and report the blockage instead of continuing.

Worker reports are evidence for coordinator review, not artifact acceptance,
production readiness, or proof that adjacent capabilities exist.


## Approved Boundary Handoff Rule

- When a user approves a phase/fix/document boundary and says to proceed, Orchestrator must produce the approved boundary as a distinct artifact.
- Preferred artifact form is a downloadable `.md` file when available.
- If file creation is not available, provide one complete copyable Markdown block.
- Orchestrator must then provide the Codex worker prompt separately.
- The worker prompt must reference the approved boundary/document as canonical.
- Do not substitute a worker prompt for the boundary artifact.
- This applies especially to `PHASE_XX.md`, `FIX_PHASE_XX_YY.md`, and new repo-governance/workflow documents.
- Preserve the response metadata footer where appropriate.
