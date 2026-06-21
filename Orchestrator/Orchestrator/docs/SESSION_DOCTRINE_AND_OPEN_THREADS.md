# SESSION_DOCTRINE_AND_OPEN_THREADS.md

Status: Current product-side session doctrine and open-thread ledger convention.

## Purpose

This document gives product-side re-entry sessions a durable place to record session doctrine and open-thread handling conventions.

It exists because live chat instructions can preserve active session rails, but durable product state must live in product docs.

This document complements, but does not replace:

- STARTUP_BRIEF.md
- ORCHESTRATOR_METHOD.md
- ORCHESTRATOR_INTERACTION_MODEL.md
- REENTRY_PROTOCOL_01.md
- PHASE_INDEX.md
- ACTION_LOG.md
- SOURCE_MANIFEST.md
- CURRENT_SUCCESS_CRITERION.md
- PROJECT_VISION.md
- TRACKS_AND_OPEN_THREADS.md
- OPEN_THREAD_TRIAGE_PROTOCOL.md

## Session doctrine

A coordinator re-entry session is the active Orchestrator coordinator continuation unless the supplied prompt explicitly labels the session as a worker prompt.

The coordinator must orient from current product docs before substantive product recommendations.

The coordinator must triage visible open threads before ranking NBMs. It must
identify which thread, if any, is the highest-leverage `ACTIVE_NBM_CANDIDATE`
and preserve blocked, deferred, external, historical, retired, and unclear
caveats without letting them dominate the active NBM list.

The coordinator must not rely on conversation memory alone as proof.

The coordinator must separate accepted facts, observed fresh output, inference, suspicion, and recommendation.

The coordinator must keep work bounded by a named next boundary marker.

Pre-approval of NBMs may remove the approval wait, but it does not remove the need to state the boundary, preserve lockouts, and keep the work inside the allowed mutation surface.

## Response metadata convention

Substantive coordinator responses should preserve a RESPONSE_METADATA section with at least:

- active boundary
- mode
- changed files
- mutation status
- source/capsule status when relevant
- open threads
- next boundary
- proof/validation status

Live relevant open threads and their triage statuses should remain visible in
RESPONSE_METADATA.

RESPONSE_METADATA should show active relevant open threads, not blindly dump
every historical thread.

Durable product open threads should be recorded in this document when they matter beyond the current chat turn.

Durable phase status remains governed by PHASE_INDEX.md and ACTION_LOG.md.

## Open-thread classes

Use these classes when recording durable open threads:

- product-implementation
- product-language
- product-protocol
- source-record
- platform-deferred
- watchlist

Use the triage statuses in `OPEN_THREAD_TRIAGE_PROTOCOL.md` when deciding what
belongs in the active NBM list:

- `ACTIVE_NBM_CANDIDATE`
- `BLOCKED_AWAITING_PROOF`
- `DEFERRED_VALID`
- `EXTERNAL_TRACK`
- `HISTORICAL_EVIDENCE`
- `RETIRED_OR_RESOLVED`
- `NEEDS_TRIAGE`

A durable open thread should state:

- the unresolved issue
- whether it is product-side or platform-side
- the next allowed boundary type
- what is explicitly not authorized yet

## Intake-surface terminology

The phrase intake surface means the entry judgment and control surface where a human objective first becomes classified as proceed, clarify, or blocked.

It is not a planner.

It is not a task.

It is not a case packet.

It is not runtime execution.

It may authorize the next bounded move only when the outcome and boundary permit that move.

For Phase 64 specifically, the intake surface may emit a minimal decomposition_handoff object for proceed results, but that object is authorization context only.

## Durable open-thread ledger

