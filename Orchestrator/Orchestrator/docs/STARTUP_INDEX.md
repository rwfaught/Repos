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

## READ_BY_DEFAULT

Read these documents by default, in this order:

1. `STARTUP_BRIEF.md`
2. `ORCHESTRATOR_METHOD.md`
3. `ORCHESTRATOR_INTERACTION_MODEL.md`
4. `CONTEXT_MAP.md`
5. `CURRENT_SUCCESS_CRITERION.md`
6. `OPEN_THREAD_TRIAGE_PROTOCOL.md`
7. `TRACKS_AND_OPEN_THREADS.md`
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
- `ARTIFACT_RETENTION_AND_SOURCE_HYGIENE.md`
- `OPERATOR_CODEBASE_MAP.md`
- operator runbooks
- current boundary docs
- source/test referenced phase docs
- track-specific product, founder, design, dossier, provider, RAG, platform, or
  artifact docs

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

## Mutation Caution

This index does not authorize deletion, archive, rewrite, consolidation, source
edits, provider/runtime execution, model execution, or phase advancement. Any
such work requires a separate explicit boundary with its own allowed scope,
excluded scope, and proof expectations.
