# Open Thread Triage Protocol

Status: Current product-side coordinator triage protocol.

## Purpose

This document defines the durable triage statuses used when coordinator
sessions evaluate visible open threads before ranking the next best move
(NBM).

It is docs/control guidance only. It does not authorize source changes,
runtime execution, provider/model execution, platform execution, export,
package creation, cleanup, deletion, archive, or production task execution.

## Required Triage Rule

Every CTO/coordinator re-entry must evaluate visible open threads as triage
before recommending NBMs.

The coordinator should identify which thread, if any, is the highest-leverage
`ACTIVE_NBM_CANDIDATE`. Blocked, deferred, external, historical, retired, and
unclear threads must preserve their caveats without dominating the active NBM
list.

## Triage Statuses

Use these statuses when classifying open threads:

- `ACTIVE_NBM_CANDIDATE`: A live candidate for the next bounded move.
- `BLOCKED_AWAITING_PROOF`: Valid thread, but cannot advance until fresh
  proof, operator output, or artifact evidence exists.
- `DEFERRED_VALID`: Valid but intentionally not next.
- `EXTERNAL_TRACK`: Belongs primarily to platform, OpenClaw, Hermes, model,
  RAG, installer, or another non-product track unless an integration boundary
  authorizes it.
- `HISTORICAL_EVIDENCE`: Preserved for audit/history, not active work.
- `RETIRED_OR_RESOLVED`: No longer active. Must not influence NBM ranking
  unless reopened with reason and proof.
- `NEEDS_TRIAGE`: Thread exists but its status is unclear; coordinator must
  classify it before ranking it.

## Startup Load Discipline

Use these document load classes for coordinator re-entry:

- `ALWAYS_READ_CONTROL`: Small docs needed for role, protocol, and current
  orientation.
- `CURRENT_STATE`: Docs used to understand active product state and open
  threads.
- `ON_DEMAND_EVIDENCE`: Append-heavy docs such as `ACTION_LOG.md`,
  `SOURCE_MANIFEST.md`, `PHASE_INDEX.md`, phase docs, and historical design
  docs. Read when the boundary requires evidence, phase history, source
  registration, proof, or reconciliation.
- `EXTERNAL_TRACK_PACKAGE`: Platform/OpenClaw/Hermes/model/RAG package docs.
  Read only when that track or an integration boundary is in scope.

Startup should not automatically full-load every historical/evidence document
unless the boundary requires it. The coordinator must still load enough current
orientation to preserve safety, proof caveats, role boundaries, and active
open-thread triage.

## Response Metadata Rule

`RESPONSE_METADATA` should show active relevant open threads and their triage
status. It should not blindly dump every historical thread when those threads
are evidence, retired, deferred, blocked pending proof, or external to the
current boundary.
