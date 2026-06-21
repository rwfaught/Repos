# Phase 83 - Product Zipper Acceptance Generated Data Hygiene Repair

## Purpose

Phase 83 permanently repairs the product zipper/source-hygiene rule that Phase 82 exposed.

Generated acceptance proof payloads under:

- data/acceptance_inputs
- data/acceptance_records

are local generated workspace proof data, not canonical source payloads.

The product ZIP must exclude JSON payloads under those directories unless a later boundary explicitly promotes a specific file as a fixture.

Empty directory entries and .gitkeep placeholders may remain allowed when consistent with the existing source-hygiene policy.

## Ratified Boundary

MUTATE_PRODUCT_PHASE83_ZIPPER_HYGIENE_EXCLUDE_ACCEPTANCE_GENERATED_DATA_AND_EXPORT_PRODUCT_ALLOW_TEMP_SYNTHETIC_FIXTURE_CREATE_REMOVE_ONLY_NO_TASK_EXECUTION_NO_PROVIDER_EXECUTION_NO_MODEL_NO_WSL_NO_INSTALLER_NO_DISCORD_NO_BRIDGE_NO_ADAPTER_NO_PLATFORM_MUTATION_NO_A18CF_NO_VENDOR_NO_BROAD_CLEANUP_NO_ARCHIVE_NO_OZ_NO_CODEX

## Changed Surface

- Product zipper: C:\Users\accou\Desktop\Repos\Powershell Scripts\Zip-OrchestratorProductRepo.ps1
- Product docs: docs/PHASE_83.md
- Product docs: docs/ACTION_LOG.md
- Product docs: docs/PHASE_INDEX.md
- Product docs: docs/SOURCE_MANIFEST.md
- Product docs: docs/ARTIFACT_RETENTION_AND_SOURCE_HYGIENE.md

## Proof Requirements

Phase 83 must prove:

- starting uploaded/source ZIP hash matched 76d7841386569a8db67014c27bf592f55a5bd2f613e5fc7fbf26dc1285fa354f
- product zipper contains explicit generated acceptance-data exclusions
- a synthetic generated acceptance input JSON payload is excluded from exported product ZIP
- a synthetic generated acceptance record JSON payload is excluded from exported product ZIP
- required source docs still export
- generated acceptance JSON payloads do not leak into the product ZIP
- no task, provider, model, runtime, WSL, installer, Discord, bridge, adapter, platform, A18CF, vendoring, oz, or Codex execution occurred

## Caveat

This is export/source-hygiene repair only.

It does not broaden current-success proof beyond the deterministic local_file provider caveat.

It does not prove autonomous AI coding, model-backed generation, or broad semantic correctness.

PHASE83_PRODUCT_ZIPPER_ACCEPTANCE_GENERATED_DATA_HYGIENE_REPAIR
