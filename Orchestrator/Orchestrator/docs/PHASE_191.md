# Phase 191 - Supervised Provider Call Tracer Target Reconciliation To 30B

## Purpose

Phase 191 reconciles the supervised provider-call tracer packet target away
from `qwen3.6:35b-a3b` and to the accepted 30B viability candidate:

`qwen3:30b-a3b-instruct-2507-q4_K_M`

This is source/test/docs reconciliation only. It does not run providers,
models, HTTP, Ollama, routes, workers, WSL, OpenClaw, Hermes, Discord,
connectors, services, APIs, UI, cleanup/delete/archive, or production behavior.

## Why 35B Was Rejected

`qwen3.6:35b-a3b` is disallowed for current laptop target selection because
Roger reported operational evidence that it locks up the laptop.

Phase 187 had targeted `qwen3.6:35b-a3b` from inventory visibility only. That
visibility did not prove marker-smoke behavior, route execution, semantic
correctness, real workload sufficiency, long-context behavior,
sustained-load stability, or production readiness.

## Why 30B Is Now Target

Phase 190 accepted a constrained one-call 30B marker-smoke viability result for
`qwen3:30b-a3b-instruct-2507-q4_K_M`: HTTP `200`, JSON parse success `true`,
returned model `qwen3:30b-a3b-instruct-2507-q4_K_M`, response text
`ORCH_30B_VIABILITY_OK`, `done=true`, `done_reason=stop`, duration `9394ms`,
marker present `true`, and classification
`pass_30b_marker_smoke_viability`.

`qwen3.6:27b` remains the safer fallback candidate based on prior smoother
operation and earlier accepted marker-smoke and metadata evidence.

## Changed Files

- `orchestrator/supervised_provider_call_tracer.py`
- `tests/test_phase_183_supervised_provider_call_tracer_packet_contract.py`
- `docs/PHASE_190.md`
- `docs/PHASE_191.md`
- `docs/SUPERVISED_PROVIDER_CALL_TRACER_RUNBOOK.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/CONTEXT_MAP.md`

## Implementation Summary

- Retargeted the packet model to
  `qwen3:30b-a3b-instruct-2507-q4_K_M`.
- Preserved endpoint shape as data only:
  `POST local_ollama_http/api/generate`.
- Preserved endpoint URL as string only:
  `http://127.0.0.1:11434/api/generate`.
- Preserved product tracer prompt contract:
  `Return exactly: ORCH_PROVIDER_SMOKE_OK`.
- Preserved expected marker: `ORCH_PROVIDER_SMOKE_OK`.
- Preserved conservative request parameters: `stream=false`,
  `num_predict=96`, `num_ctx=4096`, `temperature=0`.
- Updated classifier PASS behavior so the returned model must be
  `qwen3:30b-a3b-instruct-2507-q4_K_M`.
- Added wrong-model tests for `qwen3.6:35b-a3b` and `qwen3.6:27b`.
- Preserved all execution authority and activity flags as false.

## Validation Commands And Results

- `python -m compileall orchestrator` - PASS
- `python -m unittest discover -s tests -p "test_phase_183_supervised_provider_call_tracer_packet_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_176_tiny_vertical_tracer_cli_adapter_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_169_tiny_vertical_tracer_bullet_dry_report_artifact_contract.py" -v` - PASS
- `git diff --check` - PASS
- `git status --short --branch` - reviewed

## Accepted Facts

- Packet target is `qwen3:30b-a3b-instruct-2507-q4_K_M`.
- Packet does not target `qwen3.6:35b-a3b`.
- Phase 190 proves only a constrained 30B marker-smoke viability call.
- Phase 190 Retry 1 backfilled the proof artifact without a provider call.
- Phase 190 GPU process attribution was not proven by the `nvidia-smi`
  process table.
- `qwen3.6:35b-a3b` is disallowed for current laptop target selection.
- `qwen3.6:27b` remains the safer fallback candidate.
- The next product tracer proof still needs a supervised
  `ORCH_PROVIDER_SMOKE_OK` marker call for the product contract.

## Non-Proofs

Phase 191 does not prove route execution, semantic correctness, real workload
sufficiency, long-context behavior, sustained-load stability, production
readiness, provider/model execution, HTTP/Ollama execution, worker dispatch,
service/API/UI behavior, or product execution.

Phase 190 does not prove route execution, semantic correctness, real workload
sufficiency, long-context behavior, sustained-load stability, or production
readiness.

## Caveats

The Phase 190 marker was `ORCH_30B_VIABILITY_OK`, not the product tracer marker
`ORCH_PROVIDER_SMOKE_OK`.

The endpoint URL remains string-only data in source. No provider call was made
by this phase.

## Next Boundary Recommendation

Next boundary remains a separately authorized supervised product tracer marker
proof for `ORCH_PROVIDER_SMOKE_OK` on
`qwen3:30b-a3b-instruct-2507-q4_K_M`, with captured status, parsed JSON,
returned model, marker, completion state, and no route execution proof.

`PHASE191_SUPERVISED_PROVIDER_CALL_TRACER_TARGET_RECONCILIATION_TO_30B_SOURCE_TEST_DOCS_PROVEN=PASS`
