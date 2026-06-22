# Phase 156 - Local Provider Target Alignment 27B

## Purpose

Retarget the active deterministic local provider generation smoke probe packet
from `qwen3-30b-24k:latest` to `qwen3.6:27b` after Phase 155 Retry 3 showed
the 30b/24k target reached `/api/generate` but failed model load with CUDA
OOM. This phase is source/test/docs alignment only, not runtime proof.

## Changed Files

- `orchestrator/provider_generation_smoke_probe_packet.py`
- `tests/test_phase_152_local_provider_generation_smoke_probe_packet_contract.py`
- `tests/test_phase_156_local_provider_target_alignment_27b_contract.py`
- `docs/PROVIDER_GENERATION_SMOKE_PROBE_PACKET.md`
- `docs/LOCAL_FIRST_PROVIDER_CATALOG.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/CONTEXT_MAP.md`
- `docs/PHASE_156.md`

## Accepted Facts

- Phase 152 added a deterministic future generation smoke probe packet for
  `qwen3-30b-24k:latest`.
- Phase 154 pushed Phase 152 to `origin/main` at commit `d4b68c3`.
- Phase 155 Retry 3 reached `/api/generate` for the 30b/24k target but failed
  with HTTP 500 and provider CUDA OOM:
  `cudaMalloc failed: out of memory`;
  `alloc_tensor_range: failed to allocate CUDA0 buffer of size 18375698432`;
  `error loading model: unable to allocate CUDA0 buffer`.
- `qwen3.6:27b` is visible in prior Phase 131 provider-surface model-list
  evidence.
- No accepted `qwen3.6:27b` `/api/show` metadata proof exists yet.
- No accepted `qwen3.6:27b` `/api/generate` proof exists yet.

## Validation Commands And Results

- `python -m compileall orchestrator` - PASS
- `python -m pytest tests/test_phase_152_local_provider_generation_smoke_probe_packet_contract.py` - PASS
- `python -m pytest tests/test_phase_156_local_provider_target_alignment_27b_contract.py` - PASS
- `python -m pytest tests/test_phase_143_provider_evidence_registry_router_report_contract.py tests/test_phase_146_provider_evidence_backed_router_recommendation_envelope_contract.py tests/test_phase_149_provider_evidence_gated_route_selection_readiness_contract.py` - PASS

## Non-Proofs

Phase 156 does not run runtime probes, call Ollama, call `/api/generate`,
`/api/chat`, `/api/show`, or `/api/tags`, execute models, dispatch workers,
execute routes, perform RAG/local lookup, web lookup, scheduler/reminder work,
connector execution, platform/runtime execution, or production execution.

This phase does not prove `qwen3.6:27b` metadata, generation, semantic
correctness, model loadability, VRAM sufficiency, real workload suitability,
route execution, service/API/UI productization, or production readiness.

## Next Boundary Recommendation

`PHASE_157_LOCAL_PROVIDER_GENERATION_SMOKE_PROBE_27B_OPERATOR_PROOF`

`PHASE156_LOCAL_PROVIDER_TARGET_ALIGNMENT_27B_LOCAL_SOURCE_TEST_DOCS_PROVEN=PASS`
