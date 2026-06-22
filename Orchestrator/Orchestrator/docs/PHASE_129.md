# Phase 129 - Provider Probe Packet CLI Draft Adapter

## Status

Locally source/test/docs-proven.

Marker:

`PHASE129_PROVIDER_PROBE_PACKET_CLI_DRAFT_ADAPTER_LOCAL_SOURCE_TEST_DOCS_PROVEN=PASS`

## Purpose

Add an explicit deterministic, non-executing CLI adapter path for drafting
provider probe packet paperwork through manual review output.

The CLI lets an operator intentionally request probe-packet drafting metadata,
but it does not execute a probe, provider, model, runtime, worker, RAG, web,
scheduler, connector, route, or production behavior.

## Changed Files

- `orchestrator/manual_review_cli.py`
- `tests/test_phase_129_provider_probe_packet_cli_draft_adapter_contract.py`
- `tests/test_phase_120_manual_review_cli_module_entrypoint.py`
- `docs/PHASE_129.md`
- `docs/MANUAL_REVIEW_CLI_RUNBOOK.md`
- `docs/PROVIDER_PROBE_BOUNDARY_PACKET.md`
- `docs/LOCAL_FIRST_MODEL_ROUTER_POLICY.md`
- `docs/LOCAL_FIRST_PROVIDER_CATALOG.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/CONTEXT_MAP.md`

## CLI Path Added

The existing command remains supported:

`python -m orchestrator.manual_review_cli --fixture safe_direct_answer`

The explicit paperwork-only command shape is:

`python -m orchestrator.manual_review_cli --fixture safe_direct_answer --draft-provider-probe-packet --authorize-probe-boundary --probe-kind read_only_future_probe_plan --probe-surface provider_runtime_surface --probe-scope read_only_probe_command_draft --expected-evidence captured_future_probe_output`

`--draft-provider-probe-packet` alone does not authorize a packet. Missing
authorization, scope, or expected evidence remains blocked/missing
requirements.

## Validation Performed

- `python -m py_compile orchestrator/manual_review_cli.py`
- `python -m py_compile orchestrator/manual_review_runner.py`
- `python -m py_compile orchestrator/coordinator_review_report.py`
- `python -m py_compile orchestrator/provider_probe_boundary_packet.py`
- `python -m unittest tests.test_phase_129_provider_probe_packet_cli_draft_adapter_contract`
- `python -m unittest tests.test_phase_128_provider_probe_packet_manual_review_integration_contract`
- `python -m unittest tests.test_phase_127_provider_probe_boundary_packet_contract`
- `python -m unittest tests.test_phase_123_model_router_policy_manual_review_integration_contract`
- `python -m unittest tests.test_phase_122_local_first_model_router_policy_contract`
- `python -m unittest tests.test_phase_120_manual_review_cli_module_entrypoint`
- `python -m unittest tests.test_phase_121_manual_review_cli_runbook_golden_contract`

## Source Snapshot Refresh Status

`C:\Users\accou\Desktop\Repos\Source Files\Update-SourceFiles.ps1` was run
after validation. Generated ZIP files under `Source Files` were not staged.

## Explicit Non-Proofs

Phase 129 does not prove provider/model execution, provider availability proof,
model availability proof, provider availability probe, model availability
probe, provider runtime import, model selection for execution, Ollama, WSL,
OpenClaw, Hermes, Discord, installer, runtime/probe execution outside ordinary
Python unit-test execution, runtime/platform execution, web lookup, RAG/local
document lookup execution, scheduler/reminder execution, connector execution,
Codex dispatch from product code, worker dispatch, route execution, production
execution, cleanup/delete/archive, artifact export/package behavior beyond the
requested source refresh, autonomous writeback, service/API/UI productization,
live routing, or production readiness.

## Caveats

- CLI probe packet flags draft manual review metadata only.
- `--fixture`, router recommendation, and `--draft-provider-probe-packet` do
  not imply authorization by themselves.
- No CLI flag executes a probe.
