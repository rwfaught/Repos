# ARTIFACT_RETENTION_AND_SOURCE_HYGIENE.md

Status: Current product-side retention doctrine after OT-007 cleanup/export-tooling implementation for the ratified clean product ZIP baseline.

## Purpose

This document separates product source from generated Orchestrator artifacts.

The goal is not to erase proof.

The goal is to keep proof legible without letting the source tree become mud.

## Artifact classes

### Source

Source files are implementation, tests, docs, scripts, and fixtures required to understand, validate, or evolve the product.

Examples:

- orchestrator Python modules
- tests
- product docs
- deliberate test fixtures under data phase directories when referenced by tests

### Fixture

Fixture files are stable test inputs that should remain in source while tests depend on them.

Current protected fixture/input directories:

- data/phase53_fixtures
- data/phase54_fixtures
- data/phase57_intake_inputs
- data/phase58_case_packet_inputs
- data/phase59_case_packet_inputs
- data/phase60_case_packet_seeds
- data/phase61_case_packet_inputs
- data/phase62_case_packet_inputs

Do not delete these casually.

### Generated workspace data

Generated workspace data is output produced by the Orchestrator during local runs, proof-of-concept exercises, acceptance testing, or manual development.

Cleanup-targeted generated-data directories:

- data/tasks
- data/runs
- data/artifacts
- data/verifier_results
- data/reviewer_recommendations
- data/case_packets
- test_logs

These should not automatically ship in every source artifact.

### Disposable cache and host metadata

These files are not product source and should not ship in source artifacts:

- Python bytecode cache directories
- Python compiled bytecode files
- pytest cache
- mypy cache
- ruff cache
- Windows Zone Identifier metadata
- macOS and Windows desktop metadata files

## Historical source-hygiene issue

The post-Phase64 pre-cleanup product ZIP contained 9,191 entries.

Observed high-noise surfaces from uploaded ZIP inspection included:

- data/tasks: 2,673 JSON files
- data/runs: 1,903 JSON files
- data/artifacts: 1,420 JSON files
- data/verifier_results: 1,417 JSON files
- data/reviewer_recommendations: 883 JSON files
- data/case_packets: 256 JSON files
- Python cache files: 51 compiled bytecode files
- Zone Identifier style files: 8 files

That artifact is now superseded by the clean product ZIP baseline.

## Current clean baseline

The ratified clean product ZIP baseline is:

- SHA256: d7ebcfdd928650501fe835e498ec79ebf2fd0913dc5a21a60149aa4096a773af
- Size: 615,428 bytes
- Entry count: 631
- Total JSON entries: 322
- Fixture/input JSON entries: 321
- data/state/workspace_state.json entries: 1
- Generated workspace JSON entries under cleanup-targeted surfaces: 0
- Generated workspace .gitkeep placeholders: 7
- test_logs payload entries: 0
- Python .pyc/.pyo entries: 0
- Host metadata / Zone Identifier entries: 0

Generated workspace state was archived outside the product repo before cleanup.

- Archive path: C:\Users\accou\Desktop\Repos\Orchestrator\source_hygiene_archives\Orchestrator_generated_workspace_state_20260611_131044.zip
- Archive SHA256: b17f6ee14038ee62dbcba359a010f59230085064b43d7fed43d4ce6fb60bd120
- Archive size: 4,300,257 bytes
- Archive entry count: 8,564

## Retention doctrine

Generated artifacts should have an explicit lifecycle.

Recommended lifecycle:

1. Active workspace output may exist locally during development.
2. Boundary proof should be summarized in ACTION_LOG.md and phase docs.
3. If raw generated artifacts matter, archive them into a named proof bundle outside the canonical source surface.
4. The source export should exclude disposable caches and stale generated-output sludge.
5. Stable fixtures should remain in source only when tests or docs require them.
6. Product docs should record enough proof summary to avoid keeping large generated payloads in the source ZIP by inertia.

## Implemented cleanup/export-tooling result

SOURCE_HYGIENE_CLEANUP_AND_EXPORT_TOOLING was implemented for the current product baseline.

Generated workspace state was archived outside the product repo and removed from source payload surfaces. Future product exports should preserve fixture/source data while excluding runtime/proof payloads, Python caches, and host metadata by default.

See docs/SOURCE_HYGIENE_CLEANUP_REPORT.md for the archive record and exact cleanup boundary.

## Remaining watchlist

OT-007 is implemented for the current product ZIP baseline, but it remains a watchlist concern:

- Future phases may generate new workspace/proof/runtime artifacts.
- Future export tooling must keep generated payloads out of canonical source artifacts unless explicitly authorized.
- Fixture/input directories must remain protected unless tests/docs are deliberately changed.
- Raw proof bundles should be archived outside the canonical source surface when they matter.

## Non-authorization

This document does not authorize deletion, archiving, runtime execution, model execution, WSL, installer work, Discord, OpenClaw, bridge, adapter, A18CF, platform mutation, vendoring, oz, Codex, or export.

## Phase 82 Generated Acceptance Data Amendment

PHASE82_GENERATED_ACCEPTANCE_DATA_RETENTION_AMENDMENT

Phase 82 introduced two generated workspace proof surfaces:

- data/acceptance_inputs
- data/acceptance_records

These are generated workspace data.

They may exist locally during acceptance-demo work.

They should not automatically ship as canonical product source payload.

Durable proof should be summarized in phase docs, ACTION_LOG.md, SOURCE_MANIFEST.md, and any relevant current-success documentation unless a later boundary explicitly promotes a specific generated acceptance fixture into source.

## PHASE82_EXPORT_HYGIENE_REPAIR_GENERATED_ACCEPTANCE_DATA_EXCLUDED

Phase 82 export hygiene repair confirms that generated acceptance data remains local proof data.

The product ZIP must exclude:

- data/acceptance_inputs/phase82_phase80_current_success_acceptance_input.json
- data/acceptance_records/acceptance_8d7e762f.json

The local repo may retain these files after export so current-success-result-review can continue surfacing the acceptance summary.

PHASE82_EXPORT_HYGIENE_REPAIR_GENERATED_ACCEPTANCE_DATA_EXCLUDED
## Phase 83 Product Zipper Acceptance Generated-Data Hygiene Rule

PHASE83_PRODUCT_ZIPPER_ACCEPTANCE_GENERATED_DATA_HYGIENE_REPAIR

The product zipper/source-hygiene rule now explicitly treats JSON payloads under the following directories as generated workspace proof data:

- data/acceptance_inputs
- data/acceptance_records

Product ZIP exports must exclude generated JSON payloads under those directories unless a later boundary explicitly promotes a specific file as a durable fixture.

Empty directory entries and .gitkeep placeholders may remain allowed when consistent with existing source-hygiene policy.

This rule repairs the Phase 82 export-hygiene gap where generated acceptance JSON payloads could leak into the product ZIP even though the durable proof belonged in docs.

PHASE83_PRODUCT_ZIPPER_ACCEPTANCE_GENERATED_DATA_HYGIENE_REPAIR
