# Provider Generation Smoke Probe Packet

## Purpose

The provider generation smoke probe packet is deterministic paperwork for a
future manual operator proof. It describes how a bounded local provider
generation smoke probe could be requested later without running that proof now.

## Future Boundary

`PHASE_157_LOCAL_PROVIDER_GENERATION_SMOKE_PROBE_27B_OPERATOR_PROOF`

Future execution requires explicit coordinator acceptance. Packet existence is
not provider selection, provider execution, model generation, route execution,
or production readiness.

## Request Shape

- Provider catalog key: `local_model_candidate`
- Model: `qwen3.6:27b`
- Endpoint surface: `local_ollama_http`
- Endpoint path: `/api/generate`
- Method: `POST`
- Prompt contract: `Return exactly: ORCH_PROVIDER_SMOKE_OK`
- Stream: `false`
- Output size: small
- Tool calls: none
- External lookup: none
- Route execution: none

The request shape is descriptive only. It is not a runnable command and does
not call `/api/generate`.

## Required Operator Evidence

- command boundary markers
- HTTP status code
- content type
- response bytes count
- finish/done marker if available
- response text marker `ORCH_PROVIDER_SMOKE_OK`
- exit code captured separately
- elapsed time if present

## Acceptance Criteria

- operator captures command boundary markers
- operator captures HTTP status code
- operator captures content type
- operator captures response bytes count
- operator captures finish/done marker if available
- response text includes `ORCH_PROVIDER_SMOKE_OK` or a clearly bounded
  equivalent
- exit code captured separately
- elapsed time captured if possible

## Relationship To Phase 149

Phase 149 route-selection readiness can name a future generation smoke probe
boundary. Phase 152 adds the deterministic packet contract for describing that
future proof. It still does not authorize, run, or accept the proof.

Phase 156 retargets the active packet from `qwen3-30b-24k:latest` to
`qwen3.6:27b` after Phase 155 Retry 3 proved the 30b/24k target reached
`/api/generate` but failed model load with CUDA OOM. The 27b target is visible
in prior Phase 131 model-list evidence only; at the Phase 156 point no
accepted 27b `/api/show` metadata proof or `/api/generate` proof existed yet.

Phase 159 Retry 1 later accepted the `qwen3.6:27b` `/api/generate` marker
smoke proof with `num_predict=96`, HTTP `200`, JSON parse success, returned
model `qwen3.6:27b`, response field `ORCH_PROVIDER_SMOKE_OK`, `done=true`,
and `done_reason=stop`. The earlier Phase 159 initial failure remains a
token-budget/probe-shape failure from `num_predict=16`, not a model-load
failure. The Phase 155 Retry 3 CUDA OOM remains a 30b/24k failure, not a 27b
failure. The remaining conservative next proof is `qwen3.6:27b` `/api/show`
metadata visibility.

## Non-Proofs

The packet contract is not provider execution, model execution, generation,
`/api/generate`, `/api/chat`, route execution, worker dispatch, RAG, scheduler,
connector execution, service/API/UI productization, or production readiness.

Even if a future smoke probe later passes, that would not prove semantic
correctness, model loadability for real workloads, VRAM sufficiency for real
workloads, route execution, worker dispatch, RAG, scheduler, connector,
service/API/UI productization, or production readiness.
