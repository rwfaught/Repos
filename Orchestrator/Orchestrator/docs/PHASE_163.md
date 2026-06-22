# Phase 163 - Qwen3.6 27B API Show Metadata Evidence

## Purpose

Record the accepted Phase 162 local Ollama `/api/show` metadata proof for
`qwen3.6:27b` in deterministic source/docs/tests without running Ollama,
calling provider endpoints, selecting providers, executing routes, or claiming
production readiness.

## Changed Files

- `orchestrator/provider_evidence_registry.py`
- `orchestrator/route_selection_readiness.py`
- `tests/test_phase_143_provider_evidence_registry_router_report_contract.py`
- `tests/test_phase_146_provider_evidence_backed_router_recommendation_envelope_contract.py`
- `tests/test_phase_149_provider_evidence_gated_route_selection_readiness_contract.py`
- `tests/test_phase_156_local_provider_target_alignment_27b_contract.py`
- `tests/test_phase_160_local_provider_generation_smoke_27b_evidence_contract.py`
- `tests/test_phase_163_qwen36_27b_api_show_metadata_evidence_contract.py`
- `docs/PHASE_163.md`
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

- Phase 162 accepted:
  `PHASE162_QWEN36_27B_API_SHOW_METADATA_OPERATOR_PROOF=PASS`.
- Observed classification:
  `PASS_QWEN36_27B_API_SHOW_METADATA_VISIBLE_WITH_DETAILS`.
- Endpoint: `http://127.0.0.1:11434/api/show`.
- Model: `qwen3.6:27b`.
- The response included metadata with visible details.
- The raw body included license text, tensor/model metadata, capabilities, and
  `modified_at`.
- Capabilities visibly included: `completion`, `vision`, `tools`, and
  `thinking`.
- The raw body was large/noisy and was not copied wholesale into source docs.
- Exact family, parameter-size, and quantization fields are
  `unknown_not_recorded` because they were not provided in the packet/source
  fields used by this source-ledger phase.
- Final git status during the operator proof was `## main...origin/main`.

## Preserved Facts

- Phase 159 Retry 1 accepted `qwen3.6:27b` `/api/generate` marker smoke proof
  with HTTP `200`, JSON parse success, response field
  `ORCH_PROVIDER_SMOKE_OK`, `done=true`, `done_reason=stop`, and
  `num_predict=96`.
- The earlier Phase 159 initial failure remains a token-budget/probe-shape
  failure from `num_predict=16`, not a model-load failure.
- Phase 155 Retry 3 remains a `qwen3-30b-24k:latest` CUDA OOM failure, not a
  `qwen3.6:27b` failure.

## Readiness Impact

The deterministic provider evidence registry now includes the accepted Phase
162 `qwen3.6:27b` `/api/show` metadata visibility evidence. Route-selection
readiness now treats both the exact accepted generation-smoke evidence gate and
the `qwen3.6:27b` metadata evidence gate as satisfied.

The readiness label is conservative:
`future_probe_ready_qwen36_27b_evidence_registered`.

The next recommended boundary is:
`PHASE_164_ROUTE_SELECTION_READINESS_RECOMMENDATION_ENVELOPE_REVIEW`.

All provider selection, provider execution, route execution, generation-now,
and production readiness permissions remain false.

## Validation Commands And Results

- `python -m compileall orchestrator` - PASS
- `python -m unittest discover -s tests -p "test_phase_163_qwen36_27b_api_show_metadata_evidence_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_160_local_provider_generation_smoke_27b_evidence_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_143_provider_evidence_registry_router_report_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_146_provider_evidence_backed_router_recommendation_envelope_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_149_provider_evidence_gated_route_selection_readiness_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_152_local_provider_generation_smoke_probe_packet_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_156_local_provider_target_alignment_27b_contract.py" -v` - PASS

## Non-Proofs

Phase 163 does not run runtime probes, call Ollama, call `/api/show`,
`/api/generate`, `/api/chat`, or `/api/tags`, execute providers or models,
select providers, dispatch workers, execute routes, perform RAG/local lookup,
web lookup, scheduler/reminder work, connector execution, platform/runtime
execution, or production execution.

This phase does not prove `/api/chat`, semantic correctness, real workload
loadability, broad VRAM sufficiency, route execution, worker dispatch,
Hermes/OpenClaw behavior, RAG/web/scheduler/connector behavior, service/API/UI
productization, or production readiness.

## Next Boundary Recommendation

`PHASE_164_ROUTE_SELECTION_READINESS_RECOMMENDATION_ENVELOPE_REVIEW`

`PHASE163_QWEN36_27B_API_SHOW_METADATA_EVIDENCE_SOURCE_TEST_DOCS_PROVEN=PASS`
