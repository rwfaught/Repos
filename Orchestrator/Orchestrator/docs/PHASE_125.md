# Phase 125 - Local-First Provider Catalog And Escalation Matrix

## Status

Locally source/test/docs-proven.

Marker:

`PHASE125_LOCAL_FIRST_PROVIDER_CATALOG_AND_ESCALATION_MATRIX_LOCAL_SOURCE_TEST_DOCS_PROVEN=PASS`

## Purpose

Add a deterministic, non-executing local-first provider catalog and escalation
matrix that supports future model/router decisions without executing providers,
models, runtimes, workers, RAG, web, schedulers, connectors, or production
work.

## Changed Files

- `orchestrator/model_provider_catalog.py`
- `orchestrator/model_router_policy.py`
- `tests/test_phase_125_local_first_provider_catalog_contract.py`
- `docs/LOCAL_FIRST_PROVIDER_CATALOG.md`
- `docs/LOCAL_FIRST_MODEL_ROUTER_POLICY.md`
- `docs/PHASE_125.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/CONTEXT_MAP.md`

## Doctrine Added

Phase 125 adds catalog entries for local model candidates, frontier provider
candidates, worker/Codex boundaries, RAG/local-document boundaries,
scheduler/reminder boundaries, web/research boundaries, and blocked or
unavailable provider posture.

Each entry exposes provider tier, maturity, allowed boundary, execution and
selection flags, fallback, escalation posture, required authority, non-proofs,
activity flags, and the provider posture string used by router policy reports.

The catalog distinguishes local-first preference from provider execution
authority, frontier escalation authority, worker/Codex dispatch authority, and
RAG/web/scheduler boundary authority. All execution and activity flags remain
false.

## Validation Performed

- `python -m py_compile orchestrator/model_provider_catalog.py`
- `python -m py_compile orchestrator/model_router_policy.py`
- `python -m unittest tests.test_phase_125_local_first_provider_catalog_contract`
- `python -m unittest tests.test_phase_122_local_first_model_router_policy_contract`
- `python -m unittest tests.test_phase_123_model_router_policy_manual_review_integration_contract`
- `python -m unittest tests.test_phase_120_manual_review_cli_module_entrypoint`
- `python -m unittest tests.test_phase_121_manual_review_cli_runbook_golden_contract`

## Source Snapshot Refresh Status

`C:\Users\accou\Desktop\Repos\Source Files\Update-SourceFiles.ps1` was run
after validation. Generated ZIP files under `Source Files` were not staged.

## Explicit Non-Proofs

Phase 125 does not prove provider/model execution, provider availability,
model availability, live provider/model selection, Ollama, WSL, OpenClaw,
Hermes, Discord, installer, runtime/probe execution outside ordinary Python
unit-test execution, runtime/platform execution, web lookup, RAG/local document
lookup execution, scheduler/reminder execution, connector execution, Codex
dispatch from product code, worker dispatch, route execution, production
execution, cleanup/delete/archive, artifact export/package behavior beyond the
requested source refresh, autonomous writeback, service/API/UI productization,
live routing, or production readiness.

## Caveats

- The provider catalog is deterministic policy data only.
- `model_router_policy.py` uses catalog-backed posture strings but still does
  not execute or select providers, models, runtimes, platforms, or workers.
- Future provider/runtime proof remains a separate boundary.
