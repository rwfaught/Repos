# Supervised Provider Call Tracer Runbook

## Purpose

The supervised provider-call tracer packet defines a future operator-run local
provider marker smoke through the product harness. Phase 183 created the packet
and result-classification contract only. Phase 187 reconciles the target with
Phase 186 Retry 4 current inventory visibility.

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
- Model: `qwen3.6:35b-a3b`
- Endpoint shape: `POST local_ollama_http/api/generate`
- Endpoint URL string: `http://127.0.0.1:11434/api/generate`
- Prompt contract: `Return exactly: ORCH_PROVIDER_SMOKE_OK`
- Expected marker: `ORCH_PROVIDER_SMOKE_OK`
- Request data: `stream=false`, `num_predict=96`, `temperature=0`

The endpoint URL is recorded as a string only. It is not called by Phase 183 or
Phase 187.

## What Phase 183 And Phase 187 Prove

- The packet contract can be built deterministically.
- The packet carries `phase=PHASE_187` and
  `artifact_kind=supervised_provider_call_tracer_packet_contract`.
- The packet records `original_packet_phase=PHASE_183`,
  `target_reconciliation_phase=PHASE_187`, and
  `inventory_evidence_phase=PHASE_186_RETRY4`.
- The packet anchors to `source_tracer_phase=PHASE_169`,
  `adapter_phase=PHASE_176`, and `operator_smoke_phase=PHASE_179`.
- The packet target is `qwen3.6:35b-a3b`.
- The packet records Phase 186 Retry 4 inventory visibility for
  `qwen3.6:35b-a3b` only.
- The packet does not transfer prior `qwen3.6:27b` marker-smoke or metadata
  evidence to `qwen3.6:35b-a3b`.
- The packet keeps provider selection, provider execution, route execution,
  generation, and production readiness authority false.
- The result classifier is pure and classifies caller-supplied captured result
  dictionaries without making calls.

## Why qwen3.6:27b Was Retired For This Packet

Phase 186 Retry 4 proved current inventory visibility only: `/api/version`
returned HTTP 200 with version `0.30.10`, `/api/tags` returned HTTP 200,
`qwen3.6:27b` was not present, and `qwen3.6:35b-a3b` was present.

No `/api/generate` was run and no model execution occurred. The current packet
therefore targets `qwen3.6:35b-a3b`, while preserving that inventory visibility
is not marker-smoke proof.

## What Phase 183 And Phase 187 Do Not Prove

Phase 183 and Phase 187 do not prove provider/model execution, route
execution, live routing, HTTP/API endpoint execution, Ollama generation,
WSL/OpenClaw/Hermes/Discord, product-harness Codex dispatch, worker dispatch,
RAG/web/scheduler/connector behavior, semantic correctness, real workload
proof, service/API/UI productization, production behavior, or production
readiness.

Phase 186 Retry 4 inventory visibility is not marker-smoke proof.
`qwen3.6:35b-a3b` still needs a future supervised marker-smoke proof. A future
smoke pass would not prove semantic correctness, real workload VRAM
sufficiency, route execution, or production readiness.

## Future Operator Proof Requirements

A future captured result may classify as PASS only when all of these are true:

- `http_status=200`
- `json_parse_success=True`
- `returned_model=qwen3.6:35b-a3b`
- `response_text` contains `ORCH_PROVIDER_SMOKE_OK`
- `done=True`

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
