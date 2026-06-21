# Source Hygiene Cleanup Report

Boundary: MUTATE_PRODUCT_SOURCE_HYGIENE_ARCHIVE_GENERATED_STATE_CLEAN_SOURCE_TREE_PATCH_PRODUCT_ZIPPER_EXPORT_VERIFY_NO_RUNTIME_NO_WSL_NO_INSTALLER_NO_MODEL_NO_DISCORD_NO_BRIDGE_NO_ADAPTER_NO_A18CF_NO_VENDOR_NO_OZ_NO_CODEX

Timestamp: 20260611_131044

Status: Implemented for the current clean product ZIP baseline. Reconciled by doc-manifest boundary after uploaded ZIP ratification.

## Result

Generated workspace state was archived outside the product repo, then removed from the source tree. Placeholder .gitkeep files were left in generated directories so the directory surface remains visible without carrying runtime/proof payloads.

The product zipper was repaired so generated workspace/proof/runtime payloads do not re-enter source ZIPs by default.

## Archive

- Archive path: C:\Users\accou\Desktop\Repos\Orchestrator\source_hygiene_archives\Orchestrator_generated_workspace_state_20260611_131044.zip
- Archive SHA256: b17f6ee14038ee62dbcba359a010f59230085064b43d7fed43d4ce6fb60bd120
- Archive size bytes: 4,300,257
- Archive entry count: 8,564

## Pre-cleanup generated surfaces

| Surface | Files | JSON |
|---|---:|---:|
| data\tasks | 2,673 | 2,673 |
| data\runs | 1,903 | 1,903 |
| data\artifacts | 1,420 | 1,420 |
| data\verifier_results | 1,417 | 1,417 |
| data\reviewer_recommendations | 883 | 883 |
| data\case_packets | 256 | 256 |
| test_logs | 10 | 0 |

## Protected fixture/input surfaces

These were not targeted for cleanup:

- data\phase53_fixtures
- data\phase54_fixtures
- data\phase57_intake_inputs
- data\phase58_case_packet_inputs
- data\phase59_case_packet_inputs
- data\phase60_case_packet_seeds
- data\phase61_case_packet_inputs
- data\phase62_case_packet_inputs

## Ratified clean product ZIP profile

- Ratified uploaded clean ZIP SHA256: d7ebcfdd928650501fe835e498ec79ebf2fd0913dc5a21a60149aa4096a773af
- Ratified uploaded clean ZIP size: 615,428 bytes
- Ratified uploaded clean ZIP entry count: 631
- Total JSON entries: 322
- Fixture/input JSON entries: 321
- data/state/workspace_state.json entries: 1
- Generated workspace JSON entries under cleanup-targeted surfaces: 0
- Generated workspace .gitkeep placeholders: 7
- test_logs payload entries: 0
- Python .pyc/.pyo entries: 0
- Host metadata / Zone Identifier entries: 0

## Export-tooling policy

Zip-OrchestratorProductRepo.ps1 now excludes Python caches and host metadata during staging, and prunes generated workspace payloads from the staged ZIP copy while preserving .gitkeep placeholders.

## Fixture caveat

During the cleanup sequence, fixture-sensitive unit tests generated or modified some fixture/input-side data, increasing fixture JSON count from the earlier inventory. This was accepted because fixture/input directories are protected source/test surfaces, not generated workspace payload surfaces.

## Caveat

This cleanup does not delete durable docs, source code, tests, phase fixture/input data, or data/state. It does not establish any current platform/runtime truth.