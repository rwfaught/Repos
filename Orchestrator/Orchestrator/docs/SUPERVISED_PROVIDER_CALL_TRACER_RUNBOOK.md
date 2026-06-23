# Supervised Provider Call Tracer Runbook

## Purpose

The supervised provider-call tracer packet defines a future operator-run local
provider marker smoke through the product harness. Phase 183 created the packet
and result-classification contract only. Phase 187 reconciled the target to
`qwen3.6:35b-a3b` from inventory visibility, but Phase 191 rejects that laptop
target based on Roger's operational evidence that it locks up the laptop.

Phase 191 retargets the packet to the accepted 30B viability candidate:

`qwen3:30b-a3b-instruct-2507-q4_K_M`

It does not call Ollama, HTTP, providers, models, routes, workers, OpenClaw,
Hermes, WSL, Discord, connectors, schedulers, RAG, web, service/API/UI, or
production behavior.

## Future Operator Boundary

Required future boundary:

`future_supervised_provider_call_tracer_operator_proof`

Required future proof:

`captured_http_status_json_response_marker_and_no_route_execution`

The future operator proof must capture the status, parsed JSON state, returned
model, response marker, completion state, and proof that no route execution
occurred.

## Endpoint, Model, Prompt, Marker

- Provider catalog key: `local_model_candidate`
- Model: `qwen3:30b-a3b-instruct-2507-q4_K_M`
- Endpoint shape: `POST local_ollama_http/api/generate`
- Endpoint URL string: `http://127.0.0.1:11434/api/generate`
- Prompt contract: `Return exactly: ORCH_PROVIDER_SMOKE_OK`
- Expected marker: `ORCH_PROVIDER_SMOKE_OK`
- Request data: `stream=false`, `num_predict=96`, `num_ctx=4096`,
  `temperature=0`

The endpoint URL is recorded as a string only. It is not called by Phase 191.

## Target Selection

`qwen3.6:35b-a3b` is disallowed for current laptop target selection because
Roger reported operational evidence that it locks up the laptop.

`qwen3.6:27b` remains the safer fallback candidate based on prior smoother
operation and earlier accepted marker-smoke and metadata evidence.

`qwen3:30b-a3b-instruct-2507-q4_K_M` is the current product tracer target
because Phase 190 accepted a constrained one-call 30B marker-smoke viability
result for that exact returned model.

## Phase 190 Viability Evidence

Phase 190 captured constrained 30B marker-smoke viability only:

- HTTP status: `200`
- JSON parse success: `true`
- Returned model: `qwen3:30b-a3b-instruct-2507-q4_K_M`
- Response text: `ORCH_30B_VIABILITY_OK`
- Done: `true`
- Done reason: `stop`
- Duration: `9394ms`
- Marker present: `true`
- Classification: `pass_30b_marker_smoke_viability`

Phase 190 Retry 1 backfilled the proof artifact without a provider call:

`C:\Users\accou\AppData\Local\Temp\orchestrator_phase190_30b_provider_viability\phase_190_30b_provider_viability_probe.json`

GPU observation is caveated: before memory was `0MiB / 24463MiB`, after memory
was `18302MiB / 24463MiB`, and process attribution was not proven by the
`nvidia-smi` process table.

## What Phase 191 Proves

- The packet contract can be built deterministically.
- The packet carries `phase=PHASE_191` and
  `artifact_kind=supervised_provider_call_tracer_packet_contract`.
- The packet records `original_packet_phase=PHASE_183`,
  `target_reconciliation_phase=PHASE_191`, and
  `inventory_evidence_phase=PHASE_190`.
- The packet target is `qwen3:30b-a3b-instruct-2507-q4_K_M`.
- The packet does not target `qwen3.6:35b-a3b`.
- Phase 190 evidence is recorded only as constrained 30B marker-smoke
  viability, not as product tracer proof.
- The packet keeps provider selection, provider execution, route execution,
  generation, and production readiness authority false.
- The result classifier is pure and classifies caller-supplied captured result
  dictionaries without making calls.

## What Phase 191 Does Not Prove

Phase 191 does not prove provider/model execution, route execution, live
routing, HTTP/API endpoint execution, Ollama generation, WSL/OpenClaw/Hermes/
Discord, product-harness Codex dispatch, worker dispatch, RAG/web/scheduler/
connector behavior, semantic correctness, real workload sufficiency,
long-context behavior, sustained-load stability, service/API/UI
productization, production behavior, or production readiness.

Phase 190 does not prove route execution, semantic correctness, real workload
sufficiency, long-context behavior, sustained-load stability, or production
readiness. It proves only a constrained 30B marker-smoke viability call.

## Future Operator Proof Requirements

A future captured product tracer result may classify as PASS only when all of
these are true:

- `http_status=200`
- `json_parse_success=True`
- `returned_model=qwen3:30b-a3b-instruct-2507-q4_K_M`
- `response_text` contains `ORCH_PROVIDER_SMOKE_OK`
- `done=True`

The next product tracer proof still needs a supervised
`ORCH_PROVIDER_SMOKE_OK` marker call for the product contract. The Phase 190
`ORCH_30B_VIABILITY_OK` marker is viability evidence only.

Even a PASS classification remains a marker-smoke classification only and
keeps `route_execution_allowed=false` and `production_readiness=false`.

## Failure Classifications

- `missing_required_fields`
- `non_200_http_status`
- `json_parse_failure`
- `wrong_model`
- `missing_marker`
- `incomplete_done_false`

Each failure classification preserves blocked conditions or missing
requirements and keeps production readiness false.

## No-Execution Posture

The packet and classifier preserve false activity flags for provider/model/
runtime/route execution, `/api/generate`, `/api/chat`, `/api/show`,
`/api/tags`, worker/Codex dispatch, Ollama/WSL/OpenClaw/Hermes/Discord,
RAG/web/scheduler/connector behavior, service/API/UI/product execution, and
cleanup/delete/archive.