| ID | Class | Thread | Current status | Next allowed boundary | Explicit non-authorization |
| --- | --- | --- | --- | --- | --- |
| OT-001 | product-language | Intake-surface terminology must remain clean: entry judgment/control surface, not planner/case packet/runtime. | Defined here for product-side use. | Product docs or intake-surface wording only. | Does not authorize planner, task, case-packet, or runtime behavior. |
| OT-002 | product-implementation | Phase 64 minimal decomposition_handoff implementation. | Implemented and locally validated; no longer pending. | Future product-code boundary only if Phase 64 behavior is deliberately extended. | Does not authorize platform, OpenClaw, model, WSL, installer, Discord, bridge, adapter, or A18CF work. |
| OT-003 | platform-deferred | Platform model-cache / installer testing strategy remains deferred. | Real concern, separate track. | Future platform strategy boundary. | Does not authorize current product integration or platform mutation. |
| OT-004 | source-record | Platform ZIP identity discrepancy between current observed aa39 and handoff-stated 2cc7. | Reconciled for current local/latest platform ZIP: aa39b6e3305220df5239a227e6ecc106877fad4ddcb412f4adf421e2ab38c2c5 is the present local platform ZIP identity under fresh read-only proof; 2cc7b7b77a48af9111d89bb32e0a4cfe4c5b3979078ceab921e4eb20b621a968 is retained as historical handoff-stated non-current audit context. | Future platform mutation or release/export baseline must compute a fresh hash from fresh operator output. | Does not authorize runtime, WSL, installer, model, Discord, bridge, adapter, A18CF, vendoring, cleanup, deletion, archive, Codex, or platform release claims without fresh proof. |
| OT-005 | source-record | Product ZIP identity after any later doc/code mutation must be captured from fresh operator output. | Latest clean uploaded artifact is recorded in SOURCE_MANIFEST.md, but edits after that artifact make the local source tree newer than the recorded ZIP. | Product export/ratification boundary when a new source artifact is needed. | The in-repo manifest cannot self-prove a future ZIP hash after it is edited. |
| OT-006 | product-protocol | Durable product open-thread ledger convention needed a repo-doc home. | Implemented here. | Maintain here when threads outlive a session. | Does not replace phase docs, action log, or current success criterion. |
| OT-007 | source-record/watchlist | Product source artifact had accumulated generated JSON/proof/runtime sludge requiring classification, archive, cleanup, and export-tooling repair. | Implemented for the current clean product ZIP baseline; remaining concern is a watchlist for future generated artifacts and export discipline. | Future source-hygiene audit/export-tooling boundary only if new generated payloads accumulate or export rules regress. | Does not authorize deletion, archive, runtime, WSL, installer, model, Discord, OpenClaw, bridge, adapter, A18CF, platform mutation, oz, Codex, or export. |

## Source-record caution

A ZIP cannot contain a manifest line that proves its own final post-edit hash if that line is edited before export.

Therefore, in-repo source hash records must be read as records of ratified observed artifacts, not as magical proof of every future export.

Fresh operator output for a product export supersedes older in-repo artifact records when the export occurs after the recorded artifact.

## Boundary lockouts preserved

This document does not authorize:

- runtime execution
- WSL execution
- installer execution
- model pull or model run
- Discord execution
- OpenClaw integration
- bridge execution
- adapter execution
- A18CF
- platform repo mutation
- vendoring
- cleanup/delete/archive
- oz
- Codex
- export

## PLATFORM_SOURCE_IDENTITY_SELF_HASH_CAVEAT_REPAIR_20260611

- Timestamp: 2026-06-11 14:44:37 -05:00
- Boundary: MUTATE_DOCS_CORRECT_PLATFORM_IDENTITY_SELF_HASH_CAVEAT_EXPORT_VERIFY_EXACT_PATHS_NO_RUNTIME_NO_WSL_NO_INSTALLER_NO_MODEL_NO_DISCORD_NO_BRIDGE_NO_ADAPTER_NO_A18CF_NO_VENDOR_NO_CLEANUP_NO_DELETE_NO_ARCHIVE_NO_CODEX
- Correction: earlier docs used language implying aa39b6e3305220df5239a227e6ecc106877fad4ddcb412f4adf421e2ab38c2c5 was the current/latest platform ZIP identity.
- Correct interpretation: aa39b6e3305220df5239a227e6ecc106877fad4ddcb412f4adf421e2ab38c2c5 was the pre-repair platform ZIP identity confirmed before docs mutation/export.
- Post-repair platform export identity from fresh operator output: 5802282f5228043ac94c0b231800f4bad0cfc0d2e838ad103204b917eb4cde92.
- Earlier handoff-stated non-current hash retained as audit context: 2cc7b7b77a48af9111d89bb32e0a4cfe4c5b3979078ceab921e4eb20b621a968.
- Self-hash caveat: a ZIP cannot stably contain its own final SHA256 as an internal source-of-truth field because writing that hash into the ZIP changes the ZIP hash.
- Durable rule: platform ZIP identity claims must be verified from fresh external operator output, not inferred from an embedded self-hash line.
- Product contamination status: no product contamination observed; product export hygiene remained passing through the repair sequence.
- Lockouts preserved: no runtime, no WSL, no installer, no model run/pull, no Discord, no bridge, no adapter, no A18CF, no vendoring, no cleanup, no deletion, no archive, no Codex.

