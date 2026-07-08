# Startup Index

## Purpose

This document is a startup routing index for Orchestrator CTO/coordinator
sessions. It defines which documents should be read by default, which documents
should be read only when named or when a boundary requires them, and which
documents should not be loaded by default.

This index does not supersede the documents it names. If this index conflicts
with a named authority document, inspect the live repo document and resolve the
conflict explicitly instead of relying on memory, old prompts, or historical
summaries.

## Source Authority / GitHub Connector Rule

Current repo docs are the authority for startup and role behavior.

In ChatGPT sessions without direct local repo access, if the boundary or
session opener names current repo docs, the session must use the
GitHub-connected repository unless current uploaded docs or operator evidence
are explicitly supplied. Local filesystem paths in prompts are operator/repo
orientation, not proof that ChatGPT can inspect local files directly.

Default GitHub source, unless the boundary overrides it:

- repository: `rwfaught/Repos`
- branch: `main`
- docs root: `Orchestrator/Orchestrator/docs`

First reads should normally be:

1. `STARTUP_INDEX.md`
2. the active role doc named by the resolved session role

If the active role is CTO/coordinator, read:

1. `STARTUP_INDEX.md`
2. `ROLE_CTO_COORDINATOR.md`
3. the current `READ_BY_DEFAULT` docs named by this index

If the active role is Relay, read:

1. `STARTUP_INDEX.md`
2. `ROLE_RELAY.md`
3. only docs explicitly named by the boundary or by this index as required

If the connector/source is unavailable, report the missing source and do not
invent continuity. Memory, pasted summaries, old handoffs, and prior worker
reports are not substitutes for reading current source docs when the boundary
depends on current repo doctrine.

Only CTO/coordinator handoffs can initialize CTO/coordinator continuity or
route the next role. Relay closeout reports, Worker/Codex reports,
Platform/Substrate reports, Specialist memos, stale handoffs, and session
records are evidence artifacts for CTO/coordinator review; they are not
startup authority unless CTO/coordinator ratifies them against current repo
docs.

## READ_BY_DEFAULT

Read these documents by default, in this order:

1. `STARTUP_BRIEF.md`
2. `ORCHESTRATOR_METHOD.md`
3. `ORCHESTRATOR_INTERACTION_MODEL.md`
4. `CONTEXT_MAP.md`
5. `CURRENT_SUCCESS_CRITERION.md`
6. `OPEN_THREAD_TRIAGE_PROTOCOL.md`
7. `TRACKS_AND_OPEN_THREADS_CURRENT.md`
8. `PROJECT_CONTINUITY_EVIDENCE_PROTOCOL.md`
9. `REENTRY_PROTOCOL_01.md`
10. `PROJECT_VISION.md`
11. `FOUNDER_CONTROL_PROTOCOL.md`
12. `FOUNDER_COMPREHENSION_SNAPSHOT_CURRENT.md`
13. `CAPABILITY_REALITY_MAP.md`
14. `FIRST_PRODUCT_WEDGE_RATIFICATION_RECORD.md`
15. `LOCAL_TOPOLOGY_AND_EXPORTS.md`
16. `OWNER_AUTHORED_SYSTEM_PRINCIPLE.md`

## READ_WHEN_NAMED

Read these documents or classes only when the user, packet, current boundary,
or evidence question names them or makes them load-bearing:

- `BUILD_RULES.md`
- `CAPABILITY_REGISTRY.md`
- `LOCAL_FIRST_MODEL_ROUTER_POLICY.md`
- `LOCAL_FIRST_PROVIDER_CATALOG.md`
- `TRACKS_AND_OPEN_THREADS.md` full historical ledger
- `ARTIFACT_RETENTION_AND_SOURCE_HYGIENE.md`
- `OPERATOR_CODEBASE_MAP.md`
- operator runbooks
- `session_records/` saved closeout records
- current boundary docs
- source/test referenced phase docs
- track-specific product, founder, design, dossier, provider, RAG, platform, or
  artifact docs

The full `TRACKS_AND_OPEN_THREADS.md` ledger is `READ_WHEN_NAMED`: read it
when the user, packet, current boundary, historical proof question, or
open-thread archaeology requirement makes it load-bearing. Startup orientation
should use `TRACKS_AND_OPEN_THREADS_CURRENT.md` by default.

Read `session_records/` only when named, when a boundary requires a specific
record, or when evidence archaeology is required. Do not load saved session
records by default.

## DO_NOT_LOAD_BY_DEFAULT

Do not load these documents or classes by default:

- `ACTION_LOG.md`
- `PHASE_INDEX.md`
- `SOURCE_MANIFEST.md`
- all `PHASE_*.md` unless phase history or source/test proof is in scope
- old restart prompts
- alignment/integration packets
- superseded design/reentry packets
- generated archives or ZIPs

## Ledger Search Rule

Search ledgers instead of full-loading them when the question is about:

- phase registration
- proof history
- source manifest entries
- action-log provenance
- missing/stale document names
- current track status

After a search narrows the evidence target, read the relevant excerpt or named
document section. Do not treat the size or existence of a ledger as permission
to skip targeted evidence checks.

## Stale Authority Rule

Do not treat memory, old prompts, archived docs, ZIP contents, historical
capsules, or prior worker reports as current authority without checking live
repo docs and git/source state. Prefer current live repo files over packaged
artifacts unless the active boundary is explicitly about a packaged artifact.

Do not treat stale handoffs, Relay reports, Worker/Codex reports,
Platform/Substrate reports, Specialist memos, or saved session records as
substitutes for current repo docs and CTO/coordinator ratification.

## Mutation Caution

This index does not authorize deletion, archive, rewrite, consolidation, source
edits, provider/runtime execution, model execution, or phase advancement. Any
such work requires a separate explicit boundary with its own allowed scope,
excluded scope, and proof expectations.
