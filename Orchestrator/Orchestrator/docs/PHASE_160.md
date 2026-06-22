# Phase 160 - Local Provider Generation Smoke 27B Evidence

## Purpose

Record the accepted Phase 159 Retry 1 local Ollama `/api/generate` smoke
proof for `qwen3.6:27b` in deterministic source/docs/tests without running
Ollama, calling provider endpoints, selecting providers, executing routes, or
claiming production readiness.

## Changed Files

- `orchestrator/provider_evidence_registry.py`
- `orchestrator/route_selection_readiness.py`
- `tests/test_phase_143_provider_evidence_registry_router_report_contract.py`
- `tests/test_phase_146_provider_evidence_backed_router_recommendation_envelope_contract.py`
- `tests/test_phase_149_provider_evidence_gated_route_selection_readiness_contract.py`
- `tests/test_phase_156_local_provider_target_alignment_27b_contract.py`
- `tests/test_phase_160_local_provider_generation_smoke_27b_evidence_contract.py`
- `docs/PHASE_160.md`
- `docs/LOCAL_FIRST_PROVIDER_CATALOG.md`
- `docs/LOCAL_FIRST_MODEL_ROUTER_POLICY.md`
- `docs/PROVIDER_EVIDENCE_REGISTRY.md`
- `docs/PROVIDER_GENERATION_SMOKE_PROBE_PACKET.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/CONTEXT_MAP.md`

## Accepted Facts

- Phase 159 Retry 1 accepted:
  `PHASE159_RETRY1_LOCAL_PROVIDER_GENERATION_SMOKE_27B_OPERATOR_PROOF=PASS`.
- Endpoint: `http://127.0.0.1:11434/api/generate`.
- Model: `qwen3.6:27b`.
- Prompt:
  `Return exactly this marker in your final response and do not explain: ORCH_PROVIDER_SMOKE_OK`.
- Stream: `false`; temperature: `0`; `num_predict=96`.
- Curl exit code: `0`; HTTP status: `200`; content type:
  `application/json; charset=utf-8`.
- JSON parse succeeded; returned model was `qwen3.6:27b`.
- Response field was exactly `ORCH_PROVIDER_SMOKE_OK`; `done=true`;
  `done_reason=stop`.
- Marker was present in the response field, thinking field, and raw body.
- Final git status during the operator probe was `## main...origin/main`.

## Preserved Failure Caveats

- The earlier Phase 159 initial failure remains:
  `PHASE159_LOCAL_PROVIDER_GENERATION_SMOKE_PROBE_27B_OPERATOR_PROOF=FAIL_HTTP_200_LOCAL_PROVIDER_GENERATED_THINKING_ONLY_LENGTH_NO_MARKER`.
  It was a token-budget/probe-shape failure: `num_predict=16` was too small,
  output was consumed by thinking, the response field was empty,
  `done_reason=length`, and no marker was accepted.
- Phase 155 Retry 3 remains:
  `PHASE155_LOCAL_PROVIDER_GENERATION_SMOKE_PROBE_OPERATOR_PROOF_RETRY_3=FAIL_HTTP_500_PROVIDER_MODEL_LOAD_CUDA_OOM_RAW_BODY_CAPTURED_NO_GENERATION_PROOF`.
  It was a `qwen3-30b-24k:latest` CUDA OOM model-load failure, not a
  `qwen3.6:27b` failure.

## Readiness Impact

The deterministic provider evidence registry now includes the accepted Phase
159 Retry 1 `qwen3.6:27b` generation-smoke marker evidence. Route-selection
readiness now treats the generation-smoke gate as satisfied, but it remains
not ready for execution because accepted `qwen3.6:27b` `/api/show` metadata
proof is still missing.

The next required proof is:
`bounded_qwen36_27b_api_show_metadata_operator_proof`.

All provider selection, provider execution, route execution, generation-now,
and production readiness permissions remain false.

## Validation Commands And Results

- `python -m compileall orchestrator` - PASS
- `python -m unittest discover -s tests -p "test_phase_160_local_provider_generation_smoke_27b_evidence_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_143_provider_evidence_registry_router_report_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_146_provider_evidence_backed_router_recommendation_envelope_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_149_provider_evidence_gated_route_selection_readiness_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_152_local_provider_generation_smoke_probe_packet_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_156_local_provider_target_alignment_27b_contract.py" -v` - PASS

## Non-Proofs

Phase 160 does not run runtime probes, call Ollama, call `/api/generate`,
`/api/chat`, `/api/show`, or `/api/tags`, execute providers or models, select
providers, dispatch workers, execute routes, perform RAG/local lookup, web
lookup, scheduler/reminder work, connector execution, platform/runtime
execution, or production execution.

This phase does not prove `/api/chat`, `qwen3.6:27b` `/api/show` metadata,
semantic correctness, real workload loadability, VRAM sufficiency beyond the
exact accepted Phase 159 Retry 1 smoke request, route execution, worker
dispatch, Hermes/OpenClaw behavior, RAG/web/scheduler/connector behavior,
service/API/UI productization, or production readiness.

## Next Boundary Recommendation

`PHASE_161_QWEN36_27B_API_SHOW_METADATA_OPERATOR_PROOF`

`PHASE160_LOCAL_PROVIDER_GENERATION_SMOKE_27B_EVIDENCE_SOURCE_TEST_DOCS_PROVEN=PASS`
