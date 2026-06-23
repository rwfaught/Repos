# Supervised Provider Call Tracer Runbook

## Purpose

The supervised provider-call tracer packet defines a future operator-run local
provider marker smoke through the product harness. Phase 183 creates the packet
and result-classification contract only.

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
- Model: `qwen3.6:27b`
- Endpoint shape: `POST local_ollama_http/api/generate`
- Endpoint URL string: `http://127.0.0.1:11434/api/generate`
- Prompt contract: `Return exactly: ORCH_PROVIDER_SMOKE_OK`
- Expected marker: `ORCH_PROVIDER_SMOKE_OK`
- Request data: `stream=false`, `num_predict=96`, `temperature=0`

The endpoint URL is recorded as a string only. It is not called by Phase 183.

## What Phase 183 Proves

- The packet contract can be built deterministically.
- The packet carries `phase=PHASE_183` and
  `artifact_kind=supervised_provider_call_tracer_packet_contract`.
- The packet anchors to `source_tracer_phase=PHASE_169`,
  `adapter_phase=PHASE_176`, and `operator_smoke_phase=PHASE_179`.
- The packet carries the qwen3.6:27b evidence keys:
  `phase_159_retry1_qwen36_27b_generate_marker_smoke` and
  `phase_162_qwen36_27b_show_metadata_visibility`.
- The packet keeps provider selection, provider execution, route execution,
  generation, and production readiness authority false.
- The result classifier is pure and classifies caller-supplied captured result
  dictionaries without making calls.

## What Phase 183 Does Not Prove

Phase 183 does not prove provider/model execution, route execution, live
routing, HTTP/API endpoint execution, Ollama/WSL/OpenClaw/Hermes/Discord,
product-harness Codex dispatch, worker dispatch, RAG/web/scheduler/connector
behavior, semantic correctness, real workload proof, service/API/UI
productization, production behavior, or production readiness.

Prior smoke evidence is not current loadability proof. A future smoke pass
would not prove semantic correctness, real workload VRAM sufficiency, route
execution, or production readiness.

## Future Operator Proof Requirements

A future captured result may classify as PASS only when all of these are true:

- `http_status=200`
- `json_parse_success=True`
- `returned_model=qwen3.6:27b`
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
